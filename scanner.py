# Individual token
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

# DFA class
class DFA:
    def __init__(self, scanner):
        self.scanner = scanner

    def scan_number(self):
        number_str = ""
        while self.scanner.current_char is not None and (
                self.scanner.current_char.isdigit() or self.scanner.current_char in '.-+eE'):
            number_str += self.scanner.current_char
            self.scanner.advance()
        return Token("NUM", number_str)

    def scan_string(self):
        string_str = ""
        self.scanner.advance()
        while self.scanner.current_char is not None and self.scanner.current_char != '"':
            if self.scanner.current_char == '\\':
                if self.scanner.peek() == '"':
                    string_str += '\\"'
                    self.scanner.advance()
                    self.scanner.advance()
                else:
                    string_str += self.scanner.current_char
                    self.scanner.advance()
            else:
                string_str += self.scanner.current_char
                self.scanner.advance()
        if self.scanner.current_char is None:
            print("ERROR: String was not closed")
        self.scanner.advance()
        return Token("STR", f'"{string_str}"')

    def scan_bool(self):
        if self.scanner.current_char == 't':
            if self.scanner.peek() == 'r' and self.scanner.input_str[self.scanner.current_pos + 2] == 'u' and \
                    self.scanner.input_str[self.scanner.current_pos + 3] == 'e':
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                return Token("BOOL", "true")
        elif self.scanner.current_char == 'f':
            if self.scanner.peek() == 'a' and self.scanner.input_str[self.scanner.current_pos + 2] == 'l' and \
                    self.scanner.input_str[self.scanner.current_pos + 3] == 's' and \
                    self.scanner.input_str[self.scanner.current_pos + 4] == 'e':
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                return Token("BOOL", "false")
        return None

    def scan_null(self):
        if self.scanner.current_char == 'n':
            if self.scanner.peek() == 'u' and self.scanner.input_str[self.scanner.current_pos + 2] == 'l' and \
                    self.scanner.input_str[self.scanner.current_pos + 3] == 'l':
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                self.scanner.advance()
                return Token(None, "NULL")
        return None

# Scanner class
class Scanner:
    # Initialize the scanner
    def __init__(self, input_str):
        self.input_str = input_str
        self.current_pos = 0
        self.current_char = self.input_str[self.current_pos] if self.current_pos < len(self.input_str) else None
        self.dfa = DFA(self)

    # Move to the next character
    def advance(self):
        self.current_pos += 1
        self.current_char = self.input_str[self.current_pos] if self.current_pos < len(self.input_str) else None

    # Look at the next character
    def peek(self):
        return self.input_str[self.current_pos + 1] if self.current_pos < len(self.input_str) - 1 else None

    # Look at previous character
    def back(self):
        return self.input_str[self.current_pos - 1] if self.current_pos > 0 else None

    # Ignore whitespace
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Scanning the character
    def scan_char(self):
        self.skip_whitespace()
        if self.current_char == '"':
            result = self.dfa.scan_string()
        elif self.current_char is None:
            return None
        elif self.current_char.isdigit() or self.current_char in '-+eE.':
            result = self.dfa.scan_number()
        elif self.current_char == 't' or self.current_char == 'f':
            result = self.dfa.scan_bool()
        elif self.current_char == 'n':
            result = self.dfa.scan_null()
        elif self.current_char == '[':
            self.advance()
            return Token(None, "[")
        elif self.current_char == ']':
            self.advance()
            return Token(None, "]")
        elif self.current_char == '{':
            self.advance()
            return Token(None, "{")
        elif self.current_char == '}':
            self.advance()
            return Token(None, "}")
        elif self.current_char == ':':
            self.advance()
            return Token(None, ":")
        elif self.current_char == ',':
            self.advance()
            return Token(None, ",")
        else:
            print("ERROR: Unexpected character: " + self.current_char)
            self.advance()
            return

        if result is None:
            print("ERROR: Failed to tokenize: " + self.current_char + self.peek())
            self.advance()
            return
        else:
            return result

    def scan_all(self):
        tokens = []
        while self.current_char is not None:
            token = self.scan_char()
            if token is not None:
                tokens.append(token)
        return tokens

if __name__ == "__main__":
    with open("test_11.txt", "r") as file:
        input_str = file.read()
    scanner = Scanner(input_str)
    tokens = scanner.scan_all()
    for token in tokens:
        if token.type is not None:
            print(f"<{token.type}, {token.value}>", end="\n")
        else:
            print(f"<{token.value}>", end="\n")
