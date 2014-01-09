# -*- coding: iso-8859-1 -*-
""" Module permetant l'utilisation de la'API de la freebox 
    (voir http://dev.freebox.fr/sdk/ et http://dev.freebox.fr/sdk/os )         
""" 
import os
import requests
import json
import time

#============================================================================== 
#                           C O N S T A N T E S
#============================================================================== 
TOKEN_FILE          = 'AppToken.txt'
REQUEST_API_VERSION = r'http://mafreebox.freebox.fr/api_version'
REQUEST_URL_BASE    = r'http://mafreebox.freebox.fr/api/v1/'

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
    nom_repertoire = split(nom_complet_de_ce_fichier)[0]    
    # Renvoie l'information
    return nom_repertoire 
    
def str2bool(chaine):
    """
    :brief: Conversion d'une chaine en booléen
    :param chaine: chaine à convertir
    :returns: Booléen correspondant
    """
    return chaine.lower() in ('yes', 'true', '1', 'oui', 'o')      
        
def print_debug(texte):
    """
    :brief: permet de publier des infos pour le debug
    :texte: Texte a publier
    """
    print texte    
    
class FreeboxAPI:
    """ Cette classe permet d'utiliser l'API HTTP de la freebox
    """
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
        # Connexion à la freebox
        self.__connection()
        
    def __reset_parametres_connection(self):
        """
        :brief: Supprime les paramètres de connexion
        """  
        # Paramètres de connection et d'autorisation
        self.cookie_connection      = None # Cookie à utiliser dans change requête HTTP
        self.app_token              = None # Permet à la Freebox d'enregistrer les applications autorisées        
        # Paramètres de la Freebox
        self.freebox_uid            = None
        self.freebox_device_name    = None
        self.freebox_api_version    = None
        self.freebox_api_base_url   = None
        self.freebox_device_type    = None         
    
    def __connection(self):
        """
        :brief: Utilise la requête 'API version' pour obtenir le cookie de connexion et des infos sur l'API
        """    
        # Reinitialise les paramètres
        self.__reset_parametres_connection()        
        # Demande des infos sur l'API
        reponse = requests.get(REQUEST_API_VERSION)  
        # Traitement de la réponse
        if(reponse.status_code == requests.codes.ok):
            # Recupère le cookie de connection qui est renvoyé dans l'entête de la réponse
            # on ne conserve que le nom et la valeur, on supprime les attributs path, date expiration ... 
            self.cookie_connection = reponse.headers.get('set-cookie').split(';')[0] 
            print_debug('cookie_connection: ' + self.cookie_connection)
            # Recupère les informations sur la Freebox
            self.freebox_uid            = reponse.json()['uid']
            self.freebox_device_name    = reponse.json()['device_name']
            self.freebox_api_version    = reponse.json()['api_version']
            self.freebox_api_base_url   = reponse.json()['api_base_url']           
            self.freebox_device_type    = reponse.json()['device_type']            
            # Saisie du token qui identifie l'application sur la Freebox
            self.__getAppToken()
            
    def __getAppToken(self):
        """
        :brief: Saisie du Token qui identifie l'application sur la Freebox (A partir d'un fichier ou demande à la Freebox)
        """    
        if (os.path.isfile(os.path.join(repertoire(), TOKEN_FILE)) == True):
            # Le Token est déjà enregistré dans un fichier, on l'utilise
            fichier = open(os.path.join(repertoire(), TOKEN_FILE), 'r')
            self.app_token = fichier.read()
            fichier.close()
            print_debug(u'Token lu depuis le fichier: ' + str(self.app_token))           
        else:
            print_debug(u'Demande d\'un token...')
            # Demande d'un Token à la Freebox
            requestUrl = REQUEST_URL_BASE + '/login/authorize/'
            headers = {'Content-type':'application/json', 'Cookie':self.cookie_connection}
            body    = json.dumps({"app_id": self.app_id, "app_name": self.app_name, "app_version": self.app_version, "device_name": self.device_name})
            reponse = requests.post(requestUrl, data=body, headers=headers)
            # Traitement de la réponse
            if(reponse.status_code == requests.codes.ok):
                if(str2bool(str(reponse.json()['success']))):
                    self.app_token = reponse.json()['app_token']
                    track_id       = reponse.json()['track_id']
                    # Ok, il faut maintenant attendre que l'autorisation soit confirmée
                    status = None
                    while(status != 'granted'):
                        reponse = requests.get(REQUEST_URL_BASE + '/login/authorize/' + track_id)
                        if(reponse.status_code == requests.codes.ok):
                            status = reponse.json()['status']
                        time.sleep(1)
                else:
                    print_debug(u'Erreur = ' + reponse.json())
            else:
                print_debug(u'Erreur = ' + reponse.status_code)

    
#==============================================================================    
#                               M A I N    
#==============================================================================    
if __name__ == "__main__" :  
    api = FreeboxAPI(app_id='com.app.toto', app_name='toto', app_version='1.0', device_name='laptop')



