local Util = require("lazyvim.util")
return {
  {
    "nvimtools/none-ls.nvim",
    optional = true,
    opts = function(_, opts)
      local nls = require("null-ls")
      opts.sources = opts.sources or {}
      table.insert(opts.sources, nls.builtins.formatting.csharpier)
    end,
  },
  {
    "stevearc/conform.nvim",
    optional = true,
    opts = {
      formatters_by_ft = {
        cs = { "csharpier" },
        xml = { "xmllint" },
      },
      formatters = {
        csharpier = {
          command = "dotnet-csharpier",
          args = { "--write-stdout" },
        },
      },
    },
  },
  {
    "williamboman/mason.nvim",
    opts = function(_, opts)
      opts.ensure_installed = opts.ensure_installed or {}
      table.insert(opts.ensure_installed, "csharpier")
    end,
  },
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        roslyn = {
          mason = false,
          keys = {},
          settings = {},
        },
      },
      setup = {
        roslyn = function(_, opts)
          local cmp_nvim_lsp = require("cmp_nvim_lsp")
          local capabilities = vim.tbl_deep_extend(
            "force",
            vim.lsp.protocol.make_client_capabilities(),
            cmp_nvim_lsp.default_capabilities()
          )
          require("roslyn").setup({
            dotnet_cmd = "dotnet", -- this is the default
            roslyn_version = "4.8.0-3.23475.7", -- this is the default
            on_attach = function()
              Util.lsp.on_attach(function(client, buffer)
                require("lazyvim.plugins.lsp.keymaps").on_attach(client, buffer)
              end)
            end,
            capabilities = capabilities,
          })
          return true
        end,
      },
    },
  },
}
