# Los Angeles stage and screen ephemera: sources

Five items from Tetrak's OCR evaluation corpus, copied from
`evaluation/ocr/corpus/images/` in
[scattercode/tetrak](https://github.com/scattercode/tetrak), where their
human-verified transcripts also live. That corpus's `SOURCES.md` has the full
rights reasoning; this records what applies to these five. Four are
byte-for-byte copies; the playbill was converted to PNG (see the notes).

Every item is in the public domain in the United States. None carries an
attribution requirement, but we credit the holding institution anyway.

| File | Item | Date | Source | Rights |
|---|---|---|---|---|
| `inside-facts-1930-cover.jpg` | *Inside Facts of Stage and Screen*, vol. XI, no. 22, front page | 31 May 1930 | [Internet Archive / Media History Digital Library](https://archive.org/details/insidefacts1122-1930-05-31) | US work published 1930; copyright expired 1 January 2026 |
| `kar-mi-troupe-poster.jpg` | "The great Victorina Troupe … sword swallowing act on earth": vaudeville chromolithograph, Donaldson Litho. Co. | c. 1914 | [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:The_great_Victorina_Troupe_originators_and_presenters_of_the_most_marvelous_sword_swallowing_act_on_earth._LCCN2014636914.jpg), from the Library of Congress theatrical poster collection (LCCN 2014636914) | Library of Congress: no known restrictions on publication; published before 1929 |
| `hollywood-boulevard-east.jpg` | "Looking east on Hollywood Boulevard": Tichnor linen postcard, front | c. 1930–45 | [Digital Commonwealth / Boston Public Library](https://www.digitalcommonwealth.org/search/commonwealth:2n49tg34w) | Published without a copyright notice; the Boston Public Library states "No known copyright restrictions" |
| `graumans-chinese-theatre.jpg` | "The Chinese Theatre, Hollywood, California": Tichnor linen postcard, front | c. 1937–45: the marquee dates the photograph | [Digital Commonwealth / Boston Public Library](https://www.digitalcommonwealth.org/search/commonwealth:2n49tg32b) | As above |
| `hollywood-music-box-playbill-1926.png` | Hollywood Music Box Theatre playbill: *Ken-Geki*, the Imperial Theatre (Tokio) company. Published by J. F. Huber, 1631 South Los Angeles St. | Week beginning 18 June 1926 | Workman and Temple Family Homestead Museum Collection, 1830–1930, via [USC Digital Library](https://digitallibrary.usc.edu/) | US work published 1926; public domain on its date alone |

## Transcripts

`transcripts/<name>.txt` is the reference transcript of the first three
items, copied byte for byte from `evaluation/ocr/corpus/expected/` in Tetrak
at release 5.14.0, where all three are recorded as human-verified (28
September 2026). Each media record links to its file at that tag. Tetrak
publishes its ground-truth transcripts under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the text they
transcribe is public domain, as above.

The Grauman's postcard and the playbill deliberately have no transcript here,
though Tetrak's corpus has verified ones for both. They are the items the
demo transcribes with Tetrak (`tutorials/transcribe-with-tetrak.md`), and
their verified transcripts in Tetrak's corpus are there to check its reading
against afterwards.

## Notes

- **The poster's two names.** The title is the Library of Congress
  catalogue's, after the performer Victorina named in the captions. The
  printed headline reads "See the great Kar-Mi Troupe", which is where the
  file name comes from. The Omeka item keeps the catalogue title and records
  the headline as `dcterms:alternative`.
- **The poster was downscaled** in Tetrak's corpus from the source 4104 × 5116
  to 1123 × 1400, to sit in the same resolution band as the rest of that
  corpus. Nothing was cropped: the colour calibration bar and ruler are still
  in frame.
- **The playbill is a PNG here, not the corpus's TIFF.** Browsers do not
  display TIFF, and the sites' viewer shows the original file, so it was
  converted losslessly: the pixels are identical to the 573 × 1200 TIFF,
  checked image against image. Only the container changed, along with a
  meaningless 1 × 1 dpi tag, which was dropped.
- **Grauman's marquee is cut off by the frame**, at *SYLVIA SI…*: Sylvia
  Sidney in *You Only Live Once*, which opened there on 27 January 1937 and
  so dates the photograph.
- **The postcards are the front only.** The reverse is a different OCR problem
  and is not included.
