import numpy as np
import random
from . import aco_tsp

#import sys
#sys.path.append('.') 
#
#import aco_tsp

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

def revisar_simetria(a, rtol=1e-05, atol=1e-08):
    return np.allclose(a, a.T, rtol=rtol, atol=atol)

def revisar_ceros_diagonal(matriz):
    resultado = True
    #matriz = rand_dist_matrix(10, graph=False, scale_factor=100, round_factor=0, 
    #                 seed=1950, int=True)
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