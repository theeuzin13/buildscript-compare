# BuildScript — Linguagem Temática de Hardware

Interpretador completo para a **BuildScript**, uma linguagem de programação acadêmica com sintaxe baseada em peças e conceitos de hardware. Desenvolvido para a disciplina de **Compiladores**.

---

## IDE Utilizada no Desenvolvimento

O projeto foi desenvolvido no **Visual Studio Code (VS Code)**, com as seguintes extensões auxiliares:

- **Python** (Microsoft) — suporte a sintaxe, IntelliSense e execução de scripts `.py`
- **Live Server** / abertura direta do `index.html` para testes da interface web durante o desenvolvimento

---

## Passo a Passo: Como Executar o Projeto

O projeto oferece duas formas de execução. Requisito único: **Python 3** instalado na máquina.

### Opção 1 — Web IDE (Recomendado)

Inicia um servidor local e abre uma IDE visual no navegador para editar, tokenizar e interpretar código BuildScript.

**Windows (CMD ou PowerShell):**
```
python server.py
```

**Linux / macOS:**
```
python3 server.py
```

Depois, acesse no navegador: `http://localhost:8000`

A interface permite:
- Escrever código manualmente (com numeração de linhas em tempo real)
- Carregar um dos 5 exemplos prontos pelo menu suspenso
- Abrir e salvar arquivos `.bs` do disco
- Visualizar o **Console**, a **Tabela de Tokens**, a **Árvore Sintática** e os **Erros** em abas separadas

---

### Opção 2 — Linha de Comando (CLI)

Executa um arquivo `.bs` diretamente no terminal, imprimindo a saída no console.

**Windows:**
```
python main.py builds/exemplo1.bs
```

**Linux / macOS:**
```
python3 main.py builds/exemplo1.bs
```

Os arquivos de exemplo disponíveis são `exemplo1.bs` até `exemplo5.bs`, localizados na pasta `builds/`.

---

## Arquivos do Projeto

| Arquivo | Função |
| :--- | :--- |
| `server.py` | Servidor HTTP local (porta 8000) que expõe a Web IDE |
| `index.html` | Interface gráfica da IDE (editor, abas de resultado, manual) |
| `lexer.py` | Analisador léxico — converte o código-fonte em tokens |
| `parser.py` | Analisador sintático — constrói a Árvore Sintática Abstrata (ASA) |
| `interpreter.py` | Interpretador — executa a ASA, gerencia variáveis, funções e fluxo |
| `main.py` | Ponto de entrada para execução via terminal (CLI) |
| `builds/` | Programas de exemplo escritos em BuildScript |

---

## Vocabulário da Linguagem

| Token BuildScript | Equivalente | Descrição |
| :--- | :--- | :--- |
| `POWER_ON;` | `main()` / `{` | Inicia a execução do programa (obrigatório) |
| `POWER_OFF;` | `}` | Finaliza a execução do programa (obrigatório) |
| `SLOT` | `int` | Tipo inteiro |
| `VOLTAGE` | `float` | Tipo ponto flutuante |
| `LABEL` | `string` | Tipo cadeia de caracteres |
| `LED` | `bool` | Tipo booleano |
| `GREENSCREEN` / `BLUESCREEN` | `true` / `false` | Valores booleanos |
| `CPU` | `function` | Define uma função |
| `EJECT` | `return` | Retorna valor de uma função |
| `RUNCIRCUIT` | `if` | Condicional |
| `SHORTCIRCUIT` | `else` | Senão |
| `RUNCOOLER` / `STOPCOOLER` | `for` | Loop com inicialização, condição e incremento |
| `MONITOR(...)` | `print()` | Saída de dados |
| `KEYBOARD()` | `input()` | Leitura de entrada |

> Variáveis sempre começam com `$` (ex: `$total`). Chamadas de função começam com `!` (ex: `!calcular()`).

---

## Regras Sintáticas Adotadas (Gramática)

A gramática abaixo descreve a estrutura formal da linguagem BuildScript, conforme implementada em `parser.py`.

### Estrutura geral do programa

```
programa       → POWER_ON ; declaração_global* POWER_OFF ;

declaração_global → def_funcao
                  | comando
```

### Definição de função

```
def_funcao     → CPU ID_FUNC ( params ) { corpo }

params         → ε
               | TYPE_VAR VAR ( , TYPE_VAR VAR )*

corpo          → comando*
```

### Comandos

```
comando        → declaração
               | atribuição
               | op_unaria
               | saída
               | condicional
               | loop
               | retorno
               | chamada_funcao
               | bloco
               | comando_vazio

declaração     → TYPE_VAR VAR ( = expr )? ;
atribuição     → VAR OP_ATRIB expr ;          (OP_ATRIB: = += -= *= /=)
op_unaria      → VAR OP_UNARIO ;              (OP_UNARIO: ++ --)
saída          → MONITOR ( args ) ;
condicional    → RUNCIRCUIT ( expr ) { corpo } ( SHORTCIRCUIT { corpo } )?
loop           → RUNCOOLER ( init ; cond ; incr ) { corpo } STOPCOOLER ;
retorno        → EJECT expr ;
chamada_funcao → ID_FUNC ( args ) ;
bloco          → { corpo }
comando_vazio  → ;

init           → TYPE_VAR VAR = expr
               | VAR = expr
               | ε

args           → expr ( , expr )*
               | ε
```

### Expressões (precedência do menor para o maior)

```
expr           → or_expr

or_expr        → and_expr ( OR and_expr )*
and_expr       → not_expr ( AND not_expr )*
not_expr       → NOT not_expr
               | comparação

comparação     → adição ( OP_COMP adição )?    (OP_COMP: == != < > <= >=)
adição         → multiplicação ( (+ | -) multiplicação )*
multiplicação  → unário ( (* | /) unário )*
unário         → OP_UNARIO VAR
               | primário

primário       → STRING
               | NUMBER
               | VAL_BOOL
               | VAR
               | KEYBOARD ()
               | ID_FUNC ( args )
```

---

## Erros Tratados pelo Analisador Sintático

O `parser.py` implementa **recuperação de erros**: ao encontrar um erro, registra a mensagem e avança até o próximo ponto seguro (`;`, início de novo comando ou `}`), permitindo que múltiplos erros sejam reportados em uma única passagem.

### Erros de estrutura do programa

| Situação | Mensagem gerada |
| :--- | :--- |
| Código não começa com `POWER_ON` | `Programa deve iniciar com POWER_ON (encontrado '...' na linha X, coluna Y).` |
| `POWER_OFF` ausente — chegou no fim do arquivo | `Esperado POWER_OFF para finalizar o programa, encontrado final do arquivo (EOF).` |
| `POWER_OFF` ausente — encontrou outro token | `Esperado POWER_OFF para finalizar o programa, encontrado '...' na linha X, coluna Y.` |
| `}` inesperada no nível do programa | `Chave de fechamento '}' inesperada na linha X, coluna Y.` |

### Erros de blocos e parênteses

| Situação | Mensagem gerada |
| :--- | :--- |
| Bloco `{` aberto sem `}` de fechamento | `Chave aberta e não fechada — esperado '}', encontrado ... na linha X, coluna Y.` |
| Parêntese `(` aberto sem `)` de fechamento | `Parêntese aberto e não fechado — esperado ')', encontrado ... na linha X, coluna Y.` |
| Token genérico esperado mas não encontrado | `Esperado TIPO_TOKEN, encontrado OUTRO_TOKEN ('valor') na linha X, coluna Y.` |

### Erros de comandos e expressões

| Situação | Mensagem gerada |
| :--- | :--- |
| Inicialização de loop com token inválido | `Inicialização do loop inválida na linha X, coluna Y.` |
| Token desconhecido no lugar de um comando | `Comando inesperado 'valor' (TIPO) na linha X, coluna Y.` |
| Token inválido no lugar de uma expressão | `Expressão inválida 'valor' (TIPO) na linha X, coluna Y.` |

### Erros léxicos (reportados pelo `lexer.py`)

| Situação | Exemplo | Mensagem gerada |
| :--- | :--- | :--- |
| Variável com letras maiúsculas | `$Nome` | `Identificador/variável mal formado: '$Nome'` |
| Identificador começa com dígito | `123abc` | `Identificador/variável mal formado: '123abc'` |
| Float com parte decimal inválida | `1.abc` | `Número mal formado: '1.abc'` |
| String sem fechamento de aspas | `"texto` | `Cadeia de caracteres mal formada ou não fechada: '"texto'` |
| Símbolo fora do alfabeto da linguagem | `@` | `Símbolo não pertencente ao conjunto de símbolos terminais: '@'` |
| Identificador com mais de 30 caracteres | — | `Tamanho do identificador excede o limite de 30 caracteres` |
| Número com mais de 15 dígitos | — | `Tamanho excessivo do número (máximo de 15 dígitos)` |

---

## Detalhes da Implementação

### Analisador Léxico (`lexer.py`)

- Utiliza **expressões regulares** compiladas em um único padrão alternado via `re.finditer`, garantindo eficiência linear no tamanho do código.
- Tokens com erros (mal formados, símbolos inválidos) são descartados e registrados na lista de erros, permitindo que a tokenização continue.
- Rastreia **linha e coluna** de cada token para mensagens de erro precisas.
- A saída formatada exibe cada token no padrão: `Linha: N - Coluna C - Token:<NomePT, valor>`.

### Analisador Sintático (`parser.py`)

- Implementa um **parser descendente recursivo** (_recursive descent parser_) manual, sem uso de geradores de parser.
- A recuperação de erros (`_sync`) descarta tokens até encontrar um `;`, o início de um novo comando reconhecível ou uma `}`, evitando que um único erro interrompa toda a análise.
- A Árvore Sintática Abstrata (ASA) é construída com nós `ParseNode`, cujos nomes são traduzidos para o português na exibição.
- A árvore é impressa em formato texto com prefixos `├──` / `└──` para visualização na aba **Árvore Sintática** da IDE.

### Regras da linguagem

- Identificadores de variável: apenas letras minúsculas, dígitos e `_`, precedidos de `$`, máximo 30 caracteres.
- Números: inteiros ou decimais (com `.`), máximo 15 dígitos totais.
- Strings: delimitadas por aspas duplas `"`, suportam sequências de escape `\"`.
- Comentários de linha com `//`, ignorados pelo léxico.
- Funções aceitam no máximo **3 parâmetros**, todos tipados.
- Todo comando termina obrigatoriamente com `;`.
