#!/usr/bin/python
# coding=utf-8
from MyWindow import MyWindow
from PyQt4 import QtCore, QtGui, uic
import sys

# Metodo principal
if __name__ == '__main__':

    #Init application
    app = QtGui.QApplication(sys.argv)

    # New window
    win = MyWindow()
    sys.exit(app.exec_())
