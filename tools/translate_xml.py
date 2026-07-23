"""
translate_xml.py
----------------
Translates a Moodle XML question file from Hebrew to Arabic (or any target language)
using the OpenAI GPT API.

What it does:
    Reads a Moodle XML file containing Hebrew programming questions (e.g. while loops,
    nested loops), translates all Hebrew text to Arabic using GPT-4, and saves a new
    XML file ready for import into Moodle.

The script translates ONLY Hebrew text inside the XML.
It does NOT translate:
  - HTML tags and attributes
  - Java code and method names
  - Run examples (lines containing --> or →)
  - File names and @@PLUGINFILE@@ references
  - Content inside <pre> blocks (code examples)

Output: same filename with _ar.xml suffix (or _<lang>.xml)

Requirements:
    pip install openai

Setup (one time only):
    1. Activate virtual environment:
           source venv/bin/activate
    2. Install dependencies:
           pip install openai
    3. Set your OpenAI API key:
           export OPENAI_API_KEY="sk-..."

Usage:
    python3 translate_xml.py --input questions.xml --key YOUR_API_KEY
    python3 translate_xml.py --input questions.xml --key YOUR_API_KEY --glossary glossary.csv
    python3 translate_xml.py --input questions.xml --key YOUR_API_KEY --lang ar

Examples with our files:
    python3 translate_xml.py --input While_All_Questions.xml --key sk-...
    python3 translate_xml.py --input NestedLoop_Questions.xml --key sk-...
    python3 translate_xml.py --input While_All_Questions.xml --key sk-... --glossary glossary.csv
"""

import argparse
import csv
import os
import re
import sys
from openai import OpenAI


# ──────────────────────────────────────────────
# 1. Load glossary from CSV (optional)
# ──────────────────────────────────────────────
def load_glossary(path):
    """Load glossary CSV with columns: hebrew, arabic"""
    glossary = {}
    if not path:
        return glossary
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                he = row.get("hebrew", "").strip()
                ar = row.get("arabic", "").strip()
                if he and ar:
                    glossary[he] = ar
        print(f"Loaded {len(glossary)} glossary entries from {path}")
    except FileNotFoundError:
        print(f"Warning: glossary file not found: {path}")
    return glossary


# ──────────────────────────────────────────────
# 2. Extract translatable segments from CDATA
# ──────────────────────────────────────────────
def extract_cdata_blocks(xml_text):
    """Return list of (start, end, content) for all CDATA sections."""
    pattern = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)
    return [(m.start(), m.end(), m.group(1)) for m in pattern.finditer(xml_text)]


def split_html_into_segments(html):
    """
    Split HTML into a list of (is_translatable, text) tuples.
    Translatable = plain text outside tags and outside <pre> blocks.
    Not translatable = HTML tags, <pre>...</pre> blocks, lines with → or -->
    """
    segments = []

    # First, protect <pre> blocks entirely
    pre_pattern = re.compile(r'<pre[^>]*>.*?</pre>', re.DOTALL | re.IGNORECASE)
    last = 0
    for m in pre_pattern.finditer(html):
        before = html[last:m.start()]
        _split_non_pre(before, segments)
        segments.append((False, m.group(0)))  # pre block: do not translate
        last = m.end()
    _split_non_pre(html[last:], segments)

    return segments


def _split_non_pre(text, segments):
    """Split text (outside pre blocks) into tag vs plain-text segments."""
    tag_pattern = re.compile(r'(<[^>]+>)')
    parts = tag_pattern.split(text)
    for part in parts:
        if not part:
            continue
        if tag_pattern.match(part):
            segments.append((False, part))  # HTML tag
        else:
            # Check if the line contains run examples (→ or -->)
            if '→' in part or '-->' in part or '@@PLUGINFILE@@' in part:
                segments.append((False, part))
            else:
                segments.append((True, part))


# ──────────────────────────────────────────────
# 3. Apply glossary before sending to API
# ──────────────────────────────────────────────
def apply_glossary(text, glossary):
    """Replace Hebrew terms with their Arabic equivalents before translation."""
    for he, ar in glossary.items():
        text = text.replace(he, ar)
    return text


# ──────────────────────────────────────────────
# 4. Translate with GPT
# ──────────────────────────────────────────────
def translate_batch(client, texts, target_lang, glossary):
    """
    Send a batch of Hebrew strings to GPT and return translated strings.
    texts: list of strings to translate
    Returns: list of translated strings (same order)
    """
    if not texts:
        return []

    # Apply glossary first
    texts_for_api = [apply_glossary(t, glossary) for t in texts]

    # Build numbered list for the API
    numbered = "\n".join(f"[{i+1}] {t}" for i, t in enumerate(texts_for_api))

    lang_names = {"ar": "Arabic", "en": "English", "fr": "French"}
    lang_name = lang_names.get(target_lang, target_lang)

    system_prompt = f"""You are a professional translator specializing in technical and educational content.
Translate the numbered Hebrew text segments below into {lang_name}.

Rules:
- Translate ONLY the text after the number and bracket, e.g. [1] text
- Translate ALL Hebrew words into {lang_name}, including Hebrew words that describe programming concepts.
  For example: the Hebrew word for "static" must become the {lang_name} word for "static" (e.g. Arabic: ساكنة), NOT the English word "static".
  The same applies to all Hebrew descriptive words such as "method", "loop", "integer", "boolean", etc.
- Keep actual Java code, method signatures, and identifiers exactly as-is (e.g. public static void, int, boolean, method names with parentheses).
  These appear verbatim in the source text and must remain unchanged.
- Always insert a space between translated {lang_name} text and any adjacent Java code snippet.
- Keep mathematical symbols and operators as-is
- Return ONLY the numbered translations, one per line, in the same format: [1] translation
- Do not add explanations or extra text"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": numbered}
        ],
        temperature=0.1
    )

    result_text = response.choices[0].message.content.strip()

    # Parse numbered results
    result_map = {}
    for line in result_text.split("\n"):
        m = re.match(r'\[(\d+)\]\s*(.*)', line.strip())
        if m:
            idx = int(m.group(1)) - 1
            result_map[idx] = m.group(2).strip()

    # Return in order, fallback to original if missing
    return [result_map.get(i, texts[i]) for i in range(len(texts))]


# ──────────────────────────────────────────────
# 5. Translate a full CDATA block
# ──────────────────────────────────────────────
def translate_cdata(client, cdata_content, target_lang, glossary, batch_size=20):
    """Translate all Hebrew text segments in a CDATA block."""
    segments = split_html_into_segments(cdata_content)

    # Collect translatable segments
    translatable_indices = [i for i, (trans, _) in enumerate(segments) if trans]
    translatable_texts = [segments[i][1] for i in translatable_indices]

    # Filter out whitespace-only or non-Hebrew segments
    hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
    real_indices = [i for i, t in zip(translatable_indices, translatable_texts)
                    if hebrew_pattern.search(t)]
    real_texts = [segments[i][1] for i in real_indices]

    if not real_texts:
        return cdata_content

    # Translate in batches
    translated_texts = []
    for start in range(0, len(real_texts), batch_size):
        batch = real_texts[start:start + batch_size]
        translated_batch = translate_batch(client, batch, target_lang, glossary)
        translated_texts.extend(translated_batch)

    # Put translations back
    translation_map = dict(zip(real_indices, translated_texts))
    result_segments = []
    for i, (translatable, text) in enumerate(segments):
        if i in translation_map:
            result_segments.append(translation_map[i])
        else:
            result_segments.append(text)

    return "".join(result_segments)


# ──────────────────────────────────────────────
# 6. Translate the full XML file
# ──────────────────────────────────────────────
def translate_xml_file(input_path, output_path, api_key, target_lang, glossary):
    print(f"\nReading: {input_path}")
    with open(input_path, "r", encoding="utf-8") as f:
        xml_text = f.read()

    client = OpenAI(api_key=api_key)

    cdata_blocks = extract_cdata_blocks(xml_text)
    print(f"Found {len(cdata_blocks)} CDATA blocks to process")

    result = xml_text
    offset = 0  # track position shifts as we replace

    for i, (start, end, content) in enumerate(cdata_blocks):
        print(f"  Translating block {i+1}/{len(cdata_blocks)}...")
        translated_content = translate_cdata(client, content, target_lang, glossary)
        new_cdata = f"<![CDATA[{translated_content}]]>"
        adj_start = start + offset
        adj_end = end + offset
        result = result[:adj_start] + new_cdata + result[adj_end:]
        offset += len(new_cdata) - (end - start)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"Output written: {output_path}")


# ──────────────────────────────────────────────
# 7. Help
# ──────────────────────────────────────────────
def print_help():
    print("""
translate_xml.py — Hebrew to Arabic Moodle XML translator
==========================================================

WHAT IT DOES:
    Translates a Moodle XML file from Hebrew to Arabic.
    The file contains programming questions (e.g. while loops, nested loops)
    and the output is a new XML file ready to import into Moodle.

    Preserves untouched: Java code, HTML tags, run examples (-->),
    <pre> blocks, and @@PLUGINFILE@@ references.

USAGE:
    python3 translate_xml.py --input <xml_file> --key <api_key> [options]

ARGUMENTS:
    --input      Path to the Hebrew Moodle XML file (required)
    --key        OpenAI API key (required)
    --lang       Target language code, default: ar (Arabic)
    --glossary   Optional CSV file with Hebrew,Arabic term pairs

OUTPUT (saved next to the input file):
    <name>_ar.xml    Arabic XML — ready to import into Moodle

EXAMPLE:
    python3 translate_xml.py \\
        --input "/mnt/c/Users/user/Documents/openUniversity/11203 מדמח בתיכון/שאלות לתרגול/יחידה 5/for loops/code questions/For_All_Questions.xml" \\
        --key "sk-pr..."

    python3 translate_xml.py --input While_All_Questions.xml --key sk-... --glossary glossary.csv

SETUP (one time only):
    1. Activate virtual environment:
           source venv/bin/activate
    2. Install dependencies:
           pip install openai
    3. Set your OpenAI API key:
           export OPENAI_API_KEY="sk-..."
       Then run without --key flag:
           python3 translate_xml.py --input While_All_Questions.xml

OPTIONS:
    -h, --help    Show this help message
""")


# ──────────────────────────────────────────────
# 8. Main
# ──────────────────────────────────────────────
def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Translate Moodle XML from Hebrew to Arabic")
    parser.add_argument("--input",    required=True,  help="Input XML file")
    parser.add_argument("--key",      required=True,  help="OpenAI API key")
    parser.add_argument("--lang",     default="ar",   help="Target language code (default: ar)")
    parser.add_argument("--glossary", default=None,   help="Optional glossary CSV file (hebrew,arabic)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: input file not found: {args.input}")
        sys.exit(1)

    # Build output filename
    base, ext = os.path.splitext(args.input)
    output_path = f"{base}_{args.lang}{ext}"

    glossary = load_glossary(args.glossary)

    translate_xml_file(
        input_path=args.input,
        output_path=output_path,
        api_key=args.key,
        target_lang=args.lang,
        glossary=glossary
    )

    print(f"\nDone! Translated file: {output_path}")


if __name__ == "__main__":
    main()
