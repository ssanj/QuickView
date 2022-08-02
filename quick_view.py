import sublime
import sublime_plugin
from typing import Optional, List
from OpenSplit.target_file import TargetFile
import re

class QuickViewCommand(sublime_plugin.TextCommand):

  sealed_trait_r = re.compile(r"sealed trait ([A-Z][0-9A-Za-z_]*)")
  trait_r = re.compile(r"trait [A-Z][0-9A-Za-z_]*\s+{")


  def run(self, edit):
    view = self.view
    window = view.window()

    if window:
      if (text := self.has_selected_word(view.sel())) is not None:
        print(f"found symbol: {text}")
        symbol = window.symbol_locations(text, type=sublime.SYMBOL_TYPE_DEFINITION)

        if len(symbol) > 0:
          print(f"{symbol}")
          result = self.read_symbol_from_file(symbol[0])
          if result:
            print(f"received: {result}")
            self.show_popup(result)
          else:
            print(f"not result")
        else:
          print("symbol is empty")
      else:
        print("Invalid word selected")
    else:
      print("No active window found")

  def read_symbol_from_file(self, symbol_location: sublime.SymbolLocation) -> Optional[str]:
    line = symbol_location.row
    path = symbol_location.path

    with open(path, 'r') as f:
      lines: list[str] = f.readlines()

    if len(lines) >= line and line > 0:
      target_line = lines[line-1].lstrip().rstrip()
      syntax: Optional[sublime.Syntax] = self.view.syntax()
      # TODO: move out
      if syntax and syntax.scope == "source.scala":
        return self.enhance_scala(lines, target_line, line-1)
      else:
        return lines[line-1]
    else:
      return None

  def enhance_scala(self, lines: List[str], line: str, line_index: int) -> str:
    print(f"---------> [{line}]")
    if QuickViewCommand.sealed_trait_r.match(line):
      return self.handle_sealed_traits(lines, line, line_index)
    elif QuickViewCommand.trait_r.match(line):
      return self.handle_traits(lines, line, line_index)
    else:
      print("------------> no matches")
      return line

  def handle_sealed_traits(self, lines: List[str], line: str, line_index: int) -> str:
    matched_extensions: List[str] = self.find_matching_sealed_trait_extensions(0, lines, line)
    matched_extensions.insert(0, line)

    # if matched_extension are also sealed, then recurse
    # TODO: do this only if there's at least a single extension
    other_matches: List[str] = []
    # other_lines = list(filter(lambda l: l != line, lines))
    # for me in matched_extensions:
    #   other_matches += self.find_matching_sealed_trait_extensions(1, other_lines, me)

    # matched_extensions.insert(0, line)
    all_matches: List[str] = matched_extensions + other_matches
    return "\n".join(all_matches)

  def find_matching_sealed_trait_extensions(self, depth: int, lines: List[str], line: str) -> List[str]:
    matches: Optional[re.Match] = QuickViewCommand.sealed_trait_r.match(line)
    if matches:
      groups = matches.groups()
      if groups and len(groups) > 0:
        trait_name = groups[0]
        extends_sealed_trait = f"extends {trait_name}"
        prefix = "++" * depth
        matched_extensions: List[str] = [f"{prefix} {l}" for l in lines if extends_sealed_trait in l]
        return matched_extensions
      else:
        return []
    else:
      return []


  def handle_traits(self, lines: List[str], line: str, line_index: int) -> str:
    print("trait matched with {")
    current_line: int = line_index + 1 # move to next line
    following_lines: List[str] = []
    length_of_lines: int = len(lines)

    while length_of_lines > current_line:
      next_line = lines[current_line]
      if (next_line.lstrip().rstrip() == "}"):
        break
      else:
        following_lines.append(next_line.lstrip().rstrip().replace("def", "+"))
        current_line += 1

    following_lines.insert(0, line.strip("{").lstrip().rstrip())
    return "\n".join(following_lines)

  def has_selected_word(self, selection: sublime.Selection) -> Optional[str]:
    if len(selection) > 0:
      view = self.view
      possible_word = view.substr(view.word(selection[0]))
      if possible_word and possible_word.lstrip():
        word = possible_word.lstrip()
      else:
        word = None
    else:
      word = None

    return word

  def show_popup(self, content: str) -> None:
    lines = content.split("\n")

    formatted_lines = "".join(list(map(lambda l: f"<div>{l}</div>", lines)))

    markup = f'''
        <body id="open-split">
            <style>
                    body#open-split {{
                      background-color:  white;
                      color: color(var(--bluish));
                    }}
            </style>
            <div>{formatted_lines}</div>
        </body>
    '''
    self.view.show_popup(content = markup, max_width = 1200, max_height = 800, flags = sublime.HIDE_ON_MOUSE_MOVE_AWAY)
