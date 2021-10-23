import typing
import lib.ply.yacc as yacc
from drip.lex import tokens
import drip.ast as ast
from dataclasses import replace, dataclass


def p_program_structure_definition(p: yacc.YaccProduction) -> None:
    """program : structure_definition program"""
    p[0] = replace(p[2], structure_definitions=p[2].structure_definitions + (p[1],))


def p_program_function_definition(p: yacc.YaccProduction) -> None:
    """program : function_definition program"""
    p[0] = replace(p[2], function_definitions=p[2].function_definitions + (p[1],))


def p_program_empty(p: yacc.YaccProduction) -> None:
    """program : empty"""
    p[0] = ast.Program()


def p_function_definition(p: yacc.YaccProduction) -> None:
    """function_definition : FUNCTION SNAKE_NAME LPAREN argument_definitions_final RPAREN ARROW CAMEL_NAME LPAREN function_body RPAREN"""
    p[0] = ast.FunctionDefinition(
        name=p[2],
        arguments=p[4],
        procedure=p[9],
    )


def p_function_body_statement(p: yacc.YaccProduction) -> None:
    """function_body : statement SEMICOLON function_body"""
    p[0] = (p[1],) + p[3]


def p_function_body_empty(p: yacc.YaccProduction) -> None:
    """function_body : empty"""
    p[0] = tuple()


def p_statement_return(p: yacc.YaccProduction) -> None:
    """statement : RETURN expression"""
    p[0] = ast.ReturnStatement(expression=p[2])


def p_statement_assignment(p: yacc.YaccProduction) -> None:
    """statement : SNAKE_NAME EQUALS expression"""
    p[0] = ast.AssignmentStatement(variable_name=p[1], expression=p[3])


def p_expression_literal_number(p: yacc.YaccProduction) -> None:
    """expression : NUMBER"""
    p[0] = ast.LiteralExpression(type_name="float", value=p[1])


def p_expression_variable_reference(p: yacc.YaccProduction) -> None:
    """expression : SNAKE_NAME"""
    p[0] = ast.VariableReferenceExpression(name=p[1])


def p_expression_construction(p: yacc.YaccProduction) -> None:
    """expression : CAMEL_NAME LPAREN arguments_final RPAREN"""
    p[0] = ast.ConstructionExpression(
        type_name=p[1],
        arguments={argument.name: argument.expression for argument in p[3]},
    )


def p_function_call_expression(p: yacc.YaccProduction) -> None:
    """expression : SNAKE_NAME LPAREN arguments_final RPAREN"""
    p[0] = ast.FunctionCallExpression(
        function_name=p[1],
        arguments={argument.name: argument.expression for argument in p[3]},
    )


def p_property_access_expression(p: yacc.YaccProduction) -> None:
    """expression : expression PERIOD SNAKE_NAME"""
    p[0] = ast.PropertyAccessExpression(entity=p[1], property_name=p[3])


BINARY_OPERATORS = {
    "+": ast.BinaryOperator.ADD,
}


def p_binary_operator_expression(p: yacc.YaccProduction) -> None:
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


def p_arguments_final(p: yacc.YaccProduction) -> None:
    """arguments_final : arguments comma_opt"""
    p[0] = p[1]


def p_arguments_final_empty(p: yacc.YaccProduction) -> None:
    """arguments_final : empty"""
    p[0] = tuple()


def p_arguments_multiple(p: yacc.YaccProduction) -> None:
    """arguments : arguments COMMA argument"""
    p[0] = p[1] + (p[3],)


def p_arguments_single(p: yacc.YaccProduction) -> None:
    """arguments : argument"""
    p[0] = (p[1],)


def p_argument(p: yacc.YaccProduction) -> None:
    """argument : SNAKE_NAME EQUALS expression"""
    p[0] = NamedArgument(name=p[1], expression=p[3])


def p_structure_definition(p: yacc.YaccProduction) -> None:
    """structure_definition : STRUCTURE CAMEL_NAME LPAREN argument_definitions_final RPAREN"""
    p[0] = ast.StructureDefinition(
        name=p[2],
        fields=p[4],
    )


def p_argument_definitions_final(
    p: yacc.YaccProduction,
) -> None:
    """argument_definitions_final : argument_definitions comma_opt"""
    p[0] = p[1]


def p_argument_definitions_final_empty(
    p: yacc.YaccProduction,
) -> None:
    """argument_definitions_final : empty"""
    p[0] = tuple()


def p_argument_definitions_multiple(
    p: yacc.YaccProduction,
) -> None:
    """argument_definitions : argument_definitions COMMA argument_definition"""
    p[0] = p[1] + (p[3],)


def p_argument_definitions_single(p: yacc.YaccProduction) -> None:
    """argument_definitions : argument_definition"""
    p[0] = (p[1],)


def p_argument_definition(p: yacc.YaccProduction) -> None:
    """argument_definition : SNAKE_NAME COLON CAMEL_NAME"""
    p[0] = ast.ArgumentDefinition(name=p[1], type_name=p[3])


def p_comma_opt(
    p: yacc.YaccProduction,
) -> None:
    """comma_opt : COMMA
    | empty"""
    p[0] = None


def p_expression_parenthetical(p: yacc.YaccProduction) -> None:
    """expression : LPAREN expression RPAREN"""
    p[0] = p[2]


def p_error(p: yacc.YaccProduction) -> None:
    print(
        "error in input",
        parser.state,
        [symbol.type for symbol in parser.symstack][1:],
        p,
    )


class Empty:
    pass


def p_empty(p: yacc.YaccProduction) -> Empty:
    """empty :"""
    return Empty()


parser = yacc.yacc()
