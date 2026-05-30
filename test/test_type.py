from sympy import Mul, Integer, Rational, Pow, pi, srepr
from src.aidu.ai.sympy.ast.pretty.linear import cleanup_ast

expr = Mul(Integer(1), Pow(Integer(2), Integer(-1)), pi, evaluate=False)
print(f"Type(expr): {type(expr)}")
print(f"expr.is_Mul: {expr.is_Mul}")

# Debug cleanup_ast
def debug_cleanup_ast(expr):
    from sympy import Mul, Add, Pow, Basic, Rational
    print(f"Processing: {type(expr)} {expr}")
    if not isinstance(expr, Basic):
        return expr
    
    cleaned_args = [debug_cleanup_ast(arg) for arg in expr.args]
    print(f"Cleaned args for {expr}: {cleaned_args}")
    
    if expr.is_Pow:
        base, exp = cleaned_args
        if exp == 0: return 1
        if exp == 1: return base
        return Pow(base, exp, evaluate=False)
    
    if expr.is_Mul:
        rat_coeff = None
        other_args = []
        for arg in cleaned_args:
            if isinstance(arg, Rational):
                if rat_coeff is None: rat_coeff = arg
                else: rat_coeff = rat_coeff * arg
            elif arg != 1:
                other_args.append(arg)
        final_args = []
        if rat_coeff is not None: final_args.append(rat_coeff)
        final_args.extend(other_args)
        if not final_args: return 1
        if len(final_args) == 1: return final_args[0]
        return Mul(*final_args, evaluate=False)
    
    if cleaned_args:
        return expr.func(*cleaned_args, evaluate=False)
    return expr

res = debug_cleanup_ast(expr)
print(f"Result srepr: {srepr(res)}")
