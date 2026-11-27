return {
  {
    "hrsh7th/nvim-cmp",
    dependencies = { "hrsh7th/cmp-emoji" },
    ---@param opts cmp.ConfigSchema
    opts = function(_, opts)
      local cmp = require("cmp")
      table.insert(opts.sources, { name = "emoji" })
      vim.list_extend(
        opts.mapping,
        cmp.mapping.preset.insert({
          ["<M-CR>"] = function(fallback)
            cmp.abort()
            fallback()
          end,
        })
      )
    end,
  },
}
