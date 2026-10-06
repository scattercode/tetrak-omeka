#!/bin/sh
# Build the "tetrak-reader" theme: Omeka's default theme with Octopus Viewer
# on the item page, where the default theme puts its plain media embeds, and
# dressed in tetrak.dev's design: its palette, and its fonts, self-hosted.
#
# Run once, at image build time, by omeka/Dockerfile. Copying the bundled
# theme rather than keeping a copy here means it follows the pinned Omeka
# release, and every edit below fails the build if the default theme ever
# changes underneath it.
#
# Usage (inside the image build only):
#   build-theme.sh <directory holding reader.css, reader.js,
#                   octopusviewer-viewer-extra.css, fonts/ and view/>
set -eu

source_dir=$1
themes=/var/www/html/themes
theme=$themes/tetrak-reader

cp -r "$themes/default" "$theme"
ini=$theme/config/theme.ini
layout=$theme/view/layout/layout.phtml

# Replace a line of a file, failing if it is not there exactly once; an empty
# replacement deletes the line.
replace() {
    [ "$(grep -cxF "$2" "$1")" -eq 1 ] || { echo "$1: '$2' not found once" >&2; exit 1; }
    awk -v old="$2" -v new="$3" '$0 == old { if (new != "") print new; next } { print }' \
        "$1" > "$1.new" && mv "$1.new" "$1"
}

replace "$ini" 'name = "Default"' 'name = "Tetrak reader"'
# Omeka puts the theme's version on its asset URLs (?v=...) so browsers fetch
# a stylesheet or script again when it changes. Ours change without the
# default theme's version moving, so stamp the version with a hash of them:
# otherwise a browser keeps the old ones until someone thinks to hard-refresh.
default_version=$(sed -n 's/^version = "\(.*\)"$/\1/p' "$ini")
asset_hash=$(cat "$source_dir/reader.css" "$source_dir/octopusviewer-viewer-extra.css" "$source_dir/reader.js" | sha256sum | cut -c1-8)
replace "$ini" "version = \"$default_version\"" "version = \"$default_version-$asset_hash\""
replace "$ini" ';description = ""' 'description = "Omeka'"'"'s default theme, with Octopus Viewer showing each page beside its transcript"'
# The viewer replaces both the embeds above the metadata and the media list
# below it: it is a media list in its own right.
replace "$ini" 'resource_page_blocks.items.main[] = "mediaEmbeds"' 'resource_page_blocks.items.main[] = "octopusViewer"'
replace "$ini" 'resource_page_blocks.items.main[] = "mediaList"' ''

# The theme settings' defaults: links in Tetrak's clay rather than Omeka's
# red, and a footer that says what this is. Omeka applies these only once
# someone saves a site's theme settings in the admin interface, and the
# seeder's sites have none saved, so the layout's own fallback footer is
# replaced below as well, and reader.css sets the link colour.
replace "$ini" 'elements.accent_color.attributes.value = "#920b0b"' 'elements.accent_color.attributes.value = "#8a6a33"'
replace "$ini" 'elements.footer.attributes.value = "Powered by Omeka S"' \
    'elements.footer.attributes.value = "A demonstration of <a href='"'"'https://tetrak.dev/'"'"'>Tetrak</a> with <a href='"'"'https://omeka.org/s/'"'"'>Omeka S</a>"'
# The default theme loads Open Sans from Google's CDN. The fonts here are
# self-hosted, so the demo makes no request off the machine and works offline.
replace "$layout" "\$this->headLink()->prependStylesheet('//fonts.googleapis.com/css?family=Open+Sans:400,400italic,600,600italic,700italic,700');" ''
cp -r "$source_dir/fonts" "$theme/asset/"
replace "$layout" "                <?php echo \$this->translate('Powered by Omeka S'); ?>" \
    '                A demonstration of <a href="https://tetrak.dev/">Tetrak</a> with <a href="https://omeka.org/s/">Omeka S</a>'

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
