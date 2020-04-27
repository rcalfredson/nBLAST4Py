import sys
import unittest
from unittest.mock import call, patch, mock_open
import pytest
import numpy as np
import findNeuronMatches

def testMissingQShouldFail(capsys):
  """Ensure script exits with error if no query skeleton is inputted."""
  with patch.object(sys, 'argv', ['']):
    with pytest.raises(SystemExit):
      findNeuronMatches.runSearch()
    captured = capsys.readouterr()
    assert 'error: the following arguments are required: query' in captured.err

@patch("pickle.load", new_callable=mock_open)
@patch("swcHelper.NearestNeighbourSearch")
@patch('findNeuronMatches.globFiles')
@patch("builtins.open", new_callable=mock_open, read_data="0 3 5 7 9")
@patch("nblast.NBLASTHelper.calculateMatchScores")
class ValidCallsToScript(unittest.TestCase):
  def testSavesResultsFileForGivenQ(self, mock_nbh, mock_file, *args):
    """Ensure the results of NBLAST test are written as a JSON file."""
    with patch.object(sys, 'argv', ['', 'mockQ.swc']):
      findNeuronMatches.runSearch()
      assert(mock_file.call_args_list[0] == call('mockQ.swc', 'r'))
      assert(mock_file.call_args_list[1] == call('mockQ.pickSkel', 'wb'))
      assert(mock_file.call_args_list[2] == call('nblast_results_mockQ.json',
        'w', encoding='utf-8'))

  @patch('swcHelper.SWCHelper.reflectX')
  def testCallsReflectXAsNeeded(self, reflectX_mock, *args):
    """Ensure SWCHelper.reflectX() gets called if --reflectX flag is present."""
    with patch.object(sys, 'argv', ['', 'mockQ.swc', '--reflectX', '3']):
      findNeuronMatches.runSearch()
      assert len(reflectX_mock.call_args_list) == 1

  @patch('swcHelper.SWCHelper.rescale')
  def testCallsRescaleAsNeeded(self, rescale_mock, *args):
    """Ensure SWCHelper.rescale() gets called if --rescale flag is present."""
    with patch.object(sys, 'argv', ['', 'mockQ.swc', '--rescale', '3.2']):
      findNeuronMatches.runSearch()
      assert len(rescale_mock.call_args_list) == 1

  @patch('swcHelper.SWCHelper.reflectX')
  @patch('json.dump')
  def testNormalizeScoresAsNeeded(self, json_mock, reflectX_mock, mock_nbh,
    mock_file, mock_glob, *args):
    """Ensure NBLAST scores get normalized (max score = 1) if -n flag is present."""
    with patch.object(sys, 'argv', ['', 'mockQ.swc', '-n']):
      mock_nbh.return_value = [7, 2]
      mock_glob.return_value = ['skel1.swc', 'skel2.swc']
      findNeuronMatches.runSearch()
      print('json mock:', json_mock.call_args_list)
      assert json_mock.call_args_list[0][0][0] == list(zip(mock_glob.return_value,
        mock_nbh.return_value / np.max(mock_nbh.return_value)))
