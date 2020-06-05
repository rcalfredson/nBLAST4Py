import numpy as np
from pynabo import NearestNeighbourSearch
from nblast import NBLASTHelper
from swcHelper import SWCHelper
from unittest.mock import patch

class MockSkel(SWCHelper):
  def __init__(self, numPts=4):
    self.numPts = numPts
    self.path = 'TEST_PATH'
    self.x, self.y, self.z = np.random.random(numPts), np.random.random(numPts), np.random.random(numPts)
    self.tree = NearestNeighbourSearch(self.numpy().astype(np.float64))
    self.parents = np.array(range(-1, numPts - 1))

# @patch('nblast.SWCHelper')
# def testMatchScoresCalc(swc_mock):
#   """Ensure NBLASTHelper returns a score for each target skeleton, at least one
#   of which is nonzero."""
#   numTargets = 4
#   swc_mock.return_value = MockSkel()
#   scores = NBLASTHelper(MockSkel()).calculateMatchScores(['' for _ in range(numTargets)])
#   assert len(scores) == numTargets
#   assert type(np.random.choice(scores)) == np.float64
#   assert np.count_nonzero(np.array(scores) > 0) > 0
