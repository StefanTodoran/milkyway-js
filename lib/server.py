from http.server import HTTPServer, SimpleHTTPRequestHandler
from css_html_js_minify import process_single_html_file
from css_html_js_minify import process_single_css_file
from css_html_js_minify import process_single_js_file

from lib.utils import logStatus, output, setOutputMode
from .compiler import compile
from .utils import formatLog, locateAll
import subprocess
import threading
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
  output(message)
  output("Server ready and waiting at " + link("http://localhost:8080/") + "\n", logStatus.GOOD)

def handleSubprocessErrors(proc):
  for line in proc.stdout:
    if "error" in str(line):
      output(line, logStatus.WARN)

# ============== #
# *** SERVER *** #

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, bg_proc=None, print_thread=None):
  server_address = ("", 8080)
  httpd = server_class(server_address, handler_class)

  try:
    httpd.serve_forever()
  except:
    if bg_proc:
      output("Recieved keyboard interrupt, killing compiler/bunlder and exiting...", logStatus.WARN)
      bg_proc.kill()
      print_thread.join()
    output("")

class NoExtensionHandler(SimpleHTTPRequestHandler):
  def do_GET(self):
    output("Unmodified path: " + self.path, newLine=True)
    if redirect:
      self.path = directory + self.path.replace(redirect, "/")
    else:
      self.path = directory + self.path
    output("With directory and redirect: " + self.path)
    
    home_paths = ["/", "/docs/"]
    # The exclusion of paths with a period excludes image, js and other file types
    if self.path not in home_paths and not "." in self.path:
      self.path += ".html"
      output("Extension added: " + self.path)

    if self.path.endswith(".html") or self.path in home_paths:
      if watch:
        compile(doOutput=True)

      if doMinifyHTML:
        pages = locateAll("./", "*.html")
        for page in pages:
          process_single_html_file(page, overwrite=True, output_path=page)
    
    if jsWatcher and self.path.endswith(".js") and jsWatcher.check():
      output("JavaScript modified, minifying...", logStatus.EMPHASIS)
      # unminifiedScript = "." + self.path.replace(".min", "")
      # process_single_js_file(unminifiedScript, overwrite=False)
      process_single_js_file(self.path, overwrite=True)
    
    if cssWatcher and self.path.endswith(".css") and cssWatcher.check():
      output("CSS modified, minifying stylesheet...", logStatus.EMPHASIS)
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

      output(f"Checking {file} modified time: {stamp}, {self._cachedStamps[index]}", newLine=True)
      if stamp != self._cachedStamps[index]:
        self._cachedStamps[index] = stamp
        return True # file changed
    
    return False # file unchanged

# =============== #
# *** RUNNING *** #

def verifyDependencyInstallation(name: str):
  try:
    output(f"Verifying {name} installation...")
    installed = subprocess.check_output(["npm", "list"], shell=True)
  except:
    raise EnvironmentError(formatLog("Failed to list installed packages, is npm installed?"), logStatus.FAIL)
  if not name.lower() in str(installed):
    raise EnvironmentError(formatLog(f"{name} is not installed! Running npm list did not reveal {name} installation."), logStatus.FAIL)

def serve(
      watchComponents = False,
      rootDirectory = "", 
      useTS = False,
      doPack = False,
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
  setOutputMode(False)

  if useTS: verifyDependencyInstallation("TypeScript")
  if doPack: verifyDependencyInstallation("Webpack")
  if useTS and doPack: verifyDependencyInstallation("ts-loader")

  if useTS and not doPack:
    try:
      output("\nStarting TypeScript compiler...") 
      proc = subprocess.Popen(["npx", "tsc", "-w"], shell=True, stdout=subprocess.PIPE)
    except:
      raise EnvironmentError(formatLog("Failed to start TypeScript compiler, verify npx and tsc are installed.", logStatus.FAIL))
  
  elif doPack:
    try:
      output("\nStarting Webpack bundler...") 
      proc = subprocess.Popen(["npx", "webpack", "--watch"], shell=True, stdout=subprocess.PIPE)
      # FNULL = open(os.devnull, "w")
      # proc = subprocess.Popen(["npx", "webpack", "--watch"], shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    except:
      raise EnvironmentError(formatLog("Failed to start TypeScript compiler, verify npx and webpack cli are installed.", logStatus.FAIL))

  jsWatcher = None
  if minifyJS:
    output("Watching for changes and minifying transpiled JavaScript...")
    scripts = locateAll("./dist/", "*.js")
    paths = [str(path) for path in scripts]
    jsWatcher = FileWatcher(paths)
  
  cssWatcher = None
  if minifyCSS:
    output("Watching for and minifying CSS changes...")
    cssWatcher = FileWatcher(["src/index.css"])
  
  doMinifyHTML = minifyHTML
  if minifyHTML:
    output("Watching for and minifying HTML changes...")
  
  if directory == "":
    prepare("Serving from root directory...")
  else: 
    prepare(f"Serving from {directory} directory...")

  if useTS:
    printThread = threading.Thread(target=handleSubprocessErrors, args=(proc,))
    printThread.start()
    run(HTTPServer, NoExtensionHandler, proc, printThread)
  else:
    run(HTTPServer, NoExtensionHandler)