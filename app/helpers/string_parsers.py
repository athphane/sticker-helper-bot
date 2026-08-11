import re

import emoji


def is_text(input_str) -> bool:
    # Check if the input is one word
    if not re.match(r'^\w+$', input_str):
        return False

    return True


def is_emoji(text):
    return emoji.is_emoji(text)


def parse_tags(input_str: str) -> list:
    """
    Parse multiple tags from input string.
    Tags can be separated by commas or spaces.
    Returns a list of individual tags.
    """
    if not input_str:
        return []

    # Split by commas and spaces, and clean up
    tags = []
    for part in input_str.split(','):
        # Split by spaces too and clean up each tag
        sub_parts = re.split(r'\s+', part.strip())
        for tag in sub_parts:
            clean_tag = tag.strip().lower()
            if clean_tag:  # Only add non-empty tags
                tags.append(clean_tag)

    # Remove duplicates while preserving order
    unique_tags = []
    for tag in tags:
        if tag not in unique_tags:
            unique_tags.append(tag)

    return unique_tags


def validate_tag(tag: str) -> bool:
    """
    Validate if a single tag is valid.
    """
    # A valid tag should contain only word characters
    return bool(re.match(r'^\w+$', tag))
