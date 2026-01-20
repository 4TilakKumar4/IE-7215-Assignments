import random
import math

def failure():
    global s
    global sLast
    global tLast
    global area
    global nextFailure
    global nextRepair
    global repairQueue
    
    s -= 1
    
    ### Check if repair is ongoing
    if nextRepair == infinity:
        ### No repair ongoing, start immediately
        nextRepair = clock + 3.5
    else:
        ### Repair ongoing, add to queue
        repairQueue.append(1) 
    

    ### Generate next failure if spares still available
    if s > 0:
        nextFailure = clock + math.ceil(6*random.random())
    else:
        nextFailure = infinity
    
    area = area + sLast * (clock - tLast)
    tLast = clock
    sLast = s
    
def repair():
    global s
    global sLast
    global tLast
    global area
    global nextFailure
    global nextRepair
    global repairQueue
    
    s += 1
    
    ### Remove completed repair from queue
    repairQueue.pop(0)
    
    ### Schedule next repair if queue not empty
    if len(repairQueue) > 0:
        repairQueue.pop(0)
        nextRepair = clock + 3.5  
    else:
        nextRepair = infinity
    
    """
    1000 clock run IDEA
    If system was down (s was 0), generate new failure time
    if s == 1 and nextFailure == infinity:
        nextFailure = clock + math.ceil(6*random.random())
    """
    
    area = area + sLast * (clock - tLast)
    tLast = clock
    sLast = s
    
def timer():
    global clock
    global nextFailure
    global nextRepair
    
    if nextFailure < nextRepair:
        result = "Failure"
        clock = nextFailure
        nextFailure = infinity
    else:
        result = "Repair"
        clock = nextRepair
        nextRepair = infinity
    return result

# Parameters
infinity = 1000000
random.seed(1234)

"""
For random seed for every run use the below code 
seed = random.randint(1,5)  # Random seed from 1-4
random.seed(seed)
print(f"Random Seed: {seed}")
"""


print("\nRunning 100 replications >>>>>")

sumS = 0
sumY = 0
itr=1

for reps in range(0, 100, 1):
    nextFailure = math.ceil(6*random.random())
    nextRepair = infinity
    repairQueue = []  # Queue to track components in repair
    
    s = 3  # 3 components (1 active + 2 spares)
    sLast = 3
    clock = 0.0
    tLast = 0.0
    area = 0.0
    
    while s > 0:
        nextEvent = timer()
        if nextEvent == "Failure":
            failure()
        else:
            repair()
    itr +=1
    
    sumS = sumS + area/clock
    sumY = sumY + clock

print(f"\nAverage time to system failure: {sumY/100:.2f} days")
print(f"Average number of functional components: {sumS/100:.4f}")
print(f"Components in system: 3 (1 active + 2 spares)")
print(f"Repair time: 3.5 days")