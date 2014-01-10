# -*- coding: iso-8859-1 -*-
import os
import sys
import wx
import base64

#==============================================================================  
def repertoire_script():
    """
    :brief: Renvoie le chemin absolu du repertoire qui contient le présent fichier
    """
    from os.path import abspath, split
    from inspect import stack as call_stack
    # Saisie de la "call stack"
    frame_record_list = call_stack()      
    # Le dernier enregistrement (donc l'appel de cette fonction de ce fichier) est en début de liste
    record = frame_record_list[1]     
    # Composition du “frame record” :
    #   [0]: the frame object
    #   [1]: the filename
    #   [2]: the line number of the current line
    #   [3]: the function name
    #   [4]: a list of lines of context from the source code
    #   [5]: the index of the current line within that list 
    nom_de_ce_fichier         = record[1]    
    # Extraction du chemin absolu du repertoire
    nom_complet_de_ce_fichier = abspath( nom_de_ce_fichier )       
    nom_repertoire, nom_fichier = split(nom_complet_de_ce_fichier)    
    # Renvoie l'information
    return nom_repertoire 
    
#==============================================================================   
class InterfaceGraphique(wx.Frame):
    """Module permettant de gerer l'interface graphique         
    """
    def __init__(self, parent, titre):
        """
        :brief: Constructeur de la classe  
        :param parent: fenêtre mère
        :param titre: Titre de la fenêtre    
        """    
        # Création de l'application graphique
        self.app = wx.App(False)        
        # Création de la fenetre
        wx.Frame.__init__(self, parent, title=titre)        
        # Création du "sizer" principal
        sizer_principal = wx.BoxSizer(wx.VERTICAL)        
        # Création des boutons
        sizer_boutons = wx.BoxSizer(wx.HORIZONTAL)
        self.__ajouter_bouton(self.__copier, 'Copier', sizer_boutons)
        self.__ajouter_bouton(self.__coller, 'Coller', sizer_boutons)
        self.__ajouter_bouton(self.__enc, 'Enc', sizer_boutons)
        self.__ajouter_bouton(self.__dec, 'Dec', sizer_boutons)
        sizer_principal.Add(sizer_boutons)
        # Création de la zone de texte
        self.zone_texte = wx.TextCtrl(self, style=(wx.TE_MULTILINE), size=(-1, 400))
        sizer_principal.Add(self.zone_texte, 1, wx.EXPAND)       
        # Affichage
        self.SetBackgroundColour('white') # Couleur de fond de la fenêtre
        self.SetSizerAndFit(sizer_principal) # Définit le "sizer" + Dimensionnement automatique
        self.Show()
        self.zone_texte.SetFocus()        
        
    def __ajouter_bouton(self, callback, libelle, sizer):
        """
        :brief: Ajoute un bouton à l'interface
        :param callback: Fonction appelée lorsque le bouton est appuyé
        :param libelle: Texte affiché sur le bouton
        :param sizer: Sizer auquel le bouton doit être ajouté
        """  
        objet = wx.Button(self, -1, libelle)
        sizer.Add(objet)
        self.Bind(wx.EVT_BUTTON, callback, objet)
        
    def __copier(self, evenement):   
        self.zone_texte.SetFocus()
        self.zone_texte.SelectAll()
        self.zone_texte.Copy()
        
    def __coller(self, evenement):   
        self.zone_texte.SetValue('')
        self.zone_texte.Paste()
        
    def __enc(self, evenement):   
        resultat = base64.b64encode(self.zone_texte.GetValue().encode('utf-8'))
        self.zone_texte.SetValue(resultat)
        
    def __dec(self, evenement):  
        try:
            resultat = base64.b64decode(self.zone_texte.GetValue())
        except :
            pass
        else:    
            self.zone_texte.SetValue(resultat.decode('utf-8'))
    
    def run(self):
        """
        :brief: Lance l'interface graphique 
        """       
        # Lance l'application graphique
        self.app.MainLoop()    
        
#==============================================================================    
#                               M A I N    
#==============================================================================    
if __name__ == "__main__" :
    gui = InterfaceGraphique(parent=None, titre="EncDec")
    gui.run()     
    
    
    
