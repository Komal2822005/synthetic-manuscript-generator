from pathlib import Path
import random


def load_text(file_path="data/raw/devanagari.md"):
    """Load manuscript text from a Markdown file."""

    project_root = Path(__file__).resolve().parent.parent
    path = project_root / file_path

    if not path.exists():
        raise FileNotFoundError(
            f"Text file not found:\n{path}"
        )

    return path.read_text(encoding="utf-8")


def clean_text(text):
    """Remove empty lines and unnecessary whitespace."""

    lines = []

    for line in text.splitlines():
        line = line.strip()

        if line:
            lines.append(line)

    return "\n".join(lines)


def get_random_passage(
    text,
    min_chars=200,
    max_chars=600
):
    """Select a random passage from the manuscript."""

    text = clean_text(text)

    if len(text) <= max_chars:
        return text

    start = random.randint(
        0,
        len(text) - min_chars
    )

    return text[start:start + max_chars]


if __name__ == "__main__":

    file_path = "data/raw/devanagari.md"

    text = load_text(file_path)

    passage = get_random_passage(text)

    print("Generated passage:")
    print("------------------")
    print(passage)