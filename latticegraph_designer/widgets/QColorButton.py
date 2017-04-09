#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 23:51:08 2017

@author: ivan

This module contains the defitinion of QColorButton
for color selection and test example.

Module is compatible with both pyQt4 and pyQt5

source: https://mfitzp.io/article/qcolorbutton-a-color-selector-tool-for-pyqt/

"""
# define pyQt version
try:
    import PyQt4 as PyQt
    pyQtVersion = "PyQt4"

except ImportError:
    try:
        import PyQt5 as PyQt
        pyQtVersion = "PyQt5"
    except ImportError:
        raise ImportError("neither PyQt4 or PyQt5 is found")

if pyQtVersion == "PyQt4":
    from PyQt4.QtCore import pyqtSignal
    from PyQt4.QtGui import QColorDialog, QPushButton, QPalette, QColor
else:
    from PyQt5.QtCore import pyqtSignal
    from PyQt5.QtGui import QColor, QPalette
    from PyQt5.QtWidgets import QColorDialog, QPushButton
        
# classes definition

class QColorButton(QPushButton):
    '''
    Custom Qt Widget to show a chosen color.
    Left-clicking the button shows the color-chooser, while
    
    source: https://mfitzp.io/article/qcolorbutton-a-color-selector-tool-for-pyqt/
    
    '''
    colorChanged = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(QColorButton, self).__init__(*args, **kwargs)

        self._color = None
        self.setMaximumWidth(32)
        self.setMaximumHeight(20)
        self.pressed.connect(self.onColorPicker)
        self.defaultColor = self.palette().color(QPalette.Background).name()
        self.set_color(self.defaultColor)

    def set_color(self, color):
        if color != self._color:
            self._color = color
            self.colorChanged.emit()

        if self._color:
            self.setStyleSheet("background-color: %s;" % self._color)
        else:
            self.setStyleSheet("")

    def get_color(self):
        return str(self._color)

    def onColorPicker(self):
        '''Show color-picker dialog to select color.'''
        
        dlg = QColorDialog(self)
        dlg.setStyleSheet("background-color: %s" % self.defaultColor)
        
        if self._color:
            dlg.setCurrentColor(QColor(self._color))
            
        if dlg.exec_():
            self.set_color(dlg.currentColor().name())
            

##############################################################################
    
if __name__ == '__main__':

    # test classes   

    def run_test():
    
        print("\n {} is imported".format(pyQtVersion))
        # imports requied PyQt modules
        if pyQtVersion == "PyQt4":
            from PyQt4.QtGui import QApplication, QSizePolicy
        else:
            from PyQt5.QtWidgets import QApplication, QSizePolicy
        
        import sys
            
        app = QApplication([])
                
        print("\n# run {} test\n".format(QColorButton))
    
        myBtn = QColorButton()
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        myBtn.setSizePolicy(sizePolicy)
        myBtn.setMaximumWidth(10000)     
        myBtn.setMaximumHeight(10000)
        myBtn.resize(100,100)
        myBtn.set_color(u'#00aaff')    
        myBtn.show()
    
        sys.exit(app.exec_())

    
    run_test()
