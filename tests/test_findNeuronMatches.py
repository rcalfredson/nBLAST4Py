import os, sys
import unittest
import unittest.mock as mock
from unittest.mock import call, patch, mock_open
import pytest
import numpy as np
import common, findNeuronMatches

QUERY_DIR = 'tests/data/query'
TARGET_DIR = 'tests/data/target'
QUERY_SKEL = 'skel0_mb399b_jrc.swc'
QUERY_PATH = os.path.join(QUERY_DIR, QUERY_SKEL)
TD_ARGS = ['-tD', TARGET_DIR]
NUM_QUERY_SKELS = len(common.globFiles(QUERY_DIR, ext='swc'))
NUM_TARGET_SKELS = len(common.globFiles(TARGET_DIR, ext='swc'))
qL = 'tests/data/mockQueryList.txt'
with open(qL, 'r') as qlFile:
  NUM_LIST_SKELS = len(qlFile.read().splitlines())

def testMissingQShouldFail(capsys):
  """Ensure script exits with error if no query skeleton is inputted."""
  with patch.object(sys, 'argv', ['']):
    with pytest.raises(SystemExit):
      findNeuronMatches.runSearch()
    captured = capsys.readouterr()
    assert 'error: the following arguments are required: query' in captured.err

def testInvalidQShouldFail(capsys):
  """Ensure script exits with error if given query path does not exist."""
  with patch.object(sys, 'argv', ['', 'nonExistentSkel']):
    with pytest.raises(SystemExit):
      findNeuronMatches.runSearch()
    captured = capsys.readouterr()
    assert 'Query must be a file or directory' in captured.out

@patch('multiprocessing.pool.Pool.map')
@patch("builtins.open", new_callable=mock_open, read_data="0 3 5 7 9")
class ValidCallsToRunSearch(unittest.TestCase):
  def testQIsFile(self, mock_file, pool_map):
    """Ensure NBLAST search is run if query path is a single skeleton file."""
    with patch.object(sys, 'argv', ['', QUERY_PATH] + TD_ARGS):
      findNeuronMatches.runSearch()
      map_args = pool_map.call_args_list[0][0]
      assert(map_args[0] == findNeuronMatches.runSingleThreadedSearch)
      assert(map_args[1][0][0] == [QUERY_PATH])

  def testQIsDirMultipleSkels(self, mock_file, pool_map):
    """Ensure NBLAST search is run if query path is a directory containing
    multiple skeleton files."""
    with patch.object(sys, 'argv', ['', QUERY_DIR] + TD_ARGS):
      findNeuronMatches.runSearch()
      map_args = pool_map.call_args_list[0][0]
      assert(len(map_args[1][0][0]) == NUM_QUERY_SKELS)

  def testQIsDirWithQueryList(self, mock_file, pool_map):
    """Ensure NBLAST search is run if query path is a directory containing
    multiple skeleton files, but limited by given list of neurons to test."""
    with patch.object(sys, 'argv', ['', QUERY_DIR] + TD_ARGS +
      ['-qL', 'tests/data/mockQueryList.txt']):
      findNeuronMatches.runSearch()
      map_args = pool_map.call_args_list[0][0]
      assert(len(map_args[1][0][0]) == NUM_LIST_SKELS)

@patch("nblast.NBLASTHelper.calculateMatchScores")
class ValidCallsToRunSingleThreadSearch(unittest.TestCase):
  def testOneScoreListPerQuerySkeleton(self, nbh_mock):
    """Ensure number of calls to calculateMatchScores matches the number of
    query skeletons."""
    with patch.object(sys, 'argv', ['', QUERY_DIR] + TD_ARGS):
      tls, opts = findNeuronMatches.getThreadLists()
    findNeuronMatches.runSingleThreadedSearch([tls[0], opts])
    assert(len(nbh_mock.call_args_list) == NUM_QUERY_SKELS)

  @patch('findNeuronMatches.subprocess.call')
  def testVisualCompOption(self, subprocess_mock, nbh_mock):
    """Ensure the visualization script gets called if that option was set."""
    process_mock = mock.Mock()
    nbh_mock.return_value = np.random.random(NUM_QUERY_SKELS)
    subprocess_mock.return_value = process_mock
    with patch.object(sys, 'argv', ['', TARGET_DIR, '--visualComp'] + TD_ARGS):
      tls, opts = findNeuronMatches.getThreadLists()
    findNeuronMatches.runSingleThreadedSearch([tls[0], opts])
    assert(len(subprocess_mock.call_args_list) ==
      NUM_QUERY_SKELS * NUM_TARGET_SKELS)
