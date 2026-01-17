class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        props = ""
        if self.props:
            for prop in self.props:
                props += f' {prop}="{self.props[prop]}"'
        return props

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.childern}, {self.props})"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)

    def to_html(self):
        if not self.value:
            raise ValueError("Leaf node must have a value")
        if not self.tag:
            return self.value
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"


class ParentNode(HTMLNode):
    def __init__(self, tag, childern, props=None):
        super().__init__(tag, None, childern, props)

    def to_html(self):
        if not self.tag:
            raise ValueError("Tag is required")
        if not self.children:
            raise ValueError("Children/s is/are required")
        return f"<{self.tag}{self.props_to_html()}>{''.join([n.to_html() for n in self.children])}</{self.tag}>"
