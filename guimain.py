from webbrowser import Error
from tkinter import *

import threading

from classes import *
from ws_data import data
from bytecanvas import *

from programs import Program

class Application(Frame):
    
    def __init__(self) -> None:
        # Create root
        self.root = Tk()
        self.root.title('Vorne Scoreboard Console Tool')
        
        # Creating Widgets
        self.inputBar = Entry()
        self.consoleOutputLabel = Label(text = 'Console Output')
        self.consoleOutput = Text()
        
        # Formatting Widgets
        self.Build()

        # Keybinds / Handlers
        self.root.bind('<Return>', self.RunCommand)
        self.root.bind('<Up>', self.GetRecentCommandUp)
        self.root.bind('<Down>', self.GetRecentCommandDown)
        self.root.protocol("WM_DELETE_WINDOW", self.OnClose)

        # Misc class variables
        self.cmdHistory = list()
        self.cmdHistoryIndex = 0
        self.runningPrograms = dict()
        
    # Builds application gui
    def Build(self):
        self.consoleOutputLabel.place(x = 0)
        self.inputBar.focus_set()
        self.inputBar.pack(fill = X)
        self.consoleOutputLabel.pack(fill = X)
        self.consoleOutput.pack(fill = X)
        self.consoleOutput.configure(state=DISABLED)

        self.OutputConsole('Press ENTER to submit command. \'Help\' for command list.')

    # Window close handling
    def OnClose(self):
        for program in self.runningPrograms:
            self.runningPrograms[program].Stop()
        
        self.root.destroy()

    # up-arrow for selecting a recent cmd
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
            'STOP'      : self.Close,
            'QUIT'      : self.Close,
            'CLOSE'     : self.Close,
            'SERIAL'    : self.PrintSampleSerial
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
    def OutputConsole(self, message):
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

    # Alters the current scoreboard
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
            if not resultDisplay:
                raise NameError('Error setting display mode to \'over\'')
            else:
                self.OutputConsole('Turned off scoreboard display for ' + str(args[0][1]))
                self.OutputConsole('Call \'display turnon {ws}\' to return to normal screen.')
            return
        
        if str(args[0][0]).upper() == 'TURNON':
            wsObject = WorkStation(data["workstations"][args[0][1]]["ip"])
            resultDisplay = wsObject.Scoreboard.SetImageMode('none')
            if not resultDisplay:
               raise NameError('Error posting \'turnon\' to scoreboard.')
            else:
                self.OutputConsole('Turned on scoreboard display for ' + str(args[0][1]) + '.')
            return

        if str(args[0][0]).upper() == 'RUN':
            if str(args[0][1]) in self.runningPrograms:
                self.runningPrograms[str(args[0][1])].Stop()
                self.runningPrograms.pop(str(args[0][1]))
                self.OutputConsole('Stopped program running at workstation: ' + str(args[0][1]))

            wsObject = WorkStation(data["workstations"][args[0][1]]["ip"])

            if str(args[0][2]).upper() == 'BOUNCE':
                newProgram = Program(str(args[0][1]))
                newThread = threading.Thread(target=newProgram.BounceProgram, args=(wsObject,))
                newThread.start()
                self.runningPrograms[str(args[0][1])] = newProgram
                self.OutputConsole('Running Bounce program on ' + str(args[0][1]))
                return
            
            if str(args[0][2]).upper() == 'CONTROL':
                newProgram = Program(str(args[0][1]))
                newThread = threading.Thread(target=newProgram.ControlProgram, args=(wsObject,))
                newThread.start()
                self.runningPrograms[str(args[0][1])] = newProgram
                self.OutputConsole('Running Control program on ' + str(args[0][1]))
                return
                
            if str(args[0][2]).upper() == 'BOUNCE2':
                newProgram = Program(str(args[0][1]))
                newThread = threading.Thread(target=newProgram.Bounce2Program, args=(wsObject, args[0][3]))
                newThread.start()
                self.runningPrograms[str(args[0][1])] = newProgram
                self.OutputConsole('Running Bounce2 program on ' + str(args[0][1]))
                return

            raise NameError('Program name not found.')

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
        # setpart ws serial
        wsObject = WorkStation(data["workstations"][args[0][0]]["ip"])
        postResult = wsObject.SetPart(args[0][1], serialMode=True)
        
        self.OutputConsole("Set {" + str(args[0][0]) + "} part run to " + str(args[0][1]) + ".") \
            if postResult else \
                self.OutputConsole("Error posting part run to: " + str(args[0][0]))



    # Opens a workstation in the browser
    def Open(self, *args):
        if (len(args[0]) == 0):
            raise NameError("OPEN cmd requires a workstation name")
        
        try:
            webbrowser.open(data["workstations"][args[0][0]]["ip"])
            self.OutputConsole("Opened workstation {name} in browser.".format(name = args[0]))
        except:
            raise NameError("Could not find path.")

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
            raise Error("Error posting message to display")


    
    # Outputs the help block
    def Help(self, *args):
        helpBlock = """
Commands:
Help       - Lists all commands
List       - Display all workstation data
Msg        - Write a message to a WS
Open       - Opens a WS in browser
Display    - Display/scoreboard specific commands
Quit       - Quit Application"""
        self.OutputConsole(helpBlock)
    
    # Prints a sample serial to console
    def PrintSampleSerial(self, *args):
        serial = "I3993893"
        self.root.clipboard_clear()
        self.root.clipboard_append(serial)
        self.OutputConsole("Copied sample serial to clipboard: " + serial)

    # Run the application
    def Run(self):
        self.root.mainloop()

    # Closes the application
    def Close(self, *args):
        self.root.destroy()
        

def main():
    ConsoleApp = Application()

    ConsoleApp.Run()


if __name__ == '__main__': main()