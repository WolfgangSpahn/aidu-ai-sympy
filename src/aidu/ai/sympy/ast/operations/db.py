RULES = {
    # STRUCTURAL
    "distribute"               : "A:expr * (B:expr + C:expr) -> A*B + A*C",
    "factor"                   : "A:expr*B:expr + A:expr*C:expr -> A*(B + C)",
    "commute_add"              : "A:expr + B:expr -> B + A",
    "commute_mul"              : "A:expr * B:expr -> B * A",
    "associate_add_left"       : "(A:expr + B:expr) + C:expr -> A + (B + C)",
    "associate_add_right"      : "A:expr + (B:expr + C:expr) -> (A + B) + C",
    "associate_mul_left"       : "(A:expr * B:expr) * C:expr -> A * (B * C)",
    "associate_mul_right"      : "A:expr * (B:expr * C:expr) -> (A * B) * C",
    "factor_common_rational"   : "A:expr*R:rational + R:rational -> R*(A + 1)",
    "factor_common_rational_rev": "R:rational + A:expr*R:rational -> R*(1 + A)",
    "factor_common_rational_sympy": "R:rational + R:rational*A:expr -> R*(1 + A)",

    # NUMERIC
    "evaluate_integer_add"     : "A:int + B:int -> eval(A + B)",
    "evaluate_integer_mul"     : "A:int * B:int -> eval(A * B)",
    "evaluate_integer_pow"     : "A:int ** B:int -> eval(A ** B)",
    "expand_integer"           : "N:int * X:expr -> repeat(X,N,'+')",
    "reduce_fraction"          : "A:int / B:int -> reduce(A/B)",

    # FRACTIONS
    "factor_fraction_add"      : "A:expr/C:expr + B:expr/C:expr -> (A + B)/C",
    "split_fraction_add"       : "(A:expr + B:expr) / C:expr -> A/C + B/C",
    "combine_fraction_add"     : "A:expr/C:expr + B:expr/C:expr -> (A + B)/C",
    "multiply_fractions"       : "(A:expr/B:expr) * (C:expr/D:expr) -> (A*C)/(B*D)",
    "divide_fractions"         : "(A:expr/B:expr) / (C:expr/D:expr) -> (A*D)/(B*C)",
    "cancel_common_factor"     : "(A:expr*B:expr)/(A:nonzero*C:expr) -> B/C",

    # POWERS
    "expand_power_integer"     : "X:expr ** N:int -> repeat(X,N,'*')",
    "factor_power"             : "X:expr * X:expr -> X**2",
    "power_product"            : "(A:expr * B:expr) ** N:int -> A**N * B**N",
    "combine_powers"           : "X:expr**A:expr * X:expr**B:expr -> X**(A + B)",
    "power_of_power"           : "(X:expr**A:expr)**B:expr -> X**(A*B)",

    # LIKE TERMS
    "combine_like_terms"       : "X:expr + X:expr -> 2*X",
    "split_coefficient"        : "N:int * X:expr -> repeat(X,N,'+')",

    # EQUATIONS
    "equation_add_both_sides"  : "A:expr = B:expr | + C:expr -> A + C = B + C",
    "equation_mul_both_sides"  : "A:expr = B:expr | * C:expr -> A*C = B*C",

    # TRIG
    "pythagorean_identity"     : "sin(X:expr)**2 + cos(X:expr)**2 -> 1",
    "sin_to_cos_shift"         : "sin(X:expr) -> cos(X - pi/2)",
    "cos_to_sin_shift"         : "cos(X:expr) -> sin(X + pi/2)",

    # LOGIC
    # "double_negation"          : "not(not(A:expr)) -> A",
}


TESTS = {
    # STRUCTURAL
    "distribute"               : "3*(x + 1)",
    "factor"                   : "x*y + x*z",
    "commute_add"              : "x + y",
    "commute_mul"              : "x*y",
    "associate_add_left"       : "(x + y) + z",
    "associate_add_right"      : "x + (y + z)",
    "associate_mul_left"       : "(x*y)*z",
    "associate_mul_right"      : "x*(y*z)",
    "factor_common_rational"   : "x/3 + 1/3",
    "factor_common_rational_rev": "1/3 + x/3",
    "factor_common_rational_sympy": "1/3 + 1/3*x",

    # NUMERIC
    "evaluate_integer_add"     : "2 + 3",
    "evaluate_integer_mul"     : "2*3",
    "evaluate_integer_pow"     : "2**3",
    "expand_integer"           : "3*x",
    "reduce_fraction"          : "6/8",

    # FRACTIONS
    "factor_fraction_add"      : "x/3 + 1/3",
    "split_fraction_add"       : "(x + y)/z",
    "combine_fraction_add"     : "x/z + y/z",
    "multiply_fractions"       : "(a/b)*(c/d)",
    "divide_fractions"         : "(a/b)/(c/d)",
    "cancel_common_factor"     : "(x*y)/(x*z)",

    # POWERS
    "expand_power_integer"     : "x**3",
    "factor_power"             : "x*x",
    "power_product"            : "(a*b)**3",
    "combine_powers"           : "x**a * x**b",
    "power_of_power"           : "(x**a)**b",

    # LIKE TERMS
    "combine_like_terms"       : "x + x",
    "split_coefficient"        : "4*x",

    # EQUATIONS
    "equation_add_both_sides"  : "x = y | + 2",
    "equation_mul_both_sides"  : "x = y | * 3",

    # TRIG
    "pythagorean_identity"     : "sin(t)**2 + cos(t)**2",

    # LOGIC
    # "double_negation"          : "not(not(p))",
}
