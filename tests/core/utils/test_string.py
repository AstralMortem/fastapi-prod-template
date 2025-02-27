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

    return camel.strip("_*")


def camel2snake(camel: str) -> str:
    """
    Converts a camelCase string to snake_case.
    """
    snake = re.sub(r"([a-zA-Z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", camel)
    between = snake
    snake = re.sub(
        r"([a-z0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2).lower()}", snake
    )

    if between == snake:
        camel = []
        for i in snake:
            if i.isupper():
                camel.append(i)
        snake = "".join(camel[:-1]) + "_" + camel[-1] + snake.strip("".join(camel))

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


def test_snake2camel():
    assert snake2camel("test_case") == "TestCase"
    assert snake2camel("test_case", start_lower=True) == "testCase"
    assert snake2camel("_private_var") == "PrivateVar"


def test_camel2snake():
    assert camel2snake("TestCase") == "test_case"
    assert camel2snake("testCase") == "test_case"
    assert camel2snake("HTTPRequest") == "http_request"
    assert camel2snake("Super_TestCase") == "super_test_case"


def test_pluralize():
    assert pluralize("box") == "boxes"
    assert pluralize("toy") == "toys"
    assert pluralize("baby") == "babies"
    assert pluralize("church") == "churches"
    assert pluralize("dog") == "dogs"
