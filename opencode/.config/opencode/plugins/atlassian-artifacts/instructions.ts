// shortcut: matches Atlassian's current wording; update the match if the offer returns.
export const overrideArtifactOffer = (text: string) =>
  text.replace(/^[ \t]*<server name="atlassian">\r?\n[\s\S]*?^[ \t]*<\/server>$/gm, (server) =>
    server.replace(
      "When creating an HTML or text-based file, always ask the user whether they would like to upload it to Atlassian Artifacts. If they do,",
      "Keep generated files local unless the user explicitly requests an upload to Atlassian Artifacts. Do not offer to upload them. If the user explicitly requests an upload,",
    ),
  )
