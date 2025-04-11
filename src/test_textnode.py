import unittest

from textnode import TextNode, TextType, split_nodes_delimiter, extract_markdown_images, extract_markdown_links

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

    def test_extract_markdown_images_single(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "Check this ![cat](https://i.imgur.com/cat.jpg) and ![dog](https://i.imgur.com/dog.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("cat", "https://i.imgur.com/cat.jpg"), ("dog", "https://i.imgur.com/dog.png")],
            matches
        )

    def test_extract_markdown_images_no_match(self):
        text = "There are no images here, just text."
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_links_single(self):
        matches = extract_markdown_links(
            "Here is a [link](https://example.com) for testing."
        )
        self.assertListEqual(
            [("link", "https://example.com")],
            matches
        )

    def test_extract_markdown_links_and_images(self):
        text = "A [link](https://example.com) and ![image](https://img.com/img.png)"
        links = extract_markdown_links(text)
        images = extract_markdown_images(text)
        self.assertListEqual([("link", "https://example.com")], links)
        self.assertListEqual([("image", "https://img.com/img.png")], images)

    def test_split_nodes_image_single(self):
        node = TextNode("Look at this ![cat](https://img.com/cat.png)", TextType.TEXT)
        from textnode import split_nodes_image
        result = split_nodes_image([node])

        expected = [
            TextNode("Look at this ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://img.com/cat.png"),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_image_multiple(self):
        node = TextNode("One ![img1](url1) two ![img2](url2)", TextType.TEXT)
        from textnode import split_nodes_image
        result = split_nodes_image([node])

        expected = [
            TextNode("One ", TextType.TEXT),
            TextNode("img1", TextType.IMAGE, "url1"),
            TextNode(" two ", TextType.TEXT),
            TextNode("img2", TextType.IMAGE, "url2"),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_image_preserves_non_text_nodes(self):
        from textnode import split_nodes_image
        text_node = TextNode("Before ![img](url)", TextType.TEXT)
        image_node = TextNode("Already image", TextType.IMAGE, "existing-url")
        result = split_nodes_image([text_node, image_node])

        expected = [
            TextNode("Before ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url"),
            TextNode("Already image", TextType.IMAGE, "existing-url"),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_link_single(self):
        node = TextNode("Click [here](https://example.com) please", TextType.TEXT)
        from textnode import split_nodes_link
        result = split_nodes_link([node])

        expected = [
            TextNode("Click ", TextType.TEXT),
            TextNode("here", TextType.LINK, "https://example.com"),
            TextNode(" please", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_link_multiple(self):
        node = TextNode("Visit [Google](https://google.com) or [Bing](https://bing.com) now", TextType.TEXT)
        from textnode import split_nodes_link
        result = split_nodes_link([node])

        expected = [
            TextNode("Visit ", TextType.TEXT),
            TextNode("Google", TextType.LINK, "https://google.com"),
            TextNode(" or ", TextType.TEXT),
            TextNode("Bing", TextType.LINK, "https://bing.com"),
            TextNode(" now", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_split_nodes_link_preserves_non_text_nodes(self):
        from textnode import split_nodes_link
        text_node = TextNode("Check [this](url)", TextType.TEXT)
        code_node = TextNode("`not a link`", TextType.CODE)
        result = split_nodes_link([text_node, code_node])

        expected = [
            TextNode("Check ", TextType.TEXT),
            TextNode("this", TextType.LINK, "url"),
            TextNode("`not a link`", TextType.CODE),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_bold(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("This is **bold** text.")
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text.", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_italic(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("This is _italic_ text.")
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text.", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_code(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("Here is some `code` in text.")
        expected = [
            TextNode("Here is some ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" in text.", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_image(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("A cute ![cat](https://img.com/cat.jpg) picture.")
        expected = [
            TextNode("A cute ", TextType.TEXT),
            TextNode("cat", TextType.IMAGE, "https://img.com/cat.jpg"),
            TextNode(" picture.", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_link(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("Check [this site](https://example.com).")
        expected = [
            TextNode("Check ", TextType.TEXT),
            TextNode("this site", TextType.LINK, "https://example.com"),
            TextNode(".", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_multiple_code(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("Use `print()` and `len()` functions.")
        expected = [
            TextNode("Use ", TextType.TEXT),
            TextNode("print()", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("len()", TextType.CODE),
            TextNode(" functions.", TextType.TEXT),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_malformed_bold(self):
        from textnode import text_to_textnodes
        with self.assertRaises(ValueError):
            text_to_textnodes("This is **broken")

    def test_text_to_textnodes_nested_unparsed(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("**Bold _not italic inside_**")
        expected = [
            TextNode("Bold _not italic inside_", TextType.BOLD),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_bold_and_link(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("**Bold** and a [link](https://example.com)")
        expected = [
            TextNode("Bold", TextType.BOLD),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_image_and_code(self):
        from textnode import text_to_textnodes
        result = text_to_textnodes("Look at ![dog](https://img.com/dog.png) and `snippet`")
        expected = [
            TextNode("Look at ", TextType.TEXT),
            TextNode("dog", TextType.IMAGE, "https://img.com/dog.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("snippet", TextType.CODE),
        ]
        self.assertEqual(result, expected)

    def test_text_to_textnodes_all_formats(self):
        from textnode import text_to_textnodes
        text = "Here is **bold**, _italic_, and `code` with ![img](url) and a [link](link)"
        result = text_to_textnodes(text)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(", ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(", and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" with ", TextType.TEXT),
            TextNode("img", TextType.IMAGE, "url"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "link"),
        ]
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
