import argparse, glob, json, os
import numpy as np

neuronsByType = dict()
with open('data/hemibrainNeuronsToType.json', 'r') as myFile:
  neuronsToType = json.load(myFile)

for key in neuronsToType:
  if neuronsToType[key] in neuronsByType:
    neuronsByType[neuronsToType[key]].append(key)
  else:
    neuronsByType[neuronsToType[key]] = [key]

# look for data in base directory for time being
# input: list of neurons to analyze
def options():
  """Parse options for NBLAST results analyzer."""
  p = argparse.ArgumentParser(description=
    'Analyzes results of an NBLAST search (currently, analysis only works for' +
      'Hemibrain self-queries.\n\n The success statistic outputted by the ' +
      'script measures what proportion of neurons have another neuron of ' +
      'their type in the top ten results. For example, if there are 15 query' +
      ' neurons, 12 of them belonging to multi-neuron types, and 7 of them ' +
      'having a same-type neuron in top ten, then success is 0.58.')
  p.add_argument('queryList', help='path to newline-separated list of query ' +
    'skeleton IDs to analyze')
  p.add_argument('resDir', help='path to directory of results files')
  p.add_argument('--useFwd', action='store_true', help='look for forward ' +
    'search results first, not forward-reverse averaged ones')
  return p.parse_args()

opts = options()

with open(opts.queryList, 'rt') as queryList:
    neurons = queryList.read().splitlines()

successes, total = 0, len(neurons)
typeWithTwoOrMoreCount = 0
noTypeCount, singletonTypes = 0, []
for nI, neuron in enumerate(neurons):
  print('Analyzing neuron %s, %i of %i'%(neuron, nI + 1, total))
  nType = neuronsToType[neuron]
  if len(nType) == 0:
    noTypeCount += 1
  elif len(neuronsByType[nType]) == 1:
    singletonTypes.append(nType)
  else:
    typeWithTwoOrMoreCount += 1
    neuronsInType = [nId for nId in neuronsByType[nType] if nId != neuron]
    fwd, fwdRev = [glob.glob(os.path.join(opts.resDir, 'nblast_results' + \
        '_%s%s.json'%(neuron, suffix))) for suffix in ('', '_fwdRev')]
    if len(fwd) == 0 and len(fwdRev) == 0:
      print('note: no results found for neuron %s'%neuron)
      continue
    if opts.useFwd:
      resultsFile = fwd[0] if len(fwd) > 0 else fwdRev[0]
    else:
      resultsFile = fwdRev[0]
    with open(resultsFile, 'r') as myFile:
      searchResults = [os.path.basename(target[0]).split('.')[0] for target \
        in json.load(myFile)[1:]]
    if np.any([searchResult in neuronsInType for searchResult in \
        searchResults[0:9]]):
      successes += 1

print('\nsingleton types:', singletonTypes)
print('num. singleton type:', len(singletonTypes))
print('num. neurons without any type:', noTypeCount)
print('successes:', successes,
  '\ttotal belonging to type with two or more neurons:', typeWithTwoOrMoreCount)
print('success proportion:', successes / typeWithTwoOrMoreCount)
print('total number neurons:', total)
