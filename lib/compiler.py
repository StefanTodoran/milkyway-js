import os
import re
import copy
from pathlib import Path

silent = False
def output(data):
  if not silent:
    print(data)

# =============== #
# FILE MANAGEMENT #

def readFileData(path: str):
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

def extractIfClause(string):
  pattern = r"\{\[\s*%\s*if\s+(?P<prop>[a-zA-Z]+)\s*\]\}"
  invertedPattern = r"\{\[\s*%\s*if\s+not\s+(?P<prop>[a-zA-Z]+)\s*\]\}"
  
  match = re.search(pattern, string)
  if match:
    return {
      "propName": match.group("prop"), 
      "inverted": False, 
      "start": match.start(),
      "end": match.end()
    }
  
  invertedMatch = re.search(invertedPattern, string)
  if invertedMatch:
    return {
      "propName": invertedMatch.group("prop"), 
      "inverted": True,
      "start": invertedMatch.start(),
      "end": invertedMatch.end()
    }
    
  return None

# =============== #
# DATA POPULATING #

def splitLineOnComponent(line):
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

def removeSubstring(string, start, end):
  return string[:start] + string[end+1:]

# Removes the section of a string between an
# if and its corresponding end if.
def removeIfSection(line, clause):
  start = clause["start"]
  end = line.find("{[ %endif ]}") + len("{[ %endif ]}") - 1
  return removeSubstring(line, start, end)

# Removes any if and any end if declarations from
# a string, leaves the rest of the string unchanged.
def removeIfClause(line):
  clause = extractIfClause(line)
  if not clause: return line

  start = clause["start"]
  end = clause["end"] - 1
  line = removeSubstring(line, start, end)
  
  start = line.find("{[ %endif ]}")
  end = start + len("{[ %endif ]}") - 1
  return removeSubstring(line, start, end)

def populateComponentData(lines: list, props: dict):
  for index in range(len(lines)):
    handleIfClause(lines, index, props)

    for prop, value in props.items():
      split = splitLineOnProp(lines[index], prop)
        
      if len(split) == 2:
        lines[index] = split[0] + value + split[1]

    lines[index] = removeProp(lines[index]) # In case there was no prop value given

  return lines

def handleIfClause(lines: list, index: int, props: dict):
  clause = extractIfClause(lines[index])
  targetPropFound = False
    
  for prop in props:
    if clause and clause["propName"] == prop:
      targetPropFound = True
    
      if clause["inverted"]:
        # If we have an if clause of the form {[ %if not prop ]}
        lines[index] = removeIfSection(lines[index], clause)
  
  if clause and not clause["inverted"] and not targetPropFound:
    # If we have an if clause of the form {[ %if prop ]} and prop's value was not specified
    lines[index] = removeIfSection(lines[index], clause)

  lines[index] = removeIfClause(lines[index]) # In case if didn't trigger

  # Check if there is another if on the line
  clause = extractIfClause(lines[index])
  if clause: handleIfClause(lines, index, props)

# ======== #
#   MISC   #

def concatenateComponentLines(lines):
  newLines = []
  currentComponent = None

  line: str
  for line in lines:
    componentStart = line.find("<!-- %MLKY")
    componentEnd = line.find("-->")

    if currentComponent:
      currentComponent += " " + line.strip()

      if componentStart != -1:
        raise SyntaxError("Cannot declare a component inside another component!")
      
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

def compile(doOutput = True):
  global silent
  silent = not doOutput
  output("\nStarting MilkywayJS compilation...")

  pages = locateAllPages("./pages/")
  for page in pages:
    
    pageLines = readFileData(page)
    pageLines = concatenateComponentLines(pageLines) # This way our logic for component substitution can assume one line components

    writeLines = copy.copy(pageLines)
    index = 0

    for line in pageLines:
      component = extractComponentData(line)
    
      if component:
        name = component["name"]
        output(f"Found '{name}' component indicator, searching for file...")
        
        path = "./components/" + name.lower() + ".mcomp"
        if not os.path.exists(path):
          raise NameError(path + " does not exist!")

        # Note that writeLines.pop(index) == line, it's the same line!
        splitLine = splitLineOnComponent(writeLines.pop(index))
        componentLines = readFileData(path)
        componentLines = populateComponentData(componentLines, component["props"])

        # We do this to essentially "insert" the component
        # between whatever tags lie on either side of the indicator.
        componentLines[0] = splitLine[0] + componentLines[0]
        componentLines[-1] = componentLines[-1] + splitLine[1]

        writeLines[index:index] = componentLines
        index += len(componentLines) - 1

      index += 1

    writeDataToFile(getSavePath(page), writeLines)

  output(f"Compiled all {len(pages)} HTML files found\n")

if __name__ == "__main__":
  compile()