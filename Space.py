# coding=utf-8
import random
import sys
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QObject, pyqtSignal
import Queue
import threading
from time import sleep

# Number of matrix columns
cols = 100

# Colors that cameras can take
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
# fig, ax = plt.subplots()  # note we must use plt.subplots, not plt.subplot

# Main class that creates a set of cameras


class Space(threading.Thread):
    def __init__(self, *args):
        self.confParam = args[0]

        # Define the new signals called 'drawSpace' that has no arguments
        self.drawSpace = args[1]
        self.drawPher = args[2]

        self.q = args[3]
        self.timeout = args[4]
        super(Space, self).__init__()

        # Lists to calculate each wall
        self.wall1 = np.ones(cols)
        self.wall2 = np.ones(cols)

        # Cameras of the space
        self.cameras = []
        # Color of each camera
        self.color = []
        if(args[0] != None):
            for i in range(self.confParam['numCamerasF']):
                self.cameras.append(
                    (random.randint(0, 1) * self.confParam['rowsF'], random.randint(0, cols)))
                self.color.append(random.choice(colors))

        self.fit = 0

        if(args[0] != None):
            self.evaluateSpace()
            print 'space Inicio', self.cameras, self.fit

    def run(self):
        while self.fit > self.confParam['minThresholdF']:
            try:
                function, args, kwargs = self.q.get(timeout=self.timeout)
                function(*args, **kwargs)
            except Queue.Empty:
                self = self.ants()
                print "best 3 ->", self.cameras, self.fit
                #raw_input("Press enter to continue")

        # I show the final solution
        print 'Solution:', self.cameras, 'fit', self.fit

    # Process each camera and add the distance between them, the goal is to minimize it
    def processDistMax(self):
        list1 = []
        list2 = []

        for a in range(self.confParam['numCamerasF']):
            if self.cameras[a][0] == 0:
                list1.append(self.cameras[a][1] *
                             self.confParam['colsF'] / cols)
            else:
                list2.append(self.cameras[a][1] *
                             self.confParam['colsF'] / cols)

        list1.sort()
        list2.sort()

        dist = 0

        for a in range(len(list1) - 1):
            dist += abs(list1[a] - list1[a + 1] - self.confParam['focusF'])
        for a in range(len(list2) - 1):
            dist += abs(list2[a] - list2[a + 1] - self.confParam['focusF'])

        return dist / cols

    # Process each wall to see the distance not covered by the cameras. The objective is to minimize it.
    def processEmptySpace(self):
        list1 = []
        list2 = []

        for a in range(self.confParam['numCamerasF']):
            if self.cameras[a][0] == 0:
                list1.append(self.cameras[a][1] *
                             self.confParam['colsF'] / cols)
            else:
                list2.append(self.cameras[a][1] *
                             self.confParam['colsF'] / cols)

        list1.append(0)
        list1.append(self.confParam['colsF'])
        list2.append(0)
        list2.append(self.confParam['colsF'])
        list1.sort()
        list2.sort()

        vacio = 0
        for a in range(len(list1) - 1):
            if a == 0 or a == (len(list1) - 2):
                dist = self.confParam['focusF']
            else:
                dist = 2 * self.confParam['focusF']

            resul = list1[a + 1] - list1[a]
            if resul > dist:
                vacio += resul - dist

        for a in range(len(list2) - 1):
            if a == 0 or a == (len(list2) - 2):
                dist = self.confParam['focusF']
            else:
                dist = 2 * self.confParam['focusF']

            resul = list2[a + 1] - list2[a]
            if resul > dist:
                vacio += resul - dist

        return vacio

    # Method that evaluates the goodness of a space
    def evaluateSpace(self):
        fit = self.processDistMax() * \
            self.confParam['distPowerF'] + self.processEmptySpace() * \
            (1 - self.confParam['distPowerF'])
        print fit
        self.fit = fit

    # Function that places each camera in a new position based on its probability
    def processCamera(self, cam, crazy):
        focus = int(self.confParam['focusF'] * 0.4)
        if cam[1] - focus < 0:
            low = 0
        else:
            low = cam[1] - focus

        if cam[1] + focus > cols:
            high = cols
        else:
            high = cam[1] + focus

        y = int(random.triangular(low, high))

        # If the ant is not crazy
        if crazy == 0:
            mode = 0
            pos = cam[1]
            if cam[0] == 0.0:
                for i in range(int(low), int(high)):
                    if self.wall1[i] > mode:
                        mode = self.wall1[i]
                        pos = i
            else:
                for i in range(int(low), int(high)):
                    if self.wall2[i] > mode:
                        mode = self.wall2[i]
                        pos = i

            mode = pos * self.confParam['pheromPowerF'] + \
                cam[1] * (1 - self.confParam['pheromPowerF'])
            y = int(random.triangular(low, mode, high))

        x = cam[0]
        if x == 0.0:
            # Cam changes from wall depending on the pheromones
            if random.uniform(0, 1) < 0.05 * self.wall2[y]:
                print 'Camera change de 0 a 50'
                x = self.confParam['rowsF']
        else:
            if random.uniform(0, 1) < 0.05 * self.wall1[y]:
                print 'Camera change de 50 a 0'
                x = 0.0

        return (x, y)

    # Algorithm that copies an object in a new object
    def copySpace(self):
        spaceNew = Space(None, None, None, None, None)
        spaceNew.confParam = self.confParam
        spaceNew.drawSpace = self.drawSpace
        spaceNew.drawPher = self.drawPher
        spaceNew.q = self.q
        spaceNew.out = self.timeout
        spaceNew.wall1 = self.wall1
        spaceNew.wall2 = self.wall2
        spaceNew.cameras = self.cameras
        spaceNew.color = self.color
        spaceNew.fit = self.fit
        return spaceNew

    # Algorithm that creates a space taking into account the data of the previous
    def createSpace(self, crazy):
        print 'New space'
        spaceNew = self.copySpace()
        print 'space 1', spaceNew.cameras, spaceNew.fit
        for i in range(spaceNew.confParam['numCamerasF']):
            # You get the position of each camera to build te path
            # Each camera is placed in the new space, in the new position
            spaceNew.cameras[i] = spaceNew.processCamera(
                spaceNew.cameras[i], crazy)

        # The new space is returned
        return spaceNew

    # Mark the pheromones of the route
    def markPheromones(self, crazy):
        if crazy == 0:
            # print 'markPheromones'
            input = 2
        else:  # if it is a crazy ant its input is bigger
            # print 'markPheromones crazy'
            input = 10

        for i in range(self.confParam['numCamerasF']):
            if self.cameras[i][0] == 0:
                self.wall1[self.cameras[i][1]] += input
            else:
                self.wall2[self.cameras[i][1]] += input

    # Evaporates the trace of pheromones in each iteration
    def evaporatePheromones(self):
        print 'Evaporacion'
        for i in range(cols):
            self.wall1[i] *= (1 - self.confParam['evaporationF'])
            if self.wall1[i] < 0.01:
                self.wall1[i] = 0.0
            self.wall2[i] *= (1 - self.confParam['evaporationF'])
            if self.wall2[i] < 0.01:
                self.wall2[i] = 0.0
        # Emit drawPher signal
        self.drawPher.emit()
        sleep(1)

    def updateSpace(self, spaceNew):
        self.confParam = spaceNew.confParam
        self.drawSpace = spaceNew.drawSpace
        self.drawPher = spaceNew.drawPher
        self.q = spaceNew.q
        self.timeout = spaceNew.out
        self.wall1 = spaceNew.wall1
        self.wall2 = spaceNew.wall2
        self.cameras = spaceNew.cameras
        self.color = spaceNew.color
        self.fit = spaceNew.fit

    # Ants colony algorithm that creates new ants until finding better solutions
    def ants(self):
        print '-------------------- hormigas ------------------ '
        crazy = 0
        # For each ant
        for i in range(self.confParam['numAntsF']):
            # I mark if it is crazy
            if random.uniform(0, 1) < (self.confParam['numCrazyF'] / 100):
                crazy = 1
                print 'crazy'

            # I create a new space based in the previous
            print 'space 0', self.cameras, self.fit
            spaceNew = self.createSpace(crazy)
            print 'spaceNew', spaceNew.cameras
            # I evaluated it
            spaceNew.evaluateSpace()

            # If the new one is better I keep it and frame it with pheromones
            if spaceNew.fit < self.fit:
                self.updateSpace(spaceNew)
                print 'space 2', self.cameras, self.fit
                self.markPheromones(crazy)
                print '<<<<<<<<<<<< Espacio mejor', self.cameras, self.fit
                # Emit drawSpace signal
                self.drawSpace.emit()
                sleep(1)
                # self.drawSpace()  # I only paint the spaces that are best

            crazy = 0

        # When all the ants are finished, I evaporate the pheromones
        self.evaporatePheromones()
        return self
