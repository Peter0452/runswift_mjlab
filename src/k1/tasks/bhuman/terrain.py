"""B-Human's training field (Booster Gym ``utils/terrain.py``, ``K1_Ball.yaml``).

One heightfield: ``num_terrains`` strips of ``terrain_width`` x
``terrain_length`` m side by side along x, typed by ``terrain_proportions``
(plane / random uniform / discrete obstacles), inside a flat ``border_size``
border. Heights are int16 multiples of ``vertical_scale`` on a
``horizontal_scale`` grid, generated like Isaac Gym's ``terrain_utils``.

All worlds share the one field (mjlab worlds don't interact), so robots are
spread over it at reset like B-Human's env origins. ``FieldHeights`` answers
B-Human's ``terrain_heights`` (bilinear on the grid) from the compiled model.

Not ported: per-5 m-patch ground friction (one MuJoCo geom has one friction);
the foot friction is randomized per env instead.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

import mujoco
import numpy as np
import torch
from scipy import interpolate

from mjlab.terrains.terrain_generator import (
  SubTerrainCfg,
  TerrainGeneratorCfg,
  TerrainGeometry,
  TerrainOutput,
)


def _random_uniform(
  rng: np.random.Generator,
  shape: tuple[int, int],
  hs: float,
  vs: float,
  min_height: float,
  max_height: float,
  step: float,
  downsampled_scale: float,
) -> np.ndarray:
  lo, hi, st = int(min_height / vs), int(max_height / vs), int(step / vs)
  heights = np.arange(lo, hi + st, st)
  w_m, l_m = shape[0] * hs, shape[1] * hs
  coarse = rng.choice(
    heights, (int(w_m / downsampled_scale), int(l_m / downsampled_scale))
  )
  x = np.linspace(0, w_m, coarse.shape[0])
  y = np.linspace(0, l_m, coarse.shape[1])
  f = interpolate.RegularGridInterpolator((x, y), coarse, method="linear")
  xx, yy = np.meshgrid(
    np.linspace(0, w_m, shape[0]), np.linspace(0, l_m, shape[1]), indexing="ij"
  )
  return np.rint(f((xx, yy))).astype(np.int16)


def _discrete_obstacles(
  rng: np.random.Generator,
  shape: tuple[int, int],
  hs: float,
  vs: float,
  max_height: float,
  min_size: float,
  max_size: float,
  num_rects: int,
  platform_size: float,
) -> np.ndarray:
  field = np.zeros(shape, dtype=np.int16)
  h = int(max_height / vs)
  lo, hi, plat = int(min_size / hs), int(max_size / hs), int(platform_size / hs)
  heights = [-h, -h // 2, h // 2, h]
  sizes = range(lo, hi, 4)
  for _ in range(num_rects):
    w, ln = int(rng.choice(sizes)), int(rng.choice(sizes))
    i0 = int(rng.choice(range(0, shape[0] - w, 4)))
    j0 = int(rng.choice(range(0, shape[1] - ln, 4)))
    field[i0 : i0 + w, j0 : j0 + ln] = rng.choice(heights)
  x1, y1 = (shape[0] - plat) // 2, (shape[1] - plat) // 2
  field[x1 : x1 + plat, y1 : y1 + plat] = 0
  return field


@dataclass(kw_only=True)
class BHumanFieldTerrainCfg(SubTerrainCfg):
  num_terrains: int = 8
  terrain_width: float = 10.0
  terrain_length: float = 20.0
  border_size: float = 15.0
  terrain_proportions: tuple[float, ...] = (0.6, 0.0, 0.2, 0.2, 0.0)
  """[plane, slope, random, discrete, stairs]; slope / stairs not ported."""
  random_height: float = 0.075
  discrete_height: float = 0.02
  horizontal_scale: float = 0.1
  vertical_scale: float = 0.005

  def __post_init__(self) -> None:
    p = self.terrain_proportions
    if p[1] > 0 or p[4] > 0:
      raise ValueError("Slope and stairs strips are not ported.")
    self.size = self.field_size

  @property
  def field_size(self) -> tuple[float, float]:
    return (
      self.num_terrains * self.terrain_width + 2 * self.border_size,
      self.terrain_length + 2 * self.border_size,
    )

  def function(
    self, difficulty: float, spec: mujoco.MjSpec, rng: np.random.Generator
  ) -> TerrainOutput:
    del difficulty
    hs, vs = self.horizontal_scale, self.vertical_scale
    border = int(self.border_size / hs)
    tw, tl = int(self.terrain_width / hs), int(self.terrain_length / hs)
    raw = np.zeros((self.num_terrains * tw + 2 * border, tl + 2 * border), np.int16)
    cum = np.cumsum(self.terrain_proportions) / np.sum(self.terrain_proportions)
    bounds = self.num_terrains * cum
    for i in range(self.num_terrains):
      if i < bounds[0]:
        sub = np.zeros((tw, tl), np.int16)
      elif i < bounds[2]:
        sub = _random_uniform(
          rng,
          (tw, tl),
          hs,
          vs,
          -0.5 * self.random_height,
          0.5 * self.random_height,
          step=0.005,
          downsampled_scale=0.2,
        )
      else:
        sub = _discrete_obstacles(
          rng,
          (tw, tl),
          hs,
          vs,
          self.discrete_height,
          min_size=1.0,
          max_size=2.0,
          num_rects=20,
          platform_size=3.0,
        )
      raw[border + i * tw : border + (i + 1) * tw, border : border + tl] = sub

    lo, hi = int(raw.min()), int(raw.max())
    span = max(hi - lo, 1)
    # MuJoCo hfield: rows run along y, columns along x.
    normalized = ((raw - lo) / span).T.astype(np.float32)
    uid = uuid.uuid4().hex
    nx, ny = raw.shape
    size_x, size_y = (nx - 1) * hs, (ny - 1) * hs
    field = spec.add_hfield(
      name=f"bhuman_field_{uid}",
      size=[size_x / 2, size_y / 2, span * vs, 0.1],
      nrow=ny,
      ncol=nx,
      userdata=normalized.flatten().tolist(),
    )
    geom = spec.body("terrain").add_geom(
      type=mujoco.mjtGeom.mjGEOM_HFIELD,
      hfieldname=field.name,
      pos=[size_x / 2, size_y / 2, lo * vs],
      rgba=(0.35, 0.55, 0.35, 1.0),
    )
    origin = np.array([size_x / 2, size_y / 2, 0.0])
    return TerrainOutput(origin=origin, geometries=[TerrainGeometry(geom=geom)])


def bhuman_field_generator_cfg(**overrides) -> TerrainGeneratorCfg:
  sub = BHumanFieldTerrainCfg(**overrides)
  return TerrainGeneratorCfg(
    size=sub.field_size,
    num_rows=1,
    num_cols=1,
    border_width=0.0,
    curriculum=False,
    color_scheme="none",
    sub_terrains={"bhuman_field": sub},
  )


class FieldHeights:
  """Ground height under world xy points: bilinear on the field's grid.

  Also gives the inner field bounds (B-Human's ``env_width`` x ``env_length``
  area inside the border), used for spawning and for wrapping robots and balls
  that leave it. Without a heightfield (plane) heights are 0 and nothing wraps.
  """

  def __init__(self, mj_model: mujoco.MjModel, border_size: float, device: str) -> None:
    self.device = device
    self.border = border_size
    ids = [
      g
      for g in range(mj_model.ngeom)
      if mj_model.geom_type[g] == mujoco.mjtGeom.mjGEOM_HFIELD
    ]
    self.enabled = len(ids) == 1
    if not self.enabled:
      return
    g = ids[0]
    h = int(mj_model.geom_dataid[g])
    nrow, ncol = int(mj_model.hfield_nrow[h]), int(mj_model.hfield_ncol[h])
    adr = int(mj_model.hfield_adr[h])
    data = mj_model.hfield_data[adr : adr + nrow * ncol].reshape(nrow, ncol)
    size = mj_model.hfield_size[h]
    pos = mj_model.geom_pos[g]
    # (x, y) grid, like B-Human's height_field_raw (in meters).
    grid = pos[2] + data.T * size[2]
    self.grid = torch.tensor(grid, dtype=torch.float, device=device)
    self.lo = torch.tensor(
      [pos[0] - size[0], pos[1] - size[1]], dtype=torch.float, device=device
    )
    self.step = torch.tensor(
      [2 * size[0] / (ncol - 1), 2 * size[1] / (nrow - 1)],
      dtype=torch.float,
      device=device,
    )
    self.inner_lo = self.lo + border_size
    extent = torch.tensor([2 * size[0], 2 * size[1]], dtype=torch.float, device=device)
    self.inner_hi = self.lo + extent - border_size

  def __call__(self, xy: torch.Tensor) -> torch.Tensor:
    if not self.enabled:
      return torch.zeros(xy.shape[:-1], device=xy.device)
    f = (xy[..., :2] - self.lo) / self.step
    nx, ny = self.grid.shape
    x1 = torch.floor(f[..., 0]).long().clamp(0, nx - 2)
    y1 = torch.floor(f[..., 1]).long().clamp(0, ny - 2)
    tx = (f[..., 0] - x1).clamp(0.0, 1.0)
    ty = (f[..., 1] - y1).clamp(0.0, 1.0)
    g = self.grid
    return (
      (1 - tx) * (1 - ty) * g[x1, y1]
      + tx * (1 - ty) * g[x1 + 1, y1]
      + (1 - tx) * ty * g[x1, y1 + 1]
      + tx * ty * g[x1 + 1, y1 + 1]
    )
