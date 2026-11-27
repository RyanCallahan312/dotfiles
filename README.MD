# Dotfiles

Dotfiles managed with gnu stow. use `--dotfiles` to replace `dot-<file_name>` with `.<file_name>`. it might work without the flag tho

example usage: `stow -R rvim` for latest neovim setup. You will need to add the following to your profile to make it work: `export NVIM_APPNAME="rvim"`

## Agent config

| Package | Installs |
| --- | --- |
| `agents` | Shared skills in `~/.agents/skills` |
| `claude` | Claude Code settings, instructions, and local skills in `~/.claude` (some skills link to `agents`) |
| `pi` | Pi settings and model overrides in `~/.pi/agent` |

```sh
cd ~/dotfiles
mkdir -p ~/.agents/skills ~/.claude/skills ~/.pi/agent
stow -n -v -t "$HOME" agents claude pi
stow -t "$HOME" agents claude pi
```

Create those directories first so Stow links the managed entries without linking the app's entire config directory. If the dry run reports conflicts, back up the conflicting files before moving them aside; don't use `--adopt` blindly.

Credentials, sessions, caches, Claude-synced skills, and installed dependencies stay local. Pi's extension sources are in `settings.json`; sign in separately on a new machine.

Set your Git identity in `~/.gitconfig.local` (or per repository). Set `GOG_ACCOUNT` in the environment that launches OpenCode to select the account for its Gmail connector.
