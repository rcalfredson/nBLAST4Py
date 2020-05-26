""""Render neuron skeletons from SWC files with orientation landmarks"""

import argparse, os

import matplotlib.pyplot as plt
import trimesh
import numpy as np
from mpl_toolkits.mplot3d import Axes3D, art3d

from swcHelper import SWCHelper

def options():
  """Parse options for NBLAST search engine."""
  p = argparse.ArgumentParser(description=
    'Runs NBLAST search for a given query neuron skeleton (in SWC format) and' +
    ' returns a match score for every neuron in the Hemibrain database.')
  p.add_argument('swcs', help='comma-separated paths to SWC files of neurons' +
    ' to view')
  p.add_argument('--reflectX', help='flip sign of X coords of the first ' +
    'inputted neuron by reflecting across the inputted X midpoint of the ' +
    'brain (e.g., 314 microns for JRC2018F).', type=float)
  return p.parse_args()

opts = options()
swcPaths, swcs = opts.swcs.split(','), []
print('SWCs:', opts.swcs) 
for pathI, swcPath in enumerate(swcPaths):
  swcs.append(SWCHelper(swcPath))
  if pathI == 0 and opts.reflectX is not None:
    swcs[-1].reflectX(opts.reflectX)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for swcI, swc in enumerate(swcs):
  ax.scatter(swc.x, swc.y, zs=swc.z, label=os.path.basename(swcPaths[swcI]))
ax.plot([258, 290], [85, 85], zs=[74, 74], c='r', marker='*', linewidth=5)
ax.scatter([258], [30], zs=[74], c='r', marker='p', s=200)
ax.scatter([270], [128], zs=[43], c='r', marker='x', s=200)
# brainSurfaces = ('al_R', 'alPrime_R', 'bl_R', 'blPrime_R', 'EB', 'lh_R')
# colors = ('b', 'springgreen', 'y', 'darkorange', 'r', 'magenta')
# for sI, surfName in enumerate(brainSurfaces):
#   surf = trimesh.load("C:\\Users\\Tracking\\nblast-data\\brainSurfaces\\transformed\\%s.obj"%surfName)
#   v = np.array(surf.vertices)
#   f = np.array(surf.faces)
#   pc = art3d.Poly3DCollection(v[f], alpha=0.4)
#   pc.set_facecolor(colors[sI])
#   ax.add_collection(pc)
# ax.view_init(elev=-90., azim=-90)
# ax.set_xlim(160)
plt.legend()
plt.show()
