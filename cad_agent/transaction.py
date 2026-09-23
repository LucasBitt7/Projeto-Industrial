"""File transaction: copy -> temp working -> apply -> readback -> validate -> atomic publish."""
from __future__ import annotations

import os
import shutil
import tempfile
import uuid

from .audit import log_event
from .drawing import drawing_identity, sha256_file
from .errors import CadError
from .models import TransactionManifest
from .validators import validate_no_changes_outside_scope


class FileTransaction:
    def __init__(self, source_path: str, output_path: str, scope: dict | None = None,
                 plan_hash: str | None = None, transaction_id: str | None = None):
        if not os.path.isfile(source_path):
            raise CadError("DRAWING_NOT_FOUND", f"Source not found: {source_path}", {"path": source_path})
        # NEVER edit production originals in place: working copy is mandatory
        self.source_path = os.path.abspath(source_path)
        self.output_path = os.path.abspath(output_path)
        if self.output_path == self.source_path:
            raise CadError("OUT_OF_SCOPE",
                           "Refusing to overwrite the source file in place. "
                           "Provide a distinct output_path (versioned artifact).",
                           {"source": self.source_path})
        self.scope = scope or {}
        self.plan_hash = plan_hash
        self.transaction_id = transaction_id or uuid.uuid4().hex[:12]
        self.workdir = tempfile.mkdtemp(prefix=f"cadtx_{self.transaction_id}_")
        self.working_path = os.path.join(self.workdir, "working.dxf")
        shutil.copy2(self.source_path, self.working_path)
        self.source_sha = sha256_file(self.source_path)
        self.operations: list = []
        self.validations: list = []
        self.manifest = TransactionManifest(
            transaction_id=self.transaction_id, source_path=self.source_path,
            source_sha256=self.source_sha, working_path=self.working_path,
            output_path=self.output_path,
            allowed_bbox=self.scope.get("allowed_bbox"), allowed_handles=self.scope.get("allowed_handles"),
            allowed_layers=self.scope.get("allowed_layers"), plan_hash=plan_hash)

    def record(self, op: str, detail: dict):
        self.operations.append({"op": op, **detail})
        self.manifest.operations = self.operations

    def commit(self, extra_validators: list | None = None) -> dict:
        """Readback + scope guard + atomic publish. Returns manifest dict."""
        try:
            after_ident = drawing_identity(self.working_path)
        except Exception as ex:
            self.manifest.status = "FAIL"
            raise CadError("READBACK_FAIL", f"Cannot read back working file: {ex}", {})
        scope_res = validate_no_changes_outside_scope(self.source_path, self.working_path, self.scope)
        self.validations.append({"validator": "scope_guard", **scope_res})
        results = [scope_res["ok"]]
        for v in (extra_validators or []):
            try:
                r = v(self.working_path)
                ok = bool(r.get("ok", False))
            except CadError as ce:
                r = ce.to_dict()
                ok = False
            self.validations.append({"validator": getattr(v, "__name__", "custom"), **r})
            results.append(ok)
        self.manifest.validation_results = self.validations
        if not all(results):
            self.manifest.status = "FAIL"
            log_event({"transaction_id": self.transaction_id, "event": "commit_rejected",
                       "validations": self.validations})
            raise CadError("VALIDATION_FAIL", "Transaction validation failed; temp discarded, source untouched.",
                           {"validations": self.validations})
        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
        tmp_out = self.output_path + f".tmp-{self.transaction_id}"
        shutil.copy2(self.working_path, tmp_out)
        os.replace(tmp_out, self.output_path)
        self.manifest.final_sha256 = sha256_file(self.output_path)
        self.manifest.status = "PASS"
        log_event({"transaction_id": self.transaction_id, "event": "commit",
                   "source_sha": self.source_sha, "final_sha": self.manifest.final_sha256,
                   "plan_hash": self.plan_hash})
        return self.manifest.to_dict()

    def discard(self):
        self.manifest.status = "DISCARDED"
        log_event({"transaction_id": self.transaction_id, "event": "discard"})
        return self.manifest.to_dict()
