"""SWCHelper class"""
import timeit
import os, pickle
import numpy as np

from pynabo import NearestNeighbourSearch

class SWCHelper:
  """Read SWC files."""

  def __init__(self, path, origin=(0, 0, 0), doPickle=True):
    """Read a SWC file from the given path."""
    self.path, self.origin = path, origin
    self.x, self.y, self.z, self.parents, self.ids = [], [], [], [], []
    picklePath = '%s.pickSkel'%path.split('.swc')[0]
    hasPickle = os.path.exists(picklePath)
    with open(picklePath if hasPickle else path, 'rb' if hasPickle else 'r') as f:
      if hasPickle:
        tempData = pickle.load(f)
        self.__dict__.update(tempData)
      else:
        swc_content = f.readlines()
        for line in swc_content:
          if line.startswith('#'):
            continue
          self.appendSWCLine(line)        
        for attr in ('parents', 'x', 'y', 'z'):
          setattr(self, attr, np.array(getattr(self, attr)))
        self.cleanUpParents()
        self.numPts = len(self.x)
        if not hasPickle:
          with open(picklePath, 'wb') as pickleFile:
            pickle.dump({dKey: self.__dict__[dKey] for dKey in self.__dict__ if dKey is not 'tree'}, pickleFile, 2)
      #start_t = timeit.default_timer()
      #print('passed to NNS', self.numpy().astype(np.float64))
      #print(self.numpy().astype(np.float64).shape)
      self.tree = NearestNeighbourSearch(np.asfortranarray(self.numpy().astype(np.float64)))
      #self.tree = NearestNeighbourSearch(np.array([[0.,3., 5], [1,22, 4], [4,5, 1], [4, 6, 1]]))
      #print('time to calculate tree:', timeit.default_timer() - start_t)

  def appendSWCLine(self, line):
    """Add a new row of skeleton data to the instance: X, Y, Z, node index, and
    parent index."""
    data = line.split(' ')
    for dataIdx, attrName in ((0, 'ids'), (2, 'x'), (3, 'y'), (4, 'z'), (-1, 'parents')):
      dataPiece = data[dataIdx].strip()
      if dataIdx >= 2:
        dataPiece = np.float32(dataPiece) + self.origin[dataIdx - 2]
      else:
        dataPiece = int(dataPiece)
      getattr(self, attrName).append(dataPiece)

  def rescale(self, scalingFactor):
    for attr in ('x', 'y', 'z'):
      setattr(self, attr, np.multiply(getattr(self, attr), scalingFactor))
  
  def translateOrigin(self, origin):
    for i, attr in enumerate(('x', 'y', 'z')):
      setattr(self, attr, np.add(getattr(self, attr), origin[i]))

  def reflect(self):
    self.x = -self.x

  def numpy(self):
    """Return the skeleton as an N-by-3 matrix (X Y Z tuple for each node)"""
    return np.array([self.x, self.y, self.z])

  def cleanUpParents(self):
    """Returns a list of parent indices with any value <1 replaced by the
    first offspring of that point."""
    negPoints = np.where(self.parents < 1)[0]
    for point in negPoints:
      ptId = self.ids[point]
      offspring = np.where(self.parents == ptId)[0]
      if len(offspring) == 0:
        continue
      self.parents[point] = self.ids[offspring[0]]
