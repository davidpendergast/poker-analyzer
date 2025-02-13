
Program that parses logs from Pokernow and gives profit/loss breakdowns of various situations.

![Per-hand profit table](/screenshots/profit_chart.PNG?raw=true "Per-Hand Profit Table")

Sample Output:

```
Hands:        2573 (in 16 sessions)
Saw Flop:     769 time(s) (29.89%)
VPIP:         31.4%
Net Gain:     $24.26

-- Situational Breakdowns --
KK:                             64.7bb      $84.12      in 13 hand(s)   [VPIP=99.9%, WIN=84.6%, WaSD=85.7%]
Premiums (JJ+, AQ+):            31.4bb      $122.36     in 39 hand(s)   [VPIP=97.4%, WIN=71.1%, WaSD=78.9%]
AK:                             24.9bb      $66.14      in 27 hand(s)   [VPIP=99.9%, WIN=55.6%, WaSD=64.3%]
QQ:                             15.3bb      $6.12       in 4 hand(s)    [VPIP=99.9%, WIN=75.0%, WaSD=99.9%]
Gets to Showdown:               8.5bb       $205.42     in 229 hand(s)  [VPIP=92.6%, WIN=56.3%, WaSD=55.5%]
Low S Ax (A5-A2s):              4.8bb       $12.47      in 26 hand(s)   [VPIP=84.6%, WIN=31.8%, WaSD=99.9%]
2-way Flops:                    3.8bb       $84.68      in 208 hand(s)  [VPIP=90.9%, WIN=56.4%, WaSD=60.5%]
IP Post-Flop:                   3.5bb       $87.54      in 261 hand(s)  [VPIP=96.9%, WIN=40.0%, WaSD=55.8%]
Mid Position:                   1.8bb       $95.41      in 500 hand(s)  [VPIP=34.2%, WIN=37.9%, WaSD=73.5%]
Low Pairs (66-22):              1.8bb       $8.38       in 49 hand(s)   [VPIP=91.8%, WIN=22.2%, WaSD=72.7%]
OoP Post-Flop:                  1.7bb       $44.08      in 239 hand(s)  [VPIP=90.0%, WIN=37.4%, WaSD=55.1%]
Mid S Ax (AJ-A6s):              1.4bb       $4.70       in 45 hand(s)   [VPIP=91.1%, WIN=31.7%, WaSD=57.1%]
Low S Connectors (32-65s):      1.0bb       $2.00       in 23 hand(s)   [VPIP=65.2%, WIN=26.7%, WaSD=50.0%]
UTG:                            0.8bb       $30.78      in 374 hand(s)  [VPIP=32.9%, WIN=25.2%, WaSD=59.3%]
Low oS Ax (A5-A2o):             0.7bb       $11.40      in 114 hand(s)  [VPIP=25.4%, WIN=37.5%, WaSD=66.7%]
BTN:                            0.6bb       $21.65      in 449 hand(s)  [VPIP=38.8%, WIN=34.3%, WaSD=53.1%]
3-way Flops:                    0.4bb       $11.88      in 250 hand(s)  [VPIP=88.0%, WIN=34.5%, WaSD=51.8%]
All Hands:                      0.1bb       $24.26      in 2573 hand(s) [VPIP=31.4%, WIN=32.8%, WaSD=55.5%]
??:                             0.0bb       $0.00       in 0 hand(s)    [VPIP= 0.0%, WIN= 0.0%, WaSD= 0.0%]
Mid oS Ax (AJ-A6o):             -0.0bb      ($0.70)     in 130 hand(s)  [VPIP=64.6%, WIN=34.9%, WaSD=50.0%]
as BB:                          -0.0bb      $0.94       in 432 hand(s)  [VPIP=25.0%, WIN=38.8%, WaSD=55.1%]
Early Position:                 -0.1bb      ($1.27)     in 531 hand(s)  [VPIP=36.3%, WIN=30.7%, WaSD=54.9%]
Junky oS Kx (KT-K2o):           -0.1bb      ($2.62)     in 214 hand(s)  [VPIP=15.9%, WIN=38.9%, WaSD=66.7%]
Junky oS Qx (QT-Q2o):           -0.2bb      ($3.75)     in 229 hand(s)  [VPIP=14.8%, WIN=33.3%, WaSD=99.9%]
from Blinds:                    -0.2bb      ($15.13)    in 866 hand(s)  [VPIP=29.7%, WIN=38.2%, WaSD=52.2%]
4-way+ Flops:                   -0.3bb      ($8.59)     in 311 hand(s)  [VPIP=87.5%, WIN=18.4%, WaSD=53.8%]
as SB:                          -0.4bb      ($16.07)    in 434 hand(s)  [VPIP=34.3%, WIN=37.6%, WaSD=48.8%]
Late Position:                  -0.4bb      ($36.11)    in 730 hand(s)  [VPIP=35.2%, WIN=31.0%, WaSD=50.7%]
Doesn't get to Showdown:        -2.2bb      ($132.50)   in 595 hand(s)  [VPIP=99.9%, WIN=23.4%, WaSD= 0.0%]
Suited Qx (QT-Q2s):             -3.6bb      ($27.71)    in 76 hand(s)   [VPIP=52.6%, WIN=18.2%, WaSD=37.5%]
Suited Kx (KT-K2s):             -3.7bb      ($27.75)    in 74 hand(s)   [VPIP=75.7%, WIN=20.7%, WaSD=42.9%]
High S Gappers (AQ-J9s):        -5.0bb      ($15.28)    in 24 hand(s)   [VPIP=83.3%, WIN=15.0%, WaSD=33.3%]
Mid Pairs (TT-77):              -7.9bb      ($39.08)    in 56 hand(s)   [VPIP=91.1%, WIN=30.8%, WaSD=50.0%]
High S Connectors (AK-JTs):     -8.0bb      ($24.75)    in 35 hand(s)   [VPIP=88.6%, WIN=29.0%, WaSD=50.0%]
Broadways (KQ KJ QJ):           -10.8bb     ($83.28)    in 77 hand(s)   [VPIP=77.9%, WIN=18.3%, WaSD=25.0%]
AA:                             -11.5bb     ($10.36)    in 9 hand(s)    [VPIP=99.9%, WIN=66.7%, WaSD=25.0%]
Mid S Connectors (T9-76s):      -13.0bb     ($27.40)    in 21 hand(s)   [VPIP=95.2%, WIN=25.0%, WaSD=16.7%]

-- Per-Hand Stats --
KK          64.7bb      $84.12     in 13 hand(s)
AKo         36.9bb      $69.15     in 19 hand(s)
JJ          35.4bb      $42.48     in 12 hand(s)
75s         33.6bb      $10.08     in 3 hand(s)
44          22.2bb      $19.97     in 9 hand(s)
A2s         17.2bb      $12.05     in 7 hand(s)
65s         16.6bb      $8.30      in 5 hand(s)
J8s         15.5bb      $12.44     in 8 hand(s)
QQ          15.3bb      $6.12      in 4 hand(s)
97o         11.9bb      $15.47     in 13 hand(s)
KJs         9.5bb       $3.80      in 4 hand(s)
K9o         9.3bb       $12.10     in 13 hand(s)
T8s         9.0bb       $8.07      in 9 hand(s)
J8o         8.7bb       $5.25      in 6 hand(s)
ATs         7.3bb       $2.92      in 4 hand(s)
A7s         6.8bb       $6.15      in 9 hand(s)
AJs         8.7bb       $5.33      in 8 hand(s)
A2o         6.7bb       $10.66     in 16 hand(s)
TT          2.0bb       $5.01      in 8 hand(s)
Q5s         5.9bb       $3.54      in 6 hand(s)
A6o         5.7bb       $8.01      in 14 hand(s)
T6s         5.7bb       $2.83      in 5 hand(s)
T7s         5.4bb       $2.15      in 4 hand(s)
96s         5.4bb       $1.61      in 3 hand(s)
A7o         4.9bb       $7.65      in 16 hand(s)
98s         4.8bb       $3.23      in 7 hand(s)
AQo         3.3bb       $12.28     in 27 hand(s)
55          4.3bb       $3.00      in 7 hand(s)
K7s         4.3bb       $3.84      in 9 hand(s)
53s         4.2bb       $2.52      in 6 hand(s)
JTs         0.0bb       $3.15      in 10 hand(s)
77          3.0bb       $5.67      in 19 hand(s)
42o         3.0bb       $3.50      in 12 hand(s)
J2s         2.9bb       $1.45      in 5 hand(s)
54o         2.8bb       $3.05      in 11 hand(s)
A3s         2.5bb       $1.50      in 6 hand(s)
52s         2.5bb       $1.25      in 5 hand(s)
A5o         2.3bb       $4.05      in 18 hand(s)
72o         1.9bb       $1.74      in 9 hand(s)
QTo         1.7bb       $3.92      in 23 hand(s)
Q8s         1.5bb       $1.55      in 10 hand(s)
76o         1.5bb       $1.35      in 9 hand(s)
T2o         1.2bb       $0.70      in 6 hand(s)
K3s         0.9bb       $0.62      in 7 hand(s)
Q7o         0.1bb       $1.45      in 18 hand(s)
96o         0.8bb       $0.75      in 10 hand(s)
K2o         0.7bb       $0.96      in 13 hand(s)
43o         0.6bb       $0.45      in 7 hand(s)
JTo         0.6bb       $0.75      in 12 hand(s)
J5o         0.4bb       $0.20      in 5 hand(s)
T9o         0.4bb       $0.37      in 13 hand(s)
A4s         0.2bb       $0.17      in 7 hand(s)
A3o         -3.1bb      $0.27      in 12 hand(s)
82s         0.2bb       $0.10      in 5 hand(s)
63o         0.2bb       $0.20      in 10 hand(s)
65o         0.2bb       $0.12      in 7 hand(s)
76s         0.1bb       $0.05      in 5 hand(s)
73s         0.1bb       $0.05      in 7 hand(s)
K3o         0.0bb       ($0.05)    in 12 hand(s)
84o         -0.1bb      ($0.05)    in 5 hand(s)
94o         -0.2bb      ($0.10)    in 6 hand(s)
74o         -0.3bb      ($0.30)    in 13 hand(s)
A9o         -0.1bb      ($0.63)    in 24 hand(s)
53o         -0.5bb      ($0.25)    in 5 hand(s)
Q3o         -0.5bb      ($0.65)    in 13 hand(s)
32s         -0.6bb      ($0.30)    in 5 hand(s)
52o         -0.6bb      ($0.25)    in 4 hand(s)
T3o         -0.7bb      ($0.60)    in 9 hand(s)
82o         -0.6bb      ($0.40)    in 6 hand(s)
93o         -0.7bb      ($0.55)    in 8 hand(s)
J3o         -0.6bb      ($0.35)    in 5 hand(s)
J7o         -0.7bb      ($0.50)    in 7 hand(s)
86o         -0.7bb      ($0.50)    in 7 hand(s)
T6o         -0.7bb      ($0.65)    in 9 hand(s)
95o         -0.6bb      ($0.60)    in 8 hand(s)
T3s         -0.5bb      ($0.45)    in 6 hand(s)
AJo         -0.8bb      ($2.02)    in 26 hand(s)
K5o         -0.8bb      ($0.80)    in 10 hand(s)
85o         -0.7bb      ($1.25)    in 15 hand(s)
Q6o         -0.8bb      ($0.85)    in 10 hand(s)
32o         -0.7bb      ($0.60)    in 7 hand(s)
83o         -0.7bb      ($0.95)    in 11 hand(s)
75o         -0.9bb      ($1.00)    in 11 hand(s)
Q4o         -0.9bb      ($1.50)    in 16 hand(s)
92o         -1.0bb      ($1.20)    in 12 hand(s)
62o         -1.1bb      ($0.65)    in 6 hand(s)
Q2o         -0.9bb      ($0.55)    in 5 hand(s)
73o         -1.1bb      ($0.90)    in 8 hand(s)
K6o         -1.1bb      ($1.25)    in 11 hand(s)
J2o         -1.2bb      ($1.05)    in 9 hand(s)
64o         -1.2bb      ($0.60)    in 5 hand(s)
K8o         -1.2bb      ($1.35)    in 10 hand(s)
J9o         -1.4bb      ($0.95)    in 7 hand(s)
J4s         -1.5bb      ($0.45)    in 3 hand(s)
Q5o         -1.5bb      ($0.60)    in 4 hand(s)
J4o         -1.2bb      ($0.45)    in 3 hand(s)
A8s         -1.5bb      ($1.54)    in 10 hand(s)
K9s         -1.7bb      ($1.55)    in 9 hand(s)
T7o         -1.7bb      ($2.25)    in 13 hand(s)
Q2s         -1.8bb      ($1.40)    in 8 hand(s)
K7o         -1.7bb      ($1.42)    in 8 hand(s)
T8o         -1.8bb      ($1.45)    in 8 hand(s)
62s         -1.9bb      ($0.95)    in 5 hand(s)
87o         -2.0bb      ($1.40)    in 7 hand(s)
63s         -2.1bb      ($2.35)    in 11 hand(s)
22          -2.2bb      ($2.17)    in 10 hand(s)
98o         -2.1bb      ($3.05)    in 14 hand(s)
K4o         -2.2bb      ($2.65)    in 12 hand(s)
Q6s         -2.4bb      ($0.95)    in 4 hand(s)
A5s         -2.5bb      ($1.25)    in 5 hand(s)
Q8o         -2.5bb      ($2.75)    in 11 hand(s)
T4o         -2.4bb      ($2.30)    in 9 hand(s)
J6o         -2.6bb      ($1.85)    in 7 hand(s)
J7s         -2.7bb      ($0.80)    in 3 hand(s)
86s         -2.3bb      ($2.17)    in 8 hand(s)
Q9o         -2.8bb      ($2.22)    in 8 hand(s)
A4o         -2.7bb      ($3.58)    in 12 hand(s)
42s         -2.9bb      ($2.15)    in 7 hand(s)
ATo         -3.6bb      ($5.01)    in 14 hand(s)
AKs         -3.8bb      ($3.01)    in 8 hand(s)
KTs         -3.9bb      ($1.95)    in 5 hand(s)
T5o         -4.2bb      ($1.70)    in 4 hand(s)
Q3s         -4.2bb      ($1.70)    in 4 hand(s)
85s         -4.3bb      ($4.30)    in 10 hand(s)
KJo         -4.8bb      ($9.63)    in 20 hand(s)
33          -4.9bb      ($5.85)    in 12 hand(s)
97s         -5.0bb      ($3.00)    in 6 hand(s)
K8s         -5.3bb      ($3.69)    in 7 hand(s)
72s         -5.3bb      ($2.65)    in 5 hand(s)
K2s         -5.4bb      ($5.40)    in 10 hand(s)
Q4s         -5.4bb      ($2.70)    in 5 hand(s)
J9s         -2.1bb      ($5.46)    in 10 hand(s)
KTo         -5.5bb      ($8.16)    in 14 hand(s)
K5s         -5.9bb      ($3.53)    in 6 hand(s)
A9s         -6.3bb      ($4.41)    in 7 hand(s)
66          -6.1bb      ($6.57)    in 10 hand(s)
54s         -8.2bb      ($5.25)    in 6 hand(s)
A6s         -9.4bb      ($3.75)    in 4 hand(s)
A8o         -9.7bb      ($8.70)    in 9 hand(s)
T2s         -11.1bb     ($5.53)    in 5 hand(s)
AA          -11.5bb     ($10.36)   in 9 hand(s)
84s         -12.3bb     ($6.16)    in 5 hand(s)
QJo         -12.6bb     ($15.13)   in 12 hand(s)
83s         -13.0bb     ($7.83)    in 6 hand(s)
QJs         -13.4bb     ($8.07)    in 6 hand(s)
QTs         -13.6bb     ($8.17)    in 6 hand(s)
Q9s         -15.8bb     ($17.38)   in 11 hand(s)
K6s         -16.1bb     ($16.09)   in 10 hand(s)
KQs         -16.8bb     ($16.82)   in 10 hand(s)
88          -15.3bb     ($18.66)   in 11 hand(s)
AQs         -18.2bb     ($5.45)    in 3 hand(s)
99          -23.1bb     ($31.10)   in 15 hand(s)
KQo         -20.7bb     ($37.43)   in 18 hand(s)
T9s         -25.8bb     ($12.90)   in 5 hand(s)
87s         -59.3bb     ($17.78)   in 3 hand(s)
```
