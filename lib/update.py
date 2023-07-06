from pathlib import Path
import requests

def locateAll(root: str, glob: str, ignore: list):
  dir = Path(root)
  all = sorted(dir.glob(glob))
  print(f"Located {len(all)} {glob} files: {[str(file) for file in all]}")

  if ignore:
    ignore = {str(Path(root) / file) for file in ignore}
    files = [file for file in all if str(file) not in ignore]
    pruned = list(set(all) - set(files))
    print(f"Ignored {len(pruned)} of located files: {[str(file) for file in pruned]}")
    return files
  else:
    return all

def writeDataToFile(path: str, lines: list):
  print("Writing data to " + path)

  with open(path, "w", encoding="utf8") as file:
    file.writelines(lines)

def updateScript(path, url):
  source = url + path
  raw = requests.get(source)
  writeDataToFile(path, raw.text)

# ======== #
#   MAIN   #

def update(updateSource = "https://raw.githubusercontent.com/StefanTodoran/milkyway-js/main/"):
  print("\nUpdating MilkywayJS...")

  libs = locateAll("./lib/", "*.py", ["__init__.py", "update.py"])
  paths = [str(file).replace("\\", "/") for file in libs]
  
  for path in paths:
    updateScript(path, updateSource)
  updateScript("manage.py", updateSource)

  print(f"Updated all {len(libs)} lib files!\n")

if __name__ == "__main__":
  update()
  exit("Update complete! Press CTRL+C to exit.")