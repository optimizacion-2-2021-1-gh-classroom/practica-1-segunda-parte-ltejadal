import random
import tsplib95
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from ant_colony.utils import graph_optim_path

class ant():
    def __init__(self, G, r_len = float('inf'), route = []):
        
        self.graph = G
        self.seed = 19512959
        self.route = route
        self.r_len = r_len
        self.atraction_mat = None
        
    def walk_over_graph(self, 
                      init_node,
                      dist, 
                      atrac):
        
        x = [init_node]
        nodes = list(self.graph.nodes)
        lenghts = create_dic_dist_from_graph(self.graph)
        
        while len(x) < len(nodes):
            i = x[-1]
            neighbors = set(list(G.neighbors(i))) - set(x)
            if len(neighbors) == 0:
                break
        
            a_s = [atrac[i][j] for j in neighbors]
            next_ = random.choices(list(neighbors), weights= a_s)
            x = x + next_

        # distancia total del recorrido (se adiciona retorno al origen)
        l = sum([lenghts[i-1][i] for i in range(1, len(x))]) + lenghts[x[-1]][init_node] 

        # sumar regreso al origen
        self.route = x + [init_node]   
        self.r_len = l
            
    def plot_route(self, plt_size):
        graph_optim_path(self.graph, self.route, self.r_len, plt_size)
        
