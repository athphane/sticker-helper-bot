import re

import emoji


def is_text(input_str) -> bool:
    # Check if the input is one word
    if not re.match(r'^\w+$', input_str):
        return False

    return True


def is_emoji(text):
    return emoji.is_emoji(text)
