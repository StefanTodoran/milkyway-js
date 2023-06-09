import os
import copy
import shutil
from pathlib import Path

silent = False
def output(data):
  if not silent:
    print(data)

# ======= #
# HELPERS #

def locateAll(root: str, glob: str):
  dir = Path(root)
  files = sorted(dir.glob(glob))
  output(f"Located {len(files)} {glob} files: {files}")
  return files

def migrateAll(root: str, dest: str, dir: str, glob: str):
  print(dest + dir)
  if not os.path.exists(dest + dir):
    os.makedirs(dest + dir)

  files = locateAll(root + dir, glob)
  for file in files:
    shutil.copyfile(file, dest / file)
  output(f"Migrated all {len(files)} {glob} files to production\n")

# ======== #
#   MAIN   #

def migrate(doOutput = True):
  global silent
  silent = not doOutput
  output("\nBuilding site to production...")

  root = "./"
  dest = "./docs/"
  
  migrateAll(root, dest, "", "*.html")
  migrateAll(root, dest, "dist/", "*.js")

if __name__ == "__main__":
  compile()