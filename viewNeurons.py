""""Render neuron skeletons from SWC files with orientation landmarks"""

import argparse, os

import matplotlib.pyplot as plt

from swcHelper import SWCHelper

def options():
  """Parse options for NBLAST search engine."""
  p = argparse.ArgumentParser(description=
    'Runs NBLAST search for a given query neuron skeleton (in SWC format) and' +
    ' returns a match score for every neuron in the Hemibrain database.')
  p.add_argument('swcs', help='comma-separated paths to SWC files of neurons' +
    ' to view')
  return p.parse_args()

opts = options()
swcPaths, swcs = opts.swcs.split(','), []
print('SWCs:', opts.swcs) 
for swcPath in swcPaths:
  swcs.append(SWCHelper(swcPath))
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for swc in swcs:
  ax.scatter(swc.x, swc.y, zs=swc.z)
# XYZ
ax.plot([258, 258], [85, 85], zs=[20, 74], c='r', marker='*', linewidth=5)
ax.scatter([258], [30], zs=[74], c='r', marker='p', s=200)
ax.scatter([270], [128], zs=[43], c='r', marker='x', s=200)
plt.legend([os.path.basename(swcPath) for swcPath in swcPaths])
plt.show()
