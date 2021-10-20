import typing
import lib.ply.yacc as yacc
from drip.lex import tokens
import drip.ast as ast
from dataclasses import replace, dataclass


def p_program_structure_definition(p):
    """program : structure_definition program"""
    p[0] = replace(p[2], structure_definitions=p[2].structure_definitions + (p[1],))


def p_program_function_definition(p):
    """program : function_definition program"""
    p[0] = replace(p[2], function_definitions=p[2].function_definitions + (p[1],))


def p_program_empty(p):
    """program : empty"""
    p[0] = ast.Program()


def p_function_definition(p):
    """function_definition : FUNCTION SNAKE_NAME LPAREN argument_definitions RPAREN ARROW CAMEL_NAME LPAREN function_body RPAREN"""
    p[0] = ast.FunctionDefinition(
        name=p[2],
        arguments=p[4],
        procedure=p[9],
    )


def p_function_body_statement(p):
    """function_body : statement SEMICOLON function_body"""
    p[0] = (p[1],) + p[3]


def p_function_body_empty(p):
    """function_body : empty"""
    p[0] = tuple()


def p_statement_return(p):
    """statement : RETURN expression"""
    p[0] = ast.ReturnStatement(expression=p[2])


def p_statement_assignment(p):
    """statement : SNAKE_NAME EQUALS expression"""
    p[0] = ast.AssignmentStatement(variable_name=p[1], expression=p[3])


def p_expression_literal(p):
    """expression : NUMBER"""
    p[0] = ast.LiteralExpression(value=p[1])


def p_expression_variable_reference(p):
    """expression : SNAKE_NAME"""
    p[0] = ast.VariableReferenceExpression(name=p[1])


def p_expression_construction(p):
    """expression : CAMEL_NAME LPAREN arguments RPAREN"""
    p[0] = ast.ConstructionExpression(
        type_name=p[1],
        arguments={argument.name: argument.expression for argument in p[3]},
    )


def p_function_call_expression(p) -> ast.FunctionCallExpression:
    """expression : SNAKE_NAME LPAREN arguments RPAREN"""
    p[0] = ast.FunctionCallExpression(
        function_name=p[1],
        arguments={argument.name: argument.expression for argument in p[3]},
    )


def p_property_access_expression(p) -> ast.PropertyAccessExpression:
    """expression : expression PERIOD SNAKE_NAME"""
    p[0] = ast.PropertyAccessExpression(entity=p[1], property_name=p[3])


BINARY_OPERATORS = {
    "+": ast.BinaryOperator.ADD,
}


def p_binary_operator_expression(p) -> ast.BinaryOperatorExpression:
    """expression : expression PLUS expression"""
    p[0] = ast.BinaryOperatorExpression(
        operator=BINARY_OPERATORS[p[2]],
        lhs=p[1],
        rhs=p[3],
    )


@dataclass(frozen=True)
class NamedArgument:
    name: str
    expression: ast.Expression


def p_arguments_argument(p) -> typing.Tuple[NamedArgument, ...]:
    """arguments : argument arguments"""
    p[0] = (p[1],) + p[2]


def p_arguments_empty(p) -> typing.Tuple[NamedArgument, ...]:
    """arguments : empty"""
    p[0] = tuple()


def p_argument(p) -> NamedArgument:
    """argument : SNAKE_NAME EQUALS expression COMMA"""
    p[0] = NamedArgument(name=p[1], expression=p[3])


def p_structure_definition(p):
    """structure_definition : STRUCTURE CAMEL_NAME LPAREN argument_definitions RPAREN"""
    p[0] = ast.StructureDefinition(
        name=p[2],
        fields=p[4],
    )


def p_expression_parenthetical(p):
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_argument_definitions_argument_definition(
    p,
) -> typing.Tuple[ast.ArgumentDefinition, ...]:
    """argument_definitions : argument_definition argument_definitions"""
    p[0] = (p[1],) + p[2]


def p_argument_definitions_empty(p) -> typing.Tuple[ast.ArgumentDefinition, ...]:
    """argument_definitions : empty"""
    p[0] = tuple()


def p_argument_definition(p) -> ast.ArgumentDefinition:
    """argument_definition : SNAKE_NAME COLON CAMEL_NAME COMMA"""
    p[0] = ast.ArgumentDefinition(name=p[1], type_name=p[3])


def p_error(p):
    print("error in input", p)


class Empty:
    pass


def p_empty(p) -> Empty:
    """empty :"""
    return Empty()


parser = yacc.yacc()
