import random
import tsplib95
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from ant_colony.utils import *

class colony():
    """Clase que representa una colonia de hormigas que recorren
    el grafo asignado para resolver el problema TSP.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        init_node (int): Nodo inicial del recorrido.
        best_route (list, optional): Ruta con respecto a la cual se quiere mejorar.
        best_dist ([type], optional): Distancia total del recorrido x_best.
        n_ants (int, optional): Número de hormigas. Default es 2.
        max_iter (int, optional): [description]. Default es 100.
        alpha (int, optional): Factor de influencia de tau. Defaults to 1.
        beta (int, optional): Factor de influencia de eta. Defaults to 5.
        rho (float, optional): Tasa de evaporación de las feromonas. Defaults to .5.
        verbose (int, optional): Imprime progreso del algoritmo cada K iteraciones. Defaults to 10.
    """
    def __init__(self, G, init_node,
                 best_route = [],
                 best_dist = float('inf'),
                 n_ants=2,
                 max_iter=100, 
                 alpha=1, 
                 beta=5, 
                 rho=.5, 
                 verbose=10):
        self.graph = G
        self.init_node = init_node
        self.best_route = best_route
        self.best_dist = best_dist
        self.lenghts = create_dic_dist_from_graph(self.graph)
        self.n_ants = n_ants
        self.ants = [ant(G) for i in range(self.n_ants)]
        self.max_iter = max_iter
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.tau = init_ferom(self.graph)
        self.eta = init_atrac(self.graph, self.lenghts)
        
    def _update_pheromone_levels(self, route, dist_route):
        """Actualiza el nivel de feromonas en las respectivas trayectorias
        del grafo.

        Args:
            route (lst): Lista que incluye un recorrido por el grafo.
            dist_route (float): Distancia de la ruta.
        """
        for i in range(1, len(route[:-1])):
            self.tau[i-1][i] += 1/dist_route
        self.tau[route[:-1][-1]][self.init_node]
        
    def _update_many_pheromone_levels(self, routes, distances):
        """Actualiza los niveles de feromonas para diferentes rutas
        recorridas por diferentes hormigas.

        Args:
            routes (lst of lst): Lista que contiene los recorridos 
            realziados por diferentes hormigas.
            distances (lst of floats): Lista con las distancias de
            las rutas.
        """
        if (len(distances) == len(self.graph.nodes)):
            for i in range(len(routes)):
                self._update_pheromone_levels(routes[i], distances[i])
            
    def _evaporates_pheromone(self):
        """Evapora los niveles de feromonas en todos los tramos del 
        grafo.
        """
        for e in self.tau:
            for v in self.tau:
                self.tau[e][v] = (1-self.rho)*v
            
    def _colony_run(self, A):
        """La hormigas de la colonia realizan recorridos 
        independientes simultáneamente.

        Args:
            A (dic): nivel de atracción de los nodos con respecto
            a sus vecinos.
        """
        distances = []
        routes = []
        for ant in self.ants:
            ant.walk_over_graph(init_node=self.init_node, 
                                dist = self.lenghts, 
                                atrac = A)
            
            routes.append(ant.route)
            distances.append(ant.r_len)
            
        # updates pheromone levels
        self._update_many_pheromone_levels(routes, distances)
            
        # best route
        min_dist = min(distances)
        bst_idx = distances.index(min_dist)
        bst_route = self.ants[bst_idx].route
        
        # improves route if possible
        if min_dist < self.best_dist:
            self.best_dist = min_dist
            self.best_route = bst_route
            
    def solve_tsp(self):
        """Resuelve el problema TSP.
        """
        route = self.best_route
        dist = self.best_dist
        
        for k in range(self.max_iter):
            A = atraccion_nodos(self.graph,tau= self.tau, eta=self.eta, 
                                alpha=self.alpha, beta=self.beta)
            
            if k>1:
                self._evaporates_pheromone()
                
            # ants running across the graph
            self._colony_run(A)

    def plot_route(self, plt_size=(12, 8)):
        """Grafica la trayectoria encontrada por la colonia en el grafo.

        Args:
            plt_size (tuple, optional): Tamaño del gŕafico (ancho x altura). Defaults es (12, 8).
        """
        graph_optim_path(self.graph, self.best_route, self.best_dist, plt_size)
            
    def optim_hyper_params(self):
        """[summary]
        """
        None

class ant():
    """Clase que representa una hormiga de la colonia y realizará
    recorridos por el grafo.
    
    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
    """
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
        """La hormiga intenta recorrer el grafo y volver
        al origen sin repetir otros nodos.

        Args:
            init_node (int): Nodo inicial del recorrido.
            dist (dic): Diccionario de distancias de las trayectorias.
            atrac (dic): Diccionario de atracción de los nodos con 
            relación a sus vecinos.
        """
        
        x = [init_node]
        nodes = list(self.graph.nodes)
        lenghts = create_dic_dist_from_graph(self.graph)
        
        while len(x) < len(nodes):
            i = x[-1]
            neighbors = set(list(self.graph.neighbors(i))) - set(x)
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
        """Grafica la trayectoria encontrada por la colonia en el grafo.

        Args:
            plt_size (tuple, optional): Tamaño del gŕafico (ancho x altura). Defaults es (12, 8).
        """
        graph_optim_path(self.graph, self.route, self.r_len, plt_size)