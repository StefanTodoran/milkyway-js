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
    pattern = r"<!--\s*%MILKY\s*([A-Za-z\-]+)\s*-->"
    match = re.search(pattern, line)
    if match:
        component_name = match.group(1)
        return component_name.strip()
    else:
        return None

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
      component = extractComponentName(line)
    
      if component:
        output(f"Found '{component}' component indicator, searching for file...")
        path = "./components/" + component.lower() + ".mcomp"
        if not os.path.exists(path):
          raise NameError(path + " does not exist!")
        
        componentLines = readFileData(path)
        if componentLines[-1] != "\n":
          componentLines[-1] += "\n"

        writeLines.pop(index)
        writeLines[index:index] = componentLines

      index += 1

    writeDataToFile(getSavePath(page), writeLines)

  print(f"Compiled all {len(pages)} HTML files found\n")

if __name__ == "__main__":
  compile()