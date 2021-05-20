# Requerimientos para programación

el algoritmo recibirá una matriz de distancias entre los puntos.

será una matriz con puros ceros en la diagonaly puede ser consideradad como la matriz de costos
se utiliza una matriz de "feromonas" para representar la cantidad de veces que se ha pasado en cada unión

Las feromonas pueden ser relacionadas con la "calidad" del camino entre puntos

En una gráfica, se utiliza un modelo matemático para representar el número de "Feromonas" que tendrá cada camino entre puntos. El modelo es el siguiente:

$$\Delta \tau ^{k} _{i,j} =\left\lbrace\begin{array}{c} \frac{1}{L_k}~si~la~hormiga~k^{esima}~recorre~ese~camino  \\ 0~e.o.c\end{array}\right.$$
Entonces, para calcular $\tau ^{k} _{i,j}$ "sin vaporización", se debe seguir la siguiente función:

$$\tau ^{k} _{i,j} = \sum^m_{k=1} \Delta \tau ^{k} _{i,j}$$

En caso de existir "vaporización", sería de la siguiente forma:

$$\tau ^{k} _{i,j} = [(1-\rho) * \tau _{i,j}] + \sum^m_{k=1} \Delta \tau ^{k} _{i,j}$$
donde $\rho$ es la tasa de evaporización.
De igual forma, se debe calcular la probabilidad de cada camino como:
$$P_{i,j} = \frac{(\tau _{i,j})^\alpha (\eta_{i,j})^\beta}{\sum ((\tau _{i,j})^\alpha (\eta_{i,j})^\beta)}$$
donde $\eta _{i,j} = \frac {1}{L_{i,j}}$

una vez que se tienen las probabilidades de seguir cada nodo, se usa un algoritmo llamado Roulette wheel

Cómo se implementa en el TSP?
