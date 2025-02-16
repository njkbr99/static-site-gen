from enum import Enum

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other_node):
        return True if self.text == other_node.text and self.text_type == other_node.text_type and self.url == other_node.url else False

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        parts = old_node.text.split(delimiter)

        if len(parts) == 1:
            new_nodes.append(old_node)
            continue

        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid Markdown syntax: Unmatched '{delimiter}' in text '{old_node.text}'")

        is_special = False
        for part in parts:
            if part:
                new_nodes.append(TextNode(part, text_type if is_special else TextType.TEXT))
            is_special = not is_special

    return new_nodes

