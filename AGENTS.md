# BuildScript Compiler — Agent Guide

## Run modes
- **CLI**: `python3 main.py builds/exemplo1.bs`
- **Tokens only**: `python3 main.py --tokens builds/exemplo1.bs`
- **Syntax tree**: `python3 main.py --syntax builds/exemplo1.bs`
- **Web IDE**: `python3 server.py` → http://localhost:8000

## Language quirks
- Variables start with `$`, functions with `!`
- Max identifier length: 30 chars; max number literal length: 15 digits
- Each program wrapped in `POWER_ON;` … `POWER_OFF;`
- Error messages and token labels in Portuguese (PT_BR)

## Project structure
- `main.py` — CLI entrypoint (reads file → `lexer.py` → `parser.py` → `interpreter.py`)
- `server.py` — HTTP server for the Web IDE (port 8000)
- `index.html` — Web IDE frontend
- `lexer.py` — Tokenizer (regex-based)
- `parser.py` — Syntax analyzer (produces tree via recursive descent)
- `interpreter.py` — Runtime interpreter (uses own recursive descent)
- `builds/` — 5 example `.bs` programs

## No tooling
- No tests, no CI, no linter/formatter config, no package manager
- Pure Python 3 stdlib — no dependencies to install
