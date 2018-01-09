# coding=utf-8
import random
import sys
import math
import copy
import myWindow
import numpy as np
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui, uic

# Influencia de las feromonas
influenciaFer = 0.5
# Influencia de la distancia respecto al espacio cubierto
pesoFitness = 0.0
# coeficiente de evaporación de las feromonas
evaporacion = 0.9  # Se evapora un 10%
# Umbral que aceptamos para obtener una solución
umbral = 0.2
# Número de hormigas locas
numLocas = 20  # 5% de las hormigas son locas
# Número de hormigas para el algoritmo
numHormigas = 5
# Número de cámaras por cada sala
numCamaras = 6
# Espacio que abarca cada cámara
foco = 35
# Espacio máximo que abarca cada cámara
distMax = 2 * foco
# Filas
rows = 50
# Columnas
cols = 2 * rows

plt.ion()
fig, ax = plt.subplots()  # note we must use plt.subplots, not plt.subplot
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
draw_iterations = 10
draw_index = 10  # So it shows the first iteration

# Clase principal que crea un conjunto de cámaras


class Sala:
    def __init__(self):
        self.pared1 = np.zeros(cols)
        self.pared2 = np.zeros(cols)
        self.camaras = []
        self.color = []
        for i in range(numCamaras):
            self.camaras.append(
                (random.randint(0, 1) * rows, random.randint(0, cols)))
            self.color.append(random.choice(colors))
        self.fit = 0


# Procesa cada camara y suma la distancia entre ellas, el objetivo es minimizarla.
def procesarDistMax(sala):
    dist = 0
    listaCam = []
    for a in range(numCamaras):
        listaCam.append(sala.camaras[a][1])

    listaCam.sort()

    for a in range(numCamaras - 1):
        dist += abs(listaCam[a] - listaCam[a + 1])

    return dist

# Procesa cada pared para ver la distancia sin cubrir por las cámaras. El objetivo es minimizarlo.


def procesarEspacioVacio(sala):
    lista1 = []
    lista2 = []

    for a in range(numCamaras):
        if sala.camaras[a][0] == 0:
            lista1.append(sala.camaras[a][1])
        else:
            lista2.append(sala.camaras[a][1])

    lista1.append(0)
    lista1.append(cols)
    lista2.append(0)
    lista2.append(cols)
    lista1.sort()
    lista2.sort()

    vacio = 0
    for a in range(len(lista1) - 1):
        if a == 0 or a == (len(lista1) - 2):
            dist = foco
        else:
            dist = 2 * foco

        resul = lista1[a + 1] - lista1[a]
        if resul > dist:
            vacio += resul - dist

    for a in range(len(lista2) - 1):
        if a == 0 or a == (len(lista2) - 2):
            dist = foco
        else:
            dist = 2 * foco

        resul = lista2[a + 1] - lista2[a]
        if resul > dist:
            vacio += resul - dist

    return vacio

# Metodo que evalua la bondad de una sala


def evaluarSala(sala):
    fit = procesarDistMax(sala) * pesoFitness + \
        procesarEspacioVacio(sala) * (1 - pesoFitness)
    print 'fit', fit
    sala.fit = fit

# Función que situa cada cámara en una nueva posición a partir de su probabilidad


def procesarCamara(cam, loca):
    if cam[1] - foco < 0:
        low = 0
    else:
        low = cam[1] - foco

    if cam[1] + foco > cols:
        high = cols
    else:
        high = cam[1] + foco

    y = int(random.triangular(low, high))  # podría ser la gaussiana

    # Si la hormiga no es loca
    '''if loca == 0:
		y = int(influenciaFer*y + (1-influenciaFer))'''

    x = cam[0]

    # Un 1% de las veces cambia de pared
    if random.randint(0, 100) == 1:
        if x == 0:
            x == rows
        else:
            x == 0

    return [x, y]

# Algoritmo que crea una sala teniendo en cuenta los datos de la anterior


def crearSala(sala, loca):
    salaNew = copy.copy(sala)
    for i in range(numCamaras):
        # Se obtiene la posición de cada cámara
        [x, y] = procesarCamara(salaNew.camaras[i], loca)
        # Se coloca cada cámara en la sala nueva, en la nueva posición
        salaNew.camaras[i] = [x, y]

    # Se devuelve la nueva sala
    return salaNew


# Funcion que compara la coordenada y dos individuos x e y
'''def compare(x, y):
	if x[1] < y[1] :
		rst = -1
	elif x[1] > y[1] :
		rst = 1
	else :
		rst = 0
	return rst'''


# Marca las feromonas del recorrido
def marcarFeromonas(sala):
    for i in range(numCamaras):
        x = sala.camaras[i][1]
        if sala.camaras[i][0] == 0:
            sala.pared1[sala.camaras[i][1]] += 1
        else:
            sala.pared2[sala.camaras[i][1]] += 1

# Evapora el rastro de feromonas en cada iteracion


def evaporarFeromonas(sala):
    for i in range(cols):
        sala.pared1[i] *= evaporacion
        sala.pared2[i] *= evaporacion

# Algoritmo de colonia de hormigas que va creando nuevas hormigas hasta encontrar soluciones mejores


def hormigas(sala):
    loca = 0
    # Por cada hormiga
    for i in range(numHormigas):
        # marco si es loca
        if random.randint(0, numLocas) == 1:
            loca = 1
        # creo una sala basándome en la anterior
        salaNueva = crearSala(sala, loca)

        loca = 0
        # la evaluo
        evaluarSala(salaNueva)

        # si la nueva es mejor la guardo y marco con feromonas
        if salaNueva.fit < sala.fit:
            sala = salaNueva
            marcarFeromonas(sala)
            print salaNueva.fit
            pintarSala(sala)  # Solo pinto las salas que van a mejor

    # Cuando acaban todas las hormigas evaporo las feromonas
    evaporarFeromonas(sala)

    return sala


# Dibuja las cámaras en una ventana
def pintarSala(sala):
    ax.set_xlim((0, cols))
    ax.set_ylim((0, rows))
    i = 1
    for cam in range(len(sala.camaras)):
        ax.add_artist(plt.Circle((sala.camaras[cam][1], sala.camaras[cam][0]),
                                 foco, color=sala.color[cam], fill=sala.color[cam], alpha=0.5, clip_on=True))
        ax.annotate("C" + str(cam),
                    [sala.camaras[cam][1], sala.camaras[cam][0]])
        ax.plot((sala.camaras[cam][1]), (sala.camaras[cam]
                                         [0]), 'o', color=sala.color[cam])
        i += 1

    fig.gca().set_aspect('equal', 'box')
    plt.show()
    plt.pause(5)
    # while not input():
    # plt.pause(1)
    ax.clear()  # which clears axes


# Metodo principal
if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    MyWindow = MyWindowClass(None)
    MyWindow.show()
    app.exec_()

    # Generación de una solución inicial
    sala = Sala()

    # La evaluo
    evaluarSala(sala)

    # Busco una solución aceptable con el algoritmo de las hormigas
    while sala.fit > umbral:
        sala = hormigas(sala)

    # Muestro la solución final
    print 'Solucion:', sala.camaras, 'fit', sala.fit
    # pintarSala(sala)
    # while not input():
    # plt.pause(1)
