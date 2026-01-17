import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHtmlNode(unittest.TestCase):
    def test_node(self):
        node = HTMLNode("p", "This is a paragraph.")
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "This is a paragraph.")

    def test_children(self):
        li = HTMLNode(tag="li", value="element")
        ul = HTMLNode(tag="ul", children=[li, li])
        self.assertEqual(ul.tag, "ul")
        self.assertIn(li, ul.children)

    def test_props_to_html(self):
        node = HTMLNode(
            tag="a",
            value="This is a link.",
            props={"href": "http://example.com", "target": "_blank"},
        )
        props = node.props_to_html()
        self.assertEqual(props, ' href="http://example.com" target="_blank"')


class TestLeafNode(unittest.TestCase):
    def test_raw_text(self):
        node = LeafNode(tag=None, value="This is raw text.")
        self.assertEqual(node.to_html(), "This is raw text.")

    def test_link(self):
        node = LeafNode(
            tag="a", value="Click me!", props={"href": "https://google.com"}
        )
        self.assertEqual(node.to_html(), '<a href="https://google.com">Click me!</a>')

    def test_bold(self):
        node = LeafNode(tag="b", value="bold")
        self.assertEqual(node.to_html(), "<b>bold</b>")


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(), "<div><span><b>grandchild</b></span></div>"
        )

    def test_parent_missing_tag(self):
        with self.assertRaises(ValueError):
            ParentNode(None, ["a"]).to_html()

    def test_parent_missing_children(self):
        with self.assertRaises(ValueError):
            ParentNode("a", []).to_html()


if __name__ == "__main__":
    unittest.main()
