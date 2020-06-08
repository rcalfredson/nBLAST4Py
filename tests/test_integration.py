import json, os, sys
import numpy as np
from unittest.mock import patch

import findNeuronMatches

result_filename = 'nblast_results_skel0_mb399b_jrc%s.json'

def testParentBasedTangent():
    """Ensure the results of NBLAST test match those from the existing
    implementation in R. Conditions: parent-based tangent vector calculation.

    How to replicate results in R using the nat.NBLAST library:
      library(nat.nblast)
      targetNeurons <- read.neurons("${PATH_TO_TESTS}/data/target",
        pattern="(1324365879|5813061260|424789697|1036637638).swc")
      queryNeuron <- read.neuron(
        "${PATH_TO_TESTS}/data/query/skel0_mb399b_jrc.swc")
      scores <- nblast(queryNeuron, targetNeurons)
    """
    results = result_filename%''
    results_from_R = [15223.51, 14336.45, 12316.37, -33786.63]
    with patch.object(sys, 'argv', ['', 'tests/data/query/skel0_mb399b_jrc.swc',
        '-tD', 'tests/data/target', '--dirVec', 'parent']):
      findNeuronMatches.runSearch()
    with open(results, 'r') as f:
      scores = [el[1] for el in json.load(f)]
      assert np.all(np.isclose(results_from_R, scores, rtol=1e-3, atol=1e-3)) == True
    os.remove(results)

def testParentBasedTangentFwdRev():
    """Ensure the results of NBLAST test match those from the existing
    implementation in R. Conditions: parent-based tangent vector calculations,
    forward-reverse averaging.

    How to replicate results in R using the nat.NBLAST library:
      library(nat.nblast)
      targetNeurons <- read.neurons("${PATH_TO_TESTS}/data/target",
        pattern="(1324365879|5813061260|424789697|1036637638).swc")
      queryNeuron <- neuronlist(read.neuron(
        "${PATH_TO_TESTS}/data/query/skel0_mb399b_jrc.swc"))
      scores <- nblast_allbyall(c(queryNeuron, targetNeurons),
        normalisation="mean")
      # final row of scores matrix contains relevant results
    """
    results = result_filename%'_fwdRev'
    results_from_R = [0.18933926, 0.1336908, 0.02367754, -0.8361671]
    with patch.object(sys, 'argv', ['', 'tests/data/query/skel0_mb399b_jrc.swc',
        '-tD', 'tests/data/target', '--dirVec', 'parent', '--fwdRev']):
      findNeuronMatches.runSearch()
    with open(results, 'r') as f:
      scores = [el[1] for el in json.load(f)]
      assert np.all(np.isclose(results_from_R, scores, rtol=1e-3, atol=1e-3)) == True
    os.remove(results)
