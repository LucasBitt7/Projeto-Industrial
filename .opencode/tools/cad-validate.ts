import { tool } from "@opencode-ai/plugin"

async function bridge(op: string, args: any, ctx: any) {
  const path = await import("path")
  const script = path.join(ctx.worktree, "cad_agent", "tool_bridge.py")
  const payload = JSON.stringify(args ?? {})
  const proc = Bun.$`python3 ${script} ${op} ${payload}`.cwd(ctx.worktree)
  return await proc.text()
}

// ---- INDEPENDENT VALIDATION SURFACE (read-only, re-reads from disk) ----
export const detect_collisions = tool({
  description: "READ-ONLY. Collision engine over drawing bboxes (outlet/panel/callout/text). Returns hits.",
  args: { drawing: tool.schema.string(), bbox: tool.schema.array(tool.schema.number()).optional(), clearance: tool.schema.number().optional(), limit: tool.schema.number().optional() },
  async execute(args, ctx) { return bridge("detect_collisions", args, ctx) },
})

export const validate_room = tool({
  description: "READ-ONLY. Room semantic validation: every circuit tag inside room must be allowed (ROOM_SEMANTIC_VIOLATION otherwise).",
  args: { drawing: tool.schema.string(), room: tool.schema.any().describe("RoomRules {room_id, bbox_or_polygon, allowed_circuits, forbidden_circuits}") },
  async execute(args, ctx) { return bridge("validate_room", args, ctx) },
})

export const validate_network = tool({
  description: "READ-ONLY. Conduit graph validation: connected, acyclic, orphan endpoints.",
  args: { drawing: tool.schema.string(), layer: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("validate_network", args, ctx) },
})

export const validate_scope = tool({
  description: "READ-ONLY. Scope guard: compare before/after drawings, FAIL on any change outside scope (SCOPE_VIOLATION).",
  args: { before: tool.schema.string(), after: tool.schema.string(), scope: tool.schema.any() },
  async execute(args, ctx) { return bridge("validate_scope", args, ctx) },
})

export const validate_callouts = tool({
  description: "READ-ONLY. Callout integrity: complete spec + bound to edge, no orphans.",
  args: { drawing: tool.schema.string(), layer: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("validate_callouts", args, ctx) },
})

export const template_integrity = tool({
  description: "READ-ONLY. Panel template integrity: fill/diagonal/label coherent with outline (detects QDF/QDL disassembly).",
  args: { drawing: tool.schema.string(), handles: tool.schema.array(tool.schema.string()), semantic_type: tool.schema.string().optional(), eps: tool.schema.number().optional() },
  async execute(args, ctx) { return bridge("template_integrity", args, ctx) },
})
