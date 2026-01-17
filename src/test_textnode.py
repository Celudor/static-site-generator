import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node 2", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_url(self):
        node = TextNode("test", TextType.LINK, "http://example.com")
        self.assertEqual(node.url, "http://example.com")

    def test_url_none(self):
        node = TextNode("test", TextType.TEXT)
        self.assertIsNone(node.url)


if __name__ == "__main__":
    unittest.main()
