# Used from fastapi-utils library https://github.com/fastapiutils/fastapi-utils/blob/master/fastapi_utils/camelcase.py
import re


def snake2camel(snake: str, start_lower: bool = False) -> str:
    """
    Converts a snake_case string to camelCase.

    The `start_lower` argument determines whether the first letter in the generated camelcase should
    be lowercase (if `start_lower` is True), or capitalized (if `start_lower` is False).
    """
    camel = snake.title()
    camel = re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)
    if start_lower:
        camel = re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)
    return camel


def camel2snake(camel: str) -> str:
    """
    Converts a camelCase string to snake_case.
    """
    snake = re.sub(r"([a-zA-Z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", camel)
    snake = re.sub(r"([a-z0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    return snake.lower()


def pluralize(word: str):
    vowel_criteria = ["oy", "ey", "ay"]
    ch_criteria = ["ch", "s", "sh", "ss", "z", "x", "o"]
    for i in vowel_criteria:
        if word.endswith(i):
            return word + "s"
    for i in ch_criteria:
        if word.endswith(i):
            return word + "es"
    if word.endswith("y"):
        return word[:-1] + "ies"
    else:
        return word + "s"
