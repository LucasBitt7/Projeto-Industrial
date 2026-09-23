"""Bridge: single entry for OpenCode TS tools. stdin JSON -> stdout JSON (standard envelope)."""
from __future__ import annotations

import json
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def envelope(ok: bool, **kw) -> dict:
    d = {"ok": ok}
    d.update(kw)
    return d


def main():
    try:
        op = sys.argv[1] if len(sys.argv) > 1 else ""
        args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        os.environ.setdefault("CAD_BACKEND", args.pop("backend", "") or os.environ.get("CAD_BACKEND", "file"))
        if op == "inspect":
            from cad_agent.drawing import drawing_identity
            print(json.dumps(envelope(True, drawing=drawing_identity(args["drawing"]).to_dict())))
        elif op == "find_entities":
            from cad_agent.entities import find_entities
            refs = find_entities(args["drawing"], layer=args.get("layer"), etype=args.get("etype"),
                                 block_name=args.get("block_name"), text_regex=args.get("text_regex"),
                                 bbox=args.get("bbox"), limit=int(args.get("limit", 200)))
            print(json.dumps(envelope(True, count=len(refs), entities=refs)))
        elif op == "get_entity":
            from cad_agent.entities import get_entity
            print(json.dumps(envelope(True, entity=get_entity(args["drawing"], args["handle"]))))
        elif op == "find_blocks":
            from cad_agent.entities import find_blocks
            refs = find_blocks(args["drawing"], name_regex=args.get("name_regex"),
                               bbox=args.get("bbox"), limit=int(args.get("limit", 200)))
            print(json.dumps(envelope(True, count=len(refs), entities=refs)))
        elif op == "find_walls":
            from cad_agent.walls import find_walls
            print(json.dumps(envelope(True, walls=find_walls(args["drawing"], args.get("wall_layers"),
                                                             args.get("bbox")))))
        elif op == "capture_template":
            from cad_agent.templates import capture_template
            print(json.dumps(envelope(True, template=capture_template(
                args["drawing"], args["handles"], args.get("name", "tpl"),
                args.get("semantic_type", "GENERIC"), args.get("template_id")))))
        elif op == "clone_template":
            from cad_agent.session import require_expected_revision
            from cad_agent.templates import clone_template
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            print(json.dumps(clone_template(args["drawing"], args["template_id"],
                                            float(args.get("dx", 0)), float(args.get("dy", 0)),
                                            float(args.get("angle_deg", 0.0)),
                                            args.get("anchor_override"), args.get("new_label"),
                                            args.get("out_path"), args.get("expected_revision"))))
        elif op == "clone_parametrized":
            from cad_agent.session import require_expected_revision
            from cad_agent.parametrize import clone_parametrized
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            print(json.dumps(clone_parametrized(
                args["drawing"], args["template_id"],
                float(args.get("dx", 0)), float(args.get("dy", 0)),
                float(args.get("angle_deg", 0.0)), args.get("anchor_override"),
                args.get("text_map"), args.get("handle_rules"), args.get("extra_groups"),
                args.get("extra_texts"), args.get("member_edits"),
                args.get("out_path"), args.get("expected_revision"),
                bool(args.get("dry_run", False)))))
        elif op == "move_along_wall":
            from cad_agent.session import require_expected_revision
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            from cad_agent.electrical import electrical_move_outlet_along_wall
            print(json.dumps(electrical_move_outlet_along_wall(
                args["drawing"], args["entity_handle"], args["wall_handle"],
                float(args["displacement"]), args.get("unit", "mm"), int(args.get("direction", 1)),
                args.get("expected_revision"), bool(args.get("dry_run", False)),
                args.get("out_path"), args.get("allowed_bbox"))))
        elif op == "place_panel":
            from cad_agent.session import require_expected_revision
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            from cad_agent.electrical import electrical_place_panel_on_wall
            print(json.dumps(electrical_place_panel_on_wall(
                args["drawing"], args["template_id"], args["wall_handle"],
                args.get("position_rule", "free_interval_nearest_to_handle"),
                float(args.get("clearance", 10.0)), args.get("new_label"),
                args.get("expected_revision"), bool(args.get("dry_run", False)),
                args.get("out_path"), args.get("near_handle"))))
        elif op == "route_conduit":
            from cad_agent.session import require_expected_revision
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            from cad_agent.electrical import electrical_route_conduit
            print(json.dumps(electrical_route_conduit(
                args["drawing"], args["source_handle"], args["destination_handles"],
                args.get("layer", "ELETRODUTO"), float(args.get("clearance", 5.0)),
                args.get("expected_revision"), bool(args.get("dry_run", False)), args.get("out_path"))))
        elif op == "create_callout":
            from cad_agent.session import require_expected_revision
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            from cad_agent.electrical import electrical_create_callout
            print(json.dumps(electrical_create_callout(
                args["drawing"], args["conduit_edge"], args["circuits"], args["conductor_spec"],
                args.get("placement", "above"), args.get("expected_revision"),
                bool(args.get("dry_run", False)), args.get("out_path"))))
        elif op == "delete_guarded":
            from cad_agent.session import require_expected_revision
            from cad_agent.fiacao import delete_entities_guarded
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            print(json.dumps(delete_entities_guarded(
                args["drawing"], list(args.get("handles", [])), args.get("identity"),
                args.get("expected_count"),
                args.get("expected_revision"), bool(args.get("dry_run", False)),
                args.get("out_path"))))
        elif op == "create_fiacao_callout":
            from cad_agent.session import require_expected_revision
            from cad_agent.fiacao import create_fiacao_callout_bound
            require_expected_revision(args.get("expected_revision"), args["drawing"])
            print(json.dumps(create_fiacao_callout_bound(
                args["drawing"], args["source_handle"], args["circuit"],
                args["conductor_spec"], args["edge_p1"], args["edge_p2"],
                args["insert_xy"], float(args.get("max_dist", 0.005)),
                args.get("expected_revision"), bool(args.get("dry_run", False)),
                args.get("out_path"))))
        elif op == "detect_collisions":
            from cad_agent.entities import find_entities
            from cad_agent.collisions import detect_collisions
            refs = find_entities(args["drawing"], bbox=args.get("bbox"), limit=int(args.get("limit", 2000)))
            print(json.dumps(envelope(True, collisions=detect_collisions(
                refs, float(args.get("clearance", 0.0))))))
        elif op == "validate_room":
            from cad_agent.rooms import validate_room
            print(json.dumps(validate_room(args["drawing"], args["room"])))
        elif op == "validate_network":
            from cad_agent.conduit import build_network_from_layer, validate_network_graph
            net = build_network_from_layer(args["drawing"], args.get("layer", "ELETRODUTO"))
            print(json.dumps(validate_network_graph(net["graph"])))
        elif op == "validate_scope":
            from cad_agent.validators import validate_no_changes_outside_scope
            print(json.dumps(validate_no_changes_outside_scope(
                args["before"], args["after"], args.get("scope", {}))))
        elif op == "validate_callouts":
            from cad_agent.callouts import validate_callouts
            print(json.dumps(validate_callouts(args["drawing"], args.get("layer", "ELE-CALLOUT"))))
        elif op == "template_integrity":
            from cad_agent.templates import validate_template_integrity
            print(json.dumps(validate_template_integrity(
                args["drawing"], args["handles"], args.get("semantic_type", "PANEL_QDF"),
                float(args.get("eps", 1.0)))))
        elif op == "render":
            from cad_agent.render import render_region
            print(json.dumps(envelope(True, **render_region(args["drawing"], args["out"], args.get("bbox")))))
        elif op == "plan_finalize":
            from cad_agent.models import PlanManifest
            m = PlanManifest(drawing_identity=args["drawing_identity"], scope=args.get("scope", {}),
                             entities=args.get("entities", []), template_refs=args.get("template_refs", []),
                             operations=args.get("operations", []),
                             expected_changes=args.get("expected_changes", {}),
                             protected_regions=args.get("protected_regions", []),
                             validations=args.get("validations", []))
            m.finalize()
            print(json.dumps(envelope(True, plan=m.to_dict())))
        elif op == "route":
            from cad_agent.router import classify, pipeline_for
            r = classify(args.get("prompt", ""))
            print(json.dumps(envelope(True, route=r["route"], cad_task=r["cad_task"],
                                      confidence=r["confidence"], reasons=r["reasons"],
                                      pipeline=pipeline_for(r["route"]))))
        elif op == "guard_check":
            from cad_agent.guard import guard_check
            print(json.dumps(guard_check(args.get("command", ""))))
        elif op == "current_artifact":
            from cad_agent.session import resolve_current_artifact
            print(json.dumps(resolve_current_artifact(args.get("project"))))
        else:
            print(json.dumps(envelope(False, error_code="UNKNOWN_OP", error=f"unknown op {op}")))
            sys.exit(2)
    except Exception as ex:  # structured, never raw-only
        code = getattr(ex, "code", "VALIDATION_FAIL")
        print(json.dumps(envelope(False, error_code=code, error=f"{ex}",
                                  details=getattr(ex, "details", {}),
                                  traceback=traceback.format_exc(limit=5))))
        sys.exit(1)


if __name__ == "__main__":
    main()
