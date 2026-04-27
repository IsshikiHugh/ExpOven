---
name: notify
description: >
  Send a notification via ExpOven's `ding` CLI to whichever messaging platform(s)
  the user has configured (DingTalk, Feishu/Lark, Slack, email, ...).
  Triggers: "notify", "ding", "alert me", "let me know when done".
allowed-tools: Bash(ding *), Bash(oven list-ogroups), Bash(oven help), Bash(mkdir -p *), Bash(printf *), Bash(rm *)
---

# Notify

Sends a notification through [ExpOven](https://github.com/IsshikiHugh/ExpOven)'s `ding` CLI. ExpOven dispatches the message to whichever notification group (`ogroup`) the user has configured — DingTalk, Feishu/Lark, Slack, email, etc.

This skill remembers which ogroup to route to: it asks once on first use, stores the choice per-user, and exposes sub-commands to change it later.

---

## Input

Parse `$ARGUMENTS`. Recognized forms:

| Args | Behavior |
|------|----------|
| *(empty)* | Send `Task complete` using the saved ogroup |
| `<message>` | Send `<message>` using the saved ogroup |
| `--set-group <name>` | Save `<name>` as the ogroup this skill uses (no notification sent) |
| `--show-group` | Print the currently saved ogroup (no notification sent) |
| `--reset-group` | Forget the saved ogroup (no notification sent) |

Examples:
- `/notify` — sends "Task complete"
- `/notify Training finished epoch 50` — sends that message
- `/notify --set-group work` — switches the routing target to the `work` ogroup
- Auto-triggered after a long task completes

---

## State

The chosen ogroup is persisted at:

```
${OVEN_HOME:-$HOME/.config/oven}/claude-notify-group
```

Single line, plain text, ogroup name only. Honors a custom `$OVEN_HOME` if set; falls back to ExpOven's default. The file lives outside any project repo, so the choice is per-user and not committed anywhere.

---

## Workflow

### Step 1 — Branch on sub-commands

If `$ARGUMENTS` begins with one of the config flags, handle it and exit *without* sending a notification.

#### `--set-group <name>`

1. Run `oven list-ogroups` and capture stdout.
2. If `<name>` does not appear in the listed groups, refuse: print the available groups and instruct the user to either pick an existing one or create the YAML file under `$OVEN_HOME/ogroups/`.
3. Resolve the state file path: `STATE="${OVEN_HOME:-$HOME/.config/oven}/claude-notify-group"`.
4. Ensure the parent directory exists, then write the name:
   ```bash
   mkdir -p "$(dirname "$STATE")"
   printf '%s\n' "<name>" > "$STATE"
   ```
5. Tell the user the ogroup is saved.

#### `--show-group`

Read the state file. If it exists and is non-empty, print the contents. Otherwise, tell the user no ogroup is saved yet and that one will be requested on the next `/notify` call.

#### `--reset-group`

Delete the state file:

```bash
rm -f "${OVEN_HOME:-$HOME/.config/oven}/claude-notify-group"
```

Confirm to the user that the saved ogroup has been cleared.

### Step 2 — Resolve the ogroup (notification path)

If the call is a notification (no config flag), determine which ogroup to use:

1. Read the state file. If it exists and is non-empty → use its contents as `<group>` and skip to Step 3.
2. **First-run setup:**
   1. Run `oven list-ogroups` to enumerate available groups.
   2. If the command fails or returns no groups, surface the error: ExpOven config is likely uninitialized. Suggest `oven init-cfg`, then abort without sending anything.
   3. Use `AskUserQuestion` to ask the user which ogroup this skill should send to. Offer up to 4 of the listed groups as options. If there are more than 4, list the rest in the question text and rely on the implicit "Other" option for typing a name.
   4. Persist the chosen name to the state file (same `mkdir -p` + `printf` pattern as `--set-group`).
3. Continue with the chosen `<group>`.

### Step 3 — Send the notification

Default the message to `Task complete` if `$ARGUMENTS` (after stripping any flags) is empty. Then run:

```bash
ding --ogroup "<group>" "<message>"
```

Make sure `<message>` is shell-quoted so spaces and special characters survive intact.

---

## Error Handling

| Error | Detection | Action |
|-------|-----------|--------|
| `ding` not in `PATH` | "command not found" / non-zero exit on first invocation | Tell the user ExpOven is not installed (or not on `PATH`); link them to the project README's Installation section. |
| `oven list-ogroups` fails or empty | Non-zero exit code, or empty stdout | ExpOven config is missing/uninitialized. Ask the user to run `oven init-cfg` and rerun. |
| `--set-group <name>` references an unknown group | `<name>` absent from `oven list-ogroups` output | Refuse, print the available groups, suggest creating a YAML under `$OVEN_HOME/ogroups/` if they want a new one. |
| `ding` returns non-zero | Exit code != 0 | Forward stderr to the user; common causes are an invalid hook/token in the ogroup's YAML. |
| State file unreadable | Permission error on read | Suggest `--reset-group` followed by a fresh first-run setup. |

---

## Quality Checklist

- [ ] Sub-command branch exits without sending a notification
- [ ] First-run flow asks for an ogroup before sending anything
- [ ] State file path uses `${OVEN_HOME:-$HOME/.config/oven}` — no hardcoded paths
- [ ] `--set-group` validates the name against `oven list-ogroups` before writing
- [ ] Default message (`Task complete`) fires on empty args
- [ ] Message is properly shell-quoted
- [ ] Skill body contains no user-specific paths, usernames, or secrets
