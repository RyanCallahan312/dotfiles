return {
  { "iamcco/markdown-preview.nvim", enabled = false },
  {
    "sammaji/markdown-preview.nvim",
    -- Keep the fork's checkout and build hook separate from LazyVim's default.
    name = "markdown-preview-modern",
    tag = "v0.3.0",
    ft = "markdown",
    cmd = { "MarkdownPreview", "MarkdownPreviewStop", "MarkdownPreviewToggle" },
    keys = {
      { "<leader>cp", "<cmd>MarkdownPreviewToggle<cr>", ft = "markdown", desc = "Markdown Preview" },
    },
  },
}
