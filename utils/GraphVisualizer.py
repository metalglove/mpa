import numpy as np
from scipy.spatial import Voronoi
from matplotlib import pyplot as plt
import os

from algorithms.Graph import Component, Graph


class GraphVisualizer:
    def __init__(self, G: Graph, save = False, dir = ''):
        self.G = G
        self.plot_calls = 0
        self.save = save
        self.dir = dir

    def __savefig(self, title):
        if self.save:
            directory = 'GraphVisualizerResults'
            if self.dir != '':
                directory = f'{directory}/{self.dir}'
            if not os.path.exists(directory):
                os.makedirs(directory)
            plt.savefig(f'{directory}/{title}.png')

    def gca(self, ax):
        if ax is None:
            plt.figure()
            ax = plt.gca()
        return ax
        
    def plot_graph(self, title = '', ax = None):
        ax = self.gca(ax)

        xs, ys = [], []
        for x in self.G.V.keys():
            xs.append(self.G.points[x][0])
            ys.append(self.G.points[x][1])
        ax.set_title(title)
        ax.scatter(xs, ys, c='r')

        if self.plot_calls == 0:
            self.xlim = ax.get_xlim()
            self.ylim = ax.get_ylim()
        else:
            ax.set_xlim(self.xlim)
            ax.set_ylim(self.ylim)

        self.plot_calls = self.plot_calls + 1

        self.__savefig(title)


    def plot_component_graph(self, title = '', ax = None):
        ax = self.gca(ax)

        components = [component for component in self.G.components if type(component) is Component]
        
        title = f"{title} components {len(components)}"
        colors = plt.get_cmap('viridis')(np.linspace(0, 1, len(components)))

        ax.set_title(title)

        for i in range(len(components)):
            component = components[i]

            xs, ys = [], []
            for x in component.V:
                xs.append(self.G.points[x][0])
                ys.append(self.G.points[x][1])

            ax.scatter(xs, ys, color=colors[i])

        if self.plot_calls == 0:
            self.xlim = ax.get_xlim()
            self.ylim = ax.get_ylim()
        else:
            ax.set_xlim(self.xlim)
            ax.set_ylim(self.ylim)

        self.plot_calls = self.plot_calls + 1
        
        self.__savefig(title)


    def plot_kmeans(self, title = '', centroids = None, voronoi = False, ax = None):
        ax = self.gca(ax)
        ax.clear()

        tempsave = self.save
        self.save = False
        self.plot_graph(title=title, ax = ax)
        self.save = tempsave

        if centroids is None:
            return

        # plot centroids
        ax.plot(centroids[:,0], centroids[:,1], 'ko')

        if voronoi:
            # compute Voronoi tesselation
            vor = Voronoi(centroids)

            # plot
            regions, vertices = self.__voronoi_finite_polygons_2d(vor, radius = 150)

            # colorize
            for region in regions:
                polygon = vertices[region]
                ax.fill(*zip(*polygon), alpha=0.4)
        
        self.__savefig(title)
            

    def __voronoi_finite_polygons_2d(self, vor, radius=None):
        """
        Reconstruct infinite voronoi regions in a 2D diagram to finite
        regions.

        Parameters
        ----------
        vor : Voronoi
            Input diagram
        radius : float, optional
            Distance to 'points at infinity'.

        Returns
        -------
        regions : list of tuples
            Indices of vertices in each revised Voronoi regions.
        vertices : list of tuples
            Coordinates for revised Voronoi vertices. Same as coordinates
            of input vertices, with 'points at infinity' appended to the
            end.

        """

        if vor.points.shape[1] != 2:
            raise ValueError("Requires 2D input")

        new_regions = []
        new_vertices = vor.vertices.tolist()

        center = vor.points.mean(axis=0)
        if radius is None:
            radius = vor.points.ptp().max()*2

        # Construct a map containing all ridges for a given point
        all_ridges = {}
        for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
            all_ridges.setdefault(p1, []).append((p2, v1, v2))
            all_ridges.setdefault(p2, []).append((p1, v1, v2))

        # Reconstruct infinite regions
        for p1, region in enumerate(vor.point_region):
            vertices = vor.regions[region]

            if all([v >= 0 for v in vertices]):
                # finite region
                new_regions.append(vertices)
                continue

            # reconstruct a non-finite region
            ridges = all_ridges[p1]
            new_region = [v for v in vertices if v >= 0]

            for p2, v1, v2 in ridges:
                if v2 < 0:
                    v1, v2 = v2, v1
                if v1 >= 0:
                    # finite ridge: already in the region
                    continue

                # Compute the missing endpoint of an infinite ridge

                t = vor.points[p2] - vor.points[p1] # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])  # normal

                midpoint = vor.points[[p1, p2]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[v2] + direction * radius

                new_region.append(len(new_vertices))
                new_vertices.append(far_point.tolist())

            # sort region counterclockwise
            vs = np.asarray([new_vertices[v] for v in new_region])
            c = vs.mean(axis=0)
            angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
            new_region = np.array(new_region)[np.argsort(angles)]

            # finish
            new_regions.append(new_region.tolist())

        return new_regions, np.asarray(new_vertices)