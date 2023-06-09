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
    file.close()

  return lines

def writeDataToFile(path: str, lines: list):
  output("Writing compiled HTML data to " + path)

  with open(path, "w", encoding="utf8") as file:
    file.writelines(lines)

# =============== #
# DATA EXTRACTION #

def locateAllPages(root: str = ""):
  dir = Path(root)
  pages = sorted(dir.glob("*.mhtml"))
  output(f"Located {len(pages)} site pages...")
  return pages

def extractComponentName(line):
  pattern = r"<!--\s*%MLKY\s*([A-Za-z\-]+)\s*-->"
  match = re.search(pattern, line)
  if match:
      component_name = match.group(1)
      return component_name.strip()
  else:
      return None

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

def splitLineOnComponent(line, componentName):
  pattern = r"<!--\s*%MLKY\s*" + re.escape(componentName) + r"\s*-->"
  parts = re.split(pattern, line)
  return parts

def getSavePath(path):
  filename = os.path.basename(path)
  base, extension = os.path.splitext(filename)
  return base + ".html"

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
      # component = extractComponentName(line)
      component = extractComponentData(line)
    
      if component:
        name = component["name"]
        output(f"Found '{name}' component indicator, searching for file...")
        
        path = "./components/" + name.lower() + ".mcomp"
        if not os.path.exists(path):
          raise NameError(path + " does not exist!")

        # Note that writeLines.pop(index) == line, it's the same line!
        splitLine = splitLineOnComponent(writeLines.pop(index), name)
        componentLines = readFileData(path)

        print(component["props"])

        # We do this to essentially "insert" the component
        # between whatever tags lie on either side of the indicator.
        componentLines[0] = splitLine[0] + componentLines[0]
        componentLines[-1] = componentLines[-1] + splitLine[1]

        if componentLines[-1] != "\n":
          componentLines[-1] += "\n"

        writeLines[index:index] = componentLines

      index += 1

    writeDataToFile(getSavePath(page), writeLines)

  print(f"Compiled all {len(pages)} HTML files found\n")

if __name__ == "__main__":
  compile()