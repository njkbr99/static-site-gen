import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextType, TextNode

class TestHTMLNode(unittest.TestCase):
    """Basic HTMLNode class tests"""
    def test_init_defaults(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {})  

    def test_props_to_html_empty(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")  # Should return an empty string

    def test_props_to_html_with_props(self):
        node = HTMLNode(props={"href": "https://example.com", "target": "_blank"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com" target="_blank"')

    def test_repr(self):
        node = HTMLNode(tag="p", value="Hello", props={"class": "text-bold"})
        expected_repr = "HTMLNode(tag=p, value=Hello, children=[], props={'class': 'text-bold'})"
        self.assertEqual(repr(node), expected_repr)

    def test_to_html_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()

    """LeafNode class tests"""
    def test_leafnode_init_defaults(self):
        node = LeafNode(None, None)
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertEqual(node.children, [])
        self.assertEqual(node.props, {})

    def test_valid_leafnode(self):
        node = LeafNode("p", "This is a LeafNode", {"class": "text"})
        expected_html = '<p class="text">This is a LeafNode</p>'
        self.assertEqual(node.to_html(), expected_html)

    def test_leafnode_without_value_raises_error(self):
        with self.assertRaises(ValueError) as context:
            LeafNode(tag="p", value=None).to_html()

        self.assertEqual(str(context.exception), "All leaf nodes must have a value")

    def test_leafnode_without_tag(self):
        node = LeafNode(tag=None, value="Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leafnode_link_with_props(self):
        node = LeafNode(tag="a", value="Click me", props={"href": "https://example.com", "target": "_blank"})
        expected_html = '<a href="https://example.com" target="_blank">Click me</a>'
        self.assertEqual(node.to_html(), expected_html)

    """ParentNode class tests"""
    def test_valid_parentnode(self):
        child1 = LeafNode(tag="span", value="Hello")
        child2 = LeafNode(tag="span", value="World")
        parent = ParentNode(tag="div", children=[child1, child2])

        expected_html = "<div><span>Hello</span><span>World</span></div>"
        self.assertEqual(parent.to_html(), expected_html)

    def test_parentnode_without_tag_raises_error(self):
        child = LeafNode(tag="p", value="Test")
        with self.assertRaises(ValueError) as context:
            ParentNode(tag=None, children=[child]).to_html()
        self.assertEqual(str(context.exception), "All parent nodes must have a tag")

    def test_parentnode_without_children_raises_error(self):
        with self.assertRaises(ValueError) as context:
            ParentNode(tag="div", children=[]).to_html()
        self.assertEqual(str(context.exception), "All parent nodes must have children")

    def test_parentnode_with_multiple_children(self):
        child1 = LeafNode(tag="p", value="Paragraph 1")
        child2 = LeafNode(tag="p", value="Paragraph 2")
        parent = ParentNode(tag="section", children=[child1, child2])

        expected_html = "<section><p>Paragraph 1</p><p>Paragraph 2</p></section>"
        self.assertEqual(parent.to_html(), expected_html)

    def test_parentnode_with_props(self):
        child = LeafNode(tag="span", value="Text")
        parent = ParentNode(tag="div", children=[child], props={"class": "container"})

        expected_html = '<div class="container"><span>Text</span></div>'
        self.assertEqual(parent.to_html(), expected_html)

    def test_nested_parentnode(self):
        inner_child1 = LeafNode(tag="li", value="Item 1")
        inner_child2 = LeafNode(tag="li", value="Item 2")
        inner_parent = ParentNode(tag="ul", children=[inner_child1, inner_child2])

        outer_parent = ParentNode(tag="div", children=[inner_parent])

        expected_html = "<div><ul><li>Item 1</li><li>Item 2</li></ul></div>"
        self.assertEqual(outer_parent.to_html(), expected_html)

    """TextNode to HTMLNode convertion tests"""
    def test_text_node_to_html_node_text(self):
        text_node = TextNode(text="Hello, world!", text_type=TextType.TEXT)
        html_node = text_node_to_html_node(text_node)
        
        self.assertIsInstance(html_node, LeafNode)
        self.assertIsNone(html_node.tag)
        self.assertEqual(html_node.value, "Hello, world!")
        self.assertEqual(html_node.props, {})
    
    def test_text_node_to_html_node_text_bold(self):
        text_node = TextNode(text="Bold text", text_type=TextType.BOLD)
        html_node = text_node_to_html_node(text_node)

        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")
        self.assertEqual(html_node.props, {})

    def test_text_node_to_html_node_text_italic(self):
        text_node = TextNode(text="Italic text", text_type=TextType.ITALIC)
        html_node = text_node_to_html_node(text_node)

        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")
        self.assertEqual(html_node.props, {})

    def test_text_node_to_html_node_text_code(self):
        text_node = TextNode(text="print('Hello')", text_type=TextType.CODE)
        html_node = text_node_to_html_node(text_node)

        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('Hello')")
        self.assertEqual(html_node.props, {})

    def test_text_node_to_html_node_link(self):
        text_node = TextNode(text="Click here", text_type=TextType.LINK, url="https://example.com")
        html_node = text_node_to_html_node(text_node)

        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_text_node_to_html_node_image(self):
        text_node = TextNode(text="An image", text_type=TextType.IMAGE, url="https://example.com/image.jpg")
        html_node = text_node_to_html_node(text_node)

        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "https://example.com/image.jpg", "alt": "An image"})

    def test_text_node_to_html_node_exception(self):
        class FakeTextType:
            UNKNOWN = "unknown"

        text_node = TextNode(text="Unsupported", text_type=FakeTextType.UNKNOWN)

        with self.assertRaises(Exception) as context:
            text_node_to_html_node(text_node)

        self.assertEqual(str(context.exception), "Text type from TextNode is not supported by HTMLNode")

if __name__ == "__main__":
    unittest.main()
