# coding=utf-8
import random
import sys
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui, uic

# Influencia de las pheromonas
influenciapher = 0.5
# Influencia de la distancia respecto al espacio cubierto
pesoFitness = 0.0
# coeficiente de evaporación de las pheromonas
evaporacion = 0.9  # Se evapora un 10%
# Umbral que aceptamos para obtener una solución
umbral = 0.2
# Número de ants crazys
numcrazys = 20  # 5% de las ants son crazys
# Número de ants para el algoritmo
numAnts = 5
# Número de cámaras por cada space
numCameras = 6
# Espacio que abarca cada cámara
focus = 35
# Espacio máximo que abarca cada cámara
distMax = 2 * focus
# Filas
rows = 50
# Columnas
cols = 2 * rows

plt.ion()
fig, ax = plt.subplots()  # note we must use plt.subplots, not plt.subplot
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
draw_iterations = 10
draw_index = 10  # So it shows the first iteration

# Main class that creates a set of cameras
class Space:
    def __init__(self):
        self.wall1 = np.zeros(cols)
        self.wall2 = np.zeros(cols)
        self.cameras = []
        self.color = []
        for i in range(numCameras):
            self.cameras.append(
                (random.randint(0, 1) * rows, random.randint(0, cols)))
            self.color.append(random.choice(colors))
        self.fit = 0


    # Process each camera and add the distance between them, the goal is to minimize it
    def processDistMax(self):
        dist = 0
        listCam = []
        for a in range(numCameras):
            listCam.append(self.cameras[a][1])

        listCam.sort()

        for a in range(numCameras - 1):
            dist += abs(listCam[a] - listCam[a + 1])

        return dist

    #Process each wall to see the distance not covered by the cameras. The objective is to minimize it.
    def processEmptySpace(self):
        list1 = []
        list2 = []

        for a in range(numCameras):
            if self.cameras[a][0] == 0:
                list1.append(self.cameras[a][1])
            else:
                list2.append(self.cameras[a][1])

        list1.append(0)
        list1.append(cols)
        list2.append(0)
        list2.append(cols)
        list1.sort()
        list2.sort()

        vacio = 0
        for a in range(len(list1) - 1):
            if a == 0 or a == (len(list1) - 2):
                dist = focus
            else:
                dist = 2 * focus

            resul = list1[a + 1] - list1[a]
            if resul > dist:
                vacio += resul - dist

        for a in range(len(list2) - 1):
            if a == 0 or a == (len(list2) - 2):
                dist = focus
            else:
                dist = 2 * focus

            resul = list2[a + 1] - list2[a]
            if resul > dist:
                vacio += resul - dist

        return vacio

    # Method that evaluates the goodness of a space
    def evaluateSpace(self):
        fit = self.processDistMax() * pesoFitness + \
            self.processEmptySpace() * (1 - pesoFitness)
        print 'fit', fit
        self.fit = fit

    # Function that places each camera in a new position based on its probability
    def processCamera(self, cam, crazy):
        if cam[1] - focus < 0:
            low = 0
        else:
            low = cam[1] - focus

        if cam[1] + focus > cols:
            high = cols
        else:
            high = cam[1] + focus

        y = int(random.triangular(low, high))  # it colud be the gaussian

        # If the ant is not crazy
        '''if crazy == 0:
    		y = int(influenciapher*y + (1-influenciapher))'''

        x = cam[0]

        # 1% of the time it changes from wall
        if random.randint(0, 100) == 1:
            if x == 0:
                x == rows
            else:
                x == 0

        return [x, y]

    # Algorithm that creates a space taking into account the data of the previous
    def createSpace(self, crazy):
        spaceNew = copy.copy(self)
        for i in range(numCameras):
            # You get the position of each camera
            [x, y] = self.processCamera(spaceNew.cameras[i], crazy)
            # Each camera is placed in the new space, in the new position
            spaceNew.cameras[i] = [x, y]

        # The new space is returned
        return spaceNew


    # Mark the pheromones of the route
    def markPheromones(self):
        for i in range(numCameras):
            x = self.cameras[i][1]
            if self.cameras[i][0] == 0:
                self.wall1[self.cameras[i][1]] += 1
            else:
                self.wall2[self.cameras[i][1]] += 1

    # Evaporates the trace of pheromones in each iteration
    def evaporatePheromones(self):
        for i in range(cols):
            self.wall1[i] *= evaporacion
            self.wall2[i] *= evaporacion

    # Ants colony algorithm that creates new ants until finding better solutions
    def ants(self):
        crazy = 0
        # For each ant
        for i in range(numAnts):
            # I mark if it is crazy
            if random.randint(0, numcrazys) == 1:
                crazy = 1
            # I create a new space based in the previous
            spaceNew = self.createSpace(crazy)

            crazy = 0
            # I evaluated it
            spaceNew.evaluateSpace()

            # If the new one is better I keep it and frame it with pheromones
            if spaceNew.fit < self.fit:
                self = spaceNew
                self.markPheromones()
                print spaceNew.fit
                self.drawSpace()  # I only paint the spaces that are best

        # When all the ants are finished, I evaporate the pheromones
        self.evaporatePheromones()

        return self


    # Draw the cameras in a window
    def drawSpace(self):
        ax.set_xlim((0, cols))
        ax.set_ylim((0, rows))
        i = 1
        for cam in range(len(self.cameras)):
            ax.add_artist(plt.Circle((self.cameras[cam][1], self.cameras[cam][0]),
                                     focus, color=self.color[cam], fill=self.color[cam], alpha=0.5, clip_on=True))
            ax.annotate("C" + str(cam),
                        [self.cameras[cam][1], self.cameras[cam][0]])
            ax.plot((self.cameras[cam][1]), (self.cameras[cam]
                                             [0]), 'o', color=self.color[cam])
            i += 1

        fig.gca().set_aspect('equal', 'box')
        plt.show()
        plt.pause(5)
        # while not input():
        # plt.pause(1)
        ax.clear()  # which clears axes

    #if __name__ == '__main__':
    def startAlgorithm(self):

        # I'm looking for an acceptable solution with the algorithm of the ants
        while self.fit > umbral:
            self = self.ants()

        # I show the final solution
        print 'Solution:', self.cameras, 'fit', self.fit
        # drawSpace(space)
        # while not input():
        # plt.pause(1)
