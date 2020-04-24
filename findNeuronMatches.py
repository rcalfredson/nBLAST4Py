"""Conduct NBLAST search"""

import argparse, json, os
import numpy as np
import timeit
import sys

from common import globFiles
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
  p.add_argument('--reflectX', dest='reflectX', action='store_true',
    help='flip sign of X coords of the query neuron (reflect across Y axis.')
  p.add_argument('-n', dest='normalize', action='store_true', default=False,
    help='whether to normalize the NBLAST scores (default: False)')
  return p.parse_args()

startT = timeit.default_timer()
def runSearch():
  opts = options()
  query = SWCHelper(opts.query)
  if opts.rescale:
    query.rescale(opts.rescale)
  if opts.reflectX:
    query.reflectX()
  targets = globFiles(opts.dir, 'swc')
  print('skel X coords:', query.x)
  print('skel Y coords:', query.y)
  print('skel Z coords:', query.z)
  nblast = NBLASTHelper(query)
  scores = nblast.calculateMatchScores(targets)
  if opts.normalize:
    scores = scores / np.max(scores)
  with open('nblast_results_%s.json'%os.path.splitext(os.path.basename(
      opts.query))[0], 'w', encoding='utf-8') as f:
    json.dump(sorted(list(zip(targets, scores)), key=lambda x: x[1],
      reverse=True), f, ensure_ascii=False, indent=4)
  print('total compute time:', timeit.default_timer() - startT)

if __name__ == "__main__":
  runSearch()
