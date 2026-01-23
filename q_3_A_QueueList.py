import random
import math
import numpy as np

def failure():
    global s
    global sLast
    global tLast
    global area
    global nextFailure
    global nextRepair
    global repairQueue
    
    s -= 1
    
    # Check if repair is ongoing
    if nextRepair == infinity:
        # No repair ongoing, start immediately
        nextRepair = clock + 3.5
    else:
        # Repair ongoing, add to queue
        repairQueue.append(1) 
    

    # Generate next failure if spares still available
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

    
    # Schedule next repair if queue not empty
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
seed = 1234
random.seed(seed)

"""
For random seed for every run use the below code 
seed = random.randint(1,5)  # Random seed from 1-4
random.seed(seed)
print(f"Random Seed: {seed}")
"""

print()
print("PROBLEM 3.a: MODIFIED TTF SYSTEM (3 Components)")
print()
print(f"Configuration:")
print(f"  - Components: 3 (1 active + 2 spares)")
print(f"  - Repair Time: 3.5 days")
print(f"  - Component Lifetime: Discrete Uniform[1, 6] days")
print(f"  - Stop Condition: First system failure (S=0)")
print(f"  - Replications: 100")
print(f"  - Random Seed: {seed}")
print()

y = []
sBar = []

for reps in range(100):
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
    
    y.append(clock)
    sBar.append(area/clock)

mean_Y = np.mean(y)
std_Y= np.std(y, ddof=1)
ci_Y=[
    mean_Y - 1.96 * std_Y/math.sqrt(100),
    mean_Y + 1.96 * std_Y/math.sqrt(100)
]
mean_S = np.mean(sBar)
std_S = np.std(sBar, ddof=1)
ci_S = [
    mean_S - 1.96 * std_S / math.sqrt(100),
    mean_S + 1.96 * std_S / math.sqrt(100)
]

# Results
print()
print("SIMULATION RESULTS (100 Replications)")
print()
print()
print("1. EXPECTED TIME TO SYSTEM FAILURE")
print()
print(f"   Point Estimate: {mean_Y:.4f} days")
print(f"   Std Deviation: {std_Y:.4f}")
print(f"   95% CI: [{ci_Y[0]:.4f}, {ci_Y[1]:.4f}]")
print()
print("2. AVERAGE NUMBER OF FUNCTIONAL COMPONENTS")
print()
print(f"   Point Estimate: {mean_S:.4f}")
print(f"   Std Deviation: {std_S:.4f}")
print(f"   95% CI: [{ci_S[0]:.4f}, {ci_S[1]:.4f}]")
print()
