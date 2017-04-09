#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 17:07:36 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

This module contains the definition of the QCustomListWidget with add/remove buttons.
    
    class QCustomListWidget(QListWidget):
    class QCustomListWidget_Add(QWidget):
    class QCustomListWidget_AddRemove(QCustomListWidget_Add):
        
testing and examples:
    
    def showInDialog(widget):
    def test_MyQCustomListWidget(MyQCustomListWidget_class, QCustomWidget, data):
    def create_initalizing_data():
    def run_test():

Module is compatible with both pyQt4 and pyQt5
    
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

# imports requied PyQt modules
if pyQtVersion == "PyQt4":
    from PyQt4.uic import loadUiType
    from PyQt4.QtGui import (QWidget, QDialog, QPushButton, QListWidget, 
                             QSizePolicy, QListWidgetItem, QVBoxLayout, QHBoxLayout)
else:
    from PyQt5.uic import loadUiType
    from PyQt5.QtWidgets import (QWidget, QDialog, QPushButton, QListWidget, 
                                 QSizePolicy, QListWidgetItem, QVBoxLayout, QHBoxLayout) 
# classes definition
    
class QCustomListWidget(QListWidget):
    '''QListWidget with customized ItemWidget'''

    def __init__ (self, QCustomWidget, initializationData=[]):
        """
        QCustomQWidget - custom widget
        initializationData  - data for initilaization of QCustomQWidget 
                              instances
        """
        super(QCustomListWidget, self).__init__()
        
        self.QCustomWidget = QCustomWidget
        self.set_data(initializationData)        
        # Customize SizePolicy
        self.setMinimumWidth(QCustomWidget().minimumWidth()+30)     
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding,
                                 QSizePolicy.Preferred)
        self.setSizePolicy(sizePolicy)
                    
    def add_default_items(self, num):
        '''add N=num default items to the QCustomListWidget'''
        
        for j in range(num):
            newItem = self.QCustomWidget()
            self.add_item(newItem)   
    
    def add_item(self, newItemWidget):
        '''add item with widget newItemWidget'''
        
        # Create QListWidgetItem
        myQListWidgetItem = QListWidgetItem(self)
        # Set size hint
        myQListWidgetItem.setSizeHint(newItemWidget.sizeHint())
        # Add QListWidgetItem into QListWidget
        self.addItem(myQListWidgetItem)
        self.setItemWidget(myQListWidgetItem, newItemWidget)

    def set_itemData(self, j, data, strFlag=False):
        self.itemWidget(self.item(j)).set_data(data, strFlag)
    
    def get_itemData(self, j):
        itemWidget = self.itemWidget(self.item(j))
        if type(itemWidget) is self.QCustomWidget:
            return itemWidget.get_data()
        else:
            return None

    def set_data(self,initializationData, strFlag=False):                    
        self.clear()
        for data in initializationData:
            newItem = self.QCustomWidget()
            newItem.set_data(data, strFlag)
            self.add_item(newItem) 
            
    def get_data(self):    
        data = []
        for j in range(self.count()):
            data.append(self.get_itemData(j))
        return data


class QCustomListWidget_Add(QWidget):
    '''QListWidget with customized ItemWidget and add item button'''

    def __init__ (self, QCustomWidget, initializationData=[]):
        """
        QCustomQWidget - custom widget
        initializationData  - data for initilaization of QCustomQWidget 
                              instances
        """
        super(QCustomListWidget_Add, self).__init__()
        
        self.QCustomWidget = QCustomWidget
        
        # add QCustomListWidget
        self.listWidget = QCustomListWidget(QCustomWidget, initializationData)
        # if no initial data provided add 10 items to ListWidget
        if len(initializationData) == 0:
             self.listWidget.add_default_items(10)        
        self.vbox = QVBoxLayout()        
        self.vbox.addWidget(self.listWidget)

        self.btnAdd = QPushButton("add preference")
        self.vbox.addWidget(self.btnAdd)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.vbox)
        # add connections
        self.btnAdd.clicked.connect(self.add_item_callback)
        
    def add_item_callback(self):
        newItem = self.QCustomWidget()
        self.listWidget.add_item(newItem)
        self.listWidget.scrollToBottom()


##############################################################################

if __name__ == '__main__':

    # test classes    
        
    def showInDialog(widget):
        '''used for displaying widgets in dialog during test'''
            
        dlg = QDialog()
        widget.setParent(dlg)
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(widget)
        dlg.setLayout(vbox)
        dlg.exec_()
        
    
    def test_MyQCustomListWidget(MyQCustomListWidget_class, QCustomWidget, data):
        
        print("\n# run {} test\n".format(MyQCustomListWidget_class))
    
        myQCustomListWidget = MyQCustomListWidget_class(QCustomWidget, data)
        showInDialog(myQCustomListWidget)
    
    from QColorButton import QColorButton
    ui_folder = 'resources/ui_layout/'
    Ui_myColorListItem, QWidget = loadUiType(ui_folder+'widget_myColorListItem.ui')

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
    
    
    def create_initalizing_data():
        '''returns default initializing data for QCustomListWidget'''
        
        clrs = [u'#00aaff', u'#ff0000', u'#ffff7f', u'#ffaaff', u'#aaffff',
                u'#ffaa7f', u'#a3ff82', u'#5500ff', u'#aa007f', u'#ffffff'] 
        
        data = [{"label":"type %s"%j,"bool":True,"color":clr} for j,clr in enumerate(clrs)]
    
        return data
    
    
    def run_test():
        
        print("\n {} is imported".format(pyQtVersion))
        
        # imports requied PyQt modules
        if pyQtVersion == "PyQt4":
            from PyQt4.QtGui import QApplication
        else:
            from PyQt5.QtWidgets import QApplication
        
        import sys

        data = create_initalizing_data()
        
        app = QApplication([])
        
        QCustomWidget = QColorListItemWidget
                           
        test_MyQCustomListWidget(QCustomListWidget, QCustomWidget, data)
        test_MyQCustomListWidget(QCustomListWidget_Add, QCustomWidget, data)
        test_MyQCustomListWidget(QCustomListWidget_AddRemove, QCustomWidget, data)
     
        sys.exit(app.exec_())

    
    run_test()
