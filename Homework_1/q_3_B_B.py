import random
import math
import numpy as np

def failure():
    global s
    global sLast
    global tLast
    global area
    global downTime
    global nextFailure
    global nextRepair
    global queueCount
    global repairTime
    
    s -= 1
    
    r=random.random()
    if r<0.5:
        repairTime=1.25
    else:
        repairTime=2.75

    if nextRepair == infinity:
        nextRepair = clock + repairTime
    else:
        queueCount += 1
    
    if s > 0:
        nextFailure = clock + math.ceil(6*random.random())
    else:
        nextFailure = infinity  

    area = area + sLast * (clock - tLast)

    if sLast == 0:
        downTime = downTime + (clock - tLast)
    
    tLast = clock
    sLast = s

def repair():
    global s
    global sLast
    global tLast
    global area
    global downTime
    global nextFailure
    global nextRepair
    global queueCount
    global repairTime

    s += 1
    
    r=random.random()
    if r<0.5:
        repairTime=1.25
    else:
        repairTime=2.75
    
    if s == 1 and nextFailure == infinity:
        nextFailure = clock + math.ceil(6*random.random())
    
    # Check if more components waiting in queue
    if queueCount > 0:
        queueCount -= 1
        nextRepair = clock + repairTime  
    else:
        nextRepair = infinity  # No more repairs
    
    area = area + sLast * (clock - tLast)
    
    if sLast == 0:
        downTime = downTime + (clock - tLast)
    
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
maxTime = 1000
seed = 1234
random.seed(seed)

print()
print("PROBLEM 3.b.b: MODIFIED TTF SYSTEM SIMULATION - 1000 TIME UNITS & REPAIR TIME ~ UNIFORM{1.25,2.75}")
print()
print(f"Configuration:")
print(f"  - Components: 3 (1 active + 2 spares)")
print(f"  - Repair Time: X = 1.25 +1(0.5<R)(2.75-1.25) days, where R~uniform(0,1)")
print(f"  - Component Lifetime: Discrete Uniform[1, 6] days")
print(f"  - Simulation Length: {maxTime} time units")
print(f"  - Number of Replications: 100")
print(f"  - Random Seed: {seed}")
print()

proportionDown = []  
avgComponents = []   


for reps in range(100):
    nextFailure = math.ceil(6*random.random())
    nextRepair = infinity
    queueCount = 0
    
    s = 3  # 3 components (1 active + 2 spares)
    sLast = 3
    clock = 0.0
    tLast = 0.0
    area = 0.0
    downTime = 0.0  
    
    while clock < maxTime:       
        nextEventTime = min(nextFailure, nextRepair)

        if nextEventTime >= maxTime:  
            area = area + sLast * (maxTime - tLast)
    
            if sLast == 0:
                downTime = downTime + (maxTime - tLast)
            clock = maxTime
            break

        nextEvent = timer()
        if nextEvent == "Failure":
            failure()
        else:
            repair()
    
    # Calculate performance measures for this replication
    proportionDown.append(downTime / maxTime)
    avgComponents.append(area / maxTime)

# Calculate statistics across replications
mean_proportionDown = np.mean(proportionDown)
std_proportionDown = np.std(proportionDown, ddof=1)  
ci_proportionDown = [
    mean_proportionDown - 1.96 * std_proportionDown / math.sqrt(100),
    mean_proportionDown + 1.96 * std_proportionDown / math.sqrt(100)
]

mean_avgComponents = np.mean(avgComponents)
std_avgComponents = np.std(avgComponents, ddof=1)
ci_avgComponents = [
    mean_avgComponents - 1.96 * std_avgComponents / math.sqrt(100),
    mean_avgComponents + 1.96 * std_avgComponents / math.sqrt(100)
]

# Results
print("SIMULATION RESULTS (100 Replications)")
print()
print()
print("1. PROPORTION OF SYSTEM FAILURE TIME (Time when S=0)")
print()
print(f"   Point Estimate: {mean_proportionDown:.4f}")
print(f"   Standard Deviation: {std_proportionDown:.4f}")
print(f"   95% Confidence Interval: [{ci_proportionDown[0]:.4f}, {ci_proportionDown[1]:.4f}]")
print()
print("2. AVERAGE NUMBER OF FUNCTIONAL COMPONENTS")
print()
print(f"   Point Estimate: {mean_avgComponents:.4f}")
print(f"   Standard Deviation: {std_avgComponents:.4f}")
print(f"   95% Confidence Interval: [{ci_avgComponents[0]:.4f}, {ci_avgComponents[1]:.4f}]")
print()
print()
print("INTERPRETATION:")
print()
print(f"• The system is down (S=0) approximately {mean_proportionDown*100:.2f}% of the time")
print(f"• On average, there are {mean_avgComponents:.2f} functional components available")
print(f"• With 95% confidence, the true proportion of downtime is between")
print(f"  {ci_proportionDown[0]*100:.2f}% and {ci_proportionDown[1]*100:.2f}%")
print()