import re
from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(markdown):
    lines = markdown.splitlines()
    if lines[0] == "":
        del lines[0]
    if re.match(r"^#{1,6} ", lines[0]):
        return BlockType.HEADING
    if re.match(r"^`{3}$", lines[0]) and re.match(r"^`{3}$", lines[-1]):
        return BlockType.CODE
    if all([re.match(r"^> ", line) for line in lines]):
        return BlockType.QUOTE
    if all([re.match(r"^\- ", line) for line in lines]):
        return BlockType.UNORDERED_LIST
    if all([re.match(r"^\d+\. ", line) for line in lines]):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH
