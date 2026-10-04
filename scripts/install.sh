#!/bin/sh
# Install Omeka without the web form, and issue an API key for the scripts.
#
# Runs omeka/setup.php inside the container: the installer (a no-op if Omeka
# is already installed), then the modules the sites need, then a fresh API key
# for OMEKA_ADMIN_EMAIL. The key goes to .omeka-api.env, which scripts/seed.py,
# scripts/transcribe.py and the tutorials read -- or, for an instance run under
# another COMPOSE_PROJECT_NAME, to .omeka-api.<project>.env, so a second copy
# never takes over the first one's key. Every run replaces the key, because
# Omeka cannot show an old one again.
#
# Prerequisites: Docker with Compose, and a .env with the OMEKA_ADMIN_*
# variables (see .env.example). Starts the stack if it is not running.
#
# Usage:
#   scripts/install.sh
set -eu

cd "$(dirname "$0")/.."

docker compose up -d --wait

setup() {
    docker compose exec -T -u www-data omeka php /opt/tetrak-omeka/setup.php "$@"
}

setup install
setup modules
key=$(setup api-key)

# "127.0.0.1:8080", or wherever OMEKA_PORT put it.
address=$(docker compose port omeka 80)

project=$(docker compose config --format json | python3 -c 'import json, sys; print(json.load(sys.stdin)["name"])')
key_file=.omeka-api.env
if [ "$project" != "$(sed -n 's/^name: *//p' compose.yaml)" ]; then
    key_file=".omeka-api.$project.env"
fi

umask 077
cat > "$key_file" <<EOF
# Written by scripts/install.sh; reissued on every install. Not committed.
OMEKA_URL=http://${address}
OMEKA_KEY_IDENTITY=${key% *}
OMEKA_KEY_CREDENTIAL=${key#* }
EOF

echo "API key written to $key_file"
