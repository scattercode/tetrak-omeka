#!/bin/sh
# Build the "tetrak-reader" theme: Omeka's default theme with Octopus Viewer
# on the item page, where the default theme puts its plain media embeds.
#
# Run once, at image build time, by omeka/Dockerfile. Copying the bundled
# theme rather than keeping a copy here means it follows the pinned Omeka
# release, and every edit below fails the build if the default theme ever
# changes underneath it.
#
# Usage (inside the image build only):
#   build-theme.sh <directory holding reader.css, reader.js, octopusviewer-viewer-extra.css and view/>
set -eu

source_dir=$1
themes=/var/www/html/themes
theme=$themes/tetrak-reader

cp -r "$themes/default" "$theme"
ini=$theme/config/theme.ini

# Replace a line of theme.ini, failing if it is not there exactly once.
replace() {
    [ "$(grep -cxF "$1" "$ini")" -eq 1 ] || { echo "theme.ini: '$1' not found once" >&2; exit 1; }
    awk -v old="$1" -v new="$2" '$0 == old { if (new != "") print new; next } { print }' \
        "$ini" > "$ini.new" && mv "$ini.new" "$ini"
}

replace 'name = "Default"' 'name = "Tetrak reader"'
# Omeka puts the theme's version on its asset URLs (?v=...) so browsers fetch
# a stylesheet or script again when it changes. Ours change without the
# default theme's version moving, so stamp the version with a hash of them:
# otherwise a browser keeps the old ones until someone thinks to hard-refresh.
default_version=$(sed -n 's/^version = "\(.*\)"$/\1/p' "$ini")
asset_hash=$(cat "$source_dir/reader.css" "$source_dir/octopusviewer-viewer-extra.css" "$source_dir/reader.js" | sha256sum | cut -c1-8)
replace "version = \"$default_version\"" "version = \"$default_version-$asset_hash\""
replace ';description = ""' 'description = "Omeka'"'"'s default theme, with Octopus Viewer showing each page beside its transcript"'
# The viewer replaces both the embeds above the metadata and the media list
# below it: it is a media list in its own right.
replace 'resource_page_blocks.items.main[] = "mediaEmbeds"' 'resource_page_blocks.items.main[] = "octopusViewer"'
replace 'resource_page_blocks.items.main[] = "mediaList"' ''

# Outside the viewer: the theme's own stylesheet, so append to it.
cat "$source_dir/reader.css" >> "$theme/asset/css/style.css"
# Likewise the theme's script, which every page loads.
cat "$source_dir/reader.js" >> "$theme/asset/js/default.js"
# Inside the viewer, which is a web component with its own styles: Octopus
# Viewer loads this file from the theme in place of its own empty one.
cp "$source_dir/octopusviewer-viewer-extra.css" "$theme/asset/css/"
# The viewer's right-hand panel. A theme's view/ comes before a module's when
# Omeka looks for a template, so this replaces the module's own.
cp -r "$source_dir/view" "$theme/"
