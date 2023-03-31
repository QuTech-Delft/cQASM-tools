import numpy as np
from typing import Tuple


def find_closest(value: float, max_frac_res: int=100) -> Tuple:
    """ Simple utility function to check if a float is (close to) a fraction.

    Parameters
    ==========

    value : float
        Value of the float to check if it is (close to) a fraction.
    max_frac_res : int
        Fractional resolution. Default is 100.

    Returns
    =======
        Tuple with closest fraction information; numerator, denominator,
        fraction as float, input value, difference the closest fraction and
        input value.

    """
    sgn = np.sign(value)
    diff = 1.0
    table = []
    for row in range(0, max_frac_res + 1, 1):
        for col in range(1, max_frac_res + 1, 1):
            fraction = float(row / col)
            table.append((row, col, fraction))
    for i, j, f in table:
        temp_diff = abs(abs(value) - f)
        if temp_diff < diff:
            diff = temp_diff
            closest = (i, j, f * sgn, value, temp_diff)
    return closest