from typing import Optional, List
import re

class Scala:

  sealed_trait_r = re.compile(r"sealed trait ([A-Z][0-9A-Za-z_]*)")
  trait_r = re.compile(r"trait [A-Z][0-9A-Za-z_]*\s+{")
  block_start = "{"
  block_end = "}"


  @staticmethod
  def enhance(lines: List[str], line: str, line_index: int) -> str:
    print(f"---------> [{line}]")
    if Scala.sealed_trait_r.match(line):
      return Scala.handle_sealed_traits(lines, line, line_index)
    elif Scala.trait_r.match(line):
      return Scala.handle_multiline_traits(lines, line, line_index)
    else:
      print("------------> no matches")
      return line

  @staticmethod
  def handle_sealed_traits(lines: List[str], line: str, line_index: int) -> str:
    matched_extensions: List[str] = Scala.find_matching_sealed_trait_extensions(0, lines, line)
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

  @staticmethod
  def find_matching_sealed_trait_extensions(depth: int, lines: List[str], line: str) -> List[str]:
    matches: Optional[re.Match] = Scala.sealed_trait_r.match(line)
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


  @staticmethod
  def handle_multiline_traits(lines: List[str], line: str, line_index: int) -> str:
    block: List[str] = Scala.get_block(Scala.block_end, lines, line_index)

    if len(block) > 0:
      heading: str = Scala.clean_line(line, [Scala.block_start])
      body: List[str] = list(map(lambda l: Scala.clean_line(l), block))
      body.insert(0, heading)

      return "\n".join(body)
    else:
      return line

  @staticmethod
  def clean_line(line: str, tokens_to_remove: List[str] = []) -> str:
    cleaned = line

    for t in tokens_to_remove:
      cleaned = cleaned.replace(t, "")

    # remove space characters after de-tokenizing otherwise you end up with extra spaces
    return cleaned.lstrip().rstrip()


  @staticmethod
  def get_block(closer: str, lines: List[str], line_index: int) -> List[str]:
    current_line: int = line_index + 1 # move to next line
    following_lines: List[str] = []
    length_of_lines: int = len(lines)

    while length_of_lines > current_line:
      next_line = lines[current_line]
      if (next_line.lstrip().rstrip() == closer):
        break
      else:
        following_lines.append(Scala.clean_line(next_line))
        current_line += 1

    return following_lines
