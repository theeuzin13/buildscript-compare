class BuildScriptInterpreter:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.builds = {}

    def get_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def run(self):
        while self.pos < len(self.tokens):
            token = self.get_token()
            if token is None:
                break
            if token['token'] == 'PC':
                self.parse_pc_declaration()
            elif token['token'] == 'SHOW':
                self.advance()
                build_token = self.get_token()
                if build_token:
                    self.cmd_show(build_token['valor'])
                    self.advance()
            elif token['token'] == 'CHECK':
                self.advance()
                build_token = self.get_token()
                if build_token:
                    self.cmd_check(build_token['valor'])
                    self.advance()
            else:
                self.advance()

    def parse_pc_declaration(self):
        self.advance()
        name_token = self.get_token()
        build_name = name_token['valor'] if name_token else 'unnamed'
        self.advance()
        token = self.get_token()
        if token and token['token'] == 'LBRACE':
            self.advance()
            pc_info = {}
            while True:
                token = self.get_token()
                if token is None or token['token'] == 'RBRACE':
                    break
                if token['token'] in ['CPU', 'MOTHERBOARD', 'RAM', 'GPU', 'STORAGE', 'PSU', 'CASE', 'COOLER']:
                    key = token['token'].lower()
                    self.advance()
                    eq_token = self.get_token()
                    if eq_token and eq_token['token'] == 'ASSIGN':
                        self.advance()
                        value_token = self.get_token()
                        if value_token and value_token['token'] in ['STRING', 'NUMBER']:
                            pc_info[key] = value_token['valor']
                            self.advance()
                        if self.get_token() and self.get_token()['token'] == 'SEMICOLON':
                            self.advance()
                    else:
                        self.advance()
                else:
                    self.advance()
            self.advance()
            self.builds[build_name] = pc_info
            print(f"PC declarado: {build_name} -> {pc_info}")

    def cmd_show(self, build_name):
        build = self.builds.get(build_name)
        if build:
            print(f"Build '{build_name}':")
            for k, v in build.items():
                print(f"  {k}: {v}")
        else:
            print(f"Build '{build_name}' não encontrada.")

    def cmd_check(self, build_name):
        build = self.builds.get(build_name)

        if not build:
            print(f"Build '{build_name}' não encontrada.")
            return

        required_fields = ['cpu', 'motherboard', 'ram', 'storage', 'case', 'psu', 'cooler']
        missing = []

        for field in required_fields:
            if field not in build or not build[field]:
                missing.append(field)

        if missing:
            print(f"Build '{build_name}' incompatível.")
            print("Componentes ausentes:")
            for m in missing:
                print(f" - {m}")
        else:
            print(f"Build '{build_name}' compatível.")