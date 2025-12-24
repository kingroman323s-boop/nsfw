import re
import unicodedata
from unidecode import unidecode


LEET_MAP = str.maketrans({
    "0": "o",
    "1": "i",
    "3": "e",
    "4": "a",
    "5": "s",
    "7": "t",
    "@": "a",
    "$": "s",
    "!": "i",
})


def normalize(text: str) -> str:
    if not text:
        return ""

    # Unicode normalize
    text = unicodedata.normalize("NFKD", text)

    # Convert accents & non-latin
    text = unidecode(text)

    # Lowercase
    text = text.casefold()

    # Replace leetspeak
    text = text.translate(LEET_MAP)

    # Remove zero-width characters
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)

    # Remove everything except letters
    text = re.sub(r"[^a-z]", "", text)

    return text
