return {
  {
    "RyanCallahan312/gitpad.nvim",
    dependencies = { "rcarriga/nvim-notify" },
    branch = "add-split-window-on-open-support",
    config = function()
      require("gitpad").setup({
        -- your configuration comes here
        -- or leave it empty to use the default settings
        -- refer to the configuration section below
        on_attach = function(bufnr)
          -- You can also define a function to be called when the gitpad window is opened, by setting the `on_attach` option:
          -- This is just an example
          vim.api.nvim_buf_set_keymap(bufnr, "n", "q", "<Cmd>wq<CR>", { noremap = true, silent = true })
        end,
      })
    end,
    keys = {
      {
        "<leader>pp",
        function()
          require("gitpad").toggle_gitpad() -- or require('gitpad').toggle_gitpad({ title = 'Project notes' })
        end,
        desc = "gitpad project",
      },
      {
        "<leader>pbd",
        function()
          require("gitpad").toggle_gitpad_branch() -- or require('gitpad').toggle_gitpad_branch({ title = 'Branch notes' })
        end,
        desc = "gitpad branch default",
      },
      {
        "<leader>pbh",
        function()
          require("gitpad").toggle_gitpad_branch({ window_type = "split", split_win_opts = { split = "below" } }) -- or require('gitpad').toggle_gitpad_branch({ title = 'Branch notes' })
        end,
        desc = "gitpad branch horizontal split",
      },
      {
        "<leader>pbv",
        function()
          require("gitpad").toggle_gitpad_branch({ window_type = "split", split_win_opts = { split = "right" } }) -- or require('gitpad').toggle_gitpad_branch({ title = 'Branch notes' })
        end,
        desc = "gitpad branch vertical split",
      },
      {
        "<leader>pbf",
        function()
          require("gitpad").toggle_gitpad_branch({ window_type = "floating" }) -- or require('gitpad').toggle_gitpad_branch({ title = 'Branch notes' })
        end,
        desc = "gitpad branch floating",
      },
      -- Daily notes
      {
        "<leader>pd",
        function()
          local date_filename = "daily-" .. os.date("%Y-%m-%d.md")
          require("gitpad").toggle_gitpad({ filename = date_filename }) -- or require('gitpad').toggle_gitpad({ filename = date_filename, title = 'Daily notes' })
        end,
        desc = "gitpad daily notes",
      },
      -- Per file notes
      {
        "<leader>pf",
        function()
          local filename = vim.fn.expand("%:p") -- or just use vim.fn.bufname()
          if filename == "" then
            vim.notify("empty bufname")
            return
          end
          filename = vim.fn.pathshorten(filename, 2) .. ".md"
          require("gitpad").toggle_gitpad({ filename = filename }) -- or require('gitpad').toggle_gitpad({ filename = filename, title = 'Current file notes' })
        end,
        desc = "gitpad per file notes",
      },
    },
  },
}
