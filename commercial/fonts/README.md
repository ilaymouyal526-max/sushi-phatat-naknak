# Fonts

Both families are licensed under the SIL Open Font License 1.1 (see `OFL.txt`) and were downloaded from Google Fonts.

| File | Family | Copyright |
|---|---|---|
| `Montserrat-Light.ttf` | Montserrat | Copyright 2011 The Montserrat Project Authors (https://github.com/JulietaUla/Montserrat) |
| `ShipporiMincho-Medium-subset.ttf`, `ShipporiMincho-Bold-subset.ttf` | Shippori Mincho | Copyright 2021 The Shippori Mincho Project Authors (https://github.com/fontdasu/ShipporiMincho) |

The full Shippori Mincho files are about 8 MB each. The `-subset` files are cut down to the kana, the CJK punctuation and the kanji in `COPY` (`typography.py`), so they come to about 190 KB.

If you add new kanji, `typography.py` stops with an error that names the missing characters. To rebuild the subsets, download the full fonts and subset them again:

```bash
pip install fonttools
curl -sS "https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;700" | grep -o 'https[^)]*\.ttf'
# Download both URLs as ShipporiMincho-Medium.ttf / -Bold.ttf, then for each weight:
pyftsubset ShipporiMincho-Medium.ttf --unicodes="U+0020,U+3000-303F,U+3040-309F,U+30A0-30FF" \
  --text="$(python3 ../typography.py --kanji)" --layout-features='*' --output-file=ShipporiMincho-Medium-subset.ttf
```
