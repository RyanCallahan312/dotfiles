---@diagnostic disable: undefined-global

-- https://biomejs.dev/internals/language-support/
local supported = {
  "astro",
  "css",
  "graphql",
  "javascript",
  "javascript.jsx",
  "javascriptreact",
  "json",
  "jsonc",
  "svelte",
  "typescript",
  "typescript.tsx",
  "typescriptreact",
  "vue",
}

return {
  {
    "mason-org/mason.nvim",
    opts = { ensure_installed = { "biome" } },
  },
  {
    "mason-org/mason-lspconfig.nvim",
    opts = function(_, opts)
      opts.ensure_installed = opts.ensure_installed or {}
      for _, ft in ipairs(supported) do
        opts.ensure_installed[ft] = opts.ensure_installed[ft] or {}
        opts.ensure_installed[ft].biome = "biome"
      end
    end,
  },
  {
    "stevearc/conform.nvim",
    optional = true,
    ---@param opts ConformOpts
    opts = function(_, opts)
      opts.formatters_by_ft = opts.formatters_by_ft or {}
      for _, ft in ipairs(supported) do
        opts.formatters_by_ft[ft] = opts.formatters_by_ft[ft] or {}
        -- Run Biome's formatter, then its check/import passes in the same format pipeline.
        table.insert(opts.formatters_by_ft[ft], "biome")
        table.insert(opts.formatters_by_ft[ft], "biome-check")
        table.insert(opts.formatters_by_ft[ft], "biome-organize-imports")
      end

      opts.formatters = opts.formatters or {}
      opts.formatters.biome = {
        require_cwd = true,
      }
    end,
  },
}
