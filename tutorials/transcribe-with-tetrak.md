# Transcribe an Omeka collection with Tetrak

Omeka holds the images; Tetrak reads them. In this guide we start from a clean
Omeka with two collections in it, try Tetrak's command line on a couple of
pages by hand, then run one script that transcribes every untranscribed page
and writes the text back into Omeka, where the site's reader shows it beside
the image.

It takes about twenty minutes, most of it installing Tetrak. The transcription
itself takes a minute or two.

## What we start with

Two Omeka sites, each showing one collection. Some pages already have a
**reference transcript**: one checked by people, proofread on Wikisource or
verified by hand. Others have nothing yet. Those are the ones we transcribe.

| Site | Already transcribed | Not yet transcribed |
|---|---|---|
| Armenian printed books (`/s/armenian-books`) | Soviet Armenian Encyclopedia, 10 pages; Tumanyan, *Brave Nazar*, 11 pages | Tumanyan, *The Death of Kikos*, 4 pages; Popular medical encyclopedia, 2 pages |
| Los Angeles stage and screen (`/s/los-angeles`) | *Inside Facts* front page; the Kar-Mi Troupe poster; Hollywood Boulevard postcard | Grauman's Chinese Theatre postcard; Hollywood Music Box playbill, 1926 |

The pages without transcripts were chosen to be different from each other. A
single column of Armenian italic, three dense columns of Armenian type, a
picture postcard with a cut-off marquee, and a narrow playbill of small type.

## Before you start

You need:

- **Docker with Compose**, for Omeka.
- **Python 3.11 or later.**
- **Tesseract and poppler**, the system tools Tetrak builds on:

  ```bash
  brew install tesseract poppler                 # macOS
  sudo apt install tesseract-ocr poppler-utils   # Debian or Ubuntu
  ```

The guide assumes a Mac, because Tetrak's strongest local engine, Apple's
Vision framework, ships with macOS. Everything also works on Linux without it;
[Linux](#on-linux) says what changes.

## 1. Start from a clean Omeka

From the root of this repository:

```bash
cp .env.example .env      # first time only
scripts/reset.sh
```

`reset.sh` deletes whatever Omeka held, rebuilds it, installs it, and loads
both collections. It asks before deleting anything. When it finishes:

```text
Omeka is ready at http://127.0.0.1:8080/admin
Log in as admin@example.com, with the password in .env
```

Open <http://localhost:8080/s/armenian-books> and choose *Կիկոսի մահը* (*The
Death of Kikos*). The reader shows the pages down the left and the selected
page in the middle. The panel on the right shows only the page's title and
source: there is no transcript yet. Compare *Քաջ Նազարը* (*Brave Nazar*),
where every page has its reference transcript beside it.

`reset.sh` also wrote `.omeka-api.env`, the API key the transcription script
uses. It is reissued on every reset and never committed.

## 2. Install Tetrak

Tetrak is on PyPI as `tetrak`. It goes in a virtual environment of its own,
pinned to a release, with three extras:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install 'tetrak[armenian,qa,vision]==5.14.1'
```

The extras matter: a plain `pip install tetrak` installs Tetrak without the
Armenian recogniser or `auto-local`, and the demo needs both. They are:

| Extra | Gives us |
|---|---|
| `armenian` | `easyocr-hy`, Tetrak's own Armenian recogniser. Stock OCR engines cannot read Armenian at all |
| `qa` | `auto-local`, which runs every local engine on a page, scores what each produced, and keeps the best |
| `vision` | Apple's Vision framework as one of those engines. macOS only |

This pulls in PyTorch, so allow a few minutes.

Then check two things. First, that the `tetrak-ocr` the shell finds is the
one just installed, inside `.venv`. If an older Tetrak is installed elsewhere
on the machine, it can shadow this one, and it will not have these extras:

```bash
which tetrak-ocr
```

```text
/path/to/tetrak-omeka/.venv/bin/tetrak-ocr
```

Second, that the backends the demo uses are ticked: **`easyocr-hy`**,
**`auto-local`** and, on a Mac, **`vision`**:

```bash
tetrak-ocr backends
```

```text
 ✓ tesseract
 ✓ tesseract-auto
 · claude  (extra not installed)
 ✓ easyocr
 ✓ easyocr-hy
 · paddle  (extra not installed)
 · paddle-vl  (extra not installed)
 · marker  (extra not installed)
 ✓ vision
 ✓ auto-local
```

The dots are engines we have not installed and do not need. Two are worth
knowing about. `claude` sends images to Anthropic's API, which reads
decorative lettering no local engine can, at the cost of the images leaving
the machine. `marker` is the local engine that best follows reading order on
multi-column newsprint, but it is slow and wants a GPU.

## 3. Try the command line on one page

Before transcribing a whole collection, it helps to see what Tetrak does with
one page. The images in `collections/` are the same files Omeka holds, so we
can point Tetrak straight at them.

A postcard, with `auto-local`:

```bash
tetrak-ocr ocr collections/los-angeles-ephemera/graumans-chinese-theatre.jpg --backend auto-local
```

```text
    Backend         Quality  Words  Effective      Time
    --------------  -------  -----  ---------  --------
    vision           0.2356      8     0.2136      3.2s
    easyocr          0.1761     11     0.1667      3.0s
    tesseract-auto   0.1550     15     0.1550      0.3s
    [auto-local → vision]  effective=0.2136  quality=0.2356
THE CHINESE THEATRE. HOLLYWOOD. CALIFORNIA
62694 T-373
62694
```

The table is `auto-local` at work. It ran three engines, scored each
transcript for quality without needing to know the right answer, and kept
Vision's. The score is a confidence measure, not a percentage correct; Tetrak
treats anything under 0.10 as too poor to trust. The transcript follows the
table.

It has the printed caption and the card number, including the handwritten
one. It has missed the marquee at the right-hand edge, which the frame cuts
off mid-word: *SYLVIA SI…*, for Sylvia Sidney in *You Only Live Once*. That
is worth pointing out. OCR transcribes what it can see clearly, and small,
cropped, angled lettering in a photograph is where it gives up first.

An Armenian page, with the Armenian recogniser:

```bash
tetrak-ocr ocr collections/armenian-books/tumanyan-death-of-kikos/images/252.jpg --backend easyocr-hy
```

```text
1913
ԿԻԿՈՍԻ ՄԱՀԸ
Մի աղքատ մարդ ու կնիկ են լինում, ունենում են երեք
աղջիկ։
Մի օր հերը աշխատելիս է լինում, ծարավում է, մեծ աղջըկանը ջուրն է ղրկում։ ...
```

The first run of each engine downloads its model weights, a few hundred
megabytes in all, so it is slow; later runs reuse them. On an Apple-silicon
Mac, each of these pages then takes under ten seconds. PyTorch may print a
warning about `pin_memory` on Apple's GPU; it is harmless.

A few other things `tetrak-ocr` can do, none of which the demo needs:

```bash
tetrak-ocr ocr page.jpg --backend vision --output page.txt   # to a file, not the screen
tetrak-ocr ocr page.jpg --backend auto-local --pdf           # a searchable PDF beside it
tetrak-ocr batch --backend auto-local                        # a whole folder: see Tetrak's README
```

## 4. Transcribe the untranscribed pages

`scripts/transcribe.py` does for each page what we just did by hand, then
saves the result into Omeka. With the virtual environment still active, first
see what it would do:

```bash
python3 scripts/transcribe.py --dry-run
```

```text
Կիկոսի մահը / Page 246 (252.jpg): easyocr-hy
Կիկոսի մահը / Page 247 (253.jpg): easyocr-hy
Կիկոսի մահը / Page 248 (254.jpg): easyocr-hy
Կիկոսի մահը / Page 249 (255.jpg): easyocr-hy
Հանրամատչելի բժշկական հանրագիտարան / Page 512 (512.jpg): easyocr-hy
Հանրամատչելի բժշկական հանրագիտարան / Page 514 (514.jpg): easyocr-hy
The Chinese Theatre, Hollywood, California / Front of the card (graumans-chinese-theatre.jpg): auto-local
Hollywood Music Box playbill: Ken-Geki, the Imperial Theatre company of Tokio / Playbill (hollywood-music-box-playbill-1926.png): auto-local
8 page(s) would be transcribed.
```

It has found the eight pages with no transcript, and chosen an engine for
each from the item's language: the Armenian recogniser for Armenian,
`auto-local` for everything else. Then run it:

```bash
python3 scripts/transcribe.py
```

```text
Using /path/to/tetrak-omeka/.venv/bin/tetrak-ocr (Tetrak 5.14.1)
Կիկոսի մահը / Page 246: easyocr-hy ... 799 characters, via easyocr-hy
Կիկոսի մահը / Page 247: easyocr-hy ... 809 characters, via easyocr-hy
Կիկոսի մահը / Page 248: easyocr-hy ... 983 characters, via easyocr-hy
Կիկոսի մահը / Page 249: easyocr-hy ... 710 characters, via easyocr-hy
Հանրամատչելի բժշկական հանրագիտարան / Page 512: easyocr-hy ... 6008 characters, via easyocr-hy
Հանրամատչելի բժշկական հանրագիտարան / Page 514: easyocr-hy ... 6023 characters, via easyocr-hy
The Chinese Theatre, Hollywood, California / Front of the card: auto-local ... 60 characters, via auto-local → vision, quality 0.24
Hollywood Music Box playbill: Ken-Geki, the Imperial Theatre company of Tokio / Playbill: auto-local ... 3012 characters, via auto-local → vision, quality 0.16
Done: 8 page(s) transcribed, 0 failed.
```

About a minute and a half on an Apple-silicon Mac. Run it again and it finds
nothing to do, because every page now has a transcript.

Before transcribing anything, the script checks that the `tetrak-ocr` it
found can run the engines it is about to use. If not, it stops and says what
to install, rather than failing page by page:

```text
transcribe.py: this tetrak-ocr cannot run auto-local, easyocr-hy.
Install the extras into the environment it belongs to:
    pip install 'tetrak[armenian,qa,vision]==5.14.1'
and check that `which tetrak-ocr` points into that environment.
```

## 5. See the transcripts in Omeka

Reload *The Death of Kikos*. Each page now has two new fields in the panel
beside it:

- **Tetrak transcript**: what Tetrak read.
- **Transcribed with**: the Tetrak release, the engine, the quality score
  where there is one, and the date, such as *Tetrak 5.14.1, auto-local →
  vision, quality 0.24, 2026-10-04*. A transcript without its provenance is
  hard to trust or to redo.

Things worth showing:

- **The medical encyclopedia** is three columns of small type. The recogniser
  reads each column to its foot before starting the next, so the text comes
  out in reading order rather than as lines stitched across the page. These
  two pages are also held out from the recogniser's training: it has never
  seen them, so this is a fair test of it.
- **The playbill** gets the headings and the programme right, and shows
  where OCR breaks down: the small-print fire notice and the plot summary
  come out garbled, and the cast lists lose which actor plays which part.
- **The Grauman's postcard** has the caption and not the marquee, as above.

None of these transcripts has been checked by a person, and the label says
so. The reference transcripts on the other pages are the standard Tetrak's
work would have to be corrected to.

## 6. Compare Tetrak with a reference

The pages that already have a reference transcript make the comparison easy.
Ask the script to transcribe one of those too:

```bash
python3 scripts/transcribe.py --item kar-mi-troupe-poster --include-reference
```

```text
The great Victorina Troupe, originators and presenters of the most marvelous sword swallowing act on earth / Poster: auto-local ... 259 characters, via auto-local → vision, quality 0.22
```

Open the Kar-Mi Troupe poster on the Los Angeles site. The panel now shows
the reference transcript and Tetrak's one in the same panel. The poster's
reference runs to over 1,200 characters; Tetrak recovered 259. It reads the
big headlines, loses the small captions under the illustrations, and reads
the Kodak colour bar photographed beside the poster as text.
That is a fair picture of where OCR stands on decorative ephemera, and why
the triage and the reference matter.

The options, together:

| Option | Does |
|---|---|
| `--item IDENTIFIER` | Only this item (identifiers are in each collection's `collection.toml`) |
| `--collection IDENTIFIER` | Only this collection: `armenian-books` or `los-angeles-ephemera` |
| `--include-reference` | Also pages that have a reference transcript |
| `--redo` | Replace Tetrak transcripts from an earlier run |
| `--backend NAME` | One engine for every page, e.g. `vision` or `tesseract-auto` |
| `--dry-run` | List the pages and engines, change nothing |

## How the script works

For each page, `scripts/transcribe.py`:

1. **Downloads the original file** from Omeka, the file as it was uploaded,
   not a resized derivative.
2. **Runs `tetrak-ocr ocr`** on it, exactly as in step 3, and reads the
   chosen engine and score from what `auto-local` prints.
3. **Writes the transcript back** through Omeka's REST API, to two properties
   from the demo's own vocabulary: `tetrak:transcript` and
   `tetrak:transcribedWith`.

The write-back has one catch worth knowing if you build on this. Omeka
treats an update that carries any metadata as the complete set of values, so
sending only the transcript would delete the page's title and source. The
script therefore fetches the page's full record, changes the two properties,
and sends the whole record back.

Tetrak's transcript goes in its own property, never over the reference
transcript, so the two can always be compared. The reader shows whatever
properties a page has, so nothing about the sites needed changing for the
transcripts to appear.

One difference from Tetrak's own batch mode: `tetrak-ocr batch` moves any
page scoring below 0.10 to a triage folder instead of treating it as read.
The single-page command the script uses has no triage, so the script records
the score in *Transcribed with* and warns about any page under the floor.

## Start again

To put everything back as it was before the demo:

```bash
scripts/reset.sh --yes
```

The virtual environment survives a reset, so the next run starts at step 4.

## On Linux

Leave out the `vision` extra, which is macOS only:

```bash
pip install 'tetrak[armenian,qa]==5.14.1'
```

`auto-local` then chooses between EasyOCR and Tesseract instead of Vision,
which reads these postcards and the playbill noticeably less well. The
Armenian pages are unaffected: they never use `auto-local`.

## If something goes wrong

| Message | What to do |
|---|---|
| `tetrak-ocr not found` | Activate the virtual environment: `source .venv/bin/activate` |
| `this tetrak-ocr cannot run …` | The `tetrak-ocr` in use lacks an extra. Check `which tetrak-ocr` points into `.venv`, then re-run the `pip install` from step 2 there |
| `No matching distribution found for tetrak-ocr[…]` | The package is `tetrak`, not `tetrak-ocr` (that is only the command's name). Tetrak releases before 5.14.1 print the wrong name in their install hints |
| `seed.py: OMEKA_URL is not set` | Omeka has not been installed with the scripts: run `scripts/reset.sh` |
| `cannot reach http://127.0.0.1:8080/api` | Omeka is not running: `docker compose up -d` |
| `Nothing to transcribe` | Every selected page has a transcript; add `--redo` to replace them |
