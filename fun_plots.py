import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation
import numpy as np

fig1 = plt.figure()
ax1 = plt.axes(projection='3d')
zline = np.linspace(0, 15, 1000)
xline = np.sin(zline)
yline = np.cos(zline)
ax1.plot3D(xline, yline, zline, 'gray')
zdata = 15 * np.random.random(100)
xdata = np.sin(zdata) + 0.1 * np.random.randn(100)
ydata = np.cos(zdata) + 0.1 * np.random.randn(100)
ax1.scatter3D(xdata, ydata, zdata, c=zdata, cmap='Greens');

def f(x, y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))

x = np.linspace(-6, 6, 30)
y = np.linspace(-6, 6, 30)
X, Y = np.meshgrid(x, y)
Z = f(X, Y)

fig2 = plt.figure()
ax2 = plt.axes(projection='3d')
ax2.contour3D(X, Y, Z, 50, cmap='binary')
ax2.set_title('contour')

fig3 = plt.figure()
ax3 = plt.axes(projection='3d')
ax3.contour3D(X, Y, Z, 50, cmap='binary')
ax3.plot_wireframe(X, Y, Z, color='black')
ax3.set_title('wireframe')

fig4 = plt.figure()
ax4 = plt.axes(projection='3d')
ax4.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='viridis', edgecolor='none')
ax4.set_title('surface')

r = np.linspace(0, 6, 20)
theta = np.linspace(-0.9 * np.pi, 0.8 * np.pi, 40)
r, theta = np.meshgrid(r, theta)
X = r * np.sin(theta)
Y = r * np.cos(theta)
Z = f(X, Y)
fig5 = plt.figure()
ax5 = plt.axes(projection='3d')
ax5.plot_surface(X, Y, Z, rstride=1, cstride=1,
                cmap='ocean', edgecolor='none')
ax5.set_title('partial polar grid')

theta = 2 * np.pi * np.random.random(1000)
r = 6 * np.random.random(1000)
x = np.ravel(r * np.sin(theta))
y = np.ravel(r * np.cos(theta))
z = f(x, y)

fig6 = plt.figure()
ax6 = plt.axes(projection='3d')
ax6.scatter(x, y, z, c=z, cmap='hsv', linewidth=0.5)
ax6.set_title('scatter surface triangulations')

fig7 = plt.figure()
ax7 = plt.axes(projection='3d')
ax7.plot_trisurf(x, y, z,
                cmap='cool', edgecolor='none')
ax7.set_title('surface triangulations')

theta = np.linspace(0, 2 * np.pi, 30)
w = np.linspace(-0.25, 0.25, 8)
w, theta = np.meshgrid(w, theta)
phi = 0.5 * theta
r = 1 + w * np.cos(phi)
x = np.ravel(r * np.cos(theta))
y = np.ravel(r * np.sin(theta))
z = np.ravel(w * np.sin(phi))
tri = Triangulation(np.ravel(w), np.ravel(theta))
fig8 = plt.figure()
ax8 = plt.axes(projection='3d')
ax8.plot_trisurf(x, y, z, triangles=tri.triangles,
                cmap='plasma', linewidths=0.2);
ax8.set_xlim(-1, 1); ax8.set_ylim(-1, 1); ax8.set_zlim(-1, 1)
ax8.set_title('Möbius strip')

plt.show()