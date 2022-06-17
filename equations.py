def taylor_1993_equation(inflation, output_gap):
    return 1.25 + inflation + 0.5 * (inflation - 2) + 0.5 * output_gap

def taylor_1999_equation(inflation, output_gap):
    return 1.25 + inflation + 0.5 * (inflation - 2) + output_gap

def inertial_taylor_1999_equation(inflation, output_gap, prev_ffr):
    return 0.85 * prev_ffr + 0.15 * (1.25 + inflation + 0.5 * (inflation - 2) + output_gap)

def first_difference_rule_equation(prev_ffr, three_quarter_ahead_inflation, three_quarter_ahead_change_in_output_gap):
    return prev_ffr + 0.5 * (three_quarter_ahead_inflation - 2) + 0.5 * (three_quarter_ahead_change_in_output_gap)