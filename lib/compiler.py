import os
import re
import copy
from pathlib import Path

from css_html_js_minify import process_single_html_file
from lib.utils import formatLog, logStatus, output, setOutputMode

# =============== #
# FILE MANAGEMENT #

def readFileData(path: str | Path) -> list[str]:
  output("Reading HTML data from " + str(path))

  with open(path, "r", encoding="utf8") as file:
    lines = file.readlines()

  return lines

def writeDataToFile(path: str, lines: list):
  output("Writing compiled HTML data to " + path)

  with open(path, "w", encoding="utf8") as file:
    file.writelines(lines)

def getSavePath(path):
  filename = os.path.basename(path)
  base, extension = os.path.splitext(filename)
  return base + ".html"

def locateAllPages(root: str = ""):
  dir = Path(root)
  pages = sorted(dir.glob("*.mhtml"))
  output(f"Located {len(pages)} site pages...")
  return pages

# =============== #
# DATA EXTRACTION #

def extractComponentData(line: str):
  pattern = r"<!--\s*%MLKY\s+(\w+(?:-\w+)*)\s+([a-zA-Z]+=\"[^\"]*\s*\"(?:\s+[a-zA-Z]+=\"[^\"]*\s*\")*)*\s*-->"
  match = re.search(pattern, line)

  if not match:
    return None
  
  componentName = match.group(1)
  rawProps = match.group(2)
  props = {}

  if rawProps:
    propPattern = r"([a-zA-Z]+)=\"([^\"]*)\""
    propMatches = re.findall(propPattern, rawProps)
    props = {name: value for name, value in propMatches}

  return {"name": componentName, "props": props}

def extractPropName(line):
  propName = re.findall(r"{{\s*([A-Za-z]+)\s*}}", line)
  return propName

def getNthMatch(pattern, string, n):
  match = None
  matches = re.finditer(pattern, string)
  current = 0

  for m in matches:
    if current != n:
      current += 1
    else:
      match = m
      break

  return match

# Returns an object describing the n-th if clause
# on the provided line, n being the number parameter.
def extractIfClause(string, number = 0):
  endPattern = r"{\[ %endif ]}"
  end = re.findall(endPattern, string)

  pattern = r"\{\[\s*%if\s+(not\s+)?([a-zA-Z]+)(?:=\"(.+?)\")?\s*\]\}"
  match = getNthMatch(pattern, string, number)
  
  if match:
    inverted = bool(match.group(1))
    propName = match.group(2)
    value = match.group(3) or True

    return {
      "propName": propName,
      "value": value,
      "inverted": inverted,
      "start": match.start(),
      "end": match.end(),
      "inline": len(end) > number
    }
    
  return None

# =============== #
# DATA POPULATING #

def splitLineOnComponent(line) -> list[str]:
  pattern = r"<!--\s*%MLKY.*?\s*-->"
  parts = re.split(pattern, line)
  return parts

def splitLineOnProp(line, prop):
  pattern = r"{{\s*" + prop + r"\s*}}"
  parts = re.split(pattern, line)
  return parts

def removeProp(string):
  pattern = r"\{\{\s*[a-zA-Z]+\s*\}\}"
  return re.sub(pattern, "", string)

def populateComponentData(lines: list, props: dict):
  for index in range(len(lines)):
    for prop, value in props.items():
      parts = splitLineOnProp(lines[index], prop)
      
      if len(parts) > 1:
        lines[index] = value.join(parts)

    lines[index] = removeProp(lines[index]) # In case there was no prop value given

# =============== #
# IF CLAUSE LOGIC #

endIfToken = "{[ %endif ]}"

def fixEndIfTokens(line):
    pattern = r"{\[\s*%endif\s*\]}"
    fixed = re.sub(pattern, endIfToken, line)
    return fixed

def removeSubstring(string, start, end):
  return string[:start] + string[end+1:]

# Removes the section of a string between an
# if and its corresponding end if.
def removeIfSection(line, clause):
  start = clause["start"]
  end = line.find(endIfToken) + len(endIfToken) - 1
  return removeSubstring(line, start, end)

# Removes any if and any end if declarations from
# a string, leaves the rest of the string unchanged.
def removeIfClause(line):
  clause = extractIfClause(line)
  if clause:
    start = clause["start"]
    end = clause["end"] - 1
    line = removeSubstring(line, start, end)
  
  start = line.find(endIfToken)
  if start != -1:
    end = start + len(endIfToken) - 1
    line = removeSubstring(line, start, end)

  return line

def isIfClauseSatisfied(clause: dict, props: dict):
  for prop in props:
    if clause["propName"] == prop:
      if clause["value"] == True or clause["value"] == props[prop]:
        return not clause["inverted"]
    
  return clause["inverted"]

def handleInlineIfClauses(lines: list, index: int, props: dict, current: int = 0):
  clause = extractIfClause(lines[index], current)

  if not clause:
    return
  
  if not clause["inline"]:
    handleInlineIfClauses(lines, index, props, current + 1)
    return
  
  if not isIfClauseSatisfied(clause, props):
    # If we have an if clause of the form {[ %if not prop ]} and prop supplied, or
    # we have an if clause of the form {[ %if prop ]} and prop's value was not specified
    lines[index] = removeIfSection(lines[index], clause)
    current -= 1

  lines[index] = removeIfClause(lines[index]) # In case if didn't trigger
  handleInlineIfClauses(lines, index, props, current)

def handleComponentIfLogic(lines: list, props: dict):
  for index in range(len(lines)):
    lines[index] = fixEndIfTokens(lines[index])
    handleInlineIfClauses(lines, index, props)

  nestedIfs = []
  index = 0
  while index < len(lines):
    clause = extractIfClause(lines[index])
    endClause = lines[index].find(endIfToken)

    # There should never be both a clause and an endClause, because
    # that would constitute an inline if, which should have been handled.
    if (clause and clause["inline"]) or (clause and endClause != -1):
      output("Encountered inline if logic when all should have been handled. Output may be corrupted.", True)

    if endClause != -1:
      if len(nestedIfs) == 0: raise SyntaxError(formatLog("Encountered endif when no if clause had been opened!", logStatus.FAIL))
      innerMost = nestedIfs.pop()

      if not isIfClauseSatisfied(innerMost["clause"], props):
        for _ in range(index - innerMost["start"] + 1):
          lines.pop(innerMost["start"])
        index = innerMost["start"] - 1
      else:
        lines[innerMost["start"]] = removeIfClause(lines[index])
        lines[index] = removeIfClause(lines[index])

    if clause:
      nestedIfs.append({
        "start": index,
        "clause": clause
      })

    index += 1

# ======== #
#   MISC   #

# Returns a list of strings representing the lines of the component, properly populated
# with data and with logic executed. Note that this may mutate the provided list.
def getComponentInsert(writeLines: list, index: int) -> list[str] | None:
  component = extractComponentData(writeLines[index])

  if component:
    name = component["name"]
    output(f"Found '{name}' component indicator, searching for file...")
    
    path = "./components/" + name.lower() + ".mcomp"
    if not os.path.exists(path):
      raise FileNotFoundError(formatLog("(!) " + path + " does not exist!", logStatus.FAIL))

    splitLine = splitLineOnComponent(writeLines.pop(index))
    componentLines = readFileData(path)

    handleComponentIfLogic(componentLines, component["props"])
    populateComponentData(componentLines, component["props"])

    if len(componentLines) == 0:
      # Due to if statements, the component is empty
      return

    # We do this to essentially "insert" the component
    # between whatever tags lie on either side of the indicator.
    componentLines[0] = splitLine[0] + componentLines[0]
    componentLines[-1] = componentLines[-1] + splitLine[1]
    return componentLines

# Inserts the provided component lines at the specified index in the write
# lines, then returns the new index position (end of the inserted component).
def insertComponentLines(componentLines: list, writeLines: list, index: int):
  writeLines[index:index] = componentLines
  return index + len(componentLines) - 1

# Given a list of string lines and an index, if there is a component on the target line,
# replaces the component token with the component lines, populates the component's props,
# executes the component's if clause logic, and recurses on any nested components. Returns
# the new index position (the end of the inserted component).
def handleComponent(writeLines: list, index: int):
  componentLines = getComponentInsert(writeLines, index)
  if componentLines:
    return insertComponentLines(componentLines, writeLines, index)
  return index

def concatenateComponentLines(lines) -> list[str]:
  newLines = []
  currentComponent = None

  line: str
  for line in lines:
    componentStart = line.find("<!-- %MLKY")
    componentEnd = line.find("-->")

    if currentComponent:
      currentComponent += " " + line.strip()

      if componentStart != -1:
        raise SyntaxError(formatLog("Cannot declare a component inside another component!", logStatus.FAIL))
      
      if componentEnd != -1:
        newLines.append(currentComponent)
        currentComponent = None

    else:
      
      if componentStart != -1 and componentEnd == -1:
        currentComponent = line[componentStart:].strip()
        newLines.append(line[:componentStart])

      else: # Either no component or one line component
        newLines.append(line)

  return newLines

# ======== #
#   MAIN   #

def compileFile(targetFile, doOutput = True, minifyOutput = False):
  setOutputMode(not doOutput)
    
  pageLines = readFileData(targetFile)
  writeLines = copy.copy(pageLines)

  # We initialize this to True since there is no "do while"
  # construct in Python for some reason...
  foundComponent = True

  while foundComponent:
    foundComponent = False
    writeLines = concatenateComponentLines(writeLines) # This way our logic for component substitution can assume one line components
    
    index = 0
    for _ in range(len(writeLines)):
      componentLines = getComponentInsert(writeLines, index)
      if componentLines:
        foundComponent = True
        index = insertComponentLines(componentLines, writeLines, index)

      index += 1

  outputPath = getSavePath(targetFile)
  writeDataToFile(outputPath, writeLines)
  
  if minifyOutput:
    process_single_html_file(outputPath, overwrite=True, output_path=outputPath)

def compile(doOutput = True, minifyOutput = False):
  setOutputMode(not doOutput)
  output("Starting MilkywayJS compilation...", logStatus.EMPHASIS, newLine=True)

  pages = locateAllPages("./pages/")
  for page in pages:
    compileFile(page, doOutput, minifyOutput)

  output(f"Compiled all {len(pages)} HTML files found\n", logStatus.GOOD)

if __name__ == "__main__":
  compile()