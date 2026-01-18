import unittest

from blocktype import BlockType, block_to_block_type


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph_single_line(self):
        block = "This is a paragrah."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_multi_lines(self):
        block = """
This is a mutline
paragrah.
"""
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading(self):
        block = "## Tis is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_code(self):
        block = """
```
a = b
b = c
```
"""
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote(self):
        block = """
> This is a quote.
> This is a quote
"""
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = """
- List item one
- List item two
"""
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = """
1. List item one
2. List item two
"""
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
