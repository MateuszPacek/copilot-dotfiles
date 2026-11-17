# Personal Copilot setup for Codespaces

This repository can install personal Copilot instructions, agents, skills, and
workflow helpers in a new Codespace. Project files remain separate. The
installer does not install Copilot hook configuration or VS Code user settings.

## Current limitation

The `asd-ste100` skill's Git tracking has been changed from a submodule to
ordinary files. Review the staged deletion and added files before committing.
The installer stops if the skill is missing. Installer behavior has not yet
been verified in a Codespace.

The language workflow uses the skill's bundled references without requiring a
local standard. The skill describes an optional official-source check and a
limited fallback. Bundled guidance is incomplete and does not prove compliance.
Do not copy or upload the standard as part of this setup.

## Review before publishing

1. Confirm that your GitHub repository is private and that company policy
   permits uploading each selected file. A private repository does not replace
   that approval.
2. In VS Code, open **Source Control** and review each change. Do not upload
   credentials, confidential information, or restricted material.
3. Review all skill files before publishing.
4. On Windows, stage the installer with executable permission. In a terminal
   opened at the repository root, use:

   ```text
   git add --chmod=+x install.sh
   ```

   This stages the installer; it does not commit or push it. Review its staged
   content and the other selected changes. Stage only approved files, enter a
   commit message, and select **Commit**. Then use **Sync Changes** or **Push**
   to send the commit to GitHub. Resolve any Git errors before continuing.

A **commit** saves a version in your local repository. A **push** sends the
committed version to GitHub. Changes in the local folder are not sent until
you commit and push them.

## Enable for new Codespaces

1. Open [GitHub Codespaces settings](https://github.com/settings/codespaces).
2. Under **Dotfiles**, enable **Automatically install dotfiles** and select
   this repository.
3. Create a new Codespace for a project you trust. Codespaces clones the
   dotfiles repository and runs its executable `install.sh`.
4. In the Codespace, select the Copilot session you intend to use. Run
   **Chat: Open Customizations** and inspect **Instructions**, **Agents**, and
   **Skills**. Start a fresh chat and test representative personal and project
   instructions separately. Check references or agent debug logs where
   available; appearing in the list does not prove that a file was used.

The installer places personal files under `~/.copilot` on the Codespace host.
It derives the general personal instruction file from the existing personal
instruction source, and does not also install that source as a modular
instruction. Other modular instructions remain separate.
It also installs `workflow-kit/` under `~/.copilot`. For the Claude Code route,
run `bash ~/.copilot/workflow-kit/install-claude.sh`; that installer places the
Claude-specific files in `~/.claude` and project helpers in `~/.workflow-kit`.
Review the workflow guide before merging its devcontainer snippet into a
project configuration.

Copilot can combine applicable personal and project instructions. There is no
general precedence rule between them, so resolve conflicting instructions
rather than assuming either always wins. Discovery and behavior depend on the
selected session and environment. Organization policies still apply.

## Conflicts and updates

The installer checks selected destination paths before copying. If a selected
file already exists, or a destination directory is not a normal directory,
it reports the conflict and stops. Unrelated existing files and project files
are left alone. A later copy error can leave a partial installation; review
the reported paths before making any manual changes.

Changes pushed to the dotfiles repository are applied to **new** Codespaces;
existing Codespaces do not automatically receive them. To use an update, create
a new Codespace or choose and review a separate manual update method.

If setup fails, see [GitHub's personalization troubleshooting guide](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-personalization-for-codespaces).
Do not overwrite existing configuration to resolve a conflict without first
reviewing it.

This installer is for Codespaces. GitHub Copilot cloud sandboxes do not run
dotfiles install scripts and require a different repository layout.
