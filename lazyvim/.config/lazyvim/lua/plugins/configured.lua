return {
  {
    "echasnovski/mini.indentscope",
    opts = {
      draw = {
        animation = function()
          return 0
        end,
      },
    },
  },
  --  {
  --    "zbirenbaum/copilot.lua",
  --    opts = {
  --      suggestion = { enabled = true, auto_trigger = true, keymap = { accept = "<C-CR>" } },
  --      panel = {
  --        enabled = true,
  --        auto_refresh = false,
  --        keymap = {
  --          jump_prev = "[[",
  --          jump_next = "]]",
  --          accept = "<CR>",
  --          refresh = "gr",
  --          open = "<M-CR>",
  --        },
  --        layout = {
  --          position = "bottom", -- | top | left | right
  --          ratio = 0.4,
  --        },
  --      },
  --      filetypes = {
  --        markdown = true,
  --        help = true,
  --      },
  --    },
  --  },
  {
    "hrsh7th/nvim-cmp",
    keys = {
      { "<CR>", false },
    },
  },
}
