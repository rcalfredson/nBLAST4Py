"""Conduct NBLAST search"""

import argparse, json, os
import numpy as np
import timeit
import sys

from common import globFiles
from largestNeurons import largest_neurons
from swcHelper import SWCHelper
from nblast import NBLASTHelper

def options():
  """Parse options for NBLAST search engine."""
  p = argparse.ArgumentParser(description=
    'Runs NBLAST search for a given query neuron skeleton (in SWC format) and' +
    ' returns a match score for every neuron in the Hemibrain database.')
  p.add_argument('query', help='path to SWC file for the query neuron')
  p.add_argument('-d', dest='dir', help='path to directory of SWC files of ' +
    'the target neurons (default: skeletons sub-folder)', default='skeletons')
  p.add_argument('--rescale', help='rescale coordinates of query neuron by ' +
    'the given factor', type=float)
  p.add_argument('--reflectX', help='flip sign of X coords of the query neuron ' +
    'by reflecting across the inputted X midpoint of the brain (e.g., 314 ' +
    ' microns for JRC2018F).', type=float)
  p.add_argument('--dirVec', default='nn', help='specify method used to ' +
    'calculate direction vectors of points along skeleton. Values: 1) nn for ' +
    '5-point nearest neighbor singular value decomposition with resampling or '+
    '2) parent for direction vectors pointing to each point from its parent.')
  p.add_argument('--fwdRev', action='store_true', default=False,
    help='whether to average the forward and reverse NBLAST results (swapping' +
    'role of query and target neuron)')
  p.add_argument('-n', dest='normalize', action='store_true', default=False,
    help='whether to normalize the NBLAST scores (default: False)')
  return p.parse_args()

startT = timeit.default_timer()
def runSearch():
  opts = options()
  useParent = opts.dirVec=='parent'
  query = SWCHelper(opts.query, dirVectorFromParent=useParent,
    reflectX=opts.reflectX)
  if opts.rescale:
    query.rescale(opts.rescale)
  targets = globFiles(opts.dir, 'swc')
  nblast = NBLASTHelper(query, dirVectorFromParent=useParent,
    fwdRevAvg=opts.fwdRev, normalize=opts.normalize)
  scores = nblast.calculateMatchScores(targets)
  for i, target in enumerate(targets):
    if os.path.basename(target) in largest_neurons:
      targets[i] = "%s (note: is among 100 largest Hemibrain neurons)"%targets[i]
  with open('nblast_results_%s%s.json'%(os.path.splitext(os.path.basename(
      opts.query))[0], "_fwdRev" if opts.fwdRev else ""), 'w', encoding='utf-8') as f:
    json.dump(sorted(list(zip(targets, scores)), key=lambda x: x[1],
      reverse=True), f, ensure_ascii=False, indent=4)
  print('total compute time:', timeit.default_timer() - startT)

if __name__ == "__main__":
  runSearch()
