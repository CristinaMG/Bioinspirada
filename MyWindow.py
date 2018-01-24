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
from time import sleep
import Queue

# Cargar nuestro archivo .ui
form_class = uic.loadUiType("camerasWindow.ui")[0]

# Columnas
cols = 100

# Class to draw the space and the cameras position
class MyCanvasSpace(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.space = args[1]
        self.fig = Figure(figsize=(kwargs.get('width'),
                                   kwargs.get('height')), dpi=kwargs.pop('dpi'))
        self.axes = self.fig.add_subplot(111)
        #self.fig1, self.axes = plt.subplots()
        self.axes.set_xlim((0, kwargs.get('height')))
        self.axes.set_ylim((0, kwargs.get('width')))

        self.focus = kwargs.get('focus')
        FigureCanvas.__init__(self, self.fig)
        self.init_figure()

        self.setParent(kwargs.pop('parent'))

    def init_figure(self):
        plt.ion()
        for cam in range(len(self.space.cameras)):
            self.axes.add_artist(plt.Circle((self.space.cameras[cam][1] * self.space.confParam['colsF'] / cols, self.space.cameras[cam][0]),
                                            self.focus, color=self.space.color[cam], fill=self.space.color[cam], alpha=0.5, clip_on=True))
            self.axes.annotate("C" + str(cam),
                               [self.space.cameras[cam][1]* self.space.confParam['colsF'] / cols, self.space.cameras[cam][0]])
            self.axes.plot(
                (self.space.cameras[cam][1]* self.space.confParam['colsF'] / cols), (self.space.cameras[cam][0]), 'o', color=self.space.color[cam])
        self.fig.gca().set_aspect('equal', 'box')
        self.axes.text(1.1, 1.2,'fit = '+ str(self.space.fit) , horizontalalignment='right',verticalalignment='top',transform=self.axes.transAxes)

# Class to draw the space and the cameras position
class MyCanvasPheromone(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.space = args[1]
        self.cols = kwargs.get('height')
        self.fig = Figure(figsize=(kwargs.get('width'),
                                   kwargs.get('height')), dpi=kwargs.get('dpi'))
        self.axes = self.fig.add_subplot(211)
        self.axes2 = self.fig.add_subplot(212)

        self.init_figure()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(kwargs.pop('parent'))

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
                      facecolor='#0011ff', edgecolor='white')

        self.axes2.cla()
        self.axes2.set_title('Histograma de feromonas pared inferior')
        self.axes2.set_xlabel('Punto en la pared')
        self.axes2.set_ylabel('Feromona')
        self.axes2.axis([0, cols, 0, 50])
        self.axes2.bar(vcols, self.space.wall1,
                       facecolor='#008912', edgecolor='white')

        self.fig.subplots_adjust(hspace=0.9)

# Class to paint the main window
class MyWindow(QtGui.QMainWindow, form_class, QObject):

    drawSpace = pyqtSignal()
    drawPher = pyqtSignal()
    drawProcess = pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.confParam = {'rowsF': 50.0, 'colsF': 100.0, 'focusF': 35.0, 'numCamerasF': 6, 'distPowerF': 0.4,
                          'pheromPowerF': 0.5, 'evaporationF': 0.2, 'numAntsF': 5, 'numCrazyF': 5.0, 'minThresholdF': 1.06}

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
        self.distPower.setText('0.4')
        self.distPower.setValidator(onlyFloat)
        self.distPower.textEdited.connect(self.getDistPower)
        self.pheromPower.setText('0.5')
        self.pheromPower.setValidator(onlyFloat)
        self.pheromPower.textEdited.connect(self.getPheromPower)
        self.evaporation.setText('0.2')
        self.evaporation.setValidator(onlyFloat)
        self.evaporation.textEdited.connect(self.getEvaporation)
        self.numAnts.setText('5')
        self.numAnts.setValidator(onlyInt)
        self.numAnts.textEdited.connect(self.getAnts)
        self.numCrazy.setText('5')
        self.numCrazy.setValidator(onlyFloat)
        self.numCrazy.textEdited.connect(self.getCrazy)
        self.minThreshold.setText('1.06')
        self.minThreshold.setValidator(onlyFloat)
        self.minThreshold.textEdited.connect(self.getThreshold)

        # Initial labels
        self.state.setText('Estado: Configuration')
        self.state.setStyleSheet('QLabel#state {color: gray}')
        self.setGeometry(0, 0, 2000, 1000)
        self.process.setText('')
        self.listProcess.setText('')

        # It connects the button to start the application
        self.start.clicked.connect(self.button_clicked)

        # Window is showed
        self.show()

    # Methods to get the configuration parameters
    def getRows(self):
        self.confParam['rowsF'] = float(self.rows.text())

    def getCols(self):
        self.confParam['colsF'] = float(self.cols.text())

    def getFocus(self):
        self.confParam['focusF'] = float(self.focus.text())

    def getCameras(self):
        self.confParam['numCamerasF'] = int(self.numCameras.text())

    def getDistPower(self):
        self.confParam['distPowerF'] = float(self.distPower.text())

    def getPheromPower(self):
        self.confParam['pheromPowerF'] = float(self.pheromPower.text())

    def getEvaporation(self):
        self.confParam['evaporationF'] = float(self.evaporation.text())

    def getAnts(self):
        self.confParam['numAntsF'] = int(self.numAnts.text())

    def getCrazy(self):
        self.confParam['numCrazyF'] = float(self.numCrazy.text())

    def getThreshold(self):
        self.confParam['minThresholdF'] = float(self.minThreshold.text())

    # Handle to update the draw space
    def handle_drawSpace(self):
        self.canvasSpace.deleteLater()
        self.canvasSpace = MyCanvasSpace(
            self.image, self.space, parent=None, width=self.confParam['rowsF'], height=self.confParam['colsF'], dpi=100, focus=self.confParam['focusF'])
        self.imagesLayout.addWidget(self.canvasSpace)
        sleep(0.5)

    # Handle to update the draw pheromones
    def handle_drawPher(self):
        self.canvasPheromone.deleteLater()
        self.canvasPheromone = MyCanvasPheromone(
            self.pheromones, self.space, parent=None, width=30, height=self.confParam['colsF'], dpi=100)
        self.pheromLayout.addWidget(self.canvasPheromone)
        sleep(0.5)

    # Handle to update the draw process
    def handle_drawProcess(self):
        for a in range(self.confParam['numAntsF']):
            self.listProcess.setText(self.listProcess.text()+'H'+str(a)+'\n')

    def startProcess(self):
        self.drawProcess.connect(self.handle_drawProcess)
        for a in range(self.confParam['numAntsF']):
            self.listProcess.setText(self.listProcess.text()+'H'+str(a)+'\n')

    # Event of the start button
    def button_clicked(self):
        # Generation of an initial solution
        try:
            # self.space.evaluateSpace()
            # self.space.startAlgorithm()
            q = Queue.Queue()
            loop_time = 1.0 / 60
            self.space = Space(self.confParam, self.drawSpace,
                               self.drawPher, q, loop_time)
            self.space.setDaemon(True)
            self.space.start()
            self.state.setText('Estado: Processing')
            self.state.setStyleSheet('color: #AC660A')
            #self.state.setText('Estado: Finish')
            # self.state.setStyleSheet('color: #069019')
        except Exception as inst:
            print type(inst)     # the exception instance
            print inst.args      # arguments stored in .args
            print inst
            self.state.setText('Estado: Processing error')
            self.state.setStyleSheet('color: #D20101')

        self.process.setText('Process:')
        self.process.setStyleSheet('color: #1F1C1C')

        self.startProcess()

        # It start the space image
        self.canvasSpace = MyCanvasSpace(
            self.image, self.space, parent=None, width=self.confParam['rowsF'], height=self.confParam['colsF'], dpi=100, focus=self.confParam['focusF'])
        self.imagesLayout.addWidget(self.canvasSpace)
        self.image.setFocus()
        self.setCentralWidget(self.image)

        # It start the pheromone image
        self.canvasPheromone = MyCanvasPheromone(
            self.pheromones, self.space, parent=None, width=30, height=self.confParam['colsF'], dpi=100)
        self.pheromLayout.addWidget(self.canvasPheromone)
        self.pheromones.setFocus()
        self.setCentralWidget(self.pheromones)

        # Connect signals to draw
        self.drawSpace.connect(self.handle_drawSpace)
        self.drawPher.connect(self.handle_drawPher)
