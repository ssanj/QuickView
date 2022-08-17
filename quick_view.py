import sublime
import sublime_plugin
from typing import Optional, List
import re
from QuickView.components.scala import Scala

class QuickViewCommand(sublime_plugin.TextCommand):

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

        scala = Scala()
        return scala.enhance(lines, target_line, line-1)
      else:
        return lines[line-1]
    else:
      return None



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
