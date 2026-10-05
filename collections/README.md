# Collections

The material `scripts/seed.py` loads into Omeka. Each directory is one Omeka
item set, shown on a site of its own:

| Directory | Item set | Items | Site |
|---|---|---|---|
| `los-angeles-ephemera/` | Los Angeles stage and screen ephemera | A trade paper's front page, a vaudeville poster, two postcards and a playbill: one image each | `/s/los-angeles` |
| `armenian-books/` | Armenian printed books | Ten encyclopedia pages, two complete Tumanyan tales, and two pages of a medical encyclopedia | `/s/armenian-books` |

Some items have reference transcripts and some deliberately do not, so a demo
can show both and then fill the gaps with Tetrak:

| Item | Reference transcript |
|---|---|
| `inside-facts-1930-cover`, `kar-mi-troupe-poster`, `hollywood-boulevard-east` | Yes |
| `graumans-chinese-theatre`, `hollywood-music-box-playbill-1926` | No |
| `ase-vol2`, `tumanyan-brave-nazar` | Yes |
| `tumanyan-death-of-kikos`, `medical-encyclopedia` | No |

Each directory holds the images, the reference transcripts there are, a
`collection.toml` describing them, and a `SOURCES.md` recording where each
image and transcript came from and on what terms. Material must be public
domain or openly licensed, with its source and rights recorded before it is
added.

## Loading them

```bash
scripts/reset.sh                          # a clean instance, seeded
python3 scripts/seed.py                   # into the running instance
python3 scripts/seed.py armenian-books    # one collection
```

Seeding is safe to repeat: anything already in Omeka, matched on its
identifier, is left alone, and only what is missing is added. Edits to a
manifest therefore reach Omeka only through a reset. The one exception: an
existing item is added to its collection's site if it is not on it already.

## The sites

Each site uses the `tetrak-reader` theme, built into the image by
`omeka/build-theme.sh`: Omeka's default theme with
[Octopus Viewer](https://github.com/biblibre/omeka-s-module-OctopusViewer) on
the item page. The viewer lists an item's pages on the left, shows the
selected page in the middle, and that page's metadata on the right, its
reference transcript included. Page through an item and the transcript
follows.

The viewer shows whatever properties a page has, so a transcript written
back to a page by a script appears beside it with nothing else to configure.

## The manifest format

```toml
[item_set]
identifier = "los-angeles-ephemera"   # stored as dcterms:identifier
class = "dctype:Collection"           # optional resource class

[item_set.metadata]
"dcterms:title" = "Los Angeles stage and screen ephemera"

[site]                                # optional: a site for this item set
slug = "los-angeles"                  # the site is at /s/<slug>
title = "Los Angeles stage and screen"
summary = "…"                         # shown in lists of sites
introduction = "<p>…</p>"             # home page HTML, above a preview of the items
theme = "tetrak-reader"               # optional; this is the default

[[items]]
identifier = "kar-mi-troupe-poster"   # unique across all collections
class = "bibo:Image"

[items.metadata]
"dcterms:title" = "The great Victorina Troupe …"
"dcterms:date" = "c. 1914"

[[items.media]]                       # one per file, in display order
file = "kar-mi-troupe-poster.jpg"     # relative to this directory
alt_text = "Red vaudeville poster …"  # optional

[items.media.metadata]                # optional, as for items
"dcterms:title" = "Poster"
"tetrak:referenceTranscript" = { text_file = "transcripts/kar-mi-troupe-poster.txt" }
```

Metadata keys are vocabulary terms that Omeka knows: Dublin Core
(`dcterms:`), DCMI Type (`dctype:`), BIBO (`bibo:`) and FOAF (`foaf:`) come
with every install. `vocabularies.toml` adds the demo's own, created before
any collection is loaded:

| Term | Label | Holds |
|---|---|---|
| `tetrak:referenceTranscript` | Reference transcript | A verified transcription of a page, to compare OCR with |
| `tetrak:transcript` | Tetrak transcript | What Tetrak read, written back by `scripts/transcribe.py`; never set by the seeder |
| `tetrak:transcribedWith` | Transcribed with | The Tetrak release, backend, quality score and date behind it |

A value can take any of these forms:

| Form | Becomes |
|---|---|
| `"text"` | A literal |
| `{ value = "text", lang = "hy" }` | A literal tagged with a language |
| `{ text_file = "transcripts/105.txt" }` | A literal read from a file, relative to this directory: for long text such as a transcript |
| `{ uri = "https://…", label = "text" }` | A link; the label is optional |
| `[ … ]` | Several values for the same property, in order |

The first `dcterms:title` is the one Omeka displays.
