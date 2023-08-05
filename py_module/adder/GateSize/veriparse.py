# Structural Verilog Parser

import sys
import ply.yacc as yacc
from verilex import tokens
import cust_ast

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def p_source_text(p):
    'source_text : module_star'
    p[0] = p[1]

def p_module_star(p):
    '''module_star : module module_star
                   | empty'''
    if (len(p) == 3):
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_module(p):
    'module : MODULE ID list_of_ports SEMI module_item_star ENDMODULE'
    p[0] =  cust_ast.ModuleDef(p[2], p[3], p[5])

def p_list_of_ports(p):
    '''list_of_ports : LPAREN port more_ports RPAREN
                     | empty'''
    if (len(p) == 5):
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_port(p):
    'port : ID'
    # using very simple ports for time being
    p[0] = p[1]

def p_more_ports(p):
    '''more_ports : COMMA port more_ports
                  | empty'''
    if (len(p) == 4):
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_declaration(p):
    '''declaration : port_type list_of_variables SEMI'''
    p[0] = [cust_ast.NetDef(n,p[1]) for n in p[2]]

def p_port_type(p):
    '''port_type : INPUT 
                 | OUTPUT
                 | WIRE''' 
    p[0] = p[1]

def p_list_of_variables(p):
    '''list_of_variables : ID more_variables'''
    p[0] = [p[1]] + p[2]

def p_more_variables(p):
    '''more_variables : COMMA ID more_variables
                      | empty'''
    if (len(p) == 4):
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []
    
def p_module_item_star(p):
    '''module_item_star : module_item module_item_star
                        | empty'''
    if (len(p) == 3):
        p[0] = p[1] + p[2]
    else:
        p[0] = []
def p_module_item(p):
    '''module_item : module_instantiation
                    | declaration'''
    p[0] = p[1]

def p_module_instantiation(p):
    'module_instantiation : ID ID LPAREN list_of_module_connections RPAREN SEMI'
    p[0] = [cust_ast.ModuleInst(p[1], p[2], p[4])]

def p_list_of_module_connections(p):
    '''list_of_module_connections : module_port_connection more_module_ports
                                  | named_port_connection more_named_ports'''
    p[0] = [p[1]] + p[2]

def p_module_port_connection(p):
    '''module_port_connection : expression
                              | empty'''
    p[0] = p[1]

def p_more_module_ports(p):
    '''more_module_ports : COMMA module_port_connection more_module_ports
                         | empty'''
    if (len(p) == 4):
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_named_port_connection(p):
    'named_port_connection : DOT ID LPAREN expression RPAREN'
    p[0] = (p[2], p[4])

def p_more_named_ports(p):
    '''more_named_ports : COMMA named_port_connection more_named_ports
                        | empty'''
    if (len(p) == 4):
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []
    

def p_expression(p):
    '''expression : INTEGER 
                  | ID'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    print("Syntax error at", p.value, "type", p.type, "on line", p.lexer.lineno)

parser = yacc.yacc()

if __name__ == "__main__":
    verilog_src = open(sys.argv[1])
    mods = parser.parse(verilog_src.read())
    target = mods[0]
    
            
    
