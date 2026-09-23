import { tool } from "@opencode-ai/plugin"

// Persistent CAD intent router. The primary agent calls this FIRST on every user
// request (mandated by AGENTS.md) so CAD tasks enter the cad_agent pipeline
// automatically — the user never has to name tools.
async function bridge(op: string, args: any, ctx: any) {
  const path = await import("path")
  const script = path.join(ctx.worktree, "cad_agent", "tool_bridge.py")
  const payload = JSON.stringify(args ?? {})
  const proc = Bun.$`python3 ${script} ${op} ${payload}`.cwd(ctx.worktree)
  return await proc.text()
}

export const classify = tool({
  description: "Classify user intent: CAD edit (full pipeline), CAD read-only (inspector), or non-CAD. Call FIRST on every request involving drawings/electrical work.",
  args: { prompt: tool.schema.string().describe("The user's raw request text") },
  async execute(args, ctx) { return bridge("route", args, ctx) },
})

export const guard_check = tool({
  description: "Check whether a shell command would be an ad-hoc CAD-write bypass (refused) or allowed.",
  args: { command: tool.schema.string() },
  async execute(args, ctx) { return bridge("guard_check", args, ctx) },
})

export const current_artifact = tool({
  description: "Resolve THE current drawing artifact from transaction lineage (never guess *final*.dxf).",
  args: { project: tool.schema.string().optional() },
  async execute(args, ctx) { return bridge("current_artifact", args, ctx) },
})
