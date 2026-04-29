from lexer import BuildScriptLexer
from interpreter import BuildScriptInterpreter
import sys

def load_script(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    script_path = sys.argv[1] if len(sys.argv) > 1 else "builds/example.bs"
    code = load_script(script_path)

    lexer = BuildScriptLexer(code)
    tokens = list(lexer.tokenize())

    interpreter = BuildScriptInterpreter(tokens)
    interpreter.run()

if __name__ == "__main__":
    main()