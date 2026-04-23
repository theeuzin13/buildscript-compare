import re

class BuildScriptLexer:
    def __init__(self, code):
        self.code = code
        token_specification = [
            ('COMMENT',   r'//.*'),
            ('NUMBER',    r'\d+'),
            ('STRING',    r'"[^"]*"'),
            ('OP_REL',    r'==|!=|>=|<=|>|<'),
            ('ASSIGN',    r'='),
            ('LBRACE',    r'\{'),
            ('RBRACE',    r'\}'),
            ('COLON',     r':'),
            ('COMMA',     r','),
            ('SEMICOLON', r';'),
            ('PC',        r'\bpc\b'),
            ('CPU',       r'\bcpu\b'),
            ('MOTHERBOARD', r'\bmotherboard\b'),
            ('RAM',       r'\bram\b'),
            ('GPU',       r'\bgpu\b'),
            ('STORAGE',   r'\bstorage\b'),
            ('PSU',       r'\bpsu\b'),
            ('CASE',      r'\bcase\b'),
            ('COOLER',    r'\bcooler\b'),
            ('CHECK',     r'\bcheck\b'),
            ('SHOW',      r'\bshow\b'),
            ('IF',        r'\bif\b'),
            ('BOOLEAN',   r'\b(true|false)\b'),
            ('ID',        r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('NEWLINE',   r'\n'),
            ('SKIP',      r'[ \t]+'),
            ('MISMATCH',  r'.'),
        ]
        
        self.regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

    def tokenize(self):
        tokens = []
        for mo in re.finditer(self.regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'SKIP' or kind == 'NEWLINE':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'Caractere inesperado: {value}')
            tokens.append({'token': kind, 'valor': value})
        return tokens