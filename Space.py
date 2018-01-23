# coding=utf-8
import random
import sys
import math
import copy
import numpy as np
import matplotlib.pyplot as plt
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import QObject, pyqtSignal

# Number of matrix columns
cols = 100

# Colors that cameras can take
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
fig, ax = plt.subplots()  # note we must use plt.subplots, not plt.subplot

# Main class that creates a set of cameras
#class Space(QObject):
class Space():
    def __init__(self, *args):
        print 'Configuración inicial:', args
        # Space width
        self.width = args[0]
        # Space height
        self.height = args[1]
        # Space that each camera covers
        self.focus = args[2]
        # Number of cameras
        self.numCameras = args[3]
        # Power of distance beetween cameras
        self.distPower = args[4]
        # Power of pheromones
        self.pheromPower = args[5]
        # Evaporation of pheromones
        self.evaporation = args[6]
        # Number of ants
        self.numAnts = args[7]
        # Number of crazy ants
        self.numCrazy = args[8]
        # Minimun accepted solution
        self.minThreshold = args[9]

        # Lists to calculate each wall
        self.wall1 = np.ones(cols)
        self.wall2 = np.ones(cols)

        # Cameras of the space
        self.cameras = []
        # Color of each camera
        self.color = []
        for i in range(self.numCameras):
            self.cameras.append(
                (random.randint(0, 1) * self.width, random.randint(0, cols)))
            self.color.append(random.choice(colors))

        self.fit = 0

        # Define a new signal called 'draw' that has no arguments
        self.draw = args[10]

    # Process each camera and add the distance between them, the goal is to minimize it
    def processDistMax(self):
        list1 = []
        list2 = []

        for a in range(self.numCameras):
            if self.cameras[a][0] == 0:
                list1.append(self.cameras[a][1] * self.height / cols)
            else:
                list2.append(self.cameras[a][1] * self.height / cols)

        list1.sort()
        list2.sort()

        dist = 0
        '''listCam = []
        for a in range(self.numCameras):
            listCam.append(self.cameras[a][1])

        listCam.sort()'''

        for a in range(len(list1) - 1):
            dist += abs(list1[a] - list1[a + 1] - self.focus)
        for a in range(len(list2) - 1):
            dist += abs(list2[a] - list2[a + 1] - self.focus)

        return dist/cols

    # Process each wall to see the distance not covered by the cameras. The objective is to minimize it.
    def processEmptySpace(self):
        list1 = []
        list2 = []

        for a in range(self.numCameras):
            if self.cameras[a][0] == 0:
                list1.append(self.cameras[a][1] * self.height / cols)
            else:
                list2.append(self.cameras[a][1] * self.height / cols)

        list1.append(0)
        list1.append(self.height)
        list2.append(0)
        list2.append(self.height)
        list1.sort()
        list2.sort()

        vacio = 0
        for a in range(len(list1) - 1):
            if a == 0 or a == (len(list1) - 2):
                dist = self.focus
            else:
                dist = 2 * self.focus

            resul = list1[a + 1] - list1[a]
            if resul > dist:
                vacio += resul - dist

        for a in range(len(list2) - 1):
            if a == 0 or a == (len(list2) - 2):
                dist = self.focus
            else:
                dist = 2 * self.focus

            resul = list2[a + 1] - list2[a]
            if resul > dist:
                vacio += resul - dist

        return vacio

    # Method that evaluates the goodness of a space
    def evaluateSpace(self):
        fit = self.processDistMax() * self.distPower + \
            self.processEmptySpace() * (1 - self.distPower)
        print fit
        self.fit = fit

    # Function that places each camera in a new position based on its probability
    def processCamera(self, cam, crazy):
        #large = cam[1] * self.height / cols
        if cam[1] - self.focus < 0:
            low = 0
        else:
            low = cam[1] - self.focus

        if cam[1] + self.focus > cols:
            high = cols
        else:
            high = cam[1] + self.focus

        y = int(random.triangular(low, high))

        # If the ant is not crazy
        if crazy == 0:
            mode = 0
            pos = cam[1]
            if cam[0] == 0.0:
                for i in range(int(low),int(high)):
                    if self.wall1[i] > mode:
                        mode = self.wall1[i]
                        pos = i
            else:
                for i in range(int(low),int(high)):
                    if self.wall2[i] > mode:
                        mode = self.wall2[i]
                        pos = i

            mode = pos*self.pheromPower + cam[1]*(1-self.pheromPower)
            y = int(random.triangular(low, mode, high))

        x = cam[0]
        if x == 0.0:
            # Cam changes from wall depending on the pheromones
            if random.uniform(0, 1) < 0.05 * self.wall2[y]:
                print 'Camera change de 0 a 50'
                x = self.width
        else:
            if random.uniform(0, 1) < 0.05 * self.wall1[y]:
                print 'Camera change de 50 a 0'
                x = 0.0

        return (x, y)

    # Algorithm that creates a space taking into account the data of the previous
    def createSpace(self, crazy):
        print 'New space'
        spaceNew = copy.deepcopy(self)
        for i in range(spaceNew.numCameras):
            # You get the position of each camera to build te path
            # Each camera is placed in the new space, in the new position
            spaceNew.cameras[i] = spaceNew.processCamera(spaceNew.cameras[i], crazy)

        # The new space is returned
        return spaceNew

    # Mark the pheromones of the route
    def markPheromones(self, crazy):
        if crazy == 0:
            #print 'markPheromones'
            input = 1
        else:  # if it is a crazy ant its input is bigger
            #print 'markPheromones crazy'
            input = 5

        for i in range(self.numCameras):
            if self.cameras[i][0] == 0:
                self.wall1[self.cameras[i][1]] += input
            else:
                self.wall2[self.cameras[i][1]] += input
        print 'wall1', self.wall1
        print 'wall2', self.wall2

    # Evaporates the trace of pheromones in each iteration
    def evaporatePheromones(self):
        print 'Evaporacion'
        for i in range(cols):
            self.wall1[i] *= (1-self.evaporation)
            if self.wall1[i] < 0.01:
                self.wall1[i]=0.0
            self.wall2[i] *= (1-self.evaporation)
            if self.wall2[i] < 0.01:
                self.wall2[i]=0.0

    # Ants colony algorithm that creates new ants until finding better solutions
    def ants(self):
        print '-------------------- hormigas ------------------ '
        crazy = 0
        # For each ant
        for i in range(self.numAnts):
            # I mark if it is crazy
            if random.uniform(0, 1) < (self.numCrazy/100):
                crazy = 1
                print 'crazy'

            # I create a new space based in the previous
            spaceNew = self.createSpace(crazy)
            print 'spaceNew',spaceNew.cameras
            # I evaluated it
            spaceNew.evaluateSpace()

            # If the new one is better I keep it and frame it with pheromones
            if spaceNew.fit < self.fit:
                self = spaceNew
                self.markPheromones(crazy)
                print '<<<<<<<<<<<< Espacio mejor',self.cameras, self.fit
                # Emit draw signal
                #self.draw.emit()
                #self.drawSpace()  # I only paint the spaces that are best

            crazy = 0
            #self.drawPheromones()

        # When all the ants are finished, I evaporate the pheromones
        self.evaporatePheromones()
        return self

    # Auxiliary method to update the figure 1
    '''def updateSpace(self):
        global fig, ax
        i = 1
        for cam in range(len(self.cameras)):
            ax.add_artist(plt.Circle((self.cameras[cam][1], self.cameras[cam][0]),
                                     self.focus, color=self.color[cam], fill=self.color[cam], alpha=0.5, clip_on=True))
            ax.annotate("C" + str(cam),
                        [self.cameras[cam][1], self.cameras[cam][0]])
            ax.plot((self.cameras[cam][1]), (self.cameras[cam]
                                             [0]), 'o', color=self.color[cam])
            i += 1

        fig.gca().set_aspect('equal', 'box')
        plt.show()
        plt.pause(5)
        ax.clear()  # which clears axes'''

    # Draw the cameras in a window
    '''def drawSpace(self):
        plt.ion()

        ax.set_xlim((0, cols))
        ax.set_ylim((0, self.width))

        self.updateSpace()'''

    # Draw two graphics of pheromones
    '''def drawPheromones(self):
        vcols = np.zeros(cols)
        for i in range(cols):
            vcols[i] = i

        plt.figure(2)

        plt.subplot(211)
        plt.cla()
        plt.title('Histogram of pheromones of up wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 30])
        plt.bar(vcols, self.wall2, facecolor='#9999ff', edgecolor='white')

        plt.subplot(212)
        plt.cla()
        plt.title('Histogram of pheromones of down wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 30])
        plt.bar(vcols, self.wall1, facecolor='#1c702d', edgecolor='white')

        plt.subplots_adjust(hspace=0.5)
        plt.show()'''

    # if __name__ == '__main__':
    def startAlgorithm(self):
        print self.cameras

        # I'm looking for an acceptable solution with the ants algorithm
        while self.fit > self.minThreshold:
            self = self.ants()
            print "best ->", self.cameras, self.fit
            #raw_input("Press enter to continue")

        # I show the final solution
        print 'Solution:', self.cameras, 'fit', self.fit

        # while not input():
        # plt.pause(1)
