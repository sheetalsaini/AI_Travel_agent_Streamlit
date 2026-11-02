"""Allowlisted calculations. Inputs are numbers, never executable expressions."""
import math
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Number = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=-1e12, le=1e12)]


class CalculationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    a: Number
    b: Number


def calculate(operation: str, a: float, b: float) -> float:
    """Validate operands and apply exactly one known arithmetic operation."""
    values = CalculationInput(a=a, b=b)
    a, b = values.a, values.b
    if operation == "addition":
        result = a + b
    elif operation == "multiply":
        result = a * b
    elif operation == "division":
        if b == 0:
            raise ValueError("Denominator cannot be zero.")
        result = a / b
    elif operation == "substraction":
        result = a - b
    else:
        raise ValueError("Unsupported calculation operation.")
    if not math.isfinite(result):
        raise ValueError("Calculation result must be finite.")
    return result


def build_calculation_tools():
    """Create typed LangChain tools without loading Streamlit or credentials."""
    from langchain_core.tools import StructuredTool, ToolException

    def make_tool(name, description):
        def run(a: float, b: float) -> float:
            try:
                return calculate(name, a, b)
            except ValueError as error:
                raise ToolException(str(error)) from error

        return StructuredTool.from_function(
            func=run, name=name, description=description,
            args_schema=CalculationInput, handle_validation_error=True,
            handle_tool_error=True,
        )

    return [make_tool(name, description) for name, description in (
        ("addition", "Add two finite numbers, including decimal travel costs."),
        ("multiply", "Multiply two finite numbers, including costs or exchange rates."),
        ("division", "Divide two finite numbers. Denominator must not be zero."),
        ("substraction", "Subtract b from a, including decimal travel costs."),
    )]
