import sys
import os
from lib.server import serve

intro = r"""
        _ _ _                               __  __    
  /\/\ (_) | | ___   ___      ____ _ _   _  \ \/ _\   
 /    \| | | |/ / | | \ \ /\ / / _` | | | |  \ \ \    
/ /\/\ \ | |   <| |_| |\ V  V / (_| | |_| /\_/ /\ \   
\/    \/_|_|_|\_\\__, | \_/\_/ \__,_|\__, \___/\__/   
                 |___/               |___/            
            - Workflow Management Script -            
"""

def usage(message: str = ""):
  if message != "":
    message += " "

  print("\n" + message + "Usage:")
  print("python serve.py runserver [--watch] [--docs]")
  print("python serve.py build\n")

def main():
  if len(sys.argv) == 1:
    usage("No command provided!")

  elif sys.argv[1] == "build" and len(sys.argv) == 2:
    pass

  elif sys.argv[1] == "runserver":
    if len(sys.argv) == 2:
      serve()
    
    elif len(sys.argv) == 3:
      dir_flags = ["--docs", "-d"]
      watch_flags = ["--watch", "-w"]

      if sys.argv[2] in dir_flags:
        os.system('cls' if os.name=='nt' else 'clear')
        print(intro)
        serve(rootDirectory="/docs")

      elif sys.argv[2] in watch_flags:
        os.system('cls' if os.name=='nt' else 'clear')
        print(intro)
        serve(watchChanges=True)
      
      else:
        print(f"Invalid flag provided. Expected one of {str(dir_flags + watch_flags)}, got '{sys.argv[2]}'")

    else:
      usage(f"Invalid number of arguments! Note that flags are mutually exclusive.\nExpected at most 2, recieved {len(sys.argv) - 1}.")
  
  else:
    usage("Invalid command provided!")

if __name__ == "__main__":
  main()