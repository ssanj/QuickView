import unittest
from typing import Optional, List
from QuickView.components.scala import Scala

class QuickViewScalaTest(unittest.TestCase):

  def test_handle_traits_(self):
    # handle_traits(lines: List[str], line: str, line_index: int) -> str
    line: str = "trait Testable {"
    lines: List[str] = \
      [
        "// some other stuff here 1",
        "// some other stuff here 2",
        "// some other stuff here 3",
        "trait Testable {",
        "  type Actual",
        "  val value1: Defer[Actual]",
        "  val value2: Defer[Actual]",
        "  val equality: Equality[Actual]",
        "  val difference: Difference[Actual]",
        "  val equalityType: EqualityType",
        "}",
        "// some other stuff here 4"
      ]

    line_index = 3

    expected: List[str] = \
      [
        "trait Testable",
        "type Actual",
        "val value1: Defer[Actual]",
        "val value2: Defer[Actual]",
        "val equality: Equality[Actual]",
        "val difference: Difference[Actual]",
        "val equalityType: EqualityType"
      ]

    result = Scala.handle_multiline_traits(lines, line, line_index)

    actual: List[str] = result.split("\n")
    self.assertSequenceEqual(expected, actual)

