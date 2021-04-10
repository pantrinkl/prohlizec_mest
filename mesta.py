from PySide2.QtCore import QObject, Signal, Slot, Property, QUrl, QAbstractListModel, QByteArray
from PySide2.QtGui import QGuiApplication
from PySide2.QtQuick import QQuickView
from PySide2 import QtCore

import typing
from PySide2.QtPositioning import QGeoCoordinate
import sys
import json
from enum import Enum
import copy

# popis grafiky
VIEW_URL = "mesta.qml" 
# odkaz na souradnice
CITY_LIST_FILE = "souradnice.json"

# model pro seznam okresu
class OkresyListModel(QAbstractListModel):
    def __init__(self,kraj,filename=None):

        QAbstractListModel.__init__(self)
        self.okresy_list = []
        self.ktery_kraj = kraj
        self.zaloha = []
        if filename:
            self.load_from_json(filename)
        
    # nacteni okresu z jsonu
    def load_from_json(self,filename):

        with open(filename,encoding="utf-8") as f:
            self.okresy_list = json.load(f)
        
        self.zaloha = copy.deepcopy(self.okresy_list)

    # nastaveni kraje ze ktereho budou okresy
    def setkraj(self, kraj):
        self.ktery_kraj = kraj

    # pocet okresu
    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        """ Return number of cities in the list"""
        return len(self.okresy_list['polozky'])

    # nacteni nazvu okresu
    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.okresy_list['polozky'][index.row()]['nazev']
    
    # vyfiltrovani okresu dle kraje a aktualizace
    @Slot()
    def filtr(self):
        self.okresy_list = copy.deepcopy(self.zaloha)
        for i in range(len(self.okresy_list['polozky'])-1, -1, -1):
            if self.ktery_kraj != self.okresy_list['polozky'][i]['kraj']:
                self.okresy_list['polozky'].pop(i)
        ctxt = view.rootContext()
        ctxt.setContextProperty('okresyListModel',okresylist_model)
        view.show()
    
# model pro seznam kraju
class KrajeListModel(QAbstractListModel):
    def __init__(self,filename=None):
        QAbstractListModel.__init__(self)
        self.kraje_list = []
        self.ktery_kraj = None
        if filename:
            self.load_from_json(filename)
        
    # nacteni jsonu kraju
    def load_from_json(self,filename):
        with open(filename,encoding="utf-8") as f:
            self.kraje_list = json.load(f)

    # zjisteni poctu kraju
    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self.kraje_list['polozky'])

    # nacteni nazvu kraju
    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.kraje_list['polozky'][index.row()]['nazev']
    
    # poslani id vybraneho kraje do tridy okresu po vybrani kraje uzivatelem
    @ Slot()
    def zmena(self):
        print(self.ktery_kraj)
        ajdicko = 0
        for i in range(len(self.kraje_list['polozky'])-1, -1, -1):
            if self.kraje_list['polozky'][i]['nazev'] == self.ktery_kraj:
                ajdicko = self.kraje_list['polozky'][i]['id']
        okresylist_model.setkraj(ajdicko)

    # tvorba property pro ziskani nazvu kraje z qml
    def get_ktery(self):
        return self.ktery_kraj

    def set_ktery(self, new_val):
        if self.ktery_kraj != new_val:
            self.ktery_kraj = new_val
            self.counter_changed3.emit()

    counter_changed3 = Signal()
    
    krajus = Property(str, get_ktery, set_ktery, notify=counter_changed3)


# model pro seznam obci a mest
class CityListModel(QAbstractListModel):

    # zobrazované role
    class Roles(Enum):
        POPULATION = QtCore.Qt.UserRole
        AREA = QtCore.Qt.UserRole+1
        LOCATION = QtCore.Qt.UserRole+2

    # inicializace
    def __init__(self,filename=None):
        QAbstractListModel.__init__(self)
        self.city_list = []
        self.kraje_list = []
        self.obce_list = []
        self.okres_v = None
        self.dolnimez = 0
        self.hornimez = 1400000
        self.mesta = False
        self.obce = False
        self.vybranyokres = None
        self.vybranykraj = None
        if filename:
            self.load_from_json(filename)

    # extrakce roli
    def roleNames(self):
        roles = super().roleNames()
        roles[self.Roles.POPULATION.value] = QByteArray(b'population')
        roles[self.Roles.AREA.value] = QByteArray(b'area')
        roles[self.Roles.LOCATION.value] = QByteArray(b'location')
        return roles

    # nacteni jsonu se souradnicemi a s nazvy obci s okresy
    def load_from_json(self,filename):

        with open(filename,encoding="utf-8") as f:
            self.city_list = json.load(f)
        
        with open("obce.json",encoding="utf-8") as f:
            self.obce_list = json.load(f)
        
        for c in self.city_list:
            pos = c['location']
            lon,lat = pos.split("(")[1].split(")")[0].split(" ") 
            c['location'] = QGeoCoordinate(float(lat),float(lon))
        
        self.zaloha = self.city_list.copy()
        
    # vyfiltrovani obci dle zadanych parametru
    @Slot()
    def filtrovani(self):
        self.city_list = self.zaloha.copy()

        # filtrovani dle velikosti mesta ci obce
        for polozka in range(len(self.city_list)-1, -1, -1):
            if int(self.city_list[polozka]['population']) < self.dolnimez:
                self.city_list.pop(polozka)
                print(polozka)
        
        for polozka in range(len(self.city_list)-1, -1, -1):
            if int(self.city_list[polozka]['population']) > self.hornimez:
                self.city_list.pop(polozka)
        
        # filtrovani dle mesta a obce
        if self.mesta == True and self.obce == False:
            for polozka in range(len(self.city_list)-1, -1, -1):
                if "obec" in self.city_list[polozka]['muniDescription']:
                    self.city_list.pop(polozka)
        
        if self.mesta == False and self.obce == True:
            for polozka in range(len(self.city_list)-1, -1, -1):
                if "obec" not in self.city_list[polozka]['muniDescription']:
                    self.city_list.pop(polozka)
        
        if self.mesta == False and self.obce == False:
            for polozka in range(len(self.city_list)-1, -1, -1):
                self.city_list.pop(polozka)

        # filtrovani dle vybraneho okresu
        if self.okres_v == None:
            pass
        else:
            obce_vokresu = []
            id_okresu = 0
            for i in range(len(okresylist_model.okresy_list['polozky'])-1, -1, -1):
                if okresylist_model.okresy_list['polozky'][i]['nazev'] == self.okres_v:
                    id_okresu = okresylist_model.okresy_list['polozky'][i]['id']
                    break

            for i in range(len(self.obce_list['polozky'])-1, -1, -1):
                if id_okresu == self.obce_list['polozky'][i]['okres']:
                    obce_vokresu.append(self.obce_list['polozky'][i]['nazev'])
            
            for polozka in range(len(self.city_list)-1, -1, -1):
                    if self.city_list[polozka]['muniLabel'] not in obce_vokresu:
                        self.city_list.pop(polozka)

        ctxt = view.rootContext()
        ctxt.setContextProperty('cityListModel',citylist_model)
        view.show()

    # sloty pro zakrizkovani mesta ci obce
    @Slot()
    def truemesto(self):
        self.mesta = True
        print(self.mesta)
    
    @Slot()
    def falsemesto(self):
        self.mesta = False
        print(self.mesta)
    
    @Slot()
    def trueobec(self):
        self.obce = True
        print(self.obce)
    
    @Slot()
    def falseobec(self):
        self.obce = False
        print(self.obce)

    # zisteni poctu obci 
    def rowCount(self, parent:QtCore.QModelIndex=...) -> int:
        return len(self.city_list)

    # zisteni nazvu, poctu obyvatel, plochy a souradnic pro qml
    def data(self, index:QtCore.QModelIndex, role:int=...) -> typing.Any:
        if not index.isValid():
            return None
        if role == QtCore.Qt.DisplayRole:
            return self.city_list[index.row()]["muniLabel"]
        if role == self.Roles.POPULATION.value:
            return self.city_list[index.row()]['population']
        if role == self.Roles.AREA.value:
            return self.city_list[index.row()]['area']
        if role == self.Roles.LOCATION.value:
            return self.city_list[index.row()]['location']
    
    # property pro zjisteni dolni a horni meze poctu obyvatel a vybraneho okresu
    def get_dolni(self):
        return self.dolnimez
    
    def get_horni(self):
        return self.hornimez
    
    def get_okres(self):
        return self.okres_v

    def set_dolni(self,new_val):
        if self.dolnimez != new_val:
            self.dolnimez = new_val
            self.counter_changed.emit()
    
    def set_horni(self,new_val):
        if self.hornimez != new_val:
            self.hornimez = new_val
            self.counter_changed2.emit()
    
    def set_okres(self,new_val):
        if self.okres_v != new_val:
            self.okres_v = new_val
            self.counter_changed3.emit()
    
    counter_changed = Signal()
    counter_changed2 = Signal()
    counter_changed3 = Signal()

    dolni = Property(int,get_dolni,set_dolni,notify=counter_changed)
    horni = Property(int,get_horni,set_horni,notify=counter_changed2)
    okres = Property(str,get_okres,set_okres,notify=counter_changed3)

#konstrukce modelu a spusteni aplikace
app = QGuiApplication(sys.argv)
view = QQuickView()
url = QUrl(VIEW_URL)
citylist_model = CityListModel(CITY_LIST_FILE)
krajelist_model = KrajeListModel('kraje.json')
okresylist_model = OkresyListModel("Kraj/27","okresy.json")
print(citylist_model.roleNames())
ctxt = view.rootContext()
ctxt.setContextProperty('cityListModel',citylist_model)
ctxt.setContextProperty('krajeListModel',krajelist_model)
ctxt.setContextProperty('okresyListModel',okresylist_model)
view.setSource(url)
view.show()

app.exec_()
