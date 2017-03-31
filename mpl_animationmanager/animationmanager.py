#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, Ivan Luchko and Project Contributors 
Licensed under the terms of the MIT License 
https://github.com/luchko/mpl_animationmanager
luchko.ivan@gmail.com

This module contains the definition of the matplotlib animation management tool.
    
    class QDialogAnimManager(QDilaog, Ui_QDialogAnimManager):
    class AnimationManager(object):

Module is compatible with both pyQt4 and pyQt5

"""
from __future__ import division # to handle python2 int division

# define PyQt version
try:
    import PyQt4 as PyQt
    pyQtVersion = "PyQt4"

except ImportError:
    try:
        import PyQt5 as PyQt
        pyQtVersion = "PyQt5"
    except ImportError:
        raise ImportError("neither PyQt4 or PyQt5 is found")

# imports requied PyQt modules
if pyQtVersion == "PyQt4":
    from PyQt4.uic import loadUiType
    from PyQt4.QtCore import pyqtSignal, Qt
    from PyQt4.QtGui import QApplication, QFileDialog, QMessageBox
else:
    from PyQt5.uic import loadUiType
    from PyQt5.QtCore import pyqtSignal, Qt
    from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
    
def getPathString(output):
    '''
    returns a path string of the QFileDialog output
    
    pyQt5 returns a tuple (path, filter) not just a path QString like pyQt4
    
    '''
    return str(output if pyQtVersion == "PyQt4" else output[0])

#import python libs
import os
import sys
import subprocess
from matplotlib import animation
import matplotlib.pyplot as plt

# import UI created in designer
ui_folder = 'mpl_animationmanager/'
Ui_QDialogAnimManager, QDilaog = loadUiType(ui_folder+'QDialogAnimManager.ui')

# classes definition

class QDialogAnimManager(QDilaog, Ui_QDialogAnimManager):
    '''
    PyQt dialog for creation, setting up and exporting matplotlib animations.
    
    Atimation frames change according to fAnim(i, ax, fargs) funcition.
    
    Widget can deal with both 2D and 3D axes. For 3D axes manager can add 
    additional rotation of the view point resulting in both object modification 
    and rotation animation. If fAnim(i, ax, fargs) is not provided 3D object
    anyway can be animated with the rotation animation.   
    '''
    closed = pyqtSignal(object) # used for interaction with parent
    
    def __init__(self, ax, fAnim=None, fargs=None, numFramesModif=None, *args, **kwargs):
        '''
        Parameters
        ----------
        ax : 2D or 3D matplotlib axes object binded to the figure
            provides control over animated figure
        fAnim : function
            fAnim(i, ax, fargs) - modifies the "ax" at each "i" step
        fargs : any
            arguments used by the "fAnim" function during the "ax" modification
        numFramesModif : int
            number of modification frames

        '''          
        super(QDialogAnimManager, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        self.filepath = str(self.lineEdit_name.text())
        self.setup_writers_comboBox()
                
        self.ax = ax
        self.fig = ax.get_figure()
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.fAnim, self.fargs = fAnim, fargs
        self.numFramesModif = numFramesModif
        self.args, self.kwargs = args, kwargs
        
        self.dpi = self.fig.get_dpi()
        self.spinBox_dpi.setValue(self.dpi)
        self.fps = self.spinBox_fps.value()        

        # configure widgets according to type of animation
        if self.fAnim is not None: # if no changes are provided
            self.period_modif = self.spinBox_period_modif.value()
            self.spinBox_period_modif.valueChanged.connect(self.changeTiming_callback)
            self.checkBox_modif.toggled.connect(self.changeTiming_callback)    
        else:
            self.checkBox_modif.setChecked(False)
            self.widget_modif.setVisible(False)

        if self.axesDimensions(ax) == 3:
            self.elevation = self.spinBox_elev.value()
            self.zero_azim = self.spinBox_azim.value()
            self.period_rot = self.spinBox_period_rot.value()
            self.dpf = 360/(self.period_rot*self.fps)  # degrees per frame
 
            self.checkBox_rot.toggled.connect(self.changeTiming_callback)
            self.spinBox_period_rot.valueChanged.connect(self.changeTiming_callback)
            self.spinBox_azim.valueChanged.connect(self.changeAzim_callback)        
            self.spinBox_elev.valueChanged.connect(self.changeElev_callback)
        else:
            self.checkBox_rot.setChecked(False)
            self.widget_rot.setVisible(False)
        
        # some widgets will not be displayed depending on type of animation
        self.adjustSize() 
        
        # calculate the length of animation
        if self.checkBox_modif.isChecked() and self.checkBox_rot.isChecked():
            self.period = self.lcm(self.period_modif, self.period_rot)
        elif self.checkBox_modif.isChecked() and not self.checkBox_rot.isChecked():
            self.period = self.period_modif
        elif not self.checkBox_modif.isChecked() and self.checkBox_rot.isChecked():
            self.period = self.period_rot
            
        self.frames = self.period*self.fps # total number of frames
        
        # create animation
        self.stop_callback()
        self.start_callback()
        
        self.spinBox_dpi.valueChanged.connect(self.change_dpi_callback)        
        self.spinBox_fps.valueChanged.connect(self.changeTiming_callback)
 
        self.btnStart.clicked.connect(self.start_callback)
        self.btnPause.clicked.connect(self.pause_callback)
        self.btnStop.clicked.connect(self.stop_callback)
 
        self.btnBrowse.clicked.connect(self.browse_callback)
        self.btnAsk.clicked.connect(self.info_callback)
        self.btnCancel.clicked.connect(self.cancel_callback)
        self.btnShow.clicked.connect(self.show_anim_callback)
        self.btnExport.clicked.connect(self.export_callback)
               
    def rotate(self, i):
        '''called during creation animation frames'''
        
        if i == 0: # remember starting azimut (used for dynamic speed adjustment)
            self.j_modif_start = self.j_modif
            if self.checkBox_rot.isChecked():
                self.azim_start = self.ax.azim
        
        # modify figure    
        if self.checkBox_modif.isChecked():
            self.j_modif = int(i/(self.period_modif*self.fps)*self.numFramesModif)
            self.j_modif += self.j_modif_start
            self.j_modif %= self.numFramesModif   
            self.fAnim(self.j_modif, self.ax, self.fargs)
        
        # rotate figure
        if self.checkBox_rot.isChecked():
            self.ax.view_init(elev=self.elevation,
                              azim=self.azim_start + i*self.dpf)
        
        self.progressBar.setValue(round((i+1)/self.frames*100))

    def change_dpi_callback(self):        
        self.dpi = self.spinBox_dpi.value()
        self.fig.set_dpi(self.dpi)
        # hack used to update the figure size
        size = self.fig.get_size_inches()
        self.fig.set_size_inches(size, forward=True)

    def changeAzim_callback(self, azimVal):
        self.ax.view_init(elev=self.elevation, 
                          azim=self.ax.azim -self.zero_azim + azimVal)
        self.fig.canvas.draw()        
        self.zero_azim = azimVal
        
    def changeElev_callback(self, elevVal):
        self.ax.view_init(elev=elevVal, azim=self.ax.azim)
        self.fig.canvas.draw()        
        self.elevation = elevVal 
        
    def changeTiming_callback(self):
        '''called when any parameter that influences frames flow is changed'''
        
        self.fps = self.spinBox_fps.value()
        self.period_modif = self.spinBox_period_modif.value()
        self.period_rot = self.spinBox_period_rot.value()
        self.dpf = 360/(self.period_rot*self.fps)  # degrees per frame
        
        if self.checkBox_modif.isChecked() and self.checkBox_rot.isChecked():
            self.period = self.lcm(self.period_modif, self.period_rot)
        elif self.checkBox_modif.isChecked() and not self.checkBox_rot.isChecked():
            self.period = self.period_modif
        elif not self.checkBox_modif.isChecked() and self.checkBox_rot.isChecked():
            self.period = self.period_rot
        else:
            self.pause_callback()
            return
            
        self.frames = self.period*self.fps

        try: # stop previsous animation before deleting creating new one
            self.anim._stop() 
            del self.anim
            self.progressBar.setValue(0)
        except AttributeError:
            pass
        
        # create new animation
        self.anim = animation.FuncAnimation(self.fig, self.rotate, 
                                            frames=self.frames, repeat=True,
                                            interval=1000/self.fps)         

        self.fig.canvas.draw() # redraw to run the animation
         
    def start_callback(self):
        '''start animation'''  
        self.anim.event_source.start()        

    def pause_callback(self):
        '''pause animation'''  
        self.anim.event_source.stop()

    def stop_callback(self):
        '''stop animation'''
        
        self.j_modif = 0
        
        try: # stop previsous animation before deleting creating new one
            self.anim._stop()
            del self.anim
            self.progressBar.setValue(0)
        except AttributeError:
            pass
        
        # change view according to starting deafalut values
        if self.checkBox_rot.isChecked():
            self.ax.view_init(elev = self.elevation, azim = self.zero_azim)
        # create new animation
        self.anim = animation.FuncAnimation(self.fig, self.rotate, 
                                            frames=self.frames, repeat=True,
                                            interval=1000/self.fps)         
        self.fig.canvas.draw() # redraw to run the animation
        self.anim.event_source.stop()
        
    def setup_writers_comboBox(self):
        '''fill the VideoWriter comboBox'''
        
        w_list = animation.writers.list()
        self.comboBox_writers.currentIndexChanged.connect(self.set_extension)          
        for writer in w_list:
            self.comboBox_writers.addItem(writer)
        if "imagemagick" in w_list:
            self.comboBox_writers.setCurrentIndex(w_list.index("imagemagick"))

    def set_extension(self):
        '''set file extension according to chosed VideoWriter'''
        
        # set extension in comboBox_ext
        self.comboBox_ext.clear()
        support_gif = ["imagemagick", "imagemagick_file"]
        if str(self.comboBox_writers.currentText()) in support_gif:
            self.comboBox_ext.addItem("gif")
        else:
            self.comboBox_ext.addItem("mp4")
        # set extension in filepath        
        self.filepath = "{0}.{1}".format(os.path.splitext(self.filepath)[0],
                                         self.comboBox_ext.currentText()) 
        self.lineEdit_name.setText(self.filepath)
    
    def browse_callback(self):
        '''get the file name where animation will be saved'''
        
        output = QFileDialog.getSaveFileName(self, 'Save model animation', '', 
                           filter="Animations (*.mp4 *.gif);;All files (*.*)")
        path = getPathString(output)
        if path != "":
            self.filepath = path
            self.set_extension()
    
    def info_callback(self):
        '''show information anbout animation management tool'''
        
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setTextFormat(Qt.RichText)
        text = '''
<b>Matplotlib animation manager 1.0a1</b>
<br>
Copyright &copy; 2017, Ivan Luchko and Project Contributors 
<br>
Licensed under the terms of the MIT License 
<br><br>
This widget allows to manipulate and export matplotlib animations.
<br><br>
For configuring the writers refer to the 
<a href="http://matplotlib.org/api/animation_api.html">matplotlib website</a>.
<br><br>
For bug reports and feature requests, please go to our 
<a href="https://github.com/luchko/mpl_animationmanager">Github website</a>.
'''
        self.msg.setText(text)
        self.msg.setWindowTitle("Info")
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.exec_()
      
    def show_anim_callback(self):
        '''opens exported animation file with default system tool'''
        
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', self.filepath))
        elif os.name == 'nt':
            os.startfile(self.filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', self.filepath))
   
    def export_callback(self):
        '''export animation to file mp4 or gif file'''
        
        if len(animation.writers.list()) == 0:
            self.msb_noWriters = QMessageBox()
            self.msb_noWriters.setIcon(QMessageBox.Critical)
            self.msb_noWriters.setWindowTitle("Message")    
            self.msb_noWriters.setStandardButtons(QMessageBox.Ok)
            self.msb_noWriters.setText("No  MovieWriter installed")
            self.msb_noWriters.exec_()
            return
        
        # disable btnShow and reset animation
        self.btnShow.setEnabled(False)
        self.stop_callback()
        
        _writerName = self.comboBox_writers.currentText()
        self.filepath = str(self.lineEdit_name.text())      
        self.anim.save(self.filepath, fps=self.fps, dpi=self.dpi,
                       writer=_writerName, *self.args, **self.kwargs)

        self.btnShow.setEnabled(True)
        print(" animation exported into '{}'".format(os.path.basename(self.filepath)))
        
    def cancel_callback(self):
        self.anim._stop()
        del self.anim
        self.closed.emit(True)
        self.reject()
        
    def closeEvent(self, event):
        self.anim._stop()
        del self.anim
        self.closed.emit(True)
        event.accept()
    
    def axesDimensions(self, ax):
        '''returns the dimension of matplotlib axes object'''
        if hasattr(ax, 'get_zlim'): 
            return 3
        else:
            return 2
        
    def lcm(self, x, y):
        '''Returns least common multiple of x and y''' 
        z = x if x > y else y
        while(True):  
            if((z % x == 0) and (z % y == 0)):  
                lcm = z  
                break  
            z += 1  
      
        return lcm 


class AnimationManager(object):    
    '''
    A small class build on top of the 'QDialogAnimManager' and uses 
    the input arguments to initialize the 'QDialogAnimManager' object 
    and run a PyQt application using run() function.
    
    It allows creation, setting up and exporting matplotlib animations.
    
    Atimation frames change according to fAnim(i, ax, fargs) funcition.
    
    Widget can deal with both 2D and 3D axes. For 3D axes manager can add 
    additional rotation of the view point resulting in both object modification 
    and rotation animation. If fAnim(i, ax, fargs) is not provided 3D object
    anyway can be animated with the rotation animation.    
    '''
    app = QApplication([]) # start PyQt application
    
    def __init__(self, ax, fAnim=None, fargs=None, numFramesModif=None, *args, **kwargs):
        '''
        Parameters
        ----------
        ax : 2D or 3D matplotlib axes object binded to the figure
            provides control over animated figure
        fAnim : function
            fAnim(i, ax, fargs) - modifies the "ax" at each "i" step
        fargs : any
            arguments used by the "fAnim" function during the "ax" modification
        numFramesModif : int
            number of modification frames

        '''          
        self.fig = ax.get_figure()
        self.dlg = QDialogAnimManager(ax, fAnim, fargs, numFramesModif, *args, **kwargs)
        
        # bind fig and dlg for close event
        self.dlg.closed.connect(lambda: plt.close(self.fig))
        self.fig.canvas.mpl_connect('close_event', lambda e: self.dlg.reject())
        
    def run(self):
        '''Open the QDialogAnimManager and run the animation'''
        
        self.dlg.show()
        self.fig.show()
        
        return self.app.exec_()
