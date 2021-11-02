from classes import *

from tkinter import *

root = Tk()

# Builds application gui
def Build():
    global root

    root.title('Vorne Scoreboard Console Tool')
    
    input_bar = Entry()
    

    consoleOutputLabel = Label(
        text = 'Console Output',
    )
    consoleOutputLabel.place(
        x = 0
    )

    consoleOutput = Text()

    input_bar.pack(fill = X)
    consoleOutputLabel.pack(fill = X)
    consoleOutput.pack(fill = X)

def main():
    
    Build()


    root.mainloop()

if __name__ == '__main__': main()