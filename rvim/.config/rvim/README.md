# rvim

Personal [LazyVim](https://github.com/LazyVim/LazyVim) profile loaded with `NVIM_APPNAME=rvim`.
This directory lives in the dotfiles repo and is intended to be symlinked to `~/.config/rvim`.

## Install

1. From the dotfiles repo root, run `stow -R rvim`.
2. Launch Neovim with `NVIM_APPNAME="rvim" nvim`.
3. On first launch, `lazy.nvim` bootstraps itself and installs the versions pinned in `lazy-lock.json`.

The shell config in this repo also defines `alias rvim='NVIM_APPNAME="rvim" nvim'`.

## Layout

- `init.lua`: entrypoint for the `rvim` app profile.
- `lazyvim.json`: enabled LazyVim extras.
- `lua/config/`: base options, keymaps, and small helper commands.
- `lua/plugins/`: active plugin overrides and custom specs.
- `lua/plugin-references/`: inactive or experimental specs kept for reference and not imported by `lazy.nvim`.
- `lazy-lock.json`: locked plugin versions.
- `stylua.toml`: formatting rules for Lua edits.

## Notable Customizations

- `eldritch` is the default colorscheme, with a few small UI tweaks for borders, signs, notifications, and scrolling.
- `<C-h>`, `<C-j>`, `<C-k>`, and `<C-l>` move between tmux panes and Neovim splits.
- Buffer helpers add picker and path-copy shortcuts that are not part of stock LazyVim.
- Copilot, Sidekick, Gitpad, and CodeSnap are configured for AI workflows, project notes, and shareable screenshots.
- Python prefers `basedpyright` plus `ruff_lsp`.
- Ruby stays on the `solargraph` plus `rubocop` path from the LazyVim Ruby extra plus local globals.
- TOML prefers `tombi`, and `mise*.toml` files get extra Treesitter and `otter.nvim` support for embedded code blocks.
- Web filetypes can run Biome through `conform.nvim`, SQL uses `sqlfluff fix`, and C# can attach through `roslyn.nvim`.
- JavaScript and TypeScript debugging use `js-debug-adapter`, with launch profiles that work for Bun-based Vite apps.

## Custom Keymaps

- `<leader>bj`: pick a buffer from the bufferline.
- `<leader>bcr`: copy the current buffer path relative to the working directory.
- `<leader>bca`: copy the current buffer absolute path.
- `gi>` / `gi<`: increment or decrement values with `dial.nvim`.
- Visual `<leader>csc`: copy a CodeSnap image to the clipboard.
- Visual `<leader>css`: save a CodeSnap image to `~/codesnap`.
- `<leader>pp`: open project notes in Gitpad.
- `<leader>pbd`, `<leader>pbh`, `<leader>pbv`, `<leader>pbf`: open branch notes in different Gitpad layouts.
- `<leader>pd`: open a dated daily note in Gitpad.
- `<leader>pf`: open notes for the current file in Gitpad.

## External Tool Expectations

- `tmux` is expected for pane navigation and Sidekick's mux backend.
- `bun` is used by parts of the Biome and TypeScript debugging workflow.
- `node` is required to run the `js-debug-adapter` debug server.
- `sqlfluff` is expected for SQL formatting.
- Most language servers and supporting CLIs are installed by Mason on demand, including packages from `Crashdummyy/mason-registry`.

## Notes

- Inactive experiments and starter examples live under `lua/plugin-references/` so they do not get imported with active plugin specs.
