#!/usr/bin/env bash
# PreToolUse guard: force a permission prompt (even in auto mode) for risky shell commands.
# Matches the raw hook JSON on stdin, so it also sees commands wrapped in wsl.exe, bash -c or PowerShell.
input=$(cat)
reasons=()
has() { grep -Eiq -- "$1" <<<"$input"; }

# 1. pip install/uninstall, any pip path (venv pip, pip3, python -m pip, uv pip)
has '(^|[^[:alnum:]_-])pip3?(\.exe)?["'"'"'[:space:]]+(install|uninstall)([^[:alnum:]_]|$)' && reasons+=("pip install/uninstall")
has '-m[[:space:]]+pip[[:space:]]+(install|uninstall)' && reasons+=("python -m pip install/uninstall")
# 2. sudo
has '(^|[^[:alnum:]_])sudo[[:space:]]' && reasons+=("sudo")
# 3. git push (also catches `G="... git"; $G push`)
has '(^|[^[:alnum:]_])git([^[:alnum:]_].*)?[^[:alnum:]_]push([^[:alnum:]_]|$)' && reasons+=("git push")
# 4. downloads piped/substituted into a shell or interpreter
has '(curl|wget|iwr|irm|invoke-webrequest|invoke-restmethod)[^;&]*\|[[:space:]]*(sudo[[:space:]]+)?(sh|bash|zsh|dash|python3?|iex|invoke-expression)([^[:alnum:]_]|$)' && reasons+=("download piped to shell")
has '(<\(|\$\()[[:space:]]*(curl|wget)' && reasons+=("download substituted into shell")
# 5. deletions, unless the whole command is one `rm` whose every path is under cache/ or data/ (no "..")
if has '(^|[^[:alnum:]_-])(rm|rmdir|unlink|del|erase|rd|remove-item|ri|shred)[[:space:]]|shutil\.rmtree|os\.(remove|unlink|rmdir)|\.unlink\(|git[[:space:]]+clean|-delete([^[:alnum:]_]|$)|-exec[[:space:]]+rm'; then
  if ! has '"command": ?"rm( -[rRf]+)*( +(\./)?(cache|data)/[^ ;&|<>$`\\"*?]+)+"' || has '\.\.'; then
    reasons+=("delete outside cache/ or data/")
  fi
fi

if ((${#reasons[@]})); then
  msg=$(printf '%s; ' "${reasons[@]}"); msg=${msg%; }
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"interproll guard: %s"}}\n' "$msg"
fi
exit 0
