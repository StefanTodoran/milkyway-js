from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import os

intro = r"""
 _____         _ _ _        _____                 
|  |  |___ ___|_| | |___   | __  |___ ___ ___ ___ 
|  |  | .'|   | | | | .'|  | __ -| . |   | -_|_ -|
 \___/|__,|_|_|_|_|_|__,|  |_____|___|_|_|___|___|
          - Workflow Management Script -          
"""

# ============ #
# *** MAIN *** #

def main():
  if len(sys.argv) == 1:
    print("No command provided. Usage:")
    print("python serve.py runserver [--watch] [--docs]")
    print("python serve.py build")

  elif sys.argv[1] == "build":
    pass

  elif sys.argv[1] == "runserver":
    dir_flags = ["--docs", "--production"]
    head_flags = ["--watch"]

    if sys.argv[1] in dir_flags:
      directory = "/docs"
      prepare(f"Recieved '{sys.argv[1]}' flag, serving from /docs/ directory...")
      run(HTTPServer, NoExtensionHandler)

    elif sys.argv[1] in head_flags:
      watch = True
      watcher = FileWatcher("header.html")
      print("Serving from root directory...")
      prepare(f"Recieved '{sys.argv[1]}' flag, watching header.html for changes...")
      run(HTTPServer, NoExtensionHandler)
    
    else:
      print(f"Invalid flag provided. Expected one of {str(dir_flags + head_flags)}, got '{sys.argv[1]}'")

  else:
    # We can serve from the docs folder or watch for head changes, but it doesn't make sense to do both. 
    print(f"Invalid number of arguments. Flags are mutually exclusive. Expected at most 1, got {len(sys.argv) - 1}")

if __name__ == "__main__":
  os.system('cls' if os.name=='nt' else 'clear')
  print(intro)
  main()