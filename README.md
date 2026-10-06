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
| A collection of Tetrak's corpus images (Los Angeles theatre ephemera) | Done: five items, three with reference transcripts |
| A collection of Armenian books | Done: four items, two with reference transcripts |
| Scripts that reset, install and seed Omeka | Done: see below |
| A site for each collection, with a page reader | Done: each page beside its transcripts |
| A script that transcribes an Omeka collection with Tetrak | Done: `scripts/transcribe.py` |
| Tutorials | One, in `tutorials/`: [transcribing a collection with Tetrak](tutorials/transcribe-with-tetrak.md). Possibly a GitHub Pages site later |

## Running Omeka

You need Docker with Compose, and Python 3.11 or later.

```bash
cp .env.example .env
scripts/reset.sh
open http://localhost:8080/s/armenian-books
```

`scripts/reset.sh` is the clean starting point for every demo and tutorial.
It throws away whatever Omeka holds, rebuilds and starts the stack, installs
Omeka with the admin account from `.env`, and loads both collections, each
with a public site: `/s/los-angeles` and `/s/armenian-books`. The admin
interface is at `/admin`. It asks
before deleting anything (`--yes` skips the question) and takes well under a
minute once the image is built. Log in with `OMEKA_ADMIN_EMAIL` and
`OMEKA_ADMIN_PASSWORD` from `.env`.

The steps it runs also work on their own:

| Command | What it does |
|---|---|
| `scripts/install.sh` | Installs Omeka and its modules if they are not installed yet, and writes a fresh API key to `.omeka-api.env` (`.omeka-api.<project>.env` for another Compose project) |
| `python3 scripts/seed.py` | Loads whatever is missing from `collections/` through the REST API; safe to repeat |
| `scripts/reset.sh --no-seed` | A clean, installed Omeka with nothing in it |

Omeka's REST API can do everything except the three steps that come before
it: the installer is a web form, and modules and API keys are only installed
or created in the admin interface. `omeka/setup.php` does all three from the
command line, through Omeka's own services. Everything after that goes through the public API, the same one
the tutorials use. `collections/README.md` describes the collections, their
sites and their manifest format.

The sites' item pages use
[Octopus Viewer](https://github.com/biblibre/omeka-s-module-OctopusViewer), a
lightweight page viewer: the item's pages down the left, the selected page in
the middle, and that page's transcripts on the right, with Tetrak's score
against the reference where there is one.
It is pinned in `omeka/Dockerfile` like Omeka itself, and placed by the
`tetrak-reader` theme, which `omeka/build-theme.sh` derives from Omeka's
default theme at build time and dresses in tetrak.dev's design: its palette,
and its fonts, self-hosted so the demo works offline.

Without the scripts, Omeka still works the usual way: `docker compose up -d
--build`, and the first visit runs the web installer.

```bash
docker compose down       # stop, keep the data
docker compose down -v    # stop, discard the data and start clean
```

To run a second copy alongside, say to try something without disturbing a
demo, give it another project name and port:

```bash
COMPOSE_PROJECT_NAME=tetrak-omeka-scratch OMEKA_PORT=8081 scripts/reset.sh
```

Each instance gets its own API key file, `.omeka-api.<project>.env` beside the
main one's `.omeka-api.env`, and the scripts pick the file for whichever
project `COMPOSE_PROJECT_NAME` names. So set the same variable for any command
run against that copy, and leave it unset to go back to the main one.

## What the stack is

Two services and two named volumes: Omeka S, and MariaDB, the MySQL-compatible
database Omeka's own documentation assumes.

Omeka has no official Docker image, and the community ones are abandoned,
amd64-only, or ignore environment configuration. So `omeka/Dockerfile` builds
one from the official release zip on `php:8.2-apache`, checking the zip against
a pinned SHA-256, with ImageMagick for thumbnails and PHP's upload limits raised to 64 MB, since
one page scanned at archival resolution exceeds the 2 MB default. `omeka/docker-entrypoint.sh`
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
- **The credentials in `.env.example` are not secrets.** The database
  and admin passwords are local scaffolding for a service on localhost, which
  is reset whenever a clean start is wanted. `.env` is gitignored so a real
  one can be kept without being committed, but this stack is not built to hold
  anything sensitive.

## How it uses Tetrak

The seeded collections are deliberately half transcribed: some pages carry a
verified reference transcript, the rest none. `scripts/transcribe.py` runs
Tetrak's CLI on every page without one and writes the result back into Omeka,
where the sites' reader shows it beside the page.
[The tutorial](tutorials/transcribe-with-tetrak.md) walks through it from a
clean start.

Tetrak is used as an installed package, pinned to a release of the public
repository, never as a sibling checkout of it: from PyPI, where the package
is `tetrak` (the command is `tetrak-ocr`), with the extras the demo uses:

```bash
pip install 'tetrak[armenian,qa,vision]==5.14.1'
```

Pinning a tag rather than a checkout keeps this demo working for anyone who
clones it on its own, and makes it an honest test of Tetrak as other people get
it.

## Licence

MIT; see [LICENSE](LICENSE). Omeka S itself is GPL-3.0 and is not
redistributed here: `omeka/Dockerfile` downloads the official release when the
image is built. Collection material carries its own rights, recorded beside it.
