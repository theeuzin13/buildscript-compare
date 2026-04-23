from lexer import BuildScriptLexer
from interpreter import BuildScriptInterpreter

def load_script(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    code = load_script("builds/workstation.bs")

    lexer = BuildScriptLexer(code)
    tokens = list(lexer.tokenize())

    interpreter = BuildScriptInterpreter(tokens)
    interpreter.run()

if __name__ == "__main__":
    main()