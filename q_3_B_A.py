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
    
    s = s - 1
    
    # Check if repair is ongoing
    if nextRepair == infinity:
        # No repair ongoing, start immediately
        nextRepair = clock + 3.5
    else:
        # Repair ongoing, add to queue count
        queueCount += 1
    
    # Generate next failure if components still available
    if s > 0:
        nextFailure = clock + math.ceil(6*random.random())
    else:
        nextFailure = infinity  # No active component, can't fail
    
    # Update statistics
    area = area + sLast * (clock - tLast)
    
    # Track downtime (when s = 0)
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
    
    s = s + 1
    
    # If system was down (s was 0), schedule new failure
    if s == 1 and nextFailure == infinity:
        nextFailure = clock + math.ceil(6*random.random())
    
    # Check if more components waiting in queue
    if queueCount > 0:
        queueCount = queueCount - 1
        nextRepair = clock + 3.5  # Calculate new repair time
    else:
        nextRepair = infinity  # No more repairs
    
    # Update statistics
    area = area + sLast * (clock - tLast)
    
    # Track downtime (when s = 0)
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
maxTime = 1000  # Simulation run length
seed = random.randint(1, 7)
random.seed(seed)

print("=" * 70)
print("MODIFIED TTF SYSTEM SIMULATION - 1000 TIME UNITS")
print("=" * 70)
print(f"Configuration:")
print(f"  - Components: 3 (1 active + 2 spares)")
print(f"  - Repair Time: 3.5 days")
print(f"  - Component Lifetime: Discrete Uniform[1, 6] days")
print(f"  - Simulation Length: {maxTime} time units")
print(f"  - Number of Replications: 100")
print(f"  - Random Seed: {seed}")
print("=" * 70)
print()

# Lists to store results from each replication
proportionDown = []  # Proportion of time system is down (S=0)
avgComponents = []   # Average number of functional components

# Run 100 replications
for reps in range(0, 100, 1):
    nextFailure = math.ceil(6*random.random())
    nextRepair = infinity
    queueCount = 0
    
    s = 3  # 3 components (1 active + 2 spares)
    sLast = 3
    clock = 0.0
    tLast = 0.0
    area = 0.0
    downTime = 0.0  # Track time when S=0
    
    while clock < maxTime:
        # Check if next event is beyond maxTime
        nextEventTime = min(nextFailure, nextRepair)
        
        if nextEventTime >= maxTime:
            # Update statistics to maxTime and stop
            area = area + sLast * (maxTime - tLast)
            
            # Track downtime if system is down
            if sLast == 0:
                downTime = downTime + (maxTime - tLast)
            
            clock = maxTime
            break
        
        # Process next event
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
std_proportionDown = np.std(proportionDown, ddof=1)  # Sample std deviation
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

# Display results
print("SIMULATION RESULTS (100 Replications)")
print("=" * 70)
print()
print("1. PROPORTION OF SYSTEM FAILURE TIME (Time when S=0)")
print("-" * 70)
print(f"   Point Estimate: {mean_proportionDown:.6f}")
print(f"   Standard Deviation: {std_proportionDown:.6f}")
print(f"   95% Confidence Interval: [{ci_proportionDown[0]:.6f}, {ci_proportionDown[1]:.6f}]")
print()
print("2. AVERAGE NUMBER OF FUNCTIONAL COMPONENTS")
print("-" * 70)
print(f"   Point Estimate: {mean_avgComponents:.6f}")
print(f"   Standard Deviation: {std_avgComponents:.6f}")
print(f"   95% Confidence Interval: [{ci_avgComponents[0]:.6f}, {ci_avgComponents[1]:.6f}]")
print()
print("=" * 70)
print("INTERPRETATION:")
print("-" * 70)
print(f"• The system is down (S=0) approximately {mean_proportionDown*100:.2f}% of the time")
print(f"• On average, there are {mean_avgComponents:.2f} functional components available")
print(f"• With 95% confidence, the true proportion of downtime is between")
print(f"  {ci_proportionDown[0]*100:.2f}% and {ci_proportionDown[1]*100:.2f}%")
print("=" * 70)