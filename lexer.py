import re

TOKEN_NAMES_PT = {
    'PROG_INIT': 'InicioPrograma',
    'PROG_END': 'FimPrograma',
    'TYPE_VAR': 'TipoVariavel',
    'VAL_BOOL': 'ValorBooleano',
    'COND_IF': 'SeCondicional',
    'COND_ELSE': 'SenaoCondicional',
    'LOOP_INIT': 'InicioLoop',
    'LOOP_END': 'FimLoop',
    'FUNC_DEF': 'DefinicaoFuncao',
    'KW_RETURN': 'RetornoFuncao',
    'IO_OUT': 'SaidaDados',
    'IO_IN': 'EntradaDados',
    'ID_FUNC': 'IdentificadorFuncao',
    'VAR': 'Variavel',
    'NUMBER': 'Numero',
    'STRING': 'CadeiaCaracteres',
    'OP_UNARIO': 'OperadorUnario',
    'OP_COMP': 'OperadorComparacao',
    'OP_ATRIB': 'OperadorAtribuicao',
    'OP_LOGICO': 'OperadorLogico',
    'OP_ARIT': 'OperadorAritmetico',
    'LBRACE': 'AbreChaves',
    'RBRACE': 'FechaChaves',
    'LPAREN': 'AbreParenteses',
    'RPAREN': 'FechaParenteses',
    'COMMA': 'Virgula',
    'SEMICOLON': 'PontoVirgula',
    'ID': 'Identificador',
}


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
            ('MALFORMED_VAR', r'\$[a-zA-Z0-9_]+'),
            ('MALFORMED_FLOAT', r'\d+\.[a-zA-Z_][a-zA-Z0-9_]*'),
            ('MALFORMED_ID', r'\b\d+[a-zA-Z_][a-zA-Z0-9_]*\b'),
            ('NUMBER', r'\d+(?:\.\d+)?'),
            ('STRING', r'"[^"\\]*(?:\\.[^"\\]*)*"'),
            ('UNCLOSED_STRING', r'"[^"\\]*(?:\\.[^"\\]*)*'),

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

            if kind == 'MALFORMED_VAR':
                raise RuntimeError(
                    f"Erro Léxico: Identificador/variável mal formado: '{value}' na linha {line}, coluna {col}."
                )

            if kind == 'MALFORMED_ID':
                raise RuntimeError(
                    f"Erro Léxico: Identificador/variável mal formado: '{value}' na linha {line}, coluna {col}."
                )

            if kind == 'MALFORMED_FLOAT':
                raise RuntimeError(
                    f"Erro Léxico: Número mal formado: '{value}' na linha {line}, coluna {col}."
                )

            if kind == 'UNCLOSED_STRING':
                raise RuntimeError(
                    f"Erro Léxico: Cadeia de caracteres (string) mal formada ou não fechada: '{value}' na linha {line}, coluna {col}."
                )

            if kind == 'MISMATCH':
                if value == '@':
                    raise RuntimeError(
                        f"Erro Léxico: Símbolo não pertencente ao conjunto de símbolos terminais da linguagem: '@' na linha {line}, coluna {col}."
                    )
                raise RuntimeError(
                    f"Erro Léxico: Símbolo não pertencente ao conjunto de símbolos terminais da linguagem: '{value}' na linha {line}, coluna {col}."
                )
            if kind in ['VAR', 'ID_FUNC', 'ID']:
                clean_len = len(value[1:]) if kind in ['VAR', 'ID_FUNC'] else len(value)
                if clean_len > 30:
                    raise RuntimeError(
                        f"Erro Léxico: Tamanho do identificador '{value}' excede o limite de 30 caracteres na linha {line}, coluna {col}."
                    )
            if kind == 'NUMBER':
                if len(value) > 15:
                    raise RuntimeError(
                        f"Erro Léxico: Tamanho excessivo do número '{value}' (máximo de 15 dígitos) na linha {line}, coluna {col}."
                    )

            tokens.append({'token': kind, 'valor': value, 'line': line, 'col': col})
            col += len(value)

        tokens.append({'token': 'EOF', 'valor': '', 'line': line, 'col': col})
        return tokens

    @staticmethod
    def format_tokens(tokens: list[dict]) -> str:
        formatted = []
        for t in tokens:
            if t['token'] == 'EOF':
                continue
            pt_name = TOKEN_NAMES_PT.get(t['token'], t['token'])
            formatted.append(f"Linha: {t['line']} - Coluna {t['col']} - Token:<{pt_name}, {t['valor']}>")
        return "\n".join(formatted)