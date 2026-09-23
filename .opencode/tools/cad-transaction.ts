import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "File transaction control: copy->temp->apply->readback->validate->atomic publish. Never edits source in place. Actions: status.",
  args: {
    action: tool.schema.string().describe("status"),
    transaction_id: tool.schema.string().optional(),
  },
  async execute(args, ctx) {
    const path = await import("path")
    const fs = await import("fs")
    if (args.action === "status") {
      const mp = path.join(ctx.worktree, ".cad-agent", "transactions", args.transaction_id ?? "", "manifest.json")
      try {
        return await fs.promises.readFile(mp, "utf-8")
      } catch {
        return JSON.stringify({ ok: false, error_code: "DRAWING_NOT_FOUND", error: `transaction ${args.transaction_id} not found` })
      }
    }
    return JSON.stringify({ ok: false, error_code: "VALIDATION_FAIL", error: `unknown action ${args.action}` })
  },
})
