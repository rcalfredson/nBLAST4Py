"""Shared methods"""

import glob

def globFiles(dirName, ext='png'):
  """Return files matching the given extension in the given directory."""
  return glob.glob(dirName +'/*.%s'%ext)
