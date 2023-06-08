from http.server import HTTPServer, SimpleHTTPRequestHandler
from css_html_js_minify import process_single_css_file
from .compiler import compile
import sys
import os

# Found this funky little function on stack overflow:
# https://stackoverflow.com/questions/40419276/python-how-to-print-text-to-console-as-hyperlink
def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    # OSC 8 ; params ; URI ST <name> OSC 8 ;; ST 
    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'
    return escape_mask.format(parameters, uri, label)

def prepare(message: str):
  print(message)
  print("Server ready and waiting at", link("http://localhost:8080/"))

# ============== #
# *** SERVER *** #

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
  server_address = ("", 8080)
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()

class NoExtensionHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    print("\n> unmodified path:", self.path)
    self.path = directory + self.path
    print("> with directory:", self.path)
    
    home_paths = ["/", "/docs/"]
    # The exclusion of paths with a period excludes image, js and other file types
    if self.path not in home_paths and not "." in self.path:
      self.path += ".html"
      print("> extension added:", self.path)

    if watch: compile(doOutput=False)
    if watch and cssWatcher.check():
      print("> css modified, minifying stylesheet...")
      process_single_css_file("assets/index.css", overwrite=False, output_path="dist/index.min.css")

    SimpleHTTPRequestHandler.do_GET(self)

class FileWatcher(object):
  def __init__(self, path):
    self._cached_stamp = None
    self.filename = path

  def check(self):
    stamp = os.stat(self.filename).st_mtime

    print(f"> checking {self.filename} modified time:", stamp)
    if stamp != self._cached_stamp:
      self._cached_stamp = stamp
      return True # file changed
    else:
      return False # file unchanged

# =============== #
# *** RUNNING *** #

def serve(rootDirectory = "", watchChanges = False):
  global directory, watch, headerWatcher, cssWatcher
  directory = rootDirectory
  watch = watchChanges

  if watch:
    print("Watching for css and component changes...")
    cssWatcher = FileWatcher("assets/index.css")
  
  if directory == "":
    prepare("Serving from root directory...")
  else: 
    prepare(f"Serving from {directory} directory...")

  run(HTTPServer, NoExtensionHandler)

# ============ #
# *** MAIN *** #

if __name__ == "__main__":
  if len(sys.argv) == 1:
    serve()

  elif len(sys.argv) == 2:
    dir_flags = ["--docs", "-d"]
    head_flags = ["--watch", "-w"]

    if sys.argv[1] in dir_flags:
      print(f"Recieved '{sys.argv[1]}' flag")
      serve(rootDirectory="/docs")

    elif sys.argv[1] in head_flags:
      print(f"Recieved '{sys.argv[1]}' flag")
      serve(watchChanges=True)
    
    else:
      print(f"Invalid flag provided. Expected one of {str(dir_flags + head_flags)}, got '{sys.argv[1]}'")

  else:
    # We can serve from the docs folder or watch for head changes, but it doesn't make sense to do both. 
    print(f"Invalid number of arguments. Flags are mutually exclusive. Expected at most 1, got {len(sys.argv) - 1}")