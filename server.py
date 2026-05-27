import http.server
import socketserver
import json
import sys
import io
import traceback
import builtins
from lexer import BuildScriptLexer
from interpreter import BuildScriptInterpreter

PORT = 8000


class BuildScriptIDEHandler(http.server.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open("index.html", "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            except Exception as e:
                self.wfile.write(f"Erro ao carregar index.html: {e}".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/run":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                req = json.loads(post_data.decode('utf-8'))
                code = req.get("code", "")
                inputs = req.get("inputs", [])
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"JSON inválido: {e}"}).encode('utf-8'))
                return

            input_idx = 0
            def mock_input():
                nonlocal input_idx
                if input_idx < len(inputs):
                    val = inputs[input_idx]
                    input_idx += 1
                    return val
                return "Componente Padrão"

            original_input = builtins.input
            builtins.input = mock_input

            captured_stdout = io.StringIO()
            sys.stdout = captured_stdout

            tokens_formatted = ""
            execution_output = ""
            error_message = None

            try:
                lexer = BuildScriptLexer(code)
                tokens = list(lexer.tokenize())
                tokens_formatted = BuildScriptLexer.format_tokens(tokens)

                interpreter = BuildScriptInterpreter(tokens)
                interpreter.run()

                execution_output = captured_stdout.getvalue()
            except Exception as e:
                error_message = str(e)
                execution_output = captured_stdout.getvalue()
            finally:
                sys.stdout = sys.__stdout__
                builtins.input = original_input

            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            
            resp = {
                "success": error_message is None,
                "tokens": tokens_formatted,
                "output": execution_output,
                "error": error_message
            }
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()


def main():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), BuildScriptIDEHandler) as httpd:
        print("==================================================")
        print("   💻 IDE LOCAL DO BUILDSCRIPT INICIADA! 💻")
        print(f"   Acesse no seu navegador: http://localhost:{PORT}")
        print("   Para encerrar o servidor, pressione: CTRL+C")
        print("==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado. Até mais!")


if __name__ == "__main__":
    main()
