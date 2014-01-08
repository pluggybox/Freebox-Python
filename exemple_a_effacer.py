#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import logging
import time
import itertools
import json
import os
import sys

from hashlib import sha1
import hmac

class FreeboxApplication:


    def __init__(self):
        #I kept the same parameter name than the one use in freebox API for more readability
        self.app_id="DomosId"
        self.app_name="DomosApp"
        self.app_version="1"
        self.device_name="DomosDeviceName"
        #To know if the APP is register on freeboxOS side
        self.registerIntoFreeboxServer=False
        #Registration parameters
        self.app_token=""
        self.track_id=""
        self.challenge=""
        self.loadAppTokenFromFile()

    def __repr__(self):
        aRetString = ""
        aRetString = aRetString + "self.app_id: " + str(self.app_id)
        aRetString = aRetString + "self.app_name: " + str(self.app_name)
        aRetString = aRetString + "self.app_version: " + str(self.app_version)
        aRetString = aRetString + "self.device_name: " + str(self.device_name)
        aRetString = aRetString + "self.registerIntoFreeboxServer: " + str(self.registerIntoFreeboxServer)
        aRetString = aRetString + "self.app_token: " + str(self.app_token)
        aRetString = aRetString + "self.track_id: " + str(self.track_id)
        aRetString = aRetString + "self.challenge: " + str(self.challenge)
        return aRetString

    def getataForRequests(self):
        return json.dumps({"app_id": self.app_id,"app_name": self.app_name,"app_version": self.app_version,"device_name": self.device_name})

    def loadAppTokenFromFile(self):
        #Degeu...
        if (os.path.isfile("AppToken.txt")):
            aAppTokenBackupFile = open("AppToken.txt", "r")
            self.app_token = aAppTokenBackupFile.read()
            logging.info("APP token read from file. New APP token is : " + str(self.app_token))
            aAppTokenBackupFile.close()
        else:
            logging.info("No file for APP token - request a new one")
            self.initialLogging()
        #Fin Degeu

    def initialLogging(self):
        #only once. Register the APP on freebox side
        logging.info("Starting initial registration")
        aRequestUrl = "http://mafreebox.freebox.fr/api/v1/login/authorize/"
        aHeaders = {'Content-type': 'application/json', 'Accept': 'application/json'}

        logging.debug("URL used : " + aRequestUrl)
        logging.debug("Datas used : " + str(self.getataForRequests()))

        aRequestResult = requests.post(aRequestUrl, data=self.getataForRequests(), headers=aHeaders)
        logging.debug("Request result : " + str(aRequestResult))
        logging.debug("Request result : " + str(aRequestResult.json()))
        logging.debug("Registration result : " + str(aRequestResult.json()['success']))

        #if (aRequestResult.status_code != "200") or (aRequestResult.json()['success'] != True):
        if (aRequestResult.status_code != requests.codes.ok) or (aRequestResult.json()['success'] != True):
            logging.critical("Error during intial registration into Freebox Server")
        else:
            logging.debug("Please go to your Freebox. There should be a message saying that an application request access to freebox API. Please validate the request using the front display")
            self.app_token = aRequestResult.json()['result']['app_token']
            self.track_id = aRequestResult.json()['result']['track_id']
            logging.debug("app_token : " + str(self.app_token))
            logging.debug("track_id : " + str(self.track_id))
        logging.info("Ending initial registration")

        aLoopInd = 0
        while ((self.registerIntoFreeboxServer != True) and (aLoopInd < 10)):
            self.trackRegristration()
            time.sleep(15) # Delay for 1 minute (60 seconds)
            aLoopInd = aLoopInd + 1
        if (self.registerIntoFreeboxServer != True):
            logging.critical("Initial registration fails - Exiting with error")
            sys.exit(1)
        else:
            #Degeu...
            aAppTokenBackupFile = open("AppToken.txt", "w")
            aAppTokenBackupFile.write(self.app_token)
            aAppTokenBackupFile.close()
            #Fin Degeu

    def trackRegristration(self):
        logging.info("Starting trackRegristration")
        aRequestUrl = "http://mafreebox.freebox.fr/api/v1/login/authorize/" + str(self.track_id)
        aHeaders = {'Content-type': 'application/json', 'Accept': 'application/json'}

        logging.debug("URL used : " + aRequestUrl)

        aRequestResult = requests.get(aRequestUrl, headers=aHeaders)
        logging.debug("Request result : " + str(aRequestResult))
        logging.debug("Request result : " + str(aRequestResult.json()))
        if (aRequestResult.status_code != requests.codes.ok):
            logging.critical("Error during trackRegristration")
        else:
            if (aRequestResult.json()['result']['status'] == "granted"):
                logging.debug("OK during trackRegristration")
                self.registerIntoFreeboxServer=True
                self.challenge=aRequestResult.json()['result']['challenge']
                logging.info("APP is correclty registered")
        logging.info("Ending trackRegristration")

    def logWithPassword(self, iPassword):
        #only once. Register the APP on freebox side
        logging.info("Starting logWithPassword")
        aRequestUrl = "http://mafreebox.freebox.fr/api/v1/login/session/"
        aHeaders = {'Content-type': 'application/json', 'Accept': 'application/json'}

        logging.debug("URL used : " + aRequestUrl)

        aDataToLog = json.dumps({"app_id": self.app_id,"password": iPassword})

        logging.debug("Datas used : " + str(aDataToLog))

        aRequestResult = requests.post(aRequestUrl, data=aDataToLog, headers=aHeaders)
        logging.debug("Request result : " + str(aRequestResult))
        logging.debug("Request result : " + str(aRequestResult.json()))
        logging.debug("Registration result : " + str(aRequestResult.json()['success']))

        #if (aRequestResult.status_code != "200") or (aRequestResult.json()['success'] != True):
        if (aRequestResult.status_code != requests.codes.ok) or (aRequestResult.json()['success'] != True):
            logging.critical("Error during intial registration into Freebox Server")
        else:
            logging.debug("You re log")
        logging.info("Ending logWithPassword")

    def loginProcedure(self):
        logging.info("Starting loginProcedure")
        aRequestUrl = "http://mafreebox.freebox.fr/api/v1/login/"
        aHeaders = {'Content-type': 'application/json', 'Accept': 'application/json'}

        logging.debug("URL used : " + aRequestUrl)

        aRequestResult = requests.get(aRequestUrl, headers=aHeaders)
        logging.debug("Request result : " + str(aRequestResult))
        logging.debug("Request result : " + str(aRequestResult.json()))
        if (aRequestResult.status_code != requests.codes.ok):
            logging.critical("Error during loginProcedure")
        else:
            if (aRequestResult.json()['success'] == True):
                logging.debug("OK during loginProcedure")
                achallenge=aRequestResult.json()['result']['challenge']
                logging.info("We have the challenge : " + str(achallenge))
                return achallenge
            else:
                logging.critical("Error during loginProcedure")
        logging.info("Ending loginProcedure")

    def computePassword(self, iChallenge):
        hashed = hmac.new(self.app_token, iChallenge, sha1)
        logging.info("Password computed : " + str(hashed.digest().encode('hex')))
        return hashed.digest().encode('hex')

    def loginfull(self):
        aNewChallenge = self.loginProcedure()
        #password = hmac-sha1(app_token, challenge)
        #voir http://stackoverflow.com/questions/8338661/implementaion-hmac-sha1-in-python
        #http://stackoverflow.com/questions/13019598/python-hmac-sha1-vs-java-hmac-sha1-different-results
        aPassword = self.computePassword(aNewChallenge)
        self.logWithPassword(aPassword)

        
#==============================================================================    
#                               M A I N    
#==============================================================================    
if __name__ == "__main__" :        
    print ("Starting")

    aLogFileToUse='WifiAutoControl.log'

    #Clean previous log file
    with open(aLogFileToUse, 'w'):
        pass

    logging.basicConfig(filename=aLogFileToUse,level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')

    #aMyApp = FreeboxApplication()
    #aMyApp.loginfull()

    print ("Ending")

