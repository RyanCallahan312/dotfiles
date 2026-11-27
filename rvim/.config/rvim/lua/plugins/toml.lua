return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        -- Prefer tombi over taplo for TOML in this profile.
        taplo = {
          enabled = false,
        },
        tombi = {},
      },
    },
  },
}
