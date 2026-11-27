import { execFile } from "node:child_process"
import { promisify } from "node:util"

const run = promisify(execFile)

type ShellEvent = { command: string }
type PluginContext = {
  shell: {
    hook(name: "create.before", callback: (event: ShellEvent) => Promise<void>): Promise<unknown>
  }
}

// RTK OpenCode plugin — rewrites commands to use rtk for token savings.
// Requires: rtk >= 0.23.0 in PATH.
//
// This is a thin delegating plugin: all rewrite logic lives in `rtk rewrite`,
// which is the single source of truth (src/discover/registry.rs).
// To add or change rewrite rules, edit the Rust registry — not this file.

export default {
  id: "rtk",
  async setup(ctx: PluginContext) {
    try {
      await run("rtk", ["--version"])
    } catch {
      console.warn("[rtk] rtk binary not found in PATH; plugin disabled")
      return
    }

    await ctx.shell.hook("create.before", async (event) => {
      try {
        const { stdout } = await run("rtk", ["rewrite", event.command])
        const rewritten = stdout.trim()
        if (rewritten && rewritten !== event.command) event.command = rewritten
      } catch {
        // Pass through unchanged when a command has no rewrite or RTK fails.
      }
    })
  },
}
