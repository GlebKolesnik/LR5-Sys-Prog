from pycparser import c_parser

# Исходный код на C
c_code = """
int add(int a, int b) {
    return a + b;
}
"""

# Создание экземпляра парсера
parser = c_parser.CParser()

# Парсинг исходного кода C
ast = parser.parse(c_code)

# Вывод AST
ast.show()
