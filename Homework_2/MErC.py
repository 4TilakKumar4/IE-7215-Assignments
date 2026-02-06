"""
Problem 4 - Scenario 2: Cross-Trained Agents (Proposed System)
SMP Call Center Simulation

System Configuration:
- N cross-trained agents handling ALL calls (single queue)
- Service time increased by 5% (5.25 min mean)
- Financial calls: 59%, Erlang-2 service
- Contact Management calls: 41%, Erlang-3 service
- Arrival rate: 60 calls/hour = 1 call/min (Poisson process)
- Operating hours: 8am-4pm (480 minutes)
"""

import SimFunctions
import SimRNG 
import SimClasses
import pandas
import numpy as np

ZSimRNG = SimRNG.InitializeRNSeed()

Queue = SimClasses.FIFOQueue()
Wait = SimClasses.DTStat()
Servers = SimClasses.Resource()
Calendar = SimClasses.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

TheDTStats.append(Wait)
TheQueues.append(Queue)
TheResources.append(Servers)

NumberAgents = 8 
Servers.SetUnits(NumberAgents)
PhasesFinancial = 2
PhasesContact = 3
MeanTBA = 1.0
MeanST = 5.0 * 1.05
FinancialProb = 0.59
RunLength = 480.0
WarmUp = 0.0

AllWaitMean = []
AllQueueMean = []
AllQueueNum = []
AllServerMean = []

print("Starting Scenario 2 Simulations")
print()
print("Rep", "Average Wait", "Average Number in Queue", "Number Remaining in Queue", "Server Utilization")


class Call(SimClasses.Entity):
    def __init__(self, call_type):
        self.CreateTime = SimClasses.Clock
        self.CallType = call_type


def Arrival():
    SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))
    
    if SimRNG.lcgrand(2) < FinancialProb:
        Customer = Call("Financial")
    else:
        Customer = Call("Contact")
    
    if Servers.Busy < NumberAgents:
        Servers.Seize(1)
        Wait.Record(0)
        if Customer.CallType == "Financial":
            SimFunctions.Schedule(Calendar, "EndOfService", SimRNG.Erlang(PhasesFinancial, MeanST, 3))
        else:
            SimFunctions.Schedule(Calendar, "EndOfService", SimRNG.Erlang(PhasesContact, MeanST, 4))
    else:
        Queue.Add(Customer)


def EndOfService():
    if Queue.NumQueue() > 0:
        NextCustomer = Queue.Remove()
        Wait.Record(SimClasses.Clock - NextCustomer.CreateTime)
        if NextCustomer.CallType == "Financial":
            SimFunctions.Schedule(Calendar, "EndOfService", SimRNG.Erlang(PhasesFinancial, MeanST, 3))
        else:
            SimFunctions.Schedule(Calendar, "EndOfService", SimRNG.Erlang(PhasesContact, MeanST, 4))
    else:
        Servers.Free(1)


for reps in range(0, 100, 1):
    
    SimFunctions.SimFunctionsInit(Calendar, TheQueues, TheCTStats, TheDTStats, TheResources)
    SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))
    SimFunctions.Schedule(Calendar, "EndSimulation", RunLength)
    
    NextEvent = Calendar.Remove()
    SimClasses.Clock = NextEvent.EventTime
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "EndOfService":
        EndOfService()
    
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndOfService":
            EndOfService()
    
    AllWaitMean.append(Wait.Mean())
    AllQueueMean.append(Queue.Mean())
    AllQueueNum.append(Queue.NumQueue())
    AllServerMean.append(Servers.Mean() / NumberAgents)
    
    print(reps+1, Wait.Mean(), Queue.Mean(), Queue.NumQueue(), Servers.Mean()/NumberAgents)

output = {"SlNo": list(range(1, 101)), "AllWaitMean": AllWaitMean, "AllQueueMean": AllQueueMean, "AllQueueNum": AllQueueNum, "AllServerMean": AllServerMean}
output = pandas.DataFrame(output)
output.to_csv("Scenario2_output.csv", sep=",")

print("\nScenario 2 Results:")
print("Mean Wait:", AllWaitMean.mean()[0])
print("Std Wait:", AllWaitMean.std()[0])
ci_hw = 1.96 * AllWaitMean.std()[0] / np.sqrt(100)
print("95% CI: [", AllWaitMean.mean()[0] - ci_hw, ",", AllWaitMean.mean()[0] + ci_hw, "]")