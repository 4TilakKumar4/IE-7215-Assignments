
import random
import math

   
def Failure():
    global S
    global sLast
    global tLast
    global area
    global nextFailure
    global nextRepair
    
    S = S - 1
    if S == 2:
        nextFailure = Clock + math.ceil(6*random.random())
        nextRepair = Clock + 3.5
    else:
        nextFailure = infinity
        
    if S>=0 and nextRepair == infinity:
        nextRepair = Clock +3.5

    area = area + sLast * (Clock - tLast)
    tLast = Clock
    sLast = S
    
def Repair():
    global S
    global sLast
    global tLast
    global area
    global nextFailure
    global nextRepair
    
    S = S + 1
    
    if S == 1:
        NextRepair = Clock + 3.5
        if nextFailure == infinity:
            nextFailure = Clock + math.ceil(6*random.random())
    else:
        nextRepair = infinity

    
    area = area + sLast * (Clock - tLast)
    tLast = Clock
    sLast = S
    
def Timer():
    global Clock
    global nextFailure
    global nextRepair
    
    if nextFailure < nextRepair:
        result = "Failure"
        Clock = nextFailure
        nextFailure = infinity
    else:
        result = "Repair"
        Clock = nextRepair
        nextRepair = infinity
    return result
    
    
infinity = 1000000
random.seed(123456)
SumS = 0
SumY = 0

nextFailure = math.ceil(6*random.random())
nextRepair = infinity

S = 2.0
sLast = 2.0
Clock = 0.0
tLast = 0.0
area = 0.0 
while S > 0:
    NextEvent = Timer()
    if NextEvent == "Failure":
        Failure()
    else:
        Repair()
            
SumS = SumS + area/Clock
SumY = SumY + Clock
        

print("Average failure at time " +  str(SumY/100) +
 " with average # of functional components " + str(SumS/100))