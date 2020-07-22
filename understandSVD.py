import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
closestPts = np.random.randint(low=0, high=10, size=(5, 3))
diffFromMean = closestPts - np.mean(closestPts, axis=1, keepdims=True)
inertia = np.matmul(diffFromMean.T, diffFromMean)

def quickPlot(ax, data, marker=None):
    ax.scatter(data[:, 0], data[:, 1], data[:, 2], marker=marker, c='r')

quickPlot(ax, diffFromMean, marker='^')
v1d1 = np.linalg.svd(inertia)
print('diffFromMean', diffFromMean)
print('first eigenvector:', v1d1[0][:, 0])
eigen1 = v1d1[0][:, 0]
ax.quiver([0], [0], [0], [eigen1[0]], [eigen1[1]], [eigen1[2]],
  length=4, color='r')
ax.quiver([0], [0], [0], [v1d1[0][:, 1][0]], [v1d1[0][:, 1][1]],
  [v1d1[0][:, 1][2]], length=4, color='m')
ax.quiver([0], [0], [0], [v1d1[0][:, 2][0]], [v1d1[0][:, 2][1]],
  [v1d1[0][:, 2][2]], length=4, color='y')
plt.show()