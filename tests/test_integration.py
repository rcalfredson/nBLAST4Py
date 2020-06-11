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
    implementation in R. Conditions: parent-based tangent vector calculation,
    forward-reverse averaging.

    How to replicate results in R using the nat.NBLAST library:
      library(nat.nblast)
      targetNeurons <- read.neurons("${PATH_TO_TESTS}/data/target",
        pattern="(1324365879|5813061260|424789697|1036637638).swc")
      queryNeuron <- neuronlist(read.neuron(
        "${PATH_TO_TESTS}/data/query/skel0_mb399b_jrc.swc"))
      scores <- nblast_allbyall(c(queryNeuron, targetNeurons),
        normalisation="mean")
      # final row of scores contains relevant results
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

def testNeighborBasedTangent():
    """Ensure the results of NBLAST test match those from the existing
    implementation in R. Conditions: nearest-neighbor-based vector calculation.

    How to replicate results in R using the nat.NBLAST library:
      library(nat.nblast)
      targetNeurons <- read.neurons("${PATH_TO_TESTS}/data/target",
        pattern="(1324365879|5813061260|424789697|1036637638).swc")
      queryNeuron <- read.neuron(
        "${PATH_TO_TESTS}/data/query/skel0_mb399b_jrc.swc")
      scores <- nblast(dotprops(queryNeuron, resample=1, k=5),
        dotprops(targetNeurons, resample=1, k=5))
    """
    results = result_filename%''
    results_from_R = [7380.609, 7070.962, 5926.261, -16512.227]
    with patch.object(sys, 'argv', ['', 'tests/data/query/skel0_mb399b_jrc.swc',
        '-tD', 'tests/data/target']):
      findNeuronMatches.runSearch()
    with open(results, 'r') as f:
      scores = [el[1] for el in json.load(f)]
      assert np.all(np.isclose(results_from_R, scores, rtol=1e-3, atol=1e-3)) == True
    os.remove(results)

def testNeighborBasedTangentFwdRev():
    """Ensure the results of NBLAST test match those from the existing
    implementation in R. Conditions: nearest-neighbor-based vector calculation,
    forward-reverse averaging.

    How to replicate results in R using the nat.NBLAST library:
      library(nat.nblast)
      targetNeurons <- read.neurons("${PATH_TO_TESTS}/data/target",
        pattern="(1324365879|5813061260|424789697|1036637638).swc")
      queryNeuron <- neuronlist(read.neuron(
        "${PATH_TO_TESTS}/data/query/skel0_mb399b_jrc.swc"))
      scores <- nblast_allbyall(dotprops(c(targetNeurons, queryNeuron),
        resample=1, k=5), normalisation="mean")
      # final row of scores contains relevant results
    """
    results = result_filename%'_fwdRev'
    results_from_R = [0.19463832, 0.1283570, 0.01524718, -0.8327490]
    with patch.object(sys, 'argv', ['', 'tests/data/query/skel0_mb399b_jrc.swc',
        '-tD', 'tests/data/target',  '--fwdRev']):
      findNeuronMatches.runSearch()
    with open(results, 'r') as f:
      scores = [el[1] for el in json.load(f)]
      assert np.all(np.isclose(results_from_R, scores, rtol=5e-2, atol=5e-2)) == True
    os.remove(results)
