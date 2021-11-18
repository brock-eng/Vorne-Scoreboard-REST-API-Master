# Master control for vorne systems.
# Provides command line-esque functionality for 
# interacting with Vorne scoreboards
# Should only be used by IT or Admin users
#
# Version 1.0

from tkinter import *
import threading
from datetime import datetime

from workstation import *
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
        
        # Command History Support
        self.lastScannedCmd = ""
        self.cmdHistory = list()
        self.cmdHistoryIndex = 0

        # Tracked Running Programs
        self.runningPrograms = dict()
        self.runningApplications = list()
        self.runningApplicationsQueries = dict()
        self.pollingDuration = 1

        # Startup Message
        self.OutputConsole('Press ENTER to submit command. \'Help\' for command list.')

    # Builds and formats tkinter widgets
    def Build(self):
        # Create root
        self.root = Tk()
        self.root.title('Vorne Scoreboard Console Tool')
        
        # Creating Widgets
        self.inputBar = Entry()
        self.consoleOutputLabel = Label(text = 'Console Output')
        self.consoleOutput = Text()

        # Formatting Widgets
        self.root.iconbitmap('res\img\seats.ico')
        self.consoleOutputLabel.place(x = 0)
        self.inputBar.focus_set()
        self.inputBar.pack(fill = X)
        self.consoleOutputLabel.pack(fill = X)
        self.consoleOutput.pack(fill = BOTH)
        self.consoleOutput.configure(state=DISABLED)
        return
        

    # App configuration settings
    def Configure(self):
        # Set webbrowser path (set to use chrome)
        browser_path = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        #browser_path = "C:/Program Files/Internet Explorer/iexplore.exe"
        webbrowser.register("wb", None, webbrowser.BackgroundBrowser(browser_path))

        # Keybinds / Handlers
        self.root.bind('<Return>', self.RunCommand)
        self.root.bind('<Up>', self.GetRecentCommandUp)
        self.root.bind('<Down>', self.GetRecentCommandDown)
        self.root.protocol("WM_DELETE_WINDOW", self.OnClose)
        return

    # Support for using up-arrow for selecting a recent cmd
    def GetRecentCommandUp(self, event):
        if len(self.cmdHistory) < self.cmdHistoryIndex:
            return

        self.inputBar.delete(first = 0, last = len(self.inputBar.get()))
        self.cmdHistoryIndex += 1
        self.inputBar.insert(0, self.cmdHistory[-(self.cmdHistoryIndex - 1)])

    # down-arrow for selecting a recent cmd
    def GetRecentCommandDown(self, event):
        if self.cmdHistoryIndex <= 1:
            self.inputBar.delete(first = 0, last = len(self.inputBar.get()))
            return

        self.inputBar.delete(first = 0, last = len(self.inputBar.get()))
        self.cmdHistoryIndex -= 1
        self.inputBar.insert(0, self.cmdHistory[-self.cmdHistoryIndex])

    # Runs a command as entered in the entry bar
    def RunCommand(self, event, command = None):
        if (len(self.inputBar.get()) == 0):
            return

        commands = {
            'HELP'      : self.Help,
            'LIST'      : self.List,
            'OPEN'      : self.Open,
            'MESSAGE'   : self.Message,
            'MSG'       : self.Message,
            'WRITE'     : self.Message,
            'DISPLAY'   : self.Display,
            'DISP'      : self.Display,
            'SETPART'   : self.SetPartNo,
            'GETPART'   : self.GetPartRun,
            'DOWNTIME'  : self.Downtime,
            'PSCAN'     : self.PScan,
            'POLL'      : self.StartPolling,
            'STOPPOLL'  : self.StopPolling,
            'POLLSTOP'  : self.StopPolling,
            'SERIAL'    : self.PrintSampleSerial,
            'COUNT'     : self.PushCount,
            'REJECT'    : self.PushReject,
            'STOP'      : self.OnClose,
            'QUIT'      : self.OnClose,
            'CLOSE'     : self.OnClose
        }

        cmd = str(self.inputBar.get().split()[0]).upper()
        arguments = self.inputBar.get().split()[1:]

        self.cmdHistory.append(self.inputBar.get())
        
        try:
            commands[cmd](arguments)
        except KeyError as error:
            self.OutputConsole('Command argument/sub-argument not found.')
            self.OutputConsole({error})
        except IndexError as error:
            self.OutputConsole('Improper command arguments.  Type {help cmd} for cmd usage.')
            self.OutputConsole({error})
        except BaseException as error:
            self.OutputConsole('Program Error: \'' + cmd + '\' ')
            self.OutputConsole({error})
        
        self.cmdHistoryIndex = 1
        self.inputBar.delete(first = 0, last = len(self.inputBar.get()))

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
                wsObject = WorkStation(data["workstations"][ws]["ip"])
                try:
                    response = wsObject.GET("api/v0/process_state/active", printToggle=False, jsonToggle=False)
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
            wsObject = WorkStation(data["workstations"][args[0][1]]["ip"])
            result = wsObject.Scoreboard.SetImageMode(args[0][2])
            if not result:
               raise NameError('Invalid display mode -> {none, over, under, trans}')
            else:
                self.OutputConsole('Changed display mode for ' + str(args[0][1]) + ' to ' + str(args[0][2]) + '.')
            return

        if str(args[0][0]).upper() == 'TURNOFF':
            if str(args[0][1]) in self.runningPrograms:
                self.runningPrograms[str(args[0][1])].Stop()
                self.runningPrograms.pop(str(args[0][1]))
                self.OutputConsole('Stopped program running at workstation: ' + str(args[0][1]))

            wsObject = WorkStation(data["workstations"][args[0][1]]["ip"])
            blankCanvas = ByteCanvas()
            result = wsObject.Scoreboard.PrintImage(blankCanvas.Output())
            resultDisplay = wsObject.Scoreboard.SetImageMode('over')
            if not result:
                raise NameError('Improper arguments called for \'display turnoff\' command')
            elif not resultDisplay:
                raise NameError('Error setting display mode to \'over\'')
            else:
                self.OutputConsole('Turned off scoreboard display for ' + str(args[0][1]))
                self.OutputConsole('Call \'display turnon {ws}\' to return to normal screen.')
            return
        
        if str(args[0][0]).upper() == 'TURNON':
            wsObject = WorkStation(data["workstations"][args[0][1]]["ip"])
            resultDisplay = wsObject.Scoreboard.SetImageMode('none')
            if not resultDisplay: raise NameError('Error posting \'turnon\' to scoreboard.')
            else: self.OutputConsole('Turned on scoreboard display for ' + str(args[0][1]) + '.')
            return

        # Run a custom program on the screen.
        if str(args[0][0]).upper() == 'RUN':
            wsName = str(args[0][1])
            programName = str(args[0][2]).upper()
            wsObject = WorkStation(data["workstations"][wsName]["ip"])
            
            # Stop currently runnin program if there is one
            if wsName in self.runningPrograms:
                self.runningPrograms[wsName].Stop()
                self.runningPrograms.pop(wsName)
                self.OutputConsole('Stopped program running at workstation: ' + wsName)

            newProgram = Program(wsName)
            if len(args[0]) > 3: progArgs = (wsObject, args[0][3])
            else: progArgs = (wsObject, )
            programList = {
                'BOUNCE'    : newProgram.BounceProgram,
                'CONTROL'   : newProgram.ControlProgram,
                'COUNT'     : newProgram.CountProgram,
                'BOUNCE2'   : newProgram.Bounce2Program
            }
            if programName not in programList.keys():
                raise NameError('Program name not found.')
            
            # if not set to image display, change to over
            if wsObject.Scoreboard.GetImageMode() != "over":
                if programName != 'COUNT': 
                    self.Display(["TURNOFF", args[0][1]])

            newThread = threading.Thread(target=programList[programName], args=progArgs)
            newThread.start()
            self.runningPrograms[wsName] = newProgram
            self.OutputConsole('Running {program_name} program on {ws}'.format(program_name = programName, ws = wsName))
            return

        if str(args[0][0]).upper() == 'STOP':
            if str(args[0][1]) not in self.runningPrograms:
                raise RuntimeError('No program running on that workstation.')
            self.runningPrograms[str(args[0][1])].Stop()
            self.runningPrograms.pop(str(args[0][1]))
            self.OutputConsole('Stopped program running at workstation: ' + str(args[0][1]))
            return
        
        raise NameError('Display subcommand not found: ' + str(args[0][0]))

    # Sets a part run based on a serial number
    def SetPartNo(self, *args):
        # Set display to on if not already on
        wsObject = WorkStation(data["workstations"][args[0][0]]["ip"])
        if wsObject.Scoreboard.GetImageMode() != "none":
            self.Display(["TURNON", args[0][0]])

        # set serial mode if serial tag is included in cmd
        serial = True if "-serial" in args[0] else False    
        changeOverMode = True if "-changeover" in args[0] else False
        
        if serial:
            SerialNum = args[0][1]
            PartNo = self.ConvertSerial(SerialNum)
        else:
            PartNo = args[0][1]

        # Check if current part run matches new part run
        # If true then cancel the part run (it's already running the part)
        currentPartNo = wsObject.GET("api/v0/part_run", jsonToggle=True)["data"]["part_id"]
        print(currentPartNo)

        if str(PartNo) == str(currentPartNo):
            self.OutputConsole("Did not set new part run: {" + str(PartNo) + "} is already in production.")
            return

        # Call set part command
        postResult = wsObject.SetPart(PartNo, changeOver=changeOverMode)
        
        self.OutputConsole("Set {" + str(args[0][0]) + "} part run to " + str(PartNo) + ".")
        return

    # Print information about the current part run in the console
    def GetPartRun(self, *args):
        wsObject = WorkStation(data["workstations"][args[0][0]]["ip"])
        returnData = wsObject.GET("api/v0/part_run", jsonToggle=True)

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
            wsObject = WorkStation(data["workstations"][args[0][0]]["ip"])
    
        except:
            raise NameError("Workstation not found.")
        
        msg = ' '.join(args[0][1:])
        
        try:
            wsObject.Scoreboard.Display(msg)
            self.OutputConsole('Printed to {' + str(args[0][0]) + '}: \"' + msg + '\"')
        except:
            raise IndexError("Error posting message to display")
        return
    
    # Disables active state detection and provides a downtime reason
    def Downtime(self, *args):
        self.OutputConsole("Downtime command causes errors - deprecated indefinitely.")
        return
        wsObject = WorkStation(data["workstations"][args[0][0]]["ip"])
        wsObject.POST("api/v0/process_state/reason", json.dumps({"value" : str(args[0][1])}))

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
Pscan      - Force a single read/command from a scoreboard
Poll       - Start polling a scoreboard
Stoppoll   - Stop polling a scoreboard
Setstate   - Set the machine state (deprecated)
Serial     - Copy a sample serial number to the clipboard
Count      - Pushes a 'Good Count' event to a scoreboard
Quit       - Quit Application"""

        self.OutputConsole(helpBlock)
        return

    # Starts continuous polling of a workstation
    # Gets the unrecognized scan and triggers actions
    def StartPolling(self, *args):
        wsObject = WorkStation(data["workstations"][args[0][0]]["ip"], name=str(args[0][0]))
        if wsObject.ip in self.runningApplications:
            self.OutputConsole('Polling already active at workstation: ' + str(args[0][0]))
        else:
            newThread = threading.Thread(target=self.PollingLoop, args=(wsObject,))
            newThread.start()
            self.runningApplications.append(wsObject.ip)
            self.OutputConsole('Started polling at ' + wsObject.ip)

        return

    # Stops the continuous polling of a workstation
    # if the ws is currently polling
    def StopPolling(self, *args):
        if "-all" in args[0]:
            self.runningApplications.clear()
            self.OutputConsole('Stopped polling at all workstations.')
            return
        
        wsObject = WorkStation(data["workstations"][args[0][0]]["ip"])
        if wsObject.ip in self.runningApplications:
            self.runningApplications.remove(wsObject.ip)
            self.OutputConsole('Stopped polling at workstation: ' + str(args[0][0]))
        else:
            self.OutputConsole('Not currently polling at workstation: ' + str(args[0][0]))
        return

    # Constantly polls the WS and processes its last unrecognized scan
    def PollingLoop(self, wsObject):
        # Get latest unrecognized scan and store it in dict
        self.runningApplicationsQueries[wsObject] = wsObject.GetScanID()

        # Main poll loop
        while wsObject.ip in self.runningApplications:
            print("Polling at ", wsObject.ip)
            self.HandleLastScan(wsObject, pollMode = True)
            time.sleep(self.pollingDuration)

        print("Done polling at", wsObject.ip)
        return

    # Single poll command for a ws
    def PScan(self, *args):
        wsname = str(args[0][0])
        wsObject = WorkStation(data["workstations"][wsname]["ip"], name = wsname)
        self.HandleLastScan(wsObject, pollMode = False)
        return

    # Handles the latest unrecognized scan
    def HandleLastScan(self, wsObject, pollMode = False):
        scannedText = wsObject.GetScan()
        scanNumber = wsObject.GetScanID()
        wsname = wsObject.name

        # Continuous polling behavior handling
        if pollMode:
            # if returned scan is equal to previous, do nothing
            if scanNumber == self.runningApplicationsQueries[wsObject]:
                return
            else:
                self.runningApplicationsQueries[wsObject] = scanNumber

        self.OutputConsole("Last unrecognized scan: {content}".format(content = scannedText), printMode = not pollMode)
        
        # Begin scannedText handling
        if scannedText[0:4] == '%CUS': # detect if custom tag
            self.OutputConsole("Detected custom command: " + scannedText[4:])
            CustomCommand = scannedText[4:]
            self.RunScannedCommand(str(CustomCommand).upper(), wsname)

        elif scannedText[0] == 'S': # SN
            
            self.OutputConsole("Detected SN.")
            self.ConvertSerialPartRun(wsObject, scannedText)
        else:
            self.OutputConsole("Unrecognized barcode: " + scannedText)
        return

    # Runs a custom scanned command 
    def RunScannedCommand(self, cmd, wsName):
        cmd = str(cmd).rstrip()

        if cmd == "OPERATORS--":
            self.Display(["run", wsName, "control"],)
        elif cmd == "OPERATORS++":
            self.SetPartNo(["test1", "Sample"])
        elif cmd == "TURNOFF":
            self.Display(["turnoff", wsName])
        elif cmd == "TURNON":
            self.Display(["turnon", wsName])
        elif cmd == "OPENLINK1":
            webbrowser.get("wb").open("https://www.google.com/")
        elif cmd == "FUNTIMES":
            self.Display(["run", wsName, "bounce2", 5],)
        else:
            self.OutputConsole("Warning: Command not found.")

    # Reads the last unrecognized scan
    # Converts to catalog number and starts a new part run
    def ConvertSerialPartRun(self, ws, serialNum):
        serialNumParsed = str(serialNum[1:]).rstrip()   # remove 'S' and '\r' from SN
        
        # Convert serial to catalog
        partNo = self.ConvertSerial(serialNumParsed)

        # Check if current part run matches new part run
        # If true then cancel the part run (it's already running the part)
        currentPartNo = ws.GET("api/v0/part_run", jsonToggle=True)["data"]["part_id"]

        if str(partNo) == str(currentPartNo):
            self.OutputConsole("Did not set new part run: {" + str(partNo) + "} is already in production.")
            return

        # Submit new part run based on catalog num
        result = ws.SetPart(partNo)

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
        except: raise IndexError("Could not find PartNo for given serial: {" + serial + "}")
        return partNo

    # Pushes a single good count into a scoreboard
    def PushCount(self, *args):
        wsObject = wsObject = WorkStation(data["workstations"][args[0][0]]["ip"], name=str(args[0][0]))
        count = args[0][1]
        wsObject.InputPin(1, count)
        self.OutputConsole("Pushed good count of {count} to {name}".format(count=count, name = wsObject.name))
        return

    # Pushes a rejected count into a scoreboard
    def PushReject(self, *args):
        wsObject = wsObject = WorkStation(data["workstations"][args[0][0]]["ip"], name=str(args[0][0]))
        count = args[0][1]
        wsObject.InputPin(2, count)
        self.OutputConsole("Pushed rejected count of {count} to {name}".format(count=count, name = wsObject.name))
        return

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
