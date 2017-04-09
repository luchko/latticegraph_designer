#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Very weak testing of the basic functionality using unittest and QTest"""

__author__ = "Ivan Luchko (luchko.ivan@gmail.com)"
__version__ = "1.0a1"
__date__ = "Apr 4, 2017"
__copyright__ = "Copyright (c) 2017, Ivan Luchko and Project Contributors "

import sys
import os
import subprocess
import unittest

# define pyQt version
try:
    from PyQt4.QtGui import QApplication, QDialogButtonBox, QTextCursor
    from PyQt4.QtTest import QTest
    from PyQt4.QtCore import Qt
    
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication, QDialogButtonBox
        from PyQt5.QtGui import QTextCursor
        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt

    except ImportError:
        raise ImportError("neither PyQt4 or PyQt5 is found")

from latticegraph_designer.app.main import MainWindow
from latticegraph_designer.app.dialogs import (DialogImportCryst, DialogDistSearch,
                                               MyDialogPreferences, DialogEditXML)
from mpl_animationmanager import QDialogAnimManager
app = QApplication(sys.argv)

test_folder = "latticegraph_designer/test/"

def printgraph(libFile):
    
    try: 
        import pyalps
            
    except ImportError:
        print("ALPS package is not installed.")
        return "ALPS package is not installed."
    else:
        testFile = '''LATTICE_LIBRARY=\"{}\"
LATTICE=\"test\"
L=2
W=2
H=2'''.format(libFile)
            
        p = subprocess.Popen(['printgraph'], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        output, error = p.communicate(input=testFile)            
        
        if p.returncode == 0:
            return output
        else:
            raise Exception(error)
            return "Error"


class GraphEdgesEditorTest(unittest.TestCase):
    '''Test the mpl_pane functionality'''
    def setUp(self):
        
        from latticegraph_designer.app.core import Vertex, UnitCell, Lattice, CrystalCluster
        from latticegraph_designer.app.mpl_pane import GraphEdgesEditor
#        import matplotlib
#        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
        
        lattice = Lattice(basisMatrix=np.array([[1,0,0],[0,1,0],[0,0,1.3]]).T)
        self.UC = UnitCell()
        self.UC.add_vertex(Vertex(0,0,[0.2,0.2,0.2]))
        self.UC.add_vertex(Vertex(0,0,[0.3,0.3,0.6]))
        
        self.cluster = CrystalCluster(self.UC,lattice,(2,2,2))    
        self.fig = plt.figure('Graph edges editor', figsize=(5,5), dpi=100)
        self.ax = self.fig.gca(projection='3d')  # same as ax = Axes3D(fig)    
        self.gee = GraphEdgesEditor(self.ax, self.cluster, display_report=False)
        
    def test_clear(self):

        self.gee.clearEdges_callback()
        self.assertEqual(self.gee.UC.num_edges, 0)
#        self.assertEqual(len(self.ax.artists), 9)

    def addEdge(self, source, target):

        self.gee.v_source_ind = source
        self.gee.v_target_ind = target       
        self.gee.add_edge()
        
    def test_addEdges(self):
        
        self.test_clear()
        self.addEdge(0, 8)
        self.assertEqual(self.gee.UC.num_edges, 1)
        self.addEdge(0, 4)
        self.assertEqual(self.gee.UC.num_edges, 2)
#        self.assertEqual(len(self.ax.artists), 9)
                
    def test_searchActiveDistEdge(self):

        self.test_addEdges()
        self.gee.e_active_ind = 2
        self.gee.searchActiveDistEdge_callback()
        self.assertEqual(self.gee.UC.num_edges, 5)

    def test_delete(self):
        
        self.test_addEdges()
        self.gee.e_active_ind = 1
        self.gee.delete_active_edge_callback()
        self.assertEqual(self.gee.UC.num_edges, 1)


class MainWindowTest(unittest.TestCase):
    '''Test the MainWindow GUI'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=False)
        
    
#    def test_terminalLaunch(self):
#                
#        p = subprocess.Popen(['graphdesigner','&'],
#                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#        
#        output, error = p.communicate()
#
##        p = subprocess.call("graphdesigner", shell=True)
#        p.kill()            
#        
#        if p.returncode == 0:
#            return output
#        else:
#            raise Exception(error)
#            return "Error"
        
     
    def test_ImportXML(self):
        
        fn_input = os.path.abspath(test_folder+"testLib_input.xml")
        self.mainWindow.importXML_fromFile(fn_input)
        self.assertEqual(self.mainWindow.cluster.UC.num_vertices, 2)
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 6)

    def test_ImportCIF(self):
        
        fn_cif = os.path.abspath(test_folder+"test.cif")        
        self.dlgImportCryst = DialogImportCryst(self.mainWindow)
        self.dlgImportCryst.process_cif(fn_cif, TESTING=True)
        
        self.assertAlmostEqual(float(self.dlgImportCryst.lineEdit_a.text()), 20.753)
        self.assertAlmostEqual(float(self.dlgImportCryst.lineEdit_b.text()), 7.517)
        self.assertAlmostEqual(float(self.dlgImportCryst.lineEdit_c.text()), 6.4475)
        self.assertAlmostEqual(float(self.dlgImportCryst.lineEdit_alpha.text()), 90.0)
        self.assertAlmostEqual(float(self.dlgImportCryst.lineEdit_beta.text()), 103.21)
        self.assertAlmostEqual(float(self.dlgImportCryst.lineEdit_gamma.text()), 90.0)
        
        self.dlgImportCryst.importCrystal_callback()

        self.assertEqual(self.mainWindow.cluster.UC.num_vertices, 8)
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 0)
    
    def test_DistSearch(self):
        
        self.test_ImportCIF() 
        self.assertEqual(self.mainWindow.cluster.UC.num_vertices, 8)
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 0)
        # opne "edge length manager" 
        self.mainWindow.action_AddDistEdges.trigger()
        self.dlgDistSearch = self.mainWindow.dlgDistSearch
        
        lw = self.dlgDistSearch.listWidget        
        # add edges with length 5.514
        data = {"bool": True, "type":0, "dist":5.514, "err":1} 
        lw.itemWidget(lw.item(0)).set_data(data)
        self.dlgDistSearch.search_callback()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 16)
        # add edges with length 7.55        
        data = {"bool": True, "type":1, "dist":7.55, "err":0.1} 
        lw.itemWidget(lw.item(1)).set_data(data)
        self.dlgDistSearch.search_callback()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 20)
        # delete selected edges
        lw.setCurrentItem(lw.item(0))
        self.dlgDistSearch.remove_item_callback()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 4)
        # export to XML lib
        self.ExportXML(os.path.abspath(test_folder+"testLib_output.xml"))        
 
    def ExportXML(self, fn_output):
        
        self.mainWindow.fileNameXML = fn_output
        self.mainWindow.LATTICEGRAPH_name = "test"
        self.mainWindow.saveXML_callback()
        self.assertNotEqual(printgraph(fn_output), "Error")

    def test_ExportXML(self):
        
        self.test_ImportXML()
        fn_output = os.path.abspath(test_folder+"testLib_output.xml")
        self.ExportXML(fn_output)        
        fn_benchmark = os.path.abspath(test_folder+"testLib_output_benchmark.xml")
        self.assertEqual(printgraph(fn_output), printgraph(fn_benchmark))


class PreferencesTest(unittest.TestCase):
    '''Test the Preferences manager'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=False)
     
    def test_defaults(self):
        pass
 
    def test_PrefManager(self):
        
        self.dlgPref = MyDialogPreferences(parent = self.mainWindow)
        self.dlgPref.applySignal.connect(self.mainWindow.applyPref_callback)
        self.mainWindow.arrowsVisibleChanged.connect(self.dlgPref.prefWidget.checkBox_arrows.setChecked)
        self.mainWindow.latticeVisibleChanged.connect(self.dlgPref.prefWidget.checkBox_lattice.setChecked)       
        
        self.dlgPref.change_theme_callback(2)
        # check chnages in widget
        self.dlgPref.btnApply.click()
        # check changes in main
        
        self.dlgPref.btnDefaults.click()
        # check changes
        self.dlgPref.btnClose.click()


class AnimaManagerTest(unittest.TestCase):
    '''Test the Animation manager'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=False)
      
    def test_AnimManager(self):
        
        self.mainWindow.action_ExportAnim.trigger()
        self.dlgExportAnim = self.mainWindow.dlgExportAnim
        
        self.dlgExportAnim.btnPause.click()
        self.dlgExportAnim.btnStart.click()

        # change dpi
        self.dlgExportAnim.spinBox_dpi.setValue(50)
        self.assertEqual(self.dlgExportAnim.dpi, 50)
        # change fps
        self.dlgExportAnim.spinBox_fps.setValue(10)
        self.assertEqual(self.dlgExportAnim.fps, 10)

        # change elevation
        self.dlgExportAnim.spinBox_elev.setValue(10)
        self.assertEqual(self.dlgExportAnim.elevation, 10)
        # change rotation period
        self.dlgExportAnim.spinBox_period_rot.setValue(30)
        self.assertEqual(self.dlgExportAnim.period_rot, 30)        
        self.dlgExportAnim.spinBox_period_rot.setValue(3)
        self.assertEqual(self.dlgExportAnim.period_rot, 3)                
        
        # stop
        self.dlgExportAnim.btnStop.click()
        # change initial azimut
        self.dlgExportAnim.spinBox_azim.setValue(-50)
        self.assertEqual(self.dlgExportAnim.zero_azim, -50)

        # export animation
        path = os.path.abspath("./latticegraph_designer/test/test")
        self.dlgExportAnim.lineEdit_name.setText(path)
        self.dlgExportAnim.btnExport.click()

        self.dlgExportAnim.btnClose.click()


class CodeEditorTest(unittest.TestCase):
    '''Test the Animation manager'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=False)
        self.mainWindow.action_EditXML.trigger()
      
    def test_CodeEditor(self):
        
        # insert xml data from another lib and apply
        fn = os.path.abspath('./latticegraph_designer/test/triangular_network.xml')
        with open(fn) as f:
            self.mainWindow.dlgEditXML.codeEditor.setPlainText(f.read())        

        self.mainWindow.dlgEditXML.buttonBox.button(QDialogButtonBox.Apply).click()
        # check changes in main window
        self.assertEqual(self.mainWindow.cluster.UC.num_vertices, 96)
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 288)

        self.mainWindow.dlgEditXML.buttonBox.button(QDialogButtonBox.Close).click()
        
    def test_edge_selection(self):
                        
        # select edge from listWidget
        ind = 0
        self.mainWindow.listEdges.setCurrentItem(self.mainWindow.listEdges.item(ind))
        self.assertTrue(self.mainWindow.gee.e_active_ind == ind+1)
        
        # select edge from listWidget
        ind = 5
        self.mainWindow.listEdges.setCurrentItem(self.mainWindow.listEdges.item(ind))
        self.assertTrue(self.mainWindow.gee.e_active_ind == ind+1)
 
        # select edge from listWidget
        ind = 6
        self.mainWindow.listEdges.setCurrentItem(self.mainWindow.listEdges.item(ind))
        self.assertTrue(self.mainWindow.gee.e_active_ind is None)

        # move cursor to the bottow of document
        self.mainWindow.dlgEditXML.codeEditor.moveCursor(QTextCursor.End)
        
        self.mainWindow.dlgEditXML.close()


if __name__ == "__main__":
    unittest.main()
    
