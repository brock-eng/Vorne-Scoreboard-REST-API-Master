import requests
import webbrowser
import json
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
        print(datetime.now().strftime("%H:%M:%S"), ' - Display: ', response)

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
        response = self.ws.POST("api/v0/scoreboard/graphic/image?x=0&y=0&w=80&h=32", byteInformation, headersIn={'Content-Type': 'application/octet-stream'})
        if response.status_code != 200:
            print("HTTP ERROR: ", response.status_code)
        return response
    
    # Set the scoreboard display setting
    def SetImageMode(self, status) -> bool:
        if status not in ['none', 'trans', 'over', 'under']:
            return False
        else:
            response = self.ws.POST('api/v0/scoreboard/graphic/mode', json.dumps({'value' : status}))
            if response.status_code == 200:
                return True
            else:
                return False

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

    # Turns the scoreboard 'off'
    # Note that this doesn't actually turn off the power
    # Instead it displays a blank image overlay using direct screen control
    def TurnOff(self):
        imageMapBytes = bytes(7860)
        self.SetImageMode(imageMapBytes)


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
    def POST(self, query, setValue, headersIn = ""):
        requestIP = self.ip + query
        if (headersIn != ''):
            return requests.post(requestIP, setValue)
        else:
            return requests.post(requestIP, setValue, headers = headersIn)
    
    # Set current part run
    def SetPart(self, PartNo, serialMode = False) -> bool:
        serialHeaders = {"pkey" : "RIB26OGS3R7VRcaRMbVM90mjza"}
        vorneURL = "api/v0/part_run"
        if serialMode:
            response = requests.get("https://seats-api.seatsinc.com/ords/api1/serial/json/?serialno=" + PartNo + "&pkey=RIB26OGS3R7VRcaRMbVM90mjza")
            PartNo = response.json()['catalog_no']
            print(PartNo)

        partRunBase = {
            "part_id": PartNo,
            "ideal_cycle_time": 1,
            "takt_time": 1.2,
            "start_with_changeover": True,
            "changeover_reason": "part_change",
        }
        
        response = self.POST(vorneURL, json.dumps(partRunBase))

        return (response.status_code == 200)


    # Prints an overview of the current workstation, including state/reason/elapsed_time
    def PrintOverview(self):
        response = self.GET("api/v0/process_state/active", printToggle=False, jsonToggle=True)
        print("Workstation: " + self.name)
        print("Running: " + str(str(response['data']['name']) == 'running'))
        print("State  : " + response['data']['name'])
        print("Reason : " + response['data']['process_state_reason'])
        print("Time[s]: " + str(int(response['data']['elapsed'])))
        print("Time[m]: " + str(int(response['data']['elapsed'] / 60)))