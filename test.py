from sharedStack import StackShared
import threading

s = StackShared()



def runA():
    while True:
        s.push(input(">> "))
    


def runB():
    while True:
        a = s.pop()
        print(a)
    pass



a = threading.Thread(target=runA)
b = threading.Thread(target=runB)

b.start()
a.start()

a.join()
b.join()