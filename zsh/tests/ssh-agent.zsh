#!/bin/zsh -f

setopt ERR_EXIT NO_UNSET PIPE_FAIL

zshrc="${0:A:h:h}/dot-zshrc"
eval "$(sed -n '/^_ensure_ssh_agent() {$/,/^}$/p' "$zshrc")"
wrappers=$(sed -n '/^for _ssh_cmd in ssh scp sftp rsync; do$/,/^unset _ssh_cmd$/p' "$zshrc")

assert() {
  if ! "$@"; then
    print -u2 -- "FAIL: $*"
    exit 1
  fi
}

# Fake key files and a local socket keep the checks away from real keys/agents.
scratch=$(mktemp -d "${TMPDIR:-/tmp}/ssh.XXXXXX")
trap 'rm -r -- "$scratch"' EXIT
export HOME="$scratch/home"
mkdir -p "$HOME/.ssh" "$scratch/directory"
: > "$HOME/.ssh/github"
: > "$HOME/.ssh/github.pub"
zmodload zsh/net/socket
zsocket -l "$scratch/sock"
shared_sock="$scratch/sock"
unset SSH_CONNECTION
OSTYPE=darwin

typeset -i probe_status=0 shared_status=0 key_status=0 load_status=0 key_loads=0

launchctl() {
  [[ "$*" == "asuser $UID launchctl getenv SSH_AUTH_SOCK" ]] || return 99
  print -r -- "$shared_sock"
}

ssh-add() {
  case $1 in
    -l)
      if [[ ${SSH_AUTH_SOCK-} == "$shared_sock" ]]; then
        return "$shared_status"
      fi
      return "$probe_status"
      ;;
    -T) return "$key_status" ;;
    *) (( ++key_loads )); return "$load_status" ;;
  esac
}

# Valid inherited agents keep their socket, even when no identities are loaded.
for probe_status in 0 1; do
  export SSH_AUTH_SOCK=/mock/inherited-agent
  _ensure_ssh_agent
  assert test "$SSH_AUTH_SOCK" = /mock/inherited-agent
done
assert test "$key_loads" -eq 0

# Load the required GitHub key even if an agent already holds a different key.
for probe_status in 0 1; do
  key_status=1
  key_loads=0
  _ensure_ssh_agent
  assert test "$key_loads" -eq 1
done

# Forwarded agents must not receive this machine's private keys.
export SSH_CONNECTION='forwarded session'
key_loads=0
_ensure_ssh_agent
assert test "$key_loads" -eq 0
assert test "$SSH_AUTH_SOCK" = /mock/inherited-agent
unset SSH_CONNECTION

# Bad inherited paths use the shared agent rather than spawning per-shell agents.
probe_status=2
shared_status=1
for inherited_sock in '' "$scratch/directory" /mock/stale-socket; do
  export SSH_AUTH_SOCK="$inherited_sock"
  key_loads=0
  _ensure_ssh_agent
  assert test "$SSH_AUTH_SOCK" = "$shared_sock"
  assert test "$key_loads" -eq 1
done
assert test -d "$scratch/directory"
unset SSH_AUTH_SOCK
_ensure_ssh_agent
assert test "$SSH_AUTH_SOCK" = "$shared_sock"

# Startup itself repairs the environment, without first invoking an SSH wrapper.
export SSH_AUTH_SOCK=/mock/stale-socket
eval "$(sed -n '/^_ensure_ssh_agent() {$/,/^# Enable Powerlevel10k/p' "$zshrc")"
assert test "$SSH_AUTH_SOCK" = "$shared_sock"

# Unreachable shared agents fail clearly, without exporting the bad candidate.
shared_status=2
export SSH_AUTH_SOCK=/mock/stale-socket
if _ensure_ssh_agent 2>/dev/null; then
  print -u2 -- 'FAIL: unreachable shared agent was accepted'
  exit 1
fi
assert test "$SSH_AUTH_SOCK" = /mock/stale-socket

# Every lazy wrapper survives failed initialization so the user can retry.
eval "$wrappers"
for cmd in ssh scp sftp rsync; do
  if "$cmd" unused 2>/dev/null; then
    print -u2 -- "FAIL: $cmd ignored agent failure"
    exit 1
  fi
  assert test "${+functions[$cmd]}" -eq 1
done

# Key-loading failures must not be silently ignored.
shared_status=0
load_status=1
if _ensure_ssh_agent; then
  print -u2 -- 'FAIL: key-loading failure was ignored'
  exit 1
fi

print -- 'SSH agent checks passed'
