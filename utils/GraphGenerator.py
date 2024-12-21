import math
import sys

import numpy as np

from algorithms.Graph import Graph

class GraphGenerator(object):

    def __init__(self, points: list[tuple[2]], edges: list[tuple[3]] = []):
        self.points = points
        self.edges = edges

    def __find_min_max_x_y(self):
        max_x, max_y = -1.0, -1.0
        min_x, min_y = sys.maxsize, sys.maxsize

        for v in self.points:
            max_x = max(max_x, v[0])
            max_y = max(max_y, v[1])
            min_x = min(min_x, v[0])
            min_y = min(min_y, v[1])

        return min_x, max_x, min_y, max_y
        
    def add_gaussian_noise(self, noise=0.1):
        min_x, max_x, min_y, max_y = self.__find_min_max_x_y()

        size = int(np.ceil(len(self.points) * noise))
        for i in range(size):
            x = np.random.uniform(min_x, max_x)
            y = np.random.uniform(min_y, max_y)
            self.points.append((x, y))

        return self
    
    def add_clustered_noise(self, type='', noise=0.1):
        min_x, max_x, min_y, max_y = self.__find_min_max_x_y()

        size = int(np.ceil(len(self.points) * noise))
        if type == '':
            raise ValueError('No parameter given for type of clustered noise, \n\ttry: circle, horizontal_line or vertical_line')
        elif type == 'circle':
            center = ((max_x + min_x) / 2, (max_y + min_y) / 2)
            radius = min(max_x - min_x, max_y - min_y) * 0.7 / 2
            pi = math.pi
            for i in range(size):
                x = math.cos(2 * pi / size * i) * radius + center[0]
                y = math.sin(2 * pi / size * i) * radius + center[1]
                self.points.append((x, y))
        elif type == 'horizontal_line':
            y_center = (max_y + min_y) / 2
            interval = (max_x - min_x) / size
            current_x = min_x
            for i in range(size):
                self.points.append((current_x, y_center))
                current_x += interval
        elif type == 'vertical_line':
            x_center = (max_x + min_x) / 2
            interval = (max_y - min_y) / size
            current_y = min_y
            for i in range(size):
                self.points.append((x_center, current_y))
                current_y += interval
        else:
            NotImplementedError('%s not implemented' % type)
        
        return self

    def to_graph(self, gen_pair_wise = False, f = None) -> Graph:
        G = Graph()
        G.points = self.points
        G.distance_function = f

        # add a vertex for each point (map vertex id to xy data from points list)
        for i in range(len(G.points)):
            G.add_vertex(i)

        def euclidean_distance(p1, p2):
            return math.ceil(math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2))

        if gen_pair_wise:
            # add an edge for each possible point
            for i in G.V:
                for j in G.V:
                    if i == j:
                        continue
                    
                    # if no distance function is provided, we assume euclidean distance
                    if f is None:
                        f = euclidean_distance
                        
                    w = f(G.points[i], G.points[j])

                    G.add_edge(i, j, w)

        # add any remaining edges the user already specified (override any generated edges if needed)
        if len(self.edges) > 0:
            for edge in self.edges:
                if len(edge) == 3:
                    (i, j, w) = edge
                elif len(edge) == 2:
                    (i, j) = edge
                    if f is None:
                        f = euclidean_distance
                    w = f(G.points[i], G.points[j])
                else:
                    print(f"edge not a tuple of length 2 or 3: {edge}")
                    continue

                G.add_edge(i, j, w)

        # # useful for visualization later
        # min_x, max_x, min_y, max_y = self.__find_min_max_x_y()
        # G.og_min_x = min_x
        # G.og_max_x = max_x
        # G.og_min_y = min_y
        # G.og_max_y = max_y
        
        return G