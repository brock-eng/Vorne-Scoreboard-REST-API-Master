from webbrowser import Error
from classes import *
from ws_data import data
from tkinter import *

class Application(Frame):
    
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title('Vorne Scoreboard Console Tool')
        
        # Widgets
        self.inputBar = Entry()
        self.consoleOutputLabel = Label(text = 'Console Output')
        self.consoleOutput = Text()

        self.Build()

        self.root.bind('<Return>', self.RunCommand)
    
    
    # Builds application gui
    def Build(self):
        self.consoleOutputLabel.place(x = 0)

        self.inputBar.pack(fill = X)
        self.consoleOutputLabel.pack(fill = X)
        self.consoleOutput.pack(fill = X)

    # Runs a command as entered in the entry bar
    def RunCommand(self, event):
        commands = {
            'HELP' : self.Help,
            'DISPLAYALL' : self.DisplayAll
        }

        cmd = str(self.inputBar.get().split()[0]).upper()
        arguments = str(self.inputBar.get().split()[1:]).upper()
        print(arguments)
        try:
            commands[cmd]()
        except KeyError as error:
            self.OutputConsole('Command not found')
            self.OutputConsole({error})
        except BaseException as error:
            self.OutputConsole('Unknown error: \'' + cmd + '\' ')
            self.OutputConsole({error})
        
        self.inputBar.delete(first = 0, last = len(self.inputBar.get()))

    # Shows all currently entered workstations
    def DisplayAll(self):
        for key, value in data["workstations"]:
            self.OutputConsole(key)
            self.OutputConsole(value)


    def OutputConsole(self, message):
        self.consoleOutput.insert(END, message)
        self.consoleOutput.insert(END, '\n')
        self.consoleOutput.see(END)
    

    def Help(self):
        helpBlock = """
Commands:
DisplayAll - Display all workstation data
Write      - Write a message to a WS
Update     - Update a WS
Add        - Add a WS
Delete     - Delete a WS """
        self.OutputConsole(helpBlock)
        
    # Run the application
    def Run(self):
        self.root.mainloop()
        

def main():
    ConsoleApp = Application()

    ConsoleApp.Run()

if __name__ == '__main__': main()