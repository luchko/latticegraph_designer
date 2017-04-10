#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 18:13:18 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

This module contains the definition of the matplotlib manipulation pane.
    
    class Arrow3D(FancyArrowPatch):
    class Annotation3D(Annotation):
    class GraphEdgesEditor(object):
        
testing and examples:
    
    def run_test():
        
"""

from __future__ import division # make python 2 use float division

import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3D
from mpl_toolkits.mplot3d.proj3d import proj_transform
from matplotlib.mlab import dist_point_to_segment
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.text import Annotation
from matplotlib.colors import hex2color


from latticegraph_designer.app.core import DealXML
import xml.etree.ElementTree as ET


class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)


class Annotation3D(Annotation):
    def __init__(self, label, xyz, *args, **kwargs):
        Annotation.__init__(self,label, xy=(0,0), *args, **kwargs)
        self._verts3d = xyz        
    
    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.xy=(xs,ys)
        Annotation.draw(self, renderer)
                

class GraphEdgesEditor(object):
    """
 #########################################################################
 ##                                                                     ##
 ##  3D drag-and-drop graph edges editor.                               ##
 ##                                                                     ##
 ##     * In order to create a new edge pick the source vertex          ##
 ##       and drag the pointer towards the targtet vertex               ##
 ##                                                                     ##
 ##     * One left mouse button click selects the edge                  ##
 ##                                                                     ##
 ##     * Hold righ mouse button and move pointer up/down for zooming   ##
 ##                                                                     ##
 ##     * Usefull key-bindings:                                         ##
 ##         'Ctrl+NumKey' - change the type of active edge to NumKey    ##     
 ##         'Shift+Del' - delete all edges                              ##
 ##         'Del' - delete selected active edge                         ##     
 ##         't' - Switch on/off displaying manipulation actions into    ## 
 ##               terminal window.                                      ##
 ##         'n' - switch on/off displaying of the lattice               ##
 ##         'm' - switch on/off displaying of the unit cell arrows      ##
 ##                                                                     ##
 ##     * Close manipulation window in order to finish editing          ##
 ##                                                                     ##
 #########################################################################
    """
    
    buttonHold = False # the no hold button event so lets create one
    isRotated = False # True when axes3D is rotated
    USE_COLLECTIONS = False # use Line3DCollection for edge representation
    
    def __init__(self, ax, cluster, parent=None, display_report=False):
        '''
        input:
            xyz: Nx3 numpy array containing vertices coordinates
            edges_ind: list of tuples containing indexes of source and target 
                points which form the edge: e.g. [(s1,t1),(s2,t2),...]
            display_report: if 'True' Docstring and all additing actions are
                            displayed                           
            display_lattice: if 'True' display lattice of the classter
            display_arrows: if 'True' display unit cell arrows
        '''        
        
        self.parent = parent        
        
        self.ax = ax
        self.ax.set_axis_off()
        self.ax.figure.tight_layout()
        self.canvas = self.ax.figure.canvas        

        # create bindings
        self.cluster = cluster
        self.UC = cluster.UC
        self.edges = cluster.edges
        self.vertices = cluster.vertices
  
        # other elements
        self.display_report = display_report
        
        # initialize theme
        if parent is None:        
            self.prefFileName = "./latticegraph_designer/resources/preferences.xml"
            self.SETTINGS = ET.parse(self.prefFileName).getroot()
            self.CURRENT_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME","Current theme") 
        else: # create bindings
            self.prefFileName = self.parent.prefFileName
            self.SETTINGS = self.parent.SETTINGS
            self.CURRENT_THEME = self.parent.CURRENT_THEME
            
        self.initialize_theme(self.CURRENT_THEME)
        
        # create artists
        self.edges_lines, self.sc, self.latticeNet = None, None, None
        self.create_artists_graph()
        self.create_artists_highlight()
        self.create_artists_arrows()

        self.set_artists_properties()
        
        # canvas event bindings         
        self.canvas.mpl_connect('draw_event', self.draw_callback)
        self.canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas.mpl_connect('button_press_event', self.button_press_callback)
        self.canvas.mpl_connect('button_release_event', self.button_release_callback)
        self.canvas.mpl_connect('key_press_event', self.key_press_callback)

        # hotkey list used for changing edge type
        self.ctrl_list = ["ctrl+{}".format(n) for n in range (len(self.colors_e))]
                
    def initialize_theme(self, theme_ET):
        '''Initilaize widget theme and preferences'''
        
        self.CURRENT_THEME = theme_ET        
        
        self.display_arrows = theme_ET.find("VISIBLEARROWS").get("value") == "True"
        self.display_lattice = theme_ET.find("VISIBLELATTICE").get("value") == "True"

        self.color_background = theme_ET.find("COLORBACKGROUND").get("value")
        self.color_lattice = theme_ET.find("COLORLATTICE").get("value")
        self.color_active = theme_ET.find("COLORACTIVATE").get("value")

        dic1, dic2 = {}, {}
        for dic, elem in zip([dic1, dic2],[theme_ET.find("EDGES"),theme_ET.find("VERTICES")]):
            dic["bool"], dic["color"] = [], []
            dic["size"] = float(elem.find("SIZE").get("size"))
            for pref in elem.findall("PREFERENCE"):
                dic["bool"].append(pref.get("bool") == "True")
                dic["color"].append(pref.get("color"))
        
        self.colors_e = np.array(dic1['color']*20)
        self.visible_e = np.array(dic1['bool']*20, dtype=bool)
        self.lw = dic1["size"]*7/100
        self.lw_active = self.lw*1.7
        
        self.colors_v = np.array(dic2['color']*20)
        self.visible_v = np.array(dic2['bool']*20, dtype=bool)
        self.sc_size = dic2["size"]*20/100
        self.sc_size_active = self.sc_size*1.7
                      
    def adjust_scale(self):
        '''hack requirired for ajusting sclale in matplotlib axes3D'''
        
        if self.display_lattice:
            L,W,H = self.cluster.size
            sitesCoord = self.cluster.lattice.get_finite_lattice_sites((L+1,W+1,H+1))
            lims_max = np.max(sitesCoord,axis=0) 
            lims_min = np.min(sitesCoord,axis=0) 
        else:
            lims_max = np.max(self.vertices.coords,axis=0) 
            lims_min = np.min(self.vertices.coords,axis=0) 
            
        x0, y0, z0 = (lims_max+lims_min)/2
        delta = max(lims_max-lims_min)/2
                    
        self.ax.set_xlim3d(x0-delta,x0+delta)        
        self.ax.set_ylim3d(y0-delta,y0+delta)        
        self.ax.set_zlim3d(z0-delta,z0+delta)       
    
    def create_artists_graph(self):
        '''create and add to self.ax main artrist related to lattice graph'''
                
        # initialize vertices
        self.xyz = self.vertices.coords
        self.x, self.y, self.z = self.xyz.T
        self.update_XY_scr()      
                
        # create vertices
        if self.sc is not None: # remove previous vertices points
            self.ax.collections.remove(self.sc)
 
        self.sc = self.ax.scatter(self.x,self.y,self.z, marker='o')

        # create edges
        if self.USE_COLLECTIONS:
            if self.edges_lines is not None: # remove previous edges lines
                for key, edge_col in self.edges_lines.items():
                    self.ax.collections.remove(edge_col)
            
            self.edges_lines = {}
            for key, edge in self.UC.edges.items():
                segments = [self.xyz[self.edges.source_target[j],:] for j in self.edges.array_ind[key]]
                edge_col = Line3DCollection(segments) 
                self.ax.add_collection3d(edge_col)
                self.edges_lines[key] = edge_col
        else:
            if self.edges_lines is not None: # remove previous lines edges
                for line in self.edges_lines:
                    self.ax.artists.remove(line)
            
            self.edges_lines = []
            for j in range(len(self.edges.ids)):
                st = list(self.edges.source_target[j])
                line = Line3D(self.x[st], self.y[st], self.z[st])
                self.ax.add_artist(line)
                self.edges_lines.append(line)
            
        # create latticeNet
        if self.latticeNet is not None:  # remove previous lattice lines
            self.ax.collections.remove(self.latticeNet)
        self.latticeNet = Line3DCollection(self.cluster.latticeLines, 
                                           linestyle = '--', lw=0.2)
        self.ax.add_collection3d(self.latticeNet)
        
        self.v_source_ind, self.v_target_ind = None, None
        self.v_ind, self.v_active_ind = None, None
        self.e_ind, self.e_active_ind = None, None
        self.e_activeDist_ids = []     

    def create_artists_highlight(self):            
        ''' creates artists used to higlight active elements'''
        
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.sc_active = self.ax.plot([],[],[], animated=True, marker='o')[0]
        self.new_edge = Line3D([], [], [], color=self.color_active,
                               lw=self.lw, animated=True)
        self.ax.add_artist(self.new_edge)      
            
    def create_artists_arrows(self):
        '''create and add unit cell arrows artists'''
        
        self.arrows = []
        v0 = self.cluster.arrowVec[0,:] #origin
        for v, label in zip(self.cluster.arrowVec[1:,:],['a','b','c']):
            # create arrow
            a = Arrow3D([v0[0], v[0]], [v0[1], v[1]], [v0[2], v[2]], 
                        mutation_scale=10, arrowstyle="simple")
            self.ax.add_artist(a)
            self.arrows.append(a)
            # create label
            tag = Annotation3D(label,xyz=v,xytext=(-4,4),textcoords='offset points',
                               ha='right',va='bottom')
            self.ax.add_artist(tag)
            self.arrows.append(tag)

    def set_artists_properties(self):
        '''setup properties of lattice graph according to self.CURRENT_THEME'''
        
        # set background, lattice net and arrows
        self.ax.patch.set_facecolor(self.color_background)
        self.ax.figure.patch.set_facecolor(self.color_background)
        self.latticeNet.set_visible(self.display_lattice)        
        self.latticeNet.set_color(self.color_lattice)
        self.adjust_scale()
        self.set_visible(self.arrows,self.display_arrows)
        for elem in self.arrows:
            elem.set_color(self.color_lattice)

        # set props of the vertices
        colors = [list(hex2color(c))+[1] for c in self.colors_v[self.vertices.types]]
        self.sc._facecolor3d = colors
        self.sc._edgecolor3d = colors
        self.sc.set_sizes([self.sc_size**2]*len(self.vertices.types))
            
        # set props of the edges colentions
        if self.USE_COLLECTIONS:
            for key, edge_col in self.edges_lines.items():
                edge_col.set_color(self.colors_e[self.UC.edges[key].type])
                edge_col.set_visible(self.visible_e[self.UC.edges[key].type])
                edge_col.set_linewidth(self.lw)
        else:
            for j in range(len(self.edges.ids)):
                self.edges_lines[j].set_color(self.colors_e[self.edges.types[j]])
                self.edges_lines[j].set_visible(self.visible_e[self.edges.types[j]])
                self.edges_lines[j].set_linewidth(self.lw)
                            
        # set activation elements and new_edge      
        self.sc_active.set_markersize(self.sc_size_active)
        self.sc_active.set_color(self.color_active)
        self.new_edge.set_linewidth(self.lw_active)
        self.new_edge.set_color(self.color_active)       

        self.canvas.draw()           

    def reset_size(self, size):
        '''resize the displayed lattice cluster'''
        
        self.cluster.reset_size(size)
        self.create_artists_graph()
        self.adjust_scale()
        self.set_artists_properties()        
                        
 
    def update_XY_scr(self):
        '''returns projection of the vertices on the screen space'''
        
        # project 3d data space to 2d data space        
        self.xd, self.yd, _ = proj_transform(self.x,self.y,self.z,
                                             self.ax.get_proj())
        # convert 2d space to screen space
        self.x_scr, self.y_scr = self.ax.transData.transform(
                np.vstack((self.xd, self.yd)).T).T
        
    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        
        d = np.sqrt((self.x_scr - event.x)**2 + (self.y_scr - event.y)**2)
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]
        ind = indseq[0]       
        if d[ind] >= self.sc_size:
            ind = None
            
        return ind
        
    def getMouseXYZ(self, event):
        '''return xyz of the mouse in 3D space (like in coord_string)'''
        
        s = self.ax.format_coord(event.xdata, event.ydata)
        
        return tuple(float(a[a.find('=')+1:]) for a in s.split(','))   

    def draw_callback(self, event):
        '''on canvas draw'''
        
        if not self.isRotated:    
            self.update_XY_scr() 

        # store background for blitting
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
            

    def motion_notify_callback(self, event):
        'on mouse movement'
    
        if event.inaxes is None:
            return
        
        # when axes3D is rotated
        if self.buttonHold and (self.v_source_ind is None):
            self.isRotated = True                       
            return 
        
        self.v_ind = self.get_ind_under_point(event)

        # activation/deactivation of vertex
        if self.v_ind != self.v_active_ind: # not the same or both None
            self.v_active_ind = self.v_ind

            if self.v_source_ind is None: 
                self.canvas.restore_region(self.background)
            # else background would be restored during new edge redrawing
            if self.v_active_ind is not None: # activation (color)
                self.sc_active.set_data(self.x[self.v_active_ind],
                                        self.y[self.v_active_ind])
                self.sc_active.set_3d_properties(self.z[self.v_active_ind])
                self.ax.draw_artist(self.sc_active)
            
            self.canvas.blit(self.ax.bbox)
            
        if self.v_source_ind is not None: #redraw potential edge line            
            xm,ym,zm = self.getMouseXYZ(event)                                    
            self.canvas.restore_region(self.background_newEdgeDrawing) 
            self.new_edge.set_data([[self.x[self.v_source_ind], xm],
                                    [self.y[self.v_source_ind], ym]])
            self.new_edge.set_3d_properties([self.z[self.v_source_ind], zm])
            self.ax.draw_artist(self.new_edge)
            if self.v_active_ind is not None:
                self.ax.draw_artist(self.sc_active)
            self.canvas.blit(self.ax.bbox)
            
    def button_press_callback(self, event):
        'whenever a mouse button is pressed'
        
        if event.inaxes is None:
            return
        
        self.buttonHold = True
                
        # source selection
        if self.v_active_ind is not None:
            self.v_source_ind = self.v_active_ind
            self.ax.mouse_init(rotate_btn=2) # disable mouse rotation
            self.background_newEdgeDrawing = self.canvas.copy_from_bbox(self.ax.bbox)
            return
        
        # edge selection
        p = event.x, event.y  # display coords
        for i in range(len(self.edges.source_target)):
            (s, t) = self.edges.source_target[i]
            d = dist_point_to_segment(p, (self.x_scr[s],self.y_scr[s]),
                                      (self.x_scr[t],self.y_scr[t]))
            if d <= self.lw_active:                
                self.select_edge(self.edges.ids[i])
                if self.parent is not None:
                    self.parent.selectedEdgeChanged.emit(self.e_active_ind)
                elif self.display_report:
                    print(" selected edge: {}".format(self.UC.edges[self.e_active_ind]))

                return
            
        self.e_ind = None

    def button_release_callback(self, event):
        'whenever a mouse button is released'
                
        if self.v_source_ind is not None: # new Edge was Drawing     
            self.ax.mouse_init(rotate_btn=1) # enable mouse rotation            
            # check if new edge was created
            if (self.v_active_ind is None) or \
               (self.v_active_ind == self.v_source_ind):          
                self.v_source_ind = None
                self.canvas.restore_region(self.background)
                self.canvas.blit(self.ax.bbox)           
            else:
                self.v_target_ind = self.v_active_ind
                self.add_edge()            
                self.canvas.draw()
            
        elif self.isRotated: # Axes3D was rotated
            self.update_XY_scr()
            self.isRotated = False
            
        # Axes3D was not rotated             
        # deactivate active edge if no new edge is selected
        elif self.e_ind is None and self.e_active_ind is not None:  
            color = self.colors_e[self.UC.edges[self.e_active_ind].type]
            self.reset_active_e_color(color, self.lw)                    
            self.e_active_ind = None
            if self.parent is not None:
                self.parent.selectedEdgeChanged.emit(self.e_active_ind)
            elif self.display_report:
                print(" active edge unselected")                    
                
        self.buttonHold = False
            
    def set_visible(self, elements_list, boolVisible):
        '''set visibility of artists in elements_list'''
        
        for elem in elements_list:
            elem.set_visible(boolVisible)   

    def reset_e_color(self, ind, color, lw):
        '''reset the color of selected edge'''
        
        if self.USE_COLLECTIONS:
            self.edges_lines[ind].set_color(color)  
            self.edges_lines[ind].set_linewidth(lw)  
        else:
            for j in self.edges.array_ind[ind]:             
                self.edges_lines[j].set_color(color)
                self.edges_lines[j].set_linewidth(lw)

    def reset_active_e_color(self, color, lw):
        '''reset the color of selected active edge'''        

        self.reset_e_color(self.e_active_ind, color, lw)
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def select_edge(self, ind):
        '''select (ativate) edge with index ind'''

        self.e_ind = ind
        if self.e_active_ind is not None: # deactivate previouse
            color = self.colors_e[self.UC.edges[self.e_active_ind].type]
            self.reset_active_e_color(color, self.lw)
        self.e_active_ind = self.e_ind # activate new edge
        if ind is not None:
            self.reset_active_e_color(self.color_active, self.lw_active)                

    def select_edges(self, ids):
        '''select (ativate) edge with index in ids list'''
                    
        for ind in self.e_activeDist_ids: # deactivate previouse
            color = self.colors_e[self.UC.edges[ind].type]
            self.reset_e_color(ind, color, self.lw)

        self.e_activeDist_ids = ids # activate new edge
        self.e_ind = None if len(ids) == 0 else ids[0]
        self.e_active_ind = self.e_ind
        for ind in ids:
            self.reset_e_color(ind, self.color_active, self.lw_active)
            
        self.canvas.draw()
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)              

    def change_active_edge_type(self, new_type):
        '''change selected adge type'''

        if self.e_active_ind is not None:
            old_type = self.UC.edges[self.e_active_ind].type
            
            if len(self.e_activeDist_ids) == 0:
                self.edges.change_edge_type(self.e_active_ind, new_type)
                msg = ' type of the edge id={0} was changed from {1} to {2}'.format(
                        self.e_active_ind, old_type, new_type)
                
                #self.reset_active_e_color(self.colors_e[new_type], self.lw)            
                #self.e_active_ind = None
            else:
                for ind in self.e_activeDist_ids:
                    self.edges.change_edge_type(ind, new_type)
                msg = ' type of the edges was changed from {1} to {2}'.format(
                        self.e_active_ind, old_type, new_type)
                                            
            if self.display_report:
                print(msg)

            if self.parent is not None:
                self.parent.unitCellChanged.emit()
                self.parent.selectedEdgeChanged.emit(self.e_active_ind)
            
    def add_edge(self):
        '''create new edge (or not if condition is not fulfilled)'''
        
        newEdge_id = self.edges.add_edge(self.v_source_ind,self.v_target_ind)
                
        if newEdge_id is not None:
            
            if self.USE_COLLECTIONS:
                segments = [self.xyz[self.edges.source_target[j],:] for j in self.edges.array_ind[newEdge_id]]
                new_edge_col = Line3DCollection(segments,color=self.colors_e[0],lw=self.lw) 
                self.ax.add_collection3d(new_edge_col)
                self.edges_lines[newEdge_id] = new_edge_col
            else:
                for j in self.edges.array_ind[newEdge_id]:
                    edge = self.edges.source_target[j]
                    st = list(edge)
                    line = Line3D(self.x[st], self.y[st], self.z[st], 
                                  color = self.colors_e[0], lw=self.lw)
                    self.ax.add_artist(line)
                    self.edges_lines.append(line)
            
            # deactivate previous active edge
            if self.e_active_ind is not None:
                color = self.colors_e[self.UC.edges[self.e_active_ind].type]
                self.reset_active_e_color(color, self.lw)

            self.e_active_ind = newEdge_id # activate new edge
            self.reset_active_e_color(self.color_active, self.lw_active)

            if self.display_report:
                print(' added edge: {}'.format(self.UC.edges[newEdge_id]))

            if self.parent is not None:
                self.parent.unitCellChanged.emit()
                self.parent.selectedEdgeChanged.emit(self.e_active_ind)              
               
        self.v_source_ind = None 
        self.v_target_ind = None 

    def delete_edge_callback(self, _id):
        '''deleted edge with _id'''

        if self.edges.array_ind.get(_id) is None:
            return
        if len(self.edges.array_ind.get(_id)) == 0:
            self.edges.remove_edge(_id)
            return
            
        #remove from both list                
        if self.USE_COLLECTIONS:
            self.ax.collections.remove(self.edges_lines[_id])
            del self.edges_lines[_id]
        else:
            for j in self.edges.array_ind[_id]:             
                self.ax.artists.remove(self.edges_lines[j])                    
            begin = self.edges.array_ind[_id][0]
            end = self.edges.array_ind[_id][-1]
            self.edges_lines[begin:end+1] = []
                       
        self.edges.remove_edge(_id)

    def delete_active_edge_callback(self):
        '''deleted selected (active) edge'''

        if self.e_active_ind is not None:
            if len(self.e_activeDist_ids) == 0:
                msg = " deleted edge: {}".format(self.UC.edges[self.e_active_ind])
                self.delete_edge_callback(self.e_active_ind)
            else:
                activeDist = self.UC.edges[self.e_activeDist_ids[0]].length
                numActDist = len(self.e_activeDist_ids)
                msg = " deleted {0} edges with length: {1}".format(numActDist, activeDist)
                for ind in self.e_activeDist_ids[:]:
                    self.delete_edge_callback(ind)                
                        
            if self.display_report:
                print(msg)
              
            self.e_activeDist_ids = []
            self.e_active_ind = None            
            self.canvas.draw()        
            
            if self.parent is not None:
                self.parent.statusBar().showMessage(msg, 2000)
                self.parent.unitCellChanged.emit()
                self.parent.selectedEdgeChanged.emit(None)
            
    def clearEdges_callback(self):
        '''delete all edges''' 
        
        self.UC.clearEdges()
        self.cluster.edges.process_edges(self.cluster.size)
        self.create_artists_graph()
        self.set_artists_properties()
        msg = " all edges are deleted"
        
        if self.display_report:
            print(msg)
        
        self.e_activeDist_ids = []
        self.e_active_ind = None            
        self.canvas.draw() 
        
        if self.parent is not None:
            self.parent.statusBar().showMessage(msg, 2000) 
            self.parent.unitCellChanged.emit()
            self.parent.selectedEdgeChanged.emit(None)
               
    def searchActiveDistEdge_callback(self):
        '''search for edges with the same length as selected (active)'''
        
        if self.e_active_ind is None:
            print(' For search by distance please select a sample edge')
        else:
            self.searchDistEdge_callback(self.e_active_ind)
            self.e_active_ind = None
                    
    def searchDistEdge_callback(self, ind):
        '''search for edges with the length as edge with id=ind'''

        self.edges.search_similar_edges(self.UC.edges[ind])                
        self.create_artists_graph()
        self.set_artists_properties()
        
        # show message                        
        dist = self.UC.edges[ind].length
        num = len(self.UC.lengthDic[dist])
        msg = ' {0} edges were found with dist={1:.3f}'.format(num,dist)    
        if self.display_report:
            print(msg)
        
        if self.parent is not None:
            self.parent.unitCellChanged.emit()
            self.parent.selectedEdgeChanged.emit(None)
            self.parent.statusBar().showMessage(msg, 2000)
            
    def key_press_callback(self, event):
        '''create key-bindings'''
        
        if event.key in self.ctrl_list: # change edge type
            new_type = self.ctrl_list.index(event.key)
            self.change_active_edge_type(new_type)

        elif event.key == 'delete':
            self.delete_active_edge_callback()
                                                        
        elif event.key == 'shift+delete':
            self.clearEdges_callback()

        elif event.key == 'ctrl+d':    
            self.searchActiveDistEdge_callback()

        elif event.key == 't': # change displaying report settings
            self.display_report = not self.display_report
            # bind to parent
            if self.parent is not None:
                self.parent.TEXT_MODE = self.display_report
                self.parent.radioButton_output.setChecked(self.display_report)
            else:
                print(" displaying actions in terminal is turned {}".format("on" if self.display_report else "off"))

        elif event.key == 'n': # change displaying lattice net settings 
            self.display_lattice = not self.display_lattice
            self.latticeNet.set_visible(self.display_lattice)        
            self.adjust_scale()
            
            self.CURRENT_THEME.find("VISIBLELATTICE").set("value",str(self.display_lattice))
            ET.ElementTree(self.SETTINGS).write(self.prefFileName)
            
            # bind to parent
            if self.parent is not None:
                self.parent.latticeVisibleChanged.emit(self.display_lattice)
            
            if self.display_report:
                if self.display_lattice:                
                    print(' Lattice net enabled')
                else:
                    print(' Lattice net disabled')
                    
            self.canvas.draw()
            
        elif event.key == 'm': # change displaying arrows settings
            self.display_arrows = not self.display_arrows
            self.set_visible(self.arrows,self.display_arrows)           
            self.canvas.draw()            
            
            self.CURRENT_THEME.find("VISIBLEARROWS").set("value",str(self.display_arrows))
            ET.ElementTree(self.SETTINGS).write(self.prefFileName)
            
            # bind to parent
            if self.parent is not None:
                self.parent.arrowsVisibleChanged.emit(self.display_arrows)
                
            if self.display_report:
                if self.display_arrows:                
                    print(' Unit cell arrows enabled')
                else:
                    print(' Unit sell arrows disabled')


#############################################################################            


if __name__ == '__main__':

    def run_test():
        '''testing GraphEdgesEditor'''
        
        from core import Vertex, Edge, UnitCell, Lattice, CrystalCluster
        import matplotlib.pyplot as plt
        import numpy as np    
        
        lattice = Lattice(basisMatrix=np.array([[1,0,0],[0.1, 1.2,0],[0.05,0.05,1]]).T)
        
        UC = UnitCell()
        UC.add_vertex(Vertex(0,0,[0.2,0.2,0.2]))
        UC.add_vertex(Vertex(0,0,[0.3,0.3,0.6]))
        UC.add_edge(Edge(0,1,(1,2),(0,0,0)))
        UC.add_edge(Edge(0,2,(2,1),(0,0,1)))
        UC.add_edge(Edge(0,0,(1,1),(1,0,0)))
        UC.add_edge(Edge(0,0,(1,1),(0,1,0)))
        UC.add_edge(Edge(0,0,(2,2),(1,0,0)))
        UC.add_edge(Edge(0,0,(2,2),(0,1,0)))
        
        cluster = CrystalCluster(UC,lattice,(2,2,2))
    
        fig = plt.figure('Graph edges editor', figsize=(5,5), dpi=100)
        ax = fig.gca(projection='3d')  # same as ax = Axes3D(fig)
    
        display_report = True
        gee = GraphEdgesEditor(ax, cluster, display_report=display_report)
        
        print(gee.__doc__)
    
        if display_report:
            print('\n======================================')
            print('# Start editting editing: \n')
            print('Initial UC:\n{}'.format(cluster.UC))
            print('Editing actions:')
        
        plt.show(block=True)
     
        if display_report:
            print('\nEdited UC:\n{}'.format(cluster.UC))
            print('======================================\n')
                        
                    
    run_test()