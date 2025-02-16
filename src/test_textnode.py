import unittest

from textnode import TextNode, TextType, split_nodes_delimiter

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node with different text", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_type(self):
        node = TextNode("This is a text node with different text type", TextType.BOLD)
        node2 = TextNode("This is a text node with different text type", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_url_eq_none(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node.url, None)

    def test_valid_split(self):
        """Test splitting a text node with a valid matching delimiter."""
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_no_delimiter(self):
        """Test that text without a delimiter remains unchanged."""
        node = TextNode("This is plain text with no formatting", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [TextNode("This is plain text with no formatting", TextType.TEXT)]
        self.assertEqual(new_nodes, expected)

    def test_nested_delimiters(self):
        """Test multiple inline elements in a single string."""
        node = TextNode("Here is `code` and *italic* text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" and *italic* text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delimiter_at_start_and_end(self):
        """Test when the text starts and ends with the delimiter."""
        node = TextNode("`entire block`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("entire block", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_multiple_delimiters(self):
        """Test multiple occurrences of the delimiter in the text."""
        node = TextNode("Here is `first` and `second` code", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("first", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("second", TextType.CODE),
            TextNode(" code", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_raises_exception_on_unmatched_delimiter(self):
        """Test that an unmatched delimiter raises a ValueError."""
        node = TextNode("This is `invalid markdown", TextType.TEXT)
        
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(str(context.exception), "Invalid Markdown syntax: Unmatched '`' in text 'This is `invalid markdown'")

    def test_mixed_text_nodes(self):
        """Test that non-text nodes remain unchanged."""
        text_node = TextNode("Normal `code` text", TextType.TEXT)
        other_node = TextNode("Unchanged node", TextType.BOLD)
        
        new_nodes = split_nodes_delimiter([text_node, other_node], "`", TextType.CODE)

        expected = [
            TextNode("Normal ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.TEXT),
            TextNode("Unchanged node", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)


if __name__ == "__main__":
    unittest.main()
