# Make a page searchable with nothing but a PDF

[The first guide](transcribe-with-tetrak.md) runs a script that writes
Tetrak's transcripts into Omeka through its API. This one writes no code at
all. Tetrak turns a scan into a searchable PDF: the image, with the
transcript laid over it as an invisible text layer. We upload that PDF to
Omeka the way anyone uploads a file, and Omeka's own search finds the words
in it.

Nothing here knows about Tetrak. Omeka reads the text layer with
[Extract Text](https://omeka.org/s/modules/ExtractText/), Omeka's own module
for making files searchable, which runs `pdftotext` on every PDF it is given.
Any platform that indexes a PDF's text indexes Tetrak's the same way: the PDF
is the integration.

It takes about ten minutes once Tetrak is installed.

## Before you start

You need the clean Omeka and the Tetrak install from the first guide:
[step 1](transcribe-with-tetrak.md#1-start-from-a-clean-omeka) and
[step 2](transcribe-with-tetrak.md#2-install-tetrak). The image this repository
builds has Extract Text and `pdftotext` in it already, so there is nothing to
add to Omeka.

We use the Hollywood Music Box playbill of 1926, which has no transcript yet.

## 1. Search for a word that is only on the page

The playbill's description in Omeka names the company and its stars, but not
the performance times printed on the sheet. Open the Los Angeles site at
<http://127.0.0.1:8080/s/los-angeles>, type **Matinees** into the search box,
and press Enter. Nothing comes back: the word is in the image, and Omeka
cannot read images.

## 2. Make the searchable PDF

From the root of this repository, with the virtual environment active:

```bash
tetrak-ocr ocr collections/los-angeles-ephemera/hollywood-music-box-playbill-1926.png --pdf playbill.pdf
```

Tetrak prints the transcript, then:

```text
Wrote playbill.pdf
```

That is the default engine, Tesseract, which takes a few seconds. Add
`--backend auto-local` for a better reading of this sheet, at the cost of
twenty seconds or so; either finds the word we are after. `playbill.pdf` is
ignored by git.

The PDF is the scan with the text behind it. Open it and select some of the
small type: the selection is Tetrak's transcript, lined up with the print.

## 3. Upload it to Omeka

In the admin interface, <http://127.0.0.1:8080/admin>, logged in with the
admin from `.env`:

1. **Items**, then the **Hollywood Music Box playbill**, then **Edit**.
2. The **Media** tab, then **Upload** under *Add media*.
3. Choose `playbill.pdf`. Give it a title, such as *Searchable PDF*, so the
   reader does not list it as *[Untitled]*.
4. **Save**.

As the file goes in, Extract Text reads its text layer into the new media as
**Extracted text**, and gathers it onto the item, where Omeka's search looks.

## 4. Search again

Search the site for **Matinees** again. The playbill comes back.

Open it. The reader lists two pages: the scan, and the PDF. Select the PDF
and the panel beside it shows the extracted text, which is Tetrak's
transcript, read back out of the PDF by a module that has never heard of
Tetrak.

## What this shows, and what it does not

- **Search finds what Tetrak read, errors included.** On this sheet Tesseract
  reads the line of performance times cleanly, but the box-office line,
  *On Sale at Music Box Theatre*, as *On Sate at Music Bex Theatr*. A word
  Tetrak misread is not found under its right spelling. The first guide's scores say how
  often that happens.
- **The PDF has no thumbnail.** Omeka makes thumbnails of PDFs with
  Ghostscript, which this image leaves out, so the PDF shows a plain page
  icon. The item keeps the scan's thumbnail.
- **The scan and the PDF are both kept.** The PDF holds a downsampled copy of
  the image (this one is 216 KB, against the scan's 1.2 MB), so it is an
  access copy beside the master, not a replacement for it. `--pdf-full-size`
  embeds the scan untouched.
- **Other platforms.** The same PDF dropped into AtoM is indexed with no
  module at all, since AtoM reads PDF text itself. That is in Tetrak's
  roadmap, not in this demo.

## From a script

Uploading through the admin interface is the point of this guide, but a script
can do the same through the REST API, in two calls:

1. `POST /api/media` with the file and `"o:item": {"o:id": …}`, as
   `scripts/seed.py` uploads the scans. Extract Text reads the text as it
   would for an upload in the admin interface.
2. Fetch the item and `PUT` it back as JSON with `o:media` listing every media
   in the order wanted. A media created on its own has no position, so Omeka
   shows it first, ahead of the scan, until the item is saved with an order.

Do not try to do both in one multipart `PUT` of the item. PHP reads uploaded
files only from a `POST`, so the item arrives with no values and Omeka saves
it empty.

## Start again

```bash
scripts/reset.sh --yes
rm playbill.pdf
```
