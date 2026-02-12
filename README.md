# IE 7215 Assignments

# Homework 1 - Outupts
### Q 3.a.
<img width="466" height="362" alt="Pasted image 20260123101658" src="https://github.com/user-attachments/assets/2d83272b-04ea-4309-aded-20e9d101c86b" />

### Q 3.b.a.
<img width="577" height="459" alt="Pasted image 20260123102020" src="https://github.com/user-attachments/assets/f8da3821-23ed-42ba-b518-9f5ae1f4e009" />

### Q 3.b.b
 <img width="737" height="466" alt="Pasted image 20260123102250" src="https://github.com/user-attachments/assets/c24d59d8-9f11-4e77-86d4-4ab4b567697c" />

---

# Lab 1 - Plot
### Number of pateients in the system - L(t)
  <img width="8047" height="4618" alt="sample_path_high_res" src="https://github.com/user-attachments/assets/2c412320-a6ab-4041-9e5c-f9464d68e0c2" />

---

# Homework 2 - Results

## Problem 3 - M/M/1 Queue
### Part1 - Steady State Analysis 
#### Configuration  
Model Configuration:
- Single server queue (M/M/1)
- Arrival rate (λ): 1 customer per minute (Exponential interarrival)
- Service rate (μ): 1.5 customers per minute (Exponential service)
- Utilization (ρ): λ/μ = 1/1.5 = 0.667

Simulation Configuration:
- Run length: 55,000 minutes
- Warmup period: 5,000 minutes (observations removed)
- Replications: 5, 30, 100 (comparing CI width)

#### Results
| NumReps | MeanWait | StdWait | CI_Lower | CI_Upper |
|:-------:|:--------:|:-------:|:--------:|:--------:|
|    5    |  2.0207  | 0.0388  |  1.9867  |  2.0547  |
|   30    |  2.0043  | 0.0432  |  1.9888  |  2.0197  |
|   100   |  1.9979  | 0.0450  |  1.9891  |  2.0067  |
The mean wait time convergence at 2 minutes across all replication counts which aligns with the theoretical W value.  The main observation is that the CI width decreases as replications increase, showing that estimation accuracy improves.

### Part 2 - Transient Anlaysis
#### Configuration 
Model Configuration:
- Single server queue (M/M/1)
- Arrival rate (λ): 1 customer per minute (Exponential interarrival)
- Service rate (μ): 1.5 customers per minute (Exponential service)
- Utilization (ρ): λ/μ = 1/1.5 = 0.667

Simulation Configuration:
- Start from empty system (no warmup)
- Stop after 500 customers complete service
- Replications: 100
#### Results
![[MM1_Part2_Transient.png]]
*Figure 1: Expected and Standard Deviation of Wait Times in System* 
![[MM1_Part2_CI.png]]
*Figure 2: Expected Wait Time with 95% confidence band*

The transient plots clearly show the effect of warmup on the wait times. Early customer experience shorter wait times because the system starts empty. As the queue builds up, wait times increase until steady state is reached around 100-150th customer in this case. The confidence band widens initially and then stabilizes. 

### Part 3 - Effect of Utilization Ratio
#### Configuration 
Model Configuration:
- Single server queue (M/M/1)
- Arrival rate (λ): 1 customer per minute (fixed)
- Service rate (μ): Varies to achieve target utilization
  - ρ = 0.3: μ = 3.33/min, MeanST = 0.3 min
  - ρ = 0.5: μ = 2.0/min,  MeanST = 0.5 min
  - ρ = 0.9: μ = 1.11/min, MeanST = 0.9 min

Simulation Configuration:
- Start from empty system (no warmup)
- Stop after 500 customers complete service
- Replications: 100 per utilization level
#### Results
|  ρ  | First 50 Customers | Last 50 Customers | Steady-State Estimate |
|:---:|:------------------:|:-----------------:|:---------------------:|
| 0.3 |      0.42 min      |     0.43 min      |       0.44 min        |
| 0.5 |      1.02 min      |     1.03 min      |       1.03 min        |
| 0.9 |      4.39 min      |     9.10 min      |       9.09 min        |
![[MM1_Part3_Comparison_CI.png]]
*Figure 3: Comparison of Expected Wait Times for Different Utilization Levels*

##### Conclusions 
1. Wait times increase nonlinearly with utilization - Wait times for ρ= 0.9 is ~20x longer than ρ= 0.3. 
2. Variability increases with utilization - The CI bands for ρ= 0.9 are much wider than for ρ= 0.3, indicating greater replication to replication variability at high utilization.
3. Warmup length depends on utilization - For ρ= 0.3 and ρ= 0.5, first 50 wait times ~ last 50 wait times, suggesting a quick steady state. Whereas, for ρ= 0.9 first 50 << last 50, meaning the system takes longer to reach steady state. High utilizations systems require longer warmup periods. 

## Problem 4 - SMP Call Center Simulation
### Scenario 1 - Specialized Agents (Current System)
#### Configuration 
System Configuration:
- 4 agents for Financial calls (59% of calls, Erlang-2 service, mean 5 min)
- 3 agents for Contact Management calls (41% of calls, Erlang-3 service, mean 5 min)
- Two separate queues
- Arrival rate: 60 calls/hour = 1 call/min (Poisson process)
- Operating hours: 8am-4pm (480 minutes)
#### Results 
| Metric               | Financial Queue | Contact Queue |     Combined     |
| -------------------- |:---------------:|:-------------:|:----------------:|
| Number of Agents     |        4        |       3       |        7         |
| Service Distribution |    Erlang-2     |   Erlang-3    |        -         |
| Mean Service Time    |      5 min      |     5 min     |        -         |
| Utilization          |      73.5%      |     68.3%     |        -         |
| **Mean Wait Time**   |        -        |       -       |   **1.68 min**   |
| **95% CI**           |        -        |       -       | **[1.57, 1.80]** |

### Scenario 2 - Cross Trained Agents (Proposed System)
#### Configuration 
System Configuration:
- N cross-trained agents handling ALL calls (single queue)
- Service time increased by 5% (5.25 min mean)
- Financial calls: 59%, Erlang-2 service
- Contact Management calls: 41%, Erlang-3 service
- Arrival rate: 60 calls/hour = 1 call/min (Poisson process)
- Operating hours: 8am-4pm (480 minutes)

#### Results
| Number of Agents | Mean Wait (min) |      95% CI      |     Status     |
| :--------------: | :-------------: | :--------------: | :------------: |
|        5         |      19.09      |  [17.07, 21.11]  |  Unacceptable  |
|        6         |      3.03       |   [2.71, 3.36]   |  Unacceptable  |
|      **7**       |    **0.88**     | **[0.77, 0.98]** | **Acceptable** |
##### Conclusions 
1. **7 cross-trained agent**s are needed to match or exceed the current service level. With fewer agents (5 or 6), wait times are significantly higher than the current system. 
2. With 7 cross-trained agents, the mean wait time drops from 1.68 minutes to 0.88 minutes, which is a **48% reduction** in customer wait time.
3. Though the there is no reduction in labour, the cross trained system outperforms the current specialized system with the same total headcount. This is due to the pooling effect - in the specialized system, idle agents in one queue cannot help customers waiting in another queue. 
4. The 5% increase in service time is more than offset by the efficiency gains from pooling resources into one single queue.
##### Resources
Implement cross-training with **7 agents**. Benefits include:
- **Same labor cost** (7 agents in both systems)
- **48% reduction** in mean wait time (1.68 → 0.88 min)
- **Improved flexibility** for handling demand fluctuations
- **Better customer experience** with shorter hold times