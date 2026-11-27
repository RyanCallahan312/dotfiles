-- Prefer basedpyright + ruff-lsp over LazyVim's default Python stack.
vim.g.lazyvim_python_lsp = "basedpyright"
vim.g.lazyvim_python_ruff = "ruff_lsp"

-- Keep Ruby on the Solargraph/RuboCop path for projects that are not on ruby-lsp.
vim.g.lazyvim_ruby_lsp = "solargraph"
vim.g.lazyvim_ruby_formatter = "rubocop"

-- Only enable Prettier in projects that opted in with their own config file.
vim.g.lazyvim_prettier_needs_config = true

-- Disable cmp integration so Copilot can keep virtual text suggestions enabled.
vim.g.ai_cmp = false -- needed for virtual text copilot completion
