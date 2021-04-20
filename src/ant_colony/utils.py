import random
import tsplib95
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def read_data(path):
    """Convierte en grafo datos de matrices de distancias en
    formato .txt o .tsp

    Args:
        path (str): Ruta del archivo.

    Returns:
        (graph networkx): Grafo asociado a la matriz de distancias. 
    """
    ext = path[-3:]
    if ext == 'txt':
        data = np.loadtxt(path)
        return nx.from_numpy_matrix(data)
    elif ext == 'tsp':
        data = tsplib95.load(path)
        return data.get_graph() 


def rand_dist_matrix(n_points, graph=True, scale_factor=1, round_factor=4,seed=1951959, int=False):
    """Crea matriz aleatoria de distancias. Retorna su versión numérica en numpy o su versión en grafo con networksx. 
    
    Args:
        n_points (int): Número de nodos de la matriz de distancias.
        graph (bool, optional): Retorna la matriz como un grafo de networkx. Default es True.
        scale_factor (int, optional): Factor de escala de la matriz. Default es 1.
        round_factor (int, optional): Factor de redondeo de la matriz. Default es 4.
        seed (int, optional): Semilla aleatoria. Default es 1951959.
        int (bool, optional): Retorna matriz de enteros. Default es False.

    Returns:
        (mat or graph): Matrix de distancias o grafo no direccionado

    """
    random.seed(seed)
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