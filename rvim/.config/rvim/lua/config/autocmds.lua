-- Small local helpers that complement LazyVim defaults.

vim.keymap.set("n", "<leader>bj", "<cmd>BufferLinePick<cr>", { desc = "Pick Buffer" })

-- Copy the current buffer path relative to the working directory.
vim.api.nvim_create_user_command("CopyRelPath", function()
  vim.api.nvim_call_function("setreg", { "+", vim.fn.fnamemodify(vim.fn.expand("%"), ":.") })
end, {})
vim.keymap.set("n", "<leader>bcr", "<cmd>CopyRelPath<cr>", { desc = "Copy Buffer Relative Path" })

-- Copy the current buffer's absolute path for shell or GitHub workflows.
vim.api.nvim_create_user_command("CopyAbsPath", function()
  vim.api.nvim_call_function("setreg", { "+", vim.fn.fnamemodify(vim.fn.expand("%"), ":p") })
end, {})
vim.keymap.set("n", "<leader>bca", "<cmd>CopyAbsPath<cr>", { desc = "Copy Buffer Absolute Path" })
