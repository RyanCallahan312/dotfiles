return {
  { "catppuccin/nvim", name = "catppuccin", priority = 900 },
  {
    "eldritch-theme/eldritch.nvim",
    lazy = false,
    priority = 1000,
    opts = {
      on_colors = function(colors)
        colors.border = colors.comment
      end,
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "eldritch",
    },
  },
}
