"""Core data models: handles as identity, bboxes, plan manifests, operation results."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class BBox:
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def width(self) -> float:
        return self.xmax - self.xmin

    def height(self) -> float:
        return self.ymax - self.ymin

    def contains_point(self, x: float, y: float, tol: float = 0.0) -> bool:
        return (self.xmin - tol) <= x <= (self.xmax + tol) and (self.ymin - tol) <= y <= (self.ymax + tol)

    def intersects(self, other: "BBox", tol: float = 0.0) -> bool:
        return not (
            self.xmax + tol < other.xmin or other.xmax + tol < self.xmin
            or self.ymax + tol < other.ymin or other.ymax + tol < self.ymin
        )

    def expanded(self, amount: float) -> "BBox":
        return BBox(self.xmin - amount, self.ymin - amount, self.xmax + amount, self.ymax + amount)

    def to_list(self) -> list:
        return [self.xmin, self.ymin, self.xmax, self.ymax]

    @staticmethod
    def from_list(v: list | tuple) -> "BBox":
        return BBox(float(v[0]), float(v[1]), float(v[2]), float(v[3]))

    def center(self) -> tuple[float, float]:
        return ((self.xmin + self.xmax) / 2.0, (self.ymin + self.ymax) / 2.0)


@dataclass
class DrawingIdentity:
    absolute_path: str
    basename: str
    sha256: str
    size_bytes: int
    mtime: float
    insunits: int
    extents: list
    entity_count: int
    revision_token: str  # sha256 of canonical fingerprint; changes on every write

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CadEntityRef:
    handle: str
    type: str
    layer: str
    bbox: list  # [xmin, ymin, xmax, ymax]
    insertion_point: list | None = None
    rotation: float = 0.0
    block_name: str | None = None
    attributes: dict = field(default_factory=dict)
    text: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Scope:
    allowed_bbox: list | None = None  # [xmin,ymin,xmax,ymax]
    allowed_handles: list | None = None
    allowed_layers: list | None = None
    allowed_entity_types: list | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    def is_empty(self) -> bool:
        return not (self.allowed_bbox or self.allowed_handles or self.allowed_layers or self.allowed_entity_types)


@dataclass
class PlannedOperation:
    op: str
    params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PlanManifest:
    drawing_identity: dict
    scope: dict
    entities: list = field(default_factory=list)  # resolved CadEntityRef dicts
    template_refs: list = field(default_factory=list)
    operations: list = field(default_factory=list)  # PlannedOperation dicts
    expected_changes: dict = field(default_factory=dict)
    protected_regions: list = field(default_factory=list)
    validations: list = field(default_factory=list)
    plan_hash: str = ""

    def compute_hash(self) -> str:
        payload = {
            "drawing_identity": self.drawing_identity,
            "scope": self.scope,
            "entities": self.entities,
            "template_refs": self.template_refs,
            "operations": self.operations,
            "expected_changes": self.expected_changes,
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def finalize(self) -> "PlanManifest":
        self.plan_hash = self.compute_hash()
        return self

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class OperationResult:
    ok: bool
    operation_id: str
    drawing_before: dict | None = None
    drawing_after: dict | None = None
    modified_handles: list = field(default_factory=list)
    created_handles: list = field(default_factory=list)
    deleted_handles: list = field(default_factory=list)
    handle_map: dict = field(default_factory=dict)
    expected_state: dict | None = None
    actual_state: dict | None = None
    validations: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    artifact_paths: dict = field(default_factory=dict)
    error_code: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CadTemplate:
    template_id: str
    name: str
    source_drawing: str
    anchor: list  # [x, y] reference point
    handles: list  # member handles in source drawing
    relative_entities: list = field(default_factory=list)  # canonical relative geometry
    bbox: list = field(default_factory=list)
    expected_layers: list = field(default_factory=list)
    semantic_type: str = "GENERIC"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TransactionManifest:
    transaction_id: str
    source_path: str
    source_sha256: str
    working_path: str
    output_path: str
    allowed_bbox: list | None = None
    allowed_handles: list | None = None
    allowed_layers: list | None = None
    operations: list = field(default_factory=list)
    validation_results: list = field(default_factory=list)
    final_sha256: str | None = None
    status: str = "OPEN"  # OPEN | PASS | FAIL | DISCARDED
    plan_hash: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RoomRules:
    room_id: str
    bbox_or_polygon: dict  # {"bbox": [...]} or {"polygon": [[x,y],...]}
    allowed_circuits: list = field(default_factory=list)
    required_circuits: list = field(default_factory=list)
    panel: str | None = None
    allowed_layers: list = field(default_factory=list)
    required_points: list = field(default_factory=list)
    forbidden_circuits: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
