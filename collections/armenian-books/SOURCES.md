# Armenian printed books: sources

Pages from three books. The scans are on Wikimedia Commons and the proofread
transcriptions on Armenian Wikisource. The images here are byte-identical to
the pages `tetrak-hy-trainer` harvested from Wikisource.

Two items carry reference transcripts: the Soviet Armenian Encyclopedia pages
and *Brave Nazar*. The other two, *The Death of Kikos* and the medical
encyclopedia pages, deliberately do not. They are the items the demo
transcribes with Tetrak (`tutorials/transcribe-with-tetrak.md`), and
Wikisource's proofread text, at the revision each page's source link pins, is
there to check its reading against afterwards.

Each page's Wikisource revision is recorded in `collection.toml`, so the
transcript a page is compared with is fixed even if Wikisource is edited
later. Every page is proofread to Wikisource's quality level 4 (validated).

## Hovhannes Tumanyan, "The Death of Kikos" (`tumanyan-death-of-kikos/`)

| | |
|---|---|
| Work | Կիկոսի մահը (The Death of Kikos), 1913, complete |
| Edition | The same volume as *Brave Nazar*, below: complete works, volume 5, 1994 |
| Pages | Scan pages 252–255, printed pages 246–249 |
| Rights | **Public domain**, as *Brave Nazar* |

The tale runs from its title to its last line with nothing else on these
pages. Like *Brave Nazar*, it is not held out from Tetrak's Armenian
recogniser: its images were never trained on, but its text is in the volume's
harvest that the synthetic training text and word list draw from.

## Popular medical encyclopedia (`medical-encyclopedia/`)

| | |
|---|---|
| Title | Հանրամատչելի բժշկական հանրագիտարան (Popular medical encyclopedia) |
| Editor | Հ. Մ. Այվազյան |
| Published | Armenian Encyclopedia Publishing House, Yerevan, 2001 |
| Pages | Pages 512 and 514, scan and printed alike, from the article on caring for young children. Not 513: the held-out set samples pages rather than taking a run, and 513 is not in it |
| Scan | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:%D5%80%D5%A1%D5%B6%D6%80%D5%A1%D5%B4%D5%A1%D5%BF%D5%B9%D5%A5%D5%AC%D5%AB_%D5%A2%D5%AA%D5%B7%D5%AF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%B0%D5%A1%D5%B6%D6%80%D5%A1%D5%A3%D5%AB%D5%BF%D5%A1%D6%80%D5%A1%D5%B6_(Popular_medical_encyclopedia).djvu) |
| Rights | **CC BY-SA 3.0**, released by the Armenian Encyclopedia Publishing House like the Soviet Armenian Encyclopedia |

Both pages are in the held-out evaluation set of Tetrak's Armenian
recogniser, excluded from everything it was trained on. Anything published
from them, Tetrak's transcripts included, needs attribution and the same
licence.

## Transcripts

`*/transcripts/<scan page>.txt` is each page's text from Armenian Wikisource
at exactly that recorded revision, reduced from wikitext to plain text by the
same cleaning `tetrak-hy-trainer` uses (`clean_wikitext`, as of its charset
v4). The seeder loads it as the page's reference transcript.

That cleaning also folds a few things transcribers type in place of what the
page prints: a Latin colon where an Armenian word ends on the full stop `։`,
and angle brackets typed for guillemets, `<Ազգ>` for `«Ազգ»`. It keeps the
angle brackets the page really prints. In the encyclopedia that is the
"derived from" sign of its etymologies, as in `ԱՐՇԻՊԵԼԱԳ (<իտալ․ Arcipelago`;
in Tumanyan's collected works, the editors' brackets.

Wikisource publishes its text under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), credited to
the Armenian Wikisource contributors. For the encyclopedia that sits on top of
the scan's own CC BY-SA 3.0. For Tumanyan, whose words are in the public
domain, it covers what the volunteers added: the transcription, not the
tale.

## Soviet Armenian Encyclopedia, volume 2 (`ase-vol2/`)

| | |
|---|---|
| Title | Հայկական սովետական հանրագիտարան, հատոր 2 |
| Editor-in-chief | Վիկտոր Համբարձումյան (Viktor Ambartsumian) |
| Published | Yerevan, 1976 |
| Pages | Scan pages 105–114, which are also printed pages 105–114: the held-out evaluation set of Tetrak's Armenian recogniser |
| Scan | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:%D5%80%D5%A1%D5%B5%D5%AF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%8D%D5%B8%D5%BE%D5%A5%D5%BF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%80%D5%A1%D5%B6%D6%80%D5%A1%D5%A3%D5%AB%D5%BF%D5%A1%D6%80%D5%A1%D5%B6_(Soviet_Armenian_Encyclopedia)_2.djvu) |
| Transcription | [Armenian Wikisource index](https://hy.wikisource.org/wiki/%D4%BB%D5%B6%D5%A4%D5%A5%D6%84%D5%BD:%D5%80%D5%A1%D5%B5%D5%AF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%8D%D5%B8%D5%BE%D5%A5%D5%BF%D5%A1%D5%AF%D5%A1%D5%B6_%D5%80%D5%A1%D5%B6%D6%80%D5%A1%D5%A3%D5%AB%D5%BF%D5%A1%D6%80%D5%A1%D5%B6_(Soviet_Armenian_Encyclopedia)_2.djvu) |
| Rights | **CC BY-SA 3.0.** The Armenian Encyclopedia Publishing House holds the rights and released the encyclopedia under this licence; the permission is recorded on the Commons file page. |

Unlike everything else here, this is in copyright, under an open licence.
Reusing these pages, including transcripts made from them, needs attribution
to the Armenian Encyclopedia Publishing House and the same licence.

## Hovhannes Tumanyan, "Brave Nazar" (`tumanyan-brave-nazar/`)

| | |
|---|---|
| Work | Քաջ Նազարը (Brave Nazar), the 1912 version, complete |
| Author | Հովհաննես Թումանյան (Hovhannes Tumanyan), 1869–1923 |
| Edition | Երկերի լիակատար ժողովածու, հատոր 5 (complete works, volume 5), the ten-volume academic edition, 1994 |
| Pages | Scan pages 241–251, printed pages 235–245: in this part of the scan the printed number is 6 lower |
| Scan | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:%D4%B9%D5%B8%D6%82%D5%B4%D5%A1%D5%B6%D5%B5%D5%A1%D5%B6%D5%AB_%D4%B5%D4%BC%D4%BA_%D5%B05.djvu) |
| Transcription | [Armenian Wikisource index](https://hy.wikisource.org/wiki/%D4%BB%D5%B6%D5%A4%D5%A5%D6%84%D5%BD:%D4%B9%D5%B8%D6%82%D5%B4%D5%A1%D5%B6%D5%B5%D5%A1%D5%B6%D5%AB_%D4%B5%D4%BC%D4%BA_%D5%B05.djvu) |
| Rights | **Public domain.** Tumanyan died in 1923; Commons marks the scan PD-old |

The tale runs from its title page to its last line with nothing else on these
pages.

Unlike the encyclopedia pages, these are not held out from Tetrak's Armenian
recogniser. Their page images were never used in training, but this volume's
Wikisource text, the tale included, is among the harvests that the synthetic
training text and the word list are drawn from. OCR of these pages shows the
recogniser on text it has seen in another form; the encyclopedia pages are
the fair test.
