# zsh

This package stores the tracked Zsh config plus the pinned Oh My Zsh dependencies it expects.

## What is tracked

- `dot-zshrc`, `dot-zshenv`, and `dot-p10k.zsh` mirror the shell config that gets stowed into `$HOME`.
- `dot-config/zsh/omz-repos.lock` pins the exact `oh-my-zsh`, `powerlevel10k`, `zsh-autosuggestions`, and `fast-syntax-highlighting` revisions used by the prompt setup.
- `dot-config/zsh/bootstrap-omz.zsh` installs or updates those repos into `~/.oh-my-zsh`.
- `dot-config/zsh/local.zsh.example` shows where machine-local secrets, personal paths, and one-off overrides should live.

## Bootstrap on a new machine

1. `stow -R zsh`
2. Open a new interactive Zsh shell once and it will auto-bootstrap `~/.oh-my-zsh` if missing
3. Optional: `cp ~/.config/zsh/local.zsh.example ~/.config/zsh/local.zsh`
4. Manual fallback: `zsh ~/.config/zsh/bootstrap-omz.zsh`
5. Restart the shell if you bootstrapped manually

Homebrew-managed CLI dependencies still live in `homebrew/Brewfile`.

## SSH agent

Shell startup checks the inherited SSH agent before the prompt, so programs such as Aspire and OpenCode inherit a usable `SSH_AUTH_SOCK` without first running `ssh`. Working inherited/forwarded agents are preserved. If the inherited agent is unavailable on macOS, the shell discovers and reuses the shared launchd agent instead of starting a persistent agent per shell. Other platforms need a working system-managed agent. No existing socket paths are deleted.

If `~/.ssh/github` exists, local sessions load it when its public key is not already usable through the agent, using the macOS keychain where available. An empty agent is not assumed to contain the required key. Sessions with `SSH_CONNECTION` set never add local keys to a forwarded agent; load missing keys on the originating host instead.

Open a new terminal or run `source ~/.zshrc` to repair the current shell, then restart Aspire/OpenCode from that shell. A child shell cannot repair an already-running parent process or AppHost. The old `~/.ssh/agent.sock` path is no longer used by this config. Docker mounts referencing it must be updated separately; Docker Desktop provides `/run/host-services/ssh-auth.sock` for agent forwarding.

Run the isolated agent checks with `zsh zsh/tests/ssh-agent.zsh` from the repository root.
