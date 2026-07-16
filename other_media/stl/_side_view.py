# Seitenansichten, Schraegsichten + Querschnitte einer binaeren STL als PNG rendern
# (Selbstkontrolle der Relief-Skripte ohne Slicer).
# Orthografische Projektion per dichter Punktwolke (Vertices + Kantenmittel + Zentroide),
# tiefen-schattiert. Rote Linie = globale Maximalhoehe (macht zu niedrige Raender sichtbar).
#
# Aufruf:
#   python _side_view.py datei.stl [weitere.stl ...] [--ppm 8] [--zx 1.0]
# Ausgabe:
#   <name>_side.png    – 4 Streifen: Ansicht vorn, Schnitt Y-Mitte, Ansicht rechts,
#                        Schnitt X-Mitte (mit roter Referenzlinie auf max. Hoehe)
#   <name>_oblique.png – Schraegsichten-Raster: Zeilen = Blickrichtung 0/90/180/270 Grad,
#                        Spalten = Elevation 22.5 / 45 Grad
import argparse
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _analyze_z import read_binary_stl


def densify(tris):
    """Punktwolke: Ecken + Kantenmittel + Zentroide (fuer grob tesselierte Flaechen)."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    return np.concatenate([
        v0, v1, v2,
        (v0 + v1) / 2, (v1 + v2) / 2, (v2 + v0) / 2,
        (v0 + v1 + v2) / 3,
    ])


def splat(u, z, d, ppm, zx, section=False):
    """Punkte auf (u,z)-Ebene rastern (2x2-Splat gegen Loecher);
    Schattierung nach Tiefe d (nah = hell)."""
    umin, zmin = u.min(), z.min()
    W = int(np.ceil((u.max() - umin) * ppm)) + 4
    Hpx = int(np.ceil((z.max() - zmin) * ppm * zx)) + 4
    px = np.clip(((u - umin) * ppm).astype(int) + 1, 0, W - 2)
    py = np.clip(Hpx - 3 - ((z - zmin) * ppm * zx).astype(int), 0, Hpx - 2)
    if section:
        img = np.zeros((Hpx, W), dtype=np.uint8)
        img[py, px] = 255
        return img, zmin
    depth = np.full(Hpx * W, np.inf, dtype=np.float64)
    for dy in (0, 1):
        for dx in (0, 1):
            np.minimum.at(depth, (py + dy) * W + (px + dx), d)
    hit = np.isfinite(depth)
    dn = depth[hit]
    lo, hi = np.percentile(dn, 2), np.percentile(dn, 98)
    shadev = 220 - 150 * np.clip((dn - lo) / max(hi - lo, 1e-9), 0, 1)
    buf = np.zeros(Hpx * W, dtype=np.float32)
    buf[hit] = shadev
    return buf.reshape(Hpx, W).astype(np.uint8), zmin


def to_rgb(img):
    return np.repeat(img[:, :, None], 3, axis=2)


def draw_zline(rgb, zline, zmin, ppm, zx, color=(255, 60, 60)):
    """Horizontale Referenzlinie bei Hoehe zline einzeichnen."""
    Hpx = rgb.shape[0]
    row = Hpx - 2 - int((zline - zmin) * ppm * zx)
    if 0 <= row < Hpx:
        rgb[row, :, 0] = color[0]
        rgb[row, :, 1] = color[1]
        rgb[row, :, 2] = color[2]
    return rgb


def render_side(pts, a, up, b, ppm, zx, zref, section=None):
    """Seitenansicht bzw. Querschnitt entlang Achse b, mit Referenzlinie."""
    u, z, d = pts[:, a], pts[:, up], pts[:, b]
    if section is not None:
        m = np.abs(d - section[0]) <= section[1]
        img, zmin = splat(u[m], z[m], None, ppm, zx, section=True)
    else:
        img, zmin = splat(u, z, d, ppm, zx)
    return draw_zline(to_rgb(img), zref, zmin, ppm, zx)


def render_oblique(pts, a, b, up, phi_deg, elev_deg, ppm):
    """Schraegsicht: Azimut phi (um Hochachse), dann Kippung elev (0=seitlich, 90=oben)."""
    P = np.stack([pts[:, a], pts[:, b], pts[:, up]], axis=1)
    P = P - P.mean(axis=0)
    ph = np.deg2rad(phi_deg)
    th = np.deg2rad(elev_deg)
    Rz = np.array([[np.cos(ph), -np.sin(ph), 0], [np.sin(ph), np.cos(ph), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(th), -np.sin(th)], [0, np.sin(th), np.cos(th)]])
    Q = P @ Rz.T @ Rx.T
    img, _ = splat(Q[:, 0], Q[:, 2], Q[:, 1], ppm, 1.0)
    return to_rgb(img)


def grid(cells, gap=8):
    """Zellen [Zeile][Spalte] zu einem Bild zusammensetzen."""
    rows = []
    for row in cells:
        h = max(c.shape[0] for c in row)
        w = sum(c.shape[1] for c in row) + gap * (len(row) - 1)
        strip = np.full((h, w, 3), 30, dtype=np.uint8)
        xx = 0
        for c in row:
            strip[:c.shape[0], xx:xx + c.shape[1]] = c
            xx += c.shape[1] + gap
        rows.append(strip)
    W = max(r.shape[1] for r in rows)
    total = sum(r.shape[0] for r in rows) + gap * (len(rows) - 1)
    out = np.full((total, W, 3), 30, dtype=np.uint8)
    yy = 0
    for r in rows:
        out[yy:yy + r.shape[0], :r.shape[1]] = r
        yy += r.shape[0] + gap
    return out


def process(path, ppm, zx):
    verts = read_binary_stl(path).astype(np.float64)
    tris = verts.reshape(-1, 3, 3)
    pts = densify(tris)
    dims = pts.max(axis=0) - pts.min(axis=0)
    up = int(np.argmin(dims))
    a, b = [ax for ax in range(3) if ax != up]
    zref = pts[:, up].max()
    mid_a = (pts[:, a].max() + pts[:, a].min()) / 2
    mid_b = (pts[:, b].max() + pts[:, b].min()) / 2

    side = grid([
        [render_side(pts, a, up, b, ppm, zx, zref)],
        [render_side(pts, a, up, b, ppm, zx, zref, section=(mid_b, 0.6))],
        [render_side(pts, b, up, a, ppm, zx, zref)],
        [render_side(pts, b, up, a, ppm, zx, zref, section=(mid_a, 0.6))],
    ])
    side_path = os.path.splitext(path)[0] + "_side.png"
    Image.fromarray(side).save(side_path)

    # Schraegsichten als EINZELNE grosse Dateien (im Kachel-Raster waren Defekte
    # wie ein lueckenhafter Rand nicht erkennbar)
    stem = os.path.splitext(path)[0]
    obl_paths = []
    for phi in (0, 90, 180, 270):
        for elev in (22.5, 45.0):
            img = render_oblique(pts, a, b, up, phi, elev, ppm)
            p = f"{stem}_ob_az{phi:03d}_e{int(elev)}.png"
            Image.fromarray(img).save(p)
            obl_paths.append(os.path.basename(p))

    print(f"{os.path.basename(path)}: {os.path.basename(side_path)} + {len(obl_paths)} Schraegsichten "
          f"({obl_paths[0]} ... az=Blickrichtung, e=Elevation; BBox {dims[a]:.1f} x {dims[b]:.1f} x {dims[up]:.2f})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Seitenansichten, Schraegsichten und Querschnitte einer STL als PNG.")
    ap.add_argument("files", nargs="+", help="STL-Dateien")
    ap.add_argument("--ppm", type=float, default=8.0, help="Pixel pro mm horizontal (Default 8)")
    ap.add_argument("--zx", type=float, default=1.0, help="Z-Ueberhoehung der Seitenansichten (Default 1.0)")
    args = ap.parse_args()
    for p in args.files:
        process(p, args.ppm, args.zx)
