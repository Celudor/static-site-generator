import os
import re
import shutil

from blocktype import BlockType, block_to_block_type
from htmlnode import LeafNode, ParentNode
from textnode import TextNode, TextType


def extract_markdown_images(text):
    return re.findall(r"!\[([\w\d\- ]+)\]\(([\w\d:\/\.-]+)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes):
    new_nodes = []
    for node in old_nodes:
        images = extract_markdown_images(node.text)
        if not images:
            new_nodes.append(node)
            continue
        image = images[0]
        section = node.text.split(f"![{image[0]}]({image[1]})", maxsplit=1)
        if len(section) >= 1 and section[0]:
            new_nodes.append(TextNode(section[0], TextType.TEXT))
        new_nodes.append(TextNode(image[0], TextType.IMAGE, image[1]))
        if len(section) == 2 and section[1]:
            new_nodes.extend(split_nodes_image([TextNode(section[1], TextType.TEXT)]))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for node in old_nodes:
        links = extract_markdown_links(node.text)
        if not links:
            new_nodes.append(node)
            continue
        link = links[0]
        section = node.text.split(f"[{link[0]}]({link[1]})", maxsplit=1)
        if len(section) >= 1 and section[0]:
            new_nodes.append(TextNode(section[0], TextType.TEXT))
        new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
        if len(section) == 2 and section[1]:
            new_nodes.extend(split_nodes_link([TextNode(section[1], TextType.TEXT)]))
    return new_nodes


def text_node_to_html_node(text_node):
    if text_node.text_type == TextType.TEXT:
        return LeafNode(tag=None, value=text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode(tag="b", value=text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode(tag="i", value=text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode(tag="code", value=text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode(tag="a", value=text_node.text, props={"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode(
            tag="img", value=None, props={"src": text_node.url, "alt": text_node.text}
        )


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        splited = node.text.split(delimiter)
        for i in range(len(splited)):
            if splited[i] == "":
                continue
            if i % 2 == 0:
                new_nodes.append(TextNode(splited[i], TextType.TEXT))
            else:
                new_nodes.append(TextNode(splited[i], text_type))
    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes


def markdown_to_blocks(markdown):
    blocks = [block.strip() for block in markdown.split("\n\n")]
    return blocks


def text_to_htmlnodes(text):
    htmlnodes = []
    for node in text_to_textnodes(text):
        htmlnodes.append(text_node_to_html_node(node))
    return htmlnodes


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    p = []
    for block in blocks:
        if not block:
            continue
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            p.append(ParentNode("p", text_to_htmlnodes(block.replace("\n", " "))))
        elif block_type == BlockType.HEADING:
            parts = re.findall(r"(^#{1,6} )(.*)", block)
            count = 0
            for _ in parts[0][0][:-1]:
                count += 1
            p.append(ParentNode(f"h{count}", text_to_htmlnodes(parts[0][1])))
        elif block_type == BlockType.QUOTE:
            p.append(
                ParentNode(
                    "blockquote",
                    text_to_htmlnodes(
                        block.replace("> ", "").replace("\n", " ").strip()
                    ),
                )
            )
        elif block_type == BlockType.UNORDERED_LIST:
            c = []
            for line in block.splitlines():
                if line.startswith("- "):
                    c.append(
                        ParentNode("li", text_to_htmlnodes(line.replace("- ", "", 1)))
                    )
            p.append(ParentNode("ul", c))
        elif block_type == BlockType.ORDERED_LIST:
            c = []
            for line in block.splitlines():
                match = re.match(r"(^\d{1,}\. )(.*)", line)
                if match:
                    c.append(ParentNode("li", text_to_htmlnodes(match.group(2))))
            p.append(ParentNode("ol", c))
        elif block_type == BlockType.CODE:
            lines = block.splitlines()
            p.append(
                ParentNode(
                    "pre",
                    [
                        ParentNode(
                            "code",
                            [
                                text_node_to_html_node(
                                    TextNode(
                                        "\n".join(lines[1:-1]) + "\n", TextType.TEXT
                                    )
                                )
                            ],
                        )
                    ],
                )
            )

    return ParentNode("div", p)


def copy_dir(source, target):
    if os.path.exists(target):
        shutil.rmtree(target)
    os.mkdir(target)
    for item in os.listdir(source):
        path = os.path.join(source, item)
        if os.path.isfile(path):
            shutil.copy(path, target)
        else:
            copy_dir(path, os.path.join(target, item))


def extract_title(markdown):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line.replace("#", "", 1).strip()
    raise Exception("Document does not contain header")


def generate_page(from_path, template_path, dest_path, basepath="/"):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        md = f.read()
    with open(template_path, "r") as f:
        template = f.read()
    html = markdown_to_html_node(md).to_html()
    title = extract_title(md)
    page = (
        template.replace("{{ Title }}", title)
        .replace("{{ Content }}", html)
        .replace('href="/', f'href="{basepath}')
        .replace('src="/', f'src="{basepath}')
    )
    with open(dest_path, "w") as f:
        f.write(page)


def generate_pages_recursive(
    dir_path_content, template_path, dest_dir_path, basepath="/"
):
    for item in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, item)
        if os.path.isfile(source_path):
            basename = os.path.splitext(item)
            if basename[1] == ".md":
                dest_path = os.path.join(dest_dir_path, f"{basename[0]}.html")
                generate_page(source_path, template_path, dest_path, basepath)
        else:
            dest_path = os.path.join(dest_dir_path, item)
            os.mkdir(dest_path)
            generate_pages_recursive(source_path, template_path, dest_path, basepath)
