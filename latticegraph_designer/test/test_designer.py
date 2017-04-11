#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Very weak testing of the basic functionality using unittest and QTest"""

from __future__ import division

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

test_folder = "./latticegraph_designer/test/"

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

from latticegraph_designer.app.core import Vertex, Edge, UnitCell, Lattice, CrystalCluster
from latticegraph_designer.app.mpl_pane import GraphEdgesEditor
from matplotlib.backend_bases import KeyEvent, MouseEvent
import matplotlib.pyplot as plt
import numpy as np


class GeeMethodsTest(unittest.TestCase):
    '''Test the mpl_pane GraphEdgesEditor methods'''
    def setUp(self):
                
        lattice = Lattice(basisMatrix=np.array([[1,0,0],[0,1,0],[0,0,1.3]]).T)
        self.UC = UnitCell()
        self.UC.add_vertex(Vertex(0,0,[0.2,0.2,0.2]))
        self.UC.add_vertex(Vertex(0,0,[0.3,0.3,0.6]))
        self.UC.add_edge(Edge(0,1,(1,2),(0,0,0)))
        self.UC.add_edge(Edge(0,2,(2,1),(0,0,1)))
        self.UC.add_edge(Edge(0,0,(1,1),(1,0,0)))
        self.UC.add_edge(Edge(0,0,(1,1),(0,1,0)))
        self.UC.add_edge(Edge(0,0,(2,2),(1,0,0)))
        self.UC.add_edge(Edge(0,0,(2,2),(0,1,0)))
        
        self.cluster = CrystalCluster(self.UC,lattice,(2,2,2))    
        self.fig = plt.figure()
        self.ax = self.fig.gca(projection='3d')  # same as ax = Axes3D(fig)    
        self.gee = GraphEdgesEditor(self.ax, self.cluster, display_report=True)
        
    def test_setUp(self):

        self.setUp()        
        self.assertEqual(self.gee.UC.num_vertices, 2)        
        self.assertEqual(self.gee.UC.num_edges, 6)        
        self.assertEqual(len(self.ax.artists), 6+1+4*4+4*3) # arrows + new edge + edges
        self.assertEqual(len(self.gee.edges_lines), 28)

    def test_clear(self):
        
        self.setUp()
        self.gee.clearEdges_callback()
        
        self.assertEqual(self.gee.UC.num_edges, 0)
        self.assertEqual(len(self.ax.artists), 6+1) # arrows + new edge
        self.assertEqual(len(self.gee.edges_lines), 0)
 
    def addEdge(self, source, target):

        self.gee.v_source_ind = source
        self.gee.v_target_ind = target       
        self.gee.add_edge()

    def test_addRemoveEdges(self):
        
        self.setUp()
        self.gee.clearEdges_callback()
        
        self.addEdge(0, 8)
        self.assertEqual(self.gee.UC.num_edges, 1)
        self.assertEqual(len(self.gee.edges_lines), 8)
        self.assertEqual(len(self.ax.artists), 6+1+8)

        self.addEdge(0, 4)
        self.assertEqual(self.gee.UC.num_edges, 2)
        self.assertEqual(len(self.gee.edges_lines), 8+4)
        self.assertEqual(len(self.ax.artists), 6+1+8+4)
  
        self.gee.select_edge(1)
        self.gee.delete_active_edge_callback()
        self.assertEqual(self.gee.UC.num_edges, 1)
        self.assertEqual(len(self.gee.edges_lines), 4)
        self.assertEqual(len(self.ax.artists), 6+1+4)
  
    def test_edgeSelection(self):
        
        self.setUp()
        self.gee.clearEdges_callback()       
        self.addEdge(0, 8)
        self.addEdge(0, 4)        
 
        # select edge
        _id = 2
        self.gee.select_edge(_id)
        self.assertTrue(self.gee.e_active_ind == _id)
        for j in self.gee.edges.array_ind[_id]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == self.gee.color_active)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw_active)
        
        # test unselect edge
        self.gee.select_edge(None)
        self.assertTrue(self.gee.e_active_ind is None)
        color = self.gee.colors_e[self.UC.edges[_id].type]
        for j in self.gee.edges.array_ind[_id]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == color)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw)
       
        # test edge unselection by selecting another edge
        self.gee.select_edge(_id)
        id_new = 1
        self.gee.select_edge(id_new)
        self.assertTrue(self.gee.e_active_ind == id_new)
        for j in self.gee.edges.array_ind[id_new]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == self.gee.color_active)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw_active)
        #check if previous active unselected
        color = self.gee.colors_e[self.UC.edges[_id].type]
        for j in self.gee.edges.array_ind[_id]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == color)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw)
        
    def test_searchActiveDistEdge(self):

        self.setUp()
        self.gee.clearEdges_callback()        
        self.addEdge(0, 8)
        self.addEdge(0, 4)

        self.assertEqual(self.gee.UC.num_edges, 1+1)
        self.assertEqual(len(self.gee.edges_lines), 8+4)
        self.assertEqual(len(self.ax.artists), 6+1+8+4)

        self.gee.select_edge(2)
        self.gee.searchActiveDistEdge_callback()
        self.assertEqual(self.gee.UC.num_edges, 1+4) # 4 edges simmilar to 2 found
        self.assertEqual(len(self.gee.edges_lines), 8+4*4)
        self.assertEqual(len(self.ax.artists), 6+1+8+4*4)
        
    def test_xml_ImportExport(self):
        
        self.setUp()
        
        # export to lib
        fn = test_folder+"test_coreExport.xml"
        self.cluster.export_toFile(fileName = fn, LATTICEGRAPH_name = "test")       
        self.gee.clearEdges_callback() 
        self.assertEqual(self.gee.UC.num_vertices, 2)        
        self.assertEqual(self.gee.UC.num_edges, 0)        
        
        # import from lib
        self.cluster.import_fromFile(fileName = fn, LATTICEGRAPH_name = "test")
        self.fig = plt.figure()
        self.ax = self.fig.gca(projection='3d')  # same as ax = Axes3D(fig)    
        self.gee = GraphEdgesEditor(self.ax, self.cluster, display_report=True)
        
        # check initialization
        self.assertEqual(self.gee.UC.num_vertices, 2)        
        self.assertEqual(self.gee.UC.num_edges, 6)        
        self.assertEqual(len(self.ax.artists), 6+1+4*4+4*3) # arrows + new edge + edges
        self.assertEqual(len(self.gee.edges_lines), 28)

    def test_USE_COLLECTIONS(self):
        '''testing the usage of lineCollection for depicting edges'''

        GraphEdgesEditor.USE_COLLECTIONS = True
        self.setUp()
        try:
            self.assertEqual(self.gee.UC.num_vertices, 2)        
            self.assertEqual(self.gee.UC.num_edges, 6)        
            self.assertEqual(len(self.ax.artists), 6+1) # arrows + new edge
            self.assertEqual(len(self.gee.edges_lines), 6)
            # collections: vertices, lattice, edges
            self.assertEqual(len(self.ax.collections), 1+1+6) 

            # select edge
            _id = 3
            self.gee.select_edge(_id)
            self.assertTrue(self.gee.e_active_ind == _id)

            # remove edge
            self.gee.delete_active_edge_callback()
            self.assertEqual(self.gee.UC.num_edges, 5)
            self.assertEqual(len(self.gee.edges_lines), 5)
            # collections: vertices, lattice, edges
            self.assertEqual(len(self.ax.collections), 1+1+5) 

            # clear edges
            self.gee.clearEdges_callback()
            self.assertEqual(self.gee.UC.num_edges, 0)        
            self.assertEqual(len(self.ax.artists), 6+1) # arrows + new edge
            self.assertEqual(len(self.gee.edges_lines), 0)
            # collections: vertices, lattice, edges
            self.assertEqual(len(self.ax.collections), 1+1+0) 
            
            # add edge
            self.addEdge(0, 4)
            self.assertEqual(self.gee.UC.num_edges, 1)
            self.assertEqual(len(self.gee.edges_lines), 1)
            # collections: vertices, lattice, edges
            self.assertEqual(len(self.ax.collections), 1+1+1) 
                  
        except:  # we have to  set USE_COLLECTIONS=False for other tests
            GraphEdgesEditor.USE_COLLECTIONS = False
            raise
            
        finally:    
            GraphEdgesEditor.USE_COLLECTIONS = False

class GeeInteractionTest(unittest.TestCase):
    '''Test the mpl_pane keybounding and mouse manipulation'''
    def setUp(self):
        
        self.mainWindow = MainWindow(TEXT_MODE=True)

        self.ax = self.mainWindow.ax
        self.gee = self.mainWindow.gee
        self.canvas = self.mainWindow.canvas
 
    def test_keyBindings(self):
                
        self.setUp()
        
        # test ctrl+numKey - change active edge type to numkey
        _id, new_type = 2, 5
        self.gee.select_edge(_id)
        self.canvas.key_press_event('ctrl+{}'.format(new_type))        
        self.gee.select_edge(None)
        self.assertTrue(self.gee.UC.edges[_id].type == new_type)
        color = self.gee.colors_e[new_type]
        for j in self.gee.edges.array_ind[_id]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == color)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw)

        self.canvas.key_press_event('delete')        
        
        self.canvas.key_press_event('shift+delete') 
        
        self.canvas.key_press_event('ctrl+d')        
        
        # test display_report switch
        _bool = self.gee.display_report
        self.canvas.key_press_event('t')        
        self.assertTrue(self.gee.display_report != _bool)
        self.canvas.key_press_event('t')        
        self.assertTrue(self.gee.display_report == _bool)

        # test display_lattice switch
        _bool = self.gee.display_lattice
        self.canvas.key_press_event('n')        
        self.assertTrue(self.gee.display_lattice != _bool)
        self.assertTrue(self.gee.latticeNet.get_visible() != _bool)
        self.canvas.key_press_event('n')        
        self.assertTrue(self.gee.display_lattice == _bool)
        self.assertTrue(self.gee.latticeNet.get_visible() == _bool)

        # test display_arrows switch
        _bool = self.gee.display_arrows
        self.canvas.key_press_event('m')        
        self.assertTrue(self.gee.display_arrows != _bool)
        for elem in self.gee.arrows:
            self.assertTrue(elem.get_visible() != _bool)
        self.canvas.key_press_event('m')        
        self.assertTrue(self.gee.display_arrows == _bool)
        for elem in self.gee.arrows:
            self.assertTrue(elem.get_visible() == _bool)

    def test_mouseManipulation(self):
                
        self.setUp()
        self.gee.clearEdges_callback() 
        
        # simulate rotation
        self.canvas.motion_notify_event(x=20, y=20)  
        self.canvas.button_press_event(x=20, y=20, button=1)        
        self.assertEqual(self.gee.v_source_ind, None)
        self.canvas.motion_notify_event(x=20, y=20)
        azim, elev = self.gee.ax.azim, self.gee.ax.elev
        # rotate
        self.assertTrue(self.gee.isRotated)
        self.canvas.motion_notify_event(x=30, y=30)
        self.assertTrue(self.gee.isRotated)
        self.assertTrue(self.gee.ax.elev != elev)
        self.assertTrue(self.gee.ax.azim != azim)        
        azim, elev = self.gee.ax.azim, self.gee.ax.elev
        # rotate more
        self.canvas.motion_notify_event(x=40, y=40)
        self.assertTrue(self.gee.ax.elev != elev)
        self.assertTrue(self.gee.ax.azim != azim)                
        # release button
        self.canvas.button_release_event(x=40, y=40, button=1)
        self.canvas.motion_notify_event(x=40, y=45)
        # check
        self.assertEqual(self.gee.UC.num_edges, 0)
        self.assertEqual(self.gee.e_active_ind, None)
        self.assertEqual(self.gee.isRotated, False)

        # vertice actiovation/deactivation test
        source_ind = 0
        x_data, y_data = self.gee.x_scr[source_ind], self.gee.y_scr[source_ind]
        # vertice actiovation
        self.canvas.motion_notify_event(x=x_data, y=y_data)
        self.assertTrue(self.gee.v_active_ind == source_ind)
        # vertice deactivation
        self.canvas.motion_notify_event(x=30, y=30)
        self.assertTrue(self.gee.v_active_ind == None)
        
        # simulate unsuccessful edge creation atempt
        # activate source vertex
        self.canvas.motion_notify_event(x=x_data, y=y_data)  
        self.canvas.button_press_event(x=x_data, y=x_data, button=1)        
        self.assertEqual(self.gee.v_source_ind, source_ind)
        # draw potential edge
        self.canvas.motion_notify_event(x=30, y=30)
        # release button at random spot
        self.canvas.motion_notify_event(x=40, y=40)
        self.canvas.button_release_event(x=40, y=40, button=1)
        # check
        self.assertEqual(self.gee.UC.num_edges, 0)
        self.assertEqual(self.gee.e_active_ind, None)

        # simulate successful edge creation atempt
        _id = 1
        # activate source vertex
        self.canvas.motion_notify_event(x=x_data, y=y_data)  
        self.canvas.button_press_event(x=x_data, y=x_data, button=1)        
        self.assertEqual(self.gee.v_source_ind, source_ind)
        # draw potential edge
        self.canvas.motion_notify_event(x=30, y=30)
        # select target vertex
        target_ind = 4
        x_data, y_data = self.gee.x_scr[target_ind], self.gee.y_scr[target_ind]
        self.canvas.motion_notify_event(x=x_data, y=y_data)  
        self.canvas.button_release_event(x=x_data, y=y_data, button=1)
        # check
        self.assertEqual(self.gee.UC.num_edges, 1)
        self.assertEqual(self.gee.e_active_ind, _id)
        
        # unselect edge by clicking on the empty spot
        self.canvas.motion_notify_event(x=30, y=30)
        self.canvas.button_press_event(x=30, y=30, button=1)
        self.canvas.button_release_event(x=30, y=30, button=1)
        # check
        self.assertTrue(self.gee.e_active_ind is None)
        color = self.gee.colors_e[self.gee.UC.edges[_id].type]
        for j in self.gee.edges.array_ind[_id]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == color)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw)

        # select the edge
        source_ind, target_ind = 0, 4
        x_data = (self.gee.x_scr[source_ind] + self.gee.x_scr[target_ind])/2
        y_data = (self.gee.y_scr[source_ind] + self.gee.y_scr[target_ind])/2
        # simulate selection
        self.canvas.motion_notify_event(x=x_data, y=y_data)
        self.canvas.button_press_event(x=x_data, y=y_data, button=1)
        self.canvas.button_release_event(x=x_data, y=y_data, button=1)
        self.assertTrue(self.gee.e_active_ind == _id)
        for j in self.gee.edges.array_ind[_id]:             
            self.assertTrue(self.gee.edges_lines[j].get_color() == self.gee.color_active)
            self.assertTrue(self.gee.edges_lines[j].get_linewidth() == self.gee.lw_active)

        # search for edges having the same length as selected
        self.mainWindow.action_AddSimEdges.trigger()
        self.assertEqual(self.gee.UC.num_edges, 4)
        self.assertEqual(self.gee.e_active_ind, None)        
     
class MainWindowTest(unittest.TestCase):
    '''Test the MainWindow GUI'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=True)
           
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

    def test_ImportFromALPS_lib(self):
        
        fn_input = os.path.abspath(test_folder+"testALPS_lib.xml")
        self.mainWindow.importXML_fromFile(fn_input)
        listLG = self.mainWindow.dlgSelectLG.list_LG_names
        self.assertEqual(listLG.count(), 31)
        cluster = None
        for j in range(listLG.count()):
            listLG.setCurrentItem(listLG.item(j))
            self.assertTrue(self.mainWindow.cluster is not cluster)
            cluster = self.mainWindow.cluster

    def test_ImportCIF(self):
        
        fn_cif = os.path.abspath(test_folder+"test.cif")  
        self.mainWindow.action_ImportCryst.trigger()
        self.dlgImportCryst = self.mainWindow.dlgImportCryst
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
        self.dlgDistSearch.btnSearch.click()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 16)
        # add edges with length 7.55        
        data = {"bool": True, "type":1, "dist":7.55, "err":0.1} 
        lw.itemWidget(lw.item(1)).set_data(data)
        self.dlgDistSearch.btnSearch.click()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 16+4)
        # export to XML lib
        self.ExportXML(os.path.abspath(test_folder+"testLib_output.xml"))        
        # test adding new item
        self.assertEqual(lw.count(), 3)
        self.dlgDistSearch.btnAdd.click()
        self.assertEqual(lw.count(), 4)
        # select edges
        lw.setCurrentItem(lw.item(1))
        self.assertEqual(len(self.mainWindow.gee.e_activeDist_ids), 4)
        lw.setCurrentItem(lw.item(0))
        self.assertEqual(len(self.mainWindow.gee.e_activeDist_ids), 16)
        # delete selected edges
        self.dlgDistSearch.btnRemove.click()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 4)
        # delete more selected edges
        lw.setCurrentItem(lw.item(0))
        self.assertEqual(len(self.mainWindow.gee.e_activeDist_ids), 4)
        self.mainWindow.action_DelEdge.trigger()
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 0)

        self.dlgDistSearch.btnClose.click()

 
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
        
    def test_ExportIMG(self):
    
        self.mainWindow.exportIMG(test_folder+"test.png")
        self.assertTrue(os.path.exists(test_folder+"test.png"))

    def test_resetSize(self):
        
        self.test_ImportXML()
        self.assertEqual(len(self.mainWindow.gee.ax.artists), 1+6+4*4+4*3)
        self.mainWindow.spinBox_sizeL.setValue(3)
        self.assertEqual(len(self.mainWindow.gee.ax.artists), 1+6+4*7+6*3)
        
        self.mainWindow.spinBox_sizeW.setValue(3)
        self.assertEqual(len(self.mainWindow.gee.ax.artists), 1+6+4*12+9*3)
        
        self.mainWindow.spinBox_sizeH.setValue(3)
        self.assertEqual(len(self.mainWindow.gee.ax.artists), 1+6+6*12+9*5)

    def test_changeEdgeType(self):
        
        self.test_ImportXML()
        # select edge from listWidget
        ind, _id = 1, 2
        self.mainWindow.listEdges.setCurrentItem(self.mainWindow.listEdges.item(ind))
        self.assertTrue(self.mainWindow.gee.e_active_ind == _id)

        new_type = 5
        self.mainWindow.spinBox_type.setValue(new_type)
        self.mainWindow.btnChangeType.click()
        self.assertEqual(self.mainWindow.UC.edges[_id].type, new_type)
        
        # test changing the type using menu action and dialog

        # select edge from listWidget
        ind, _id = 2, 3
        self.mainWindow.listEdges.setCurrentItem(self.mainWindow.listEdges.item(ind))
        self.assertTrue(self.mainWindow.gee.e_active_ind == _id)
        current_type = self.mainWindow.UC.edges[_id].type
        # open change type dialog and test cancel
        self.mainWindow.action_ChangeType.trigger()
        self.assertEqual(self.mainWindow.dlg.spinBox_current.value(), current_type)
        self.assertEqual(self.mainWindow.dlg.spinBox_new.value(), current_type)
        new_type = 7
        self.mainWindow.dlg.spinBox_new.setValue(new_type)
        self.mainWindow.dlg.btnCancel.click()
        self.assertEqual(self.mainWindow.UC.edges[_id].type, current_type)
        # open change type dialog and test ok
        self.mainWindow.action_ChangeType.trigger()
        self.assertEqual(self.mainWindow.dlg.spinBox_current.value(), current_type)
        self.assertEqual(self.mainWindow.dlg.spinBox_new.value(), current_type)
        self.mainWindow.dlg.spinBox_new.setValue(new_type)
        self.mainWindow.dlg.btnOk.click()
        self.assertEqual(self.mainWindow.UC.edges[_id].type, new_type)
        
    def test_changeTEXT_MODE(self):
        
        _bool = self.mainWindow.TEXT_MODE
        self.mainWindow.radioButton_output.toggle()
        self.assertTrue(self.mainWindow.TEXT_MODE != _bool)
        self.mainWindow.radioButton_output.toggle()
 

class PreferencesTest(unittest.TestCase):
    '''Test the Preferences manager'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=False)
 
    def test_PrefManager(self):
        
        self.mainWindow.action_Pref.trigger()
        dlgPref = self.mainWindow.dlgPref
        dlgPref.btnDefaults.click()
        edgePref = dlgPref.prefWidget.edgePref
        lw = edgePref.listWidget

        try:
            # compare gee pref and dialog widgets values
            self.assertEqual(lw.count(), 10)
            # edge linewidth
            self.assertAlmostEqual(self.mainWindow.gee.lw, 
                                   edgePref.sliderSize.value()*7/100)
            _type = 4
            data = lw.get_itemData(_type)
            self.assertEqual(self.mainWindow.gee.colors_e[_type], data["color"])
            self.assertEqual(self.mainWindow.gee.visible_e[_type], data["bool"])
            
            #change theme but not apply
            dlgPref.comboBox.setCurrentIndex(2)
    
            _type = 4
            data = lw.get_itemData(_type)
            data['bool'] = False
            lw.set_itemData(_type, data)
            self.assertNotEqual(self.mainWindow.gee.colors_e[_type], data["color"])
            self.assertNotEqual(self.mainWindow.gee.visible_e[_type], data["bool"])
            
            # add new preference item to the list
            edgePref.btnAdd.click()
            self.assertEqual(lw.count(), 11)
            _type = 10
            data = lw.get_itemData(_type)
            
            # Apply and check changes in gee prefs
            dlgPref.btnApply.click()
            self.assertEqual(self.mainWindow.gee.colors_e[_type], data["color"])
            self.assertEqual(self.mainWindow.gee.visible_e[_type], data["bool"])
        
        finally:
            dlgPref.btnDefaults.click()
            # check changes
            dlgPref.btnClose.click()


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
        path = os.path.abspath(test_folder+"test")
        self.dlgExportAnim.lineEdit_name.setText(path)
        self.dlgExportAnim.btnExport.click()
        self.assertTrue(os.path.exists(test_folder+"test.gif")
                        or os.path.exists(test_folder+"test.mp4"))

        self.dlgExportAnim.btnClose.click()
        


class CodeEditorTest(unittest.TestCase):
    '''Test the Animation manager'''
    def setUp(self):
        '''Create the GUI'''
        self.mainWindow = MainWindow(TEXT_MODE=True)
      
    def test_CodeEditor(self):
        
        self.mainWindow.action_EditXML.trigger()

        # insert xml data from another lib and apply
        fn = os.path.abspath(test_folder+'triangular_network.xml')
        with open(fn) as f:
            self.mainWindow.dlgEditXML.codeEditor.setPlainText(f.read())        

        self.mainWindow.dlgEditXML.buttonBox.button(QDialogButtonBox.Apply).click()
        # check changes in main window
        self.assertEqual(self.mainWindow.cluster.UC.num_vertices, 96)
        self.assertEqual(self.mainWindow.cluster.UC.num_edges, 288)

        self.mainWindow.dlgEditXML.buttonBox.button(QDialogButtonBox.Close).click()
        
    def test_edge_selection(self):
                        
        self.mainWindow.action_EditXML.trigger()

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
    
