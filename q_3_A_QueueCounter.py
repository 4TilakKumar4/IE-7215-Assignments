import random
import math

def failure():
    global s
    global sLast
    global tLast
    global area
    global nextFailure
    global nextRepair
    global queueCount
    
    s = s - 1
    
    ### Check if repair is ongoing
    if nextRepair == infinity:
        ### No repair ongoing, start immediately
        nextRepair = clock + 3.5
    else:
        ### Repair ongoing, add to queue count
        queueCount += 1
    
    ### Generate next failure if components still available
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
    global queueCount
    
    s = s + 1
    
    ### Check if more components waiting in queue
    if queueCount > 0:
        queueCount -= 1
        nextRepair = clock + 3.5 # Calculate new repair time
    else:
        nextRepair = infinity  # No more repairs
    
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
seed = 1234
random.seed(seed)

print(f"Random Seed: {seed}")
print("Running 100 replications...")

# Run 100 replications
sumS = 0
sumY = 0

for reps in range(0, 100, 1):
    nextFailure = math.ceil(6*random.random())
    nextRepair = infinity
    queueCount = 0
    
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
    
    sumS = sumS + area/clock
    sumY = sumY + clock

print(f"\nSystem Paramters: ")
print(f"Components in system: 3 (1 active + 2 spares)")
print(f"Repair time: 3.5 days")
print(f"Stop Condition: Total system failure, i.e S=0")


print(f"\nAverage time to system failure: {sumY/100:.2f} days")
print(f"Average number of functional components: {sumS/100:.4f}")