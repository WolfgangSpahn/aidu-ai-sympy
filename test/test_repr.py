from sympy import symbols, Mul, Rational, pi
expr = Mul(Rational(-1, 2), pi, evaluate=False)
print("Args:", expr.args)
for i, arg in enumerate(expr.args):
    print(f"Arg {i}: {arg}, is_Pow: {arg.is_Pow}, is_Rational: {arg.is_Rational}")
