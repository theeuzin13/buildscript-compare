from __future__ import annotations

NODE_NAMES_PT = {
    'program': 'Programa',
    'function_def': 'DefinicaoFuncao',
    'function_call': 'ChamadaFuncao',
    'params': 'Parametros',
    'body': 'Corpo',
    'declaration': 'Declaracao',
    'assignment': 'Atribuicao',
    'io_out': 'SaidaDados',
    'if_stmt': 'CondicionalSe',
    'condition': 'Condicao',
    'else_stmt': 'CondicionalSenao',
    'loop': 'Loop',
    'init': 'Inicializacao',
    'increment': 'Incremento',
    'return_stmt': 'Retorno',
    'expr': 'Expressao',
    'block': 'Bloco',
    'empty_stmt': 'ComandoVazio',
    'args': 'Argumentos',
    'var': 'Variavel',
    'io_in': 'EntradaDados',
    'function_call_expr': 'ChamadaFuncaoExpr',
    'unary_expr': 'ExpressaoUnaria',
    'unary_op': 'OperacaoUnaria',
    'string': 'CadeiaCaracteres',
    'number': 'Numero',
    'val_bool': 'ValorBooleano',
    'token': 'Token',
    'param': 'Parametro',
}


class ParseNode:
    def __init__(self, kind: str, value: str = '', children: list[ParseNode] | None = None):
        self.kind = kind
        self.value = value
        self.children = children or []

    def add(self, child: ParseNode) -> ParseNode:
        self.children.append(child)
        return self


class ParseError(RuntimeError):
    pass


class BuildScriptParser:

    def __init__(self, tokens: list[dict]):
        self.tokens = tokens
        self.pos = 0
        self.errors: list[str] = []

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
            raise ParseError(
                f"Erro Sintático: Esperado {kind}, encontrado {t['token']} "
                f"('{t.get('valor')}') na linha {t.get('line')}, coluna {t.get('col')}."
            )
        self.pos += 1
        return t

    def _consume(self, kind: str) -> bool:
        if self._at(kind):
            self._advance()
            return True
        return False

    STATEMENT_STARTERS = {'TYPE_VAR', 'IO_OUT', 'COND_IF', 'LOOP_INIT', 'KW_RETURN', 'FUNC_DEF'}

    def _sync(self):
        """Skip tokens until the next statement boundary for error recovery."""
        depth = 0
        while not self._at('EOF') and not self._at('PROG_END'):
            if self._at('SEMICOLON'):
                self._advance()
                return
            if depth == 0:
                if self._cur()['token'] in self.STATEMENT_STARTERS:
                    return
                if self._at('VAR') and self._peek().get('token') in ('OP_ATRIB', 'OP_UNARIO', 'SEMICOLON'):
                    return
                if self._at('ID_FUNC') and self._peek().get('token') == 'LPAREN':
                    return
            if self._at('LBRACE'):
                depth += 1
            elif self._at('RBRACE'):
                if depth == 0:
                    return
                depth -= 1
            self._advance()

    def get_errors(self) -> list[str]:
        return self.errors

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def parse(self) -> ParseNode:
        root = ParseNode('program')

        if self._at('PROG_INIT'):
            self._expect('PROG_INIT')
            self._expect('SEMICOLON')

        while not self._at('PROG_END') and not self._at('EOF'):
            try:
                if self._at('FUNC_DEF'):
                    root.add(self._parse_function_def())
                    continue
                root.add(self._parse_statement())
            except ParseError as e:
                self.errors.append(str(e))
                self._sync()

        if self._at('PROG_END'):
            self._expect('PROG_END')
            self._expect('SEMICOLON')
            self._expect('EOF')
        elif self._at('EOF'):
            self.errors.append(
                "Erro Sintático: Esperado POWER_OFF para finalizar o programa, "
                "encontrado final do arquivo (EOF)."
            )
        else:
            t = self._cur()
            self.errors.append(
                f"Erro Sintático: Esperado POWER_OFF para finalizar o programa, "
                f"encontrado '{t.get('valor')}' na linha {t.get('line')}, coluna {t.get('col')}."
            )

        return root

    def _parse_function_def(self) -> ParseNode:
        node = ParseNode('function_def')

        self._expect('FUNC_DEF')
        name_tok = self._expect('ID_FUNC')
        node.value = name_tok['valor']

        self._expect('LPAREN')
        params_node = ParseNode('params')
        if not self._at('RPAREN'):
            while True:
                if self._at('TYPE_VAR'):
                    self._advance()
                var_tok = self._expect('VAR')
                params_node.add(ParseNode('param', var_tok['valor']))
                if self._consume('COMMA'):
                    continue
                break
        self._expect('RPAREN')
        node.add(params_node)

        body_node = ParseNode('body')
        self._expect('LBRACE')
        self._parse_block_body(body_node)
        self._expect('RBRACE')
        node.add(body_node)

        return node

    def _parse_block_body(self, body_node: ParseNode):
        """Parse statements inside a brace block with error recovery."""
        while not self._at('RBRACE') and not self._at('EOF') and not self._at('PROG_END'):
            try:
                body_node.add(self._parse_statement())
            except ParseError as e:
                self.errors.append(str(e))
                self._sync()

    def _parse_statement(self) -> ParseNode:
        if self._at('TYPE_VAR'):
            type_tok = self._advance()
            var_tok = self._expect('VAR')
            node = ParseNode('declaration', f"{type_tok['valor']} {var_tok['valor']}")
            if self._consume('OP_ATRIB'):
                node.add(ParseNode('assignment', '=').add(self._parse_expr()))
            self._expect('SEMICOLON')
            return node

        if self._at('IO_OUT'):
            self._advance()
            node = ParseNode('io_out')
            args_node = ParseNode('args')
            self._expect('LPAREN')
            if not self._at('RPAREN'):
                while True:
                    args_node.add(self._parse_expr())
                    if self._consume('COMMA'):
                        continue
                    break
            self._expect('RPAREN')
            node.add(args_node)
            self._expect('SEMICOLON')
            return node

        if self._at('COND_IF'):
            self._advance()
            self._expect('LPAREN')
            cond = self._parse_expr()
            self._expect('RPAREN')

            if_node = ParseNode('if_stmt')
            if_node.add(ParseNode('condition').add(cond))

            if_body = ParseNode('body')
            self._expect('LBRACE')
            self._parse_block_body(if_body)
            self._expect('RBRACE')
            if_node.add(if_body)

            if self._at('COND_ELSE'):
                self._advance()
                else_body = ParseNode('body')
                self._expect('LBRACE')
                self._parse_block_body(else_body)
                self._expect('RBRACE')
                if_node.add(ParseNode('else_stmt').add(else_body))

            return if_node

        if self._at('LOOP_INIT'):
            self._advance()
            node = ParseNode('loop')

            self._expect('LPAREN')
            if not self._at('SEMICOLON'):
                if self._at('TYPE_VAR'):
                    type_tok = self._advance()
                    var_tok = self._expect('VAR')
                    init_node = ParseNode('init', f"{type_tok['valor']} {var_tok['valor']}")
                    if self._consume('OP_ATRIB'):
                        init_node.add(ParseNode('assignment', '=').add(self._parse_expr()))
                elif self._at('VAR'):
                    var_tok = self._advance()
                    self._expect('OP_ATRIB')
                    init_node = ParseNode('init', var_tok['valor'])
                    init_node.add(ParseNode('assignment', '=').add(self._parse_expr()))
                else:
                    t = self._cur()
                    raise ParseError(
                        f"Erro Sintático: Inicialização do loop inválida "
                        f"na linha {t.get('line')}, coluna {t.get('col')}."
                    )
                node.add(init_node)
            self._expect('SEMICOLON')

            if not self._at('SEMICOLON'):
                node.add(ParseNode('condition').add(self._parse_expr()))
            self._expect('SEMICOLON')

            if not self._at('RPAREN'):
                incr_node = ParseNode('increment')
                while not self._at('RPAREN'):
                    incr_node.add(ParseNode('token', self._advance()['valor']))
                node.add(incr_node)
            self._expect('RPAREN')

            body_node = ParseNode('body')
            self._expect('LBRACE')
            self._parse_block_body(body_node)
            self._expect('RBRACE')
            node.add(body_node)

            self._expect('LOOP_END')
            self._expect('SEMICOLON')
            return node

        if self._at('KW_RETURN'):
            self._advance()
            node = ParseNode('return_stmt')
            node.add(self._parse_expr())
            self._expect('SEMICOLON')
            return node

        if self._at('ID_FUNC') and self._peek()['token'] == 'LPAREN':
            name_tok = self._advance()
            node = ParseNode('function_call', name_tok['valor'])
            args_node = ParseNode('args')
            self._expect('LPAREN')
            if not self._at('RPAREN'):
                while True:
                    args_node.add(self._parse_expr())
                    if self._consume('COMMA'):
                        continue
                    break
            self._expect('RPAREN')
            node.add(args_node)
            self._expect('SEMICOLON')
            return node

        if self._at('VAR') and self._peek()['token'] == 'OP_ATRIB':
            var_tok = self._advance()
            op = self._advance()['valor']
            node = ParseNode('assignment', f"{var_tok['valor']} {op}")
            node.add(self._parse_expr())
            self._expect('SEMICOLON')
            return node

        if self._at('VAR') and self._peek()['token'] == 'OP_UNARIO':
            var_tok = self._advance()
            op = self._advance()['valor']
            node = ParseNode('unary_op', f"{var_tok['valor']}{op}")
            self._expect('SEMICOLON')
            return node

        if self._at('LBRACE'):
            node = ParseNode('block')
            self._expect('LBRACE')
            body = ParseNode('body')
            self._parse_block_body(body)
            self._expect('RBRACE')
            node.add(body)
            return node

        if self._consume('SEMICOLON'):
            return ParseNode('empty_stmt')

        t = self._cur()
        raise ParseError(
            f"Erro Sintático: Comando inesperado '{t.get('valor')}' ({t['token']}) "
            f"na linha {t.get('line')}, coluna {t.get('col')}."
        )

    def _parse_expr(self) -> ParseNode:
        return self._parse_or()

    def _parse_or(self) -> ParseNode:
        left = self._parse_and()
        while self._at('OP_LOGICO') and self._cur()['valor'] == 'OR':
            op = self._advance()['valor']
            right = self._parse_and()
            left = ParseNode('expr', op).add(left).add(right)
        return left

    def _parse_and(self) -> ParseNode:
        left = self._parse_not()
        while self._at('OP_LOGICO') and self._cur()['valor'] == 'AND':
            op = self._advance()['valor']
            right = self._parse_not()
            left = ParseNode('expr', op).add(left).add(right)
        return left

    def _parse_not(self) -> ParseNode:
        if self._at('OP_LOGICO') and self._cur()['valor'] == 'NOT':
            self._advance()
            return ParseNode('expr', 'NOT').add(self._parse_not())
        return self._parse_comparison()

    def _parse_comparison(self) -> ParseNode:
        left = self._parse_add()
        if self._at('OP_COMP'):
            op = self._advance()['valor']
            right = self._parse_add()
            left = ParseNode('expr', op).add(left).add(right)
        return left

    def _parse_add(self) -> ParseNode:
        left = self._parse_mul()
        while self._at('OP_ARIT') and self._cur()['valor'] in ['+', '-']:
            op = self._advance()['valor']
            right = self._parse_mul()
            left = ParseNode('expr', op).add(left).add(right)
        return left

    def _parse_mul(self) -> ParseNode:
        left = self._parse_unary()
        while self._at('OP_ARIT') and self._cur()['valor'] in ['*', '/']:
            op = self._advance()['valor']
            right = self._parse_unary()
            left = ParseNode('expr', op).add(left).add(right)
        return left

    def _parse_unary(self) -> ParseNode:
        if self._at('OP_UNARIO') and self._peek()['token'] == 'VAR':
            op = self._advance()['valor']
            var = self._advance()['valor']
            return ParseNode('unary_expr', f"{op}{var}")
        return self._parse_primary()

    def _parse_primary(self) -> ParseNode:
        t = self._cur()

        if t['token'] == 'STRING':
            self._advance()
            return ParseNode('string', t['valor'])

        if t['token'] == 'NUMBER':
            self._advance()
            return ParseNode('number', t['valor'])

        if t['token'] == 'VAL_BOOL':
            self._advance()
            return ParseNode('val_bool', t['valor'])

        if t['token'] == 'VAR':
            self._advance()
            return ParseNode('var', t['valor'])

        if t['token'] == 'IO_IN' and self._peek()['token'] == 'LPAREN':
            self._advance()
            self._expect('LPAREN')
            self._expect('RPAREN')
            return ParseNode('io_in', 'KEYBOARD()')

        if t['token'] == 'ID_FUNC' and self._peek()['token'] == 'LPAREN':
            name_tok = self._advance()
            node = ParseNode('function_call_expr', name_tok['valor'])
            args_node = ParseNode('args')
            self._expect('LPAREN')
            if not self._at('RPAREN'):
                while True:
                    args_node.add(self._parse_expr())
                    if self._consume('COMMA'):
                        continue
                    break
            self._expect('RPAREN')
            node.add(args_node)
            return node

        raise ParseError(
            f"Erro Sintático: Expressão inválida '{t.get('valor')}' ({t['token']}) "
            f"na linha {t.get('line')}, coluna {t.get('col')}."
        )

    @staticmethod
    def format_tree(node: ParseNode, indent: str = '', is_last: bool = True) -> str:
        prefix = '└── ' if is_last else '├── '
        name = NODE_NAMES_PT.get(node.kind, node.kind)
        label = f"{name}: {node.value}" if node.value else name

        lines = [f"{indent}{prefix}{label}"]

        child_indent = indent + ('    ' if is_last else '│   ')
        for i, child in enumerate(node.children):
            lines.append(BuildScriptParser.format_tree(child, child_indent, i == len(node.children) - 1))

        return '\n'.join(lines)
