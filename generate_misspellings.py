#!/usr/bin/env python3
"""
Generates 4 misspelled versions and a high school level definition for each
word in data/commonly-misspelled-words.md.

Output: data/misspellings.json

Authentication (in order of precedence):
  1. ANTHROPIC_API_KEY env var  → uses x-api-key header
  2. ~/.claude/remote/.session_ingress_token  → uses Authorization: Bearer header
"""

import json
import re
import os
import httpx

WORDS_FILE = "data/commonly-misspelled-words.md"
OUTPUT_FILE = "data/misspellings.json"
SESSION_TOKEN_PATH = "/home/claude/.claude/remote/.session_ingress_token"

# Number of words to process per API call
BATCH_SIZE = 10


def parse_words(filepath: str) -> list[str]:
    """Extract the canonical word from each line, stripping notes like '(vs practise)'."""
    words = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and headers
            if not line or line.startswith("#"):
                continue
            # Strip parenthetical notes like "(vs practise)" or "(vs principle)"
            word = re.sub(r"\s*\(.*?\)", "", line).strip()
            if word:
                words.append(word)
    return words


def get_auth_headers() -> dict:
    """Return auth headers, preferring ANTHROPIC_API_KEY then session ingress token."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return {"x-api-key": api_key}
    if os.path.exists(SESSION_TOKEN_PATH):
        token = open(SESSION_TOKEN_PATH).read().strip()
        return {"Authorization": f"Bearer {token}"}
    raise EnvironmentError(
        "No API credentials found. Set ANTHROPIC_API_KEY or ensure "
        f"{SESSION_TOKEN_PATH} exists."
    )


def generate_for_batch(headers: dict, words: list[str]) -> list[dict]:
    """
    Call Claude to generate 4 misspellings and a definition for each word in the batch.
    Returns a list of dicts with keys: word, misspellings, definition.
    """
    words_list = "\n".join(f"- {w}" for w in words)
    prompt = f"""For each word in the list below, provide:
1. Four (4) plausible misspellings that a student might make (vary the types of errors: transposed letters, wrong vowels, missing/doubled consonants, phonetic spellings, etc.)
2. A clear, concise definition suitable for a high school student (1-2 sentences)

Return your answer as a JSON array. Each element must have exactly these keys:
- "word": the correct spelling (exactly as given)
- "misspellings": an array of exactly 4 strings
- "definition": a string with the high school-level definition

Words:
{words_list}

Return only the JSON array, no other text."""

    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

    with httpx.Client(timeout=120) as client:
        response = client.post(
            f"{base_url}/v1/messages",
            headers={
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01",
                **headers,
            },
            json={
                "model": "claude-opus-4-6",
                "max_tokens": 4096,
                "thinking": {"type": "adaptive"},
                "messages": [{"role": "user", "content": prompt}],
            },
        )
        response.raise_for_status()
        data = response.json()

    # Extract text block from response
    text = next(
        (block["text"] for block in data["content"] if block["type"] == "text"),
        "",
    ).strip()

    # Find the first '[' and parse exactly one JSON array from that position
    start = text.find("[")
    if start == -1:
        raise ValueError(f"No JSON array found in response: {text[:200]}")
    result, _ = json.JSONDecoder().raw_decode(text, idx=start)
    return result


def main():
    auth_headers = get_auth_headers()

    words = parse_words(WORDS_FILE)
    print(f"Found {len(words)} words to process.")

    # Load existing results to support resume
    results = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE) as f:
            results = json.load(f)
        print(f"Resuming: {len(results)} entries already done.")

    done_words = {entry["word"] for entry in results}

    for i in range(0, len(words), BATCH_SIZE):
        batch = words[i : i + BATCH_SIZE]
        # Skip words already processed
        pending = [w for w in batch if w not in done_words]
        if not pending:
            continue
        print(f"Processing words {i + 1}–{i + len(batch)}: {', '.join(pending)}")
        batch_results = generate_for_batch(auth_headers, pending)
        results.extend(batch_results)
        done_words.update(r["word"] for r in batch_results)
        print(f"  → {len(batch_results)} entries generated.")

        # Save incrementally so we can resume on failure
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)

    print(f"\nDone! {len(results)} entries written to {OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
