import threading

class Debugger():
    def __init__(self,table):
        self.table = table
        pass
    
    def debugger(self,name):
        inp = input(name+"> ")
        while inp != "exit":
            if inp == "print":
                print(self.table.value)
            
            inp = input(name+"> ")
        pass
    
    def start(self):
        threading.Thread(target=self.debugger, args=("debugger",)).start()
