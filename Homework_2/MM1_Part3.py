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
Phases = 1
NumReps = 100
MaxCustomers = 500

CustomerCount = 0
WaitTimes = []

RhoList = [0.3, 0.5, 0.9]
AllResults = {}


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
print("MM1 Part 3: Different Utilization Levels")
print("-"*60)

for rho in RhoList:
    
    MeanST = rho
    WaitMatrix = np.zeros((NumReps, MaxCustomers))
    
    print("\nRunning simulations for rho =", rho)
    print("-"*40)
    
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
    SE_Wi = SD_Wi / np.sqrt(NumReps)
    
    AllResults[rho] = {'E_Wi': E_Wi, 'SD_Wi': SD_Wi, 'SE_Wi': SE_Wi, 'WaitMatrix': WaitMatrix}
    
    # Plot 1: E[Wi] and SD[Wi]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(range(1, MaxCustomers + 1), E_Wi, 'b-', linewidth=0.8)
    ax1.set_xlabel('Customer Number (i)')
    ax1.set_ylabel('E[Wi] (minutes)')
    ax1.set_title(f'Expected Time in System (rho = {rho})')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(range(1, MaxCustomers + 1), SD_Wi, 'r-', linewidth=0.8)
    ax2.set_xlabel('Customer Number (i)')
    ax2.set_ylabel('SD[Wi] (minutes)')
    ax2.set_title(f'Standard Deviation of Time in System (rho = {rho})')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'MM1_Part3_rho{rho}_Transient.png', dpi=150)
    plt.close()
    
    # Plot 2: Confidence Band
    fig, ax = plt.subplots(figsize=(14, 6))
    
    customers = range(1, MaxCustomers + 1)
    ax.fill_between(customers, E_Wi - 1.96*SE_Wi, E_Wi + 1.96*SE_Wi, color='lightblue', alpha=0.5, label='95% CI')
    ax.plot(customers, E_Wi, 'b-', linewidth=2, label='E[Wi]')
    
    ax.set_xlabel('Customer Number (i)')
    ax.set_ylabel('Wait Time (minutes)')
    ax.set_title(f'Expected Wait Time with 95% Confidence Band (rho = {rho})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'MM1_Part3_rho{rho}_CI.png', dpi=150)
    plt.close()
    
    # Save CSV
    output = pandas.DataFrame({'Customer': range(1, MaxCustomers + 1), 'E_Wi': E_Wi, 'SD_Wi': SD_Wi})
    output.to_csv(f'MM1_Part3_rho{rho}.csv', index=False)

# Comparison Plot: All rho values on one plot
fig, ax = plt.subplots(figsize=(14, 6))

colors = {'0.3': 'green', '0.5': 'blue', '0.9': 'red'}
customers = range(1, MaxCustomers + 1)

for rho in RhoList:
    E_Wi = AllResults[rho]['E_Wi']
    ax.plot(customers, E_Wi, linewidth=2, label=f'rho = {rho}', color=colors[str(rho)])

ax.set_xlabel('Customer Number (i)')
ax.set_ylabel('E[Wi] (minutes)')
ax.set_title('Comparison of Expected Wait Times for Different Utilization Levels')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('MM1_Part3_Comparison.png', dpi=150)
plt.close()

# Comparison Plot with CI bands
fig, ax = plt.subplots(figsize=(14, 6))

for rho in RhoList:
    E_Wi = AllResults[rho]['E_Wi']
    SE_Wi = AllResults[rho]['SE_Wi']
    color = colors[str(rho)]
    ax.fill_between(customers, E_Wi - 1.96*SE_Wi, E_Wi + 1.96*SE_Wi, alpha=0.2, color=color)
    ax.plot(customers, E_Wi, linewidth=2, label=f'rho = {rho}', color=color)

ax.set_xlabel('Customer Number (i)')
ax.set_ylabel('E[Wi] (minutes)')
ax.set_title('Comparison of Expected Wait Times with 95% CI for Different Utilization Levels')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('MM1_Part3_Comparison_CI.png', dpi=150)
plt.close()

print()
print("Results Summary")
print("-"*60)
for rho in RhoList:
    E_Wi = AllResults[rho]['E_Wi']
    print(f"\nrho = {rho}:")
    print(f"  Mean wait (first 50 customers): {np.mean(E_Wi[:50]):.4f}")
    print(f"  Mean wait (last 50 customers):  {np.mean(E_Wi[-50:]):.4f}")
    print(f"  Steady-state estimate:          {np.mean(E_Wi[-100:]):.4f}")

print("\n" + "-"*50)
print("Files saved:")
print("  - MM1_Part3_rho{0.3,0.5,0.9}_Transient.png")
print("  - MM1_Part3_rho{0.3,0.5,0.9}_CI.png")
print("  - MM1_Part3_rho{0.3,0.5,0.9}.csv")
print("  - MM1_Part3_Comparison.png")
print("  - MM1_Part3_Comparison_CI.png")