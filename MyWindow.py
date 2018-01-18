#!/usr/bin/python
# coding=utf-8

import sys
from Space import Space
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSlot
from PyQt4.QtCore import QObject, pyqtSignal
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends import qt_compat
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
import numpy as np
from PyQt4.QtGui import QDoubleValidator, QIntValidator

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

# Class to draw the space and the cameras position


class MyCanvasSpace(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.space = args[1]

        self.fig = Figure(figsize=(kwargs.pop('width'),
                                   kwargs.pop('height')), dpi=kwargs.pop('dpi'))
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
        # plt.ion()
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
        # self.axes.clear()

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

# Class to draw the space and the cameras position


class MyCanvasPheromone(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.space = args[1]

        self.fig = Figure(figsize=(kwargs.get('width'),
                                   kwargs.get('height')), dpi=kwargs.get('dpi'))
        self.axes = self.fig.add_subplot(211)
        self.axes2 = self.fig.add_subplot(212)
        #self.fig1, self.axes = plt.subplots()
        #self.axes.set_xlim((0, cols))
        #self.axes.set_ylim((0, 50))

        self.init_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(kwargs.pop('parent'))

        '''FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)'''
        # plt.ion()
        '''timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure())
        timer.start(1000)'''

    def update_figure(self):
        vcols = np.zeros(cols)
        for i in range(cols):
            vcols[i] = i

        self.axes.cla()

        plt.subplot(211)
        plt.cla()
        plt.title('Histogram of pheromones of up wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 50])
        plt.bar(vcols, self.space.wall2,
                facecolor='#9999ff', edgecolor='white')

        self.axes2.cla()

        plt.subplot(212)
        plt.cla()
        plt.title('Histogram of pheromones of down wall')
        plt.xlabel('Point on wall')
        plt.ylabel('Pheromone')
        plt.axis([0, cols, 0, 30])
        plt.bar(vcols, self.space.wall1,
                facecolor='#1c702d', edgecolor='white')

        plt.subplots_adjust(hspace=0.5)
        plt.show()

    def init_figure(self):
        vcols = np.zeros(cols)
        for i in range(cols):
            vcols[i] = i

        self.axes.cla()
        self.axes.set_title('Histograma de feromonas pared superior')
        self.axes.set_xlabel('Punto en la pared')
        self.axes.set_ylabel('Feromona')
        self.axes.axis([0, cols, 0, 50])
        self.axes.bar(vcols, self.space.wall2,
                      facecolor='#9999ff', edgecolor='white')

        self.axes2.cla()
        self.axes2.set_title('Histograma de feromonas pared inferior')
        self.axes2.set_xlabel('Punto en la pared')
        self.axes2.set_ylabel('Feromona')
        self.axes2.axis([0, cols, 0, 50])
        self.axes2.bar(vcols, self.space.wall1,
                       facecolor='#1c702d', edgecolor='white')

        self.fig.subplots_adjust(hspace=0.9)


class MyWindow(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.rowsF = 50.0
        self.colsF = 100.0
        self.focusF = 35.0
        self.numCamerasF = 6
        self.distPowerF = 0.5
        self.pheromPowerF = 0.5
        self.evaporationF = 0.9
        self.numAntsF = 5
        self.numCrazyF = 20.0
        self.minThresholdF = 0.2

        onlyFloat = QDoubleValidator()
        onlyFloat.setNotation(QDoubleValidator.StandardNotation)
        onlyInt = QIntValidator()
        # Default initialization of variables
        self.rows.setText('50')
        self.rows.setValidator(onlyFloat)
        self.rows.textEdited.connect(self.getRows)
        self.cols.setText('100')
        self.cols.setValidator(onlyFloat)
        self.cols.textEdited.connect(self.getCols)
        self.focus.setText('35')
        self.focus.setValidator(onlyFloat)
        self.focus.textEdited.connect(self.getFocus)
        self.numCameras.setText('6')
        self.numCameras.setValidator(onlyInt)
        self.numCameras.textEdited.connect(self.getCameras)
        self.distPower.setText('0.5')
        self.distPower.setValidator(onlyFloat)
        self.distPower.textEdited.connect(self.getDistPower)
        self.pheromPower.setText('0.5')
        self.pheromPower.setValidator(onlyFloat)
        self.pheromPower.textEdited.connect(self.getPheromPower)
        self.evaporation.setText('0.9')
        self.evaporation.setValidator(onlyFloat)
        self.evaporation.textEdited.connect(self.getEvaporation)
        self.numAnts.setText('5')
        self.numAnts.setValidator(onlyInt)
        self.numAnts.textEdited.connect(self.getAnts)
        self.numCrazy.setText('20')
        self.numCrazy.setValidator(onlyFloat)
        self.numCrazy.textEdited.connect(self.getCrazy)
        self.minThreshold.setText('0.2')
        self.minThreshold.setValidator(onlyFloat)
        self.minThreshold.textEdited.connect(self.getThreshold)

        #Initial labels
        self.state.setText('Estado: Configuration')
        self.state.setStyleSheet('QLabel#state {color: gray}')
        self.setGeometry(0, 0, 2000, 1000)
        self.process.setText('')
        self.listProcess.setText('')

        # It connects the button to start the application
        self.start.clicked.connect(self.button_clicked)

        # Window is showed
        self.show()

    def getRows(self):
        self.rowsF = float(self.rows.text())
        print self.rowsF

    def getCols(self):
        self.colsF = float(self.cols.text())
        print self.colsF

    def getFocus(self):
        self.focusF = float(self.focus.text())
        print self.focusF

    def getCameras(self):
        self.numCamerasF = int(self.numCameras.text())
        print self.numCamerasF

    def getDistPower(self):
        self.distPowerF = float(self.distPower.text())
        print self.distPowerF

    def getPheromPower(self):
        self.pheromPowerF = float(self.pheromPower.text())
        print self.pheromPowerF

    def getEvaporation(self):
        self.evaporationF = float(self.evaporation.text())
        print self.evaporationF

    def getAnts(self):
        self.numAntsF = int(self.numAnts.text())
        print self.numAntsF

    def getCrazy(self):
        self.numCrazyF = float(self.numCrazy.text())
        print self.numCrazyF

    def getThreshold(self):
        self.minThresholdF = float(self.minThreshold.text())
        print self.minThresholdF

    # Event of the start button
    def button_clicked(self):
        # Generation of an initial solution
        self.space = Space(self.rowsF, self.colsF, self.focusF, self.numCamerasF, self.distPowerF,
                           self.pheromPowerF, self.evaporationF, self.numAntsF, self.numCrazyF, self.minThresholdF)

        self.process.setText('Process:')
        self.process.setStyleSheet('color: #1F1C1C')

        # It start the space image
        canvasSpace = MyCanvasSpace(
            self.image, self.space, parent=None, width=self.space.rows, height=self.space.cols, dpi=100)
        self.imagesLayout.addWidget(canvasSpace)
        self.image.setFocus()
        self.setCentralWidget(self.image)

        # It start the pheromone image
        canvasPheromone = MyCanvasPheromone(
            self.image, self.space, parent=None, width=30, height=self.space.cols, dpi=100)
        self.imagesLayout.addWidget(canvasPheromone)
        self.pheromones.setFocus()
        self.setCentralWidget(self.pheromones)

        # Evaluation
        self.state.setText('Estado: Processing')
        self.state.setStyleSheet('color: #AC660A')
        try:
            self.space.evaluateSpace()
            self.space.startAlgorithm()
            self.state.setText('Estado: Finish')
            self.state.setStyleSheet('color: #069019')
        except:
            self.state.setText('Estado: Processing error')
            self.state.setStyleSheet('color: #D20101')
