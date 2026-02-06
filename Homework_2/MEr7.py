"""
Problem 4 - Scenario 1: Specialized Agents (Current System)
SMP Call Center Simulation

System Configuration:
- 4 agents for Financial calls (59% of calls, Erlang-2 service, mean 5 min)
- 3 agents for Contact Management calls (41% of calls, Erlang-3 service, mean 5 min)
- Two separate queues
- Arrival rate: 60 calls/hour = 1 call/min (Poisson process)
- Operating hours: 8am-4pm (480 minutes)
"""

import SimFunctions
import SimRNG 
import SimClasses
import pandas
import numpy as np

ZSimRNG = SimRNG.InitializeRNSeed()

FinancialQueue = SimClasses.FIFOQueue()
ContactQueue = SimClasses.FIFOQueue()
FinancialWait = SimClasses.DTStat()
ContactWait = SimClasses.DTStat()
FinancialServers = SimClasses.Resource()
ContactServers = SimClasses.Resource()
Calendar = SimClasses.EventCalendar()

TheCTStats = []
TheDTStats = []
TheQueues = []
TheResources = []

TheDTStats.append(FinancialWait)
TheDTStats.append(ContactWait)
TheQueues.append(FinancialQueue)
TheQueues.append(ContactQueue)
TheResources.append(FinancialServers)
TheResources.append(ContactServers)

NumberFinancialAgents = 4
NumberContactAgents = 3
FinancialServers.SetUnits(NumberFinancialAgents)
ContactServers.SetUnits(NumberContactAgents)
PhasesFinancial = 2
PhasesContact = 3
MeanTBA = 1.0
MeanST = 5.0
FinancialProb = 0.59
RunLength = 480.0
WarmUp = 0.0

AllWaitMean = []
AllFinancialQueueMean = []
AllContactQueueMean = []
AllFinancialUtilMean = []
AllContactUtilMean = []

print("Starting Scenario 1 Simulations")
print()
print("Rep", "Avg Wait", "Finance Queue", "Contact Queue", "Finance Util", "Contact Util")


class Call(SimClasses.Entity):
    def __init__(self, call_type):
        self.CreateTime = SimClasses.Clock
        self.CallType = call_type


def Arrival():
    SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))
    
    if SimRNG.lcgrand(2) < FinancialProb:
        Customer = Call("Financial")
        if FinancialServers.Busy < NumberFinancialAgents:
            # Server available - start service immediately (no queue)
            FinancialServers.Seize(1)
            FinancialWait.Record(0)  # No wait time
            SimFunctions.Schedule(Calendar, "EndFinancialService", SimRNG.Erlang(PhasesFinancial, MeanST, 3))
        else:
            # All servers busy - customer must wait
            FinancialQueue.Add(Customer)
    else:
        Customer = Call("Contact")
        if ContactServers.Busy < NumberContactAgents:
            ContactServers.Seize(1)
            ContactWait.Record(0)
            SimFunctions.Schedule(Calendar, "EndContactService", SimRNG.Erlang(PhasesContact, MeanST, 4))
        else:
            ContactQueue.Add(Customer)


def EndFinancialService():
    if FinancialQueue.NumQueue() > 0:
        # Pick up waiting customer from queue
        NextCustomer = FinancialQueue.Remove()
        FinancialWait.Record(SimClasses.Clock - NextCustomer.CreateTime)
        SimFunctions.Schedule(Calendar, "EndFinancialService", SimRNG.Erlang(PhasesFinancial, MeanST, 3))
    else:
        # No one waiting - free the server
        FinancialServers.Free(1)


def EndContactService():
    if ContactQueue.NumQueue() > 0:
        NextCustomer = ContactQueue.Remove()
        ContactWait.Record(SimClasses.Clock - NextCustomer.CreateTime)
        SimFunctions.Schedule(Calendar, "EndContactService", SimRNG.Erlang(PhasesContact, MeanST, 4))
    else:
        ContactServers.Free(1)

for reps in range(0, 100, 1):
    
    SimFunctions.SimFunctionsInit(Calendar, TheQueues, TheCTStats, TheDTStats, TheResources)
    SimFunctions.Schedule(Calendar, "Arrival", SimRNG.Expon(MeanTBA, 1))
    SimFunctions.Schedule(Calendar, "EndSimulation", RunLength)
    
    NextEvent = Calendar.Remove()
    SimClasses.Clock = NextEvent.EventTime
    if NextEvent.EventType == "Arrival":
        Arrival()
    elif NextEvent.EventType == "EndFinancialService":
        EndFinancialService()
    elif NextEvent.EventType == "EndContactService":
        EndContactService()
    
    while NextEvent.EventType != "EndSimulation":
        NextEvent = Calendar.Remove()
        SimClasses.Clock = NextEvent.EventTime
        if NextEvent.EventType == "Arrival":
            Arrival()
        elif NextEvent.EventType == "EndFinancialService":
            EndFinancialService()
        elif NextEvent.EventType == "EndContactService":
            EndContactService()
    
    TotalN = FinancialWait.N() + ContactWait.N()
    AvgWait = (FinancialWait.Sum + ContactWait.Sum) / TotalN if TotalN > 0 else 0
    
    AllWaitMean.append(AvgWait)
    AllFinancialQueueMean.append(FinancialQueue.Mean())
    AllContactQueueMean.append(ContactQueue.Mean())
    AllFinancialUtilMean.append(FinancialServers.Mean() / NumberFinancialAgents)
    AllContactUtilMean.append(ContactServers.Mean() / NumberContactAgents)
    
    print(reps+1, 
          round(AvgWait, 4), 
          round(FinancialQueue.Mean(), 4), 
          round(ContactQueue.Mean(), 4), 
          round(FinancialServers.Mean()/NumberFinancialAgents, 4), 
          round(ContactServers.Mean()/NumberContactAgents, 4))

output = {"SlNo": list(range(1, 101)), "AllWaitMean": AllWaitMean, "AllFinancialQueueMean": AllFinancialQueueMean, "AllContactQueueMean": AllContactQueueMean, "AllFinancialUtilMean": AllFinancialUtilMean, "AllContactUtilMean": AllContactUtilMean}
output = pandas.DataFrame(output)
output.to_csv("MEr7_output.csv", sep=",")

AllWaitMean = pandas.DataFrame(AllWaitMean)
print("\nScenario 1 Results:")
print("Mean Wait:", AllWaitMean.mean()[0])
print("Std Wait:", AllWaitMean.std()[0])