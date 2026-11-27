-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

vim.keymap.set("n", "<leader>bj", "<cmd>BufferLinePick<cr>", { desc = "Pick Buffer" })

vim.api.nvim_create_user_command("CopyRelPath", function()
  vim.api.nvim_call_function("setreg", { "+", vim.fn.fnamemodify(vim.fn.expand("%"), ":.") })
end, {})
vim.keymap.set("n", "<leader>bcr", "<cmd>CopyRelPath<cr>", { desc = "Copy Buffer Relative Path" })

vim.api.nvim_create_user_command("CopyAbsPath", function()
  vim.api.nvim_call_function("setreg", { "+", vim.fn.fnamemodify(vim.fn.expand("%"), ":p") })
end, {})
vim.keymap.set("n", "<leader>bca", "<cmd>CopyAbsPath<cr>", { desc = "Copy Buffer Absolute Path" })

vim.keymap.set("n", "<C-h>", "<Cmd>NvimTmuxNavigateLeft<CR>", { silent = true })
vim.keymap.set("n", "<C-j>", "<Cmd>NvimTmuxNavigateDown<CR>", { silent = true })
vim.keymap.set("n", "<C-k>", "<Cmd>NvimTmuxNavigateUp<CR>", { silent = true })
vim.keymap.set("n", "<C-l>", "<Cmd>NvimTmuxNavigateRight<CR>", { silent = true })
