from classes import *
from ws_data import data
import time
import requests
import keyboard

from bytecanvas import ByteCanvas

def GetTest(WS):
    response = WS.GET("api/v0/process_state/active", printToggle=True, jsonToggle=True)
    WS.PrintOverview()

def DisplayTest(WS, text1 = "Test1"):
    WS.Scoreboard.Display(line1=text1, line2="Time: " + datetime.now().strftime("%H:%M:%S"), time=5)
    #WS.Scoreboard.DisplayNonsense("", "Test", time=1)

def ImageTest(WS):
    response = WS.GET('api/v0/scoreboard/graphic/image')
    response_bytes = bytearray(response.content)
    print(len(response_bytes))
    for i in range(len(response_bytes)):
        response_bytes[i] = 0
    for i in range(50):
        response_bytes[i] = (i % 50)

    final_image = bytes(response_bytes)
    response = WS.Scoreboard.PrintImage(final_image)

def BounceProgram():
    newCanvas = ByteCanvas()

    weldingWorkstation = data["workstations"]["welding1"]
    testWorkstation = data["workstations"]["test1"]
    # WS = WorkStation(weldingWorkstation['ip'], weldingWorkstation['name'])
    WS = WorkStation(testWorkstation['ip'], testWorkstation['name'])

    # newCanvas.DrawLine(40, 0, 40, 32, 'G4')
    newCanvas.Fill(0, 0, 80, 31, 'G4')
    newCanvas.Fill(35, 14, 45, 18, 'BLANK')
    
    x = 40
    y = 16
    vX = 1
    vY = 1
    isRunning = True
    while isRunning:
        # Clear the previous 'ball' position
        newCanvas.ClearPixel(x, y)

        x += vX
        y += vY
        
        # Collides with x-wall
        if bool(newCanvas.GetPixel(x, y - vY)):
            newCanvas.PaintPixel(x, y - vY, 'BLANK')
            x -= vX
            vX = -vX
            yNotTriggered = False
        # Collides with y-wall
        if bool(newCanvas.GetPixel(x-vX, y)):
            newCanvas.PaintPixel(x-vX, y, 'BLANK')
            y -= vY
            vY = -vY
        else: # Collides with corner-wall
            if bool(newCanvas.GetPixel(x, y) and yNotTriggered):
                newCanvas.PaintPixel(x, y, 'BLANK')
                x -= vX
                y -= vY
                vX = -vX
                vY = -vY
        yNotTriggered = False    

        # Collision with screen borders
        if (x >= 79): 
            vX = -1
        else:
            if x <= 0: 
                vX = 1

        if (y >= 31): 
            vY = -1
        else:
            if y <= 0: vY = 1

        # Update the ball position
        newCanvas.PaintPixel(x, y, 'R1')
        WS.Scoreboard.PrintImage(newCanvas.Output())
        
        time.sleep(0.1)

        # Quit if q is pressed
        if keyboard.is_pressed('q'):
            isRunning = False

def ControlProgram():
    newCanvas = ByteCanvas()

    weldingWorkstation = data["workstations"]["welding1"]
    testWorkstation = data["workstations"]["test1"]
    # WS = WorkStation(weldingWorkstation['ip'], weldingWorkstation['name'])
    WS = WorkStation(testWorkstation['ip'], testWorkstation['name'])
    x = 40
    y = 16
    vX = 1
    vY = 1
    isRunning = True
    deleteMode = True
    color = 7
    size = 10
    
    while isRunning:

        if deleteMode:
            newCanvas.Fill(x, y, x + size, y + size, 0)

        if keyboard.is_pressed('up'):
            y += -1
        if keyboard.is_pressed('left'):
            x += -1
        if keyboard.is_pressed('right'):
            x += 1
        if keyboard.is_pressed('down'):
            y += 1

        if keyboard.is_pressed('shift'):
            color += 1

        if keyboard.is_pressed('ctrl'):
            color -= 1

        if color < 0:
            color = 0
        if keyboard.is_pressed('d'):
            print(color)

        newCanvas.Fill(x, y, x + size, y + size, color)
        WS.Scoreboard.PrintImage(newCanvas.Output())
        
        time.sleep(0.1)

        if keyboard.is_pressed('q'):
            isRunning = False
        
        if keyboard.is_pressed('enter'):
            deleteMode = not deleteMode

def main():
    BounceProgram()
    # ControlProgram()
    
    return

    timeHours = 60 * 60 * 2
    WS2 = WorkStation(testWorkstation['ip'], testWorkstation['name'])

    i = 0
    while True:
        try: 
            WS2.Scoreboard.Display("Python Connected", time = timeHours)
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