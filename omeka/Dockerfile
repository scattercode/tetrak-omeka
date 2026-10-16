# Omeka S, built here rather than pulled.
#
# The Omeka project publishes no official image, and the community ones are
# either abandoned, amd64-only, or ignore environment configuration. Building
# from the official release zip on the official PHP image keeps this stable,
# multi-arch, and dependent on nobody else's registry.
#
# The release zip is pinned by version and checksum. To move to a new release,
# change both build args together; the build fails if they disagree.

FROM php:8.2-apache

# Fail a RUN whose pipeline fails anywhere, not only at its last command: the
# checksum check below is a pipe.
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG OMEKA_VERSION=4.1.1
ARG OMEKA_SHA256=b53c9eeb5e8479c6991de3c47197abac59be577884e7224f92f87758f2f14f7f

# pdo_mysql, mbstring, xml and fileinfo are what Omeka's composer.json requires;
# mbstring, xml and fileinfo already ship with the PHP image. ImageMagick is the
# thumbnailer Omeka finds on its own; without one, uploads get no derivatives.
# poppler-utils is for pdftotext, which Extract Text uses to read a PDF's text
# layer (below).
# The upgrade applies Debian's security fixes, which the official PHP image
# often lags: without it Trivy found 48 HIGH vulnerabilities with fixes
# available, all in the base packages. Omeka and PHP stay pinned; only the
# operating system's patches float.
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends imagemagick poppler-utils unzip \
    && docker-php-ext-install pdo_mysql \
    && a2enmod rewrite \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL -o /tmp/omeka.zip \
        "https://github.com/omeka/omeka-s/releases/download/v${OMEKA_VERSION}/omeka-s-${OMEKA_VERSION}.zip" \
    && echo "${OMEKA_SHA256}  /tmp/omeka.zip" | sha256sum -c - \
    && unzip -q /tmp/omeka.zip -d /tmp \
    && rm -rf /var/www/html \
    && mv /tmp/omeka-s /var/www/html \
    && rm /tmp/omeka.zip \
    && chown -R www-data:www-data /var/www/html/files

# Omeka ships a .htaccess that routes everything through index.php; Apache
# ignores it unless overrides are allowed.
RUN sed -i '/<Directory \/var\/www\/>/,/<\/Directory>/ s/AllowOverride None/AllowOverride All/' \
        /etc/apache2/apache2.conf \
    && echo 'ServerName localhost' > /etc/apache2/conf-available/servername.conf \
    && a2enconf servername

# Octopus Viewer, the page viewer the sites use: each page's image beside its
# metadata, transcript included. Pinned like Omeka, by version and checksum;
# omeka/setup.php installs it in Omeka once Omeka itself is installed.
ARG OCTOPUSVIEWER_VERSION=0.10.4
ARG OCTOPUSVIEWER_SHA256=faecc5b37c36f1867c3ab29de3a875c6e2692841a6c32eee6d0e818e8776fb14
RUN curl -fsSL -o /tmp/octopusviewer.zip \
        "https://github.com/biblibre/omeka-s-module-OctopusViewer/releases/download/v${OCTOPUSVIEWER_VERSION}/OctopusViewer-${OCTOPUSVIEWER_VERSION}.zip" \
    && echo "${OCTOPUSVIEWER_SHA256}  /tmp/octopusviewer.zip" | sha256sum -c - \
    && unzip -q /tmp/octopusviewer.zip -d /var/www/html/modules \
    && rm /tmp/octopusviewer.zip

# Extract Text, Omeka's own module for making files searchable: on upload it
# reads a PDF's text layer with pdftotext into the media, and gathers it onto
# the item, where Omeka's search finds it. This is how a searchable PDF from
# Tetrak is indexed with no integration written for it. Pinned the same way.
ARG EXTRACTTEXT_VERSION=2.1.0
ARG EXTRACTTEXT_SHA256=a1d1b09f0c2d69be5dedcb0a3b4eda5b3de243421a5334ff98f88d6667f552bf
RUN curl -fsSL -o /tmp/extracttext.zip \
        "https://github.com/omeka-s-modules/ExtractText/releases/download/v${EXTRACTTEXT_VERSION}/ExtractText-${EXTRACTTEXT_VERSION}.zip" \
    && echo "${EXTRACTTEXT_SHA256}  /tmp/extracttext.zip" | sha256sum -c - \
    && unzip -q /tmp/extracttext.zip -d /var/www/html/modules \
    && rm /tmp/extracttext.zip

# CSV Import, Omeka's own module for loading a spreadsheet: here, Tetrak's
# batch manifest, matched to the media it describes by their file name in
# dcterms:identifier, puts every transcript in Omeka without a script
# (tutorials/import-a-manifest.md). Pinned the same way.
ARG CSVIMPORT_VERSION=2.6.2
ARG CSVIMPORT_SHA256=726b371bb5d00dd3fed0f87a8f54ee70f38fee37a7765f485830e310729340a5
RUN curl -fsSL -o /tmp/csvimport.zip \
        "https://github.com/omeka-s-modules/CSVImport/releases/download/v${CSVIMPORT_VERSION}/CSVImport-${CSVIMPORT_VERSION}.zip" \
    && echo "${CSVIMPORT_SHA256}  /tmp/csvimport.zip" | sha256sum -c - \
    && unzip -q /tmp/csvimport.zip -d /var/www/html/modules \
    && rm /tmp/csvimport.zip

# The sites' theme: the default theme with the viewer on its item pages.
COPY build-theme.sh theme/ /tmp/tetrak-reader/
RUN sh /tmp/tetrak-reader/build-theme.sh /tmp/tetrak-reader \
    && rm -rf /tmp/tetrak-reader

COPY uploads.ini /usr/local/etc/php/conf.d/uploads.ini

# Installs Omeka and issues an API key from the command line, for
# scripts/install.sh. Outside the web root, so Apache never serves it.
COPY setup.php /opt/tetrak-omeka/setup.php

COPY docker-entrypoint.sh /usr/local/bin/omeka-entrypoint
RUN chmod +x /usr/local/bin/omeka-entrypoint

ENTRYPOINT ["omeka-entrypoint"]
CMD ["apache2-foreground"]
