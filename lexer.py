import re


class BuildScriptLexer:

    def __init__(self, code: str):
        self.code = code

        token_specification = [
            ('COMMENT', r'//.*'),

            ('PROG_INIT', r'\bPOWER_ON\b'),
            ('PROG_END', r'\bPOWER_OFF\b'),

            ('TYPE_VAR', r'\b(SLOT|VOLTAGE|LABEL|LED)\b'),

            ('VAL_BOOL', r'\b(GREENSCREEN|BLUESCREEN)\b'),

            ('COND_IF', r'\bRUNCIRCUIT\b'),
            ('COND_ELSE', r'\bSHORTCIRCUIT\b'),
            ('LOOP_INIT', r'\bRUNCOOLER\b'),
            ('LOOP_END', r'\bSTOPCOOLER\b'),

            ('FUNC_DEF', r'\bCPU\b'),
            ('KW_RETURN', r'\bEJECT\b'),

            ('IO_OUT', r'\bMONITOR\b'),
            ('IO_IN', r'\bKEYBOARD\b'),

            ('ID_FUNC', r'![a-zA-Z_][a-zA-Z0-9_]*'),
            ('VAR', r'\$[a-z_][a-z0-9_]*'),

            ('NUMBER', r'\d+(?:\.\d+)?'),
            ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),

            ('OP_UNARIO', r'\+\+|--'),
            ('OP_COMP', r'==|!=|>=|<=|>|<'),
            ('OP_ATRIB', r'\+=|-=|\*=|/=|='),
            ('OP_LOGICO', r'\b(AND|OR|NOT)\b'),
            ('OP_ARIT', r'\+|-|\*|/'),

            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('COMMA', r','),
            ('SEMICOLON', r';'),

            ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),

            ('NEWLINE', r'\n'),
            ('SKIP', r'[ \t\r]+'),
            ('MISMATCH', r'.'),
        ]

        self.regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    def tokenize(self):
        tokens = []
        line = 1
        col = 1
        for mo in re.finditer(self.regex, self.code):
            kind = mo.lastgroup
            value = mo.group()

            if kind == 'NEWLINE':
                line += 1
                col = 1
                continue

            if kind == 'SKIP' or kind == 'COMMENT':
                col += len(value)
                continue

            if kind == 'MISMATCH':
                raise RuntimeError(f'Caractere inesperado: {value} (linha {line}, coluna {col})')

            tokens.append({'token': kind, 'valor': value, 'line': line, 'col': col})
            col += len(value)

        tokens.append({'token': 'EOF', 'valor': '', 'line': line, 'col': col})
        return tokens