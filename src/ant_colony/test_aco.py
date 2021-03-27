# Imports

import numpy as np
import random
from . import aco_tsp

from .aco_tsp import rand_dist_matrix
from .aco_tsp import create_dic_dist
from .aco_tsp import create_dic_dist_from_graph
from .aco_tsp import plot_graph
from .aco_tsp import init_ferom
from .aco_tsp import init_atrac
from .aco_tsp import atraccion_nodos
from .aco_tsp import hormiga_recorre
from .aco_tsp import graph_optim_path
from .aco_tsp import ant_colony

# Auxiliares
def revisar_simetria(a, rtol=1e-05, atol=1e-08):
    return np.allclose(a, a.T, rtol=rtol, atol=atol)

def revisar_ceros_diagonal(matriz):
    resultado = True
    rango_renglones = matriz.shape[1]
    rango_columnas = matriz.shape[0]
    
    for renglon in range(0,rango_renglones,1):
        for columna in range(0,rango_columnas,1):
            if renglon == columna:
                if matriz[renglon][columna] != 0:
                    resultado = False
    return resultado

def test_probar_matriz_cuadrada():
    matriz = rand_dist_matrix(10, graph=False, scale_factor=100, round_factor=0, 
                     seed=1950, int=True)
    assert revisar_simetria(matriz)
    
def test_diagonal_ceros():
    matriz = rand_dist_matrix(10, graph=False, scale_factor=100, round_factor=0, 
                     seed=1950, int=True)
    assert revisar_ceros_diagonal(matriz)
    
def test_creacion_llaves_de_diccionario():
    result=False
    matriz = rand_dist_matrix(10, graph=False, scale_factor=100, round_factor=0, 
                     seed=1950, int=True)
    dictionary = create_dic_dist(matriz)
    if matriz.shape[0]==len(dictionary.keys()):
        result = True
    assert result
    
def test_feromonas_por_nodo():
    result=False
    G = rand_dist_matrix(10, int=True, scale_factor=10, round_factor=4, seed=1950)
    #plot_graph(G, m_plot='graph')
    #plot_graph(G, m_plot='coordinate')
    tau = init_ferom(G)
    if len(G.nodes)==len(tau.keys()):
        result = True
    assert result

def test_atracciones_por_nodo():
    result=True
    G = rand_dist_matrix(10, int=True, scale_factor=10, round_factor=4, seed=1950)
    #plot_graph(G, m_plot='graph')
    #plot_graph(G, m_plot='coordinate')
    tau = init_ferom(G)
    lenghts = create_dic_dist_from_graph(G)
    eta = init_atrac(G, lenghts)
    A = atraccion_nodos(G, tau, eta, alpha=1, beta=5)
    for nodo in range(0,len(A.keys()),1):
        if (len(A[nodo]))!=(len(list(G.nodes))-1):
            result = False
    assert result
    
def test_hormiga_por_todo_nodo():
    result=True
    G = rand_dist_matrix(10, int=True, scale_factor=10, round_factor=4, seed=1950)
    #plot_graph(G, m_plot='graph')
    #plot_graph(G, m_plot='coordinate')
    tau = init_ferom(G)
    lenghts = create_dic_dist_from_graph(G)
    eta = init_atrac(G, lenghts)
    A = atraccion_nodos(G, tau, eta, alpha=1, beta=5)
    route, dist = hormiga_recorre(G,lenghts, A, tau, 1, x_best=[], y_best= float('inf'))
    if (len(route)-1) != len(list(G.nodes)):
        result = False
    assert result
    
def test_distancia_hormiga_dif_de_cero():
    result=True
    G = rand_dist_matrix(10, int=True, scale_factor=10, round_factor=4, seed=1950)
    #plot_graph(G, m_plot='graph')
    #plot_graph(G, m_plot='coordinate')
    tau = init_ferom(G)
    lenghts = create_dic_dist_from_graph(G)
    eta = init_atrac(G, lenghts)
    A = atraccion_nodos(G, tau, eta, alpha=1, beta=5)
    route, dist = hormiga_recorre(G,lenghts, A, tau, 1, x_best=[], y_best= float('inf'))
    if (dist == 0):
        result = False
    assert result
    
def test_ejemplo_completo():
    result = False
    seed = 101934
    n_nodos = 10
    X = rand_dist_matrix(n_nodos, int=True, scale_factor=100, round_factor=4, seed=seed)
    X_num = rand_dist_matrix(n_nodos, graph=False, int=True, scale_factor=10, round_factor=4, seed=seed)
    # diccionario de distancias
    dic_dists = create_dic_dist(X_num)
    # antcolony
    ruta, dist = ant_colony(X, dic_dists, ants=3, max_iter=500, verbose=20)
    if (dist!=0):
        result = True
    return result