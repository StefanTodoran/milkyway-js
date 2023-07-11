import unittest
from lib.compiler import doComponentSubstitutions

class TestCompiler(unittest.TestCase):
  def testBasicComponentSubstitution(self):
    mhtml = '<!-- %MLKY COMMAND-SNIPPET text="manage.py runserver --watch" -->'
    expected = '<span class="command-snippet" tabindex="0">manage.py runserver --watch</span>'

    self.assertEqual(doComponentSubstitutions(mhtml.splitlines(), False), [expected])

if __name__ == "__main__":
  unittest.main()