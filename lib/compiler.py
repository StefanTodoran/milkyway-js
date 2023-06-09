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
  pattern = r"<!--\s*%MLKY\s+(\w+(?:-\w+)*)\s*([a-zA-Z]+=\"[^\"]*\s*\"(?:\s+[a-zA-Z]+=\"[^\"]*\s*\")*)*\s*-->"
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

def splitLineOnComponent(line):
  pattern = r"<!--\s*%MLKY.*?\s*-->"
  parts = re.split(pattern, line)
  return parts

def extractPropName(line):
  propName = re.findall(r"{{\s*([A-Za-z]+)\s*}}", line)
  return propName

def splitLineOnProp(line, prop):
  pattern = r"{{\s*" + prop + r"\s*}}"
  parts = re.split(pattern, line)
  return parts

# =============== #
# DATA POPULATING #

def populateComponentData(lines: list, props: dict):
  index = 0
  for line in lines:
    for prop, value in props.items():
      split = splitLineOnProp(line, prop)
      
      if len(split) == 2:
        lines[index] = split[0] + value + split[1]
    
    index += 1
  return lines

# ======== #
#   MAIN   #

def compile(doOutput = True):
  global silent
  silent = not doOutput
  output("\nStarting MilkywayJS compilation...")

  pages = locateAllPages("./pages/")
  for page in pages:
    
    pageLines = readFileData(page)
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

        # if componentLines[-1] != "\n":
        #   componentLines[-1] += "\n"

        writeLines[index:index] = componentLines
        index += len(componentLines) - 1

      index += 1

    writeDataToFile(getSavePath(page), writeLines)

  output(f"Compiled all {len(pages)} HTML files found\n")

if __name__ == "__main__":
  compile()