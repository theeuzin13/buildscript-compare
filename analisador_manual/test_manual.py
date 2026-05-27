"""Bateria de testes automatizada para o ManualLexer."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from lexer_manual import ManualLexer, LexerError

BUILDS = os.path.join(os.path.dirname(__file__), '..', 'builds')

passed = 0
failed = 0

def ok(label):
    global passed
    passed += 1
    print(f"  ✅  {label}")

def err(label, msg=""):
    global failed
    failed += 1
    print(f"  ❌  {label}" + (f": {msg}" if msg else ""))


print("=" * 60)
print("  BATERIA DE TESTES — ANALISADOR LÉXICO MANUAL")
print("=" * 60)

# ── Exemplos válidos (.bs files) ────────────────────────────────
print("\n[1] Exemplos válidos:")
for i in range(1, 6):
    path = os.path.join(BUILDS, f'exemplo{i}.bs')
    code = open(path, encoding='utf-8').read()
    try:
        toks = ManualLexer(code).tokenize()
        ok(f"exemplo{i}.bs — {len(toks) - 1} token(s) reconhecidos")
    except LexerError as e:
        err(f"exemplo{i}.bs", str(e))

# ── Erros léxicos esperados ──────────────────────────────────────
print("\n[2] Erros léxicos esperados:")

error_cases = [
    ("Símbolo inválido (@)",          "POWER_ON; SLOT $x = @; POWER_OFF;"),
    ("Número mal formado (2a3)",       "POWER_ON; SLOT $x = 2a3; POWER_OFF;"),
    ("Variável mal formada ($1a)",     "POWER_ON; SLOT $1a = 8; POWER_OFF;"),
    ("Número mal formado (2.a3)",      "POWER_ON; SLOT $x = 2.a3; POWER_OFF;"),
    ("Número excessivo (>15 dígitos)", "POWER_ON; SLOT $x = 5555555555555555; POWER_OFF;"),
    ("String não fechada",             'POWER_ON; MONITOR("nao fechou); POWER_OFF;'),
    ("Bloco aberto não fechado",       "POWER_ON; CPU !f() { SLOT $x = 1; POWER_OFF;"),
]

for label, code in error_cases:
    try:
        ManualLexer(code).tokenize()
        err(label, "erro NÃO foi detectado!")
    except LexerError as e:
        ok(f"{label}\n       → {e}")

# ── Resumo ───────────────────────────────────────────────────────
print()
print("=" * 60)
print(f"  Resultado: {passed} passou(ram)  |  {failed} falhou(aram)")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
