from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class ParseError(RuntimeError):
    pass


@dataclass
class FunctionDef:
    name: str
    params: list[str]
    body_tokens: list[dict]


class BuildScriptInterpreter:
    """Interpreter bem simples para a linguagem (tokens customizados + sintaxe C-like).

    Suporta:
    - POWER_ON; ... POWER_OFF;
    - declaração de função: CPU !nome() { ... }
    - chamada de função: !nome();
    - variáveis: LABEL $x; $x = KEYBOARD();
    - saída: MONITOR("a", $x, "b");
    - entrada: KEYBOARD()
    """

    def __init__(self, tokens: list[dict]):
        self.tokens = tokens
        self.pos = 0
        self.functions: dict[str, FunctionDef] = {}
        self.globals: dict[str, Any] = {}

    # ----------------- helpers -----------------
    def _cur(self) -> dict:
        return self.tokens[self.pos]

    def _peek(self, n: int = 1) -> dict:
        i = self.pos + n
        if i < len(self.tokens):
            return self.tokens[i]
        return self.tokens[-1]

    def _at(self, kind: str) -> bool:
        return self._cur()['token'] == kind

    def _advance(self) -> dict:
        t = self._cur()
        self.pos += 1
        return t

    def _expect(self, kind: str) -> dict:
        t = self._cur()
        if t['token'] != kind:
            raise ParseError(f"Esperado {kind}, veio {t['token']} ({t.get('valor')}) em {t.get('line')}:{t.get('col')}")
        self.pos += 1
        return t

    def _consume(self, kind: str) -> bool:
        if self._at(kind):
            self._advance()
            return True
        return False

    # ----------------- entrypoint -----------------
    def run(self):
        self._expect('PROG_INIT')
        self._expect('SEMICOLON')

        while not self._at('PROG_END') and not self._at('EOF'):
            if self._at('FUNC_DEF'):
                self._parse_function_def()
                continue
            self._parse_statement(env=self.globals)

        self._expect('PROG_END')
        self._expect('SEMICOLON')
        self._expect('EOF')

    # ----------------- parsing: top-level -----------------
    def _parse_function_def(self):
        self._expect('FUNC_DEF')  # CPU
        name_tok = self._expect('ID_FUNC')  # !cadastrar_peca
        fn_name = name_tok['valor']

        self._expect('LPAREN')
        params: list[str] = []
        if not self._at('RPAREN'):
            # params estilo C: (LABEL $x, SLOT $y)
            while True:
                if self._at('TYPE_VAR'):
                    self._advance()  # tipo (não usamos ainda)
                var_tok = self._expect('VAR')
                params.append(var_tok['valor'])
                if self._consume('COMMA'):
                    continue
                break
        self._expect('RPAREN')

        body_tokens = self._collect_brace_block_tokens()
        self.functions[fn_name] = FunctionDef(name=fn_name, params=params, body_tokens=body_tokens)

    def _collect_brace_block_tokens(self) -> list[dict]:
        self._expect('LBRACE')
        depth = 1
        collected: list[dict] = []
        while depth > 0:
            t = self._advance()
            if t['token'] == 'LBRACE':
                depth += 1
            elif t['token'] == 'RBRACE':
                depth -= 1
                if depth == 0:
                    break
            collected.append(t)
        collected.append({'token': 'EOF', 'valor': '', 'line': self._cur().get('line'), 'col': self._cur().get('col')})
        return collected

    # ----------------- parsing/execution: statements -----------------
    def _parse_statement(self, env: dict[str, Any]) -> Any:
        if self._at('TYPE_VAR'):
            self._advance()
            var_tok = self._expect('VAR')
            if self._consume('OP_ATRIB'):
                rhs = self._parse_expr(env)
                self._expect('SEMICOLON')
                env[var_tok['valor']] = rhs
                return rhs
            env.setdefault(var_tok['valor'], None)
            self._expect('SEMICOLON')
            return None

        if self._at('IO_OUT'):
            self._advance()
            args = self._parse_call_args(env)
            self._expect('SEMICOLON')
            self._cmd_monitor(args)
            return None

        if self._at('COND_IF'):
            self._advance()
            self._expect('LPAREN')
            cond = self._parse_expr(env)
            self._expect('RPAREN')
            if_block = self._collect_brace_block_tokens()
            else_block = None
            if self._at('COND_ELSE'):
                self._advance()
                else_block = self._collect_brace_block_tokens()
            if self._truthy(cond):
                self._exec_token_stream(if_block, env)
            elif else_block is not None:
                self._exec_token_stream(else_block, env)
            return None

        if self._at('LOOP_INIT'):
            self._advance()
            self._expect('LPAREN')
            if not self._at('SEMICOLON'):
                if self._at('TYPE_VAR'):
                    self._advance()
                    v = self._expect('VAR')
                    if self._consume('OP_ATRIB'):
                        env[v['valor']] = self._parse_expr(env)
                    else:
                        env.setdefault(v['valor'], None)
                elif self._at('VAR'):
                    v = self._advance()
                    self._expect('OP_ATRIB')
                    env[v['valor']] = self._parse_expr(env)
                else:
                    raise ParseError("Init do RUNCOOLER inválido")
            self._expect('SEMICOLON')

            cond_start_pos = self.pos
            cond_tokens_snapshot_pos = cond_start_pos
            cond_expr = None
            if not self._at('SEMICOLON'):
                cond_expr = self._parse_expr(env)
            self._expect('SEMICOLON')

            incr_start_pos = self.pos
            incr_tokens: list[dict] = []
            if not self._at('RPAREN'):
                while not self._at('RPAREN'):
                    incr_tokens.append(self._advance())
            self._expect('RPAREN')

            body = self._collect_brace_block_tokens()
            self._expect('LOOP_END')
            self._expect('SEMICOLON')

            cond_tokens = self.tokens[cond_tokens_snapshot_pos:self._find_token_index_before_kind(cond_tokens_snapshot_pos, 'SEMICOLON')]

            while True:
                if cond_expr is not None:
                    if not self._truthy(self._eval_expr_from_tokens(cond_tokens, env)):
                        break
                self._exec_token_stream(body, env)
                if incr_tokens:
                    self._exec_incr_tokens(incr_tokens, env)
            return None

        if self._at('KW_RETURN'):
            self._advance()
            value = self._parse_expr(env)
            self._expect('SEMICOLON')
            raise _ReturnSignal(value)

        if self._at('ID_FUNC') and self._peek()['token'] == 'LPAREN':
            fn_tok = self._advance()
            args = self._parse_call_args(env)
            self._expect('SEMICOLON')
            return self._call_function(fn_tok['valor'], args)

        if self._at('VAR') and self._peek()['token'] == 'OP_ATRIB':
            var_tok = self._advance()
            op = self._advance()['valor']
            rhs = self._parse_expr(env)
            self._expect('SEMICOLON')
            if op == '=':
                env[var_tok['valor']] = rhs
                return rhs
            cur = env.get(var_tok['valor'])
            if op == '+=':
                env[var_tok['valor']] = (cur if cur is not None else 0) + rhs
            elif op == '-=':
                env[var_tok['valor']] = (cur if cur is not None else 0) - rhs
            elif op == '*=':
                env[var_tok['valor']] = (cur if cur is not None else 0) * rhs
            elif op == '/=':
                env[var_tok['valor']] = (cur if cur is not None else 0) / rhs
            else:
                raise ParseError(f"Operador de atribuição '{op}' não suportado")
            return env[var_tok['valor']]

        if self._at('VAR') and self._peek()['token'] == 'OP_UNARIO':
            var_tok = self._advance()
            op = self._advance()['valor']
            self._expect('SEMICOLON')
            cur = env.get(var_tok['valor'])
            if cur is None:
                cur = 0
            if op == '++':
                env[var_tok['valor']] = cur + 1
            elif op == '--':
                env[var_tok['valor']] = cur - 1
            else:
                raise ParseError(f"Operador unário '{op}' inválido")
            return env[var_tok['valor']]

        if self._at('LBRACE'):
            block = self._collect_brace_block_tokens()
            local = dict(env)
            self._exec_token_stream(block, local)
            env.update(local)
            return None

        if self._consume('SEMICOLON'):
            return None

        t = self._cur()
        raise ParseError(f"Comando inesperado: {t['token']} ({t.get('valor')}) em {t.get('line')}:{t.get('col')}")

    def _parse_expr(self, env: dict[str, Any]) -> Any:
        return self._parse_or(env)

    def _parse_or(self, env: dict[str, Any]) -> Any:
        left = self._parse_and(env)
        while self._at('OP_LOGICO') and self._cur()['valor'] == 'OR':
            self._advance()
            right = self._parse_and(env)
            left = self._truthy(left) or self._truthy(right)
        return left

    def _parse_and(self, env: dict[str, Any]) -> Any:
        left = self._parse_not(env)
        while self._at('OP_LOGICO') and self._cur()['valor'] == 'AND':
            self._advance()
            right = self._parse_not(env)
            left = self._truthy(left) and self._truthy(right)
        return left

    def _parse_not(self, env: dict[str, Any]) -> Any:
        if self._at('OP_LOGICO') and self._cur()['valor'] == 'NOT':
            self._advance()
            return not self._truthy(self._parse_not(env))
        return self._parse_comparison(env)

    def _parse_comparison(self, env: dict[str, Any]) -> Any:
        left = self._parse_add(env)
        if self._at('OP_COMP'):
            op = self._advance()['valor']
            right = self._parse_add(env)
            if op == '==':
                return left == right
            if op == '!=':
                return left != right
            if op == '>':
                return left > right
            if op == '<':
                return left < right
            if op == '>=':
                return left >= right
            if op == '<=':
                return left <= right
            raise ParseError(f"Operador de comparação inválido: {op}")
        return left

    def _parse_add(self, env: dict[str, Any]) -> Any:
        left = self._parse_mul(env)
        while self._at('OP_ARIT') and self._cur()['valor'] in ['+', '-']:
            op = self._advance()['valor']
            right = self._parse_mul(env)
            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    left = str(left) + str(right)
                else:
                    left = left + right
            else:
                left = left - right
        return left

    def _parse_mul(self, env: dict[str, Any]) -> Any:
        left = self._parse_unary(env)
        while self._at('OP_ARIT') and self._cur()['valor'] in ['*', '/']:
            op = self._advance()['valor']
            right = self._parse_unary(env)
            left = left * right if op == '*' else left / right
        return left

    def _parse_unary(self, env: dict[str, Any]) -> Any:
        if self._at('OP_UNARIO') and self._peek()['token'] == 'VAR':
            op = self._advance()['valor']
            var = self._advance()['valor']
            cur = env.get(var) or 0
            env[var] = cur + 1 if op == '++' else cur - 1
            return env[var]
        return self._parse_primary(env)

    def _parse_primary(self, env: dict[str, Any]) -> Any:
        t = self._cur()

        if t['token'] == 'STRING':
            self._advance()
            return self._unquote(t['valor'])

        if t['token'] == 'NUMBER':
            self._advance()
            return float(t['valor']) if '.' in t['valor'] else int(t['valor'])

        if t['token'] == 'VAL_BOOL':
            self._advance()
            return True if t['valor'] == 'GREENSCREEN' else False

        if t['token'] == 'VAR':
            self._advance()
            return env.get(t['valor'])

        if t['token'] == 'IO_IN' and self._peek()['token'] == 'LPAREN':
            self._advance()
            self._expect('LPAREN')
            self._expect('RPAREN')
            return input()

        if t['token'] == 'ID_FUNC' and self._peek()['token'] == 'LPAREN':
            fn_tok = self._advance()
            args = self._parse_call_args(env)
            return self._call_function(fn_tok['valor'], args)

        raise ParseError(f"Expressão inválida: {t['token']} ({t.get('valor')}) em {t.get('line')}:{t.get('col')}")

    @staticmethod
    def _truthy(v: Any) -> bool:
        return bool(v)

    def _find_token_index_before_kind(self, start: int, kind: str) -> int:
        i = start
        while i < len(self.tokens) and self.tokens[i]['token'] != kind:
            i += 1
        return i

    def _eval_expr_from_tokens(self, tokens: list[dict], env: dict[str, Any]) -> Any:
        saved_tokens, saved_pos = self.tokens, self.pos
        try:
            self.tokens = tokens + [{'token': 'EOF', 'valor': '', 'line': 0, 'col': 0}]
            self.pos = 0
            return self._parse_expr(env)
        finally:
            self.tokens, self.pos = saved_tokens, saved_pos

    def _exec_incr_tokens(self, incr_tokens: list[dict], env: dict[str, Any]):
        if len(incr_tokens) == 2 and incr_tokens[0]['token'] == 'VAR' and incr_tokens[1]['token'] == 'OP_UNARIO':
            var = incr_tokens[0]['valor']
            op = incr_tokens[1]['valor']
            cur = env.get(var) or 0
            env[var] = cur + 1 if op == '++' else cur - 1
            return
        if len(incr_tokens) == 2 and incr_tokens[0]['token'] == 'OP_UNARIO' and incr_tokens[1]['token'] == 'VAR':
            op = incr_tokens[0]['valor']
            var = incr_tokens[1]['valor']
            cur = env.get(var) or 0
            env[var] = cur + 1 if op == '++' else cur - 1
            return
        if len(incr_tokens) >= 3 and incr_tokens[0]['token'] == 'VAR' and incr_tokens[1]['token'] == 'OP_ATRIB':
            var = incr_tokens[0]['valor']
            rhs = self._eval_expr_from_tokens(incr_tokens[2:], env)
            env[var] = rhs
            return
        raise ParseError("Incremento do RUNCOOLER não suportado")

    def _parse_call_args(self, env: dict[str, Any]) -> list[Any]:
        self._expect('LPAREN')
        args: list[Any] = []
        if not self._at('RPAREN'):
            while True:
                args.append(self._parse_expr(env))
                if self._consume('COMMA'):
                    continue
                break
        self._expect('RPAREN')
        return args

    def _cmd_monitor(self, args: list[Any]):
        out = ''.join('' if a is None else str(a) for a in args)
        print(out)

    def _call_function(self, fn_name: str, args: list[Any]) -> Any:
        fn = self.functions.get(fn_name)
        if not fn:
            raise ParseError(f"Função não encontrada: {fn_name}")

        local_env: dict[str, Any] = dict(self.globals)
        for i, param in enumerate(fn.params):
            local_env[param] = args[i] if i < len(args) else None

        try:
            self._exec_token_stream(fn.body_tokens, local_env)
        except _ReturnSignal as r:
            self.globals.update({k: v for k, v in local_env.items() if k in self.globals})
            return r.value

        self.globals.update({k: v for k, v in local_env.items() if k in self.globals})
        return None

    def _exec_token_stream(self, tokens: list[dict], env: dict[str, Any]):
        saved_tokens, saved_pos = self.tokens, self.pos
        try:
            self.tokens = tokens
            self.pos = 0
            while not self._at('EOF'):
                self._parse_statement(env)
        finally:
            self.tokens, self.pos = saved_tokens, saved_pos

    @staticmethod
    def _unquote(s: str) -> str:
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
        return bytes(s, 'utf-8').decode('unicode_escape')


class _ReturnSignal(Exception):
    def __init__(self, value: Any):
        self.value = value