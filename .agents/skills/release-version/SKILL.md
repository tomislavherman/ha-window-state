---
name: release-version
description: Prepare or publish a new Window State integration release for HACS. Determine the version from changes, update version declarations, validate, push main, and publish GitHub release notes.
---

# Release Window State

Repository: the GitHub repository associated with the current checkout.
Release branch: `main`.
Use Git and GitHub CLI (`gh`). A request to publish authorizes the version commit,
push, tag creation, and release. A request only to prepare or preview authorizes
preparation only. Editing this skill does not authorize a release.

## Inspect and select a version

1. Inspect status, branch, remotes, and release workflows. Resolve the GitHub
   repository with `gh repo view --json nameWithOwner,url` from the checkout and
   verify it matches the intended push remote, especially for forks. Store its
   `nameWithOwner` as `release_repo` and use `--repo "$release_repo"` consistently
   for GitHub commands. Build comparison links from the resolved repository URL.
   Fetch origin and tags.
   Use current `main`, fast-forwarding when safe. Preserve local work; do not
   discard changes, force-push, or silently include unrelated uncommitted work.
   Complete already authorized pending changes; clarify inclusion only if unclear.
   Resolve divergent history before proceeding.
2. Identify the latest published stable GitHub release using `gh release view`
   or `gh release list`, excluding drafts and prereleases. Use its tag as the
   baseline, not the newest local tag. Resolve the tag to a commit and verify it
   is an ancestor of `main`. Clarify the baseline if no stable release exists or
   its history cannot be resolved.
3. Inspect the log and full diff from the baseline tag to `main`, including local
   commits intended for release. Choose the highest applicable increment:
   - Patch: compatible fixes, tuning defaults, translations, documentation, or
     maintenance without a new user-facing capability.
   - Minor: new backward-compatible user-facing features or options.
   - Major: incompatible configuration, removal of supported behavior, changed
     entity identities, or changes requiring migration.
   Apply these same rules at `0.x`; do not silently downgrade breaking changes
   to minor. Judge actual changes, not only commit prefixes. Respect an explicit
   user version; explain compatibility conflicts before publication.
4. Calculate the next `X.Y.Z` from the baseline. Inspect any already bumped
   manifest version to avoid double increments when resuming. Verify the target
   version is newer and has no conflicting release/tag. Use bare numeric tags
   such as `0.3.1`, without `v`. If no changes exist, do not manufacture a release.

## Prepare

- Search tracked files for current-version declarations. Currently the only
  integration version declaration is `version` in
  `custom_components/window_state/manifest.json`. Update all current-version
  declarations if more are introduced. Keep manifest, tag, and release title
  identical. Preserve historical versions, dependencies, and Home Assistant
  minimum versions, including `hacs.json`'s `homeassistant` value.
- Write concise Markdown release notes from ALL changes on `main` since the
  baseline, including direct commits rather than only PRs. Inspect the diff and
  explain observable changes. Mention breaking changes, migrations, changed
  defaults, and treatment of saved settings where applicable. Omit internal
  maintenance unless useful to users. Link relevant issues/PRs when supported.
  Include a GitHub comparison link from baseline tag to new tag. Save exact
  notes to a temporary file outside the repo; no changelog file is required.
- Validate JSON, parse Python without importing Home Assistant, and run
  `git diff --check`. Run further checks appropriate to behavioral changes.
  Review the version diff and notes. Report the chosen version and rationale.
- Commit version changes, conventionally `chore: release X.Y.Z`, staging explicit
  paths. Commit pending product/documentation work separately where appropriate.
  Record the full release commit SHA.

## Push and publish

1. Push `main` normally and verify the release SHA is on `origin/main`. If branch
   protection requires a PR, follow that process and use the merged SHA instead
   of bypassing protection.
2. Wait for `.github/workflows/validate.yml` (`Validate`) to succeed for that exact
   SHA, including HACS and Hassfest jobs. Use bounded polling and progress updates.
   Do not publish while checks are failed or unresolved.
3. Publish a stable GitHub release using the inspected values:

   ```sh
   gh release create "$release_version" --repo "$release_repo" \
     --target "$release_sha" --title "$release_version" \
     --notes-file "$release_notes_file" --latest --fail-on-no-commits
   ```

   `release_repo` is the resolved current repository, `release_sha` is the full
   validated commit SHA; `release_notes_file` contains
   the reviewed notes. GitHub creates the tag automatically if absent, so no
   separate tag command or tag push is needed. If a tag already exists, verify
   its peeled commit matches the release SHA before using it: `--target` does not
   move existing tags. Never replace a published tag automatically.
4. Fetch tags. Verify the published release is neither draft nor prerelease,
   its tag resolves to the validated SHA, its title and notes are correct, and
   the tagged manifest contains the same version. Report the release URL,
   version, and validation result.

If a mutation times out or fails ambiguously, inspect remote branch, tag, and
release state before retrying. Resume from the completed step; do not increment
again or create duplicates. If blocked, report the blocker and exact published
state.

HACS reads the published GitHub release and its body for release notes. This repo
currently has no `zip_release` setting, so no ZIP upload is required. Discovery
is asynchronous; do not promise immediate updates or change `hacs.json` merely
to release a version.

References: [GitHub CLI](https://cli.github.com/manual/gh_release_create),
[HACS publishing](https://www.hacs.dev/docs/publish/start/).
