#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from Space import Space
from PyQt4 import QtCore, QtGui, uic
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import qt_compat
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import numpy as np

# Cargar nuestro archivo .ui
form_class = uic.loadUiType("camerasWindow.ui")[0]

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
# Número de cámaras por cada space
numCamaras = 6
# Espacio que abarca cada cámara
focus = 35
# Espacio máximo que abarca cada cámara
distMax = 2 * focus
# Filas
rows = 50
# Columnas
cols = 2 * rows

#Class to draw the space and the cameras position
class MyCanvasSpace(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.space = args[1]

        self.fig = Figure(figsize=(kwargs.pop('width'), kwargs.pop('height')), dpi=kwargs.pop('dpi'))
        self.axes = self.fig.add_subplot(111)
        #self.fig1, self.axes = plt.subplots()
        self.axes.set_xlim((0, cols))
        self.axes.set_ylim((0, rows))

        self.init_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(kwargs.pop('parent'))

        '''FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)'''
        #plt.ion()
        '''timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure())
        timer.start(1000)'''

    def update_figure(self):
        #global fig, ax
        self.axes.cla()
        i = 1
        for cam in range(len(self.space.cameras)):
            self.axes.add_artist(plt.Circle((self.space.cameras[cam][1], self.space.cameras[cam][0]),
                                     focus, color=self.space.color[cam], fill=self.space.color[cam], alpha=0.5, clip_on=True))
            self.axes.annotate("C" + str(cam),
                        [self.space.cameras[cam][1], self.space.cameras[cam][0]])
            self.axes.plot((self.space.cameras[cam][1]), (self.space.cameras[cam]
                                             [0]), 'o', color=self.space.color[cam])
            i += 1

        self.fig.gca().set_aspect('equal', 'box')
        plt.show()
        plt.pause(5)
        #self.axes.clear()

    def init_figure(self):
        plt.ion()
        i = 1
        for cam in range(len(self.space.cameras)):
            self.axes.add_artist(plt.Circle((self.space.cameras[cam][1], self.space.cameras[cam][0]),
                                     focus, color=self.space.color[cam], fill=self.space.color[cam], alpha=0.5, clip_on=True))
            self.axes.annotate("C" + str(cam),
                        [self.space.cameras[cam][1], self.space.cameras[cam][0]])
            self.axes.plot((self.space.cameras[cam][1]), (self.space.cameras[cam]
                                             [0]), 'o', color=self.space.color[cam])
            i += 1
        self.fig.gca().set_aspect('equal', 'box')

#Class to draw the space and the cameras position
class MyCanvasPheromone(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.space = args[1]

        self.fig = Figure(figsize=(kwargs.get('width'), kwargs.get('height')), dpi=kwargs.get('dpi'))
        self.axes = self.fig.add_subplot(211)
        self.axes = self.fig.add_subplot(212)
        #self.fig1, self.axes = plt.subplots()
        self.axes.set_xlim((0, cols))
        self.axes.set_ylim((0, 50))

        self.init_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(kwargs.pop('parent'))

        '''FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)'''
        #plt.ion()
        '''timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure())
        timer.start(1000)'''

    def update_figure(self):
        vcols = np.zeros(cols)
        for i in range(cols):
            vcols[i] = i

        #plt.figure(111)

        plt.subplot(211)
        plt.cla();
        plt.title('Histogram of pheromones of up wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 50])
        plt.bar(vcols, self.space.wall2, facecolor='#9999ff', edgecolor='white')

        plt.subplot(212)
        plt.cla();
        plt.title('Histogram of pheromones of down wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 30])
        plt.bar(vcols, self.space.wall1, facecolor='#1c702d', edgecolor='white')

        plt.subplots_adjust(hspace=0.5)
        plt.show()

    def init_figure(self):
        vcols = np.zeros(cols)
        for i in range(cols):
            vcols[i] = i

        #plt.figure(112)

        plt.subplot(211)
        plt.cla();
        plt.title('Histogram of pheromones of up wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 50])
        plt.bar(vcols, self.space.wall2, facecolor='#9999ff', edgecolor='white')

        plt.subplot(212)
        plt.cla();
        plt.title('Histogram of pheromones of down wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 30])
        plt.bar(vcols, self.space.wall1, facecolor='#1c702d', edgecolor='white')

        plt.subplots_adjust(hspace=0.5)


class MyWindow(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Generation of an initial solution
        self.space = Space()

        #It connects the button to start the application
        self.button.clicked.connect(self.button_clicked)
        self.configuration.addWidget(self.button)

        # Default initialization of variables
        self.rows.setText('50')
        self.cols.setText('100')
        self.focus.setText('35')
        self.numCameras.setText('6')
        #self.connect(self.numCameras, SIGNAL("textEdited()"), self.borrar)
        self.distPower.setText('0.5')
        self.pheromPower.setText('0.5')
        self.evaporation.setText('0.9')
        self.numAnts.setText('5')
        self.numCrazy.setText('20')
        self.minThreshold.setText('0.2')

        #It start the space image
        canvasSpace = MyCanvasSpace(self.image, self.space,parent=None, width=self.space.rows, height=self.space.cols, dpi=100)
        self.imagesLayout.addWidget(canvasSpace)
        self.image.setFocus()
        self.setCentralWidget(self.image)

        #It start the pheromone image
        canvasPheromone = MyCanvasPheromone(self.image, self.space,parent=None, width=30, height=self.space.cols, dpi=100)
        self.imagesLayout.addWidget(canvasPheromone)
        self.pheromones.setFocus()
        self.setCentralWidget(self.pheromones)

        # Window is showed
        self.show()



    # Event of the start button
    def button_clicked(self):
        # Evaluation
        self.space.evaluateSpace()
        self.space.startAlgorithm()

    #def borrar(self):
        #self.qle_texto.setText("hola")
