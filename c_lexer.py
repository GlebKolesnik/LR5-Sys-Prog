import ply.lex as lex

# Список токенов
tokens = (
    'ID',
    'INT_CONST',
    'CHAR_CONST',
    'FLOAT_CONST',
    'STRING',
    'ENUMERATION_CONST',
    # Зарезервированные слова
    'AUTO', 'REGISTER', 'STATIC', 'EXTERN', 'TYPEDEF',
    'VOID', 'CHAR', 'SHORT', 'INT', 'LONG', 'FLOAT', 'DOUBLE', 'SIGNED', 'UNSIGNED',
    'STRUCT', 'UNION', 'ENUM',
    'CONST', 'VOLATILE',
    'IF', 'ELSE', 'SWITCH', 'CASE', 'DEFAULT',
    'WHILE', 'DO', 'FOR',
    'GOTO', 'CONTINUE', 'BREAK', 'RETURN',
    # Операторы
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'OR', 'AND', 'NOT', 'XOR', 'LSHIFT', 'RSHIFT',
    'LOR', 'LAND', 'LNOT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    'ASSIGN',
    'PLUS_ASSIGN', 'MINUS_ASSIGN', 'TIMES_ASSIGN', 'DIVIDE_ASSIGN', 'MOD_ASSIGN',
    'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN', 'LSHIFT_ASSIGN', 'RSHIFT_ASSIGN',
    # Другие символы
    'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE',
    'LBRACKET', 'RBRACKET',
    'COMMA', 'PERIOD', 'SEMICOLON', 'COLON',
    'POINTER', 'ADDRESS',
    'INCREMENT', 'DECREMENT',
    # Предпроцессор и прочее
    'PREPROCESSOR',
    'COMMENT',
    'INCLUDE',
    'DEFINE',
    'IFDEF',
    'IFNDEF',
    'ELSE',
    'ENDIF',
    'ATTRIBUTE', 'ASM', 'BUILTIN', 'ERROR',
    'LONG_LONG', 'LONG_DOUBLE',
    'TYPE_QUALIFIER'
)

# Регулярные выражения для токенов
t_INT_CONST = r'\d+'
t_CHAR_CONST = r'\'[^\']*\''
t_FLOAT_CONST = r'((\d+\.\d*)|(\d*\.\d+))([eE][-+]?\d+)?'
t_STRING = r'\"[^\"]*\"'
t_ENUMERATION_CONST = r'[A-Z][A-Z_0-9]*'
t_INCLUDE = r'\#\s*include\s+<[^>]+>'
t_DEFINE = r'\#\s*define\s+[a-zA-Z_][a-zA-Z_0-9]*\s+.*'
t_IFDEF = r'\#\s*ifdef\s+[a-zA-Z_][a-zA-Z_0-9]*'
t_IFNDEF = r'\#\s*ifndef\s+[a-zA-Z_][a-zA-Z_0-9]*'
t_ELSE = r'\#\s*else'
t_ENDIF = r'\#\s*endif'
t_ID = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_ATTRIBUTE = r'__attribute__\s*\(\s*\(\s*[a-zA-Z_][a-zA-Z_0-9]*\s*(,\s*[a-zA-Z_][a-zA-Z_0-9]*\s*)*\)\s*\)'
t_ASM = r'__asm\s+\"[^\"]*\"'
t_BUILTIN = r'__builtin_[a-zA-Z_][a-zA-Z_0-9]*\s*\(\s*[^\)]*\s*\)'
t_ERROR = r'error\s*\(s*\"[^\"]*\"\s*\)'
t_LONG_INT_CONST = r'\d+[lL]'
t_LONG_FLOAT_CONST = r'((\d+\.\d*)|(\d*\.\d+))([eE][-+]?\d+)?[lLfF]'


# Зарезервированные слова
reserved = {
    'auto': 'AUTO', 'register': 'REGISTER', 'static': 'STATIC', 'extern': 'EXTERN', 'typedef': 'TYPEDEF',
    'void': 'VOID', 'char': 'CHAR', 'short': 'SHORT', 'int': 'INT', 'long': 'LONG', 'float': 'FLOAT', 'double': 'DOUBLE', 'signed': 'SIGNED', 'unsigned': 'UNSIGNED',
    'struct': 'STRUCT', 'union': 'UNION', 'enum': 'ENUM',
    'const': 'CONST', 'volatile': 'VOLATILE',
    'if': 'IF', 'else': 'ELSE', 'switch': 'SWITCH', 'case': 'CASE', 'default': 'DEFAULT',
    'while': 'WHILE', 'do': 'DO', 'for': 'FOR',
    'goto': 'GOTO', 'continue': 'CONTINUE', 'break': 'BREAK', 'return': 'RETURN',
}

# Определение токена ID (идентификатора)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t

# Определение операторов и других символов
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_OR = r'\|'
t_AND = r'&'
t_NOT = r'~'
t_XOR = r'\^'
t_LSHIFT = r'<<'
t_RSHIFT = r'>>'
t_LOR = r'\|\|'
t_LAND = r'&&'
t_LNOT = r'!'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_ASSIGN = r'='
t_PLUS_ASSIGN = r'\+='
t_MINUS_ASSIGN = r'-='
t_TIMES_ASSIGN = r'\*='
t_DIVIDE_ASSIGN = r'/='
t_MOD_ASSIGN = r'%='
t_AND_ASSIGN = r'&='
t_OR_ASSIGN = r'\|='
t_XOR_ASSIGN = r'\^='
t_LSHIFT_ASSIGN = r'<<='
t_RSHIFT_ASSIGN = r'>>='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_PERIOD = r'\.'
t_SEMICOLON = r';'
t_COLON = r':'
t_POINTER = r'\->'
t_ADDRESS = r'&'
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'

# Определение предпроцессорных директив и комментариев
def t_PREPROCESSOR(t):
    r'\#.*'
    pass  # No return value. Token discarded
def t_COMMENT(t):
    r'(\/\/[^\n]*|\/\*[\s\S]*?\*\/)'
    pass
# Определение новой строки
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
# Определение пробелов и табуляции
t_ignore = ' \t'
# Определение ошибок
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

def t_LONG_LONG(t):
    r'long\s+long\b'
    return t

def t_LONG_DOUBLE(t):
    r'long\s+double\b'
    return t

# Если 'const' и 'volatile' ещё не были включены
def t_TYPE_QUALIFIER(t):
    r'(const|volatile)\b'
    return t

# Используйте этот код для обработки #define с идентификатором и значением
def t_DEFINE(t):
    r'\#\s*define\s+[a-zA-Z_][a-zA-Z_0-9]*\s+([^\n]*)'
    t.value = t.value.split(maxsplit=2)[2]  # Сохраняет значение после #define и идентификатора
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}")
    t.lexer.skip(1)

# Построение лексера
lexer = lex.lex()

