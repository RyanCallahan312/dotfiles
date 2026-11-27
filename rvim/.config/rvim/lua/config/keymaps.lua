-- Mirror tmux pane navigation inside Neovim terminals and normal buffers.

vim.keymap.set({ "n", "t" }, "<C-h>", "<Cmd>NvimTmuxNavigateLeft<CR>", { silent = true })
vim.keymap.set({ "n", "t" }, "<C-j>", "<Cmd>NvimTmuxNavigateDown<CR>", { silent = true })
vim.keymap.set({ "n", "t" }, "<C-k>", "<Cmd>NvimTmuxNavigateUp<CR>", { silent = true })
vim.keymap.set({ "n", "t" }, "<C-l>", "<Cmd>NvimTmuxNavigateRight<CR>", { silent = true })
