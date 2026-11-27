import { expect, test } from "bun:test"
import { overrideArtifactOffer } from "./instructions"

test("only replaces the Atlassian upload offer and preserves the explicit upload workflow", () => {
  const offer = "When creating an HTML or text-based file, always ask the user whether they would like to upload it to Atlassian Artifacts. If they do,"
  const workflow = " use `discover` to retrieve `createArtifactsUpload` (step 1) and `publishArtifact` (step 2)."
  const atlassian = `  <server name="atlassian">\n    Jira guidance\n    # Atlassian Artifacts\n    - ${offer}${workflow}\n  </server>`
  const other = atlassian.replace('name="atlassian"', 'name="other"')
  const prompt = `<mcp_instructions>\n${atlassian}\n${other}\n</mcp_instructions>\n\nOther instructions.`
  const expected = prompt.replace(offer, "Keep generated files local unless the user explicitly requests an upload to Atlassian Artifacts. Do not offer to upload them. If the user explicitly requests an upload,")

  expect(overrideArtifactOffer(prompt)).toBe(expected)
  expect(overrideArtifactOffer(expected)).toBe(expected)
  expect(overrideArtifactOffer(other)).toBe(other)
})
