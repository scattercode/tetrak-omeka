# tetrak-omeka

A demonstration of [Tetrak](https://tetrak.dev/) working with
[Omeka S](https://omeka.org/s/): a local Omeka instance with collections in
it, scripts that send its images through Tetrak and put the transcripts back,
and tutorials that walk through doing the same with your own material.

It is a demo, not a deployment. Everything runs on your machine, bound to
localhost, and nothing here should be pointed at material that matters.

## Status

| Part | State |
|---|---|
| A stable, pinned Omeka S stack | Done: see below |
| A collection of Tetrak's corpus images (Los Angeles theatre ephemera) | Planned |
| A collection of Armenian books | Planned |
| Scripts that transcribe an Omeka collection with Tetrak | Planned |
| Tutorial pages | Planned, possibly as a GitHub Pages site |

## Running Omeka

You need Docker with Compose.

```bash
cp .env.example .env
docker compose up -d --build
open http://localhost:8080
```

The first visit runs Omeka's installer, which asks for the admin email and
password to create. Those are yours and are not stored here.

```bash
docker compose down       # stop, keep the data
docker compose down -v    # stop, discard the data and start clean
```

## What the stack is

Two services and two named volumes: Omeka S, and MariaDB, the MySQL-compatible
database Omeka's own documentation assumes.

Omeka has no official Docker image, and the community ones are abandoned,
amd64-only, or ignore environment configuration. So `omeka/Dockerfile` builds
one from the official release zip on `php:8.2-apache`, checking the zip against
a pinned SHA-256, with ImageMagick for thumbnails. `omeka/docker-entrypoint.sh`
writes Omeka's `config/database.ini` from the `OMEKA_DB_*` variables at
start-up, so `.env` stays the only place the credentials live.

Both versions are pinned rather than tracking `latest`, so the demo still comes
up when somebody returns to it months later. To upgrade Omeka, change
`OMEKA_VERSION` and `OMEKA_SHA256` in `omeka/Dockerfile` together, bump the
image tag in `compose.yaml` to match, and rebuild. The database has a real
health check and Omeka waits for it, because Omeka's installer fails
confusingly against a database that is still starting.

Two choices are deliberate:

- **It binds to `127.0.0.1`, not to every interface.** Between `compose up`
  and finishing the installer, anyone who can reach the port can claim the
  admin account.
- **The database credentials in `.env.example` are not secrets.** They are
  local scaffolding for a service on localhost. `.env` is gitignored so a real
  one can be kept without being committed, but this stack is not built to hold
  anything sensitive.

## How it uses Tetrak

As an installed package, pinned to a release of the public repository, never
as a sibling checkout of it. Tetrak is not on PyPI, so that means:

```bash
pip install "tetrak[all] @ git+https://github.com/scattercode/tetrak@5.14.0"
```

Pinning a tag rather than a checkout keeps this demo working for anyone who
clones it on its own, and makes it an honest test of Tetrak as other people get
it.

## Licence

MIT; see [LICENSE](LICENSE). Omeka S itself is GPL-3.0 and is not
redistributed here: `omeka/Dockerfile` downloads the official release when the
image is built. Collection material carries its own rights, recorded beside it.
