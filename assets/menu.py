import pi3d
import RPi.GPIO as GPIO
from assets.encoder import encoder

red = (1.0, 0.0 , 0.0, 1.0)
orange = (1.0, 0.7 , 0.0, 1.0)
green = (0.0, 1.0 , 0.0, 1.0)
blue = (0.0, 0.0 , 1.0, 1.0)
white = (1.0, 1.0 , 1.0, 1.0)
gray = (0.5,0.5,0.5, 1.0)

class TextData(object):
    arrow = ">"
    page = ''
    row1 = ''
    row2 = ''
    row3 = ''
    row4 = ''
    row5 = ''
    row6 = ''
    row7 = ''
    row8 = ''
    row9 = ''
    row10 = ''
    tgtRow = ''
    menuIdx = 0


text_data = TextData()

class Menu:
    def __init__(self, controller):
        espace = 0.40
        color = green
        self.txt = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=700, point_size=64)
        arrow = pi3d.PointText(controller.pointFont, controller.CAMERA2D, max_chars=400, point_size=64)
        maxItemSize = 50

        menuTxt = pi3d.TextBlock(-550, 250, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="page",
                text_format="== {:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(menuTxt)
        row1Txt = pi3d.TextBlock(-500, 200, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row1",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row1Txt)
        row2Txt = pi3d.TextBlock(-500, 150, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row2",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row2Txt)
        row3Txt = pi3d.TextBlock(-500, 100, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row3",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row3Txt)
        row4Txt = pi3d.TextBlock(-500, 50, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row4",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row4Txt)
        row5Txt = pi3d.TextBlock(-500, 0, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row5",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row5Txt)
        row6Txt = pi3d.TextBlock(-500, -50, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row6",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row6Txt)
        row7Txt = pi3d.TextBlock(-500, -100, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row7",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row7Txt)
        row8Txt = pi3d.TextBlock(-500, -150, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row8",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row8Txt)
        row9Txt = pi3d.TextBlock(-500, -200, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row9",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row9Txt)
        row10Txt = pi3d.TextBlock(-500, -250, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="row10",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=color)
        self.txt.add_text_block(row10Txt)
        tgtRowTxt = pi3d.TextBlock(-500, -330, 0.1, 0.0, maxItemSize, data_obj=text_data, attr="tgtRow",
                text_format="{:s}", size=0.55, spacing="C", space=0.55,
                colour=orange)
        self.txt.add_text_block(tgtRowTxt)


        self.arrow = pi3d.TextBlock(-550, 200, 0.1, 0.0, 1, data_obj=text_data, attr="arrow",
                text_format="{:s}", size=0.50, spacing="C", space=0.5, justify=0.5,
                colour=color)
        self.txt.add_text_block(self.arrow)

        self.antiBounce = 0
        self.pagesList = {}
        self.redirectList = {}
        self.actionList = {}
        self.pageHide = []

        self.currentPage = "ROOT"
        self.offset = 0      


    def setPagesList(self, page, pagesList):
        self.pagesList[page] = pagesList

    def showMenu(self, page):
        text_data.page = str(page)              #Le nom de la page correspond au nom de la page du dictionnaire

        self.itemList = self.pagesList.get(page)[:]  #Liste des textes à afficher pour la page actuelle
        
        if self.currentPage != "ROOT":               #Si on est pas dans la page "ROOT"
            self.itemList.append("")                 #Création d'un item nul et d'un item "BACK" pour revenir à la page précédente
            self.itemList.append("BACK")

        while(len(self.itemList) < 10):              #Tant que celle-ci est inferieure au nombre de colonnes d'affichage
            self.itemList.append("")                 #On rajoute un élément nul à la liste  

        for idx, item in  enumerate(self.itemList):  #Teste tous les items du menu actuel
            if item in self.pageHide:                #Si l'item est dans la liste des items à cacher
                self.itemList[idx] = ""              #On cache l'item

        self.menuLength = len(self.itemList)-1       #Stockage de la longeur de la liste pour le curseur
        if self.menuLength <= 10:
            while(self.itemList[self.menuLength] == ""):
                self.menuLength -= 1

        text_data.row1 = self.itemList[self.offset+0]        #Pour chaque colonne, on afficher l'élément de la liste qui corresponds
        text_data.row2 = self.itemList[self.offset+1]
        text_data.row3 = self.itemList[self.offset+2]
        text_data.row4 = self.itemList[self.offset+3]
        text_data.row5 = self.itemList[self.offset+4]
        text_data.row6 = self.itemList[self.offset+5]
        text_data.row7 = self.itemList[self.offset+6]
        text_data.row8 = self.itemList[self.offset+7]
        text_data.row9 = self.itemList[self.offset+8]               
        text_data.row10 = self.itemList[self.offset+9]


    def setAction(self, element, function=None, goToPage = None):
        if goToPage != None:
            self.redirectList[element] = goToPage
        if function != None:
            self.actionList[element] = function

    def setAllRedirectIn(self, page, pageDest):
        for element in self.pagesList[page]: 
            self.setAction(element, goToPage=pageDest)

    def setAllAction(self, page, function):
        for element in self.pagesList[page]: 
            self.setAction(element, function=function)

    def click(self):
        idx = self.offset+encoder.getValue()
        selectedItem = self.itemList[idx] #Selection de l'item en fonction de la valeur actuelle de l'encodeur
                         
        if selectedItem in self.redirectList:                   #Si il y a une redirection
            redirect = self.redirectList[selectedItem]          #Association à une redirection dans la liste des redirections
            self.setAction("BACK", goToPage = self.currentPage) #Action de "BACK" : aller à la page actuelle (avant maj de la page)
            self.offset = 0
            self.currentPage = redirect                         #MAJ de la page

        if selectedItem in self.actionList:                     #Si il y a une action
            action = self.actionList[selectedItem]              #Association à une action dans la liste des actions
            action(selectedItem)                            #Execution de la fonction associée à l'action
        
            
    def hide(self, item, hide):
        if hide == True and item not in self.pageHide:
            self.pageHide.append(item)
        elif hide == False and item in self.pageHide:
            self.pageHide.remove(item)

    def changeName(self, menu, itemIdx, newName):
        temp = {}
        temp = self.pagesList[menu][:]
        temp[itemIdx] = newName
        
        self.pagesList[menu] = temp

    def run(self):

        
        self.arrow.set_position(y = 200-(50*text_data.menuIdx))
        self.showMenu(self.currentPage)


        if GPIO.event_detected(4) and self.antiBounce > 15:
            self.click()
            encoder.setValue(0)
            self.antiBounce = 0

        if self.antiBounce < 20:
            self.antiBounce = self.antiBounce+1

        temp = encoder.getValue()

        while temp < 10 and temp >= 0 and self.itemList[self.offset+temp] == "": #Skip n'importe quel item vide
            temp = temp+(temp-text_data.menuIdx)
            encoder.setValue(temp)

        if temp < 0:                                    #Si on revient en arrière
            if self.offset == 0:                        #Si y'a pas d'offset
                self.offset = 9*int(self.menuLength/9)  #On ajoute l'offset nécéssaire pour aller à la fin
                if self.offset != 0:                    #Exception : si l'offset n'est pas nul, on enlève les éléments de la première page
                    self.offset -= 9
                encoder.setValue(self.menuLength%9)     #Et on retourne à la fin
            else:
                encoder.setValue(9)                     #Si il y a un offset, on réduit l'offset
                self.offset -= 9

        elif temp > self.menuLength and self.currentPage == "ROOT": #Si on arrive à la fin du menu - Exception pour la page "ROOT"
            encoder.setValue(0)
            self.offset = 0                             #On revient au début

        elif temp > (self.menuLength-self.offset):    #Si on arrive à la fin du menu (+2 pour les éléments "BACK")
            encoder.setValue(0)
            self.offset = 0                             #On revient au début

        elif temp > 9:                                  #Si on va au delà de 9 sans être arrivé à la fin du menu
            encoder.setValue(0)
            self.offset += 9                            #On offset de 9

        else:                                           #Si aucun de ces éléments n'est activé, on bouge le curseur
            text_data.menuIdx = temp


        
            
        
        self.txt.draw()
        self.txt.regen()
        