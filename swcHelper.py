"""SWCHelper class"""
import timeit
import os, pickle
import numpy as np

from pynabo import NearestNeighbourSearch

class SWCHelper:
  """Read SWC files."""

  def __init__(self, path):
    """Read an SWC file from the given path."""
    self.path = path
    self.x, self.y, self.z, self.parents, self.ids = [], [], [], [], []
    pklPath = '%s.pickSkel'%path.split('.swc')[0]
    hasPickle = os.path.exists(pklPath)
    with open(pklPath if hasPickle else path, 'rb' if hasPickle else 'r') as f:
      if hasPickle:
        tempData = pickle.load(f)
        self.__dict__.update(tempData)
      else:
        swcContent = f.readlines()
        for line in swcContent:
          if line.startswith('#'):
            continue
          self.appendSWCLine(line)        
        for attr in ('parents', 'x', 'y', 'z'):
          setattr(self, attr, np.array(getattr(self, attr)))
        self.cleanUpParents()
        self.numPts = len(self.x)
        if not hasPickle:
          with open(pklPath, 'wb') as pickleFile:
            pickle.dump({dKey: self.__dict__[dKey] for dKey in self.__dict__ if\
              dKey is not 'tree'}, pickleFile, 2)
      self.tree = NearestNeighbourSearch(self.numpy().astype(np.float64))

  def appendSWCLine(self, line):
    """Add a new row of skeleton data to the instance: X, Y, Z, node index, and
    parent index."""
    data = line.split(' ')
    for dataIdx, attrName in ((0, 'ids'), (2, 'x'), (3, 'y'), (4, 'z'),
        (-1, 'parents')):
      dataPiece = data[dataIdx].strip()
      if dataIdx >= 2:
        dataPiece = np.float32(dataPiece)
      else:
        dataPiece = int(dataPiece)
      getattr(self, attrName).append(dataPiece)

  def rescale(self, scalingFactor):
    """Multiply the coords of each node by the given factor."""
    for attr in ('x', 'y', 'z'):
      setattr(self, attr, np.multiply(getattr(self, attr), scalingFactor))

  def reflectX(self, midpoint=None):
    """Flip the sign of X coordinates (reflect across Y axis)."""
    self.x = np.multiply(self.x, -1) if midpoint is None else np.subtract(2*midpoint, self.x)

  def numpy(self):
    """Return the skeleton as an N-by-3 matrix (XYZ tuple for each node)"""
    return np.asfortranarray([self.x, self.y, self.z])

  def cleanUpParents(self):
    """Returns a list of parent indices with any value <1 replaced by the first
    offspring of that point.
    """
    negPoints = np.where(self.parents < 1)[0]
    for point in negPoints:
      ptId = self.ids[point]
      offspring = np.where(self.parents == ptId)[0]
      if len(offspring) == 0:
        continue
      self.parents[point] = self.ids[offspring[0]]
