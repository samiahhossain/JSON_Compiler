# Token representation
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"<{self.type}{', ' + str(self.value) if self.value else ''}>"

# Node of the parse tree
class Node:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        self.children = []

    def add_child(self, child):  # Creating children of the tree
        self.children.append(child)

    def print_tree(self, indent=0):
        print(" " * indent + f"{self.type} {self.value if self.value else ''}")  # The root (base case)
        for child in self.children:  # For all the children that is under the root
            child.print_output(indent + 4)  # Print their tree (glue case)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.position = -1
        self.advance()

    # Moving to the next token
    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    # Moving to the next token assuming the current token is a specified value
    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            print(f"ERROR: Expected {token_type}, got {self.current_token}")     # Error recovery
            self.advance()

    def parse(self):
        return self.value()

    # Parsing values
    def value(self):
        node = Node("value")
        token = self.current_token
        if token.type == "STR":
            self.eat("STR")
            node.add_child(Node("STRING", token.value))
        elif token.type == "NUM":
            self.eat("NUM")
            node.add_child(Node("NUMBER", token.value))
        elif token.type == "BOOL":
            self.eat("BOOL")
            node.add_child(Node("BOOLEAN", token.value))
        elif token.type == "NULL":
            self.eat("NULL")
            node.add_child(Node("NULL"))
        elif token.type == "{":
            node.add_child(self.parse_dict())
        elif token.type == "[":
            node.add_child(self.parse_list())
        else:
            print(f"ERROR: Unexpected token {token}")   # Error recovery
            self.advance()
            self.value()
        return node

    def parse_list(self):
        node = Node("list")
        self.eat("[")
        node.add_child(Node("["))

        # Content inside list
        if self.current_token and self.current_token.type != "]":
            node.add_child(self.value())
            while self.current_token and self.current_token.type == ",":
                self.eat(",")
                node.add_child(Node(","))
                node.add_child(self.value())
                # Add error recovery for trailing comma and no closing bracket

        self.eat("]")
        node.add_child(Node("]"))
        return node

    def parse_dict(self):
        node = Node("dict")
        self.eat("{")
        node.add_child(Node("{"))

        # Content inside dict
        if self.current_token and self.current_token.type != "}":
            node.add_child(self.parse_pair())
            while self.current_token and self.current_token.type == ",":
                self.eat(",")
                node.add_child(Node(","))
                node.add_child(self.parse_pair())
                # Add error recovery for trailing comma and no closing bracket

        self.eat("}")
        node.add_child(Node("}"))
        return node

    def parse_pair(self):
        # Add error recovery for trailing/leading colon, or wrong key
        key_token = self.current_token
        if key_token.type != "STR":
            # Error recovery
            print(f"ERROR: Pair key is {key_token.type}, not STRING")
            transformed_value = str(key_token.value)
            key_token = Token("STR", transformed_value)
        self.advance()
        self.eat(":")
        node = Node("pair")
        node.add_child(Node("STRING", key_token.value))
        node.add_child(Node(":"))
        node.add_child(self.value())
        return node

# Recognize tokens from file
def tokenize(file_path):
    tokens = []
    # Removing brackets to get token content
    matches = {
        "<STR,": "STR", "<NUM,": "NUM", "<BOOL,": "BOOL", "<NULL>": "NULL", "<[>": "[", "<]>": "]", "<{>": "{",
        "<}>": "}", "<,>": ",", "<:>": ":"
    }
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("<STR,") or line.startswith("<NUM,") or line.startswith("<BOOL,"):     # when there is an attached value
                extract = line[1:-1].split(", ")
                type = extract[0]
                value = extract[1]
                tokens.append(Token(matches[f"<{type},"], value))
            elif line in matches:
                tokens.append(Token(matches[line]))  # Adding token to list

    return tokens


if __name__ == "__main__":
    tokens = tokenize("test_12.txt")
    parser = Parser(tokens)
    parsing = parser.parse()
    print()
    parsing.print_tree()
