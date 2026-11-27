return {
  "stevearc/conform.nvim",
  opts = {
    formatters = {
      sqlfluff = {
        -- `sqlfluff fix` edits files in place instead of reading from stdin.
        stdin = false,
        args = { "fix", "$FILENAME" },
      },
    },
    formatters_by_ft = {
      sql = { "sqlfluff" },
    },
  },
}
