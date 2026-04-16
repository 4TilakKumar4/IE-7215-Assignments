import sim_engine.SimFunctions as SimFunctions
import sim_engine.SimRNG as SimRNG 
import sim_engine.SimClasses as SimClasses
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
WarmupCustomers = 500
RunLength = 100

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


def FitAR1(series):
    n = len(series)
    mu = np.mean(series)
    c0 = np.sum((series - mu) ** 2) / n
    c1 = np.sum((series[1:] - mu) * (series[:-1] - mu)) / n
    phi = c1 / c0
    sigma2 = c0 * (1 - phi ** 2)
    return mu, phi, sigma2


print()
print("MM1 Part 2: AR(1) Surrogate Model")
print("-"*60)

for rho in RhoList:

    MeanST = rho
    MuMatrix = np.zeros(NumReps)
    PhiMatrix = np.zeros(NumReps)
    Sigma2Matrix = np.zeros(NumReps)
    WaitMatrix = np.zeros((NumReps, RunLength))

    print("\nRunning simulations for rho =", rho)
    print("-"*40)

    for rep in range(NumReps):

        CustomerCount = 0
        WaitTimes = []

        SimFunctions.SimFunctionsInit(Calendar, TheQueues, TheCTStats, TheDTStats, TheResources)
        SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))

        while CustomerCount < WarmupCustomers + RunLength:
            NextEvent = Calendar.Remove()
            SimClasses.Clock = NextEvent.EventTime

            if NextEvent.EventType == "Arrival":
                Arrival()
            elif NextEvent.EventType == "EndOfService":
                EndOfService()

        SteadyStateWaits = np.array(WaitTimes[WarmupCustomers:WarmupCustomers + RunLength])
        WaitMatrix[rep] = SteadyStateWaits

        MuMatrix[rep], PhiMatrix[rep], Sigma2Matrix[rep] = FitAR1(SteadyStateWaits)

        if (rep + 1) % 20 == 0:
            print("Completed replication", rep + 1)

    MeanMu = MuMatrix.mean()
    MeanPhi = PhiMatrix.mean()

    AllErrors = []
    for rep in range(NumReps):
        YPred = MeanMu + MeanPhi * (WaitMatrix[rep, :-1] - MeanMu)
        Errors = WaitMatrix[rep, 1:] - YPred
        AllErrors.extend(Errors.tolist())

    AllErrors = np.array(AllErrors)
    RMSE = np.sqrt(np.mean(AllErrors ** 2))
    MAE = np.mean(np.abs(AllErrors))

    AllResults[rho] = {
        'WaitMatrix': WaitMatrix,
        'Mu': MuMatrix,
        'Phi': PhiMatrix,
        'Sigma2': Sigma2Matrix,
        'RMSE': RMSE,
        'MAE': MAE
    }

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(PhiMatrix, bins=20, color='steelblue', edgecolor='white', alpha=0.8)
    ax.axvline(PhiMatrix.mean(), color='black', linestyle='--', linewidth=1.5, label=f'Mean = {PhiMatrix.mean():.3f}')
    ax.set_xlabel('phi_hat')
    ax.set_ylabel('Frequency')
    ax.set_title(f'AR(1) Coefficient Distribution (rho = {rho})')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'MM1_Part2_rho{rho}_Phi.png', dpi=150)
    plt.close()

    output = pandas.DataFrame({
        'Rep': range(1, NumReps + 1),
        'Mu': MuMatrix,
        'Phi': PhiMatrix,
        'Sigma2': Sigma2Matrix
    })
    output.to_csv(f'MM1_Part2_rho{rho}.csv', index=False)


# Comparison plot: phi estimates across rho levels
fig, ax = plt.subplots(figsize=(10, 6))
data = [AllResults[rho]['Phi'] for rho in RhoList]
labels = [f'rho = {rho}' for rho in RhoList]
bp = ax.boxplot(data, labels=labels, patch_artist=True)
colors_list = ['#2196F3', '#4CAF50', '#F44336']
for patch, color in zip(bp['boxes'], colors_list):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_ylabel('phi_hat')
ax.set_title('AR(1) Autocorrelation Coefficient by Utilization Level')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('MM1_Part2_PhiComparison.png', dpi=150)
plt.close()


print()
print("Results Summary")
print("-"*60)
for rho in RhoList:
    MuRate = 1.0 / rho
    WTheory = (rho / (MuRate * (1.0 - rho))) + rho
    print(f"\nrho = {rho}:")
    print(f"  Theoretical E[W]:  {WTheory:.4f}")
    print(f"  Mean mu_hat:       {AllResults[rho]['Mu'].mean():.4f} +/- {AllResults[rho]['Mu'].std():.4f}")
    print(f"  Mean phi_hat:      {AllResults[rho]['Phi'].mean():.4f} +/- {AllResults[rho]['Phi'].std():.4f}")
    print(f"  Mean sigma2_hat:   {AllResults[rho]['Sigma2'].mean():.4f} +/- {AllResults[rho]['Sigma2'].std():.4f}")
    print(f"  Prediction RMSE:   {AllResults[rho]['RMSE']:.4f}")
    print(f"  Prediction MAE:    {AllResults[rho]['MAE']:.4f}")

print("\n" + "-"*50)
print("Files saved:")
print("  - MM1_Part2_rho{0.3,0.5,0.9}_Phi.png")
print("  - MM1_Part2_rho{0.3,0.5,0.9}.csv")
print("  - MM1_Part2_PhiComparison.png")