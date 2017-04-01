#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 23:13:29 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

This module contains the definition of impotant dialogs and widgets used in app:
    
    class QNotImplemented(QMessageBox):
    class DialogExportLG(QDilaog, Ui_DialogExportLG):
    class DialogSelectLG(QDilaog, Ui_DialogSelectLG):
    class DialogChangeEdgeType(QDilaog, Ui_DialogChangeEdgeType):
    class DialogEditXML(QDialog, Ui_DialogEditXML):

    class QSitesListItemWidget(QWidget, Ui_mySiteListItem):
    class DialogSelectSites(QDialog, Ui_selectSites):
    class DialogImportCryst(QDilaog, Ui_DialogImportCryst):
        
    class QColorListItemWidget(QWidget, Ui_myColorListItem):
    class QGraphElemPreference(QCustomListWidget_Add):
    class MyWidgetPreferences(WidgetPreferences, Ui_WidgetPreferences):
    class MyDialogPreferences(DialogPreferences):        

    class QDistListItemWidget(QWidget, Ui_myDistListItem):
    class MyDistToolBox(QCustomListWidget_Add):
    class DialogDistSearch(QDialog, MyDistToolBox):

testing and examples:
    
    class TestMainWindow(QObject):
    def test_QGraphElemPreference():
    def test_MyWidgetPreferences():
    def run_test():

Module is compatible with both pyQt4 and pyQt5
        
"""

from __future__ import division # make python 2 use float division

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
    from PyQt4.uic import loadUiType
    from PyQt4.QtCore import Qt, pyqtSignal
    from PyQt4.QtGui import (QMessageBox, QFontDialog, QFileDialog, QPushButton, 
                             QDialogButtonBox, QListWidgetItem, QLabel, QSlider,
                             QHBoxLayout,  QSizePolicy, QTextCursor, QTextFormat, 
                             QColor, QFont, QShortcut, QKeySequence)
else:
    from PyQt5.uic import loadUiType
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import (QColor, QFont, QTextCursor, QTextFormat, QKeySequence) 
    from PyQt5.QtWidgets import (QMessageBox, QFontDialog, QFileDialog, QPushButton, 
                                 QDialogButtonBox, QListWidgetItem, QLabel, 
                                 QSlider, QHBoxLayout, QSizePolicy, QShortcut)    
def getPathString(output):
    '''
    returns a path string of the QFileDialog output
    
    pyQt5 returns a tuple (path, filter) not just a path QString like pyQt4
    
    '''
    return str(output if pyQtVersion == "PyQt4" else output[0])

# import python libs
import numpy as np
import xml.etree.ElementTree as ET

# import project modules
from latticegraph_designer.app.mpl_pane import GraphEdgesEditor 
from latticegraph_designer.app.core import (ParseXML, ExportXML, UnitCell, 
                                            Lattice, CrystalCluster)
from latticegraph_designer.widgets import (QColorButton, XMLHighlighter, 
                                           QCodeEditor, QCustomListWidget, 
                                           QCustomListWidget_Add, DealXML,
                                           DialogPreferences, WidgetPreferences)

# import UI layout created in designer
ui_folder = 'latticegraph_designer/resources/ui_layout/'
Ui_DialogExportLG, QDilaog = loadUiType(ui_folder+'dialog_exportLG.ui')
Ui_DialogSelectLG, QDilaog = loadUiType(ui_folder+'dialog_select_LATTICEGRAPH.ui')
Ui_DialogChangeEdgeType, QDilaog = loadUiType(ui_folder+'dialog_changeEdgeType.ui')
Ui_DialogEditXML, QDialog = loadUiType(ui_folder+'dialog_EditXML.ui')
Ui_mySiteListItem, QDilaog = loadUiType(ui_folder+'widget_mySiteListItem.ui')
Ui_selectSites, QDilaog = loadUiType(ui_folder+'dialog_selectSites.ui')
Ui_DialogImportCryst, QDilaog = loadUiType(ui_folder+'dialog_importCryslat.ui')
Ui_myColorListItem, QWidget = loadUiType(ui_folder+'widget_myColorListItem.ui')
Ui_WidgetPreferences, QWidget = loadUiType(ui_folder+'widget_myPreferences.ui')
Ui_myDistListItem, QWidget = loadUiType(ui_folder+'widget_myDistListItem.ui')

# classes definition

class QNotImplemented(QMessageBox):
    '''called when some functionality is not implemented yet'''
    
    def __init__(self):    
        super(QNotImplemented,self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setIcon(QMessageBox.Information)
        self.setText("Not implemented yet")
        self.setWindowTitle("Message")
        self.setStandardButtons(QMessageBox.Ok)
        self.exec_()            


class DialogExportLG(QDilaog, Ui_DialogExportLG):
    '''exporting Lattice Graph providing Boundary and Lattice Graph name'''
    def __init__(self, parent, LG_name, boundary):
        super(DialogExportLG, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        boundaty_list = ["periodic","open"]
        self.lineEdit_LGname.setText(LG_name)
        self.comboBox_boundary.addItems(boundaty_list)
        currentIndex = boundaty_list.index(boundary)
        self.comboBox_boundary.setCurrentIndex(currentIndex)
        self.btnPreviewXML.clicked.connect(parent.editXML_callback)
            

class DialogSelectLG(QDilaog, Ui_DialogSelectLG):
    '''selecting lattice graph from list in xml library'''
    def __init__(self, parent, names):
        super(DialogSelectLG, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        self.parent = parent
        self.list_LG_names.currentItemChanged.connect(self.importXML)
        
        defaultItem = QListWidgetItem(names[0])
        self.list_LG_names.addItem(defaultItem)
        self.list_LG_names.setCurrentItem(defaultItem)

        if len(names) > 1:
            for name in names[1:]:
                self.list_LG_names.addItem(str(name))
            
    def importXML(self, selectedItem):
            
        self.parent.importXml(str(selectedItem.text()))
        self.parent.fileNameXML = None


class DialogChangeEdgeType(QDilaog, Ui_DialogChangeEdgeType):
    '''Change type of the selected edge'''
    def __init__(self, parent):
        super(DialogChangeEdgeType, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        self.parent = parent
        edge = parent.UC.edges[parent.gee.e_active_ind]
        _type = edge.type
        num = len(parent.gee.e_activeDist_ids) 
        if num == 0:
            label = "Selected edge: {}".format(edge)
        else:
            label = "Selected {0} edges with length: {1}".format(num, edge.length)
        
        self.label_selected.setText(label)
        self.spinBox_current.setValue(_type)
        self.spinBox_new.setValue(_type)
        
        self.btnOk.clicked.connect(self.ok_callback)
        self.btnCancel.clicked.connect(self.reject)
                    
    def ok_callback(self):
        self.parent.gee.change_active_edge_type(self.spinBox_new.value())
        self.accept()


class DialogEditXML(QDialog, Ui_DialogEditXML):
    '''Dialog for interacting with xml library code'''
    
    def __init__(self, parent):
        super(DialogEditXML, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        # "overload" codeEditor 
        self.vbox.removeWidget(self.codeEditor)
        self.codeEditor.setParent(None)
        self.codeEditor.deleteLater()
        
        self.codeEditor = QCodeEditor(DISPLAY_LINE_NUMBERS = True, 
                                     HIGHLIGHT_CURRENT_LINE = False,
                                     SyntaxHighlighter = XMLHighlighter) 
        self.vbox.insertWidget(1,self.codeEditor)
        
        self.parent = parent
        self.fileNameXML = parent.fileNameXML
        self.labelName.setText("XML library file:  "+self.parent.getFileLabelText())

        self.setup_edgeHighlighter()
        self.setXML_fromGEE()  # import xml code
        # highlight active edge
        self.selectedEdgeChanged_slot(self.parent.gee.e_active_ind)

        self.parent.unitCellChanged.connect(self.setXML_fromGEE)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply_callback)    
        self.btnFont.clicked.connect(self.changeFont_callback)
        
    def setXML_fromGEE(self):
        '''add to aditor xml code of the model defined in GraphEdgesEditor'''        
        #remember scrollBar position
        scrollValue = self.codeEditor.verticalScrollBar().value()   
        exporter = ExportXML(self.parent.gee.cluster.lattice,
                             self.parent.gee.cluster.UC,
                             self.parent.LATTICEGRAPH_name,
                             NEW_ID = False)
        self.codeEditor.setPlainText(exporter.get_xml_string())
        
        # restore scrollBar position
        self.codeEditor.verticalScrollBar().setValue(scrollValue)

    def setup_edgeHighlighter(self):
        '''setup active edge code block highligter format'''
        
        self.cursor = QTextCursor(self.codeEditor.document())
        self.noFormat = self.cursor.blockFormat()
        self.activeEdgeFormat = self.cursor.blockFormat()
        self.activeEdgeFormat.setBackground(QColor("#e2e2e2"))
        self.activeEdgeFormat.setProperty(QTextFormat.FullWidthSelection,True)

        self.parent.selectedEdgeChanged.connect(self.selectedEdgeChanged_slot)
        self.parent.selectedEdgeChangedList.connect(self.selectedEdgeChanged_slot)

    def selectedEdgeChanged_slot(self, _id):
        '''highlight the block of code coresponding to the selected edge '''
       
        # dlete previous highlighting       
        self.cursor.setBlockFormat(self.noFormat)
        # set new highlighting
        if _id is not None:
            # search for block of code
            strBegin = '<EDGE id="{}"'.format(_id)
            self.cursor_begin = self.codeEditor.document().find(strBegin)
            self.begin = self.cursor_begin.position()
            self.cursor = self.codeEditor.document().find('</EDGE>', self.begin)
            # select block and change format
            self.cursor.setPosition(self.begin, QTextCursor.KeepAnchor)
            self.cursor.setBlockFormat(self.activeEdgeFormat)
            
            # set proper position of scrollBar
            N = 3; d = 4
            for i in range(d+N):
                self.cursor_begin.movePosition(QTextCursor.Down)
            self.codeEditor.setTextCursor(self.cursor_begin)
            for i in range(d+2*N):
                self.cursor_begin.movePosition(QTextCursor.Up)
            self.codeEditor.setTextCursor(self.cursor_begin)
            for i in range(d):
                self.cursor_begin.movePosition(QTextCursor.Down)
            self.codeEditor.setTextCursor(self.cursor_begin)
            
    def changeFont_callback(self):
        '''change font of the codeEditor'''
        currentFont = self.codeEditor.currentCharFormat().font()
        currentFont.setStyle(QFont.StyleNormal)
        font, valid = QFontDialog.getFont(currentFont)
        if valid:
            self.codeEditor.setFont(font)
 
    def apply_callback(self):
        '''apply changes add update GraphEdgesEditor'''
        
        text = str(self.codeEditor.toPlainText())
        self.parent.parser = ParseXML(string = text)           
        LG_name = self.parent.parser.get_LATTICEGRAPH_names()[0]
        self.parent.importXml(LG_name) 
        #edges ids are changes (ordered) after importing importing 
        self.setXML_fromGEE() 


# classes for importting structure proving crystal parameters


class QSitesListItemWidget(QWidget, Ui_mySiteListItem):
    '''widget for setting listWidget parameters: bool, label, label1, x, y, z'''

    def __init__ (self, parent=None):
        super(QSitesListItemWidget, self).__init__(parent)
        self.setupUi(self)
                     
    def set_data(self, data, strFlag=False):
         
        if data.get("bool") is not None: self.checkBox.setChecked(data["bool"])
        if data.get("label") is not None: self.label.setText(str(data["label"]))
        if data.get("type") is not None: self.label_type.setText(str(data["type"]))        
        if data.get("x") is not None: self.lineEdit_x.setText(str(data["x"]))
        if data.get("y") is not None: self.lineEdit_y.setText(str(data["y"]))
        if data.get("z") is not None: self.lineEdit_z.setText(str(data["z"]))        
        
    def get_data(self):        

        data = {"bool":self.checkBox.isChecked(),
                "label":str(self.label.text()),
                "type":str(self.label_type.text()),
                "x":str(self.lineEdit_x.text()),
                "y":str(self.lineEdit_y.text()),
                "z":str(self.lineEdit_z.text())}        
        
        return data 


class DialogSelectSites(QDialog, Ui_selectSites):
    '''dialog for selecting sites during parsing a cif file''' 
            
    def __init__ (self, data):

        super(DialogSelectSites, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        # "overload" prefWidget 
        self.vbox.removeWidget(self.listWidget)
        self.listWidget.setParent(None)
        self.listWidget.deleteLater()  
        self.listWidget = QCustomListWidget(QCustomWidget = QSitesListItemWidget,
                                            initializationData = data)
        self.vbox.insertWidget(1, self.listWidget)
        
        self.checkBox_all.toggled.connect(self.select_all)
        self.btnCancel.clicked.connect(self.reject)
        self.btnOk.clicked.connect(self.ok_callback)
    
    def select_all(self, _bool):
        '''select/unselect all items'''
        
        data = self.listWidget.get_data()
        for line in data:
            line["bool"] = _bool    
        self.listWidget.set_data(data)
        
    def ok_callback(self):
        '''when button Ok is pressed'''
        
        data = self.listWidget.get_data()
        # create sites text
        atomsTextLine = [" ".join([d["x"],d["y"],d["z"]]) for d in data if d["bool"]]             
        self.atomsText = '\n'.join(atomsTextLine)
        self.accept()


class DialogImportCryst(QDilaog, Ui_DialogImportCryst):
    '''Importing Crystal providing lattice and unit cell parameters'''
    
    def __init__(self, parent):
        super(DialogImportCryst, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setupUi(self)
        
        self.parent = parent
        self.UC = self.parent.UC
        self.lattice = self.parent.lattice
        
        self.btnClose.clicked.connect(self.reject)
        self.btnImport.clicked.connect(self.importCrystal_callback)
        self.btnCIF.clicked.connect(self.process_cif_callback)
        
        self.initialize_forms()
        
    def initialize_forms(self):
        
        self.lineEdit_a.setText(str(round(self.lattice.a, 3)))
        self.lineEdit_b.setText(str(round(self.lattice.b, 3)))
        self.lineEdit_c.setText(str(round(self.lattice.c, 3)))

        self.lineEdit_alpha.setText(str(round(np.rad2deg(self.lattice.alpha),3)))   
        self.lineEdit_beta.setText(str(round(np.rad2deg(self.lattice.beta),3)))   
        self.lineEdit_gamma.setText(str(round(np.rad2deg(self.lattice.gamma),3)))   

        self.textEdit_symops.setText('x, y, z')
        atomsText = ''
        for key, vertex in self.UC.vertices.items():
            coords = ' '.join([str(round(num,5)) for num in vertex.coords])                
            atomsText = atomsText + coords + '\n'
            
        self.textEdit_atoms.setText(atomsText)
        
    def importCrystal_callback(self):
        '''
        compute the coordinates of a unit cell sites according to the 
        space group symmetry operations and import the crystal.
        
        '''
        msg = " Computig the vertices coordinates applying symetry operations"    
        self.parent.statusBar().showMessage(msg)
        if self.parent.TEXT_MODE:
            print(msg)
        
        # parse lattice parameters
        cryst_params = []
        lEs = [self.lineEdit_a, self.lineEdit_b, self.lineEdit_c,
               self.lineEdit_alpha,self.lineEdit_beta,self.lineEdit_gamma]
        for lineEdit in lEs:
            cryst_params.append(float(lineEdit.text()))    
        abc = cryst_params[:3]
        angles = cryst_params[3:]

        # parse atoms coordinates 
        atomsText = str(self.textEdit_atoms.toPlainText())
        atomsText = ''.join(e for e in atomsText if e not in ",") # strip comma
        lines = atomsText.splitlines()
        sites = [[float(num) for num in line.split(' ')] for line in lines if line != '']

        # parse symmetry operations
        symopsText = str(self.textEdit_symops.toPlainText())
        symopsText = ''.join(e for e in symopsText if e not in " '") #strip space and '
        symops_list = [line.split(',') for line in symopsText.splitlines() if line != '']
      
        # check if parsed corectly
        for symop in symops_list:
            if len(symop) != 3:
                raise ValueError("Symmetry operations are not defined according to 'x, y, z' pattern with comma used as separator")
        
        # create UC and lattice 
        self.parent.lattice = Lattice(cell_lengths = abc, angles = angles)
        self.parent.UC = UnitCell(self.parent.lattice)
        self.parent.UC.add_vertices_using_symops(sites, symops_list, 
                                                 self.radioButton_diffTypes.isChecked())
        self.parent.cluster = CrystalCluster(self.parent.UC,
                                             self.parent.lattice,
                                             self.parent.size)
        self.parent.ax.clear()
        self.parent.gee = GraphEdgesEditor(self.parent.ax, self.parent.cluster, 
                                           parent = self.parent, 
                                           display_report = self.parent.TEXT_MODE)        
        self.parent.canvas.draw()
       
        msg = " {} vertices were created".format(self.parent.UC.num_vertices)    
        self.parent.statusBar().showMessage(msg, 2000)
        if self.parent.TEXT_MODE:
            print(msg)
        
        self.parent.fileNameXML = None
        self.parent.LATTICEGRAPH_name = "None"
        self.parent.label_fileNameXML.setText("XML library file:  None")
        self.parent.label_LG_name.setText("Lattice graph name:  None")
        
        self.parent.unitCellChanged.emit()    

    def process_cif_callback(self):
        '''parse lattice parameters from cif file'''
        
        output = QFileDialog.getOpenFileName(self, 
                               'Open Crystallographic Information File',
                               filter = "CIF (*.cif);;All files (*.*)")        
        fileName = getPathString(output)
        
        if fileName == "":
            return
        else:
            abc, angles, UC_data, sg_data = self.parse_cif_file(fileName)
        
        # select atoms sites to consider in model
        
        self.dlg = DialogSelectSites(data = UC_data)
        if not self.dlg.exec_():
            return
        else:
            sitesDatatext = self.dlg.atomsText
        
        # initialize widget
        
        self.lineEdit_a.setText(str(abc[0]))
        self.lineEdit_b.setText(str(abc[1]))
        self.lineEdit_c.setText(str(abc[2]))

        self.lineEdit_alpha.setText(str(angles[0]))   
        self.lineEdit_beta.setText(str(angles[1]))   
        self.lineEdit_gamma.setText(str(angles[2]))   

        self.textEdit_symops.setText("\n".join(sg_data))
        self.textEdit_atoms.setText(sitesDatatext)
        
    def parse_cif_file(self, fileName):       
        '''
        read and process data from cif file
        
        return:

            abc = [a,b,c] - list of unit cell length
            angles = [alpha, beta, gamma] - list of unit cell angles 
            UC_data = [site, ... ] - list of unit cell sites labels and coordinates
                where: site = {'bool':_ ,'label':_, 'type':_, 'x':_, 'y':_, 'z':_}
                       site['bool'] - defines wheather to use site in the model 
            sg_data = ['x, y, z', ...] - space group symmetry operation list
        
        '''        
        with open(fileName, 'r') as f:
            read_data = f.read()
        
        read_data = read_data.replace("\r","")
        read_data = read_data.replace("\n \n","\n\n")
        blocks = read_data.split("\n\n")
        
        abc, angles = self.get_lattice_data(blocks)
        UC_data = self.get_UC_data(blocks)
        sg_data = self.get_sg_data(blocks)
        
        return abc, angles, UC_data, sg_data


    def get_lattice_data(self, blocks):
        '''return lattice parameters data'''
    
        keys = ["_cell_length_a", "_cell_length_b", "_cell_length_c",
                "_cell_angle_alpha", "_cell_angle_beta", "_cell_angle_gamma"]
        
        latttice_block = self.get_block_by_word(blocks, "_cell_length_a")
        data = []
        for key in keys:
            for line in latttice_block.splitlines():
                if key in line:
                    data.append(self._float(line.split()[-1]))
                    break
        return data[:3], data[3:]      
    
    def get_UC_data(self, blocks):
        '''return unit cell data'''
    
        keys = ["_atom_site_label", "_atom_site_type_symbol",
                "_atom_site_fract_x", "_atom_site_fract_y", "_atom_site_fract_z"]
    
        UC_block = self.get_block_by_word(blocks, "_atom_site_fract_x")    
        data = self.get_list_val(UC_block, keys)
        # turn to float site coords
        data = [[val if j<2 else self._float(val) for j, val in enumerate(line)] for line in data]

        data_keys = ["label", "type", "x", "y", "z"]
        data = [{data_keys[j]:val for j, val in enumerate(line)} for line in data]
        for line in data:
            line["bool"] = line["type"] in ["Cu"]  # automaticly selected atoms
                
        return data    
    
    def get_sg_data(self, blocks):
        '''return space group symmetry operations'''
    
        keys = ["_space_group_symop_operation_xyz"]
        sg_block = self.get_block_by_word(blocks, keys[0])
        data = self.get_list_val(sg_block, keys)
        data = [line[0] for line in data]
        
        return data

    # helper functions
    
    def get_block_by_word(self, blocks, word):
        '''helper: return block if it contains a word'''
        for block in blocks:
            if word in block:
                return block
    
    def _float(self, string):
        '''helper: return string without precision parenthesis: 1.23(3)'''
        return float(string.split("(")[0])
    
    def words_split(self, line):
        '''split line on words counting symbols between " chars as single word'''
        
        new_line = []
        in_word = False
        j0 = 0
        for j, char in enumerate(line):
            if (char == "'") or (char == "\""):
                if in_word:
                    new_line.append(line[j0:j])
                else:
                    new_line += line[j0:j].split(' ')
    
                in_word = not in_word
                j0 = j+1
                    
        new_line += line[j0:].split(' ')
        new_line = [elem for elem in new_line if elem != ""]      
    
        return new_line
        
    def get_list_val(self, block, keys):
        '''return data list according to keys in _loop block'''
        
        lines = block.split("loop_")[-1].splitlines()
        lines = [line for line in lines if line != ""]
        all_keys = [line.strip() for line in lines if "_" in line]
        all_line_vals = lines[len(all_keys):]
        
        data = []
        for line in all_line_vals:
            data_line = []  
            for j, val in enumerate(self.words_split(line)):
                if all_keys[j] in keys:
                    data_line.append(val)
            data.append(data_line)
            
        return data    
    
                       
# Preference dialog classes

                
class QColorListItemWidget(QWidget, Ui_myColorListItem):
    '''widget for setting listWidget parameters: label, bool, color'''

    def __init__ (self, parent=None):
        super(QColorListItemWidget, self).__init__(parent)
        self.setupUi(self)        
     
        # "overload" colorBtn 
        self.horizontalLayout.removeWidget(self.colorBtn)
        self.colorBtn.setParent(None)
        self.colorBtn.deleteLater()        
        self.colorBtn = QColorButton()
        self.horizontalLayout.addWidget(self.colorBtn)
       
    def set_data(self, data, strFlag=False):
        '''
        data - dictionary with corresponding keys
        if strFlag = True return input data has str format

        '''
        if data.get("label") is not None: self.label.setText(str(data["label"]))
        if data.get("bool") is not None: 
            self.checkBox.setChecked((data["bool"]=="True") if strFlag else data["bool"])
        if data.get("color") is not None: self.colorBtn.set_color(data["color"])
        
    def get_data(self):
        '''return widgets data'''
        
        data = {"label": str(self.label.text()),
                "bool": self.checkBox.isChecked(),
                "color": self.colorBtn.get_color()}
        
        return data 
                               

class QGraphElemPreference(QCustomListWidget_Add):
    '''toolBox for manipulating vertices and edges preferences'''
    
    def __init__ (self, label="myLabel", initializationData=[]):
        '''label =  Vertices or 'Edges'. '''

        if initializationData == []:
            initializationData = self.create_initalizing_data()
            
        super(QGraphElemPreference, self).__init__(QColorListItemWidget, initializationData)
        self.sliderSize = QSlider(Qt.Horizontal)
        self.labelSize = QLabel("Size: ")
        self.hbox_size = QHBoxLayout()
        self.hbox_size.addWidget(self.labelSize)
        self.hbox_size.addWidget(self.sliderSize)
        self.label = label              
        self.labelQ = QLabel(self.get_labelStr())
        self.labelQ.setAlignment(Qt.AlignCenter) 
        sizePolicy = QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.labelQ.setSizePolicy(sizePolicy)
        #change order of btnAdd
        self.vbox.insertLayout(0,self.hbox_size)        
        self.vbox.insertWidget(0,self.labelQ)
        
    def add_item_callback(self): 
        '''overloaded method'''
        newItem = self.QCustomWidget()
        newItem.set_data({"label": "type {}".format(self.listWidget.count()),
                          "bool": True,
                          "color": None})
        self.listWidget.add_item(newItem)
        self.listWidget.scrollToBottom()
        self.labelQ.setText(self.get_labelStr())
     
    def get_labelStr(self):
        '''get label string'''
        
        return self.label+" ({})".format(self.listWidget.count())
        
    def get_data_ET(self, tag):
        '''get xml ElementTree containing preferences data'''
        
        SETTINGS = ET.Element(tag)
        
        SIZE = ET.Element("SIZE")
        SIZE.set("size", str(self.sliderSize.value()))
        SETTINGS.append(SIZE)        
        dataList = self.listWidget.get_data()
        
        for data in dataList:
            PREFERENCE = ET.Element("PREFERENCE")
            for key, val in data.items():
                PREFERENCE.set(key, str(val))
            SETTINGS.append(PREFERENCE)
        
        return SETTINGS
    
    def set_data_ET(self, root):
        '''get xml ElementTree containing preferences data'''
        
        self.sliderSize.setValue(float(root.find("SIZE").get("size")))
        data_list = []
        for item in root.findall("PREFERENCE"):
            data_list.append(item.attrib)
        self.listWidget.set_data(data_list, strFlag = True)
        self.labelQ.setText(self.get_labelStr())
        
    def create_initalizing_data(self):
        '''returns default initializing data for QCustomListWidget'''
    
        clrs = [u'#00aaff', u'#ff0000', u'#ffff7f', u'#ffaaff', u'#aaffff',
                u'#ffaa7f', u'#a3ff82', u'#5500ff', u'#aa007f', u'#ffffff'] 
        
        data = [{"label":"type %s"%j,"bool":True,"color":clr} for j,clr in enumerate(clrs)]
    
        return data


class MyWidgetPreferences(WidgetPreferences, Ui_WidgetPreferences):
    '''widget used for setting up mpl manipulation pane preferences'''
        
    def __init__ (self):
                
        super(MyWidgetPreferences, self).__init__()
        self.setupUi(self)
        
        # "overload" colorBtn 
        for btnItem in [self.btn_backColor,
                        self.btn_latticeColor,
                        self.btn_activateColor]: 
            self.hbox_colors.removeWidget(btnItem)
            btnItem.setParent(None)
            btnItem.deleteLater()
            
        self.btn_backColor = QColorButton()
        self.hbox_colors.insertWidget(1,self.btn_backColor)
        self.btn_latticeColor = QColorButton()
        self.hbox_colors.insertWidget(4,self.btn_latticeColor)
        self.btn_activateColor = QColorButton()
        self.hbox_colors.insertWidget(7,self.btn_activateColor)    

       # "overload" edgePref/vertPref 
        for prefItem in [self.edgePref, self.vertPref]: 
            self.hbox_pref.removeWidget(prefItem)
            prefItem.setParent(None)
            prefItem.deleteLater()
        self.edgePref = QGraphElemPreference("Edges")
        self.hbox_pref.addWidget(self.edgePref)
        self.vertPref = QGraphElemPreference("Vertices")
        self.hbox_pref.addWidget(self.vertPref)
        
    def set_theme_ET(self, THEME):
        '''initialize preference widget according to THEME ElementTree''' 

        self.checkBox_arrows.setChecked(THEME.find("VISIBLEARROWS").get("value") == "True")
        self.checkBox_lattice.setChecked(THEME.find("VISIBLELATTICE").get("value") == "True")
        self.btn_backColor.set_color(THEME.find("COLORBACKGROUND").get("value"))
        self.btn_latticeColor.set_color(THEME.find("COLORLATTICE").get("value"))
        self.btn_activateColor.set_color(THEME.find("COLORACTIVATE").get("value"))
        self.edgePref.set_data_ET(THEME.find("EDGES"))
        self.vertPref.set_data_ET(THEME.find("VERTICES"))
        
    def get_current_theme_ET(self):
        '''get xml ElementTree containing setting data in preference widget'''
        
        THEME = ET.Element("THEME")
        THEME.set('name',self.curent_theme_name)
        
        tagsList = ["VISIBLEARROWS","VISIBLELATTICE", 
                    "COLORBACKGROUND","COLORLATTICE","COLORACTIVATE"]
        getValList = [self.checkBox_arrows.isChecked(),self.checkBox_lattice.isChecked(), 
                      self.btn_backColor._color, self.btn_latticeColor._color, self.btn_activateColor._color]

        for tag, val in zip(tagsList,getValList):        
            item = ET.Element(tag)
            item.set('value',str(val))
            THEME.append(item)
        
        THEME.append(self.edgePref.get_data_ET("EDGES"))
        THEME.append(self.vertPref.get_data_ET("VERTICES"))
        
        return DealXML.prettify(THEME)
    
class MyDialogPreferences(DialogPreferences):
    '''Preference manager dialog used for setting up mpl manipulation pane'''
    
    def __init__(self, parent):
        DialogPreferences.__init__(self, parent = parent,
                                   WidgetPreferencesClass = MyWidgetPreferences)
 

# classes for manipulating edges relating to their length


class QDistListItemWidget(QWidget, Ui_myDistListItem):
    '''widget for setting listWidget parameters: bool, type, dist, err'''

    def __init__ (self, parent=None):
        super(QDistListItemWidget, self).__init__(parent)
        self.setupUi(self)
         
        self.lineEdit_dist.textEdited.connect(self.activate_checkbox)
        self.lineEdit_err.textEdited.connect(self.activate_checkbox)
        self.spinBox.valueChanged.connect(self.activate_checkbox)
        
    def activate_checkbox(self):
        self.checkBox.setChecked(True)
            
    def set_data(self, data, strFlag=False):
 
        if data.get("bool") is not None: self.checkBox.setChecked(data["bool"])
        if data.get("type") is not None: self.spinBox.setValue(data["type"])
        if data.get("dist") is not None: self.lineEdit_dist.setText(str(data["dist"]))
        if data.get("err") is not None: self.lineEdit_err.setText(str(data["err"]))
        if data.get("found") is not None: self.set_found(data["found"])
         
    def get_data(self):        

        data = {"bool":self.checkBox.isChecked(), "type":self.spinBox.value(),
                "dist":self.get_dist(), "err":float(self.lineEdit_err.text())}        
        
        return data 
               
    def get_dist(self):
        srtDist = self.lineEdit_dist.text()
        return 0 if srtDist == "" else float(srtDist)        
            
    def set_found(self, val):           
        self.label_found.setText("{} edges found".format(val))
        
        
class MyDistToolBox(QCustomListWidget_Add):
    '''toolBox for manipulating edges by their length'''
    
    def __init__ (self, default_data = []):
        ''''''        
        super(MyDistToolBox, self).__init__(QDistListItemWidget, default_data)
        
        sizePolicy = QSizePolicy(QSizePolicy.Maximum,QSizePolicy.Fixed)
        text = "Provide edges type, distance between atoms, and tolerance (%):"
        self.label = QLabel(text)
        self.label.setSizePolicy(sizePolicy)
        self.vbox.insertWidget(0,self.label)
        self.vbox.removeWidget(self.btnAdd)          
        self.btnAdd.setText("+")
        self.btnAdd.setSizePolicy(sizePolicy)
        self.btnAdd.setMaximumWidth(40)     
        self.btnRemove = QPushButton("-")
        self.btnRemove.setSizePolicy(sizePolicy)
        self.btnRemove.setMaximumWidth(40)     
        self.btnSearch = QPushButton("Search")
        self.btnClose = QPushButton("Close")
        self.btnSearch.setDefault(True)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.btnAdd)
        hbox.addWidget(self.btnRemove)
        hbox.addStretch(1)
        hbox.addWidget(self.btnSearch)
        hbox.addWidget(self.btnClose)
        
        self.vbox.addLayout(hbox)

        self.btnRemove.clicked.connect(self.remove_item_callback)
        
    def remove_item_callback(self):
        for item in self.listWidget.selectedItems():
            self.listWidget.takeItem(self.listWidget.row(item))


class DialogDistSearch(QDialog, MyDistToolBox):
    '''dialog for manipulating edges relating to their length'''
    
    def __init__(self, parent):
        
        super(DialogDistSearch, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.parent = parent
        self.update()
                
        self.vbox.setContentsMargins(9,15,9,9)
        self.vbox.setSpacing(10)
        self.setWindowTitle("Manipulate the edges relating to their length")
        
        self.listWidget.currentItemChanged.connect(self.selectDistList_callback) 
        self.parent.selectedEdgeChanged.connect(self.selectEdgeSignal_slot)
        self.parent.unitCellChanged.connect(self.update)
        self.btnSearch.clicked.connect(self.search_callback)
        self.btnClose.clicked.connect(self.close_callback)
        
        QShortcut(QKeySequence("Del"), self, self.parent.gee.delete_active_edge_callback)
        QShortcut(QKeySequence("Shift+Del"), self, self.parent.gee.clearEdges_callback)

    def update(self):
        '''update listWidget'''

        self.initialization = True # block QListWidget valuechanged callback
        
        # read data from parent unitcell
        init_data  = []
        for length, ids in self.parent.UC.lengthDic.items():
            init_data.append({"bool": True, 
                              "type":self.parent.UC.edges[ids[0]].type, 
                              "dist":length,
                              "err":1,
                              "found":len(ids)})
        init_data.append({}) # add one empty item
        self.listWidget.set_data(init_data)
        # select empty item (the last)
        lastItemID = self.listWidget.count() - 1
        self.listWidget.setCurrentItem(self.listWidget.item(lastItemID))        
        
        # create binding dictionaries
        self.distToListItem, self.itemIDToDist = {}, {}
        for j in range(self.listWidget.count()):
            self.distToListItem[init_data[j].get("dist")] = self.listWidget.item(j)
            self.itemIDToDist[j] = init_data[j].get("dist")
        
        self.initialization = False # relieze QListWidget valuechanged callback
        
    def search_callback(self):
        '''searching edges by their length given in listWidget'''
        
        self.parent.UC.clearEdges()
        
        for dataDic in self.listWidget.get_data():
            if (dataDic is not None) and dataDic["bool"]:
                search = self.parent.cluster.edges.search_edges_by_dist
                search(dataDic["type"], dataDic["dist"], dataDic["err"])
                
                # show message                        
                dist = dataDic["dist"]
                edgesList = self.parent.UC.lengthDic.get(dist)
                num = 0 if edgesList is None else len(edgesList)
                msg = ' {0} edges were found with dist={1:.3f}'.format(num,dist)    
                self.parent.statusBar().showMessage(msg, 2000)
                if self.parent.TEXT_MODE:
                    print(msg)

        # make chnages on mpl_pane
        self.parent.gee.create_artists_graph()
        self.parent.gee.set_artists_properties()
        self.parent.unitCellChanged.emit()
        self.parent.selectedEdgeChanged.emit(None)
        
    def selectDistList_callback(self, selectedItem):
        '''select edges from listWidget according to their length'''
        
        if not self.initialization:
            activeDist = self.itemIDToDist[self.listWidget.row(selectedItem)]
            if activeDist is None:
                self.edgesIDs = []
            else:
                self.edgesIDs = self.parent.UC.lengthDic[activeDist][:]
                        
            self.parent.gee.select_edges(self.edgesIDs)
                        
            if activeDist is None:
                msg = " active edges unselected"
            else:
                msg = " selected {0} edges with length: {1}".format(len(self.edgesIDs), activeDist)

            self.parent.statusBar().showMessage(msg, 2000)
            
            if self.parent.TEXT_MODE:
                print(msg)
    
    def add_item_callback(self):
        '''add item to the list toolbox'''
        MyDistToolBox.add_item_callback(self)
        self.itemIDToDist[self.listWidget.count()-1] = None

    def remove_item_callback(self):
        '''remove item from the list toolbox'''
        self.parent.gee.delete_active_edge_callback()
                    
    def selectEdgeSignal_slot(self, activeEdge_id):
        '''when edge is selected at maniplation mpl_pane'''
        
        if activeEdge_id is None:
            dist = None
        else:
            dist = self.parent.UC.edges[activeEdge_id].length
        
        activeItem = self.distToListItem[dist]
        self.listWidget.setCurrentItem(activeItem)
        
    def close_callback(self):
        '''overload close in order to stop distEdge interaction mode'''
        self.parent.gee.select_edges([])
        self.reject()
    
    def closeEvent(self, evnt):
        '''overload close in order to stop distEdge interaction mode'''
        self.parent.gee.select_edges([])
        super(DialogDistSearch, self).closeEvent(evnt)
   
     
#############################################################################


if __name__ == '__main__':

    # test classes    
    
    from core import Vertex, Edge
    import matplotlib.pyplot as plt
    
    # imports requied PyQt modules
    if pyQtVersion == "PyQt4":
        from PyQt4.QtCore import QObject
        from PyQt4.QtGui import QApplication
    else:
        from PyQt5.QtCore import QObject
        from PyQt5.QtWidgets import QApplication
    
    import sys
    
    
    class TestMainWindow(QObject):
        '''class for testing interaction of dialogs with MainWindow'''
        
        selectedEdgeChanged = pyqtSignal(object)
        selectedEdgeChangedList = pyqtSignal(object) #when edge selected in QListWidget
        unitCellChanged = pyqtSignal()
        latticeVisibleChanged = pyqtSignal(object) # used to bind with mpl.event
        arrowsVisibleChanged = pyqtSignal(object) # used to bind with mpl.event
        
        class Label(object):
            def __init__(self): pass
            def setText(self, text): pass
            
        class RadioButton(object):
            def __init__(self): pass
            def setChecked(self, _bool): pass
            
        class statusBar(object):
            def __init__(self): pass
            def showMessage(msg="", sec=2000): pass
                
        def __init__ (self):
            
            super(TestMainWindow, self).__init__()
                                
            self.prefFileName = "preferences.xml"
            self.fileNameXML = None
            self.label_fileNameXML  = None
            self.LATTICEGRAPH_name = "testGraph"
            self.label_fileNameXML = self.Label()
            self.label_LG_name = self.Label()
            
            self.SETTINGS = ET.parse(self.prefFileName).getroot()
            self.CURRENT_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME","Current theme") 
            self.TEXT_MODE = True
            self.radioButton_output = self.RadioButton()
            
            basisMatrix = np.array([[1,0,0],[0,1,0],[0,0,1.3]])
            self.lattice = Lattice(basisMatrix=basisMatrix)        
            self.UC = UnitCell(self.lattice)
            self.UC.add_vertex(Vertex(0,0,[0.2,0.2,0.2]))
            self.UC.add_vertex(Vertex(0,0,[0.3,0.3,0.6]))
            self.UC.add_edge(Edge(0,1,(1,2),(0,0,0)))
            self.UC.add_edge(Edge(0,2,(2,1),(0,0,1)))
            self.UC.add_edge(Edge(0,0,(1,1),(1,0,0)))
            self.UC.add_edge(Edge(0,0,(1,1),(0,1,0)))
            self.UC.add_edge(Edge(0,0,(2,2),(1,0,0)))
            self.UC.add_edge(Edge(0,0,(2,2),(0,1,0)))
            self.size = (2,2,2)
            self.cluster = CrystalCluster(self.UC, self.lattice, self.size)
        
            fig = plt.figure('Graph edges editor', figsize = (6,6))
            self.ax = fig.gca(projection='3d')
            self.gee = GraphEdgesEditor(self.ax, self.cluster, parent = self,                               
                                        display_report = True)
            self.canvas = fig.canvas
            plt.show()
            self.que = []
        
        def getFileLabelText(self):
            return "None"
        
        def importXml(self, LG_name):
            
            if self.parser is None:
                raise ValueError("Parser is not defined")
            self.lattice, self.UC = self.parser.parse_LATTICEGRAPH(self.LATTICEGRAPH_name)
            self.cluster = CrystalCluster(self.UC, self.lattice, self.size)
            self.ax.clear()
            self.gee = GraphEdgesEditor(self.ax, self.cluster, parent = self,                               
                                        display_report = True)
            self.canvas.draw()
        
        # test methonds
        
        def addToQue(self, myQlg):
            '''used to show dialogs in sequence while not blocking the mainWindow'''
            
            if len(self.que) == 0:
                self.showFromQue(myQlg)
            else:
                self.que[-1].rejected.connect(lambda: self.showFromQue(myQlg))
                
            self.que.append(myQlg)
            
        def showFromQue(self, myQlg):        
            print("\n# run {} test".format(type(myQlg)))
            myQlg.show()
            
        def testDialog(self, QDlg):
            '''testing interaction of QDlg with MainWindow'''
            self.myQDlg = QDlg(self) #pass parent
            self.addToQue(self.myQDlg)
            
        def testQPreferencesManager(self):
            
            def applyPref_callback():
                '''when apply button is cklicked in DialogPreferences'''
                self.gee.initialize_theme(self.CURRENT_THEME)
                self.gee.set_artists_properties()
            
            self.myQDlg = MyDialogPreferences(parent = self)
            self.myQDlg.applySignal.connect(applyPref_callback)
            self.addToQue(self.myQDlg)            
        
        def testQDialogExportAnim(self):
            from widgets.QDialogExportAnim import DialogExportAnim
            self.myQDlg = DialogExportAnim(self.ax)
            self.myQDlg.stop_callback()
            if len(self.que) == 0:
                self.myQDlg.start_callback()
            else:
                self.que[-1].rejected.connect(self.myQDlg.start_callback)
            self.addToQue(self.myQDlg)       
    
    
    def showInDialog(widget):
        '''used for displaying widgets in dialog during test'''
            
        dlg = QDialog()
        widget.setParent(dlg)
        vbox = QHBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(widget)
        dlg.setLayout(vbox)
        dlg.exec_()
    
    
    def test_QGraphElemPreference():
        '''testing interaction with QGraphElemPreference via ElementTree object'''
        
        print("\n# run {} test\n".format(QGraphElemPreference))
        
        myQGraphElemPreference = QGraphElemPreference("Vertices")
        elem = myQGraphElemPreference.get_data_ET("VERTICES") # get ET from widget
    
        print(" myQGraphElemPreference.get_data_ET() test\n")
        ET.dump(DealXML.prettify(elem))
        myQGraphElemPreference.set_data_ET(elem)  # initialize widget with ET
    
        showInDialog(myQGraphElemPreference)
            
    def test_MyWidgetPreferences():
        '''testing interaction with MyWidgetPreferences via ElementTree object'''
        
        print("\n# run {} test\n".format(MyWidgetPreferences))
    
        myWidgetPreferences = MyWidgetPreferences()

        xmlText = '''
<THEME name="Default theme">
  <VISIBLEARROWS value="True" />
  <VISIBLELATTICE value="True" />
  <COLORBACKGROUND value="#000000" />
  <COLORLATTICE value="#b5ff93" />
  <COLORACTIVATE value="#00ff00" />
  <EDGES>
    <SIZE size="23" />
    <PREFERENCE bool="True" color="#00aaff" label="type 0" />
    <PREFERENCE bool="True" color="#ff0000" label="type 1" />
    <PREFERENCE bool="True" color="#fafa00" label="type 2" />
    <PREFERENCE bool="True" color="#ffaaff" label="type 3" />
    <PREFERENCE bool="True" color="#00007f" label="type 4" />
    <PREFERENCE bool="True" color="#ffaa7f" label="type 5" />
    <PREFERENCE bool="True" color="#a3ff82" label="type 6" />
    <PREFERENCE bool="True" color="#ffffff" label="type 7" />
    <PREFERENCE bool="True" color="#aa007f" label="type 8" />
    <PREFERENCE bool="True" color="#55aa7f" label="type 9" />
  </EDGES>
  <VERTICES>
    <SIZE size="26" />
    <PREFERENCE bool="True" color="#ffaa00" label="type 0" />
    <PREFERENCE bool="True" color="#ffff00" label="type 1" />
    <PREFERENCE bool="True" color="#5500ff" label="type 2" />
    <PREFERENCE bool="True" color="#ff0adf" label="type 3" />
    <PREFERENCE bool="True" color="#aa5500" label="type 4" />
    <PREFERENCE bool="True" color="#ff0000" label="type 5" />
    <PREFERENCE bool="True" color="#55ffff" label="type 6" />
    <PREFERENCE bool="True" color="#ffffff" label="type 7" />
    <PREFERENCE bool="True" color="#ffaaff" label="type 8" />
    <PREFERENCE bool="True" color="#55ff00" label="type 9" />
  </VERTICES>
</THEME>
'''
        THEME = ET.fromstring(xmlText)   
    
        print(" MyWidgetPreferences.set_theme_ET() test\n")
        myWidgetPreferences.set_theme_ET(THEME)
        print(" MyWidgetPreferences.get_current_theme_ET() test\n")
        ET.dump(myWidgetPreferences.get_current_theme_ET()) # get ET from widget
        
        showInDialog(myWidgetPreferences)
        
    
    def run_test():
        
        print("\n {} is imported".format(pyQtVersion))
            
        app = QApplication([])
        
        # creating TestDialogDistSearch
        myTestMainWindow = TestMainWindow()
    
        # testing
        myTestMainWindow.testDialog(DialogImportCryst)
#        myTestMainWindow.testDialog(DialogEditXML)
#        myTestMainWindow.testDialog(DialogDistSearch)
    
#        test_QGraphElemPreference()
#        test_MyWidgetPreferences()
#        myTestMainWindow.testQPreferencesManager()
    
#        myTestMainWindow.testQDialogExportAnim()
        
        sys.exit(app.exec_())

############################################################################
    
    run_test()

