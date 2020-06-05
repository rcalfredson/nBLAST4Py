import unittest
import numpy as np
from swcHelper import SWCHelper
from unittest.mock import patch, mock_open

@patch('swcHelper.NearestNeighbourSearch')
class TestSWCHelper:
  @patch("builtins.open", new_callable=mock_open, read_data="0 3 5 7 9")
  @patch('pickle.load')
  @patch('os.path.exists')
  def testLoadFromPickle(self, path_mock, pickle_mock, *args):
    """Ensure SWCHelper instance is initialized via pickle file, if present."""
    path_mock.return_value = True
    SWCHelper('')
    assert len(pickle_mock.call_args_list) == 1

  # @patch("builtins.open", new_callable=mock_open,
  #   read_data="#drosophila\n0 3 5 7 9\n1 5 7 9 11")
  # @patch('swcHelper.SWCHelper.appendSWCLine')
  # def testSkipSkeletonComments(self, append_swc_mock, *args):
  #   """Ensure that lines beginning with # are skipped when parsing SWC file."""
  #   SWCHelper('')
  #   assert len(append_swc_mock.call_args_list) == 2

  # @patch('builtins.open')
  # def testReflectX(self, *args):
  #   """Ensure X coordinates flip their sign after calling reflectX()."""
  #   mySWCHelper = SWCHelper('')
  #   origX = np.random.random(5)
  #   mySWCHelper.x = origX
  #   mySWCHelper.reflectX()
  #   assert np.array_equal(mySWCHelper.x, -1 * origX) == True

  # @patch('builtins.open')
  # def testRescale(self, *args):
  #   """Ensure coordinates get rescaled after calling rescale()."""
  #   mySWCHelper = SWCHelper('')
  #   origX, scalingFactor = np.random.random(5), np.random.random()
  #   mySWCHelper.x = origX
  #   mySWCHelper.rescale(scalingFactor)
  #   assert np.array_equal(mySWCHelper.x, scalingFactor * origX) == True

  # @patch('builtins.open')
  # def testParentsCleanup(self, *args):
  #   """Ensure parent indices with any value <1 get replaced by the first
  #   offspring of that point, if it exists."""
  #   mySWCHelper = SWCHelper('')
  #   mySWCHelper.parents =  np.asarray([-1, 1, -1, 3, 4, -1])
  #   mySWCHelper.ids = range(1, len(mySWCHelper.parents) + 1)
  #   mySWCHelper.cleanUpParents()
  #   assert np.array_equal(mySWCHelper.parents, [2, 1, 4, 3, 4, -1])
