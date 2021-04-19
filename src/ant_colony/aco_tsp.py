
import random
import tsplib95
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint
from itertools import combinations, groupby

def rand_dist_matrix(n_points, graph=True, scale_factor=1, round_factor=4, 
                     seed=1951959, int=False):
    """Crea matriz aleatoria de distancias. Retorna su versión numérica en numpy o
    su versión en grafo con networksx. 

    Args:
        n_points (int): Número de nodos de la matriz de distancias
        graph (bool, optional): Retorna la matriz como un grafo de networkx. Default es True.
        scale_factor (int, optional): Factor de escala de la matriz. Default es 1.
        round_factor (int, optional): Factor de redondeo de la matriz. Default es 4.
        seed (int, optional): Semilla aleatoria. Default es 1951959.
        int (bool, optional): Retorna matriz de enteros. Default es False.

    Returns:
        G (mat or graph): Matrix de distancias o grafo no direccionado
    """
    random.seed(seed)
    import scipy.spatial as spatial
    # Basado en:
    # https://www.w3resource.com/python-exercises/numpy/python-numpy-random-exercise-12.php

    pts = np.random.random((n_points,2))
    x, y = np.atleast_2d(pts[:,0], pts[:,1])
    # Vector de distancias para cada punto 
    dist_mat = np.sqrt((x - x.T)**2 + (y - y.T)**2)
    if int:
        dist_mat = (dist_mat*scale_factor).round(round_factor)
    # Matriz de distancias
    if graph:
        G = nx.from_numpy_matrix(dist_mat) 
    else:
        G = dist_mat
    return G

def create_dic_dist(dist):
    """Crea diccionario de distancias entre nodos a partir de la versión
    numérica de la matriz de distancias.

    Args:
        dist (np.array): Arreglo con la matriz de distancias

    Returns:
        lenghts (dic): Diccionario de distancias de los nodos

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
        G (networkx graph): Grafo con relaciones asociadas entre nodos

    Returns:
        lenghts (dic): Diccionario de distancias de los nodos
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
    de forma deterministica con una semilla (seed).

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        m_plot (str): Tipo de gráfico 
                        - coordinate: Coordenadas X, Y
                        - graph: Grafo
        seed (int, optional):Semilla para determinar las posiciones de los nodos en la 
            visualización. Default es 19511959.
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

def init_ferom(G, init_lev=1.0):
    """Inicialización de diccionario con nivel de feromonas de los nodos.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        init_lev (float, optional): Nivel de inicialización de feromona para todas
            las trayectorias de los nodos. Default es 1.0.

    Returns:
        tau (dic): Diccionario con nivel de feronomas de las trayectorias
    """
    
    nodos = list(G.nodes)
    tau = {}

    for nodo in nodos:
        tau[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            tau[nodo][neighbor] = init_lev

    return tau

def init_atrac(G, lenghts):
    """Inicialización de diccionario con nivel de atracción a priori de los nodos
       utilizando la inversa de las distancias.
    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        lenghts (dic): Diccionario de distancias

    Returns:
        eta (dic): Diccionario con nivel de atracción inicial de las trayectorias
            de los nodos
    """
    nodos = list(G.nodes)
    eta = {}
    
    for nodo in nodos:
        eta[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            eta[nodo][neighbor] = 1/lenghts[nodo][neighbor]
    return eta

def atraccion_nodos(G, tau, eta, alpha=1, beta=5):
    """Calcula el grado de atracción de todos los nodos pertenicientes al grafo G.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        tau (dic): Diccionario con niveles de feromonas de los vecinos de cada nodo
        eta (dic): Diccionario con nivel de atracción inicial de los vecinos de cada nodo
        alpha (int, optional): Factor de influencia de tau. Defaults to 1.
        beta (int, optional): Factor de influencia de eta. Defaults to 5.

    Returns:
        dic_attr (dic): Diccionario con los valores de atracción de los vecinos del nodo j
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
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        lenghts (dic): Diccionario de distancias
        dic_attr (dic): [description]
        tau (dic): Diccionario con niveles de feromonas de los vecinos de cada nodo
        init_point (int): Nodo inicial del recorrido
        x_best (list): Ruta con respecto a la cual se quiere mejorar
        y_best (float): Distancia total del recorrido x_best

    Returns:
        x_best, y_best (list, float): Mejor ruta y distancia encontradas
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
        
    tau[x[-1]][init_point] += 1/l # aportación a los niveles de feromonas

    # sumar regreso al origen
    x = x + [init_point]
    
    if l < y_best:
        return x, l
    else:
        return x_best, y_best  

def ant_colony(G, lenghts, init=0, graph=True, ants=200, max_iter=100, 
               alpha=1, beta=5, rho=.5, verbose=10):
    """Computa el algoritmo ant-colony para encontra la ruta con menor distancia en el problema
    TSP.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        lenghts (dic): Diccionario de distancias
        init (int, optional): Nodo inicial del recorrido. Defaults to 0.
        graph (bool, optional): Grafica la mejor ruta encontrada. Default es True.
        ants (int, optional): Número de hormigas por iteracion. Defaults to 200.
        max_iter (int, optional): Número máximo de iteraciones. Defaults to 100.
        alpha (int, optional): Factor de influencia de tau. Defaults to 1.
        beta (int, optional): Factor de influencia de eta. Defaults to 5.
        rho (float, optional): Tasa de evaporación de las feromonas. Defaults to .5.
        verbose (int, optional): Imprime progreso del algoritmo cada K iteracione. Defaults to 10.

    Returns:
        x_best, y_best (list, float): Mejor ruta y distancia encontradas
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

    return x_best, y_best

def graph_optim_path(G, route, dist):
    """Grafica la ruta direccionada de un grafo asociado a una ruta
    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        route (list): Ruta con la direccion a graficar.
        dist (float): Distancia asociada a la ruta.
    """

    seed=19511959
    pos = nx.fruchterman_reingold_layout(G, center=(0,0), seed=seed) 
    
    edges = []
    route_edges = [(route[n],route[n+1]) for n in range(len(route)-1)]
    G.add_nodes_from(route)
    G.add_edges_from(route_edges)
    edges.append(route_edges)
    
    # graph info
    textstr = '\n'.join((
    f'Distancia: {round(dist, 2)}',
    f'Ruta: {route}',
    ))
    
    fig, ax = plt.subplots()
    
    g = nx.DiGraph()
    g.add_nodes_from(route)
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

