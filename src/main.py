from textnode import TextType, TextNode

def main():
    node = TextNode("it's a node", TextType.ITALIC, "https://boot.dev")
    print(node)

main()
