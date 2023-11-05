from pycparser import c_parser, c_ast

# Ваш код C или путь к файлу C
c_code = """
int add(int a, int b) {
    return a + b;
}
"""

# Создание экземпляра парсера
parser = c_parser.CParser()

# Парсинг исходного кода C и получение AST
ast = parser.parse(c_code)


class SemanticAnalyzer(c_ast.NodeVisitor):
    def __init__(self):
        # Эта таблица будет содержать переменные и их типы
        self.symbol_table = SymbolTable()

    def visit_Decl(self, node):
        """
        Обработка объявления переменной.
        """
        if isinstance(node.type, c_ast.TypeDecl):
            # Проверяем, не была ли переменная объявлена ранее
            if node.name in self.symbol_table:
                print(f"Ошибка: переменная '{node.name}' уже объявлена.")
            else:
                self.symbol_table[node.name] = node.type.type.names[0]
                # Обновление для использования TypeInfo
                type_info = TypeInfo(node.type.type.names[0])
                self.symbol_table[node.name] = type_info

    def visit_Assignment(self, node):
        # Получаем тип левой и правой сторон присваивания
        lvalue_type = self.visit(node.lvalue)
        rvalue_type = self.visit(node.rvalue)
        # Проверяем, что типы совместимы
        if not lvalue_type.is_compatible(rvalue_type):
            print(f"Ошибка: несовместимые типы для присваивания: {lvalue_type} и {rvalue_type}.")
        # Возвращаем тип присвоенного значения
        return lvalue_type

    def visit_BinaryOp(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        # Проверка совместимости типов с использованием TypeInfo
        if not left_type.is_compatible(right_type):
            print(f"Ошибка: типы операндов {left_type} и {right_type} несовместимы для операции {node.op}")
        # Возвращаем TypeInfo для результата бинарной операции
        # Это упрощение, в реальном коде необходимо учитывать результат операции
        return left_type if left_type.is_compatible(right_type) else TypeInfo('error')

    def visit_Constant(self, node):
        # Определяем тип константы на основе ее значения
        if node.type == 'int':
            return TypeInfo('int')
        elif node.type == 'float':
            return TypeInfo('float')
        elif node.type == 'char':
            return TypeInfo('char')
        else:
            return TypeInfo('unknown')


    def visit_ID(self, node):
        # Возвращаем тип переменной, если она объявлена
        var_type = self.symbol_table.get(node.name)
        if var_type is None:
            print(f"Ошибка: переменная '{node.name}' не объявлена.")
            return TypeInfo('error')
        else:
            return var_type

    def visit_FuncDef(self, node):
        self.current_function_type = self.visit(node.decl.type)
        # Получаем имя функции и тип возвращаемого значения
        func_name = node.decl.name
        ret_type = self.visit(node.decl.type.type)

        # Проверяем, объявлена ли функция ранее
        if func_name in self.symbol_table:
            print(f"Ошибка: функция '{func_name}' уже объявлена.")
            return
        # Проверяем и получаем типы параметров функции
        param_types = []
        if node.decl.type.args:
            for param_decl in node.decl.type.args.params:
                param_type = self.visit(param_decl.type)
                param_types.append(param_type)
        # Создаем TypeInfo для функции и добавляем в символьную таблицу
        func_type = TypeInfo('function', base_type=ret_type, function_params=param_types)
        self.symbol_table[func_name] = func_type

        # Переходим к телу функции
        self.visit(node.body)
        self.current_function_type = None


    def visit_FuncDecl(self, node):
        # Получаем тип возвращаемого значения функции
        ret_type = self.visit(node.type)
        # Проверяем и получаем типы параметров функции
        param_types = []
        if node.args:
            for param in node.args.params:
                param_name = param.name or ""
                param_type = self.visit(param.type)
                param_types.append((param_name, param_type))
        # Возвращаем информацию о функции
        return TypeInfo('function', function_return_type=ret_type, function_params=param_types)


    def visit_FuncCall(self, node):
        # Получаем имя функции
        func_name = node.name.name

        # Получаем информацию о функции из символьной таблицы
        func_info = self.symbol_table.get(func_name)
        if func_info is None or func_info.type_name != 'function':
            print(f"Ошибка: вызов необъявленной функции '{func_name}'.")
            return TypeInfo('error')
        # Получаем типы аргументов вызова функции
        arg_types = [self.visit(arg) for arg in node.args.exprs] if node.args else []
        # Проверяем количество аргументов
        if len(arg_types) != len(func_info.function_params):
            print(f"Ошибка: количество аргументов не соответствует определению функции '{func_name}'.")
            return TypeInfo('error')
        # Проверяем типы аргументов на совместимость с типами параметров функции
        for arg_type, param_type in zip(arg_types, func_info.function_params):
            if not arg_type.is_compatible(param_type):
                print(f"Ошибка: тип аргумента '{arg_type}' не совместим с параметром функции '{param_type}'.")
                return TypeInfo('error')

        # Если все проверки пройдены успешно, возвращаем тип возвращаемого значения функции
        return func_info.function_return_type

    def visit_Return(self, node):
        # Предполагаем, что у нас есть переменная self.current_function_type, которая содержит TypeInfo текущей функции
        if self.current_function_type is None:
            print("Ошибка: оператор return вне функции.")
            return TypeInfo('error')
        # Проверяем, есть ли возвращаемое значение
        if not node.expr:
            if self.current_function_type.function_return_type.type_name != 'void':
                print("Ошибка: отсутствует возвращаемое значение в функции, которая должна что-то возвращать.")
                return TypeInfo('error')
            return self.current_function_type.function_return_type
        # Если возвращаемое значение есть, проверяем его тип
        return_type = self.visit(node.expr)
        if not return_type.is_compatible(self.current_function_type.function_return_type):
            print(f"Ошибка: тип возвращаемого значения '{return_type}' не соответствует типу функции '{self.current_function_type.function_return_type}'.")
            return TypeInfo('error')

        return return_type

    def visit_Compound(self, node):
        # Входим в новую область видимости
        self.symbol_table.enter_scope()
        # Посещаем все утверждения и объявления в составном блоке
        for item in node.block_items:
            self.visit(item)
        # Выходим из области видимости
        self.symbol_table.exit_scope()


    def visit_If(self, node):
        # Посещаем условие if для проверки его типа
        cond_type = self.visit(node.cond)
        if cond_type.type_name != 'bool':
            print(f"Ошибка: условие if имеет не булев тип '{cond_type.type_name}'.")
        # Посещаем тело if
        if node.iftrue:
            self.visit(node.iftrue)
        # Посещаем тело else, если оно есть
        if node.iffalse:
            self.visit(node.iffalse)

    def visit_For(self, node):
        # Входим в новую область видимости для инициализации переменных цикла
        self.symbol_table.enter_scope()
        # Посещаем инициализационное выражение, условие и итерационное выражение
        if node.init: self.visit(node.init)
        if node.cond: self.visit(node.cond)
        if node.next: self.visit(node.next)
        # Посещаем тело цикла
        self.visit(node.stmt)
        # Выходим из области видимости
        self.symbol_table.exit_scope()

    def visit_While(self, node):
        # Проверяем условие цикла
        cond_type = self.visit(node.cond)
        if not cond_type.is_boolean():
            print(f"Ошибка: условие while имеет не булев тип '{cond_type.type_name}'.")

        # Посещаем тело цикла
        self.visit(node.stmt)

    def visit_DoWhile(self, node):
        # Посещаем тело цикла
        self.visit(node.stmt)

        # Проверяем условие цикла
        cond_type = self.visit(node.cond)
        if not cond_type.is_boolean():
            print(f"Ошибка: условие do-while имеет не булев тип '{cond_type.type_name}'.")

    def visit_Switch(self, node):
        # Проверяем выражение переключения
        expr_type = self.visit(node.cond)
        if not expr_type.is_integer():
            print(f"Ошибка: выражение switch имеет не целочисленный тип '{expr_type.type_name}'.")

        # Посещаем каждый case и default
        if node.stmt:
            self.visit(node.stmt)

    def visit_Case(self, node):
        # Проверяем, что выражение в case является целочисленной константой
        expr_type = self.visit(node.expr)
        if not (expr_type.is_integer() and isinstance(node.expr, c_ast.Constant)):
            print(f"Ошибка: выражение case '{node.expr}' не является целочисленной константой.")

        # Посещаем тело case
        if node.stmt:
            self.visit(node.stmt)

    def visit_Default(self, node):
        # Посещаем тело default
        if node.stmt:
            self.visit(node.stmt)

    def visit_Break(self, node):
        # Проверяем, находимся ли мы внутри цикла или оператора switch
        if not self.in_loop_or_switch():
            print("Ошибка: оператор break находится вне цикла или switch.")
        # Здесь не требуется возвращать TypeInfo, так как break не связан с типами

    def visit_Continue(self, node):
        # Проверяем, находимся ли мы внутри цикла
        if not self.in_loop():
            print("Ошибка: оператор continue находится вне цикла.")
        # Оператор continue не возвращает и не обрабатывает типы, поэтому TypeInfo здесь не используется

    def visit_TernaryOp(self, node):
        cond_type = self.visit(node.cond)
        if not cond_type.is_boolean():
            print(f"Ошибка: условие тернарного оператора не является булевым выражением: {cond_type.type_name}")

        if_type = self.visit(node.iftrue)
        else_type = self.visit(node.iffalse)

        # Здесь должна быть логика для определения общего типа для iftrue и iffalse
        common_type = self.determine_common_type(if_type, else_type)
        if common_type is None:
            print(
                f"Ошибка: типы выражений тернарного оператора не совместимы: {if_type.type_name} и {else_type.type_name}")

        return common_type

    def visit_Cast(self, node):
        # Посещаем тип, к которому приводим
        cast_to_type = self.visit(node.to_type)
        # Посещаем выражение, которое приводится к типу
        expr_type = self.visit(node.expr)
        # Проверяем, допустимо ли приведение
        if not self.is_cast_allowed(expr_type, cast_to_type):
            print(f"Ошибка: приведение типа '{expr_type.type_name}' к '{cast_to_type.type_name}' недопустимо.")
        # Возвращаем тип, к которому приводили, так как выражение теперь этого типа
        return cast_to_type

    def visit_UnaryOp(self, node):
        # Обработка унарных операций (например, отрицания, инкремента)
        # Проверка типа операнда
        pass

class TypeInfo:
    def __init__(self, type_name, base_type=None, array_size=None, function_return_type=None, function_params=None):
        self.type_name = type_name  # Например, 'int', 'float', 'char*', 'int[10]', 'function'
        self.base_type = base_type  # Для массивов и указателей, это будет 'int', 'float', и т.д.
        self.array_size = array_size  # Для массивов, это будет размерность
        self.function_return_type = function_return_type
        self.function_params = function_params
        self.loop_or_switch_depth = 0
        self.loop_depth = 0

    TYPE_RANK = {
        'long double': 8,
        'double': 7,
        'float': 6,
        'unsigned long long': 5,
        'long long': 4,
        'unsigned long': 3,
        'long': 2,
        'unsigned int': 1,
        'int': 0,
        'unsigned short': -1,
        'short': -2,
        'unsigned char': -3,
        'signed char': -4,
        'char': -5,
        'bool': -6,
    }
    def is_compatible(self, other):
        # Базовые типы совместимы только с собой
        if self.type_name in ['int', 'float', 'char'] and self.type_name == other.type_name:
            return True

        # Если типы совпадают и оба являются функциями, проверяем их совместимость
        if self.type_name == 'function' and other.type_name == 'function':
            # Сначала проверяем возвращаемый тип
            if not self.function_return_type.is_compatible(other.function_return_type):
                return False
            # Затем проверяем совместимость параметров
            if len(self.function_params) != len(other.function_params):
                return False
            for self_param, other_param in zip(self.function_params, other.function_params):
                if not self_param.is_compatible(other_param):
                    return False
            return True

        # Дополнительные правила совместимости можно добавить здесь
        # Если ни одно из правил не сработало, типы несовместимы
        return False

    def __str__(self):
        if self.type_name == 'function':
            params_str = ', '.join(str(param) for param in self.function_params)
            return f"{self.function_return_type} function({params_str})"
        elif self.type_name == 'array':
            return f"{self.base_type}[{self.array_size}]"
        elif self.type_name in ['int', 'float', 'char']:
            return self.type_name
        else:
            # Для других, более сложных типов, например, указателей
            return f"{self.type_name} {self.base_type}"

    def is_boolean(self):
        # Возвращает True, если тип является булевым или может быть интерпретирован как булев
        return self.type_name == 'bool' or (self.type_name in ['int', 'float'] and self.base_type is None)

    def is_integer(self):
        # Возвращает True, если тип является целочисленным
        return self.type_name in ['int', 'long', 'short', 'char']

    def is_constant_expression(self):
        # Возвращает True, если тип является константой
        # Это место для реализации логики, определяющей, является ли выражение константой
        return self.base_type is not None and self.array_size is None and self.function_return_type is None and self.function_params is None

    def in_loop_or_switch(self):
        return self.loop_or_switch_depth > 0

    def visit_While(self, node):
        self.loop_or_switch_depth += 1
        super().visit_While(node)
        self.loop_or_switch_depth -= 1

    def in_loop(self):
        return self.loop_depth > 0

    def visit_While(self, node):
        self.loop_depth += 1
        super().visit_While(node)
        self.loop_depth -= 1

    def visit_For(self, node):
        self.loop_depth += 1
        super().visit_For(node)
        self.loop_depth -= 1

    @staticmethod
    def determine_common_type(type1, type2):
        # Получаем ранги типов
        rank1 = TypeInfo.TYPE_RANK.get(type1.type_name, None)
        rank2 = TypeInfo.TYPE_RANK.get(type2.type_name, None)
        # Проверяем наличие типов в рангах
        if rank1 is None or rank2 is None:
            print(f"Ошибка: неизвестный тип данных '{type1.type_name}' или '{type2.type_name}'")
            return None
        # Выбираем тип с наивысшим рангом
        higher_rank_type = type1 if rank1 >= rank2 else type2
        # Обрабатываем специальный случай для char и bool
        if 'char' in (type1.type_name, type2.type_name) or \
                'bool' in (type1.type_name, type2.type_name):
            # В C, char и bool могут быть неявно приведены к int
            return TypeInfo('int')

        # Возвращаем тип с наивысшим рангом
        return higher_rank_type

    def is_cast_allowed(self, from_type, to_type):
        return True

    def is_lossy_cast(self, other_type_info):
        # Проверка на потенциальную потерю данных при приведении
        if self.type_name in ['float', 'double'] and other_type_info.type_name in ['int', 'short']:
            return True  # Приведение с плавающей точкой к целому может привести к потере данных
        return False

    @staticmethod
    def is_integer_type(type_name):
        return type_name in ['int', 'unsigned int', 'long', 'unsigned long', 'short', 'unsigned short', 'char',
                             'unsigned char']

    @staticmethod
    def is_floating_point_type(type_name):
        return type_name in ['float', 'double', 'long double']

    def can_be_cast_to(self, other_type_info):
        # Проверки для приведения между целочисленными типами и указателями
        if self.is_pointer_type(self.type_name) or self.is_pointer_type(other_type_info.type_name):
            if self.type_name != other_type_info.type_name:
                # Приведение разрешено, но может быть опасным
                print(
                    f"Внимание: приведение между разными типами указателей или между указателями и целыми числами может быть опасным.")
            return True  # В C приведение разрешено, но может быть небезопасным
        # Проверки для приведения между целочисленными и числами с плавающей точкой
        if (self.is_integer_type(self.type_name) and self.is_floating_point_type(other_type_info.type_name)) or \
                (self.is_floating_point_type(self.type_name) and self.is_integer_type(other_type_info.type_name)):
            return True  # Приведение между целыми числами и числами с плавающей точкой допустимо

        # Дополнительные проверки для других типов могут быть добавлены здесь
        return True

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # Список словарей для каждой области видимости

    def enter_scope(self):
        # Создаем новую область видимости
        self.scopes.append({})

    def exit_scope(self):
        # Удаляем последнюю область видимости
        self.scopes.pop()

    def declare(self, name, type_info):
        # Объявляем переменную в текущей области видимости
        self.scopes[-1][name] = type_info

    def lookup(self, name):
        # Ищем переменную, начиная с текущей области видимости и двигаясь к глобальной
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None  # Возвращаем None, если переменная не найдена


# Создаем экземпляр нашего SemanticAnalyzer
semantic_analyzer = SemanticAnalyzer()
# Используем анализатор для обхода AST
semantic_analyzer.visit(ast)
ast.show()