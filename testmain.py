from classes import *

def GetTest(WS):
    response = WS.GET("api/v0/process_state/active", printToggle=True, jsonToggle=True)
    WS.PrintOverview()

def DisplayTest(WS):
    WS.Scoreboard.Display(line1="Test", line2="Time: " + datetime.now().strftime("%H:%M:%S"), time=5)
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
    weldingWorkstation = {
        "ip": "10.19.13.32",
        "name": "Welding Workstation"
    } 
    WS = WorkStation(weldingWorkstation['ip'], weldingWorkstation['name'])
    
    # WS.Scoreboard.Open()
    DisplayTest(WS)
    # GetTest(WS)
    # ImageTest(WS)

    

if __name__ == '__main__': main()