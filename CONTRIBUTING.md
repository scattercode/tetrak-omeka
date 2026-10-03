# Contributing

Thanks for your interest in tetrak-omeka. This covers how we work here: the
checks, the commit style, and the automation they feed. It applies to us as
much as to anyone sending a pull request.

## Getting set up

```bash
brew install lefthook hadolint shellcheck actionlint markdownlint-cli2
lefthook install
cp .env.example .env && docker compose up -d --build
```

Without lefthook, `git config core.hooksPath .githooks` still activates the
Conventional Commits check on its own.

## The checks

The pre-commit hooks lint what you stage; CI runs the same and more, and every
job is required before a pull request can merge:

| Check | What it runs |
|---|---|
| Lint | hadolint on `omeka/Dockerfile`, shellcheck on the scripts, actionlint on the workflows, markdownlint, and `docker compose config` |
| Omeka stack comes up | builds the image from the pinned release, starts the stack and waits for Omeka to answer |
| Trivy scan | HIGH and CRITICAL vulnerabilities with a fix available in the built image, and misconfiguration in the Dockerfile and compose file |
| Shared templates are current | `cliff.toml` and `.githooks/commit-msg` match `scattercode/release-pipelines` |
| PR title is a Conventional Commit | the title becomes the squash-merged commit, which the release reads |

A weekly run repeats the Trivy scans, MariaDB included, against a fresh build.
Accepted findings are listed in `.trivyignore` with their reasons.

## Commit style

Commits and pull request titles follow
[Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>[(scope)][!]: <description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`,
`ci`, `chore`, `revert`. The description has no trailing full stop, and the
header is 100 characters or fewer (72 preferred).

This is load-bearing: the release automation computes the next version from
the commit types (`fix` → patch, `feat` → minor, `!` → major) and writes
`CHANGELOG.md` from the messages.

## Releases and the changelog

Releases are automated; never perform one by hand. Every push to `main` runs
`release.yml`, which computes the next version, prepends that section to
`CHANGELOG.md`, tags it and publishes a GitHub Release. Never edit
`CHANGELOG.md` or create tags yourself; fix the commit messages instead.

## Conventions

- British English throughout; sentence case for headings.
- Docs and tutorials are written in the first person plural.
- Collection material must be public domain or openly licensed, with its source
  and rights recorded beside it.

## Security

Please report suspected vulnerabilities privately: see
[SECURITY.md](SECURITY.md), not the issue tracker.
