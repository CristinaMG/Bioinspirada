#!/usr/bin/python
# -*- coding: utf-8 -*-
from MyWindow import MyWindow
from PyQt4 import QtCore, QtGui, uic
import sys

# Metodo principal
if __name__ == '__main__':

    #Init application
    app = QtGui.QApplication(sys.argv)
    # Generación de una ventana
    win = MyWindow()
    app.exec_()
