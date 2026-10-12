#!/usr/bin/env python3
"""
SE(2) Planner with Active Regions  --  collision-safety fixes.

Changes vs. the original (all aimed at "path shoots through obstacles"):

  1. LEAVING-VERTEX RULE (paper Algorithm 1, lines 17-27).
     The old code "handled" a covered start/goal by skipping that obstacle in
     _visible (`if hypot(endpoint-o) <= r: continue`), which let the straight
     edge pass THROUGH the obstacle. That skip is removed. Instead, when S or G
     is inside a keep-out, we add ONE explicit exit edge to the nearest ring
     vertex in the going direction (heading for S) / coming direction (for G).

  2. PRUNED-OBSTACLE VALIDATION.
     Active-region pruning is only sound for the Euclidean-shortest path; the
     turn-augmented objective can swing outside the region and clip a pruned
     obstacle. After planning we re-check the returned polyline against ALL
     obstacles; any pruned obstacle the path actually touches is promoted to
     active and we re-plan. Bounded by the obstacle count, so it terminates.

  3. STRICT KEEP-OUT (no more 0.9 shrink).
     _visible used rc = 0.9 * keep-out, which could cut into the real body at
     low clearance. We now test against the full keep-out. To keep coarse rings
     connected, the ring radius is set from ring_n so adjacent-vertex chords
     still clear the keep-out: r_ring = R / cos(pi/ring_n) + eps.

     Planner: pass theta_tolerance in and zero the terminal turn cost inside the band. 
     Right now A* will prefer a path that nails goal_theta even if a shorter/faster path 
     arriving at goal_theta + 0.3 (within tol) existed. Relaxing the terminal cost to 
     a tolerance lets it pick the genuinely faster route.
"""
from __future__ import annotations

import heapq
import time
from dataclasses import dataclass
from math import atan2, cos, hypot, inf, pi, sin, sqrt

from legacy_world_model import FIELD_LENGTH_M, FIELD_WIDTH_M

import numpy as np


def _wrap(a: float) -> float:
    return (a + pi) % (2.0 * pi) - pi

def _bucket(theta: float, k: int) -> int:
    return int(round(_wrap(theta) / (2.0 * pi) * k)) % k

def _bucket_theta(idx: int, k: int) -> float:
    return _wrap(2.0 * pi * idx / k)


@dataclass
class SE2Params:
    vx: float = 2.1
    vy: float = 1.5
    vomega: float = 1.2
    w_turn: float = 0.6
    w_lat: float = 0.6
    heading_buckets: int = 12

    obstacle_radius: float = 0.30
    clearance: float = 0.25
    ring_n: int = 8
    region_pad: float = 0.4


# ---------------------------------------------------------------------------
#  Geometry
# ---------------------------------------------------------------------------
_RING_OFFSET_CACHE = {}


def _dist2_xy(a, b) -> float:
    dx = float(a[0] - b[0])
    dy = float(a[1] - b[1])
    return dx * dx + dy * dy


def _seg_disk(a, b, c, r):
    ax = float(a[0]); ay = float(a[1])
    bx = float(b[0]); by = float(b[1])
    cx = float(c[0]); cy = float(c[1])
    abx = bx - ax
    aby = by - ay
    L2 = abx * abx + aby * aby
    if L2 < 1e-12:
        dx = cx - ax
        dy = cy - ay
        return dx * dx + dy * dy < r * r
    t = ((cx - ax) * abx + (cy - ay) * aby) / L2
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    px = ax + t * abx
    py = ay + t * aby
    dx = cx - px
    dy = cy - py
    return dx * dx + dy * dy < r * r

def _visible(a, b, obstacles, P):
    """Strict keep-out: the segment must clear every obstacle's full keep-out.
    No endpoint skip (that was the through-the-obstacle bug); covered S/G get
    their exit edges from the leaving-vertex rule instead."""
    R = P.obstacle_radius + P.clearance
    for o in obstacles:
        if _seg_disk(a, b, o, R):
            return False
    return True

def _ring_radius(P) -> float:
    """Ring radius chosen so adjacent ring vertices' chord clears the keep-out
    even with strict collision checking and coarse ring_n."""
    R = P.obstacle_radius + P.clearance
    return R / cos(pi / max(P.ring_n, 3)) + 0.03


def _ring_offsets(P):
    r_ring = _ring_radius(P)
    key = (int(P.ring_n), round(float(r_ring), 9))
    offsets = _RING_OFFSET_CACHE.get(key)
    if offsets is None:
        offsets = np.array(
            [
                [r_ring * cos(2.0 * pi * k / P.ring_n), r_ring * sin(2.0 * pi * k / P.ring_n)]
                for k in range(P.ring_n)
            ],
            dtype=float,
        )
        _RING_OFFSET_CACHE[key] = offsets
    return offsets


def select_active(s, g, obstacles, P):
    R = P.obstacle_radius + P.clearance
    s = np.asarray(s, float); g = np.asarray(g, float)
    obstacles = [np.asarray(o, float) for o in obstacles]
    active = {i for i, o in enumerate(obstacles) if _seg_disk(s, g, o, R)}

    axis = g - s
    L = float(hypot(*axis))
    if L < 1e-6:
        return [obstacles[i] for i in sorted(active)], sorted(active)
    u = axis / L
    n = np.array([-u[1], u[0]])

    changed = True
    while changed:
        changed = False
        if active:
            w = max(abs(float((obstacles[i] - s) @ n)) + R for i in active)
            amin = min(float((obstacles[i] - s) @ u) - R for i in active)
            amax = max(float((obstacles[i] - s) @ u) + R for i in active)
        else:
            w, amin, amax = R, 0.0, L
        amin = min(amin, 0.0) - P.region_pad
        amax = max(amax, L) + P.region_pad
        for i, o in enumerate(obstacles):
            if i in active:
                continue
            a = float((o - s) @ u); p = float((o - s) @ n)
            if amin - R <= a <= amax + R and abs(p) <= w + R:
                active.add(i); changed = True
    idx = sorted(active)
    return [obstacles[i] for i in idx], idx


# ---------------------------------------------------------------------------
#  Anisotropic edge cost (unchanged)
# ---------------------------------------------------------------------------
def _max_translate_speed(delta: float, P: SE2Params) -> float:
    c, s = cos(delta), sin(delta)
    return 1.0 / sqrt((c / P.vx) ** 2 + (s / P.vy) ** 2)

def edge_cost(p_from, theta_in, p_to, P: SE2Params):
    seg = p_to - p_from
    L = float(hypot(seg[0], seg[1]))
    if L < 1e-9:
        return 0.0, theta_in, "hold"
    phi = atan2(seg[1], seg[0])
    delta = _wrap(phi - theta_in)
    t_strafe = L / _max_translate_speed(delta, P) + P.w_lat * abs(sin(delta)) * L
    dth = abs(_wrap(phi - theta_in))
    t_turn = (dth / P.vomega) + P.w_turn * dth + (L / P.vx)

    # double check
    if t_strafe <= t_turn:
        return t_strafe, theta_in, "strafe"
    return t_turn, phi, "forward"


# ---------------------------------------------------------------------------
#  Core: build graph (with leaving vertices) + search
# ---------------------------------------------------------------------------
def _plan_core(start, goal, active, P, *, safety_margin: float = 0.0):
    if abs(goal[0]) > FIELD_LENGTH_M * 0.5 + safety_margin:
        return None

    if abs(goal[1]) > FIELD_WIDTH_M * 0.5 + safety_margin:
        return None   
    
    R = P.obstacle_radius + P.clearance
    ring_offsets = _ring_offsets(P)

    V = [start[:2].copy(), goal[:2].copy()]
    rings = []  # (center, [vertex indices])
    for o in active:
        idxs = []
        for offset in ring_offsets:
            v = o + offset

            if abs(v[0]) > FIELD_LENGTH_M * 0.5 + safety_margin:
                continue

            if abs(v[1]) > FIELD_WIDTH_M * 0.5 + safety_margin:
                continue     

            V.append(v)
            idxs.append(len(V) - 1)
        rings.append((o, idxs))

    nV = len(V)

    adj = [[] for _ in range(nV)]
    for i in range(nV):
        for j in range(i + 1, nV):
            if _visible(V[i], V[j], active, P):
                adj[i].append(j); adj[j].append(i)

    # ---- leaving-vertex rule: explicit exit edge for a covered S or G ----
    def add_leaving(node_idx, pt, theta, bearing, is_start):
        d = theta if not np.isnan(theta) else bearing
        dvec = np.array([cos(d), sin(d)])
        sign = 1.0 if is_start else -1.0  # S leaves along heading; G enters along coming dir
        R2 = R * R
        for o, idxs in rings:
            if _dist2_xy(pt, o) >= R2:
                continue                                   # not covered by this obstacle
            best, best_d = -1, inf
            for vi in idxs:
                vec = V[vi] - pt
                if float(vec @ dvec) * sign > 0.0:         # in going/coming direction
                    dd = float(vec[0] * vec[0] + vec[1] * vec[1])
                    if dd < best_d:
                        best_d, best = dd, vi              # ...choose the closest
            if best < 0:                                   # fallback: closest, any direction
                for vi in idxs:
                    dx = float(V[vi][0] - pt[0])
                    dy = float(V[vi][1] - pt[1])
                    dd = dx * dx + dy * dy
                    if dd < best_d:
                        best_d, best = dd, vi
            if best >= 0 and best not in adj[node_idx]:
                adj[node_idx].append(best); adj[best].append(node_idx)

    START, GOAL = 0, 1
    bearing = atan2(goal[1] - start[1], goal[0] - start[0])
    add_leaving(START, start[:2], start[2], bearing, True)
    add_leaving(GOAL, goal[:2], goal[2], bearing, False)

    # ---- augmented A* over (node, heading bucket) ----
    K = P.heading_buckets
    start_b = _bucket(start[2] if not np.isnan(start[2]) else 0.0, K)
    dist = {(START, start_b): 0.0}
    came = {}
    h0 = float(hypot(*(goal[:2] - start[:2]))) / P.vx
    pq = [(h0, 0.0, START, start_b)]
    best = None

    while pq:
        _, g, u, bu = heapq.heappop(pq)
        if best and g >= best[0]:
            break
        if g > dist.get((u, bu), inf):
            continue
        theta_u = _bucket_theta(bu, K)
        if u == GOAL:
            term = 0.0
            if not np.isnan(goal[2]):
                dd = abs(_wrap(goal[2] - theta_u))
                term = dd / P.vomega + P.w_turn * dd
            tot = g + term
            if best is None or tot < best[0]:
                best = (tot, (u, bu))
            continue
        for v in adj[u]:
            c, exit_th, mode = edge_cost(V[u], theta_u, V[v], P)
            bv = _bucket(exit_th, K)
            ng = g + c
            if ng < dist.get((v, bv), inf):
                dist[(v, bv)] = ng
                came[(v, bv)] = (u, bu, mode, exit_th)
                hv = float(hypot(*(goal[:2] - V[v]))) / P.vx
                heapq.heappush(pq, (ng + hv, ng, v, bv))

    if best is None:
        return None

    path = []
    state = best[1]
    while state in came:
        u, bu, mode, exit_th = came[state]
        v_idx = state[0]
        path.append((float(V[v_idx][0]), float(V[v_idx][1]), float(exit_th), mode))
        state = (u, bu)
    path.append((float(V[START][0]), float(V[START][1]),
                 float(start[2]) if not np.isnan(start[2]) else 0.0, "start"))
    path.reverse()
    if not np.isnan(goal[2]):
        gx, gy, _, gm = path[-1]
        path[-1] = (gx, gy, float(goal[2]), gm)
    return path


# ---------------------------------------------------------------------------
#  Plan: prune -> solve -> validate against pruned obstacles -> re-plan
# ---------------------------------------------------------------------------
def _coerce(p):
    p = np.asarray(p, float)
    return np.array([p[0], p[1], np.nan if p.shape[0] < 3 else p[2]])

def plan(start, goal, obstacles, P: SE2Params | None = None, *, safety_margin: float = 0.0):
    t0 = time.perf_counter()
    P = P or SE2Params()
    start = _coerce(start); goal = _coerce(goal)
    obstacles = [np.asarray(o, float) for o in obstacles]
    R = P.obstacle_radius + P.clearance

    # which endpoints sit inside an obstacle (their first/last segment is an
    # unavoidable exit edge and is not a validation failure)
    R2 = R * R
    s_cov = any(_dist2_xy(start[:2], o) < R2 for o in obstacles)
    g_cov = any(_dist2_xy(goal[:2], o) < R2 for o in obstacles)

    _, idx = select_active(start[:2], goal[:2], obstacles, P)
    t_active = time.perf_counter()
    active_idx = set(idx)

    path = None
    graph_search_ms = 0.0
    validation_ms = 0.0
    replan_count = 0
    for _ in range(len(obstacles) + 1):
        active = [obstacles[i] for i in sorted(active_idx)]
        t_core0 = time.perf_counter()
        path = _plan_core(start, goal, active, P, safety_margin=safety_margin)
        graph_search_ms += (time.perf_counter() - t_core0) * 1000.0
        if path is None:
            return None, {
                "active": len(active),
                "total": len(obstacles),
                "reason": "no_path",
                "active_select_ms": round((t_active - t0) * 1000.0, 2),
                "graph_search_ms": round(graph_search_ms, 2),
                "validation_ms": round(validation_ms, 2),
                "replan_count": replan_count,
                "total_ms": round((time.perf_counter() - t0) * 1000.0, 2),
            }

        violated = set()
        t_val0 = time.perf_counter()
        for i, o in enumerate(obstacles):
            if i in active_idx:
                continue
            for s in range(len(path) - 1):
                # skip the unavoidable exit segment from a covered endpoint
                if (s == 0 and s_cov) or (s == len(path) - 2 and g_cov):
                    continue
                if _seg_disk(path[s], path[s + 1], o, R):
                    violated.add(i); break
        validation_ms += (time.perf_counter() - t_val0) * 1000.0
        if not violated:
            break
        active_idx |= violated
        replan_count += 1

    return path, {"active": len(active_idx), "total": len(obstacles),
                  "active_idx": sorted(active_idx),
                  "active_select_ms": round((t_active - t0) * 1000.0, 2),
                  "graph_search_ms": round(graph_search_ms, 2),
                  "validation_ms": round(validation_ms, 2),
                  "replan_count": replan_count,
                  "total_ms": round((time.perf_counter() - t0) * 1000.0, 2)}