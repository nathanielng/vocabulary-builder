# Vocabulary Builder

> **Two versions are available:**
> - **Original (server-based):** requires Python + `game_server.py` — progress is stored server-side in `data/progress.json`
> - **Static (GitHub Pages):** lives in `static/` — no server needed, runs entirely in the browser with progress stored in `localStorage`

An interactive web-based game platform for learning and practicing the spelling of commonly misspelled words. Powered by Claude AI for content generation, with two distinct game modes and persistent progress tracking.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Running the Server](#running-the-server)
- [Games](#games)
  - [Word Drop](#word-drop)
  - [Spelling Correction](#spelling-correction)
- [Generating Word Data](#generating-word-data)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Progress Tracking](#progress-tracking)
- [Static Version (GitHub Pages)](#static-version-github-pages)

---

## Overview

Vocabulary Builder helps students and learners improve spelling accuracy through active practice. The application uses the Claude AI API to generate realistic misspellings and definitions for a curated list of commonly misspelled English words, then presents them through two engaging game formats.

Key design goals:
- **No database required** — all data is stored as local JSON files
- **No frontend framework** — pure HTML/CSS/JavaScript
- **Minimal dependencies** — only the Anthropic Python SDK is required
- **Phase-based progression** — words are introduced in batches and reviewed until mastered

---

## Features

- Two game modes: an arcade-style falling-word game and a traditional spelling quiz
- AI-generated misspellings and definitions (4 misspellings per word)
- Phase-based progression with 10 words per phase
- Graduated learning: words require 3 correct answers in a row to be "mastered"
- Spaced repetition: mastered words return after 30 days for a quick review (1 correct re-confirms, wrong fully resets)
- Review pool: words answered incorrectly in earlier phases reappear in later phases
- Pet companion with a reward system in the Spelling Correction game — pick a pet, then earn treats (5 correct in a row) and accessories (every 10 correct)
- Persistent progress saved automatically between sessions
- Fully self-contained — runs on a single lightweight Python HTTP server

---

## Project Structure

```
vocabulary-builder/
├── game_server.py               # HTTP server (port 8080), serves games and REST API
├── generate_misspellings.py     # CLI tool: uses Claude API to generate word data
├── game_word_drop.html          # Word Drop arcade game (server version)
├── game_spelling.html           # Spelling Correction quiz (server version)
├── requirements.txt             # Python dependencies
├── data/
│   ├── commonly-misspelled-words.md  # Source list of words to learn (~99 words)
│   ├── misspellings.json             # Generated word data (created by generate_misspellings.py)
│   └── progress.json                 # User progress (created automatically at runtime)
├── static/                      # Static / GitHub Pages version (no server required)
│   ├── index.html               # Landing page with links to both games
│   ├── game_word_drop.html      # Word Drop (localStorage-based progress)
│   ├── game_spelling.html       # Spelling Correction (localStorage-based progress)
│   └── data/
│       └── misspellings.json    # Copy of word data served as a static asset
└── .github/
    └── workflows/
        └── pages.yml            # GitHub Actions workflow: deploys static/ to GitHub Pages
```

---

## Prerequisites

- Python 3.6 or higher
- An [Anthropic API key](https://console.anthropic.com/) (only needed for generating word data)

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

The `generate_misspellings.py` script requires access to the Claude API. Set your API key as an environment variable:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Optionally, you can override the API base URL:

```bash
export ANTHROPIC_BASE_URL="https://api.anthropic.com"  # default
```

### 3. Generate word data

Run the generator script once to create `data/misspellings.json`:

```bash
python generate_misspellings.py
```

This reads words from `data/commonly-misspelled-words.md`, calls the Claude API in batches of 10, and writes structured JSON output. The process takes a minute or two depending on the number of words.

You only need to run this once unless you modify the word list.

---

## Running the Server

```bash
python game_server.py
```

Output:

```
Vocabulary Builder Games
  Word Drop:  http://localhost:8080/game_word_drop.html
  Spelling:   http://localhost:8080/game_spelling.html
Press Ctrl+C to quit.
```

Open your browser to `http://localhost:8080` — it will redirect to the Word Drop game. To switch games, use the navigation links within each game page.

---

## Games

### Word Drop

An arcade-style game where words fall from the top of the screen — pick the correctly spelled one.

**How to play:**

1. Five tokens fall from the top: one correctly spelled word and four misspellings.
2. Click the **correctly spelled** word before it falls off the screen.
3. All tokens look identical — you must recognize the correct spelling from the definition hint shown at the top.
4. A word is **mastered** after you pick it correctly 3 times in a row. Mastered words stop appearing.
5. Words you miss or pick incorrectly are added to a review pool and reappear in later phases.

**Spaced repetition:**
- Mastered words return after **30 days** for review
- In review mode, only **1 correct** answer re-confirms mastery (resets the 30-day clock)
- Getting it wrong on review **fully resets** the word — it needs 3 correct again

**Mechanics:**
- 10 words per phase
- Speed increases with each phase (starts at 1.4 px/frame, +0.18 per phase)
- Words from earlier phases that had errors become "review words" in subsequent phases
- Spaced-review words are mixed into whatever phase you play once eligible

---

### Spelling Correction

A traditional spelling quiz where you type the correct spelling of a misspelled word.

**How to play:**

1. On first launch, choose a **pet companion** (Rabbit, Bear, or Puppy) — it cheers you on and collects rewards as you play.
2. A misspelled word is shown in large red text, with its definition displayed below.
3. Type the correct spelling into the input field and press **Enter** or click **Check**.
4. Immediate feedback shows whether your answer was correct or incorrect.
5. Use the **Hide/Show definition** button to toggle the hint.
6. A word is graduated after 3 correct answers in a row.

**Mechanics:**
- Same phase structure and graduation rules as Word Drop
- Progress is independent from the Word Drop game
- Incorrect answers reset the streak for that word, and the missed word is re-inserted into the current round so it comes back
- A "Words to Review" summary lists every word you missed at the end of a phase

**Pet rewards:**
- Every **5 correct answers in a row** earns a **treat** (a food item your pet keeps — the last 3 are shown)
- Every **10 correct answers** in the session earns an **accessory**
- The treat streak resets when you answer incorrectly; the accessory counter accumulates across phases
- Your chosen pet and its collected items are saved with your progress

---

## Generating Word Data

The `generate_misspellings.py` script is responsible for building `data/misspellings.json`.

**Source word list:** Edit `data/commonly-misspelled-words.md` to add, remove, or modify the words in the learning set. The file contains roughly 99 commonly misspelled English words.

**Re-generating data:** After changing the word list, delete or overwrite the existing JSON file and re-run the script:

```bash
python generate_misspellings.py
```

**Output format** — each entry in `misspellings.json`:

```json
{
  "word": "Accumulation",
  "misspellings": ["Acumulation", "Accumulaton", "Accumalation", "Accumullation"],
  "definition": "The process of gradually gathering or acquiring more of something."
}
```

---

## API Reference

The game server exposes a small REST API used by the frontend games.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/data` | Returns the full `misspellings.json` array |
| `GET` | `/api/progress` | Returns saved progress, or `{}` if none exists |
| `POST` | `/api/progress` | Accepts a JSON body and saves it to `data/progress.json` |
| `GET` | `/` | Redirects to `/game_word_drop.html` |
| `GET` | `/game_word_drop.html` | Serves the Word Drop game |
| `GET` | `/game_spelling.html` | Serves the Spelling Correction game |

CORS headers are enabled on all endpoints.

---

## Configuration

Most configuration is done by editing constants at the top of the relevant files.

### Server (`game_server.py`)

| Constant | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | HTTP server port |
| `PROGRESS_FILE` | `"data/progress.json"` | Where user progress is stored |

### Word Drop game (`game_word_drop.html`)

| Constant | Default | Description |
|----------|---------|-------------|
| `WORDS_PER_PHASE` | `10` | Words introduced per phase |
| `GRAD_STREAK` | `3` | Consecutive correct picks to master a word |
| `REVIEW_STREAK` | `1` | Correct picks needed to re-confirm mastery on review |
| `COOLDOWN_DAYS` | `30` | Days before a mastered word reappears for review |
| `BASE_SPEED` | `1.4` | Falling speed in px/frame at phase 1 |
| `SPEED_INC` | `0.18` | Speed increase per additional phase |

### Spelling game (`game_spelling.html`)

| Constant | Default | Description |
|----------|---------|-------------|
| `WORDS_PER_PHASE` | `10` | Words per phase |
| `GRAD_STREAK` | `3` | Consecutive correct answers to graduate a word |

### Data generator (`generate_misspellings.py`)

| Constant | Default | Description |
|----------|---------|-------------|
| `BATCH_SIZE` | `10` | Words sent to Claude per API request |
| `WORDS_FILE` | `"data/commonly-misspelled-words.md"` | Source word list |
| `OUTPUT_FILE` | `"data/misspellings.json"` | Generated output path |

---

## Progress Tracking

Progress is stored in `data/progress.json` and updated automatically as you play. Each game mode maintains its own independent progress under its own key, and the Spelling game also persists the selected pet and its collected items at the top level. The structure looks like this:

```json
{
  "word_drop": {
    "current_phase": 2,
    "word_stats": {
      "Accumulation": {
        "streak": 3,
        "total_errors": 1,
        "graduated": true,
        "graduated_date": "2026-06-14T10:00:00.000Z",
        "review_mode": false,
        "errors": [
          { "ts": "2026-06-14T09:55:00.000Z", "type": "missed", "game": "word_drop" }
        ]
      }
    }
  },
  "spelling": {
    "current_phase": 1,
    "word_stats": {
      "Ascend": {
        "streak": 0,
        "total_errors": 2,
        "graduated": false,
        "errors": [
          { "ts": "2026-06-15T08:00:00.000Z", "typed": "Assend", "game": "spelling" }
        ]
      }
    }
  },
  "selectedPet": "rabbit",
  "petFood": [{ "id": "cookie", "emoji": "🍪" }],
  "petAccessories": [{ "id": "ribbon", "emoji": "🎀" }]
}
```

**Word Drop `word_stats` fields:**
- `streak` — consecutive correct picks (resets to 0 on error)
- `total_errors` — lifetime error count
- `graduated` — `true` when the word is mastered
- `graduated_date` — ISO timestamp of when mastery was achieved (used for spaced repetition cooldown)
- `review_mode` — `true` when the word has returned after the 30-day cooldown
- `errors` — array of error records with `ts`, `type` (`missed` or `clicked_wrong`), and `game`

**Spelling `word_stats` fields** use the same structure but errors record `typed` (what the player entered) instead of `type`.

To reset progress for both games, delete `data/progress.json`:

```bash
rm data/progress.json
```

---

## Static Version (GitHub Pages)

The `static/` folder contains a self-contained version of both games that requires no Python server and can be hosted on GitHub Pages (or any static file host).

### What changed from the original

The two versions share the **same gameplay** — both game modes, the phase/graduation system, and the Spelling game's pet rewards are identical. They differ **only in the storage layer**: the server version talks to the Python REST API, while the static version uses the browser's `localStorage`. Keep them in sync — when you change game logic in a root file, mirror it into `static/` (and vice versa), changing only the rows below.

| Concern | Original (server) | Static (`static/`) |
|---|---|---|
| Word data | `GET /api/data` from Python server | `fetch('data/misspellings.json')` — static file |
| Load progress | `GET /api/progress` from Python server | `localStorage.getItem('vb_progress')` |
| Save progress | `POST /api/progress` to Python server | `localStorage.setItem('vb_progress', ...)` |
| Progress scope | Server file — shared across browsers/devices | Per-browser — isolated to each device |
| `save()` / `saveProgress()` | `async` function using `fetch` | Synchronous `localStorage` write |
| Error message | Mentions `game_server.py` | Generic message only |
| HTML `<title>` | `… Vocabulary Builder` | `… Vocabulary Builder (Static)` |
| In-file comment | — | Banner comment noting all changes |

### Deploying to GitHub Pages

1. **Enable GitHub Pages** in the repository settings:
   - Go to **Settings → Pages**
   - Set the source to **GitHub Actions**

2. **Push to `main`** — the workflow at `.github/workflows/pages.yml` will automatically deploy the `static/` folder to GitHub Pages on every push.

3. The site will be available at `https://nathanielng.github.io/vocabulary-builder/`.

### Running the static version locally

Because the games fetch `data/misspellings.json` via `fetch()`, you need a local HTTP server (browsers block `file://` fetches). Any of these work:

```bash
# Python 3
cd static && python -m http.server 8000

# Node (npx)
cd static && npx serve .
```

Then open `http://localhost:8000` in your browser.

### Updating word data

The `static/data/misspellings.json` file is a copy of `data/misspellings.json`. After re-running `generate_misspellings.py` to update word data, copy the file across:

```bash
cp data/misspellings.json static/data/misspellings.json
```

Then commit and push — the GitHub Actions workflow will redeploy automatically.
