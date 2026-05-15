
#test_calc.py



from dotenv import load_dotenv

import datetime
import os


# Load environment variables from .env
load_dotenv()


def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Parameters
    ----------
    a : float
        First operand.
    b : float
        Second operand.

    Returns
    -------
    float
        Sum of a and b.
    """
    return a + b

def subtract(a: float, b: float) -> float:
    """
    Subtract b from a.

    Parameters
    ----------
    a : float
        Number to subtract from.
    b : float
        Number to subtract.

    Returns
    -------
    float
        Difference of a and b.
    """
    return a - b

def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Parameters
    ----------
    a : float
        First factor.
    b : float
        Second factor.

    Returns
    -------
    float
        Product of a and b.
    """
    return a * b

def divide(a: float, b: float) -> float:
    """
    Divide a by b.

    Parameters
    ----------
    a : float
        Dividend.
    b : float
        Divisor.

    Returns
    -------
    float
        Quotient of a divided by b.

    Raises
    ------
    ValueError
        If b is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

result = multiply(4, 5)
print(result)

