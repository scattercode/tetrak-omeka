#!/bin/sh
# Throw the Omeka instance away and bring up a clean, seeded one.
#
# The starting point for every demo and tutorial: removes the containers and
# both volumes (the database and the uploaded files), rebuilds and starts the
# stack, installs Omeka with the admin from .env, and loads the collections
# under collections/. Takes a few minutes, most of it thumbnailing the scans.
#
# Prerequisites: Docker with Compose, Python 3.11 or later, and a .env (copied
# from .env.example if there is none).
#
# Usage:
#   scripts/reset.sh            # asks before deleting anything
#   scripts/reset.sh --yes      # does not ask
#   scripts/reset.sh --no-seed  # clean and installed, but empty
set -eu

cd "$(dirname "$0")/.."

confirm=yes
seed=yes
for arg in "$@"; do
    case "$arg" in
        --yes) confirm=no ;;
        --no-seed) seed=no ;;
        *) echo "usage: scripts/reset.sh [--yes] [--no-seed]" >&2; exit 2 ;;
    esac
done

if [ ! -f .env ]; then
    cp .env.example .env
    echo "No .env, so copied .env.example"
fi

project=$(docker compose config --format json | python3 -c 'import json, sys; print(json.load(sys.stdin)["name"])')

if [ "$confirm" = yes ]; then
    printf 'This deletes everything in the Omeka instance "%s". Continue? [y/N] ' "$project"
    read -r answer
    case "$answer" in
        y | Y | yes) ;;
        *) echo "Nothing deleted"; exit 1 ;;
    esac
fi

docker compose down -v
docker compose up -d --build --wait
scripts/install.sh

if [ "$seed" = yes ]; then
    python3 scripts/seed.py
fi

# Values for the closing message. The environment wins over .env, as it does
# for Compose; .env is plain KEY=value lines.
admin_email=${OMEKA_ADMIN_EMAIL:-$(sed -n 's/^OMEKA_ADMIN_EMAIL=//p' .env)}
url=$(sed -n 's/^OMEKA_URL=//p' .omeka-api.env)

echo
echo "Omeka is ready at ${url}/admin"
echo "Log in as ${admin_email:-the admin in .env}, with the password in .env"
