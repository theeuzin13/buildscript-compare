from lexer import BuildScriptLexer
from parser import BuildScriptParser
from interpreter import BuildScriptInterpreter
import sys

def load_script(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def _print_errors(label: str, errors: list[str]):
    if errors:
        plural = "s" if len(errors) > 1 else ""
        print(f"{label} ({len(errors)} erro{plural} encontrado{plural}):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)

def main():
    script_path = sys.argv[2] if len(sys.argv) > 2 else "builds/exemplo1.bs"

    if len(sys.argv) > 1 and sys.argv[1] == "--tokens":
        code = load_script(script_path)
        lexer = BuildScriptLexer(code)
        tokens = list(lexer.tokenize())
        print(BuildScriptLexer.format_tokens(tokens))
        _print_errors("Erros Léxicos", lexer.get_errors())
        if lexer.has_errors():
            sys.exit(1)

    elif len(sys.argv) > 1 and sys.argv[1] == "--syntax":
        code = load_script(script_path)
        lexer = BuildScriptLexer(code)
        tokens = list(lexer.tokenize())
        parser = BuildScriptParser(tokens)
        tree = parser.parse()
        lex_errors = lexer.get_errors()
        syn_errors = parser.get_errors()
        if lex_errors:
            _print_errors("Erros Léxicos", lex_errors)
        if syn_errors:
            _print_errors("Erros Sintáticos", syn_errors)
        if lex_errors or syn_errors:
            sys.exit(1)
        print(BuildScriptParser.format_tree(tree))

    else:
        script_path = sys.argv[1] if len(sys.argv) > 1 else "builds/exemplo1.bs"
        code = load_script(script_path)
        lexer = BuildScriptLexer(code)
        tokens = list(lexer.tokenize())
        parser = BuildScriptParser(tokens)
        parser.parse()
        lex_errors = lexer.get_errors()
        syn_errors = parser.get_errors()
        if lex_errors:
            _print_errors("Erros Léxicos", lex_errors)
        if syn_errors:
            _print_errors("Erros Sintáticos", syn_errors)
        if lex_errors or syn_errors:
            sys.exit(1)
        interpreter = BuildScriptInterpreter(tokens)
        interpreter.run()

if __name__ == "__main__":
    main()