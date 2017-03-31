#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:02:48 2017

@author: Ivan Luchko (luchko.ivan@gmail.com)

This module contains the definition of the preference management tool.
    
    class DealXML(object):
    class WidgetPreferences(QWidget):
    class DialogPreferences(QDialog, Ui_DialogPreferences):
        
testing and examples:
    
    class TestWidgetPreferences(WidgetPreferences, Ui_testWidgetPreferences):
    def test_MyQCustomListWidget_defaults():
    def test_MyQCustomListWidget_parent():    
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
    from PyQt4.QtCore import Qt, pyqtSignal
    from PyQt4.QtGui import (QWidget, QMessageBox)
else:
    from PyQt5.uic import loadUiType
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtWidgets import (QWidget, QMessageBox) 

# import python libs
import xml.etree.ElementTree as ET
from xml.dom import minidom

# import UI created in designer
ui_folder = 'latticegraph_designer/resources/ui_layout/'
Ui_DialogPreferences, QDialog = loadUiType(ui_folder+'dialog_preferences.ui')
Ui_DialogAddTheme, QDialog = loadUiType(ui_folder+'dialog_addTheme.ui')

# classes definition

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
        prettyElem = ET.fromstring(pretty_string)
        prettyElem.tail = "\n\n"
        
        return prettyElem


class WidgetPreferences(QWidget):
    '''abstract class of preference widget used in preference management tool'''
        
    def __init__ (self):

        QWidget.__init__(self)
        
        self.curent_theme_name = "Current theme"
        
    def set_theme_ET(self, THEME):
        '''initialize preference widget according to THEME ElementTree''' 
        
        raise NotImplementedError('users must define self.set_theme_ET() to use this base class')
        
        # configure setting widgets e.g: 
        self.checkBox.setChecked(THEME.find("CHECKBOX").get("value") == "True")
        self.spinBox.setValue(int(THEME.find("SPINBOX").get("value")))
        
    def get_current_theme_ET(self):
        '''get xml ElementTree containing setting data in preference widget'''
        
        raise NotImplementedError('users must define self.set_theme_ET() to use this base class')

        THEME = ET.Element("THEME")
        THEME.set('name',self.curent_theme_name)
        
        tagsList = [] # e.g. ["CHECKBOX", ... ]
        getValList = [] # e.g. [self.checkBox.isChecked(), ... ]

        for tag, val in zip(tagsList,getValList):        
            item = ET.Element(tag)
            item.set('value',str(val))
            THEME.append(item)
                
        return DealXML.prettify(THEME)


class DialogPreferences(QDialog, Ui_DialogPreferences):
    '''
    provides setting manegment tool with ability to create different settings
    themes, saving and deleting them.
    
    all settings are stored in self.prefFileName xml file
    
    ''' 
    applySignal = pyqtSignal()
    prefFileName_temp = "resources/temp_preferences.xml"
    
    class QDialogAddTheme(QDialog, Ui_DialogAddTheme):
        def __init__ (self, label=None):
            QDialog.__init__(self)
            self.setupUi(self)        
            self.set_label(label)
        
        def set_label(self,label):
            self.label.setText(label)
    
        def get_name(self):
            return str(self.lineEdit.text())
            
    def __init__ (self, WidgetPreferencesClass=WidgetPreferences,
                  parent=None, prefFileName=None):
        '''
        if 'parent' provided dialogs creates bindings with
            parent.prefFileName, parent.SETTINGS, parent.CURRENT_THEME            
        fields and emits self.applySignal() when self.btnApply is pressed. 
        This signal should be processed in the parent class
        
        if no 'parent' but 'prefFileName' is provided dialog configures according
        to this file and writes all changes into it
        
        if no 'parent' neither 'prefFileName' is provided dialog creates new
        self.prefFileName = "preferences_temp_settings.xml" and 
        and writes all changes into it. This is usefull for genereting default
        thems when primarily no preference xml file exists 
        
        '''        
        super(DialogPreferences, self).__init__()
        self.setupUi(self)
        
        # "overload" prefWidget 
        self.vbox.removeWidget(self.prefWidget)
        self.prefWidget.setParent(None)
        self.prefWidget.deleteLater()  
        self.prefWidget = WidgetPreferencesClass()
        self.vbox.insertWidget(1,self.prefWidget)
        
        # initialize theme        
        self.curent_theme_name = "Current theme"
        if parent is not None: # create bindings
            self.prefFileName = parent.prefFileName
            self.SETTINGS = parent.SETTINGS
            self.CURRENT_THEME = parent.CURRENT_THEME            
        
        elif prefFileName is not None:        
            self.prefFileName = prefFileName
            self.SETTINGS = ET.parse(self.prefFileName).getroot()
            self.CURRENT_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME","Current theme")               
            
        else: # create your own 'prefFileName' with default preferences
            self.prefFileName = self.prefFileName_temp
            print("No 'parent' neither 'prefFileName' is provided.")
            print("All settings will be stored in {}".format(self.prefFileName))
            self.CURRENT_THEME = self.prefWidget.get_current_theme_ET()
            self.SETTINGS = ET.Element("SETTINGS")
            self.SETTINGS.text = "\n\n"
            self.SETTINGS.append(self.CURRENT_THEME)
            ET.ElementTree(self.SETTINGS).write(self.prefFileName)
        
        self.initialize_dialog()

        self.comboBox.currentIndexChanged.connect(self.change_theme_callback)
        self.btnSave.clicked.connect(self.save_theme_callback)
        self.btnAdd.clicked.connect(self.addNew_theme_callback)
        self.btnRemove.clicked.connect(self.remove_theme_callback)
        self.btnClose.clicked.connect(self.reject)
        self.btnDefaults.clicked.connect(self.restore_defaults_callback)
        self.btnApply.clicked.connect(self.apply_callback)

    def initialize_dialog(self):
        '''initialize dialog settings components'''
        
        self.themeList = DealXML.get_list_names(self.SETTINGS, "THEME")
        self.comboBox.addItems(self.themeList)
        currentIndex = self.themeList.index(self.curent_theme_name)
        self.comboBox.setCurrentIndex(currentIndex)
        
        self.prefWidget.set_theme_ET(self.CURRENT_THEME)
    
    def reset_current_theme_ET(self):
        '''reset current theme ElementTree according to preferences widget'''
        
        for child in list(self.CURRENT_THEME):       
            self.CURRENT_THEME.remove(child)
        for child in list(self.prefWidget.get_current_theme_ET()):
            self.CURRENT_THEME.append(child)    

    def change_theme_callback(self, ind):
        '''is called when theme comboBox is changes'''
        
        CHOSEN_THEME = DealXML.get_child_by_name(self.SETTINGS, "THEME",
                                                 self.themeList[ind])         
        self.prefWidget.set_theme_ET(CHOSEN_THEME)
    
    def save_theme_callback(self):
        '''save changes in selected theme'''
 
        theme_name = str(self.comboBox.currentText())
        if theme_name in ("Current theme", "Default theme"):
            self.addNew_theme_callback()
        else:
            # make chnages in xml lib                
            CHOSEN_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME",theme_name)
            self.SETTINGS.remove(CHOSEN_THEME)
            CHOSEN_THEME = self.prefWidget.get_current_theme_ET()
            CHOSEN_THEME.set("name", theme_name)
            self.SETTINGS.append(CHOSEN_THEME)
            ET.ElementTree(self.SETTINGS).write(self.prefFileName)
    
    def addNew_theme_callback(self):
        '''add new theme and save it to preference file'''
        
        dlg = self.QDialogAddTheme("New theme name:")
        if dlg.exec_():
            new_theme_name = dlg.get_name()
            #check if name already exist
            while new_theme_name in self.themeList:
                dlg.set_label("'{}' already exist. \nChoose anothe new theme name:".format(new_theme_name))
                if not dlg.exec_(): return
                new_theme_name = dlg.get_name()     
            # make chnages in xml lib                
            self.NEW_THEME = self.prefWidget.get_current_theme_ET()
            self.NEW_THEME.set("name", new_theme_name)
            self.SETTINGS.append(self.NEW_THEME)
            ET.ElementTree(self.SETTINGS).write(self.prefFileName)
            # deal theme comdoBox
            self.themeList.append(new_theme_name)
            self.comboBox.addItem(new_theme_name)
            currentIndex = self.themeList.index(new_theme_name)
            self.comboBox.setCurrentIndex(currentIndex)    

    def remove_theme_callback(self):
        '''remove selected theme'''
        
        theme_name = str(self.comboBox.currentText())
        msb = QMessageBox()
        msb.setIcon(QMessageBox.Critical)
        msb.setWindowTitle("Message")
        
        if theme_name in ("Current theme", "Default theme"):
            msb.setStandardButtons(QMessageBox.Ok)
            msb.setText("'{}' cannot be deleted.".format(theme_name))
            msb.exec_()            
        else:
            msb.setText("Are you sure you want to delete '{}'?".format(theme_name))
            msb.setIcon(QMessageBox.Warning)
            msb.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            if msb.exec_() == QMessageBox.Ok:            
                index = self.themeList.index(self.curent_theme_name)
                self.comboBox.setCurrentIndex(index)
                CHOSEN_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME",theme_name)
                self.SETTINGS.remove(CHOSEN_THEME)
                ET.ElementTree(self.SETTINGS).write(self.prefFileName)
                index = self.themeList.index(theme_name)
                self.comboBox.removeItem(index)
                self.themeList.remove(theme_name)           
        
    def apply_callback(self):
        '''makes changes in pref.xml and resets current theme in parent object'''
        
        # make chnages in ET and xml lib
        self.reset_current_theme_ET() 
        ET.ElementTree(self.SETTINGS).write(self.prefFileName)
        # deal theme comdoBox
        currentIndex = self.themeList.index(self.curent_theme_name)
        self.comboBox.setCurrentIndex(currentIndex)
        #make changes in parent
        self.applySignal.emit()
            
    def restore_defaults_callback(self):
        '''restore default theme'''
        
        DEFAULT_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME","Default theme") 
        if DEFAULT_THEME is None:
            raise ValueError("Deafault theme is not defined in preference file.")
        else:
            self.prefWidget.set_theme_ET(DEFAULT_THEME)
            self.apply_callback()

##############################################################################
    
if __name__ == '__main__':

    # test classes    
    
    Ui_testWidgetPreferences, QWidget = loadUiType(ui_folder+'widget_testPreferences.ui')
    
    class TestWidgetPreferences(WidgetPreferences, Ui_testWidgetPreferences):
        '''preference widget used for test/demo of preference management tool'''
        
        def __init__ (self):
    
            super(TestWidgetPreferences, self).__init__()
            self.setupUi(self)        
        
        def set_theme_ET(self, THEME):
            '''initialize preference widget according to THEME ElementTree''' 
    
            self.checkBox.setChecked(THEME.find("CHECKBOX").get("value") == "True")
            self.lineEdit.setText(THEME.find("LINEEDIT").get("value"))
            self.spinBox.setValue(int(THEME.find("SPINBOX").get("value")))
            
        def get_current_theme_ET(self):
            '''get xml ElementTree containing setting data in preference widget'''
            
            THEME = ET.Element("THEME")
            THEME.set('name',self.curent_theme_name)
            
            tagsList = ["CHECKBOX", "LINEEDIT", "SPINBOX"]
            getValList = [self.checkBox.isChecked(), self.lineEdit.text(),
                          self.spinBox.value()]
    
            for tag, val in zip(tagsList,getValList):        
                item = ET.Element(tag)
                item.set('value',str(val))
                THEME.append(item)
                    
            return DealXML.prettify(THEME)

            
    def test_MyQCustomListWidget_defaults():
        '''testing creation of the primary defaults settings '''
         
        print("\n# run {} test".format(DialogPreferences))
        print("     - generating default settings mode\n")
    
        dlgPref = DialogPreferences(WidgetPreferencesClass = TestWidgetPreferences)
        dlgPref.exec_()
        with open(dlgPref.prefFileName, 'r') as f:
            xml_text = f.read()
        print("\n preference file after manipulation:\n")
        print(xml_text)    

        
    def test_MyQCustomListWidget_parent():
        '''testing interaction with preference parent object'''
    
        class TestPrefPatrent(object):
            '''class used for interaction with DialogPreferences as a parent during test'''
            
            def __init__(self):
        
                self.prefFileName = DialogPreferences.prefFileName_temp
                self.SETTINGS = ET.parse(self.prefFileName).getroot()
                self.CURRENT_THEME = DealXML.get_child_by_name(self.SETTINGS,"THEME","Current theme")               
                
            def preferences_callback(self):
                '''Calls preference dialog'''
                
                self.dlgPref = DialogPreferences(WidgetPreferencesClass=TestWidgetPreferences,
                                                 parent=self)
               
                self.dlgPref.applySignal.connect(self.applyPref_callback)
                self.dlgPref.exec_()
            
            def applyPref_callback(self):
                '''when apply button is pressed in DialogPreferences'''
                
                print("\n 'Apply' pressed. parent.CURRENT_THEME settings parameters:")
                
                for pref in self.CURRENT_THEME:        
                    print("     {0} = {1}".format(pref.tag, pref.get("value")))
            
        print("\n# run {} test".format(DialogPreferences))
        print("     - communicating with 'parent' mode")
    
        testPrefPatrent = TestPrefPatrent()
        testPrefPatrent.preferences_callback()
    
        with open(testPrefPatrent.prefFileName, 'r') as f:
            xml_text = f.read()
        print("\n preference file after manipulation:\n")
        print(xml_text)    
        
    
    def run_test():
        
        print("\n {} is imported".format(pyQtVersion))
        
        # imports requied PyQt modules
        if pyQtVersion == "PyQt4":
            from PyQt4.QtGui import QApplication
        else:
            from PyQt5.QtWidgets import QApplication
        
        import sys
        
        app = QApplication([])
    
        test_MyQCustomListWidget_defaults()
        test_MyQCustomListWidget_parent()
     
        sys.exit(app.exec_())

    
    run_test()