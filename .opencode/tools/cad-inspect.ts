import { tool } from "@opencode-ai/plugin"

async function bridge(op: string, args: any, ctx: any) {
  const path = await import("path")
  const script = path.join(ctx.worktree, "cad_agent", "tool_bridge.py")
  const payload = JSON.stringify(args ?? {})
  // pass via argv; payloads are small (handles/bboxes, never file bytes)
  const proc = Bun.$`python3 ${script} ${op} ${payload}`.cwd(ctx.worktree)
  const text = await proc.text()
  try {
    return text
  } catch {
    return text
  }
}

// ---- READ-ONLY INSPECTOR SURFACE ----
export const inspect_drawing = tool({
  description: "READ-ONLY. Return DrawingIdentity (path, sha256, insunits, extents, revision_token). First step of every CAD task.",
  args: { drawing: tool.schema.string().describe("Absolute or repo-relative DXF path") },
  async execute(args, ctx) { return bridge("inspect", args, ctx) },
})

export const find_entities = tool({
  description: "READ-ONLY. Discovery only: find entities by layer/type/block/text/bbox. Returns handles. Never use appearance for writes.",
  args: {
    drawing: tool.schema.string(),
    layer: tool.schema.string().optional(), etype: tool.schema.string().optional(),
    block_name: tool.schema.string().optional(), text_regex: tool.schema.string().optional(),
    bbox: tool.schema.array(tool.schema.number()).optional(), limit: tool.schema.number().optional(),
  },
  async execute(args, ctx) { return bridge("find_entities", args, ctx) },
})

export const get_entity = tool({
  description: "READ-ONLY. Get one entity by HANDLE (identity). Vague descriptions rejected.",
  args: { drawing: tool.schema.string(), handle: tool.schema.string().describe("Entity handle, e.g. 8DA3") },
  async execute(args, ctx) { return bridge("get_entity", args, ctx) },
})

export const room_entities = tool({
  description: "READ-ONLY. List entities inside a room bbox.",
  args: { drawing: tool.schema.string(), bbox: tool.schema.array(tool.schema.number()).describe("[xmin,ymin,xmax,ymax]") },
  async execute(args, ctx) { return bridge("find_entities", { drawing: (args as any).drawing, bbox: (args as any).bbox, limit: 5000 }, ctx) },
})

export const find_blocks = tool({
  description: "READ-ONLY. Find block INSERTs by name regex.",
  args: { drawing: tool.schema.string(), name_regex: tool.schema.string().optional(), bbox: tool.schema.array(tool.schema.number()).optional(), limit: tool.schema.number().optional() },
  async execute(args, ctx) { return bridge("find_blocks", args, ctx) },
})

export const find_walls = tool({
  description: "READ-ONLY. Detect wall segments (deterministic, from wall layers). Returns wall handles + p1/p2.",
  args: { drawing: tool.schema.string(), wall_layers: tool.schema.array(tool.schema.string()).optional(), bbox: tool.schema.array(tool.schema.number()).optional() },
  async execute(args, ctx) { return bridge("find_walls", args, ctx) },
})

export const readback = tool({
  description: "READ-ONLY. Re-read an entity by handle after a write (mandatory verification step).",
  args: { drawing: tool.schema.string(), handle: tool.schema.string() },
  async execute(args, ctx) { return bridge("get_entity", args, ctx) },
})

export const render_region = tool({
  description: "Visual QA ONLY. Renders PNG of drawing/region. NEVER read coordinates from images; CAD data is authoritative.",
  args: { drawing: tool.schema.string(), out: tool.schema.string(), bbox: tool.schema.array(tool.schema.number()).optional() },
  async execute(args, ctx) { return bridge("render", args, ctx) },
})
