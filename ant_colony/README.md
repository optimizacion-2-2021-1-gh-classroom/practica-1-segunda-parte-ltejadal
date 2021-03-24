En esta carpeta debe ir el codigo de Ant Colony para que pueda ser creado el paquete a través de setup.py


Los archivos en esta carpeta serán los módulos de nuestro paquete y serán los modos en que serán importados. 


Por ejemplo, si tenemos un modulo solver.py, y una funcion  llamada solver se importara del siguiente modo: from "ant_colony.solver import solver" 

A su vez, es importante que las funciones estén documentadas, para que sphinx pueda leer la documentación y crear el sitio web correspondiente. 
