from http.server import HTTPServer, SimpleHTTPRequestHandler
from css_html_js_minify import process_single_html_file
from css_html_js_minify import process_single_css_file
from css_html_js_minify import process_single_js_file
from .compiler import compile
from .build import locateAll
import subprocess
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

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, bg_proc=None):
  server_address = ("", 8080)
  httpd = server_class(server_address, handler_class)

  try:
    httpd.serve_forever()
  except:
    if bg_proc:
      print("Recieved keyboard interrupt, killing TypeScript compiler and exiting...")
      bg_proc.kill()
    print("")

class NoExtensionHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    print("\n> Unmodified path:", self.path)
    if redirect:
      self.path = directory + self.path.replace(redirect, "/")
    else:
      self.path = directory + self.path
    print("> With directory and redirect:", self.path)
    
    home_paths = ["/", "/docs/"]
    # The exclusion of paths with a period excludes image, js and other file types
    if self.path not in home_paths and not "." in self.path:
      self.path += ".html"
      print("> Extension added:", self.path)

    if self.path.endswith(".html") or self.path in home_paths:
      if watch:
        compile(doOutput=True)

      if doMinifyHTML:
        pages = locateAll("./", "*.html")
        for page in pages:
          process_single_html_file(page, overwrite=True, output_path=page)
    
    if jsWatcher and self.path.endswith(".js") and jsWatcher.check():
      print("> JavaScript modified, minifying...")
      unminifiedScript = "." + self.path.replace(".min", "")
      process_single_js_file(unminifiedScript, overwrite=False)
    
    if cssWatcher and self.path.endswith(".css") and cssWatcher.check():
      print("> CSS modified, minifying stylesheet...")
      process_single_css_file("src/index.css", overwrite=False, output_path=outputLoc + "/" + "index.min.css")

    SimpleHTTPRequestHandler.do_GET(self)

class FileWatcher(object):
  def __init__(self, paths: list[str]):
    self._cachedStamps = [None] * len(paths)
    self.watchPaths = paths

  def check(self):
    for index in range(len(self.watchPaths)):
      file = self.watchPaths[index]
      stamp = os.stat(file).st_mtime

      print(f"> Checking {file} modified time:", stamp, self._cachedStamps[index])
      if stamp != self._cachedStamps[index]:
        self._cachedStamps[index] = stamp
        return True # file changed
    
    return False # file unchanged

# =============== #
# *** RUNNING *** #

def serve(
      watchComponents = False,
      rootDirectory = "", 
      useTS = False, 
      minifyJS = False, 
      minifyCSS = False, 
      minifyHTML = False, 
      pagesRedirect = "",
      outDir = "./dist/",
    ):
  global directory, redirect, watch, outputLoc, jsWatcher, cssWatcher, doMinifyHTML
  directory = rootDirectory
  redirect = pagesRedirect
  watch = watchComponents
  outputLoc = outDir
  compile(doOutput=False)

  if useTS:
    try:
      print("Verifying TypeScript installation...")
      installed = subprocess.check_output(["npm", "list"], shell=True)
    except:
      raise EnvironmentError("(!) Failed to verify installed packages, is npm installed?")
    if not "typescript" in str(installed):
      raise EnvironmentError("(!) TypeScript is not installed! Running npm list did not reveal TypeScript installation.")

    try:
      # start the ts compiler in the bg with no ouput
      FNULL = open(os.devnull, "w")
      print("\nStarting TypeScript compiler...") 
      tsc = subprocess.Popen(["npx", "tsc", "-w"], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    except:
      raise EnvironmentError("(!) Failed to start TypeScript compiler, verify npx and tsc are installed.")

  jsWatcher = None
  if minifyJS:
    print("Watching for changes and minifying transpiled JavaScript...")
    scripts = locateAll("./dist/", "*.js")
    paths = [str(path) for path in scripts]
    jsWatcher = FileWatcher(paths)
  
  cssWatcher = None
  if minifyCSS:
    print("Watching for and minifying CSS changes...")
    cssWatcher = FileWatcher(["src/index.css"])
  
  doMinifyHTML = minifyHTML
  if minifyHTML:
    print("Watching for and minifying HTML changes...")
  
  if directory == "":
    prepare("Serving from root directory...")
  else: 
    prepare(f"Serving from {directory} directory...")

  if useTS:
    run(HTTPServer, NoExtensionHandler, tsc)
  else:
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