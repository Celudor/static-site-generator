import unittest

from functions import (
    extract_markdown_images,
    extract_markdown_links,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_image(self):
        node = TextNode("This is an image", TextType.IMAGE, "/assets/a.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.props["src"], node.url)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(len(new_nodes), 3)
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text_type, TextType.CODE)
        self.assertEqual(new_nodes[1].text, "code block")

    def test_bold(self):
        node = TextNode("This is **bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(len(new_nodes), 2)
        self.assertEqual(new_nodes[0].text_type, TextType.TEXT)
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)
        self.assertEqual(new_nodes[1].text, "bold")


class TestExtractMarkdownLink(unittest.TestCase):
    def test_only_link(self):
        self.assertEqual(
            extract_markdown_links("[click me](http://example.com)"),
            [("click me", "http://example.com")],
        )

    def test_link_and_image(self):
        self.assertEqual(
            extract_markdown_links(
                "This is [link](http://a.pl) and this is an ![image](/assets/img.png)."
            ),
            [("link", "http://a.pl")],
        )


class TestExtractMarkdownImages(unittest.TestCase):
    def test_only_image(self):
        self.assertEqual(
            extract_markdown_images("This is ![image](http://a.pl/i.jpg)"),
            [("image", "http://a.pl/i.jpg")],
        )

    def test_image_and_link(self):
        self.assertEqual(
            extract_markdown_images(
                "This is [link](http://a.pl) and this is an ![image](/assets/img.png)."
            ),
            [("image", "/assets/img.png")],
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_nodes_links(self):
        node = TextNode(
            "This is a text with a [link](http:/a.pl) and another [link2](/a/b/c).",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is a text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "http:/a.pl"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "/a/b/c"),
                TextNode(".", TextType.TEXT),
            ],
            split_nodes_link([node]),
        )


class TestSplitNodesImages(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertListEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = """
# This is H1 heading

## This is H2 heading

###### This is H6 heading
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><h1>This is H1 heading</h1><h2>This is H2 heading</h2><h6>This is H6 heading</h6></div>",
        )

    def test_quotes(self):
        md = """
> This is quote
> second one line
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><blockquote>This is quote\nsecond one line</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- item - new one
- item
- item
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ul><li>item - new one</li><li>item</li><li>item</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. item
2. item
3. item
"""
        self.assertEqual(
            markdown_to_html_node(md).to_html(),
            "<div><ol><li>item</li><li>item</li><li>item</li></ol></div>",
        )


class TestExtractTitle(unittest.TestCase):
    def test_extract_title(self):
        md = """
# This is title

## This is not
"""
        self.assertEqual(extract_title(md), "This is title")
