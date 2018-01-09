#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from Space import Space
from PyQt4 import QtCore, QtGui, uic

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
foco = 35
# Espacio máximo que abarca cada cámara
distMax = 2 * foco
# Filas
rows = 50
# Columnas
cols = 2 * rows


class MyWindow(QtGui.QMainWindow, form_class):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.button.clicked.connect(self.button_clicked)
        #self.widget
        # Default initialization of variables
        self.rows.setText('50')
        self.cols.setText('100')
        self.focus.setText('35')
        self.numCameras.setText('6')
        self.distPower.setText('0.5')
        self.pheromPower.setText('0.5')
        self.evaporation.setText('0.9')
        self.numAnts.setText('5')
        self.numCrazy.setText('20')
        self.minThreshold.setText('0.2')
        # Window is showed
        self.show()

    # Event of the start button
    def button_clicked(self):
        # Generation of an initial solution
        space = Space()
        # Evaluation
        space.evaluateSpace()
        space.startAlgorithm()
