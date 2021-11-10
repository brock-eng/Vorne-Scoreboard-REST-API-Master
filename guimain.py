from webbrowser import Error
from classes import *
from ws_data import data
from tkinter import *
import subprocess

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

        # Keybinds
        self.root.bind('<Return>', self.RunCommand)
        self.root.bind('<Up>', self.GetRecentCommandUp)
        self.root.bind('<Down>', self.GetRecentCommandDown)

        # Misc class variables
        self.cmdHistory = list()
        self.cmdHistoryIndex = 0
        

    # Builds application gui
    def Build(self):
        self.consoleOutputLabel.place(x = 0)
        self.inputBar.focus_set()
        self.inputBar.pack(fill = X)
        self.consoleOutputLabel.pack(fill = X)
        self.consoleOutput.pack(fill = X)

        self.OutputConsole('Press ENTER to submit command. \'Help\' for command list.')

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
    def RunCommand(self, event):
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
            'STOP'      : self.Close,
            'QUIT'      : self.Close,
            'CLOSE'     : self.Close
        }

        cmd = str(self.inputBar.get().split()[0]).upper()
        arguments = self.inputBar.get().split()[1:]

        self.cmdHistory.append(self.inputBar.get())
        
        try:
            commands[cmd](arguments)
        except KeyError as error:
            self.OutputConsole('Command not found')
            self.OutputConsole({error})
        except IndexError as error:
            self.OutputConsole('Improper command arguments.  Type {help cmd} for cmd usage.')
            self.OutputConsole({error})
        except BaseException as error:
            self.OutputConsole('Unknown error: \'' + cmd + '\' ')
            self.OutputConsole({error})
        
        self.cmdHistoryIndex = 1
        self.inputBar.delete(first = 0, last = len(self.inputBar.get()))

    # Output a console message
    def OutputConsole(self, message):
        self.consoleOutput.insert(END, message)
        self.consoleOutput.insert(END, '\n')
        self.consoleOutput.see(END)

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
            result = wsObject.Scoreboard.SetImageDisplay(args[0][2])
            if not result:
               raise NameError('Invalid display mode -> {none, over, under, trans}')
            else:
                self.OutputConsole('Changed display mode for ' + str(args[0][1]) + ' to ' + str(args[0][2]) + '.')


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
List       - Display all workstation data
Msg        - Write a message to a WS
Open       - Opens a WS in browser
Update     - Update a WS
Add        - Add a WS
Delete     - Delete a WS
Quit       - Quit Application"""
        self.OutputConsole(helpBlock)
        
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