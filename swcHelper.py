"""SWCHelper class"""
import timeit
import itertools, os, pickle
import numpy as np
import igraph
import scipy.interpolate

from pynabo import NearestNeighbourSearch, SearchOptionFlags

class SWCHelper:
  """Read SWC files."""

  def __init__(self, path, dirVectorFromParent=False, reflectX=None):
    """Read an SWC file from the given path."""
    self.path = path
    self.x, self.y, self.z, self.parents, self.ids = [], [], [], [], []
    pklPath = '%s.pickSkel'%path.split('.swc')[0]
    usePickle = os.path.exists(pklPath) and not dirVectorFromParent
    with open(pklPath if usePickle else path, 'rb' if usePickle else 'r') as f:
      if usePickle:
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
        self.numPts = len(self.x)
        if reflectX is not None:
          self.reflectX(reflectX)
        if not dirVectorFromParent:
          self.constructSegments()
          self.resample(1)
          self.calcDirVectors()
        self.cleanUpParents()
        if not os.path.exists(pklPath) and not dirVectorFromParent:
          with open(pklPath, 'wb') as pickleFile:
            pickle.dump({dKey: self.__dict__[dKey] for dKey in self.__dict__ if\
              dKey is not 'tree'}, pickleFile, 2)
      self.tree = NearestNeighbourSearch(self.numpy().astype(np.float64))

  @staticmethod
  def iterative_dfs(graph, start, path=[], parents=[]):
    '''Return node indices and their parents in an order determined by
    depth-first search.'''
    q=[start]
    qp=[None]
    while q:
      v=q.pop(0)
      vp=qp.pop(0)
      if v not in path:
        path=path+[v]
        parents=parents+[vp]
        q=[edge.target for edge in graph.vs[v].out_edges()] + q
        qp=[edge.source for edge in graph.vs[v].out_edges()] + qp
    return zip(path, parents)

  def calcDirVectors(self):
    pointCrds = np.asfortranarray(self.numpy().astype(np.float64))
    tree = NearestNeighbourSearch(pointCrds)
    nns = tree.knn(pointCrds.T, 5, 0, SearchOptionFlags.ALLOW_SELF_MATCH)
    self.dirVectors = np.empty((self.numPts, 3))
    for i in range(self.numPts):
      closestPts = self.numpy()[:, nns[0][i]]
      diffFromMean = closestPts - np.mean(closestPts, axis=1, keepdims=True)
      inertia = np.matmul(diffFromMean, diffFromMean.T)
      v1d1 = np.linalg.svd(inertia)
      self.dirVectors[i, :] = v1d1[0][:, 0]

  def constructSegments(self):
    """Decompose skeleton into segments (i.e., branches with shared parents)"""
    skelGraph = igraph.Graph(edges=np.asarray([[self.parents[i], i+1] for i in \
      range(0, self.numPts) if self.parents[i] != -1]), vertex_attrs={'name':
      list(range(-1, self.numPts))}, directed=True)
    decomp = skelGraph.decompose(mode=igraph.WEAK, minelements=2)
    decomp = sorted(decomp, key=igraph.Graph.ecount, reverse=True)
    sl = []
    for decompL in decomp:
      origin = np.argmax(decompL.indegree()==0)
      dfs_results = list(self.iterative_dfs(decompL, origin))
      ncount = decompL.degree()
      current_seg = [decompL.vs[dfs_results[0][0]]['name']]
      for i in range(1, len(dfs_results)):
        current_point = dfs_results[i][0]
        if len(current_seg) == 0:
          current_seg = [decompL.vs[dfs_results[current_point][1]]['name']]
        current_seg.append(decompL.vs[current_point]['name'])
        if ncount[current_point] != 2:
          sl.append(current_seg)
          current_seg = []
    self.segmentList = sl

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

  def reflectX(self, midpoint=None):
    """Flip the sign of X coordinates (reflect across Y axis)."""
    self.x = np.multiply(self.x, -1) if midpoint is None else np.subtract(
      2*midpoint, self.x)

  def resample(self, stepsize):
    """Resample the skeleton with a new spacing.
  
    To replace x, y, and z attributes, use replace=True; otherwise, the
    function just returns the resampled points."""
    xyz = self.numpy()
    rsX, rsY, rsZ = [], [], []
    segListNew = []

    for sI, seg in enumerate(self.segmentList):
      resampled_pts = self.resample_segment(xyz[:, seg], 1)
      if resampled_pts is None:
        segListNew.append(list(seg))
      else:
        newIdxs = np.arange(self.numPts, self.numPts + resampled_pts.shape[1])
        segListNew.append(list(np.hstack(([seg[0]], newIdxs,
          [seg[-1]])).astype(int)))
        self.x = np.hstack((self.x, resampled_pts[0]))
        self.y = np.hstack((self.y, resampled_pts[1]))
        self.z = np.hstack((self.z, resampled_pts[2]))
        self.numPts = len(self.x)
    segListFlatPreUniq = np.array([item for sublist in segListNew for item\
       in sublist])
    _, idx = np.unique(segListFlatPreUniq, return_index=True)
    segListFlat = segListFlatPreUniq[np.sort(idx)]
    self.x = self.x[segListFlat]
    self.y = self.y[segListFlat]
    self.z = self.z[segListFlat]
    self.numPts = len(self.x)

  @staticmethod
  def resample_segment(segment, stepsize):
    """Return the given seg if its length exceeds stepsize;
    otherwise, return None."""
    diffs = np.sqrt(np.sum(np.diff(segment, axis=1)**2, axis=0))
    pathLength = np.sum(diffs)
    if pathLength < stepsize:
      return None
    internalPoints = np.arange(stepsize, pathLength, stepsize)
    nInternalPoints = len(internalPoints)
    cumLength = np.hstack(([0], np.cumsum(diffs)))
    resampled = np.zeros((segment.shape[0], nInternalPoints))
    for dim in range(segment.shape[0]):
      interpFunc = scipy.interpolate.interp1d(cumLength, segment[dim, :])
      resampled[dim, :] = interpFunc(internalPoints)
    return resampled

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
