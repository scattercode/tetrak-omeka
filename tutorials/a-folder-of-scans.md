# Make a folder of scans searchable, with no server

The other guides put Tetrak's transcripts into Omeka. This one needs no Omeka,
no Docker and no server of any kind: a folder of scans on a laptop, one
Tetrak command, and the laptop's own file search. For a lone researcher or a
small archive with no collections system, this is the whole job.

At the end, a word printed on a scan, and nowhere else, is found by the
operating system's search. One scan in the folder is ruined on purpose, and
Tetrak puts it aside for a person to look at rather than passing off a bad
reading as done.

It takes about ten minutes once Tetrak is installed, most of it reading.

## Before you start

You need Tetrak, installed as in
[step 2 of the first guide](transcribe-with-tetrak.md#2-install-tetrak), with
its `qa` extra: that is what scores each transcript. Omeka is not needed, so
skip step 1.

The guide uses a Mac and Spotlight. [On Linux](#on-linux) says what changes.

## 1. Make the folder

Tetrak's batch mode works on a folder called `workspace`: it reads every
scan in `workspace/scans/`, and moves each one out as it finishes. So we
copy the scans rather than pointing it at this repository.

From the root of this repository:

```bash
mkdir -p ~/tetrak-folder/workspace/scans
cp collections/los-angeles-ephemera/*.jpg collections/los-angeles-ephemera/*.png \
   folder/inside-facts-1930-cover-ruined.jpg ~/tetrak-folder/workspace/scans/
```

That is the Los Angeles collection's five scans, and a sixth: the front page
of *Inside Facts*, again, shrunk, blurred and speckled until it is unreadable.
[`folder/SOURCES.md`](../folder/SOURCES.md) says how it was made.

## 2. Run Tetrak on it

```bash
cd ~/tetrak-folder
tetrak-ocr batch --backend auto-local --format markdown,pdf
```

`auto-local` reads each page with every local engine, scores what each
produced, and keeps the best. `--format markdown,pdf` asks for two things per
scan: a text sidecar, and a searchable PDF, the scan with the transcript laid
over it as an invisible text layer. It prints a table of scores for each page
as it goes, and ends:

```text
Triaged (1): inside-facts-1930-cover-ruined.jpg
Done. 5 file(s) processed, 1 sent to triage.
```

About half a minute on an M-series Mac.

## 3. Look in the folder

```bash
find workspace -type f | sort
```

```text
workspace/processed/graumans-chinese-theatre.jpg
workspace/processed/graumans-chinese-theatre.md
workspace/processed/graumans-chinese-theatre.pdf
workspace/processed/hollywood-boulevard-east.jpg
workspace/processed/hollywood-boulevard-east.md
workspace/processed/hollywood-boulevard-east.pdf
workspace/processed/hollywood-music-box-playbill-1926.md
workspace/processed/hollywood-music-box-playbill-1926.pdf
workspace/processed/hollywood-music-box-playbill-1926.png
workspace/processed/inside-facts-1930-cover.jpg
workspace/processed/inside-facts-1930-cover.md
workspace/processed/inside-facts-1930-cover.pdf
workspace/processed/kar-mi-troupe-poster.jpg
workspace/processed/kar-mi-troupe-poster.md
workspace/processed/kar-mi-troupe-poster.pdf
workspace/telemetry.jsonl
workspace/triage/inside-facts-1930-cover-ruined.jpg
workspace/triage/inside-facts-1930-cover-ruined.md
```

- **`processed/`** holds each scan with its transcript (`.md`) and its
  searchable PDF. The scan itself is untouched; the PDF holds a smaller
  access copy of it.
- **`triage/`** holds the ruined scan, and no PDF of it. Its `.md` is not a
  transcript but a report: what each engine scored, and what each read.

  ```text
  | Backend | Score |
  |---|---|
  | vision | 0.0724 |
  | easyocr | 0.0000 |
  | tesseract-auto | 0.0000 |
  ```

  The best of them read the masthead, `ISIDE FACTS`, and little else.
  Anything scoring under 0.10 comes here, so a page Tetrak could not read
  waits for a person instead of sitting in `processed/` looking finished.
  What to do with it is a person's call: find a better copy, rescan it, or
  try an engine that reads more, such as `--backend claude`.
- **`telemetry.jsonl`** is the run's log, a line for each step of each
  file, to `tail` while a long batch runs.

## 4. Search for a word on a page

The playbill's performance times are printed on the sheet and nowhere in a
file name. Press ⌘-Space and type **Matinees**, or in a Finder window press
⌘-F and choose *Contents*. Or from the terminal:

```bash
mdfind -onlyin ~/tetrak-folder Matinees
```

```text
/Users/you/tetrak-folder/workspace/processed/hollywood-music-box-playbill-1926.md
/Users/you/tetrak-folder/workspace/processed/hollywood-music-box-playbill-1926.pdf
```

Spotlight found the word inside the PDF and the sidecar, and opening the PDF
shows the scan. Nothing was installed for this but Tetrak: Spotlight reads a
PDF's text layer as it reads any document's. Spotlight takes a few seconds to
index new files, so a search straight after the run may come back empty;
try again.

The same PDFs can go anywhere else that indexes PDFs: a shared drive, a
document management system, or a collections system, as
[the searchable-PDF guide](searchable-pdf-drop-in.md) shows with Omeka.

## What is not here yet

The plan for this scene also has a CSV manifest: one row per scan, with its
file name, transcript, the engine that read it and whether it passed the
quality gate, to open in a spreadsheet or import into a collections system.
Tetrak does not write one yet. It is being added to Tetrak, and this guide
will use it when it is.

## On Linux

Leave out the `vision` extra, as in the first guide; `auto-local` then
chooses between EasyOCR and Tesseract. The ruined scan still goes to triage.

For the search, GNOME's file search (Tracker) indexes PDF text in the home
folder the same way. From a terminal, `grep -rl Matinees ~/tetrak-folder`
finds the sidecar without any index.

## Start again

```bash
rm -rf ~/tetrak-folder
```
