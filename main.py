from lexer import BuildScriptLexer
from interpreter import BuildScriptInterpreter
import sys

def load_script(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--tokens":
        script_path = sys.argv[2] if len(sys.argv) > 2 else "builds/exemplo1.bs"
        try:
            code = load_script(script_path)
            lexer = BuildScriptLexer(code)
            tokens = list(lexer.tokenize())
            print(BuildScriptLexer.format_tokens(tokens))
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        script_path = sys.argv[1] if len(sys.argv) > 1 else "builds/exemplo1.bs"
        try:
            code = load_script(script_path)
            lexer = BuildScriptLexer(code)
            tokens = list(lexer.tokenize())
            interpreter = BuildScriptInterpreter(tokens)
            interpreter.run()
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()