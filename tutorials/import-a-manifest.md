# Import a folder's transcripts into Omeka from a spreadsheet

[The folder guide](a-folder-of-scans.md) ends with a CSV manifest: a row for
every scan, with its transcript, the engine that read it, and whether it
passed the quality gate. This guide loads that file into Omeka with
[CSV Import](https://omeka.org/s/modules/CSVImport/), Omeka's own module for
spreadsheets, from its admin screens. No script, no API key: the same few
screens a cataloguer uses to load any spreadsheet.

At the end, every page in the Los Angeles collection has a Tetrak transcript
beside it in the reader, the site's search finds words that are only on the
page, and the ruined scan, which Tetrak would not vouch for, has been left out.

It takes about fifteen minutes, most of it the batch run.

## Before you start

You need:

- **A clean Omeka**, from
  [step 1 of the first guide](transcribe-with-tetrak.md#1-start-from-a-clean-omeka).
  The image this repository builds has CSV Import in it already. Start from
  a reset even if Omeka is running: the import finds each page by its file
  name, which the seed records only from this version on.
- **The folder from [the folder guide](a-folder-of-scans.md)**, run with
  `--manifest`, so that `~/tetrak-folder/workspace/manifest.csv` exists. If
  you ran that guide before it had `--manifest`, run its steps 1 and 2 again
  after `rm -rf ~/tetrak-folder`.

## 1. How a row finds its page

CSV Import updates something already in Omeka by matching one column of the
sheet to one of its fields. The manifest's `file` column is the scan's file
name, `kar-mi-troupe-poster.jpg`. Open the poster's page in the admin
interface and its media, the scan, has that same name as its *Identifier*.
That is the whole link between the two: a file name that both sides agree on.

Archives often keep the scan's file name on the record already. Where yours
does not, add it as the media's Identifier before importing, or CSV Import
has nothing to match on.

## 2. Load the file

In the admin interface, <http://127.0.0.1:8080/admin>, logged in with the
`OMEKA_ADMIN_EMAIL` and `OMEKA_ADMIN_PASSWORD` from `.env`, choose
**CSV Import** in the left-hand menu.

- **Spreadsheet**: `~/tetrak-folder/workspace/manifest.csv`. On a Mac, press
  ⌘-Shift-G in the file chooser and paste the path.
- **Import type**: *Media*, because the transcripts belong to the pages, not
  to the items that hold them.
- Leave the delimiter as *comma* and the enclosure as *double quote*.

Press **Next**. CSV Import lists the manifest's thirteen columns.

## 3. Map three columns

For each of these, press the **+** (*Add mapping*) beside the column's name,
open **Properties** in the panel that appears, type the property's name in
the filter box, choose it, and press **Apply changes**:

| Column | Property | Why |
|---|---|---|
| `file` | Dublin Core *Identifier* | How each row finds its page |
| `transcript` | Tetrak *Tetrak transcript* | What Tetrak read |
| `engine` | Tetrak *Transcribed with* | Which engine read it |

Leave the other ten unmapped: the quality score, file paths and run id are
for the person running the batch, not for the catalogue. A transcript with
commas in it stays one value, since a column is split on the multivalue
separator only if you configure it to be.

## 4. Tell it to update, not create

Open **Advanced Settings**:

- **Action**: *Revise*. It replaces the mapped fields of an existing page,
  except where the cell is empty, and leaves every other field alone: the
  page's title, and its reference transcript where it has one. A triaged
  row's transcript is empty on purpose, so Revise never writes a reading the
  quality gate rejected over anything.
- **Resource identifier column**: `file`.
- **Resource identifier property**: *Identifier*, under Dublin Core.
- **Action on unidentified resources**: *Skip the row*. A row with no
  matching page is skipped rather than made into a new media with no file.

Never choose *Create* here: it would add a second, empty media for every
row.

Press **Import**.

## 5. Read the result

CSV Import runs in the background and lists the run under **Past Imports**.
Choose the latest, then its job, and the log ends:

```text
The following identifiers are not associated with a resource and were skipped: "inside-facts-1930-cover-ruined.jpg".
5 media were updated (revise): "graumans-chinese-theatre.jpg" (9), "hollywood-boulevard-east.jpg" (7), "hollywood-music-box-playbill-1926.png" (11), "inside-facts-1930-cover.jpg" (3), "kar-mi-troupe-poster.jpg" (5).
```

The numbers in brackets are Omeka's ids, and may differ on yours. The ruined
scan was skipped twice over: it is not in Omeka, and its row had no
transcript to give. In a real collection, it would be the one page left to
look at.

## 6. See it on the site

Open the Los Angeles site at <http://127.0.0.1:8080/s/los-angeles> and
search for **Matinees**. The playbill comes back, found by a word that is
only on the sheet. Open it: the reader shows Tetrak's transcript beside the
page, headed *Read by Tetrak · not checked*, with `vision`, the engine, as
where it came from. Every other page in the
collection has its transcript too, beside the reference transcript where
there is one, for comparison.

## What this shows, and what it does not

- **The manifest is the integration.** Nothing in CSV Import knows about
  Tetrak, as nothing in Extract Text did in
  [the searchable-PDF guide](searchable-pdf-drop-in.md). Any system that
  imports a spreadsheet and can match on a file name can take Tetrak's
  output this way.
- **It fills in transcripts; it does not catalogue.** The items, their
  descriptions and their scans were in Omeka first. To create new items from
  a folder of scans, CSV Import can do that too, but it needs the scans at a
  URL or on the server through a module such as File Sideload, and the
  descriptions a person writes.
- **Running it again is safe.** The manifest grows with every batch, so the
  same file can appear twice: once triaged, and again after a rescan. Rows
  are imported in order, so the later reading wins, and Revise never lets an
  empty transcript clear one already there. Import the whole manifest each
  time.
- **The manifest is a beta in Tetrak.** If its columns change, the mapping in
  step 3 changes with them; CSV Import matches by the column names you
  choose, so nothing breaks silently.
- **A spreadsheet edited in Excel still imports.** Saved as *CSV UTF-8*,
  Excel adds a byte-order mark to the start of the file; CSV Import removes
  it.

## From a script

[The first guide's](transcribe-with-tetrak.md) `scripts/transcribe.py` does
the same job through the API, page by page, with scores against the
reference. This guide is for the person who would rather not run a script
against the collections system, or whose system has an importer and no API.

## Start again

```bash
scripts/reset.sh
```

and, for the folder:

```bash
rm -rf ~/tetrak-folder
```
