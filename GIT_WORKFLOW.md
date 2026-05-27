# Git workflow — plain-English guide

This repo lives on GitHub at `douglasmossmd/faers-drug-safety-data-viz`. You
are working on your own branch (`liviea-work`) so nothing you do can break
`main` until you choose to merge it.

---

## One-time setup (already done for you)

- The repo is cloned at `~/Desktop/GLP1/faers-repo/`.
- Your git identity is set: `liviea` / `liviaa@uci.edu`.
- You are on branch `liviea-work`.
- A "Stop hook" is configured so Claude will remind you to commit after
  meaningful edits.

You still need to sign in to GitHub from your terminal — once — by running:

```
gh auth login
```

Pick: GitHub.com → HTTPS → "Login with a web browser". Follow the prompts.

---

## The mental model

Think of git like saving versions of an essay:

1. **Branch** = a private draft of the project. Yours is `liviea-work`.
2. **Commit** = saving a snapshot with a short note about what you changed.
3. **Push** = uploading your snapshots to GitHub.
4. **Merge to main** = once your work is solid, fold it into the shared copy.

You'll spend most of your time in the commit → push loop.

---

## Daily loop

### 1. See what you've changed
```
git status
```

### 2. Stage the files you want in this snapshot
```
git add path/to/file1 path/to/file2
```
(Or `git add .` to stage everything that changed — only if you're sure.)

### 3. Commit with a short, informative message
```
git commit -m "Update README intro and fix typo in section 2"
```

**A good commit message:**
- Starts with a verb in present tense: "Add", "Fix", "Update", "Remove".
- Says **what** changed in one line (under ~70 characters).
- Optionally, leave the editor open (drop the `-m "..."`) to add a longer
  explanation of **why** on the lines below.

**Examples:**
- ✅ `Add data dictionary table to README`
- ✅ `Fix broken link in section "Sources"`
- ❌ `update` ← too vague
- ❌ `stuff` ← never

### 4. Push your work to GitHub
**The very first push** of this branch:
```
git push -u origin liviea-work
```
**Every push after that:**
```
git push
```

---

## Merging to main (when a chunk of work is finished)

You should not push directly to `main`. Instead, open a **Pull Request**
(PR) — GitHub will check for conflicts and let douglasmossmd review.

```
gh pr create --title "Short summary of your work" --body "What you changed and why"
```

This opens a PR from `liviea-work` → `main`. Once it's approved and merged
on GitHub, your changes are live on main.

---

## Staying in sync (avoid conflicts)

Before starting a new session of work, pull the latest `main` into your
branch so you don't drift apart from douglasmossmd's changes:

```
git checkout main
git pull
git checkout liviea-work
git merge main
```

If git says "CONFLICT", **stop and ask for help** — don't try to force it.
Conflicts are normal and fixable, but they need a careful eye.

---

## Cheat sheet

| What you want | Command |
|---|---|
| See what changed | `git status` |
| See exact line-by-line changes | `git diff` |
| Stage a file | `git add <file>` |
| Save a snapshot (commit) | `git commit -m "message"` |
| Upload to GitHub | `git push` |
| Get latest from main | `git pull origin main` |
| See history | `git log --oneline -20` |
| Which branch am I on? | `git branch --show-current` |

---

## If something looks scary

**Don't run anything destructive** (`reset --hard`, `push --force`, `rm -rf`).
Stop, take a screenshot of the terminal, and ask.

Almost every "broken" git state is recoverable.
