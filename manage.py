import sys
import os
import re
import json
from lib.server import serve
from lib.build import migrate

intro = r"""
        _ _ _                               __  __    
  /\/\ (_) | | ___   ___      ____ _ _   _  \ \/ _\   
 /    \| | | |/ / | | \ \ /\ / / _` | | | |  \ \ \    
/ /\/\ \ | |   <| |_| |\ V  V / (_| | |_| /\_/ /\ \   
\/    \/_|_|_|\_\\__, | \_/\_/ \__,_|\__, \___/\__/   
                 |___/               |___/            
            - Workflow Management Script -            
"""

# ======== #
# SETTINGS #

def readJSONWithComments(path: str):
  with open(path, "r") as file:
    content = file.read()
    
    content = re.sub(r"\/\/.*", "", content) # Remove single-line comments
    content = re.sub(r"\/\*.*?\*\/", "", content, flags=re.DOTALL) # Remove multi-line comments
    
    data = json.loads(content)  
  return data

def getSettingsData(path: str):
  if not os.path.exists(path):
    raise FileNotFoundError("(!) " + path + " does not exist!")

  return readJSONWithComments(path)

# ======== #
#   MAIN   #

def start():
  os.system('cls' if os.name=='nt' else 'clear')
  print(intro)

def usage(message: str = ""):
  if message != "":
    message += " "

  print("\n" + message + "Usage:")
  print("python serve.py runserver [--watch] [--docs]")
  print("python serve.py build\n")

def main():
  settings = getSettingsData("milkyconfig.jsonc")

  if len(sys.argv) == 1:
    usage("No command provided!")

  elif sys.argv[1] == "build" and len(sys.argv) == 2:
    start()
    migrate(outDir=outDir)

  elif sys.argv[1] == "runserver":
    redirect = settings["pagesRedirect"]
    outDir = settings["outDir"]
    useTS = settings["useTypeScript"]
    minifyJS = settings["minifyJavaScript"]
    minifyCSS = settings["minifyCSS"]
    minifyHTML = settings["minifyHTML"]

    if len(sys.argv) == 2:
      start()
      serve(
        useTS=useTS, 
        minifyJS=minifyJS, 
        minifyCSS=minifyCSS, 
        minifyHTML=minifyHTML,
        pagesRedirect=redirect,
      )
    
    elif len(sys.argv) == 3:
      dir_flags = ["--docs", "-d"]
      watch_flags = ["--watch", "-w"]

      if sys.argv[2] in dir_flags:
        start()
        serve(
          rootDirectory="/docs",
          pagesRedirect=redirect,
          useTS=False,
          minifyJS=False,
          minifyCSS=False, 
          minifyHTML=False,
        )

      elif sys.argv[2] in watch_flags:
        start()
        serve(
          watchComponents=True,
          outDir=outDir,
          useTS=useTS,
          minifyJS=minifyJS,
          minifyCSS=minifyCSS, 
          minifyHTML=minifyHTML,
          pagesRedirect=redirect,
        )
      
      else:
        print(f"Invalid flag provided. Expected one of {str(dir_flags + watch_flags)}, got '{sys.argv[2]}'")

    else:
      usage(f"Invalid number of arguments! Note that flags are mutually exclusive.\nExpected at most 2, recieved {len(sys.argv) - 1}.")
  
  else:
    usage("Invalid command provided!")

if __name__ == "__main__":
  main()