#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json


#============================================================================== 
#                           C O N S T A N T E S
#============================================================================== 
TOKEN_FILE          = 'AppToken.txt'
REQUEST_URL_BASE    = 'http://mafreebox.freebox.fr/api/v1/'

#============================================================================== 
def repertoire():
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
        
def print_debug(texte):
    print texte
    
class FreeboxAPI:

    def __init__(self, app_id, app_name, app_version, device_name):
        """
        :brief: Constructeur de classe - Saisie du Token autorisant l'accès à la Freebox
        :param app_id:  Identifiant de l'application à enregistrer (ou déjà enregistrée) sur la Freebox
        :param app_name: Nom de l'application à enregistrer (ou déjà enregistrée) sur la Freebox
        :param app_version: Version de l'application à enregistrer (ou déjà enregistrée) sur la Freebox
        :param device_name: Identifiant de l'appareil (téléphone, PC...) sur lequel l'application est utilisée
        """
        # Paramètres permettant d'identifier l'application (et son appareil) à associer avec la Freebox (Permet de gérer les autorisations) 
        self.app_id         = app_id
        self.app_name       = app_name
        self.app_version    = app_version
        self.device_name    = device_name
        
        # Saisie des paramètres d'autorisation
        self.app_token = ''
        self.track_id  = ''
        self.challenge = ''        
        self.getAppToken()
        
    def getAppToken(self):
        """
        :brief: Saisie du Token autorisant l'accès à la Freebox (A partir d'un fichier ou demande à la Freebox)
        """    
        if (os.path.isfile(os.path.join(repertoire(), TOKEN_FILE)) == True):
            # Le Token est déjà enregistré dans un fichier, on l'utilise
            fichier = open(os.path.join(repertoire(), TOKEN_FILE), 'r')
            self.app_token = fichier.read()
            fichier.close()
            print_debug("Token lu depuis le fichier: " + str(self.app_token))           
        else:
            # Demande d'un Token à la Freebox
            self.requestAppToken()    
        
    def getataForRequests(self):
        """
        :brief: Renvoie
        """     
        return json.dumps({"app_id": self.app_id, "app_name": self.app_name, "app_version": self.app_version, "device_name": self.device_name})
        
    def requestAppToken(self):
        # Envoi de la requête HTTP POST
        requestUrl = REQUEST_URL_BASE + '/login/authorize/'
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resultat = requests.post(requestUrl, data=self.getataForRequests(), headers=headers)
        
        print_debug("Request result : " + str(resultat))
        print_debug("Request result : " + str(resultat.json()))
        print_debug("Registration result : " + str(resultat.json()['success']))    

    
#==============================================================================    
#                               M A I N    
#==============================================================================    
if __name__ == "__main__" :  
    api = FreeboxAPI(app_id='com.app.toto', app_name='toto', app_version='1.0', device_name='laptop')



