import numpy as np
from pynabo import NearestNeighbourSearch
from nblast import NBLASTHelper
from swcHelper import SWCHelper
from unittest.mock import patch

class MockSkel(SWCHelper):
  def __init__(self, numPts=5):
    self.numPts = numPts
    self.ids = list(range(1, numPts+1))
    self.path = 'TEST_PATH'
    self.x, self.y, self.z = np.random.random(numPts), np.random.random(numPts), np.random.random(numPts)
    self.tree = NearestNeighbourSearch(self.numpy().astype(np.float64))
    if self.numPts >= 5:
      self.calcDirVectors()
    self.parents = np.array([-1] + list(range(1, numPts)))

@patch('nblast.SWCHelper')
def testMatchScoresCalc(swc_mock):
  """Ensure NBLASTHelper returns a score for each target skeleton, at least one
  of which is nonzero."""
  numTargets = 4
  swc_mock.return_value = MockSkel()
  scores = NBLASTHelper(MockSkel()).calculateMatchScores(['' for _ in range(numTargets)])
  assert len(scores) == numTargets
  assert type(np.random.choice(scores)) == np.float64
  assert np.count_nonzero(np.array(scores) > 0) > 0

@patch('nblast.NBLASTHelper.calculateNearestNeighborScore', return_value=0.5)
@patch('numpy.einsum')
@patch('nblast.SWCHelper')
@patch('nblast.NBLASTHelper.findDirectionVectorsFromParents')
def testFlagForDirVecsUsingParents(dirvec_mock, swc_mock, *args):
  """Ensure the function to calculate direction vectors from parents is called
  when the apppropriate flag is set."""
  numTargets = 4
  swc_mock.return_value = MockSkel()
  nbh = NBLASTHelper(MockSkel())
  nbh.dirVectorFromParent = True
  scores = nbh.calculateMatchScores(['' for _ in range(numTargets)])
  assert len(dirvec_mock.call_args_list) > 0

@patch('nblast.SWCHelper')
def testMatchScoresCalcFwdRev(swc_mock):
  """Ensure when forward-reverse averaging is used that NBLAST search gets run
  in reverse once for each target, and that scores are normalized."""
  numTargets = 4
  swc_mock.side_effect = [MockSkel() for _ in range(numTargets)]
  nbh = NBLASTHelper(MockSkel())
  nbh.fwdRevAvg = True
  with patch.object(nbh, 'runNBLASTForPair',wraps=nbh.runNBLASTForPair) as spy:
    scores = nbh.calculateMatchScores(['' for _ in range(numTargets)])
    assert len([arg for arg in spy.call_args_list if len(arg[1]) > 0 and \
      'reverse' in arg[1] and arg[1]['reverse'] is True]) > 0
    assert np.count_nonzero((np.array(scores) >= 0) & (np.array(scores) <= 1)
      ) == numTargets

def testCalculateDirectionVectorsFromParents():
  """Ensure accuracy of calculation of direction vectors from parent to each
  point of interest."""
  query = MockSkel(numPts=2)
  target = MockSkel(numPts=2)
  query.cleanUpParents()
  target.cleanUpParents()
  query.x, query.y = np.array([1, 0]), np.array([0, 1])
  query.z =  np.array([1, 1])
  target.x, target.y = np.array([0, 0]), np.array([0, 0.5]),
  target.z = np.array([0, 1])
  nbh = NBLASTHelper(query)
  # first row: from first point to second point
  # second row: from second point to first point
  results = nbh.findDirectionVectorsFromParents(target, query,
    np.array([[1, 1], [0, 0]]))
  for i, vec in enumerate((target, query)):
    dirVec = [np.diff(getattr(vec, dim)) for dim in ('x', 'y', 'z')]
    dirVec = (dirVec / np.linalg.norm(dirVec)).T[0]
    colRange = slice(i*3, i*3 +3)
    assert(np.array_equal(results[0, colRange], dirVec))
    assert(np.array_equal(results[1, colRange], -dirVec))
