from collections import deque
import threading
import time
class StackShared:
    def __init__(self):
        self.stack = deque([],20)
        
    def push(self,object):
        #self.condition.acquire()
        self.stack.appendleft(object)
        #print(self.stack)
        #self.condition.notify_all()
    
    def pop(self):
        #self.condition.acquire()
        #while not self.stack:
        #    time.sleep(1)
            #self.condition.wait()
        if len(self.stack) > 19:
            print("MAAAAAAAAAAAAAAAAAAAAAAAAAX")
        return self.stack.pop()
        #print(self.stack)
        #self.condition.release()

    def containsID(self,id):
        return id in self.stack
        #return id in [x.getPacketID() for x in self.stack]