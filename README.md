# BuildScript - Linguagem Temática de Hardware

Um interpretador completo para a **BuildScript**, uma linguagem de programação acadêmica com sintaxe baseada em peças e conceitos de hardware. Desenvolvido para a disciplina de **Compiladores**.

---

## 🚀 Como Executar (Passo a Passo)

O projeto possui duas formas de execução: **Modo Gráfico (Web IDE)** e **Modo Terminal (CLI)**. 
Requisito: **Python 3** instalado na máquina.

### Opção 1: Modo Gráfico (Recomendado)
Inicia uma IDE visual no seu navegador, permitindo editar, tokenizar e interpretar o código.

**No Windows:**
1. Abra o Prompt de Comando (CMD) ou PowerShell na pasta do projeto.
2. Execute o comando: `python server.py`
3. Abra o navegador e acesse: `http://localhost:8000`

**No Linux / macOS:**
1. Abra o terminal na pasta do projeto.
2. Execute o comando: `python3 server.py`
3. Abra o navegador e acesse: `http://localhost:8000`

### Opção 2: Modo Terminal (CLI)
Executa arquivos `.bs` diretamente no terminal.

**No Windows:**
1. Abra o CMD ou PowerShell na pasta do projeto.
2. Execute o interpretador passando o arquivo `.bs` desejado, exemplo:
   `python main.py builds/exemplo1.bs`

**No Linux / macOS:**
1. Abra o terminal na pasta do projeto.
2. Execute o arquivo, exemplo:
   `python3 main.py builds/exemplo1.bs`

*(Você pode testar também os arquivos `exemplo2.bs` até `exemplo5.bs`)*

---

## 📂 Arquivos Essenciais

*   **`server.py` & `index.html`**: Servidor local e interface gráfica (Web IDE) para utilizar o compilador visualmente.
*   **`main.py`**: Ponto de entrada do sistema via terminal. Lê o arquivo, aciona o analisador léxico e depois o interpretador.
*   **`lexer.py`**: **Analisador Léxico**. Lê o texto bruto e agrupa os caracteres em tokens significativos (com suporte a expressões regulares).
*   **`interpreter.py`**: **Interpretador / Analisador Sintático**. Avalia a árvore de tokens, controla o fluxo de execução, variáveis e funções.
*   **`builds/`**: Pasta com os programas de exemplo em BuildScript.

---

## 🔌 Vocabulário Básico

| Comando em BuildScript | Equivalente | O que faz |
| :--- | :--- | :--- |
| `POWER_ON;` / `POWER_OFF;` | `{ }` ou `main()` | Inicia e finaliza a execução do programa. |
| `SLOT` / `VOLTAGE` / `LABEL` | `int` / `float` / `string` | Declaração de variáveis (inteiro, decimal e texto). |
| `LED` | `bool` | Variável booleana (`GREENSCREEN` = True, `BLUESCREEN` = False). |
| `RUNCIRCUIT` / `SHORTCIRCUIT`| `if` / `else` | Estrutura condicional. |
| `RUNCOOLER` / `STOPCOOLER` | `for` / `while` | Início e fim de laços de repetição. |
| `CPU` / `EJECT` | `function` / `return`| Declaração de função e retorno de valor. |
| `MONITOR` / `KEYBOARD` | `print()` / `input()` | Saída e entrada de dados na tela. |

*(Nota: Variáveis sempre começam com `$` e funções com `!`)*