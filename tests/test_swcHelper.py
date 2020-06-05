import unittest
import numpy as np
from swcHelper import SWCHelper
from unittest.mock import patch, mock_open

with open('tests/data/target/5813061260Truncated.swc', 'r') as skelFile:
  skelData = skelFile.read()

class TestSWCHelper:
  @patch('swcHelper.NearestNeighbourSearch')
  @patch("builtins.open", new_callable=mock_open, read_data="0 3 5 7 9")
  @patch('pickle.load')
  @patch('os.path.exists')
  def testLoadFromPickle(self, path_mock, pickle_mock, *args):
    """Ensure SWCHelper instance is initialized via pickle file, if present."""
    path_mock.return_value = True
    SWCHelper('')
    assert len(pickle_mock.call_args_list) == 1

  @patch('swcHelper.NearestNeighbourSearch')
  @patch('swcHelper.SWCHelper.calcDirVectors')
  @patch('swcHelper.SWCHelper.constructSegments')
  @patch('swcHelper.SWCHelper.resample')
  @patch("builtins.open", new_callable=mock_open,
    read_data=skelData)
  @patch('swcHelper.SWCHelper.appendSWCLine')
  def testSkipSkeletonComments(self, append_swc_mock, *args):
    """Ensure that lines beginning with # are skipped when parsing SWC file."""
    SWCHelper('')
    assert len(append_swc_mock.call_args_list) == 443

  @patch('swcHelper.NearestNeighbourSearch')
  @patch('swcHelper.SWCHelper.calcDirVectors')
  @patch('swcHelper.SWCHelper.constructSegments')
  @patch('swcHelper.SWCHelper.resample')
  @patch("builtins.open", new_callable=mock_open,
    read_data=skelData)
  @patch('swcHelper.SWCHelper.appendSWCLine')
  def testParentsCleanup(self, *args):
    """Ensure parent indices with any value <1 get replaced by the first
    offspring of that point, if it exists."""
    mySWCHelper = SWCHelper('')
    mySWCHelper.parents =  np.asarray([-1, 1, -1, 3, 4, -1])
    mySWCHelper.ids = range(1, len(mySWCHelper.parents) + 1)
    mySWCHelper.cleanUpParents()
    assert np.array_equal(mySWCHelper.parents, [2, 1, 4, 3, 4, -1])

  @patch("builtins.open", new_callable=mock_open,
    read_data=skelData)
  def testVectorCalcs(self, *args):
    """Ensure segment lists, resampled nodes, and direction vectors are
    calculated when initializing instance via SWC file."""
    swcHelper = SWCHelper('')
    numPtsResampled = 130
    assert len(swcHelper.segmentList) == 32
    assert len(swcHelper.x) == numPtsResampled
    assert swcHelper.dirVectors.shape[0] == numPtsResampled

  @patch("builtins.open", new_callable=mock_open,
    read_data=skelData)
  def testReflectX(self, *args):
    """Ensure X coordinates get reflected across the given centerline if
    reflectX is given."""
    swcHelperOrig = SWCHelper('')
    swcHelperReflected = SWCHelper('', reflectX=314)
    assert np.all(np.isclose(swcHelperOrig.x, np.subtract(2*314, swcHelperReflected.x)))
