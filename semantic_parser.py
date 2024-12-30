# Token representation
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"<{self.type}{', ' + str(self.value) if self.value else ''}>"


# Errors list
errors = []


# Node of the abstract syntax tree
class Node:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
        self.children = []

    def add_child(self, child):  # Creating children of the tree
        self.children.append(child)

    # Finding latest comma
    def latest_comma_child(self):
        if self.type == "," and all(child.type != "," for child in self.children):  # Base case
            return self
        deepest_comma = None
        for child in self.children:
            child_comma = child.latest_comma_child()  # Glue case
            if child_comma:
                if not deepest_comma or self.depth_level(child_comma) > self.depth_level(deepest_comma):
                    deepest_comma = child_comma
        return deepest_comma

    # Helper method
    def depth_level(self, node, current_depth=0):
        if self == node:  # Base case
            return current_depth
        for child in self.children:
            child_depth = child.depth_level(node, current_depth + 1)  # Glue case
            if child_depth != -1:
                return child_depth
        return -1

    # Output
    def print_output(self, file, indent=0):
        if len(errors) == 0:  # when no errors
            if self.type != "":
                file.write(" " * indent + f"{self.type} {self.value if self.value else ''}\n")  # base case
            else:
                indent -= 5
            for child in self.children:
                child.print_output(file, indent + 5)  # glue case
        else:
            for error in errors:
                file.write(f"{error}\n")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.position = -1
        self.advance()
        self.keys_stack = [{}]
        self.comma_stack = []

    # Move ahead
    def advance(self):
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

    def previous(self):
        return self.tokens[self.position - 1] if self.position > 0 else None

    def next(self):
        return self.tokens[self.position + 1] if self.position < len(self.tokens) - 1 else None

    # Move if current is what was expected
    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()

    def parse(self):
        return self.value()

    # Parsing values
    def value(self):
        node = Node("")
        token = self.current_token
        if token.type == "STR":
            # Error checking
            if token.value == "\"true\"" or token.value == "\"false\"":
                errors.append(f"TYPE 7 ERROR AT {token.value}: Reserved Words as Strings.")
            self.eat("STR")
            node.add_child(Node(token.value))
        elif token.type == "NUM":
            # Error checking
            if token.value.startswith("0") and len(token.value) > 1 and token.value[1] != '.':
                errors.append(f"TYPE 3 ERROR AT {token.value}: Invalid Numbers.")
            elif token.value.startswith("+"):
                errors.append(f"TYPE 3 ERROR AT {token.value}: Invalid Numbers.")
            if token.value.count('.') == 1 and (token.value.startswith('.') or token.value.endswith('.')):
                errors.append(f"TYPE 1 ERROR AT {token.value}: Invalid Decimal Numbers.")
            self.eat("NUM")
            node.add_child(Node(token.value))
        elif token.type == "BOOL":
            self.eat("BOOL")
            node.add_child(Node(token.value))
        elif token.type == "NULL":
            self.eat("NULL")
            node.add_child(Node("NULL"))
        elif token.type == "{":
            node.add_child(self.parse_dict())
        elif token.type == "[":
            node.add_child(self.parse_list())
        return node

    # Parsing list
    def parse_list(self):
        if self.previous() and self.previous().type == ",":
            node = Node("list")
        else:
            node = Node("")
        self.eat("[")
        types = set()

        # Content inside list
        if self.current_token and self.current_token.type != "]":
            types.add(self.current_token.type)
            value_node = self.value()
            if self.current_token and self.current_token.type != ",":
                node.add_child(value_node)
            else:
                comma = Node(",")
                node.add_child(comma)
                comma.add_child(value_node)

            current_comma = node.latest_comma_child()
            self.comma_stack.append(current_comma)

            while self.current_token and self.current_token.type == ",":
                # comma
                self.eat(",")
                comma = Node(",")
                if self.next() and self.next().type != "]":
                    current_comma.add_child(comma)
                    current_comma = comma

                # additional value
                if self.current_token.type != "[" and self.current_token.type != "]":
                    types.add(self.current_token.type)
                value_node = self.value()

                # Error checking
                if len(types) > 1:
                    errors.append(f"TYPE 6 ERROR AT {value_node.value}: Inconsistent Types in List Elements.")
                current_comma.add_child(value_node)

        self.eat("]")
        if self.comma_stack:
            self.comma_stack.pop()
        return node

    # Parsing dict
    def parse_dict(self):
        if self.previous() and self.previous().type == ":":
            node = Node("dict")
        else:
            node = Node("")
        self.eat("{")
        self.keys_stack.append({})

        # Content inside dict
        if self.current_token and self.current_token.type != "}":
            # first pair
            pair_node = self.parse_pair()
            if self.current_token and self.current_token.type != ",":
                node.add_child(pair_node)
            else:
                comma = Node(",")
                node.add_child(comma)
                comma.add_child(pair_node)

            current_comma = node.latest_comma_child()
            self.comma_stack.append(current_comma)

            while self.current_token and self.current_token.type == ",":
                # comma
                self.eat(",")
                comma = Node(",")
                if self.tokens[self.position + 3].type != "}":
                    current_comma.add_child(comma)
                    current_comma = comma

                # additional pair
                pair_node = self.parse_pair()
                current_comma.add_child(pair_node)

        self.eat("}")
        self.keys_stack.pop()
        if self.comma_stack:
            self.comma_stack.pop()
        return node

    # Parsing pair
    def parse_pair(self):
        key_token = self.current_token

        # Error checking
        if key_token.value in ["\"true\"", "\"false\""]:
            errors.append(f"TYPE 4 ERROR AT {key_token.value}: Reserved Words as Dictionary Key.")
        if key_token.value in ["\"\"", "\" \""]:
            errors.append(f"TYPE 2 ERROR AT {key_token.value}: Empty Key.")
        if key_token.value in self.keys_stack[-1]:
            errors.append(f"TYPE 5 ERROR AT {key_token.value}: No Duplicate Keys in Dictionary.")
        self.keys_stack[-1][key_token.value] = True
        self.advance()

        self.eat(":")
        node = Node(":")
        node.add_child(Node(key_token.value))
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
            if line.startswith("<STR,") or line.startswith("<NUM,") or line.startswith(
                    "<BOOL,"):  # when there is an attached value
                extract = line[1:-1].split(", ")
                type = extract[0]
                value = extract[1]
                tokens.append(Token(matches[f"<{type},"], value))
            elif line in matches:
                tokens.append(Token(matches[line]))  # Adding token to list

    return tokens


# Main program
if __name__ == "__main__":
    tokens = tokenize("test_01.txt")
    parser = Parser(tokens)
    parsing = parser.parse()
    with open("output.txt", "w") as output_file:
        parsing.print_output(output_file)
    print("Written to output.txt!")
