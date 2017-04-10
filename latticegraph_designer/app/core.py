#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 21:17:12 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

This module contains the definition of core classes:
    
    class Vertex(object):
    class Edge(object):
    class Lattice(object):
    class UnitCell(object):
    class ClusterVertices(object):
    class ClusterEdges(object):
    class CrystalCluster(object):
    class DealXML(object):
    class ParseXML(object):
    class ExportXML(object):

"""

from __future__ import division # make python 2 use float division

import numpy as np
import itertools
import xml.etree.ElementTree as ET
from xml.dom import minidom
from math import *

        
class Vertex(object):
    '''Vertex class'''
    
    def __init__(self,  _id=0, _type=0, coordinates=[0,0,0]):
        
        self.id = int(_id)
        self.type = int(_type)
        self.coords = np.array(coordinates) #np.array
        	
    def __str__(self):
    
        return "[{0},{1},{2}]".format(self.id,self.type,self.coords)
	
	
class Edge(object):
    '''Edge class'''
    
    def __init__(self, _id=0, _type=0, source_target=(0,0), offset=[0,0,0]):
        
        self.id = int(_id)
        self.type = int(_type)
        self.source, self.target = source_target # tuple of Vertex ids
        self.offset = np.array(offset, dtype = int)  # tuple or np.array
        self.length = None
    
    def standart_form(self):
        '''brings edge to the standart from'''
        
        if np.sum(np.abs(self.offset)) == 0:
            if self.source > self.target:
                self.source, self.target = self.target, self.source
        else:
            for j in range(3):
                if self.offset[j] < 0:
                    self.source, self.target = self.target, self.source
                    self.offset = -self.offset
                    break
                elif self.offset[j] > 0:
                    break
    
    def recompute_length(self, UC, lattice):
        '''compute Euclidian length of edges with given lattice'''
        
        sourceCoord = lattice.convert_to_Cartesian(UC.vertices[self.source].coords)
        targetCoord = lattice.convert_to_Cartesian(UC.vertices[self.target].coords + self.offset)
        self.length =  round(np.linalg.norm(targetCoord-sourceCoord), 4)
        
        return self.length
        
    def __str__(self):
        
        s  = "[{0},{1},({2},{3}),{4}]".format(self.id, self.type, self.source,
                                             self.target,self.offset)
        if self.length is not None:
            s += " - {0:.3f}".format(self.length)

        return s


class Lattice(object):
    '''lattice class'''
    
    def __init__(self, basisMatrix=np.eye(3), **kwargs):
        '''
        basis is defined by basisMatrix 3x3 numpy array
        
        in case lattice parameters ("cell_lengths" and "angles") are provided 
        as **kwargs, basisMatrix is calculated based on this data

        '''
        self.atrib={}
        self.atrib["name"] = "myLattice"
        self.atrib["dimension"] = "3"
        self.atrib["BOUNDARY"] = "periodic"
        self.atrib.update(kwargs)
                  
        keys = kwargs.keys()
        if 'cell_lengths' in keys and 'angles' in keys:
            self.basisMatrix = self.build_basisMatrix(kwargs.get("cell_lengths"), 
                                                      kwargs.get("angles"))
        else:
            self.basisMatrix = basisMatrix
            self.a, self.b, self.c = np.linalg.norm(basisMatrix, axis = 0)
            self.alpha = self.angle_between(basisMatrix[:,1],basisMatrix[:,2])
            self.beta = self.angle_between(basisMatrix[:,0],basisMatrix[:,2])
            self.gamma = self.angle_between(basisMatrix[:,0],basisMatrix[:,1])
            
    def build_basisMatrix(self, cell_lengths, angles):
        '''
        build basisMatrix based on unit cells length a,b,c and angles:
        input:
            cell_length: np.array([a,b,c])
            angles: np.array([alpha=b^c, beta=a^c, gamma=a^b]) in degrees
        return:
            basisMatrix: 3x3 np.array with basis vectors in columns
        
        '''
        self.a, self.b, self.c = a, b, c = cell_lengths
        self.alpha,self.beta,self.gamma = alpha,beta,gamma = np.deg2rad(angles)
        basisMatrix = np.zeros((3,3))
        basisMatrix[:,0] = [a, 0, 0]
        basisMatrix[:,1] = [b*np.cos(gamma), b*np.sin(gamma), 0]
        basisMatrix[:,2] = [c*np.cos(beta), c*np.cos(alpha), 
                            c*np.sqrt((1-np.cos(alpha)-np.cos(beta))**2)]
        
        return np.round(basisMatrix,10)

    def unit_vector(self, vector):
        ''' Returns the unit vector of the vector.'''
        return vector / np.linalg.norm(vector)
    
    def angle_between(self, v1, v2):
        '''Returns the angle in radians between vectors 'v1' and 'v2'''
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))    

    def convert_to_Cartesian(self, coords):
        '''
        converts coordinates (defined in UC) into Cartesian space 
        according to Lattice basis
        
        input: coords - array([x,y,z])
        
        '''
        return np.dot(self.basisMatrix, coords)
   
    def get_finite_lattice_sites(self, size=(1,1,1)):
        '''
        input: size = (L,W,H) - size of finite lattice
        
        returns: 3x(L*W*H) numpy array - lattice sites of the finite 
        
        '''
        try:
            L,W,H = size
        except ValueError:
            print('Size should has 3 dimensions')
        
        count = 0
        sitesCoord = np.zeros((L*W*H,3))
        for site in itertools.product(range(L),range(W),range(H)):
            sitesCoord[count,:] = np.dot(self.basisMatrix, site)
            count += 1
        
        return sitesCoord  


class UnitCell(object):
    '''Unit cell class'''

    def __init__(self, lattice=Lattice(), **kwargs):
        '''lattice is used for calculating edges length'''
		
        self.lattice = lattice
       
        self.atrib={}
        self.atrib["name"] = "myUC"
        self.atrib["dimension"] = "3"
        self.atrib.update(kwargs)

        self.vertices = {}
        self.edges = {}
        self.lengthDic = {}
        self.num_vertices = 0
        self.num_edges = 0
        self.new_id = 1
          
    def add_vertex(self, vertex):
        '''Add vertex to unit cell'''
        
        vertex.id = self.num_vertices+1
        self.vertices[vertex.id] = vertex	
        self.num_vertices += 1        
	
    def add_edge(self, edge, RECOMPUTE_LENGTH=True):
        '''add edge to the UC and returns its id or None if edge is duplicate'''
        
        edge.standart_form()
    
        if self.is_duplicate(edge): #check if edge is not duplicate:
            return None
        else:       
            edge.id = self.new_id
            self.edges[edge.id] = edge	
            self.num_edges += 1
            self.new_id += 1
            
            if RECOMPUTE_LENGTH:
                edge.recompute_length(self, self.lattice)

            if self.lengthDic.get(edge.length) is None:
                self.lengthDic[edge.length] = [edge.id]
            else:
                self.lengthDic.get(edge.length).append(edge.id)
                            
            return edge.id

    def is_duplicate(self,new_edge):        
        '''checks if edge already exist in edges container'''
        
        for key, edge in self.edges.items():
            if new_edge.source == edge.source and\
               new_edge.target == edge.target and\
               tuple(new_edge.offset) == tuple(edge.offset):
                   return True               

        return False		

    def remove_edge(self, _id):
        '''Removes edge with _id'''
        
        edge = self.edges[_id]
        ids = self.lengthDic[edge.length]
        ids.remove(_id)
        if len(ids) == 0:
            del self.lengthDic[edge.length]
            
        del self.edges[_id]
        self.num_edges -= 1
        
    def clearEdges(self):
        self.edges = {}
        self.lengthDic = {}
        self.num_edges = 0
        self.new_id = 1

    def get_min_ndigits(self, site):
        '''returns the minimum number of digits after dot for list of floats'''
        
        numbers = [str(val) for val in site]
        return max([len(x[x.find('.')+1:]) for x in numbers])
    
    def apply_symops(self, site, symops_list):
        '''
        Returns list of atoms coordinates defined by the given 
        site coordinates and list of symetry operation
        
        input: site - [x,y,z]
               symops_list - [['x','y','z'], ['-y','-x+1/2','z'], ...]
        
        returns: sites - [[x1,y1,z1],...]
        '''
        ndigits=self.get_min_ndigits(site)    
        sites = [tuple(round(coord%1,ndigits) for coord in site)]
        dic = {} 
        for symop in symops_list:
            for site0 in sites[:]:
                dic['x'], dic['y'], dic['z'] = site0
                new_site = tuple(round(eval(new,dic)%1,ndigits) for new in symop)        
                if new_site not in sites:
                    sites.append(new_site)                        
        return sites
    
    def add_vertices_using_symops(self, sites, symops_list, ASSIGN_DIFF_TYPES=True):
        '''
        defines and adds vertives by given list of sites coordinates and
        list of space group symetry operations (list of strings):
            
        input: sites - [[x1,y1,z1],...]
               symops_list - [['x','y','z'], ['-y','-x+1/2','z'], ...]
               ASSIGN_DIFF_TYPES = True assign different types fro each site
        
        '''
        self.vertices = {}        
        for v_type,site in enumerate(sites):
            if ASSIGN_DIFF_TYPES == False:
                v_type = 0
            sym_sites = self.apply_symops(site, symops_list)
            for site0 in sym_sites:
                self.add_vertex(Vertex(self.num_vertices,v_type,site0))
    
    def compute_edgesLength(self, lattice):
        '''compute Euclidian length of edges with given lattice'''
        
        self.lattice = lattice
        self.lengthDic = {}
        for key, edge in self.edges.items():
            length = round(edge.recompute_length(self, lattice), 4)
            if self.lengthDic.get(length) is None:
                self.lengthDic[length] = [key]
            else:
                self.lengthDic.get(length).append(key)

    def __str__(self):
        
        string = 'Unit Cell vertices:\n'
        
        for key, vertex in self.vertices.items():
            string += str(vertex)+'\n'
        
        string += '\nUnit Cell edges:\n'
        
        for key, edge in self.edges.items():
            string += str(edge)+'\n'

        return string
    

class ClusterVertices(object):
    '''Class containing cluster data of Vertices'''
    
    def __init__(self, UC, lattice, size):
        '''
         dictionaries which binds UC_id as a key and list of site indeces
         pointing on the data of the same element extendet on lattice
         stored in corresponding vertices and edges field's arrays
        
        '''
        self.UC = UC
        self.lattice = lattice
        self.process_vertices(size) # will be later used for resizing cluster
        
    def process_vertices(self, size):
        '''compute cluseterVertex parameters from UC'''
        
        self.sitesCoord = self.lattice.get_finite_lattice_sites(size)
        self.size  = self.L, self.W, self.H = size
        self.N = self.L*self.W*self.H
        
        self.ids = []    # UC edge id
        self.types =  []
        self.coords = [] # [cluster_vertex_coords, ...]
        self.array_ind = {} #{UC_vertex_id:[cluster array indexes] }
                
        count = 0
        for key,vertex in self.UC.vertices.items():
            num = self.N
            self.array_ind[vertex.id] = range(count,count+num)
            self.ids += [vertex.id]*self.N
            self.types += [vertex.type]*self.N
            coords=self.sitesCoord + \
                    self.lattice.convert_to_Cartesian(vertex.coords)
            self.coords.append(coords)
            count += 1

        self.ids = np.array(self.ids, dtype = int)
        self.types = np.array(self.types, dtype = int)
        self.coords = np.vstack(tuple(self.coords))
 
    def get_arrayIndex(self, _id, latticeIndex):
        '''get index in vertices array based on lattice site index (X,y,x)'''
        
        x,y,z = latticeIndex
        ind = list(self.UC.vertices.keys()).index(_id)
        if (0<=x<self.L)and(0<=y<self.W)and(0<=z<self.H):
            return ind*self.N + x*self.W*self.H + y*self.H + z
        else:  
            return None # if index is ouside of the cluster
  
    
class ClusterEdges(object):
    '''Class containing cluster data of Edges'''
    
    def __init__(self, UC, vertices, lattice, size):

        self.UC = UC
        self.vertices = vertices
        self.lattice = lattice
        
        self.process_edges(size) # will be later used for resizing cluster
        self.compute_distMatrix() # is used for searching vertices by distance

    def process_edges(self, size):
        '''compute cluseterEdge parameters from UC'''
        
        self.sitesCoord = self.lattice.get_finite_lattice_sites(size)
        # list of lattice sites indexes
        self.sites = np.array(list(itertools.product(*(range(d) for d in size))))
        self.size  = self.L, self.W, self.H = size
        self.N = self.L*self.W*self.H
                
        self.ids=[]    # UC edge id
        self.types=[]
        self.source_target=[]     # [(source_ind, target_ind), ...]
        self.array_ind={}  #{UC edges_id:[cluster array indexes] }
               
        count = 0
        for key,edge in self.UC.edges.items():
            num = 0
            for site in self.sites: 
                source = self.vertices.get_arrayIndex(edge.source, site)
                target = self.vertices.get_arrayIndex(edge.target, 
                                                 site+edge.offset)
                if (source is not None) and (target is not None):                
                    self.source_target.append((source,target))
                    num +=1
            self.ids += [edge.id]*num
            self.types += [edge.type]*num
            self.array_ind[edge.id] = range(count,count+num)
            count += num
            
        self.ids = np.array(self.ids, dtype = int)
        self.types = np.array(self.types, dtype = int)
        self.source_target = np.array(self.source_target, dtype = int)
        
    def get_site(self, vertex_ind):
        '''Return lattice site of the vertex'''
        return self.sites[vertex_ind-self.N*self.vertices.ids[vertex_ind]]           
    
    def add_edge(self, sourse_ind, target_ind):
        '''
        build edge based on source and edge vertex ind
        and returns True if operation was successful
        
        '''	
        edge = Edge(0,0,(self.vertices.ids[sourse_ind],self.vertices.ids[target_ind]),
                    self.get_site(target_ind)-self.get_site(sourse_ind))
        
        edge.recompute_length(self.UC, self.lattice)

        _id = self.UC.add_edge(edge) # also brings edge to the standard form
        
        if _id is None: # edge is duplicate
            return None
        else:            
            source_target=[]     # [(source_ind, target_ind), ...]                   
            count = len(self.ids)
            num = 0
            for site in self.sites: 
                source = self.vertices.get_arrayIndex(edge.source, site)
                target = self.vertices.get_arrayIndex(edge.target,
                                                      site+edge.offset)
                if(source is not None)and(target is not None):                
                    source_target.append((source,target))
                    num +=1
    
            self.array_ind[edge.id] = range(count,count+num)
            self.ids = np.hstack((self.ids, np.array([edge.id]*num)))
            self.types = np.hstack((self.types,[edge.type]*num))
            if self.UC.num_edges == 1:
                self.source_target = np.array(source_target)
            else:    
                self.source_target = np.vstack((self.source_target,source_target))
            
            return _id

    def remove_edge(self, _id):
        '''edge_ind - index in edges array'''
        
        if self.UC.edges.get(_id) is not None:
            self.UC.remove_edge(_id)
            # change edge lattice arrays
            indexes = list(self.array_ind[_id])
            self.ids = np.delete(self.ids,indexes)
            self.types = np.delete(self.types,indexes)
            self.source_target=np.delete(self.source_target,indexes,axis=0)
            self.array_ind = {}
            for key in self.UC.edges.keys():
                self.array_ind[key]=[]
            for j in range(len(self.ids)):
                self.array_ind[self.ids[j]].append(j)    

    def compute_distMatrix(self):
        '''
        compute Euclidian distance matrix for vetices within UC 
        and to neigbouring atoms in cells defined by d_site offset
        
        it is latter used  self.search_edges_by_dist method
        
        '''
        if self.UC.atrib["dimension"] == "3":
            sites = [[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,0],
                     [1,0,1],[0,1,1],[1,-1,0],[1,0,-1],[0,1,-1],
                     [1,1,1],[-1,1,1],[1,-1,1],[1,1,-1]]
        else: # if dimension = "2"
            sites = [[0,0,0],[1,0,0],[0,1,0],[1,1,0],[1,-1,0]]
            
        self.d_sites = np.array(sites)
        sitesCoords = self.lattice.convert_to_Cartesian(self.d_sites.T).T
        
        verticesCoords0 = [] # [cluster_vertex_coords, ...]
        for key,vertex in self.UC.vertices.items():
            coords=self.lattice.convert_to_Cartesian(vertex.coords)
            verticesCoords0.append(coords)
        verticesCoords0 = np.vstack(tuple(verticesCoords0))
        
        verticesCoords = []
        for site in sitesCoords:
            verticesCoords.append(verticesCoords0+site)         
        
        verticesCoords = np.vstack(tuple(verticesCoords))
        
        xx, yy = np.meshgrid(np.arange(self.UC.num_vertices),
                             np.arange(self.UC.num_vertices*len(sites)))
        
        self.distMatrix = np.linalg.norm(verticesCoords[xx]-verticesCoords[yy],axis=2)      
    
    def search_edges_by_dist(self, _type, dist, tolerance=0.1):
        '''
        search edges which corresponds to the same distance between 
        two vertices
        
        input:  _type - type of edge
                dist - is defined in Cartesian coordinates 
                tolerance - distance calculation error (%) 
        
        '''
        eps = dist*tolerance/100
                
        n_vert = self.UC.num_vertices
        ind_pairs = np.vstack(np.where(np.abs(self.distMatrix-dist) < eps)).T
        no_duplicates = np.where(ind_pairs[:,0]>ind_pairs[:,1])[0]
                
        for ind1, ind2 in ind_pairs[no_duplicates,:]:
            offset = self.d_sites[int(ind2/n_vert),:]-self.d_sites[int(ind1/n_vert),:]
            source_target = (ind1 % n_vert + 1,ind2 % n_vert + 1)
            edge = Edge(0, _type, source_target, offset)
            edge.length = dist
            self.UC.add_edge(edge, RECOMPUTE_LENGTH=False)
            
        self.process_edges(self.size)
            
    def search_similar_edges(self, edge):
        '''
        search edges which have the same distance between two vertices 
        as given edge. New edges are assigned the same type as provided one.
                
        '''
        p1 = self.UC.vertices[edge.source].coords
        p2 = self.UC.vertices[edge.target].coords
        dist=np.linalg.norm(self.lattice.convert_to_Cartesian(p1-p2-edge.offset))
        self.search_edges_by_dist(edge.type, dist)
                            
    def change_edge_type(self, _id, new_type):
        '''changes type of the edge with _id to new_type (int: 0,1,2,..)'''
        
        self.UC.edges[_id].type = new_type
        indexes = list(self.array_ind[_id])
        self.types[indexes] = new_type    

    
class CrystalCluster(object):
    '''
    CrystalCluster stores the data Similar to UnitCell but extended to Lattice
    
    most of the fields are L*W*H sized arrays 
    j-element of array corresponds to data for j-lattice-UC
    
    ''' 
    def __init__(self, UC=UnitCell(), lattice=Lattice(), size=(1,1,1)):

        self.UC = UC
        self.lattice = lattice
        
        self.initialize_size(size)       
        self.vertices = ClusterVertices(self.UC, self.lattice, self.size)
        self.edges = ClusterEdges(self.UC,self.vertices,self.lattice,self.size)        
        self.sitesCoord = self.lattice.get_finite_lattice_sites(self.size)
        self.generate_lattice()
        self.generate_arrow()
   
    def initialize_size(self, size):
        '''Initialize Size taking into account dimensionality'''
        
        self.L, self.W, self.H = size
        if int(self.UC.atrib["dimension"]) <= 2:
            self.H = 1
        if int(self.UC.atrib["dimension"]) == 1: 
            self.W = 1     
        self.size  = self.L, self.W, self.H
        self.N = self.L*self.W*self.H
        
    def generate_lattice(self):
        '''generates coordinates of lattice net lines'''
        
        self.latticeLines = []
        
        for i in range(self.L+1):
            for j in range(self.W+1):
                line = np.dot(self.lattice.basisMatrix,np.array([[i,i],[j,j],[0,self.H]])).T
                self.latticeLines.append(line)
        
        for i in range(self.L+1):
            for j in range(self.H+1):
                line = np.dot(self.lattice.basisMatrix,np.array([[i,i],[0,self.W],[j,j]])).T
                self.latticeLines.append(line)

        for i in range(self.W+1):
            for j in range(self.H+1):
                line = np.dot(self.lattice.basisMatrix,np.array([[0,self.L],[i,i],[j,j]])).T
                self.latticeLines.append(line)
       
    def generate_arrow(self):
        '''generates coordinates of arrows lines'''        
        ucVec = np.array([[0,1,0,0],[0,0,1,0],[0,0,0,1]])-0.1
        self.arrowVec=np.dot(self.lattice.basisMatrix,ucVec).T    
        
    def reset_size(self,size):
        '''resize cluseter'''        
        self.initialize_size(size)               
        self.vertices.process_vertices(self.size)
        self.edges.process_edges(self.size)
        self.sitesCoord = self.lattice.get_finite_lattice_sites(self.size)
        self.generate_lattice()
        self.generate_arrow()
    
    def import_fromFile(self, fileNameXML, LATTICEGRAPH_name):
        '''initialize cluster by importing data from file'''
		
        parser = ParseXML(fileName = fileNameXML)
        self.lattice, self.UC = parser.parse_LATTICEGRAPH(LATTICEGRAPH_name)
        self.initialize_atributes()
			
    def export_toFile(self, fileName = "myLatticeGraphLib.xml",
                      LATTICEGRAPH_name = "myLatticeGraph"):
        '''export cluster data to XML library file'''
        
        exporter = ExportXML(self.lattice, self.UC, LATTICEGRAPH_name)
        exporter.export_to_lib(fileName)        


class DealXML(object):
    '''class containing static methods for dealing with xml'''
        
    @staticmethod
    def get_list_names(element, childTag):
        '''return list of children names with tag=childTag'''     
        names = []
        for child in element.findall(childTag):
            names.append(child.get('name'))
        return names

    @staticmethod
    def get_child_by_name(elem, childTag, childName):
        '''return child element with tag=childTag and name=childName'''     
        return elem.find("./{0}/.[@name='{1}']".format(childTag,childName))        

    @staticmethod 
    def prettify(elem):
        '''Return a pretty-printed XML string for the Element.'''     
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_string = reparsed.toprettyxml(indent="  ")
        
        return ET.fromstring(pretty_string)

  
class ParseXML(object):
    '''Class for parsing XML LATTICEGRAPH library'''
    
    def __init__(self, **kwargs):
        
        if kwargs.get("fileName"):
            self.LATTICES = ET.parse(kwargs.get("fileName")).getroot()
        elif kwargs.get("string"):
            self.LATTICES = ET.fromstring(kwargs.get("string"))
        else:
            raise ValueError("No 'filenane' or 'string' are provided")
            
        self.lattice, self.UC = None, None
                    
    def parse_LATTICEGRAPH(self, name):
        '''
        returns Lattice and UnitCell object parsed from LATTICEGRAPH 
        defined by "name"
        
        '''
        LATTICEGRAPH = DealXML.get_child_by_name(self.LATTICES,"LATTICEGRAPH",name)
        # parse Lattice
        FINITELATTICE = LATTICEGRAPH.find("FINITELATTICE")
        boundary = FINITELATTICE.find("BOUNDARY").get('type')
        if boundary is None:
            boundary = "periodic"
 
        LATTICE = FINITELATTICE.find('LATTICE')
        # check if LATTICE is defined in root
        if(LATTICE.getchildren()==[])and(LATTICE.get("ref") is not None):
            LATTICE = DealXML.get_child_by_name(self.LATTICES, "LATTICE", LATTICE.get("ref"))
            if LATTICE is None:
                raise NameError("Lattice '"+LATTICE.get("ref")+"' is not defined")
        
        self.lattice=Lattice(basisMatrix = self.parse_BASIS(LATTICE),
                             name=LATTICE.get('name') if LATTICE.get('name') else "myLattice",
                             dimension=LATTICE.get('dimension') if LATTICE.get('dimension') else "3",
                             BOUNDARY=boundary)
        # parse UnitCell
        UNITCELL = LATTICEGRAPH.find('UNITCELL')
        # check if UNITCELL is defined in root
        if (UNITCELL.getchildren()==[]) and (UNITCELL.get("ref") is not None):
            UNITCELL = DealXML.get_child_by_name(self.LATTICES, "UNITCELL", UNITCELL.get("ref"))
            if UNITCELL is None:
                raise NameError("Lattice '"+UNITCELL.get("ref")+"' is not defined")

        self.UC = self.parse_UNITCELL(UNITCELL)
        self.UC.compute_edgesLength(self.lattice)
        
        return self.lattice, self.UC

    def parse_BASIS(self, LATTICE):
        '''
        parse basis from LATTICE ElementTree element
        
        return: basisMatrix with vectors in columns
        
        '''
        param_dic = self.get_param_dic(LATTICE)
        BASIS = LATTICE.find('BASIS')
        basisMatrix = np.zeros((3,3))
        for v_ind, VECTOR in enumerate(BASIS.findall('VECTOR')):
            for coord_ind, coord in enumerate(VECTOR.text.split(' ')):
                basisMatrix[coord_ind,v_ind] = eval(coord,globals(),param_dic)        

        return basisMatrix    
    
    def parse_UNITCELL(self, UNITCELL):
        '''returns UnitCell object parsed from UNITCELL ElementTree object'''
        
        name = UNITCELL.get("name") if UNITCELL.get("name") else "myUnitCell"
        dim = UNITCELL.get("dimension") if UNITCELL.get("dimension") else "3"
        UC = UnitCell(lattice = self.lattice, name = name, dimension = dim)
        
        for VERTEX in UNITCELL.findall("VERTEX"):
         
            _type = 0 if VERTEX.get("type") is None else int(VERTEX.get("type"))    
            _coords = np.zeros(3)
            COORD = VERTEX.find("COORDINATE")
            if COORD is not None:
                coordStr = [s for s in COORD.text.split(" ") if s != ""]
                for j,val in enumerate(coordStr):
                    _coords[j] = eval(val)   
            UC.add_vertex(Vertex(0, _type, _coords))
            
        for EDGE in UNITCELL.findall("EDGE"):
            SOURCE = EDGE.find("SOURCE")
            TARGET = EDGE.find("TARGET")
            _type = 0 if EDGE.get("type") is None else int(EDGE.get("type"))    
            _source_target = (int(SOURCE.get("vertex")),int(TARGET.get("vertex")))
            _offset= np.zeros(3,dtype=int)
            offsetStr = TARGET.get("offset")
            if offsetStr is not None:
                offsetStr = [s for s in offsetStr.split(" ") if s != ""]
                for j,val in enumerate(offsetStr):
                    _offset[j] = int(val)   
            UC.add_edge(Edge(0, _type, _source_target, _offset))
    
        return UC    

    def get_param_dic(self, element):
        '''
        returns parameter dictionary for given ElementTree element
        
        dic - {'name':'default'}
        
        '''
        param_list = element.findall('PARAMETER')
        dic = {}
        for param in param_list:
            dic[param.get("name")] = eval(param.get("default"),dic)
        
        if '__builtins__' in dic.keys():
            del dic['__builtins__']
            
        return dic

    def get_LATTICEGRAPH_names(self):
        return DealXML.get_list_names(self.LATTICES,"LATTICEGRAPH")
    

class ExportXML(object):
    '''Class for exporting data into LATTICEGRAPH XML library'''
    
    def __init__(self, lattice, UC, LATTICEGRAPH_name = "myLATTICEFGRAPH", NEW_ID = True):
        '''
        input: lattice - Lattice object
               UC - UnitCell object
               NEW_ID - flag managing whether new eges ordered ids are reassigned or not 
        
        '''
        self.lattice = lattice
        self.UC = UC
        self.LATTICEGRAPH_name = LATTICEGRAPH_name
        self.NEW_ID = NEW_ID
        self.dim = int(lattice.atrib["dimension"])
        
        lib = self.get_LATTICES_lib_ET()
        self.lib = DealXML.prettify(lib)

    def export_to_lib(self, fileName):
        '''Exports LATTICEGRAPH into library XML-file'''

        ET.ElementTree(self.lib).write(fileName)        

    def dump_lib(self):
        '''writes LATTICEGRAPH library XML to sys.stdout.'''
              
        ET.dump(self.lib)        
    
    def get_xml_string(self):
        '''writes LATTICEGRAPH library XML to sys.stdout.'''
              
        return ET.tostring(self.lib).decode()    

    def get_LATTICES_lib_ET(self):
        '''Returns LATTICES library ElementTree object.'''
        
        LATTICEGRAPH = ET.Element("LATTICEGRAPH")
        LATTICEGRAPH.set("name", self.LATTICEGRAPH_name)
        LATTICEGRAPH.append(self.get_FINITELATTICE_ET())
        LATTICEGRAPH.append(self.get_UNITCELL_ET())        
        LATTICES = ET.Element("LATTICES")
        LATTICES.append(LATTICEGRAPH)

        return LATTICES
    
    def get_LATTICE_ET(self):
        '''Returns LATTICE ElementTree object.'''
        
        LATTICE = ET.Element("LATTICE")
        LATTICE.set("name",self.lattice.atrib["name"])
        LATTICE.set("dimension",self.lattice.atrib["dimension"])
        BASIS = ET.Element("BASIS")
        for vec in self.lattice.basisMatrix[:self.dim,:self.dim].T:
            VECTOR = ET.Element("VECTOR")
            VECTOR.text = ' '.join([str(c) for c in vec])
            BASIS.append(VECTOR)
        LATTICE.append(BASIS)
        
        return LATTICE    

    def get_FINITELATTICE_ET(self):
        '''Returns FINITELATTICE ElementTree object.'''
        
        FINITELATTICE = ET.Element("FINITELATTICE")         
        # create LATTICE child
        LATTICE = self.get_LATTICE_ET()
        FINITELATTICE.append(LATTICE)        
        param_list = ["L","W","H"]
        # create PARAMETER childs
        for j in range(self.dim):    
            PARAMETER = ET.Element("PARAMETER")
            PARAMETER.set("name", param_list[j])
            if j > 0:
                PARAMETER.set("default", param_list[j-1])
            FINITELATTICE.append(PARAMETER)
        # create EXTENT childs
        for j in range(self.dim):                
            EXTENT = ET.Element("EXTENT")
            EXTENT.set("dimension", str(j+1))
            EXTENT.set("size", param_list[j])            
            FINITELATTICE.append(EXTENT)        
        # create BOUNDARY child
        BOUNDARY = ET.Element("BOUNDARY")
        BOUNDARY.set("type", self.lattice.atrib["BOUNDARY"])
        FINITELATTICE.append(BOUNDARY)
  
        return FINITELATTICE
    
    def get_UNITCELL_ET(self):
        '''Returns UNITCELL ElementTree object.'''

        UNITCELL = ET.Element("UNITCELL")
        UNITCELL.set("name", self.UC.atrib["name"])
        UNITCELL.set("dimension", self.UC.atrib["dimension"])
        UNITCELL.set("vertices", str(self.UC.num_vertices))
        UNITCELL.set("edges", str(self.UC.num_edges))
        # add vertises to UNITCELL
        for key,vertex in self.UC.vertices.items():
            VERTEX = ET.Element("VERTEX")
            VERTEX.set("id",str(vertex.id))
            VERTEX.set("type",str(vertex.type))
            COORDINATE = ET.Element("COORDINATE")
            COORDINATE.text = ' '.join([str(c) for c in vertex.coords[:self.dim]])
            VERTEX.append(COORDINATE)
            UNITCELL.append(VERTEX)
        # add edges to UNITCELL
        count = 0
        for key,edge in self.UC.edges.items():
            count += 1
            EDGE = ET.Element("EDGE")
            EDGE.set("id", str(count) if self.NEW_ID else str(edge.id))
            EDGE.set("type",str(edge.type))
            # create SOURCE
            SOURCE = ET.Element("SOURCE")
            SOURCE.set("vertex",str(edge.source))
            EDGE.append(SOURCE)
            # create TARGET
            TARGET = ET.Element("TARGET")
            TARGET.set("vertex",str(edge.target))
            TARGET.set("offset",' '.join([str(c) for c in edge.offset]))
            EDGE.append(TARGET)
            UNITCELL.append(EDGE)
        
        return UNITCELL