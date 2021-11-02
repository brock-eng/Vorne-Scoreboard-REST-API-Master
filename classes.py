import requests
import webbrowser
import json
import os
import time
from datetime import date, datetime
import random

sleep = lambda t: time.sleep(t)

# Scoreboard specific methods (displaying text, etc.)
class Scoreboard:
    def __init__(self, workstation) -> None:
        self.ws = workstation
    
    # Normal display message
    def Display(self, line1 = "", line2 = "", line3 = "", time=10) -> None:
        displayObject = self.CreateTextObject(line1, line2, line3, time)
        # print(displayObject)
        response = self.ws.POST("api/v0/scoreboard/overlay", json.dumps(displayObject))
        print('Display: ', response)

    # Continuously prints some random characters to the screen
    def DisplayNonsense(self, line1 = "", line2 = "", line3 = "", time=10) -> None:
        i = 0
        timestep = 2
        while i < 10:
            letters = ['a', 'b', 'c', 'd', 'e', 'f']
            displayObject = self.CreateTextObject(str(i), "".join([random.choice(letters) for x in range(20)]), line3, time)
            response = self.ws.POST("api/v0/scoreboard/overlay", json.dumps(displayObject))
            print('Display Nonsense: ' + str(i) + '-> ', response)
            sleep(timestep)
            i += 1

    # Warning display message
    def PrintImage(self, byteInformation):
        response = self.ws.POST("api/v0/scoreboard/graphic/image?x=0&y=0&w=80&h=32", byteInformation)
        print('Image Print: ', response)
        return response

    # Opens Scoreboard in the web browser
    def Open(self):
        webbrowser.open(self.ws.ip + '#!/view/scoreboard')

    # Creates a text dictionary object that displays on the scoreboard
    def CreateTextObject(self, line1 = "", line2 = "", line3 = "", time=10) -> dict:
        displayObject = {
            "duration": time,
            "text": [
                line1,
                line2,
                line3
            ]
        }
        return displayObject


# Class that holds all API methods for interacting with a Workstations Vorne scoreboard
# Initialize with an ip address and an optional workstation name
class WorkStation:
    
    # Initialize with an ip address
    def __init__(self, ipAddress, workstation = None) -> None:
        self.Scoreboard = Scoreboard(self)
        self.name = workstation
        self.ip = 'http://' + ipAddress + '/'

    # Open the current scoreboard dashboard
    def Open(self):
        webbrowser.open(self.ip + '#!/view/tpt')
    
    # Returns GET http based on a query
    def GET(self, query, printToggle = False, jsonToggle = False):
        requestIP = self.ip + query
        response = requests.get(requestIP)
        if (response.status_code != requests.codes.ok):
            raise Exception('Error: bad http request made by ' + self.workstation + ".\nRequested from: " + requestIP + "\nError code: " + str(response.status_code))

        if jsonToggle:
            if printToggle:
                parsed = json.loads(response.text)
                print(json.dumps(parsed, indent=4, sort_keys=True))
            return response.json()
        else:
            if printToggle:
                print(response.text + '\n')
            return response

    # Posts a value to a destination query in http
    def POST(self, query, setValue):
        requestIP = self.ip + query
        return requests.post(requestIP, setValue)

    # Prints an overview of the current workstation, including state/reason/elapsed_time
    def PrintOverview(self):
        response = self.GET("api/v0/process_state/active", printToggle=False, jsonToggle=True)
        print("Workstation: " + self.name)
        print("Running: " + str(str(response['data']['name']) == 'running'))
        print("State  : " + response['data']['name'])
        print("Reason : " + response['data']['process_state_reason'])
        print("Time[s]: " + str(int(response['data']['elapsed'])))
        print("Time[m]: " + str(int(response['data']['elapsed'] / 60)))