import os
import shutil
from lib.utils import locateAll, logStatus, output

# ======= #
# HELPERS #

def migrateAll(root: str, dest: str, dir: str, glob: str):
  if not os.path.exists(dest + dir):
    os.makedirs(dest + dir)

  files = locateAll(root + dir, glob)
  for file in files:
    shutil.copyfile(file, dest / file)
  output(f"Migrated all {len(files)} {glob} files to production\n")

# ======== #
#   MAIN   #

def migrate(outDir: str = "dist/"):
  output("Building site to production...", logStatus.EMPHASIS, newLine=True)

  root = "./"
  dest = "./docs/"

  if os.path.exists(dest):
    output("Clearing previous build...", logStatus.WARN, end=" ")
    shutil.rmtree(dest)
    output("done.\n")
  
  migrateAll(root, dest, "", "*.html")
  migrateAll(root, dest, outDir, "*.js")
  migrateAll(root, dest, outDir, "*.min.css")

  output("Recursively copying all assets to produciton...", logStatus.GOOD, end=" ")
  shutil.copytree(root + "assets/", dest + "assets/")
  output("done.\n")

if __name__ == "__main__":
  compile()