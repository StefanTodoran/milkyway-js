import os
import shutil
from pathlib import Path

# ======= #
# HELPERS #

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

def migrateAll(root: str, dest: str, dir: str, glob: str):
  if not os.path.exists(dest + dir):
    os.makedirs(dest + dir)

  files = locateAll(root + dir, glob)
  for file in files:
    shutil.copyfile(file, dest / file)
  print(f"Migrated all {len(files)} {glob} files to production\n")

# ======== #
#   MAIN   #

def migrate(outDir: str = "dist/"):
  print("\nBuilding site to production...")

  root = "./"
  dest = "./docs/"

  if os.path.exists(dest):
    print("Clearing previous build...", end=" ")
    shutil.rmtree(dest)
    print("done.\n")
  
  migrateAll(root, dest, "", "*.html")
  migrateAll(root, dest, outDir, "*.js")
  migrateAll(root, dest, outDir, "*.min.css")

  print("Recursively copying all assets to produciton...", end=" ")
  shutil.copytree(root + "assets/", dest + "assets/")
  print("done.\n")

if __name__ == "__main__":
  compile()