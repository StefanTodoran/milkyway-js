import os
import shutil
from pathlib import Path

# ======= #
# HELPERS #

def locateAll(root: str, glob: str):
  dir = Path(root)
  files = sorted(dir.glob(glob))
  print(f"Located {len(files)} {glob} files: {[str(file) for file in files]}")
  return files

def migrateAll(root: str, dest: str, dir: str, glob: str):
  if not os.path.exists(dest + dir):
    os.makedirs(dest + dir)

  files = locateAll(root + dir, glob)
  for file in files:
    shutil.copyfile(file, dest / file)
  print(f"Migrated all {len(files)} {glob} files to production\n")

# ======== #
#   MAIN   #

def migrate():
  print("\nBuilding site to production...")

  root = "./"
  dest = "./docs/"

  if os.path.exists(dest):
    print("Clearing previous build...", end=" ")
    shutil.rmtree(dest)
    print("done.\n")
  
  migrateAll(root, dest, "", "*.html")
  migrateAll(root, dest, "dist/", "*.js")
  migrateAll(root, dest, "dist/", "*.min.css")

  print("Recursively copying all assets to produciton...", end=" ")
  shutil.copytree(root + "assets/", dest + "assets/")
  print("done.\n")

if __name__ == "__main__":
  compile()