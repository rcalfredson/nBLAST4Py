"""Conduct NBLAST search"""

import argparse, json, os, random
import numpy as np
import timeit
import subprocess, sys
from multiprocessing import Pool as ThreadPool

from common import globFiles
from largestNeurons import largest_neurons
from swcHelper import SWCHelper
from nblast import NBLASTHelper

def options():
  """Parse options for NBLAST search engine."""
  p = argparse.ArgumentParser(description=
    'Runs NBLAST search for a given query neuron skeleton (in SWC format) and' +
    ' returns a match score for every neuron in the Hemibrain database.')
  p.add_argument('query', help='path to SWC file for the query neuron or ' +
    'directory of SWC files to query')
  p.add_argument('-qL', help='path to newline-separated text file listing ' +
    'skeletons to query if "query" arg is a directory; if qL is omitted, then' +
    ' every SWC file in the query directory will be used')
  p.add_argument('-tD', help='path to directory of SWC files of the target ' +
    'neurons (default: skeletons sub-folder)', default='skeletons')
  p.add_argument('--nThreads', help='number of threads to use for ' +
    'simultaneous NBLAST searches of different query neurons (note: only ' +
    'decreases processing time if you have multiple query neurons, i.e., the ' +
    'duration of each individual search does not decrease)',
    type=int, default=1)
  p.add_argument('--visualComp', action='store_true', default=False, help=
    'output visual comparisons between the query neuron and the top 4 target' +
    ' neurons')
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

def runSingleThreadedSearch(args):
  queries, opts = args
  useParent = opts.dirVec=='parent'
  for query in queries:
    print('Running query for', query)
    query = SWCHelper(query, dirVectorFromParent=useParent,
      reflectX=opts.reflectX)
    targets = globFiles(opts.tD, 'swc')
    random.shuffle(targets)
    nblast = NBLASTHelper(query, dirVectorFromParent=useParent,
      fwdRevAvg=opts.fwdRev, normalize=opts.normalize)
    scores = nblast.calculateMatchScores(targets)
    sortedScores = sorted(list(zip(targets, scores)), key=lambda x: x[1],
        reverse=True)
    if opts.visualComp:
      for ss in sortedScores[0:4]:
        my_env = os.environ.copy()
        my_env["PATH"] = my_env["PATH"]
        subprocess.call(["Rscript", "--vanilla", "viewNeurons.r", ss[0],
          query.path], shell=True, env=my_env)
    for i, ss in enumerate(sortedScores):
      if os.path.basename(ss[0]) in largest_neurons:
        sortedScores[i] = ("%s (note: is among 100 largest Hemibrain neurons)"%(
          sortedScores[i][0]), ss[1])
    with open('nblast_results_%s%s.json'%(os.path.splitext(os.path.basename(
        query.path))[0], "_fwdRev" if opts.fwdRev else ""), 'w',
        encoding='utf-8') as f:
      json.dump(sortedScores, f, ensure_ascii=False, indent=4)

def getThreadLists():
  opts = options()
  qIsFile, qIsDir = os.path.isfile(opts.query), os.path.isdir(opts.query)
  if not qIsDir and not qIsFile:
    print('Query must be a file or directory')
    sys.exit()
  if qIsFile:
    queries = [opts.query]
  elif qIsDir and not opts.qL:
    queries = globFiles(opts.query, 'swc')
  else:
    with open(opts.qL, 'rt') as queryList:
      neurons = queryList.read().splitlines()
      queries = [os.path.join(opts.query, neuron) for neuron in neurons]
  nThreads = opts.nThreads
  return [queries[i::nThreads] for i in range(nThreads)], opts

def startThreadedSearch(threadLists, opts):
  pool = ThreadPool(len(threadLists))
  pool.map(runSingleThreadedSearch, [[threadLists[i], opts] for i in \
    range(len(threadLists))])

def runSearch():
  startThreadedSearch(*getThreadLists())
  print('total compute time:', timeit.default_timer() - startT)

if __name__ == "__main__":
  runSearch()
