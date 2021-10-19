import typing
import lib.ply.yacc as yacc
from drip.lex import tokens
import drip.ast as ast

def p_structure_definition(p):
    '''structure_definition : STRUCTURE CAMEL_NAME LPAREN structure_arguments RPAREN'''
    p[0] = ast.StructureDefinition(
        name=p[2],
        fields=p[4],
    )

def p_structure_arguments(p):
    '''structure_arguments : fieldlist 
                           | empty'''
    p[0] = tuple() if isinstance(p[1], Empty) else p[1]

class Empty:
    pass

def p_empty(p) -> Empty:
    '''empty :'''
    return Empty()

def p_fieldlist(p) -> typing.Tuple[ast.StructureFieldDefinition]:
    '''fieldlist : fieldlisting
                 | fieldlisting fieldlist'''
    if len(p) == 2:
        p[0] = (p[1],)
    else:
        p[0] = (p[1],) + p[2]

def p_fieldlisting(p) -> ast.StructureFieldDefinition:
    '''fieldlisting : SNAKE_NAME COLON CAMEL_NAME COMMA'''
    p[0] = ast.StructureFieldDefinition(name=p[1], type_name=p[3])



def p_error(p):
    print('error in input', p)

parser = yacc.yacc()
