---
name: git-workflow
description: Branch, staged pull request, failure issue and automated fix procedures using git and the GitHub CLI. Use for /flow start, pr, issue and fix.
---

# Git, PR and issue procedures

Uses `git` and `gh`. If `gh auth status` fails, tell the user to run `gh auth login` and stop. Ask before every push, PR and issue. Find the default branch with `git symbolic-ref --short refs/remotes/origin/HEAD` (strip the `origin/` prefix); if that fails, ask the user.

## Branches

Names: feat/SLUG/br, feat/SLUG/prd, feat/SLUG/tr, feat/SLUG/code. Create each from its parent branch with `git switch -c BRANCH PARENT`. Require a clean working tree first. Push with `git push -u origin BRANCH` after the user agrees.

## Staged PR (`/flow pr LAYER`)

Allowed only when workflow/state.md shows PASS for the branch's current HEAD commit. If not, say so and propose the gate.
The base is the PR base from skill workflow-manager. Write the body to a temporary file: requirement IDs covered, gate report path, link to the parent layer. Then run:

`gh pr create --base BASE --head BRANCH --title "[LAYER] FEATURE" --body-file FILE`

Add `--draft` when workflow/config.md says pr_mode is draft, leave it out when ready, and if blank ask and record the answer. Record the PR URL in workflow/state.md. Never merge. Remind the user of the merge order: code to tr, tr to prd, prd to br, br to the default branch.

## Failure issue (`/flow issue`)

From the latest failed gate report run:

`gh issue create --title "[gate:LAYER] REQUIREMENT IDS failed" --body-file FILE`

Add `--label` values from issue_labels in workflow/config.md if set. The body lists the failing tests with paths, the requirement IDs, links to the requirement files, the gate report path, the branch and the commit SHA. Record the issue number in workflow/state.md.

## Automated fix (`/flow fix ISSUE_NUMBER`), optional and user-triggered

1. Read the issue and the gate report it names.
2. Create `fix/ISSUE-SLUG` from the failing layer's branch.
3. Fix the smallest cause, following skill test-first-coding. Do not edit requirements to make tests pass.
4. Re-run the failed gate through the verifier. At most 2 attempts, then stop and report.
5. On PASS, ask before pushing, then open a PR with the failing layer branch as base and "Refs #ISSUE" in the body. Do not write "Fixes": the base is not the default branch, so the issue would not close.
