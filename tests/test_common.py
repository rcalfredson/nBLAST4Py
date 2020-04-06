import shutil
import unittest
from pathlib import Path
from common import globFiles

class TestGlob(unittest.TestCase):
  def setUp(self):
    Path('temp').mkdir(exist_ok=True)
    for i in range(3):
      Path('temp/file%i.good'%i).touch()
      Path('temp/file%i.bad'%i).touch()

  def tearDown(self):
    shutil.rmtree('temp')

  def testGlobFindFiles(self):
    """Ensure files are returned that match the requested extension."""
    assert len(globFiles('temp', 'good')) == 3

  def testGlobNoFiles(self):
    """Ensure empty list is returned if no files match requested extension."""
    assert len(globFiles('temp', '?')) == 0
