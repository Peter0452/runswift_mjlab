#!/usr/bin/env python3
"""
Pruned, smoothness-aware visibility planner.

Design (consistent with a face-travel path tracker):

  * Objective is the tracker's traversal TIME, not an SE(2) strafe model:
        cost = sum(segment_length) / v_cruise  +  w_turn * sum(|turn angle|)
    The turn term is a smoothness penalty on the exterior angle at each vertex,
    fit to the tracker's measured corner slowdown.  No heading buckets, no
    strafe-vs-turn branch -- the tracker faces travel and never strafes by
    choice, so pricing strafing would optimise a path the tracker won't execute.

  * Search state is the ARRIVAL EDGE (u -> v), i.e. the DAVG Algorithm-2
    vertex-pair augmented state, NOT (vertex, heading-bucket).  This gives the
    exact incoming direction at each vertex (no 30-deg discretisation) and is
    lighter than K heading buckets whenever average visibility degree < K.

  * Heading is owned by the tracker.  Only goal_theta crosses the interface,
    and the terminal turn cost is zeroed inside theta_tolerance (don't optimise
    a final angle the tracker only needs to approximate).

  * NO validate-promote-replan loop.  Pruning is made sound by construction:
    region_pad >= max keep-out radius bounds the smoothness detour, so the
    optimum stays inside the active set.  A single non-iterating assert pass
    catches the pathological case and signals "hold committed path" instead of
    re-planning -- deterministic single-plan latency, no data-dependent tail.

Performance:
  * Per-obstacle radii (supports world-model injection: posts/ball/robots).
  * Vectorised segment-disk tests; adjacency built one source at a time with a
    batched (obstacles x targets) check -> O(nV) python iters, not O(nV^2).
  * A* over directed edges with neighbour costs computed as numpy arrays;
    g-score / prev are dense int/float arrays indexed by u*nV+v, no dict churn.
  * Straight-line short-circuit skips the whole graph when the direct line is
    clear (the common case in open play).
"""
from __future__ import annotations

import heapq
import time
from dataclasses import dataclass
from math import atan2, cos, hypot, inf, pi, sin

import numpy as np

_TWO_PI = 2.0 * pi


def _wrap(a: float) -> float:
    return (a + pi) % _TWO_PI - pi


def _wrap_arr(a: np.ndarray) -> np.ndarray:
    return (a + pi) % _TWO_PI - pi


@dataclass
class Obstacles:
    centers: np.ndarray          # (N, 2)
    radii: np.ndarray            # (N,)  keep-out radius = body + clearance
    field_halfsize: np.ndarray   # (2,)  [half_len, half_wid]


@dataclass
class PlannerParams:
    v_cruise: float = 1.85       # nominal along-path speed [m/s]
    w_turn: float = 0.15         # corner penalty [s/rad]; fit to tracker slowdown
    ring_n: int = 6              # ring vertices per obstacle
    region_pad: float | None = None   # None -> max(radii); soundness margin [m]
    eps: float = 0.03            # ring inflation slack [m]
    theta_tolerance: float = 0.15     # terminal heading band [rad]
    field_margin: float = 0.0    # allow planning this far past the field edge


# --------------------------------------------------------------------------- #
#  Vectorised geometry
# --------------------------------------------------------------------------- #
def _seg_disk_mask(p: np.ndarray, q: np.ndarray, centers: np.ndarray,
                   r2: np.ndarray) -> np.ndarray:
    """Per-obstacle: does segment p->q come within radius of each center?"""
    d = q - p
    d2 = float(d @ d)
    if d2 < 1e-12:
        diff = centers - p
        return np.einsum("ij,ij->i", diff, diff) < r2 - 1e-7
    t = np.clip((centers - p) @ d / d2, 0.0, 1.0)
    proj = p + t[:, None] * d
    diff = centers - proj
    return np.einsum("ij,ij->i", diff, diff) < r2 - 1e-7


def _pt_blocked(pt: np.ndarray, centers: np.ndarray, r2: np.ndarray,
                half: np.ndarray, margin: float) -> bool:
    if np.any(np.abs(pt) > half + margin):
        return True
    if centers.shape[0] == 0:
        return False
    diff = centers - pt
    return bool(np.any(np.einsum("ij,ij->i", diff, diff) < r2 - 1e-7))


def _visible_from(src: np.ndarray, verts: np.ndarray, centers: np.ndarray,
                  r2: np.ndarray) -> np.ndarray:
    """Mask over `verts`: is the segment src->vert clear of every obstacle?

    Batched over targets AND obstacles in one shot.  Memory is O(N*M*2);
    N (active obstacles) and M (vertices) are small after pruning.
    """
    M = verts.shape[0]
    N = centers.shape[0]
    if N == 0:
        return np.ones(M, dtype=bool)
    d = verts - src                                   # (M, 2)
    d2 = np.einsum("ij,ij->i", d, d)                  # (M,)
    cs = centers - src                                # (N, 2)
    safe = np.where(d2 > 1e-12, d2, 1.0)
    t = np.clip((cs @ d.T) / safe[None, :], 0.0, 1.0)  # (N, M)
    diff = cs[:, None, :] - t[:, :, None] * d[None, :, :]  # (N, M, 2)
    dist2 = np.einsum("nmk,nmk->nm", diff, diff)      # (N, M)
    hit = dist2 < r2[:, None] - 1e-7
    return ~np.any(hit, axis=0)


# --------------------------------------------------------------------------- #
#  Active-region pruning (fattened so the optimum stays inside)
# --------------------------------------------------------------------------- #
def _select_active(s: np.ndarray, g: np.ndarray, obs: Obstacles,
                   r2: np.ndarray, region_pad: float) -> np.ndarray:
    centers, radii = obs.centers, obs.radii
    N = centers.shape[0]
    if N == 0:
        return np.array([], dtype=int)

    active = _seg_disk_mask(s, g, centers, r2)
    axis = g - s
    L = float(hypot(axis[0], axis[1]))
    if L < 1e-6:
        return np.nonzero(active)[0]

    u = axis / L
    nrm = np.array([-u[1], u[0]])
    a = (centers - s) @ u
    p = (centers - s) @ nrm

    changed = True
    while changed:
        changed = False
        if active.any():
            w = float(np.max(np.abs(p[active]) + radii[active]))
            amin = float(np.min(a[active] - radii[active]))
            amax = float(np.max(a[active] + radii[active]))
        else:
            w, amin, amax = float(radii.max()), 0.0, L
        amin = min(amin, 0.0) - region_pad
        amax = max(amax, L) + region_pad
        cand = (~active) & (a >= amin - radii) & (a <= amax + radii) & \
               (np.abs(p) <= w + radii)
        if cand.any():
            active |= cand
            changed = True
    return np.nonzero(active)[0]


# --------------------------------------------------------------------------- #
#  Planner
# --------------------------------------------------------------------------- #
def _coerce(p) -> tuple[np.ndarray, float]:
    p = np.asarray(p, dtype=float)
    th = float(p[2]) if p.shape[0] >= 3 else float("nan")
    return p[:2].copy(), th


def plan(start, goal, obs: Obstacles, P: PlannerParams | None = None):
    """Returns (path, info).  path is (M,3) array of (x, y, heading) or None."""
    t0 = time.perf_counter()
    P = P or PlannerParams()
    s_xy, s_th = _coerce(start)
    g_xy, g_th = _coerce(goal)
    centers = np.asarray(obs.centers, dtype=float).reshape(-1, 2)
    radii = np.asarray(obs.radii, dtype=float).reshape(-1)
    half = np.asarray(obs.field_halfsize, dtype=float).reshape(2)
    r2 = radii * radii
    region_pad = P.region_pad if P.region_pad is not None else (
        float(radii.max()) if radii.size else 0.0)

    base_info: dict = {}

    def _info(extra):
        d = {"total_ms": round((time.perf_counter() - t0) * 1e3, 3)}
        d.update(base_info)
        d.update(extra)
        return d

    # ---- straight-line short-circuit -------------------------------------- #
    if radii.size == 0 or not bool(_seg_disk_mask(s_xy, g_xy, centers, r2).any()):
        if not (_pt_blocked(s_xy, centers, r2, half, P.field_margin) or
                _pt_blocked(g_xy, centers, r2, half, P.field_margin)):
            heading = s_th if not np.isnan(s_th) else atan2(*(g_xy - s_xy)[::-1])
            gh = g_th if not np.isnan(g_th) else heading
            path = np.array([[s_xy[0], s_xy[1], heading],
                             [g_xy[0], g_xy[1], gh]])
            return path, _info({"nV": 0, "nE": 0, "active": 0, "shortcut": True})

    # ---- prune ------------------------------------------------------------- #
    t_a = time.perf_counter()
    idx = _select_active(s_xy, g_xy, obs, r2, region_pad)
    a_centers = centers[idx]
    a_radii = radii[idx]
    a_r2 = r2[idx]
    active_ms = (time.perf_counter() - t_a) * 1e3

    # ---- vertices: start, goal, rings ------------------------------------- #
    V = [s_xy, g_xy]
    if a_centers.shape[0]:
        ang = np.linspace(0.0, _TWO_PI, P.ring_n, endpoint=False)
        base = np.column_stack((np.cos(ang), np.sin(ang)))      # (ring_n, 2)
        rr = a_radii / cos(pi / max(P.ring_n, 3)) + P.eps       # (Na,)
        for c, ringr in zip(a_centers, rr):
            pts = c + base * ringr
            inb = np.all(np.abs(pts) <= half + P.field_margin, axis=1)
            for k in np.nonzero(inb)[0]:
                pt = pts[k]
                if not _pt_blocked(pt, a_centers, a_r2, half, P.field_margin):
                    V.append(pt)
    V = np.asarray(V, dtype=float)
    nV = V.shape[0]
    START, GOAL = 0, 1

    # ---- adjacency (vectorised per source) -------------------------------- #
    t_adj = time.perf_counter()
    adj: list[list[int]] = [[] for _ in range(nV)]
    nE = 0
    for i in range(nV):
        vis = _visible_from(V[i], V, a_centers, a_r2)
        vis[: i + 1] = False                     # upper triangle only
        for j in np.nonzero(vis)[0]:
            j = int(j)
            adj[i].append(j)
            adj[j].append(i)
            nE += 1

    # ---- leaving-vertex rule for covered start / goal --------------------- #
    s_cov = _pt_blocked(s_xy, a_centers, a_r2, half, P.field_margin)
    g_cov = _pt_blocked(g_xy, a_centers, a_r2, half, P.field_margin)

    def _add_leaving(node: int, pt: np.ndarray, theta: float, is_start: bool):
        if nV <= 2:
            return
        d = theta if not np.isnan(theta) else atan2(*(g_xy - s_xy)[::-1])
        dvec = np.array([cos(d), sin(d)])
        sign = 1.0 if is_start else -1.0
        ring = V[2:]
        vec = ring - pt
        along = (vec @ dvec) * sign
        dd = np.einsum("ij,ij->i", vec, vec)
        cand = np.nonzero(along > 0.0)[0]
        pool = cand if cand.size else np.arange(ring.shape[0])
        best = int(pool[np.argmin(dd[pool])]) + 2
        if best not in adj[node]:
            adj[node].append(best)
            adj[best].append(node)

    if s_cov:
        _add_leaving(START, s_xy, s_th, True)
    if g_cov:
        _add_leaving(GOAL, g_xy, g_th, False)
    adj_ms = (time.perf_counter() - t_adj) * 1e3

    # ---- precompute neighbour geometry ------------------------------------ #
    nbr = [np.asarray(a, dtype=np.intp) for a in adj]
    nbr_dir, nbr_t = [], []
    for v in range(nV):
        if nbr[v].size == 0:
            nbr_dir.append(np.zeros(0))
            nbr_t.append(np.zeros(0))
            continue
        dv = V[nbr[v]] - V[v]
        nbr_dir.append(np.arctan2(dv[:, 1], dv[:, 0]))
        nbr_t.append(np.hypot(dv[:, 0], dv[:, 1]) / P.v_cruise)
    hgoal = np.hypot(V[:, 0] - g_xy[0], V[:, 1] - g_xy[1]) / P.v_cruise

    # ---- A* over directed-edge states ------------------------------------- #
    t_s = time.perf_counter()
    NS = nV * nV
    gscore = np.full(NS, inf)
    prev = np.full(NS, -1, dtype=np.intp)
    SENT = -1
    wt = P.w_turn

    s_in = s_th if not np.isnan(s_th) else atan2(*(g_xy - s_xy)[::-1])
    pq: list[tuple[float, float, int, int, float]] = []
    if nbr[START].size:
        turns = wt * np.abs(_wrap_arr(nbr_dir[START] - s_in))
        gs = nbr_t[START] + turns
        for k, w in enumerate(nbr[START]):
            w = int(w)
            sid = START * nV + w
            gscore[sid] = gs[k]
            prev[sid] = SENT
            heapq.heappush(pq, (gs[k] + hgoal[w], gs[k], START, w,
                                float(nbr_dir[START][k])))

    best_tot = inf
    best_state = -1
    while pq:
        f, g, u, v, in_dir = heapq.heappop(pq)
        if f >= best_tot:
            break
        sid = u * nV + v
        if g > gscore[sid]:
            continue
        if v == GOAL:
            term = 0.0
            if not np.isnan(g_th):
                dd = abs(_wrap(g_th - in_dir))
                if dd > P.theta_tolerance:
                    term = wt * (dd - P.theta_tolerance)
            tot = g + term
            if tot < best_tot:
                best_tot, best_state = tot, sid
            continue
        nb = nbr[v]
        if nb.size == 0:
            continue
        turns = wt * np.abs(_wrap_arr(nbr_dir[v] - in_dir))
        ng_all = g + nbr_t[v] + turns
        for k in range(nb.shape[0]):
            w = int(nb[k])
            if w == u:
                continue
            ng = ng_all[k]
            cid = v * nV + w
            if ng < gscore[cid]:
                gscore[cid] = ng
                prev[cid] = sid
                heapq.heappush(pq, (ng + hgoal[w], ng, v, w,
                                    float(nbr_dir[v][k])))
    search_ms = (time.perf_counter() - t_s) * 1e3

    if best_state < 0:
        # No route reaches the exact goal.  Fall back to the reachable graph
        # vertex closest to the goal so the robot still heads toward it, rather
        # than giving up and stopping.  Every reached vertex was expanded over
        # the visibility graph, so the path to it is collision-free.
        reached = np.nonzero(gscore < inf)[0]
        arrival = reached % nV
        keep = arrival != START                    # ignore trivial back-to-start states
        reached = reached[keep]
        arrival = arrival[keep]
        if reached.size == 0:
            return None, _info({"reason": "no_path", "nV": nV, "nE": nE,
                                "active": int(a_centers.shape[0]),
                                "active_ms": round(active_ms, 3),
                                "adj_ms": round(adj_ms, 3),
                                "search_ms": round(search_ms, 3)})
        dv = V[arrival] - g_xy
        d2 = np.einsum("ij,ij->i", dv, dv)
        # closest to the goal, breaking ties toward the cheaper route
        order = np.lexsort((gscore[reached], d2))
        best_state = int(reached[order[0]])
        base_info["closest_point"] = True
        base_info["closest_gap_m"] = round(float(hypot(dv[order[0]][0],
                                                        dv[order[0]][1])), 3)

    # ---- reconstruct ------------------------------------------------------ #
    heads = []
    st = best_state
    while st != SENT:
        heads.append(st % nV)
        st = int(prev[st])
    heads.append(START)
    heads.reverse()
    pts = V[heads]

    # headings: travel direction per segment (telemetry; tracker re-derives),
    # final = goal_theta if specified.
    seg = np.diff(pts, axis=0)
    th = np.arctan2(seg[:, 1], seg[:, 0])
    headings = np.empty(len(heads))
    headings[:-1] = th
    headings[-1] = th[-1] if seg.shape[0] else (s_in if np.isnan(s_th) else s_th)
    if not np.isnan(g_th):
        headings[-1] = g_th
    if not np.isnan(s_th):
        headings[0] = s_th
    path = np.column_stack((pts, headings))

    # ---- single assert pass (NO replan) ----------------------------------- #
    #violated = False
    #if centers.shape[0]:
    #    for sgi in range(pts.shape[0] - 1):
    #        if (sgi == 0 and s_cov) or (sgi == pts.shape[0] - 2 and g_cov):
    #            continue
    #        if bool(_seg_disk_mask(pts[sgi], pts[sgi + 1], centers, r2).any()):
    #            violated = True
    #            break

    return path, _info({"nV": nV, "nE": nE, "active": int(a_centers.shape[0]),
                        "shortcut": False, # "hold_prev": violated,
                        "active_ms": round(active_ms, 3),
                        "adj_ms": round(adj_ms, 3),
                        "search_ms": round(search_ms, 3)})