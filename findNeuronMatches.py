"""Conduct NBLAST search"""

import argparse, json, os
import numpy as np
import timeit
import sys

from common import globFiles
from swcHelper import SWCHelper
from nblast import NBLASTHelper

HEMI_ORIGIN_TO_BRAIN_CENTER = (26021, 22914, 20255)
MICROMETER_TO_HEMI_PIXELS = 125

def options():
  """Parse options for NBLAST search engine."""
  p = argparse.ArgumentParser(description=
    'Runs NBLAST search for a given query neuron skeleton (in SWC format) and' +
    ' returns a match score for every neuron in the Hemibrain database.')
  p.add_argument('query', help='path to SWC file for the query neuron')
  p.add_argument('-d', dest='dir', help='path to directory of SWC files of ' +
    'the target neurons (default: skeletons sub-folder)', default='skeletons')
  p.add_argument('--noRescale', dest='noRescale', help='skip rescaling ' +
    'coordinates of query neuron from micrometers to Hemibrain pixels' +
    ' (1 px / 8 nm)', action='store_true')
  p.add_argument('--noOriginTranslate', dest='noOriginTranslate', help='skip ' +
    'translation of origin of node coordinates from center of brain to ' + 
    'Hemibrain origin (roughly, the upper left corner of image)',
    action='store_true')
  p.add_argument('--reflectX', dest='reflectX', action='store_true',
    help='flip sign of X coords of the query neuron (reflect across Y axis.')
  p.add_argument('--anatO', dest='anatomicalOrigin', help='coordinates of the' +
    ' anatomical origin, where X and Y correspond to the center of the cavity' +
    ' between the nodulus and the ellipsoid body in the XY plane, and Z' +
    'corresponds to the midpoint along the anteroposterior axis.',
    default='0,0,0', metavar='X,Y,Z')
  p.add_argument('-n', dest='normalize', action='store_true', default=False,
    help='whether to normalize the NBLAST scores (default: False)')
  return p.parse_args()

startT = timeit.default_timer()
print('sys.argv:', sys.argv)
def runSearch():
  opts = options()
  anatomicalO = [-np.float32(coord) for coord in opts.anatomicalOrigin.split(',')]
  query = SWCHelper(opts.query, origin=anatomicalO, doPickle=False)
  if not opts.noRescale:
    query.rescale(MICROMETER_TO_HEMI_PIXELS)
  if opts.reflectX:
    query.reflectX()
  if not opts.noOriginTranslate:
    query.translateOrigin(HEMI_ORIGIN_TO_BRAIN_CENTER)
  targets = globFiles(opts.dir, 'swc')
  print('targets?', targets)
  nblast = NBLASTHelper(query)
  scores = nblast.calculateMatchScores(targets)
  print('socres?', scores)
  if opts.normalize:
    scores = scores / np.max(scores)
  with open('nblast_results_%s.json'%os.path.splitext(os.path.basename(
      opts.query))[0], 'w', encoding='utf-8') as f:
    json.dump(sorted(list(zip(targets, scores)), key=lambda x: x[1],
      reverse=True), f, ensure_ascii=False, indent=4)
  print('total compute time:', timeit.default_timer() - startT)

if __name__ == "__main__":
  runSearch()
