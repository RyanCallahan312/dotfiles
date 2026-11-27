return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        tsgo = {
          cmd = function(dispatchers, config)
            local cmd = vim.fs.joinpath(vim.fn.getcwd(), "node_modules/.bin/tsgo")

            if vim.fn.executable(cmd) ~= 1 and (config or {}).root_dir then
              cmd = vim.fs.joinpath(config.root_dir, "node_modules/.bin/tsgo")
            end

            if vim.fn.executable(cmd) ~= 1 then
              cmd = "tsgo"
            end

            return vim.lsp.rpc.start({ cmd, "--lsp", "--stdio" }, dispatchers)
          end,
          capabilities = {
            workspace = {
              -- tsgo registers watchers for virtual TypeScript library URIs such as
              -- bundled:///libs/**/*, which Neovim 0.12 treats as invalid filesystem globs.
              didChangeWatchedFiles = {
                dynamicRegistration = false,
              },
            },
          },
        },
      },
    },
  },
}
