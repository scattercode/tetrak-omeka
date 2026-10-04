# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this repository is

A demo of Tetrak working with Omeka S: a pinned local Omeka stack, collections
in it, scripts that send its images through Tetrak and write the transcripts
back, and tutorial pages. `README.md` has the status of each part.

It sits beside, not inside, Tetrak:

- **Tetrak** (public, [tetrak.dev](https://tetrak.dev/)) is the OCR pipeline.
  This repository uses it **only as an installed package**, pinned to a
  release on PyPI (`tetrak`). Never import from or point
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
  `COMPOSE_PROJECT_NAME` and `OMEKA_PORT` run a second copy alongside; use
  one for experiments rather than resetting somebody's demo instance.

## Collections and seeding

`scripts/reset.sh` is the clean starting point for demos and tutorials:
`down -v`, rebuild, `scripts/install.sh`, `scripts/seed.py`. Write tutorials
to begin from it.

- **Only install, modules and the API key bypass the REST API.**
  `omeka/setup.php` does those three, because the API cannot. Everything else, seeding included,
  goes through the public API, since that is what the tutorials teach. Do not
  add direct database or service calls for anything the API can do.
- **`collections/<name>/collection.toml` is the record of what goes in.**
  `collections/README.md` has the format. Identifiers are the match keys, so
  never change one without a reset. The seeder adds what is missing and never
  edits what exists: a metadata change reaches Omeka only through a reset.
- **Every image needs a `SOURCES.md` entry before it is added**, as in
  Tetrak's corpus. The ephemera are byte-identical copies of Tetrak corpus
  fixtures; the Armenian pages are byte-identical to `tetrak-hy-trainer`'s
  Wikisource harvests, with each page's revision pinned. Only the
  encyclopedia pages are held out from the recogniser's training.
- **The sites' reader is Octopus Viewer, placed by the `tetrak-reader`
  theme.** Its right-hand panel is the selected page's `displayValues()`, so
  anything written to a page's media appears beside the image. Pin the
  module by version and SHA-256 in `omeka/Dockerfile`, as Omeka is. The theme
  is built from Omeka's default theme by `omeka/build-theme.sh`, whose edits
  fail the build if the default theme changes; never commit a copy of the
  theme. Site settings are not in the API, so configure through the theme,
  not the admin interface.
- **Reference transcripts are `tetrak:referenceTranscript`; Tetrak's are
  `tetrak:transcript`**, with `tetrak:transcribedWith` beside it. All three
  are defined in `collections/vocabularies.toml`. Never write one over the
  other: the demo is the comparison.
- **The untranscribed items are the demo, not gaps.** Grauman's, the
  playbill, *The Death of Kikos* and the medical encyclopedia have no
  reference transcript on purpose, for `scripts/transcribe.py` to fill. Do
  not add one, and keep `tutorials/transcribe-with-tetrak.md`, whose outputs
  are real runs, in step with them.
- **Writing a value back means fetching the whole record and PUTting it.**
  Omeka treats any request carrying property values as the complete set, so
  a PATCH of one property deletes the rest. `scripts/transcribe.py` shows the
  pattern.
- **Tetrak comes from PyPI as `tetrak`, pinned with `==`**; `tetrak-ocr` is
  only the command. The pin is in the tutorial, `transcribe.py` (docstring
  and `INSTALL`), the CI transcription step and README's install line. Move
  them together, and re-run the tutorial's commands, since it quotes real
  output.
- **The Soviet Armenian Encyclopedia is CC BY-SA 3.0, not public domain.**
  Anything published from it, transcripts included, needs attribution and the
  same licence.
- **Omeka 4.1.1 answers `DELETE` on items and media with HTTP 500, but the
  delete succeeds.** It fails rendering the deleted resource afterwards. A
  script that deletes should check for a 404 afterwards rather than trust the
  status code.

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
