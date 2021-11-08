from classes import *
from ws_data import data
import time
import requests

def GetTest(WS):
    response = WS.GET("api/v0/process_state/active", printToggle=True, jsonToggle=True)
    WS.PrintOverview()

def DisplayTest(WS, text1 = "Test1"):
    WS.Scoreboard.Display(line1=text1, line2="Time: " + datetime.now().strftime("%H:%M:%S"), time=5)
    #WS.Scoreboard.DisplayNonsense("", "Test", time=1)

def ImageTest(WS):
    # WS.Scoreboard.Open()
    response = WS.GET('api/v0/scoreboard/graphic/image')
    print('Image Data: ', response.apparent_encoding)
    response_bytes = bytearray(response.content)
    print('Byte Array Size: ',len(response_bytes))
    for i in range(len(response_bytes)):
        response_bytes[i] = 2

    # print(response_bytes)
    final_image = bytes(response_bytes)
    response = WS.Scoreboard.PrintImage(final_image)
    
    response = WS.GET('api/v0/scoreboard/graphic/image')
    print(response.apparent_encoding)
    response_bytes = bytearray(response.content)
    # print(response_bytes)
    # print(len(response_bytes))
    for i in range(len(response_bytes)):
        response_bytes[i] = 2

    # print(response_bytes)
    final_image = bytes(response_bytes)
    print('Final output: ', len(final_image))
    response = WS.Scoreboard.PrintImage(final_image)


def main():
    
    weldingWorkstation = data["workstations"]["welding1"]
    testWorkstation = data["workstations"]["test1"]
    WS = WorkStation(weldingWorkstation['ip'], weldingWorkstation['name'])
    WS2 = WorkStation(testWorkstation['ip'], testWorkstation['name'])

    # WS.Scoreboard.Open()
    # DisplayTest(WS, text1 = "Hello World")
    # GetTest(WS)
    # ImageTest(WS)

    timeHours = 60 * 60 * 2
    WS2.Scoreboard.Open()
    
    i = 0
    while True:
        try: 
            WS2.Scoreboard.Display("Display.py run - " + str(i), datetime.now().strftime("%H:%M:%S"))
        except:
            print("Error connecting to display.")

        time.sleep(20)
        i += 1
    


    
    '''
    response = requests.get('https://seats-api.seatsinc.com/ords/api1/color_legend/json?empid=9146&workOrderNumber=SP44092197&workCenterNo=4209&orderType=SO&pkey=PsUxHibfqpoZKUiHBGkcXQTkU')
    print(response.text)
    print(response)
    '''


    

if __name__ == '__main__': main()