"""CLI for diagnosis without the LLM: inspect/entity/fingerprint/validate/render/network/transaction-status."""
from __future__ import annotations

import argparse
import json
import sys


def cmd_inspect(args):
    from .drawing import drawing_identity
    from .backends.base import resolve_backend
    be = resolve_backend(args.backend)
    ident = be.open_identity(args.drawing)
    print(json.dumps(ident, indent=2, ensure_ascii=False))


def cmd_entity(args):
    from .entities import get_entity
    print(json.dumps(get_entity(args.drawing, args.handle), indent=2, ensure_ascii=False))


def cmd_find(args):
    from .entities import find_entities
    refs = find_entities(args.drawing, layer=args.layer, etype=args.etype,
                         block_name=args.block, text_regex=args.text, limit=args.limit)
    print(json.dumps({"count": len(refs), "entities": refs}, indent=2, ensure_ascii=False))


def cmd_fingerprint(args):
    from .drawing import drawing_fingerprint
    print(json.dumps(drawing_fingerprint(args.drawing), indent=2)[:4000])


def cmd_validate(args):
    from .rooms import validate_project_scope
    from .callouts import validate_callouts
    from .conduit import build_network_from_layer, validate_network_graph
    import yaml
    cfg = {}
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    out = {}
    rooms = cfg.get("room_rules", [])
    if rooms:
        out["rooms"] = validate_project_scope(args.drawing, rooms,
                                              cfg.get("circuit_regex", r"\bT\d{1,3}\b"))
    out["callouts"] = validate_callouts(args.drawing, cfg.get("layers", {}).get("callout", "ELE-CALLOUT"))
    layer = cfg.get("layers", {}).get("conduit", "ELETRODUTO")
    try:
        net = build_network_from_layer(args.drawing, layer)
        out["network"] = validate_network_graph(net["graph"])
    except Exception as ex:
        out["network"] = {"ok": True, "note": f"no conduit layer {layer}: {ex}"}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    ok = all(v.get("ok", True) for v in out.values() if isinstance(v, dict))
    sys.exit(0 if ok else 2)


def cmd_render(args):
    from .render import render_region
    bbox = [float(x) for x in args.bbox.split(",")] if args.bbox else None
    print(json.dumps(render_region(args.drawing, args.out, bbox), indent=2))


def cmd_network(args):
    from .conduit import build_network_from_layer, validate_network_graph
    net = build_network_from_layer(args.drawing, args.layer)
    v = validate_network_graph(net["graph"])
    print(json.dumps({"nodes": len(net["graph"]["nodes"]), "edges": len(net["graph"]["edges"]),
                      "validation": v}, indent=2))


def cmd_tx_status(args):
    import os
    p = os.path.join(".cad-agent", "transactions", args.id, "manifest.json")
    if not os.path.isfile(p):
        print(json.dumps({"ok": False, "error": "transaction not found", "id": args.id}))
        sys.exit(1)
    with open(p, encoding="utf-8") as f:
        print(f.read())


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cad_agent", description="Deterministic electrical CAD toolkit")
    ap.add_argument("--backend", default="file", help="file | autocad_live (explicit, no auto)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspect"); p.add_argument("drawing"); p.set_defaults(f=cmd_inspect)
    p = sub.add_parser("entity"); p.add_argument("drawing"); p.add_argument("handle"); p.set_defaults(f=cmd_entity)
    p = sub.add_parser("find"); p.add_argument("drawing")
    p.add_argument("--layer", default=None); p.add_argument("--etype", default=None)
    p.add_argument("--block", default=None); p.add_argument("--text", default=None)
    p.add_argument("--limit", type=int, default=50); p.set_defaults(f=cmd_find)
    p = sub.add_parser("fingerprint"); p.add_argument("drawing"); p.set_defaults(f=cmd_fingerprint)
    p = sub.add_parser("validate"); p.add_argument("drawing"); p.add_argument("config", nargs="?")
    p.set_defaults(f=cmd_validate)
    p = sub.add_parser("render"); p.add_argument("drawing"); p.add_argument("--out", required=True)
    p.add_argument("--bbox", default=None); p.set_defaults(f=cmd_render)
    p = sub.add_parser("network"); p.add_argument("drawing"); p.add_argument("--layer", default="ELETRODUTO")
    p.set_defaults(f=cmd_network)
    p = sub.add_parser("transaction-status"); p.add_argument("id"); p.set_defaults(f=cmd_tx_status)
    args = ap.parse_args(argv)
    args.f(args)


if __name__ == "__main__":
    main()
