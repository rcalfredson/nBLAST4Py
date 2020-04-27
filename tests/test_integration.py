import json, os, sys
import numpy as np
from unittest.mock import patch

import findNeuronMatches

results_from_R = [20309.85, 15223.51, 14336.45, 12316.37]
result_filename = 'nblast_results_skel0_mb399b_jrc.json'

def testSavesResultsFileForGivenQ():
    """Ensure the results of NBLAST test match those from the existing implementation in R.

    How to replicate results in R using the nat.NBLAST library:
      library(nat.nblast)
      targetNeurons <- read.neurons("${PATH_TO_TESTS}/data/target",
        pattern="(329566174|5813061260|424789697|1036637638).swc")
      queryNeuron <- read.neuron("${PATH_TO_TESTS}/data/query/skel0_mb399b_jrc.swc")
      scores <- nblast(queryNeuron, targetNeuron)
    """
    with patch.object(sys, 'argv', ['', 'tests/data/query/skel0_mb399b_jrc.swc', '-d', 'tests/data/target']):
      findNeuronMatches.runSearch()
    with open(result_filename, 'r') as f:
      scores = [el[1] for el in json.load(f)]
      assert np.all(np.isclose(results_from_R, scores)) == True
    os.remove(result_filename)

