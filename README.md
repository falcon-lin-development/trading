# 20240309
H: 
The Good performance coins would continue to have good performance in the short run

Definition: 
-> 7 days continue good performance
-> in the next day

1) data engineering
- Only top 60 trading volume in the past day coins is considered. 

-> download basic data

2) preprocessing
-> remove unsufficient data coins [ i.e. ] may be newly issued coin


3) ranking (  )
outperform in 7 days continuously
-> *for every 15 mins, that's pct_change rank on closing price*
-> *plot the rank of pct_change in every 15mins for 7 days. [ step 1s ] this is quite useless since the data is messy*

-> plot acc_percentage_change for 7 days in rolling windows manner
-> rank rolling window per 7 days with [
    highest acc_percentage_change, 
    lowest var
    ]


4) strategey hypothesis
-> rank best 10 - rank worst 10 will have +ve return in the next 15minutes


5) backtesting

