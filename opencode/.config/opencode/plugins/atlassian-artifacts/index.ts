import { Plugin } from "@opencode/plugin/effect"
import { Effect } from "effect"
import { overrideArtifactOffer } from "./instructions"

export default Plugin.define({
  id: "atlassian-artifacts",
  effect: (ctx) =>
    Effect.gen(function* () {
      yield* ctx.session.hook("context", (event) =>
        Effect.sync(() => {
          event.system = event.system.map((part) => ({ ...part, text: overrideArtifactOffer(part.text) }))
          // OpenCode can also send changed server instructions as system messages.
          event.messages = event.messages.map((message) =>
            message.role === "system"
              ? {
                  ...message,
                  content: message.content.map((part) =>
                    part.type === "text" ? { ...part, text: overrideArtifactOffer(part.text) } : part,
                  ),
                }
              : message,
          )
        }),
      )
    }),
})
