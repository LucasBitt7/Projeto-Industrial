"""Region renderer (matplotlib). Visual QA only — never a source of coordinates."""
from __future__ import annotations

import os

import ezdxf


def render_region(path: str, out_png: str, bbox: list | None = None, max_entities: int = 8000) -> dict:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_aspect("equal")
    n = 0
    for e in msp:
        if n >= max_entities:
            break
        try:
            t = e.dxftype()
            layer = str(e.dxf.layer)
            if t == "LINE":
                ax.plot([e.dxf.start.x, e.dxf.end.x], [e.dxf.start.y, e.dxf.end.y], "k-", lw=0.6)
            elif t == "LWPOLYLINE":
                pts = [(float(x), float(y)) for x, y, *_ in e.get_points()]
                if pts:
                    xs, ys = zip(*pts)
                    ax.plot(xs, ys, "k-", lw=0.6)
                    if e.closed:
                        ax.plot([xs[-1], xs[0]], [ys[-1], ys[0]], "k-", lw=0.6)
            elif t == "CIRCLE":
                ax.add_patch(plt.Circle((float(e.dxf.center.x), float(e.dxf.center.y)),
                                        float(e.dxf.radius), fill=False, lw=0.6))
            elif t == "INSERT":
                x, y = float(e.dxf.insert.x), float(e.dxf.insert.y)
                ax.plot(x, y, "bs", ms=4)
                ax.text(x, y, str(e.dxf.name)[:8], fontsize=5, color="blue")
            elif t in ("TEXT", "MTEXT"):
                p = e.dxf.insert
                content = (str(e.dxf.text) if t == "TEXT" else str(e.text))[:24]
                ax.text(float(p.x), float(p.y), content, fontsize=5, color="darkred")
            n += 1
        except Exception:
            continue
    if bbox:
        ax.set_xlim(bbox[0], bbox[2])
        ax.set_ylim(bbox[1], bbox[3])
        ax.add_patch(Rectangle((bbox[0], bbox[1]), bbox[2] - bbox[0], bbox[3] - bbox[1],
                               fill=False, edgecolor="red", lw=1.2, linestyle="--"))
    else:
        ax.autoscale()
    ax.set_title(f"{os.path.basename(path)} (visual QA only — CAD data is authoritative)")
    os.makedirs(os.path.dirname(os.path.abspath(out_png)) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png, dpi=130)
    plt.close(fig)
    return {"png": os.path.abspath(out_png), "entities_drawn": n,
            "warning": "Coordinates must never be read from this PNG; use CAD data."}
