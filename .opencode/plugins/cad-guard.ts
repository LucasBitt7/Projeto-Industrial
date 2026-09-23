// CAD guard plugin (native OpenCode enforcement, project-level).
// 1. shell.env: explicit backend for every shell execution — never "auto".
// 2. tool.execute.before: refuse probable ad-hoc CAD writes (*.dxf/*.dwg outside
//    cad_agent), delegating the verdict to the SAME deterministic Python rule
//    tested in tests/test_policy.py. Read-only diagnosis and infra development
//    remain allowed; hard failures stay visible.
import type { Plugin } from "@opencode-ai/plugin"

export const CadGuard: Plugin = async ({ worktree }) => {
  return {
    "shell.env": async (input: any, output: any) => {
      try {
        output.env.CAD_BACKEND = "file"
        if (output.env.AUTOCAD_MCP_BACKEND === "auto") output.env.AUTOCAD_MCP_BACKEND = "file"
      } catch { /* never break the session on guard failure */ }
    },
    "tool.execute.before": async (input: any, output: any) => {
      try {
        if (input.tool !== "bash") return
        const cmd: string = output?.args?.command ?? ""
        if (!/\.(dxf|dwg)\b/i.test(cmd)) return
        if (/cad_agent\/tool_bridge\.py|python3?\s+-m\s+cad_agent/.test(cmd)) return
        const proc = Bun.$`python3 cad_agent/tool_bridge.py guard_check ${JSON.stringify({ command: cmd })}`.cwd(worktree)
        const text = await proc.text()
        let verdict: any = null
        try { verdict = JSON.parse(text) } catch { return }
        if (verdict && verdict.ok === false) {
          throw new Error(`[WRITE_BYPASS_REFUSED] ${verdict.error}`)
        }
      } catch (e: any) {
        if (e && /WRITE_BYPASS_REFUSED/.test(String(e?.message ?? e))) throw e
        // guard internal error: fail open for availability, AGENTS.md still mandates pipeline
      }
    },
  }
}
