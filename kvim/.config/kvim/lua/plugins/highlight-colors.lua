return {
  {
    "brenoprata10/nvim-highlight-colors",
    version = "*",
    opts = {
      render = "virtual",
      enable_tailwind = "True",
    },
    keys = {
      {
        "<leader>uH",
        function()
          require("nvim-highlight-colors").toggle()
        end,
        desc = "Toggle Color Preview",
      },
    },
  },
}
