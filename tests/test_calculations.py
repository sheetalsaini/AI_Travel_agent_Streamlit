import ast
import math
from pathlib import Path
import unittest

from pydantic import ValidationError
from calculations import CalculationInput, calculate, build_calculation_tools


class CalculationTests(unittest.TestCase):
    def test_registered_tools_validate_and_execute(self):
        tools = {tool.name: tool for tool in build_calculation_tools()}
        self.assertEqual(set(tools), {"addition", "multiply", "division", "substraction"})
        self.assertEqual(tools["addition"].invoke({"a": 2.5, "b": 1}), 3.5)
        self.assertIsInstance(tools["multiply"].invoke({"a": "print(1)", "b": 2}), str)
        self.assertIsInstance(tools["division"].invoke({"a": 1, "b": 0}), str)
        self.assertIsInstance(tools["addition"].invoke({"a": 1, "b": 2, "code": "x"}), str)

    def test_travel_costs(self):
        for operation, a, b, expected in (
            ("addition", 12.50, 2.25, 14.75),
            ("multiply", 29.95, 4, 119.80),
            ("division", 120.50, 2, 60.25),
            ("substraction", 800, 119.80, 680.20),
            ("multiply", 250, 83.25, 20812.50),
        ):
            with self.subTest(operation=operation):
                self.assertAlmostEqual(calculate(operation, a, b), expected)

    def test_invalid_operands(self):
        for value in ("1", "__import__('os').getcwd()", True, None,
                      [], {}, math.inf, -math.inf, math.nan, 1e13):
            with self.subTest(value=value):
                with self.assertRaises(ValidationError):
                    calculate("addition", value, 1)

    def test_extra_fields_rejected(self):
        with self.assertRaises(ValidationError):
            CalculationInput(a=1, b=2, code="print('no')")

    def test_invalid_operation_and_zero(self):
        with self.assertRaises(ValueError):
            calculate("division", 1, 0)
        with self.assertRaises(ValueError):
            calculate("eval", 1, 2)
        with self.assertRaises(ValueError):
            calculate("division", 1e12, 1e-320)

    def test_app_has_no_code_execution_tool(self):
        source = (Path(__file__).resolve().parents[1] / "streamlit_app.py").read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self.assertFalse((node.module or "").startswith("langchain_experimental"))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"eval", "exec", "PythonREPL"})
        assignment = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == "tools" for t in n.targets))
        self.assertEqual([n.id for n in assignment.value.elts], [
            "addition", "multiply", "division", "substraction", "get_weather",
            "search_google", "search_duck", "youtube_search"])


if __name__ == "__main__":
    unittest.main()
