# site-keyword-scraper

A simple CLI tool that crawls a website, extracts text from every page, and outputs the most frequent words — useful for basic SEO keyword research.

## Features

- Crawls all internal pages of a given website
- Filters out common Russian and English stop words
- Outputs a ranked keyword frequency list to a `.txt` file
- Interactive prompts — no config files needed

## Requirements

- Python 3.10–3.13

> ⚠️ Python 3.14+ is not supported due to PyInstaller compatibility.

## Installation

```bash
pip install requests beautifulsoup4
```

## Usage

```bash
python keyword_scraper.py
```

You will be prompted to enter:

- **Site URL** — the website to crawl (e.g. `https://example.com/`)
- **Top N** — how many top keywords to save (default: 200)

The results are saved to `keywords_<domain>.txt` in the current directory.

### Output format

```
============================================================
  КЛЮЧЕВЫЕ СЛОВА: https://example.com/
============================================================

Обработано страниц:    142
Уникальных слов:       3871
Показаны топ-200

---------------------------------------------
№     Ключевое слово                 Частота
---------------------------------------------
1     доставка                           843
2     купить                             701
3     цена                               654
...
```

## Building a standalone executable

### Windows

```bash
pip install pyinstaller
pyinstaller --onefile --console --name "keyword_scraper" keyword_scraper.py
```

The `.exe` will be located in the `dist/` folder.

### macOS / Linux

```bash
pip3 install pyinstaller
pyinstaller --onefile --console --name "keyword_scraper" keyword_scraper.py
```

The binary will be located in the `dist/` folder.

> **Note:** Executables are platform-specific. A Windows `.exe` must be built on Windows, a macOS binary on macOS.

## Configuration

You can adjust the following constants at the top of `keyword_scraper.py`:

| Constant | Default | Description |
|---|---|---|
| `MIN_WORD_LENGTH` | `3` | Minimum number of characters for a word to be counted |
| `DELAY` | `0.5` | Delay between requests in seconds |
| `REQUEST_TIMEOUT` | `10` | Request timeout in seconds |
| `STOP_WORDS` | (built-in) | Set of words to exclude from results |

## License

MIT
