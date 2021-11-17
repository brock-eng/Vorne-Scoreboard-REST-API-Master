# End user branch for the vorne scoreboard tool.
# This branch has reduced features and is mostly used
# for polling a scoreboard and activating barcode commands

from tkinter import *
import threading
import webbrowser
import yaml

from classes import *
from ws_data import data
from bytecanvas import *
from programs import Program

class Application(Frame):
    # Application startup
    def __init__(self) -> None:
        # Create and format widgets
        self.Build()

        # Configure App, set Keybinds, class variables, etc.
        self.Configure()

        # Tracked Running Programs
        self.runningPrograms = dict()
        self.runningApplications = list()
        self.runningApplicationsQueries = dict()
        self.pollingDuration = 1

        # App title
        self.root.title('Seats-Vorne Control Server'.format(version=self.version))

        # Start main control program
        self.StartPolling([self.ws])

        # Startup Message
        self.OutputConsole('Running for workstation: {name} at ip {ip}'.format(name=self.ws.name, ip=self.ws.ip))
        self.OutputConsole('Software Version: {version}'.format(version = self.version))

    # Builds and formats tkinter widgets
    def Build(self):
        # Create root
        self.root = Tk()
        
        # Creating Widgets
        self.consoleOutputLabel = Label(text = 'Console Output')
        self.consoleOutput = Text()
        
        # Formatting Widgets
        self.root.iconbitmap('res\img\seats.ico')
        self.consoleOutputLabel.place(x = 0)
        self.consoleOutputLabel.pack(fill = X)
        self.consoleOutput.pack(fill = BOTH)
        self.consoleOutput.configure(state=DISABLED)
        return
        

    # App configuration settings
    def Configure(self):
        # Opening config file and getting settings
        stream = open("config.yml", 'r')
        config = yaml.safe_load(stream)
        self.ws = WorkStation(ipAddress = config["ipAddress"], name = config["workstation"])
        self.version = config["version"]

        # Set webbrowser path (set to use chrome)
        browserPath = config["browserPath"]
        webbrowser.register("wb", None, webbrowser.BackgroundBrowser(browserPath))

        # Keybinds / Handlers
        self.root.protocol("WM_DELETE_WINDOW", self.OnClose)
        return


    # Output a console message
    def OutputConsole(self, message, printMode = True):
        if not printMode: return
        self.consoleOutput.configure(state='normal')
        self.consoleOutput.insert(END, '[' + datetime.now().strftime("%H:%M:%S") + ']')
        self.consoleOutput.insert(END, message)
        self.consoleOutput.insert(END, '\n')
        self.consoleOutput.see(END)
        self.consoleOutput.configure(state='disabled')

    # Shows all currently entered workstations
    def List(self, *args):
        statusFlag = False
        if len(args[0]) > 0:
            for arg in args:
                if arg[0] == '-status':
                    statusFlag = True

        for ws in data["workstations"]:
            if (statusFlag):
                try:
                    response = ws.self.GET("api/v0/process_state/active", printToggle=False, jsonToggle=False)
                    response = ' HTTP_STATUS/' + str(response.status_code)
                except:
                    response = ' HTTP_STATUS/NOT_FOUND'
            else:
                response = ''
            
            outputMessage = ws + ": IP/" + data["workstations"][ws]["ip"] + " - " + "Dept/" + data["workstations"][ws]["dept"] + response
            self.OutputConsole(outputMessage)

    # Alters the current scoreboard display
    def Display(self, *args):
        if str(args[0][0]).upper() == 'MODE':
            result = self.ws.Scoreboard.SetImageMode(args[0][1])
            if not result:
               raise NameError('Invalid display mode -> {none, over, under, trans}')
            else:
                self.OutputConsole('Changed display mode for ' + self.ws.name + ' to ' + str(args[0][2]) + '.')
            return

        if str(args[0][0]).upper() == 'TURNOFF':
            if str(self.ws.name) in self.runningPrograms:
                self.runningPrograms[self.ws.name].Stop()
                self.runningPrograms.pop(self.ws.name)
                self.OutputConsole('Stopped program running at workstation: ' + self.ws.name)

            blankCanvas = ByteCanvas()
            result = self.ws.Scoreboard.PrintImage(blankCanvas.Output())
            resultDisplay = self.ws.Scoreboard.SetImageMode('over')
            if not result:
               raise NameError('Improper arguments called for \'display turnoff\' command')
            if not resultDisplay:
                raise NameError('Error setting display mode to \'over\'')
            else:
                self.OutputConsole('Turned off scoreboard display for ' + self.ws.name)
                self.OutputConsole('Call \'display turnon {ws}\' to return to normal screen.')
            return
        
        if str(args[0][0]).upper() == 'TURNON':
            resultDisplay = self.ws.Scoreboard.SetImageMode('none')
            if not resultDisplay:
               raise NameError('Error posting \'turnon\' to scoreboard.')
            else:
                self.OutputConsole('Turned on scoreboard display for ' + self.ws.name + '.')
            return

        if str(args[0][0]).upper() == 'RUN':
            if self.ws.name in self.runningPrograms:
                self.runningPrograms[self.ws.name].Stop()
                self.runningPrograms.pop(self.ws.name)
                self.OutputConsole('Stopped program running at workstation: ' + self.ws.name)

            if self.ws.Scoreboard.GetImageMode() != "over":
                self.Display(["TURNOFF"])
            
            if str(args[0][2]).upper() == 'BOUNCE':
                newProgram = Program(self.ws.name)
                newThread = threading.Thread(target=newProgram.BounceProgram, args=(self.ws,))
                newThread.start()
                self.runningPrograms[self.ws.name] = newProgram
                self.OutputConsole('Running Bounce program on ' + self.ws.name)
                return
            
            elif str(args[0][2]).upper() == 'CONTROL':
                newProgram = Program(self.ws.name)
                newThread = threading.Thread(target=newProgram.ControlProgram, args=(self.ws,))
                newThread.start()
                self.runningPrograms[self.ws.name] = newProgram
                self.OutputConsole('Running Control program on ' + self.ws.name)
                return
                
            elif str(args[0][2]).upper() == 'BOUNCE2':
                newProgram = Program(self.ws.name)
                newThread = threading.Thread(target=newProgram.Bounce2Program, args=(self.ws, args[0][3]))
                newThread.start()
                self.runningPrograms[self.ws.name] = newProgram
                self.OutputConsole('Running Bounce2 program on ' + self.ws.name)
                return

            raise NameError('Program name not found.')

        if str(args[0][0]).upper() == 'STOP':
            if self.ws.name not in self.runningPrograms:
                raise RuntimeError('No program running on that workstation.')
            self.runningPrograms[self.ws.name].Stop()
            self.runningPrograms.pop(self.ws.name)
            self.OutputConsole('Stopped program running at workstation: ' + self.ws.name)
            return
            
        
        raise NameError('Display subcommand not found: ' + str(args[0][0]))

    # Sets a part run based on a serial number
    def SetPartNo(self, *args):
        # Set display to on if not already on
        if self.ws.Scoreboard.GetImageMode() != "none":
            self.Display(["TURNON"])

        # set serial mode if serial tag is included in cmd
        serial = True if "-serial" in args[0] else False    
        changeOverMode = True if "-changeover" in args[0] else False
        
        if serial:
            SerialNum = args[0][0]
            PartNo = self.ConvertSerial(SerialNum)
        else:
            PartNo = args[0][0]

        # Check if current part run matches new part run
        # If true then cancel the part run (it's already running the part)
        currentPartNo = self.ws.GET("api/v0/part_run", jsonToggle=True)["data"]["part_id"]
        print(currentPartNo)

        if str(PartNo) == str(currentPartNo):
            self.OutputConsole("Did not set new part run: {" + str(PartNo) + "} is already in production.")
            return

        # Call set part command
        postResult = self.ws.SetPart(PartNo, changeOver=changeOverMode)
        
        self.OutputConsole("Set {" + self.ws.name + "} part run to " + str(PartNo) + ".")
        return

    # Print information about the current part run in the console
    def GetPartRun(self, *args):
        self.ws = WorkStation(data["workstations"][args[0][0]]["ip"])
        returnData = self.ws.GET("api/v0/part_run", jsonToggle=True)

        self.OutputConsole("ID       : " + str(returnData["data"]["part_id"]))
        self.OutputConsole("Ideal (s): " + str(returnData["data"]["ideal_cycle_time"]))
        self.OutputConsole("Takt  (s): " + str(returnData["data"]["takt_time"]))
        self.OutputConsole("DT Thresh: " + str(returnData["data"]["down_threshold"]))
        return

    # Opens a workstation in the browser
    def Open(self, *args):
        if (len(args[0]) == 0):
            raise NameError("OPEN cmd requires a workstation name")
        
        try:
            webbrowser.get("wb").open(data["workstations"][args[0][0]]["ip"])
            self.OutputConsole("Opened workstation {name} in browser.".format(name = args[0]))
        except:
            raise NameError("Could not find path.")
        return

    # Send a one line string message to a display
    def Message(self, *args):
        if (len(args[0]) == 0):
            raise NameError("MESSAGE cmd requires a workstation name")
        try:
            self.ws = WorkStation(data["workstations"][args[0][0]]["ip"])
    
        except:
            raise NameError("Workstation not found.")
        
        msg = ' '.join(args[0][1:])
        
        try:
            self.ws.Scoreboard.Display(msg)
            self.OutputConsole('Printed to {' + str(args[0][0]) + '}: \"' + msg + '\"')
        except:
            raise Error("Error posting message to display")
        return
    
    # Disables active state detection and provides a downtime reason
    def Downtime(self, *args):
        self.OutputConsole("Downtime command causes errors - deprecated indefinitely.")
        return
        self.ws = WorkStation(data["workstations"][args[0][0]]["ip"])
        self.ws.POST("api/v0/process_state/reason", json.dumps({"value" : str(args[0][1])}))

    # Outputs the help block
    def Help(self, *args):
        helpBlock = """
Commands:
Help       - Lists all commands
List       - Display all workstation data
Msg        - Write a message to a WS
Open       - Opens a WS in browser
Display    - Display/scoreboard specific commands
Setpart    - Change the current part run to a new part
Getpart    - Get info on the current part run
Serial     - Copy a sample serial number to the clipboard
Setstate   - Set the machine state
Quit       - Quit Application"""
        self.OutputConsole(helpBlock)
        return

    # Starts continuous polling of a workstation
    # Gets the unrecognized scan and triggers actions
    def StartPolling(self, *args):
        if self.ws.ip in self.runningApplications:
            self.OutputConsole('Polling already active at workstation: ' + str(args[0][0]))
        else:
            newThread = threading.Thread(target=self.PollingLoop)
            newThread.start()
            self.runningApplications.append(self.ws.ip)
            self.OutputConsole('Started polling at ' + self.ws.ip)

        return

    # Stops the continuous polling of a workstation
    # if the ws is currently polling
    def StopPolling(self, *args):
        if "-all" in args[0]:
            self.runningApplications.clear()
            self.OutputConsole('Stopped polling at all workstations.')
            return
        
        if self.ws.ip in self.runningApplications:
            self.runningApplications.remove(self.ws.ip)
            self.OutputConsole('Stopped polling at workstation: ' + self.ws.name)
        else:
            self.OutputConsole('Not currently polling at workstation: ' + self.ws.name)
        return

    # Constantly polls the WS and processes its last unrecognized scan
    def PollingLoop(self):
        # Get latest unrecognized scan and store it in dict
        self.runningApplicationsQueries[self.ws] = self.ws.GetScanID()

        # Main poll loop
        while self.ws.ip in self.runningApplications:
            print("Polling at ", self.ws.ip)
            self.HandleLastScan(pollMode = True)
            time.sleep(self.pollingDuration)

        print("Done polling at", self.ws.ip)
        return

    # Single poll command for a ws
    def PScan(self, *args):
        self.HandleLastScan(pollMode = False)
        return

    # Handles the latest unrecognized scan
    def HandleLastScan(self, pollMode = False):
        scannedText = self.ws.GetScan()
        scanNumber = self.ws.GetScanID()
        wsname = self.ws.name

        # Continuous polling behavior handling
        if pollMode:
            # if returned scan is equal to previous, do nothing
            if scanNumber == self.runningApplicationsQueries[self.ws]:
                return
            else:
                self.runningApplicationsQueries[self.ws] = scanNumber

        self.OutputConsole("Last unrecognized scan: {content}".format(content = scannedText), printMode = not pollMode)
        
        # Begin scannedText handling
        if scannedText[0:4] == '%CUS': # detect if custom tag
            self.OutputConsole("Detected custom command: " + scannedText[4:])
            CustomCommand = scannedText[4:]
            self.RunScannedCommand(str(CustomCommand).upper())

        elif scannedText[0] == 'S': # SN
            
            self.OutputConsole("Detected SN.")
            self.ConvertSerialPartRun(serialNum = scannedText)
        else:
            self.OutputConsole("Unrecognized barcode: " + scannedText)
        return

    # Runs a custom scanned command 
    def RunScannedCommand(self, cmd):
        cmd = str(cmd).rstrip()
        nullArg = "***NULLARGUMENT_THIS_SHOULD_NOT_BE_USED"
        if cmd == "OPERATORS--":
            self.Display(["run", nullArg,"control"],)
        elif cmd == "OPERATORS++":
            self.SetPartNo(["Sample"])
        elif cmd == "TURNOFF":
            self.Display(["turnoff"])
        elif cmd == "TURNON":
            self.Display(["turnon"])
        elif cmd == "OPENLINK1":
            webbrowser.get("wb").open("https://en.wikipedia.org/wiki/SCADA")
        elif cmd == "FUNTIMES":
            self.Display(["run", nullArg, "bounce2", 5],)
        else:
            self.OutputConsole("Warning: Command not found.")

    # Reads the last unrecognized scan
    # Converts to catalog number and starts a new part run
    def ConvertSerialPartRun(self, serialNum):
        serialNumParsed = str(serialNum[1:]).rstrip()   # remove 'S' and '\r' from SN
        
        # Convert serial to catalog
        partNo = self.ConvertSerial(serialNumParsed)

        # Check if current part run matches new part run
        # If true then cancel the part run (it's already running the part)
        currentPartNo = self.ws.GET("api/v0/part_run", jsonToggle=True)["data"]["part_id"]

        if str(partNo) == str(currentPartNo):
            self.OutputConsole("Did not set new part run: {" + str(partNo) + "} is already in production.")
            return

        # Submit new part run based on catalog num
        result = self.ws.SetPart(partNo)

        if result:
            self.OutputConsole("Converted Serial {SN} to new part run: {PN}".format(SN = serialNum, PN = partNo))
        else:
            self.OutputConsole("Failed to convert serial to new part run.")
        return


    # Prints a sample serial to console
    def PrintSampleSerial(self, *args):
        serial = "I3993893"
        self.root.clipboard_clear()
        self.root.clipboard_append(serial)
        self.OutputConsole("Copied sample serial to clipboard: " + serial)

    # Grab a catalog number using the seats-api endpoint
    def ConvertSerial(self, serial):
        response = requests.get("https://seats-api.seatsinc.com/ords/api1/serial/json/?serialno=" + serial + "&pkey=RIB26OGS3R7VRcaRMbVM90mjza")
        try: partNo = response.json()['catalog_no']
        except: raise Error("Could not find PartNo for given serial: {" + serial + "}")
        return partNo

    # Run the application
    def Run(self):
        self.root.mainloop()

    # Window close handling
    def OnClose(self, *args):
        for program in self.runningPrograms:
            self.runningPrograms[program].Stop()

        for app in self.runningApplications:
            self.runningApplications.remove(app)
        
        time.sleep(self.pollingDuration * 1.25)
        self.root.destroy()

        
def main():
    ConsoleApp = Application()
    ConsoleApp.Run()


if __name__ == '__main__': main()
