import { tool } from "@opencode-ai/plugin"

async function bridge(op: string, args: any, ctx: any) {
  const path = await import("path")
  const script = path.join(ctx.worktree, "cad_agent", "tool_bridge.py")
  const payload = JSON.stringify(args ?? {})
  const proc = Bun.$`python3 ${script} ${op} ${payload}`.cwd(ctx.worktree)
  return await proc.text()
}

const rev = "Expected revision_token from inspect. Write refused on mismatch (DRAWING_REVISION_MISMATCH)."

// ---- CONTROLLED WRITE SURFACE (executor only) ----
export const capture_template = tool({
  description: "Capture a composite template (rigid group) from member handles. Members must move as ONE transform afterwards.",
  args: { drawing: tool.schema.string(), handles: tool.schema.array(tool.schema.string()), name: tool.schema.string(), semantic_type: tool.schema.string().optional(), template_id: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("capture_template", args, ctx) },
})

export const clone_template = tool({
  description: "Clone a whole template with ONE rigid transform. Never move fill/outline/label separately.",
  args: { drawing: tool.schema.string(), template_id: tool.schema.string(), dx: tool.schema.number(), dy: tool.schema.number(), angle_deg: tool.schema.number().optional(), out_path: tool.schema.string().optional(), expected_revision: tool.schema.string().optional().describe(rev), new_label: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("clone_template", args, ctx) },
})

export const move_along_wall = tool({
  description: "Move an outlet along a wall by deterministic mm displacement. LLM never computes X/Y. Supports dry_run.",
  args: { drawing: tool.schema.string(), entity_handle: tool.schema.string(), wall_handle: tool.schema.string(), displacement: tool.schema.number(), unit: tool.schema.string().optional(), direction: tool.schema.number().optional(), expected_revision: tool.schema.string().optional().describe(rev), dry_run: tool.schema.boolean().optional(), out_path: tool.schema.string().optional(), allowed_bbox: tool.schema.array(tool.schema.number()).optional() },
  async execute(args, ctx) { return bridge("move_along_wall", args, ctx) },
})

export const place_on_wall = tool({
  description: "Place a panel template on a wall free interval (parallel long side, clearance, rigid clone). Supports dry_run.",
  args: { drawing: tool.schema.string(), template_id: tool.schema.string(), wall_handle: tool.schema.string(), position_rule: tool.schema.string().optional(), clearance: tool.schema.number().optional(), new_label: tool.schema.string().optional(), expected_revision: tool.schema.string().optional().describe(rev), dry_run: tool.schema.boolean().optional(), out_path: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("place_panel", args, ctx) },
})

export const align_to_wall = tool({
  description: "Compute deterministic alignment angle parallel/perpendicular to a wall (no write; geometry only).",
  args: { drawing: tool.schema.string(), wall_handle: tool.schema.string(), mode: tool.schema.string().optional().describe("parallel|perpendicular") },
  async execute(args, ctx) { return bridge("find_walls", args, ctx) },
})

export const route_conduit = tool({
  description: "Route orthogonal conduit tree source->destinations with clearance + graph validation. Supports dry_run.",
  args: { drawing: tool.schema.string(), source_handle: tool.schema.string(), destination_handles: tool.schema.array(tool.schema.string()), layer: tool.schema.string().optional(), clearance: tool.schema.number().optional(), expected_revision: tool.schema.string().optional().describe(rev), dry_run: tool.schema.boolean().optional(), out_path: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("route_conduit", args, ctx) },
})

export const connect_circuit = tool({
  description: "Connect one outlet to the conduit network (single-destination route). Supports dry_run.",
  args: { drawing: tool.schema.string(), source_handle: tool.schema.string(), destination_handles: tool.schema.array(tool.schema.string()), layer: tool.schema.string().optional(), expected_revision: tool.schema.string().optional().describe(rev), dry_run: tool.schema.boolean().optional(), out_path: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("route_conduit", args, ctx) },
})

export const create_callout = tool({
  description: "Create a callout group (circuits + conductor spec) bound to a conduit edge. Never orphan Tn text.",
  args: { drawing: tool.schema.string(), conduit_edge: tool.schema.any(), circuits: tool.schema.array(tool.schema.string()), conductor_spec: tool.schema.string(), placement: tool.schema.string().optional(), expected_revision: tool.schema.string().optional().describe(rev), dry_run: tool.schema.boolean().optional(), out_path: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("create_callout", args, ctx) },
})

export const move_callout = tool({
  description: "Move a callout group rigidly (leader + text together). Rejected if it would orphan the callout.",
  args: { drawing: tool.schema.string(), template_id: tool.schema.string(), dx: tool.schema.number(), dy: tool.schema.number(), out_path: tool.schema.string().optional(), expected_revision: tool.schema.string().optional().describe(rev) },
  async execute(args, ctx) { return bridge("clone_template", args, ctx) },
})
