"""NBLASTHelper class"""
import timeit
import numpy as np
import matplotlib.pyplot as plt
from pynabo import SearchOptionFlags
import feather

from swcHelper import SWCHelper

class NBLASTHelper():
  """Calculate neuron morphology scores using NBLAST."""

  def __init__(self, query, dirVectorFromParent=False):
    """Create a k-d tree for the given query neuron."""
    self.query = query
    self.dirVectorFromParent = dirVectorFromParent
    self.qNumpy = np.asfortranarray(query.numpy().astype(np.float64))
    self.scoreMatrix = feather.read_dataframe('data/fcwb.feather')

  def calculateMatchScores(self, targets):
    """Return an array of similarity scores with the query neuron for each
    target neuron using the NBLAST algorithm outlined in Costa et al 2014
    (doi: 10.1016/j.neuron.2016.06.012)
    """
    scores = []
    for i, target in enumerate(targets):
      start_time = timeit.default_timer()
      target = SWCHelper(target)
      nns = target.tree.knn(self.qNumpy.T, 1, 0,
        SearchOptionFlags.ALLOW_SELF_MATCH)
      nnIdxs = np.hstack((nns[0], np.array(range(self.query.numPts))
        .reshape(-1, 1)))
      dists = np.sqrt(np.squeeze(nns[1]))
      if self.dirVectorFromParent:
        dirVectors = self.findDirectionVectorsFromParents(target, nnIdxs)
      else:
        dirVectors = np.hstack((target.dirVectors[nnIdxs[:, 0]],
          self.query.dirVectors[nnIdxs[:, 1]]))
      dotProds = np.abs(np.einsum('ij,ij->i', dirVectors[:, 0:3],
        dirVectors[:, 3:6]))
      scores.append(self.calculateNearestNeighborScore(dists, dotProds))
      if i % 1000 == 0:
        print(i, 'of', len(targets))
        print('score for %s: %.4f  |  processing time: %.4f'%(target.path,
          scores[-1], timeit.default_timer() - start_time))
        print('num scores greater than zero:',
          len([score for score in scores if score > 0]))
    return scores

  def calculateNearestNeighborScore(self, dists, dotProds):
    """Return a neuron morphology score based on NBLAST 2D histogram binning."""
    assert len(dists) == len(dotProds)
    catsByType = [list(self.scoreMatrix[rangeName].cat.categories) for\
      rangeName in ('Var1', 'Var2')]
    scoreTable = np.array(self.scoreMatrix['Freq']).reshape((
      len(catsByType[1]), len(catsByType[0]))).T
    dotProdRanges, distanceRanges = [], []
    for tI, rangeType in enumerate((distanceRanges, dotProdRanges)):
      for rI, catRange in enumerate(catsByType[tI]):
        catRange = [float(endPt) for endPt in catRange[1:-1].split(',')]
        rangeType.append(catRange[0])
        if rI == len(catsByType[tI]) - 1:
          rangeType.append(catRange[1])
    distanceRanges = np.array(distanceRanges)
    dotProdRanges = np.array(dotProdRanges)
    distBins = np.histogram2d(dists, np.array(dotProds),
      bins=np.array([distanceRanges, dotProdRanges]))[0]
    return np.sum(np.multiply(distBins, scoreTable))

  def findDirectionVectorsFromParents(self, target, nnIdxs):
    """Return an array of the component-wise distances between the parent point
    and the point of interest for both the query neuron and target neurons.
    """
    parentsIdxs = np.hstack((np.array(target.parents[nnIdxs[:, 0]]).reshape(
      -1, 1), np.array(self.query.parents[nnIdxs[:, 1]]).reshape(-1, 1))) - 1
    parentToPtDists = np.zeros((self.query.numPts, 6))
    for nI, neuron in enumerate((target, self.query)):
      offset = 3*nI
      preNorm = np.array([getattr(neuron, dim)[nnIdxs[:, nI]] - getattr(neuron,
        dim)[parentsIdxs[:, nI]] for dim in ('x', 'y', 'z')]).T
      parentToPtDists[:, 0 + offset:3 + offset] = preNorm / np.linalg.norm(
        preNorm, axis=1)[:, None]
    return parentToPtDists
