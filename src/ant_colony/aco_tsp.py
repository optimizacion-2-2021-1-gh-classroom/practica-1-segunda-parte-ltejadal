
import random
import tsplib95
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint
from itertools import combinations, groupby

def rand_dist_matrix(n_points, graph=True, scale_factor=1, round_factor=4, 
                     seed=1951959, int=False):

    """Crea matriz aleatoria de distancias. Retorna su versión nuḿerica en numpy o
    su version en grafo con networksx.
    
    Args:

        n_points (int): ńumero de nodos de la matriz de distancias.

        graph (bool): True si se quiere retorna la matriz como un grafo de nwtworkx.

        scale_factor (int): Factor de escala de la matriz.

        round_factor (int): Factor de redondeo de la matriz.

        seed (int): Semilla aleatoria para reproducibilidad de resultados.

        int (bool): True para obtener matriz con distancias de enteros.

    Returns:

        dist_mat (numpy array): Si graph=False

        nx.from_numpy_matrix(dist_mat) (graph): Si graph=True

    """
    random.seed(seed)
    import scipy.spatial as spatial
    # Basado en https://www.w3resource.com/python-exercises/numpy/python-numpy-random-exercise-12.php
    pts = np.random.random((n_points,2))
    x, y = np.atleast_2d(pts[:,0], pts[:,1])
    # Vector de distancias para cada punto 
    dist_mat = np.sqrt((x - x.T)**2 + (y - y.T)**2)
    if int:
        dist_mat = (dist_mat*scale_factor).round(round_factor)
    # Matriz de distancias
    if graph:
        return nx.from_numpy_matrix(dist_mat) 
    else:
        return dist_mat
    
def create_dic_dist(dist):

    """Crea diccionario de distancias entre nodos a partir de la versión
    numérica de la matriz de distancias.
    
    Args:

        dist (numpy array): Arreglo con la matriz de distancias.
    
    Returns:

        lenghts (dic): Diccionario de distancias de los nodos.

    """
    lenghts = {}
    for node, z in enumerate(dist):
        lenghts[node] = {}
        for neighbor, y in enumerate(z):
            lenghts[node][neighbor] = y
    return lenghts 

def create_dic_dist_from_graph(G):

    """Crea diccionario de distancias entre nodos a partir de un grafo. 
    
    Args:

        G (graph): Grafo con distancias asociadas entre nodos

    Returns:

        lenghts (dic): Diccionario de distancias de los nodos.
    
    """
    nodos = list(G.nodes)
    G_num = nx.to_numpy_matrix(G)
    lenghts = {}
    for node, z in enumerate(G_num):
        lenghts[node] = {}
        for neighbor in nodos:
            lenghts[node][neighbor] = z[0, neighbor]

    return lenghts  

def plot_graph(G, m_plot, seed=19511959):

    """Grafica red en su versión de coordenadas o de grafo. Fija las posiciones
    de forma determinista con una semilla (seed).
    
    Args:

        G (graph):

        m_plot (str): Tipo de gráfico. 
                        Ops:
                        - coordinate: Coordenadas X, Y
                        - graph: Grafo

        seed (int): Semilla para determinar las posiciones de los nodos en la 
        visualización.

    
    Returns:

        None
    
    """
    pos = nx.fruchterman_reingold_layout(G, center=(0,0), seed=seed) 
    colors = range(20)
    if m_plot=='coordinate':
        plt.figure(figsize=(7, 7))
        for k, p in pos.items():
            plt.scatter(p[0], p[1], marker='o', s=50, edgecolor='None')
        plt.tight_layout()
        plt.axis('equal')
        plt.show()
    elif m_plot=='graph': 
        edges, weights = zip(*nx.get_edge_attributes(G,'weight').items())
        
        nx.draw(G, 
                node_color='lightblue', 
                with_labels=True,
                edge_color = [i[2]['weight'] for i in G.edges(data=True)], 
                edge_cmap=plt.cm.Blues, 
                pos=pos)
        
# inicializar diccionario de niveles de feromonas de los nodos
def init_ferom(G, init_lev=1.0):

    """Inicialización de diccionario con nivel de feromonas de los nodos.
    
        Args:

            G (graph): Representación en grafo de la red a analizar. 

            init_lev (float): Nivel de inicialización de feromona para todos
            los nodos.

        Returns:
        
            tau (dic): Diccionario con nivel de feronomas de los nodos.

    """
    nodos = list(G.nodes)
    tau = {}

    for nodo in nodos:
        tau[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            tau[nodo][neighbor] = init_lev
    return tau

# inicializar niveles de atracción de cada nodo
def init_atrac(G, lenghts):

    """Inicialización de diccionario con nivel de atracción de los nodos.
    
        Args:

            G (graph): Representación en grafo de la red a analizar. 

            lenghts (dic): Optional. Si se incluye se inicializa el nivel
            de atracción de los archos con el inverso de las distancias. 

        Returns:
        
            eta (dic): Diccionario con nivel de atracción de los nodos.

    """
    nodos = list(G.nodes)
    eta = {}
    
    for nodo in nodos:
        eta[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            # eta[nodo][neighbor] = 1/lenghts[nodo][neighbor]
            eta[nodo][neighbor] = 1
    return eta

# atracción de cada nodo
def atraccion_nodos(G, tau, eta, alpha=1, beta=5):

    """Calcula el grado de atracción de un nodo n perteneciente al grafo G.

    Args:

        G (networkx graph): Grafo de networkx.

        tau (dic): Diccionario con niveles de feromonas de los vecinos de cada nodo.

        eta (dic): Diccionario con nive de atracción de los vecinos de cada nodo.

        alpha (float): Factor de influencia (exponente del nivel de feronomas).

        beta (int): exponente anterior.

    Returns:

        atrac (dic): Diccionario con los valores de atracción de los vecinos del nodo j.

    """
    dic_attr = {}
    # componentes del grafo
    nodos = list(G.nodes)
    
    
    for nodo in nodos:
        dic_attr[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            attr = tau[nodo][neighbor]**alpha + eta[nodo][neighbor]**beta
            dic_attr[nodo][neighbor] = attr
        
    return dic_attr

def hormiga_recorre(G, lenghts, dic_attr, tau, init_point, x_best, y_best):

    """Calcula la ruta y distancia más cortas con respecto al benchmark provisto, 
    luego del recorrido (o su intento) de una hormiga por la red.

    Args:

        G (networkx graph): Grafo de la red.

        lenghts (dic): Diccionario de distancias entre nodos.

        dic_attr (dic): Diccionario de atracción de los nodos.

        tau (dic): Diccionario con niveles de feromonas de los vecinos de cada nodo.

        init_point (int): Nodo inicial

        x_best (lst): Ruta con respecto a la cual se quiere mejorar.

        y_best (float): Distancia con respecto a la cual se quiere mejorar

        
    Returns:

        x_best (lst): Ruta con la distancia más corta obtenida

        y_best (float): Distancia asociada a la ruta retornada.
    """

    random.seed(random.randint(0, 1000))
    A = dic_attr
    x = [init_point]
    nodos = list(G.nodes) 
    while len(x) < len(nodos):
        i = x[-1]
        neighbors = set(list(G.neighbors(i))) - set(x)
        if len(neighbors) == 0:
            return(x_best, y_best)
        
        a_s = [A[i][j] for j in neighbors]
        next_ = random.choices(list(neighbors), weights= a_s)
        x = x + next_
    # distancia total del recorrido (se adiciona retorno al origen)
    l = sum([lenghts[i-1][i] for i in range(1, len(x))]) + lenghts[x[-1]][init_point] 
    # aportación a los niveles de feromonas
    for i in range(1, len(x)):
        tau[i-1][i] += 1/l  
        
    tau[x[-1]][init_point] += 1/l
    # aportación a los niveles de feromonas
    # sumar regreso al origen
    x = x + [init_point]
    
    if l < y_best:
        return x, l
    else:
        return x_best, y_best
    

def graph_optim_path(G, best_route, best_dist):

    """Grafica la ruta direccionada de un grafo.

    Args:

        G (graph): Grafo sobre el que se ejecuta la ruta.

        best_route (lst): Trayectoria sobre G.

        best_dist (float): Distancia asociada a best_route

    Returns:

        None

    """

    seed=19511959
    pos = nx.fruchterman_reingold_layout(G, center=(0,0), seed=seed) 
    
    edges = []
    route_edges = [(best_route[n],best_route[n+1]) for n in range(len(best_route)-1)]
    G.add_nodes_from(best_route)
    G.add_edges_from(route_edges)
    edges.append(route_edges)
    
    # graph info
    textstr = '\n'.join((
    f'Distancia: {round(best_dist, 2)}',
    f'Ruta: {best_route}',
    ))
    
    fig, ax = plt.subplots()
    
    g = nx.DiGraph()
    g.add_nodes_from(best_route)
    nx.draw_networkx_nodes(g, ax=ax, pos=pos)
    nx.draw_networkx_labels(g, ax=ax, pos=pos)
    colors = ['b']
    linewidths = [2]
    
    
    
    for ctr, edgelist in enumerate(edges):
                           nx.draw(g,
                           node_color='lightblue', 
                           arrows=True, 
                           pos=pos,
                           edgelist=edgelist,
                           edge_color = colors[ctr], 
                           width=linewidths[ctr])
    # textbox
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.001, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

def ant_colony(G, lenghts, init=0, graph=True, ants=200, max_iter=100, 
               alpha=1, beta=5, rho=.5, verbose=10):

    """ Realiza lai mplementación del algoritmo ant colony para el problema
    TSP. Encontrar la ruta más corta en un viaje redondo.
    
    Args:

        G (graph): Grafo sobre el que se ejecuta el algoritmo.

        lenghts (dic): Diccionario de distancias entre nodos.

        init (int): nodo inicial por el que inician las hormigas.

        graph (bool): Si es True, se grafica la ruta óptima

        ants (int): Número de hormigas por iteracion.

        max_iter (int): Número máximo de iteraciones.

        alpha (float): exponente de feromonas.

        beta (float): exponente prior.

        rho (float): tasa de evaporación.

        verbose (int): Indica cada cuantas iteraciones se quiere imprimir
        el progreso del algoritmo. 
        
    Returns:

        x_best (lst): Ruta con la distancia más corta obtenida

        y_best (float): Distancia asociada a la ruta retornada.
        
    """
    # iniciales
    x_best=[]
    y_best= float('inf')
    
    tau = init_ferom(G)
    eta = init_atrac(G,lenghts)
    for k in range(1, max_iter + 1):
        A = atraccion_nodos(G, tau, eta, alpha=1, beta=5)
        for e in tau:
            for v in tau:
                tau[e][v] = (1-rho)*v
                
        for ant in range(1, ants + 1):
            x_best, y_best = hormiga_recorre(G,lenghts,  A, tau, init, x_best, y_best)
            
        if k%verbose == 0 or k==1:
            print(f'iter: {k} / {max_iter} - dist: {round(y_best, 2)}')

    if k%verbose == 0:
        print('\n')
        print("-"*30)
        print('Resumen:')
        print(f'\tNro. de hormigas: {ants}')  
        print(f'\tIteraciones: {max_iter}')  
        print(f'\tDistancia: {y_best}') 
        print(f'\tNodo inicial: {init}')  
        print(f'\tRuta: {x_best}') 
        print("-"*30)
        
    if graph:
        graph_optim_path(G, x_best, y_best)

    return x_best,y_best
