import requests

from lib.build import locateAll

silent = False
def output(data, warn = False):
  if silent: return
  if warn:
    print("WARN > " + data)
  else:
    print(data)

def writeDataToFile(path: str, lines: list):
  output("Writing data to " + path)

  with open(path, "w", encoding="utf8") as file:
    file.writelines(lines)

# ======== #
#   MAIN   #

def update(doOutput = True, updateSource = "https://raw.githubusercontent.com/StefanTodoran/milkyway-js/main/"):
  global silent
  silent = not doOutput
  output("\nUpdating MilkywayJS...")

  libs = locateAll("./lib/", "*.py", ["__init__.py", "update.py"])
  paths = [str(file).replace("\\", "/") for file in libs]
  
  for path in paths:
    source = updateSource + path
    raw = requests.get(source)
    writeDataToFile(path, raw)

  output(f"Compiled all {len(libs)} lib files\n")

if __name__ == "__main__":
  update()