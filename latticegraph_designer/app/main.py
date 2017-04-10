#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2017, Ivan Luchko and Project Contributors 
Licensed under the terms of the MIT License
https://github.com/luchko/latticegraph_designer

This module contains the definition of the app MainWindow.
    
    class MainWindow(QMainWindow, Ui_MainWindow):
    def run():

Module is compatible with both pyQt4 and pyQt5
        
"""

from __future__ import division

import matplotlib

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

# imports requied PyQt modules         
if pyQtVersion == "PyQt4":
    # Make sure that we are using QT5
    matplotlib.use('Qt4Agg')
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    # impoort pyQt modules
    from PyQt4.uic import loadUiType
    from PyQt4.QtCore import Qt, pyqtSignal
    from PyQt4.QtGui import (QMessageBox, QFileDialog, QListWidgetItem,
                             QPushButton, QHBoxLayout, QVBoxLayout)
else:
    # Make sure that we are using QT5
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    # impoort pyQt modules
    from PyQt5.uic import loadUiType
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtWidgets import (QMessageBox, QFileDialog, QListWidgetItem,
                                 QPushButton, QHBoxLayout, QVBoxLayout)

def getPathString(output):
    '''
    returns a path string of the QFileDialog output
    
    pyQt5 returns a tuple (path, filter) not just a path QString like pyQt4
    
    '''
    return str(output if pyQtVersion == "PyQt4" else output[0])

# import python libs
import os
import sys
import webbrowser
import xml.etree.ElementTree as ET
from matplotlib.figure import Figure
    
# import project modules
from mpl_animationmanager import QDialogAnimManager
from latticegraph_designer.app.mpl_pane import GraphEdgesEditor 
from latticegraph_designer.app.core import CrystalCluster, ParseXML, ExportXML, DealXML
from latticegraph_designer.app.dialogs import (QNotImplemented, DialogExportLG, 
                                               DialogSelectLG, DialogImportCryst, 
                                               DialogEditXML, MyDialogPreferences,
                                               DialogDistSearch, DialogChangeEdgeType)
     
# import UI layout created in designer
ui_folder = os.path.dirname(__file__)+'/../resources/ui_layout/'
#ui_folder = 'latticegraph_designer/resources/ui_layout/'
Ui_MainWindow, QMainWindow = loadUiType(ui_folder+'MainWindow_GUI.ui')

class MainWindow(QMainWindow, Ui_MainWindow):
    '''Main application window'''
    
    selectedEdgeChanged = pyqtSignal(object)
    selectedEdgeChangedList = pyqtSignal(object) #when edge selected in QListWidget
    unitCellChanged = pyqtSignal()
    latticeVisibleChanged = pyqtSignal(object) # used to bind with mpl.event
    arrowsVisibleChanged = pyqtSignal(object) # used to bind with mpl.event
    
    def __init__(self, fileName=None, TEXT_MODE=True):
        
        super(MainWindow, self).__init__()
        self.setupUi(self)
        
        self.prefFileName = os.path.dirname(__file__)+'/../resources/preferences.xml'
        self.SETTINGS = ET.parse(self.prefFileName).getroot()
        self.CURRENT_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME","Current theme") 
        self.TEXT_MODE = TEXT_MODE
        
        self.size = (2,2,2)
        self.spinBox_sizeL.setValue(self.size[0])
        self.spinBox_sizeW.setValue(self.size[1])
        self.spinBox_sizeH.setValue(self.size[2])
        self.spinBox_type.clear()
        self.radioButton_output.setChecked(TEXT_MODE)

        self.setup_mpl_canvas()
        
        # initialize canvas
        path = self.prefFileName if fileName is None else fileName
        self.importXML_fromFile(path)
        self.fileNameXML = fileName
        self.label_fileNameXML.setText("XML library file:  " 
                                       + self.getFileLabelText())
        
        self.msb_noActiveEdge = QMessageBox()
        self.msb_noActiveEdge.setIcon(QMessageBox.Critical)
        self.msb_noActiveEdge.setWindowTitle("Message")    
        self.msb_noActiveEdge.setStandardButtons(QMessageBox.Ok)
        self.msb_noActiveEdge.setText("No edge is selected")
        
        # setup signals and slots
        self.btnEditXML.clicked.connect(self.editXML_callback)
        self.spinBox_sizeL.valueChanged.connect(self.changeSize_callback)
        self.spinBox_sizeW.valueChanged.connect(self.changeSize_callback)
        self.spinBox_sizeH.valueChanged.connect(self.changeSize_callback)
        self.btnDel.clicked.connect(self.delteEdge_callback)
        self.btnClear.clicked.connect(self.gee.clearEdges_callback)
        self.btnChangeType.clicked.connect(self.changeType_callback)
        self.btnLength.clicked.connect(self.addDistEdges_callback)
        self.listEdges.currentItemChanged.connect(self.selectEdgeList_callback)
        self.radioButton_output.toggled.connect(self.change_textMode)
        
        self.selectedEdgeChanged.connect(self.selectEdgeSignal_slot)
        self.unitCellChanged.connect(self.update_listEdges)
 
        self.setup_menu()
        
        if self.TEXT_MODE:
            print(self.gee.__doc__)

    def setup_menu(self):
        '''setup slot for menu actions'''
        
        # configure menuFile
        self.action_ImportXML.triggered.connect(self.importXMLdlg_callback)
        self.action_ImportCryst.triggered.connect(self.importCryst_callback)
        self.action_SaveXML.triggered.connect(self.saveXML_callback)  
        self.action_SaveXML_as.triggered.connect(self.saveXML_as_callback)
        self.action_ExportIMG.triggered.connect(self.exportIMG_callback)
        self.action_ExportAnim.triggered.connect(self.exportAnim_callback)
        self.action_Quit.triggered.connect(self.quit_callback)
        # configure menuEdit
        self.action_EditXML.triggered.connect(self.editXML_callback)
        self.action_AddSimEdges.triggered.connect(self.addSimEdges_callback)
        self.action_AddDistEdges.triggered.connect(self.addDistEdges_callback)
        self.action_ChangeType.triggered.connect(self.menuChangeType_callback)
        self.action_DelEdge.triggered.connect(self.delteEdge_callback)
        self.action_ClearEdges.triggered.connect(self.gee.clearEdges_callback)       
        self.action_Pref.triggered.connect(self.preferences_callback)
        # configure menuHelo
        self.action_About.triggered.connect(self.about_callback)
        self.action_Doc.triggered.connect(self.doc_callback)
        
    def setup_mpl_canvas(self):
        '''
        setup matplotlib manipulation pane widget 
        for displaying and editing lattice graph
        
        '''
        self.dpi = 100
        self.fig = Figure((5.0, 5.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.gca(projection='3d') 
        self.fig.subplots_adjust(left=0, bottom=0, right=1, top=1)
 
        self.canvas.setParent(self.mplWidget)
        self.mplLayout.addWidget(self.canvas)
        self.canvas.setFocusPolicy(Qt.ClickFocus)
        self.canvas.setFocus()
        
        # add aniation button
        self.btnPlay = QPushButton("Animate")
        self.btnPlay.setStatusTip("Open animation manager.")
        self.btnPlay.clicked.connect(self.exportAnim_callback)
        self.btnPlay.setFocusPolicy(Qt.NoFocus) 
        mplHbox = QHBoxLayout()
        mplHbox.addWidget(self.btnPlay)
        mplHbox.addStretch()
        mplVbox = QVBoxLayout()
        mplVbox.addLayout(mplHbox)
        mplVbox.addStretch()
        self.canvas.setLayout(mplVbox)
        
    def importXML_fromFile(self, path):
        '''import lattice graph form xml file'''
        
        self.fileNameXML = path
        self.parser = ParseXML(fileName = self.fileNameXML)
        LG_name_list = self.parser.get_LATTICEGRAPH_names()
        if len(LG_name_list) > 1:
            self.dlgSelectLG = DialogSelectLG(self, LG_name_list)
            self.dlgSelectLG.show()
        else:
            self.importXml(LG_name_list[0]) 
        
    def importXml(self, LG_name):
        '''import lattice graph with given name from predefined parser - ParseXML object'''
        
        self.LATTICEGRAPH_name = LG_name
        self.label_fileNameXML.setText("XML library file:  "+self.getFileLabelText())
        self.label_LG_name.setText("Lattice graph name:  "+self.LATTICEGRAPH_name)
        if self.parser is None:
            raise ValueError("Parser is not defined")
        self.lattice, self.UC = self.parser.parse_LATTICEGRAPH(self.LATTICEGRAPH_name)
        self.cluster = CrystalCluster(self.UC, self.lattice, self.size)
        self.ax.clear()
        self.gee = GraphEdgesEditor(self.ax, self.cluster, parent=self,                               
                                    display_report=True)
        self.canvas.draw()
 
        self.update_listEdges()
        self.unitCellChanged.emit()

    def update_listEdges(self):
        '''is used to update QListWidget when unit cell is changed''' 
        
        self.initialization = True # block QListWidget valuechanged callback
        
        self.listEdges.clear()
        defaultListItem = QListWidgetItem('')
        self.listEdges_idToItem = {None: defaultListItem}
        self.listEdges_ItemToId = {defaultListItem.text(): None}
         
        for key, edge in self.gee.UC.edges.items():
            newItem = QListWidgetItem(str(edge))
            self.listEdges.addItem(newItem)
            self.listEdges_idToItem[key] = newItem
            self.listEdges_ItemToId[newItem.text()] = key
        
        self.listEdges.addItem(defaultListItem)
        self.listEdges.setCurrentItem(defaultListItem)        
        self.initialization = False # relieze QListWidget valuechanged callback
        
    def changeSize_callback(self):
        '''called when cluter size in spinBox is chanaged'''
        self.size = (self.spinBox_sizeL.value(), 
                     self.spinBox_sizeW.value(),
                     self.spinBox_sizeH.value())
        self.gee.reset_size(self.size)        
        
    def changeType_callback(self):
        '''called when value of self.spinBox_type is changed'''
        if self.gee.e_active_ind is None:
            self.msb_noActiveEdge.exec_()            
        else:
            self.gee.change_active_edge_type(self.spinBox_type.value())

    def selectEdgeList_callback(self, selectedItem):
        '''called when edge is selected in QListWidget'''
        
        if not self.initialization:
            activeEdge_id = self.listEdges_ItemToId[selectedItem.text()]
            self.gee.select_edge(activeEdge_id)
            self.selectedEdgeChangedList.emit(activeEdge_id)
            if activeEdge_id is None:
                msg = " active edge unselected"
                self.spinBox_type.clear()
            else:
                msg = " selected edge: {}".format(self.cluster.UC.edges[activeEdge_id])
                _type = self.cluster.UC.edges[activeEdge_id].type 
                self.spinBox_type.setValue(_type)
                
            self.statusBar().showMessage(msg, 2000)
            if self.TEXT_MODE:
                print(msg)
                    
    def selectEdgeSignal_slot(self, activeEdge_id):
        '''Process selecting edge signal'''
        activeItem = self.listEdges_idToItem[activeEdge_id]
        self.listEdges.setCurrentItem(activeItem)
        
    def change_textMode(self, _bool):
        '''turn on/off printing actions into terminal'''
        self.TEXT_MODE = _bool
        self.gee.display_report = _bool
        msg = " displaying actions in terminal is turned {}".format("on" if _bool else "off")
        self.statusBar().showMessage(msg, 2000)
        print(msg)
 
    def getFileLabelText(self):
        '''Returns the label string of the xml library file'''
        
        if self.fileNameXML is None:
            return "None"
        else:
            fileName = os.path.basename(self.fileNameXML)
            dirName = os.path.basename(os.path.dirname(self.fileNameXML))
            return os.path.join("...", dirName, fileName)

    def importXMLdlg_callback(self):
        '''when import acttion is activated'''
        
        output = QFileDialog.getOpenFileName(self, 
                               'Open xml library containing Lattice Graph',
                               filter = "XML files (*.xml);;All files (*.*)")
        path = getPathString(output)
        if path != "":
            self.importXML_fromFile(path)
                
    def importCryst_callback(self):
        '''import crystal providing lattice and unit cell parameters'''
        self.dlgImportCryst = DialogImportCryst(self)
        self.dlgImportCryst.show()

    def saveXML_callback(self):
        '''save changes to lattice graph xml library file'''
        
        if self.fileNameXML == None: 
            self.saveXML_as_callback()
        else:
            self.exporter = ExportXML(self.gee.cluster.lattice,
                                      self.gee.cluster.UC,
                                      self.LATTICEGRAPH_name)
            self.exporter.export_to_lib(self.fileNameXML)

    def saveXML_as_callback(self):
        '''save lattice graph to xml library file'''
        
        dialog = DialogExportLG(self, self.LATTICEGRAPH_name, 
                              self.cluster.lattice.atrib["BOUNDARY"])
        if dialog.exec_():
            
            self.LATTICEGRAPH_name = str(dialog.lineEdit_LGname.text())
            self.gee.cluster.lattice.atrib["BOUNDARY"]= \
                                str(dialog.comboBox_boundary.currentText())
                        
            output = QFileDialog.getSaveFileName(self, filter="XML files (*.xml)")
            path = getPathString(output)
            # if not canceled
            if path != '':
                self.fileNameXML = path
                self.exporter = ExportXML(self.gee.cluster.lattice,
                                          self.gee.cluster.UC,
                                          self.LATTICEGRAPH_name)
                self.exporter.export_to_lib(self.fileNameXML)
                self.label_fileNameXML.setText("XML library file:  "+self.getFileLabelText())

    def exportIMG_callback(self):
        '''Savve image of the Heisenberg model (lattice graph)'''
                
        output = QFileDialog.getSaveFileName(self,caption='Save model image',
                                        filter="Images (*.png *.xpm *.jpg);;All files (*.*)")
        path = getPathString(output)
        if path != '':
            self.canvas.print_figure(path, dpi=self.dpi, bbox_inches='tight', pad_inches=0)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def exportAnim_callback(self):
        '''animate lattice graph mpl_pane and open animation manager'''
        
        self.dlgExportAnim = QDialogAnimManager(self.ax)
        self.dlgExportAnim.show()
        # disable animated GraphEdgeEditor artists
        self.gee.sc_active.set_visible(False)
        self.gee.new_edge.set_visible(False)
        # enabele animated GraphEdgeEditor artists
        self.dlgExportAnim.closed.connect(self.gee.sc_active.set_visible)
        self.dlgExportAnim.closed.connect(self.gee.new_edge.set_visible)
        
    def quit_callback(self):
        self.close()    
    
    def editXML_callback(self):
        ''' open lattice graph xml code editor'''
        self.dlgEditXML = DialogEditXML(self)
        self.dlgEditXML.show()
        if self.TEXT_MODE:            
            print(" open lattice graph xml code editor")
    
    def addSimEdges_callback(self):
        '''search for and add edges that have the same length as selected one'''
        
        if self.gee.e_active_ind is None:
            self.msb_noActiveEdge.exec_()            
        else:
            self.gee.searchActiveDistEdge_callback()

    def addDistEdges_callback(self):
        '''opens edge length manipulation manager'''
        self.gee.select_edge(None)
        self.selectEdgeSignal_slot(None)
        self.dlgDistSearch = DialogDistSearch(self)
        self.dlgDistSearch.show()

    def menuChangeType_callback(self):
        '''change selected edge type'''
        if self.gee.e_active_ind is None:
            self.msb_noActiveEdge.exec_()            
        else:
            self.dlg = DialogChangeEdgeType(self)
            self.dlg.show()
 
    def delteEdge_callback(self):
        '''delete selected edge'''        

        if self.gee.e_active_ind is None:
            self.msb_noActiveEdge.exec_()            
        else:
            self.gee.delete_active_edge_callback()
    
    def preferences_callback(self):
        '''Calls preference dialog'''
        
        self.dlgPref = MyDialogPreferences(parent = self)
        self.dlgPref.applySignal.connect(self.applyPref_callback)
        self.arrowsVisibleChanged.connect(self.dlgPref.prefWidget.checkBox_arrows.setChecked)
        self.latticeVisibleChanged.connect(self.dlgPref.prefWidget.checkBox_lattice.setChecked)
        self.dlgPref.show()
    
    def applyPref_callback(self):
        '''when apply button is cklicked in DialogPreferences'''
        
        self.gee.initialize_theme(self.CURRENT_THEME)
        self.gee.set_artists_properties()
        
    def about_callback(self):
        '''display app help'''
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setTextFormat(Qt.RichText)

        text = '''
<b>Lattice graph designer 1.0a1</b>
<br>
Copyright &copy; 2017, Ivan Luchko and Project Contributors 
<br>
Licensed under the terms of the MIT License 
<br><br>
Lattice graph designer is a tool which allows to visualize and create 
a lattice graph model using the intuitive GUI and interactive 3D drag-and-drop 
graph manipulation pane. 
<br><br>
It was primarily created for the 
<a href="http://alps.comp-phys.org">ALPS project</a> to deal with a lattice graph of the 
<a href="https://en.wikipedia.org/wiki/Heisenberg_model_(quantum)">Heisenberg model</a> 
defined in <a href="http://alps.comp-phys.org/mediawiki/index.php/Tutorials:LatticeHOWTO">
ALPS xml graph format</a>.
<br><br>
Support of the other formats and projects can be extended.
<br><br>
For bug reports and feature requests, please go to our 
<a href="https://github.com/luchko/latticegraph_designer">Github website</a>.
'''
        
        self.msg.setText(text)
        self.msg.setWindowTitle("About Lattice graph designer")
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.exec_()
        
    def doc_callback(self):
        '''open documentation'''
        webbrowser.open_new_tab("https://latticegraph-designer.readthedocs.io")
       
 

def run():
    '''run the application'''
    
    # imports requied PyQt modules
    if pyQtVersion == "PyQt4":
        from PyQt4.QtGui import QApplication
    else:
        from PyQt5.QtWidgets import QApplication
        
    # check if xml codefile is passed as an input
    if len(sys.argv) == 2:
        fn = sys.argv[1]
        if os.path.exists(fn):
            fn = os.path.abspath(fn)
        else:
            raise ValueError("file {} doesn't exist.".format(fn))
    else:
        fn = None    
        
    app = QApplication(sys.argv)

    mainWindow = MainWindow(fileName=fn)
    mainWindow.show()
 
    sys.exit(app.exec_())
 
    
if __name__ == '__main__':

    sys.exit(run())