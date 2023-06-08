import sys
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

  with open(path, "r") as file:
    lines = file.readlines()
    file.close()

  return lines

def writeDataToFile(path: str, lines: list):
  output("Writing compiled HTML data to " + path)

  with open(path, "w") as file:
    file.writelines(lines)

# =============== #
# DATA EXTRACTION #

def locateAllPages(root: str = ""):
  dir = Path(root)
  pages = sorted(dir.glob("*.html"))
  output(f"Located {len(pages)} site pages...")
  return pages

def extractComponentName(line):
    pattern = r"<!--\s*%MWC\s*([A-Za-z]+)\s*-->"
    match = re.search(pattern, line)
    if match:
        component_name = match.group(1)
        return component_name.strip()
    else:
        return None

# ======== #
#   MAIN   #

def main():
  global silent
  silent = False
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
        path = "./components/" + component.lower() + ".mwc"
        if not os.path.exists(path):
          raise NameError(path + " does not exist!")
        
        componentLines = readFileData(path)
        writeLines.pop(index)
        writeLines[index:index] = componentLines

      index += 1

    writeDataToFile(os.path.basename(page), writeLines)

if __name__ == "__main__":
  main()