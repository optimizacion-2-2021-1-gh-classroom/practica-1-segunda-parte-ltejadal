import random
import tsplib95
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.spatial import distance_matrix

###
def create_dic_dist(dist):
    """Crea diccionario de distancias entre nodos a partir de la versión
    numérica de la matriz de distancias.

    Args:
        dist (np.array): Arreglo con la matriz de distancias

    Returns:
        (dic): Diccionario de distancias de los nodos
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
        (dic): Diccionario de distancias de los nodos
    """
    nodos = list(G.nodes)
    G_num = nx.to_numpy_matrix(G)
    lenghts = {}
    for node, z in enumerate(G_num):
        lenghts[node] = {}
        for neighbor in nodos:
            lenghts[node][neighbor] = z[0, neighbor]

    return lenghts  

def init_ferom(G, init_lev=1.0):
    """Inicialización de diccionario con nivel de feromonas de los nodos.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        init_lev (float, optional): Nivel de inicialización de feromona para 
        todas las trayectorias de los nodos. Default es 1.0.

    Returns:
        (dic): Diccionario con nivel de feronomas de las trayectorias
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
    """Inicialización de diccionario con nivel de atracción a priori de los 
    nodos utilizando la inversa de las distancias.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        lenghts (dic): Diccionario de distancias

    Returns:
        (dic): Diccionario con nivel de atracción inicial de las trayectorias
        de los nodos
    """
    nodos = list(G.nodes)
    eta = {}
    
    for nodo in nodos:
        eta[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            if neighbor != nodo:
                eta[nodo][neighbor] = 1/lenghts[nodo][neighbor]
    return eta

def atraccion_nodos(G, tau, eta, alpha=1, beta=5):
    """Calcula el grado de atracción de todos los nodos pertenicientes al 
    grafo G.

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        tau (dic): Diccionario con niveles de feromonas de los vecinos de 
        cada nodo
        eta (dic): Diccionario con nivel de atracción inicial de los vecinos 
        de cada nodo
        alpha (int, optional): Factor de influencia de tau. Defaults to 1.
        beta (int, optional): Factor de influencia de eta. Defaults to 5.

    Returns:
        (dic): Diccionario con los valores de atracción de los vecinos del 
        nodo j
    """

    dic_attr = {}

    # componentes del grafo
    nodos = list(G.nodes)
    
    for nodo in nodos:
        dic_attr[nodo] = {}
        neighbors = list(G.neighbors(nodo))
        for neighbor in neighbors:
            if neighbor != nodo:
                attr = tau[nodo][neighbor]**alpha + eta[nodo][neighbor]**beta
                dic_attr[nodo][neighbor] = attr
        
    return dic_attr


###
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

def read_coord_data(path,n_cities,seed):
    """
    Convierte en grafo datos de matrices de coordenadas leídas desde un archivo .tsp.

    Args:
        path (str): Ruta del archivo.
        n_cities (int): número de ciudades a samplear.
        seed (int): seed para el sampleo.

    Returns:
        (graph networkx): Grafo asociado a la matriz de distancias. 
    """
    
    with open(path) as f:
        node_coord_start = None
        dimension = None
        lines = f.readlines()
    
    # Obtain the information about the .tsp
    i = 0
    while not dimension or not node_coord_start:
        line = lines[i]
        if line.startswith('DIMENSION :'):
            dimension = int(line.split()[-1])
        if line.startswith('NODE_COORD_SECTION'):
            node_coord_start = i
        i = i+1
    
    cities_df = pd.read_csv(
            path,
            skiprows=node_coord_start + 1,
            sep=' ',
            names=['city', 'lat', 'lon'],
            dtype={'city': str, 'lat': np.float64, 'lon': np.float64},
            header=None,
            nrows=dimension
        )
    # Clean x, y coordinates
    cities_df['lat'] = cities_df['lat'].div(1000)
    cities_df['lon'] = cities_df['lon'].div(1000)

    print('Problem with {} cities read.'.format(dimension))
    
    sample_df = cities_df.sample(n_cities, random_state=seed)
    array_coord = sample_df[['lat','lon']].to_numpy()
    
    d_mat = distance_matrix(array_coord, array_coord)
    G = nx.from_numpy_matrix(d_mat)
    
    return G

def rand_dist_matrix(n_points, graph=True, scale_factor=1, round_factor=4,seed=1951959, int=False):
    """Crea matriz aleatoria de distancias. Retorna su versión numérica en 
    numpy o su versión en grafo con networksx. 
    
    Args:
        n_points (int): Número de nodos de la matriz de distancias.
        graph (bool, optional): Retorna la matriz como un grafo de networkx. 
        Default es True.
        scale_factor (int, optional): Factor de escala de la matriz. Default 
        es 1.
        round_factor (int, optional): Factor de redondeo de la matriz. Default
         es 4.
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
    """Grafica red en su versión de coordenadas o de grafo. Fija las 
    posiciones
    de forma deterministica con una semilla (seed).

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        m_plot (str): Tipo de gráfico 
                        - coordinate: Coordenadas X, Y
                        - graph: Grafo
        seed (int, optional):Semilla para determinar las posiciones de los 
        nodos en la 
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

def graph_optim_path(G, route, dist, plt_size=(15, 6)):
    """Grafica la ruta direccionada de un grafo asociado a una ruta

    Args:
        G (networkx graph): Grafo con relaciones asociadas entre nodos
        route (list): Ruta con la direccion a graficar.
        dist (float): Distancia asociada a la ruta.
        plt_size (tpl): Tamaño de la gráfica en matplotlib.

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
    
    fig, ax = plt.subplots(figsize=plt_size)
    
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
    # origin
    nx.draw_networkx(g.subgraph(route[0]), ax=ax, pos=pos, node_color='red')
    # textbox
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.001, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)