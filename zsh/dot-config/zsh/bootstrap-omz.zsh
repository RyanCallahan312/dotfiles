#!/usr/bin/env zsh

emulate -L zsh -o pipefail -o no_unset

typeset -r zsh_root="${ZSH:-$HOME/.oh-my-zsh}"
typeset -r manifest_path="${0:A:h}/omz-repos.lock"

ensure_repo() {
  local name=$1
  local relative_path=$2
  local remote_url=$3
  local commit_sha=$4
  local repo_dir="$zsh_root"
  local current_remote

  if [[ "$relative_path" != '.' ]]; then
    repo_dir+="/$relative_path"
  fi

  if [[ -d "$repo_dir/.git" ]]; then
    current_remote=$(git -C "$repo_dir" remote get-url origin 2>/dev/null || true)

    if [[ -n "$current_remote" && "$current_remote" != "$remote_url" ]]; then
      print -u2 -- "Skipping $name: origin is $current_remote (expected $remote_url)."
      return 0
    fi

    if [[ -n $(git -C "$repo_dir" status --porcelain --untracked-files=no 2>/dev/null) ]]; then
      print -u2 -- "Skipping $name: repository has local changes."
      return 0
    fi

    git -C "$repo_dir" fetch --tags origin
  else
    mkdir -p "${repo_dir:h}"
    git clone "$remote_url" "$repo_dir"
  fi

  git -C "$repo_dir" checkout --detach "$commit_sha"
}

if [[ ! -r "$manifest_path" ]]; then
  print -u2 -- "Missing manifest: $manifest_path"
  exit 1
fi

while IFS='|' read -r name relative_path remote_url commit_sha; do
  if [[ -z "${name// }" || "$name" == \#* ]]; then
    continue
  fi

  ensure_repo "$name" "$relative_path" "$remote_url" "$commit_sha" || exit 1
done < "$manifest_path"

print -- "Oh My Zsh runtime is pinned under $zsh_root"
print -- "Restart zsh when you are ready."
