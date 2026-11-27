return {
  {
    "richardbizik/nvim-toc",
    event = "filetype markdown",
    config = function()
      require("nvim-toc").setup({})
    end,
  },
  {
    "yaocccc/nvim-hl-mdcodeblock.lua",
    dependencies = {
      "nvim-treesitter/nvim-treesitter",
    },
    config = function()
      require("hl-mdcodeblock").setup()
    end,
  },
  -- {
  --   "OXY2DEV/markview.nvim",
  --   dependencies = {
  --     "nvim-tree/nvim-web-devicons", -- Used by the code bloxks
  --   },
  --   config = function()
  --     require("markview").setup()
  --   end,
  -- },
}
