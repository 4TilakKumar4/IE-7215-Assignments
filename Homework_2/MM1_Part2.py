"""
Problem 3 Part 2: M/M/1 Queue Transient Analysis

Model Configuration:
- Single server queue (M/M/1)
- Arrival rate (λ): 1 customer per minute (Exponential interarrival)
- Service rate (μ): 1.5 customers per minute (Exponential service)
- Utilization (ρ): λ/μ = 1/1.5 = 0.667

Simulation Configuration:
- Start from empty system (no warmup)
- Stop after 500 customers complete service
- Replications: 100
"""


import SimFunctions
import SimRNG 
import SimClasses
import pandas
import numpy as np
import matplotlib.pyplot as plt

ZSimRNG = SimRNG.InitializeRNSeed()

Queue = SimClasses.FIFOQueue()
Wait = SimClasses.DTStat()
Server = SimClasses.Resource()
Calendar = SimClasses.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

TheDTStats.append(Wait)
TheQueues.append(Queue)
TheResources.append(Server)

Server.SetUnits(1)
MeanTBA = 1.0
MeanST = 0.667
Phases = 1
NumReps = 100
MaxCustomers = 500

CustomerCount = 0
WaitTimes = []
WaitMatrix = np.zeros((NumReps, MaxCustomers))


def Arrival():
    SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))
    Customer = SimClasses.Entity()
    Queue.Add(Customer)
    
    if Server.Busy == 0:
        Server.Seize(1)
        SimFunctions.Schedule(Calendar, "EndOfService", SimRNG.Erlang(Phases, MeanST, 2))


def EndOfService():
    global CustomerCount, WaitTimes
    
    DepartingCustomer = Queue.Remove()
    WaitTime = SimClasses.Clock - DepartingCustomer.CreateTime
    WaitTimes.append(WaitTime)
    CustomerCount += 1
    
    if Queue.NumQueue() > 0:
        SimFunctions.Schedule(Calendar, "EndOfService", SimRNG.Erlang(Phases, MeanST, 2))
    else:
        Server.Free(1)

print()
print("MM1 Part 2: Transient Analysis")
print("-"*50)

for rep in range(NumReps):
    
    CustomerCount = 0
    WaitTimes = []
    
    SimFunctions.SimFunctionsInit(Calendar, TheQueues, TheCTStats, TheDTStats, TheResources)
    SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))
    
    while CustomerCount < MaxCustomers:
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
        
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfService":
            EndOfService()
    
    for i in range(MaxCustomers):
        WaitMatrix[rep, i] = WaitTimes[i]
    
    if (rep + 1) % 20 == 0:
        print("Completed replication", rep + 1)

E_Wi = np.mean(WaitMatrix, axis=0)
SD_Wi = np.std(WaitMatrix, axis=0, ddof=1)

# Plot 1: E[Wi] and SD[Wi]
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(range(1, MaxCustomers + 1), E_Wi, 'b-', linewidth=0.8)
ax1.set_xlabel('Customer Number (i)')
ax1.set_ylabel('E[Wi] (minutes)')
ax1.set_title('Expected Time in System')
ax1.grid(True, alpha=0.3)

ax2.plot(range(1, MaxCustomers + 1), SD_Wi, 'r-', linewidth=0.8)
ax2.set_xlabel('Customer Number (i)')
ax2.set_ylabel('SD[Wi] (minutes)')
ax2.set_title('Standard Deviation of Time in System')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('MM1_Part2_Transient.png', dpi=150)
plt.close()

# Plot 2: Confidence Band Plot
fig, ax = plt.subplots(figsize=(14, 6))

customers = range(1, MaxCustomers + 1)
SE_Wi = SD_Wi / np.sqrt(NumReps)

ax.fill_between(customers, E_Wi - 1.96*SE_Wi, E_Wi + 1.96*SE_Wi, color='lightblue', alpha=0.5, label='95% CI')
ax.plot(customers, E_Wi, 'b-', linewidth=2, label='E[Wi]')

ax.set_xlabel('Customer Number (i)')
ax.set_ylabel('Wait Time (minutes)')
ax.set_title('Expected Wait Time with 95% Confidence Band')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('MM1_Part2_CI.png', dpi=150)
plt.close()

# Plot 3: Box Plot at Intervals with Mean Line
fig, ax = plt.subplots(figsize=(14, 6))

positions = list(range(25, MaxCustomers + 1, 25))
box_data = [WaitMatrix[:, i-1] for i in positions]

bp = ax.boxplot(box_data, positions=positions, widths=15, patch_artist=True)

for patch in bp['boxes']:
    patch.set_facecolor('lightblue')
    patch.set_alpha(0.7)

ax.plot(customers, E_Wi, 'r-', linewidth=2, label='E[Wi]')

ax.set_xlabel('Customer Number (i)')
ax.set_ylabel('Wait Time (minutes)')
ax.set_title('Customer Wait Times: Box Plot with Mean')
ax.set_xlim(0, MaxCustomers + 10)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('MM1_Part2_BoxPlot.png', dpi=150)
plt.close()

output = pandas.DataFrame({'Customer': range(1, MaxCustomers + 1), 'E_Wi': E_Wi, 'SD_Wi': SD_Wi})
output.to_csv('MM1_Part2_Transient.csv', index=False)

print("\nResults saved to MM1_Part2_Transient.csv")
print("Plots saved:")
print("  - MM1_Part2_Transient.png (E[Wi] and SD[Wi])")
print("  - MM1_Part2_CI.png (Confidence Band)")
print("  - MM1_Part2_BoxPlot.png (Box Plot)")