"""
Problem 3 Part 1: M/M/1 Queue Steady-State Analysis

Model Configuration:
- Single server queue (M/M/1)
- Arrival rate (λ): 1 customer per minute (Exponential interarrival)
- Service rate (μ): 1.5 customers per minute (Exponential service)
- Utilization (ρ): λ/μ = 1/1.5 = 0.667

Simulation Configuration:
- Run length: 55,000 minutes
- Warmup period: 5,000 minutes (observations removed)
- Replications: 5, 30, 100 (comparing CI width)
"""


import SimFunctions
import SimRNG 
import SimClasses
import pandas
import numpy as np

ZSimRNG = SimRNG.InitializeRNSeed()

Queue = SimClasses.FIFOQueue()
Wait = SimClasses.DTStat()
Server = SimClasses.Resource()
Calendar = SimClasses.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []
SummaryResults = []

TheDTStats.append(Wait)
TheQueues.append(Queue)
TheResources.append(Server)


Server.SetUnits (1) 
MeanTBA = 1.0
MeanST = 0.667
Phases = 1
RunLength = 55000.0
WarmUp = 5000.0
NumRepsList = [5, 30, 100]


def Arrival():
    SimFunctions.Schedule(Calendar,"Arrival",SimRNG.Expon(MeanTBA, 1))
    Customer = SimClasses.Entity()
    Queue.Add(Customer)
    
    if Server.Busy == 0:
        Server.Seize(1)
        SimFunctions.Schedule(Calendar,"EndOfService",SimRNG.Erlang(Phases,MeanST,2))

def EndOfService():
    DepartingCustomer = Queue.Remove()
    Wait.Record(SimClasses.Clock - DepartingCustomer.CreateTime)
    if Queue.NumQueue() > 0:
        SimFunctions.Schedule(Calendar,"EndOfService",SimRNG.Erlang(Phases,MeanST,2))
    else:
        Server.Free(1)


print()
print("MM1 Part 1: Steady State Analysis")
print("-"*50)

for NumReps in NumRepsList:

    AllWaitMean = []
    AllQueueMean = []
    AllQueueNum = []
    AllServerMean = []
    
    print("\n")
    print("Running with", NumReps, "replications")
    print("-"*40)
    print("Rep", "Average Wait", "Average Number in Queue", "Number Remaining in Queue", "Server Utilization")
    
    for reps in range(0, NumReps, 1):

        SimFunctions.SimFunctionsInit(Calendar,TheQueues,TheCTStats,TheDTStats,TheResources)
        SimFunctions.Schedule(Calendar,"Arrival",SimRNG.Expon(MeanTBA, 1))
        SimFunctions.Schedule(Calendar,"EndSimulation",RunLength)
        SimFunctions.Schedule(Calendar,"ClearIt",WarmUp)
        
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfService":
            EndOfService() 
        elif NextEvent.EventType == "ClearIt":
            SimFunctions.ClearStats(TheCTStats,TheDTStats)
        
        while NextEvent.EventType != "EndSimulation":
            NextEvent = Calendar.Remove()
            SimClasses.Clock = NextEvent.EventTime
            if NextEvent.EventType == "Arrival":
                Arrival()
            elif NextEvent.EventType == "EndOfService":
                EndOfService()
            elif NextEvent.EventType == "ClearIt":
                SimFunctions.ClearStats(TheCTStats,TheDTStats)

        
        AllWaitMean.append(Wait.Mean())
        AllQueueMean.append(Queue.Mean())
        AllQueueNum.append(Queue.NumQueue())
        AllServerMean.append(Server.Mean())
        print (reps+1, Wait.Mean(), Queue.Mean(), Queue.NumQueue(), Server.Mean())

    AllWaitMean_df = pandas.DataFrame(AllWaitMean)
    mean_wait = AllWaitMean_df.mean()[0]
    std_wait = AllWaitMean_df.std()[0]
    ci_hw = 1.96 * std_wait / np.sqrt(NumReps)
    
    print("\nResults for", NumReps, "replications:")
    print("Mean Wait:", mean_wait)
    print("Std Wait:", std_wait)
    print("95% CI: [", mean_wait - ci_hw, ",", mean_wait + ci_hw, "]")
    
    # Add to summary
    SummaryResults.append({
        "NumReps": NumReps,
        "MeanWait": mean_wait,
        "StdWait": std_wait,
        "CI_Lower": mean_wait - ci_hw,
        "CI_Upper": mean_wait + ci_hw
    })
    
    # Save individual CSV
    output = {"AllWaitMean": AllWaitMean, "AllQueueMean": AllQueueMean, "AllQueueNum": AllQueueNum, "AllServerMean": AllServerMean}
    output = pandas.DataFrame(output)
    output.to_csv("MM1_Part1_output_" + str(NumReps) + "reps.csv", sep=",")

# Save summary CSV
summary = pandas.DataFrame(SummaryResults)
summary.to_csv("MM1_Part1_summary.csv", sep=",")
print("\nSummary saved to MM1_Part1_summary.csv")