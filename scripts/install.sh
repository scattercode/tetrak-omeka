#!/bin/sh
# Install Omeka without the web form, and issue an API key for the scripts.
#
# Runs omeka/setup.php inside the container: the installer (a no-op if Omeka
# is already installed), then the modules the sites need, then a fresh API key
# for OMEKA_ADMIN_EMAIL. The key goes to .omeka-api.env, which scripts/seed.py
# and the tutorials read. Every run replaces the key, because Omeka cannot
# show an old one again.
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

umask 077
cat > .omeka-api.env <<EOF
# Written by scripts/install.sh; reissued on every install. Not committed.
OMEKA_URL=http://${address}
OMEKA_KEY_IDENTITY=${key% *}
OMEKA_KEY_CREDENTIAL=${key#* }
EOF

echo "API key written to .omeka-api.env"
