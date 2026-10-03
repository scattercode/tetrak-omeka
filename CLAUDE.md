# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

A demo of Tetrak working with Omeka S: a pinned local Omeka stack, collections
in it, scripts that send its images through Tetrak and write the transcripts
back, and tutorial pages. `README.md` has the status of each part.

It sits beside, not inside, Tetrak:

- **Tetrak** (public, [tetrak.dev](https://tetrak.dev/)) is the OCR pipeline.
  This repository uses it **only as an installed package**, pinned to a
  release tag of `github.com/scattercode/tetrak`. Never import from or point
  at a sibling checkout (`../tetrak`): the demo has to work for someone who
  clones only this repository.
- **tetrak-easyocr-armenian** supplies the Armenian recogniser, through
  Tetrak's `[armenian]` extra; the Armenian collection depends on it.
- **tetrak-product** (private) holds the product plan. This was brief 006
  (the DAM proof of concept) and the follow-up to the repository split. Cite
  briefs by number, never by path or link.

## The Omeka stack

`compose.yaml` at the root, with the image built from `omeka/` alone, so the
collections and scripts never enter the Docker build context. Keep it that
way: anything the image needs goes in `omeka/`.

- **Versions are pinned.** Omeka by version and SHA-256 in `omeka/Dockerfile`
  (change both together and bump the image tag in `compose.yaml`), MariaDB by
  tag. Never move to `latest`.
- **It binds to `127.0.0.1`.** The first-run installer sets the admin
  password, so the port must not be reachable from the network before then.
- **`.env` is the only place credentials live.** The entrypoint renders
  Omeka's `config/database.ini` from it at start-up. `.env.example` holds
  local demo values, not secrets; `.env` is gitignored.
- The Compose project is named `tetrak-omeka`, so its volumes are
  `tetrak-omeka_db-data` and `tetrak-omeka_omeka-files`.

## Checks and releases

Set up like the other Tetrak repositories; `CONTRIBUTING.md` has the table.

- **Pre-commit (Lefthook):** hadolint, shellcheck, actionlint, markdownlint and
  `docker compose config` on what is staged; the commit-msg hook enforces
  Conventional Commits. CI runs the same, so a skipped hook only moves the
  failure to the pull request.
- **CI:** Lint, the stack smoke test, Trivy (the built image and the
  Dockerfile/compose configuration), the shared-template drift check, and the
  PR-title check. All are required by the `main` ruleset; `main` takes nothing
  by direct push except the `scattercode-release` App's release commit.
- **`.trivyignore` and the gosu skip** in `security.yml` record accepted
  findings with their reasons. Add to them only with a reason and a date.
- **The image upgrades Debian's packages at build time**, because the official
  PHP image lags Debian's security fixes. Omeka and PHP stay pinned.
- **Releases are automated** from the commit types: git-cliff prepends to
  `CHANGELOG.md`, the shared next-version action picks the version, and
  `release.yml` tags and publishes. `cliff.toml` and `.githooks/commit-msg` are
  synced from `scattercode/release-pipelines`; never edit them here.

## Conventions

- British English throughout; sentence case for headings.
- Docs and tutorials are written in the first person plural: this is a
  collaborative project.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/):
  `<type>[(scope)][!]: <description>`.
- Collection material must be public domain or openly licensed, with its
  source and rights recorded beside it, as Tetrak's corpus records them in
  `evaluation/ocr/corpus/SOURCES.md`.
