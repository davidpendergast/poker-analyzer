
Program that parses logs from Pokernow and gives profit/loss breakdowns of various situations.

Sample Output:

```
-- Summary --
Hands:      2292 (in 14 sessions)
Saw Flop:   206 time(s) (8.99%)
Net Gain:   $407.73

-- Situational Breakdowns --
KK:                             82.2bb      $73.97      in 9 hand(s)    [VPIP=99.9%, WIN=88.9%, WaSD=80.0%]
AK:                             45.1bb      $116.53     in 26 hand(s)   [VPIP=99.9%, WIN=53.8%, WaSD=57.1%]
Premiums (JJ+, AQ+):            40.8bb      $130.58     in 32 hand(s)   [VPIP=96.9%, WIN=74.2%, WaSD=76.5%]
IP Post-Flop:                   22.3bb      $194.05     in 88 hand(s)   [VPIP=98.9%, WIN=52.9%, WaSD=52.3%]
2-way Flops:                    20.6bb      $383.41     in 178 hand(s)  [VPIP=97.8%, WIN=55.7%, WaSD=55.6%]
QQ:                             19.8bb      $7.92       in 4 hand(s)    [VPIP=99.9%, WIN=75.0%, WaSD=99.9%]
Gets to Showdown:               17.1bb      $369.47     in 206 hand(s)  [VPIP=97.1%, WIN=54.0%, WaSD=53.4%]
OoP Post-Flop:                  15.5bb      $186.00     in 108 hand(s)  [VPIP=96.3%, WIN=54.8%, WaSD=54.6%]
Low S Ax (A5-A2s):              7.3bb       $17.63      in 24 hand(s)   [VPIP=83.3%, WIN=30.0%, WaSD=99.9%]
Mid S Ax (AJ-A6s):              7.4bb       $28.51      in 40 hand(s)   [VPIP=90.0%, WIN=30.6%, WaSD=63.6%]
Low Pairs (66-22):              5.8bb       $26.65      in 47 hand(s)   [VPIP=91.5%, WIN=20.9%, WaSD=70.0%]
Mid oS Ax (AJ-A6o):             4.5bb       $49.43      in 111 hand(s)  [VPIP=67.6%, WIN=34.7%, WaSD=47.6%]
Mid Position:                   3.3bb       $153.11     in 447 hand(s)  [VPIP=36.0%, WIN=36.6%, WaSD=71.1%]
UTG:                            3.1bb       $107.39     in 334 hand(s)  [VPIP=32.6%, WIN=25.7%, WaSD=60.0%]
Low oS Ax (A5-A2o):             2.2bb       $27.21      in 103 hand(s)  [VPIP=27.2%, WIN=35.7%, WaSD=62.5%]
BTN:                            2.4bb       $96.43      in 407 hand(s)  [VPIP=39.6%, WIN=33.5%, WaSD=50.0%]
as BB:                          2.1bb       $83.61      in 390 hand(s)  [VPIP=35.4%, WIN=36.2%, WaSD=53.3%]
Early Position:                 2.0bb       $95.75      in 469 hand(s)  [VPIP=38.2%, WIN=31.8%, WaSD=53.2%]
from Blinds:                    1.7bb       $142.66     in 782 hand(s)  [VPIP=35.8%, WIN=37.1%, WaSD=51.8%]
All Hands:                      1.7bb       $407.73     in 2292 hand(s) [VPIP=33.6%, WIN=32.0%, WaSD=53.4%]
as SB:                          1.4bb       $59.05      in 392 hand(s)  [VPIP=36.2%, WIN=38.0%, WaSD=50.0%]
Doesn't get to Showdown:        1.3bb       $73.11      in 571 hand(s)  [VPIP=99.9%, WIN=24.3%, WaSD= 0.0%]
Late Position:                  0.7bb       $45.85      in 658 hand(s)  [VPIP=35.6%, WIN=29.5%, WaSD=44.8%]
High S Connectors (AK-JTs):     -1.1bb      $0.96       in 29 hand(s)   [VPIP=89.7%, WIN=30.8%, WaSD=46.2%]
Junky oS Kx (KT-K2o):           0.3bb       $4.81       in 186 hand(s)  [VPIP=16.7%, WIN=38.7%, WaSD=66.7%]
Junky oS Qx (QT-Q2o):           0.1bb       $3.50       in 205 hand(s)  [VPIP=18.5%, WIN=31.6%, WaSD=50.0%]
3-way Flops:                    -0.6bb      ($1.27)     in 21 hand(s)   [VPIP=90.5%, WIN=42.1%, WaSD=38.1%]
Suited Kx (KT-K2s):             -0.9bb      ($6.11)     in 67 hand(s)   [VPIP=82.1%, WIN=21.8%, WaSD=42.9%]
Suited Qx (QT-Q2s):             -1.7bb      ($11.23)    in 68 hand(s)   [VPIP=61.8%, WIN=14.3%, WaSD=28.6%]
Low S Connectors (32-65s):      -1.5bb      ($3.05)     in 18 hand(s)   [VPIP=66.7%, WIN=25.0%, WaSD=50.0%]
Mid Pairs (TT-77):              -3.3bb      ($8.05)     in 46 hand(s)   [VPIP=91.3%, WIN=35.7%, WaSD=56.2%]
High S Gappers (AQ-J9s):        -1.2bb      ($5.06)     in 22 hand(s)   [VPIP=81.8%, WIN=11.1%, WaSD= 0.0%]
Mid S Connectors (T9-76s):      -4.2bb      ($8.98)     in 21 hand(s)   [VPIP=95.2%, WIN=25.0%, WaSD=16.7%]
Broadways (KQ KJ QJ):           -5.6bb      ($41.30)    in 73 hand(s)   [VPIP=80.8%, WIN=18.6%, WaSD=25.0%]
AA:                             -9.3bb      ($7.41)     in 8 hand(s)    [VPIP=99.9%, WIN=62.5%, WaSD=25.0%]
4-way+ Flops:                   -18.1bb     ($12.67)    in 7 hand(s)    [VPIP=99.9%, WIN=42.9%, WaSD=42.9%]

-- Per-Hand Stats --
KK          82.2bb      $73.97     in 9 hand(s)
JJ          56.1bb      $56.10     in 10 hand(s)
AKo         56.1bb      $105.97    in 19 hand(s)
75s         55.8bb      $16.73     in 3 hand(s)
44          27.5bb      $24.75     in 9 hand(s)
J8s         25.4bb      $20.28     in 8 hand(s)
TT          15.5bb      $13.74     in 6 hand(s)
AJs         23.1bb      $12.75     in 6 hand(s)
QQ          19.8bb      $7.92      in 4 hand(s)
KJs         18.2bb      $7.30      in 4 hand(s)
55          17.5bb      $12.22     in 7 hand(s)
AQo         13.6bb      $35.70     in 23 hand(s)
T8s         15.5bb      $13.96     in 9 hand(s)
A7s         15.4bb      $12.35     in 8 hand(s)
AKs         15.1bb      $10.56     in 7 hand(s)
A3s         14.2bb      $8.55      in 6 hand(s)
98s         14.2bb      $9.82      in 7 hand(s)
Q5s         13.8bb      $8.29      in 6 hand(s)
J8o         13.1bb      $7.85      in 6 hand(s)
ATs         12.8bb      $5.14      in 4 hand(s)
K9o         12.2bb      $14.70     in 12 hand(s)
K7s         11.8bb      $10.61     in 9 hand(s)
A6o         10.8bb      $12.96     in 12 hand(s)
A2o         10.7bb      $15.98     in 15 hand(s)
A4s         9.9bb       $6.96      in 7 hand(s)
96s         9.9bb       $2.96      in 3 hand(s)
53s         8.9bb       $5.32      in 6 hand(s)
T7s         8.8bb       $3.50      in 4 hand(s)
JTs         2.5bb       $5.75      in 7 hand(s)
77          8.0bb       $10.42     in 13 hand(s)
A9o         8.2bb       $13.42     in 17 hand(s)
97o         7.5bb       $8.27      in 11 hand(s)
A7o         7.5bb       $11.84     in 16 hand(s)
AJo         7.2bb       $18.42     in 25 hand(s)
A5o         6.0bb       $10.16     in 17 hand(s)
K3s         5.8bb       $3.49      in 6 hand(s)
A2s         5.3bb       $2.67      in 5 hand(s)
76s         4.9bb       $2.47      in 5 hand(s)
52s         4.9bb       $2.45      in 5 hand(s)
42o         4.5bb       $4.45      in 10 hand(s)
QTo         4.4bb       $9.76      in 22 hand(s)
J2s         4.3bb       $2.15      in 5 hand(s)
A3o         -2.9bb      $3.00      in 8 hand(s)
54o         3.7bb       $3.00      in 8 hand(s)
Q8s         3.4bb       $3.05      in 9 hand(s)
Q7o         2.1bb       $5.15      in 16 hand(s)
76o         3.2bb       $2.55      in 8 hand(s)
T2o         2.6bb       $1.55      in 6 hand(s)
72o         2.4bb       $2.19      in 9 hand(s)
65o         2.1bb       $1.24      in 6 hand(s)
J9o         1.7bb       $1.00      in 6 hand(s)
96o         1.5bb       $1.50      in 10 hand(s)
K9s         1.3bb       $1.05      in 8 hand(s)
K2o         1.1bb       $1.24      in 11 hand(s)
62s         1.1bb       $0.55      in 5 hand(s)
82s         1.0bb       $0.50      in 5 hand(s)
J5o         1.0bb       $0.50      in 5 hand(s)
T9o         1.0bb       $1.05      in 12 hand(s)
32s         0.8bb       $0.40      in 5 hand(s)
63o         0.7bb       $0.70      in 10 hand(s)
A9s         0.5bb       $0.36      in 7 hand(s)
K3o         0.5bb       $0.40      in 10 hand(s)
A8s         0.4bb       $0.31      in 8 hand(s)
T6s         0.4bb       $0.15      in 4 hand(s)
94o         -0.0bb      $0.00      in 6 hand(s)
74o         -0.2bb      ($0.05)    in 12 hand(s)
84o         -0.1bb      ($0.05)    in 5 hand(s)
ATo         -0.2bb      ($0.23)    in 10 hand(s)
Q3o         -0.3bb      ($0.35)    in 13 hand(s)
53o         -0.5bb      ($0.20)    in 4 hand(s)
43o         -0.6bb      ($0.35)    in 6 hand(s)
52o         -0.6bb      ($0.25)    in 4 hand(s)
T3o         -0.7bb      ($0.60)    in 9 hand(s)
82o         -0.6bb      ($0.40)    in 6 hand(s)
92o         -0.7bb      ($0.75)    in 11 hand(s)
K5o         -0.6bb      ($0.55)    in 8 hand(s)
J3o         -0.6bb      ($0.35)    in 5 hand(s)
93o         -0.7bb      ($0.50)    in 7 hand(s)
T6o         -0.7bb      ($0.65)    in 9 hand(s)
83o         -0.6bb      ($0.75)    in 10 hand(s)
95o         -0.6bb      ($0.45)    in 6 hand(s)
T3s         -0.5bb      ($0.45)    in 6 hand(s)
86o         -0.8bb      ($0.45)    in 6 hand(s)
J7o         -0.8bb      ($0.45)    in 6 hand(s)
K8o         -0.6bb      ($0.70)    in 9 hand(s)
75o         -0.8bb      ($0.90)    in 11 hand(s)
Q6o         -0.8bb      ($0.75)    in 9 hand(s)
32o         -0.7bb      ($0.60)    in 7 hand(s)
K6o         -0.9bb      ($0.70)    in 8 hand(s)
62o         -0.9bb      ($0.55)    in 6 hand(s)
KJo         -0.9bb      ($1.88)    in 19 hand(s)
64o         -1.0bb      ($0.30)    in 3 hand(s)
Q4o         -1.0bb      ($1.40)    in 14 hand(s)
Q2o         -0.8bb      ($0.40)    in 4 hand(s)
A5s         -1.1bb      ($0.55)    in 5 hand(s)
73o         -1.1bb      ($0.80)    in 7 hand(s)
T8o         -1.3bb      ($1.05)    in 8 hand(s)
J2o         -1.4bb      ($0.95)    in 7 hand(s)
Q6s         -1.4bb      ($0.55)    in 4 hand(s)
98o         -1.3bb      ($1.80)    in 13 hand(s)
K7o         -1.3bb      ($1.12)    in 8 hand(s)
J4s         -1.5bb      ($0.45)    in 3 hand(s)
Q5o         -1.5bb      ($0.60)    in 4 hand(s)
73s         -1.5bb      ($0.90)    in 6 hand(s)
Q9o         -1.5bb      ($1.22)    in 8 hand(s)
42s         -1.4bb      ($0.95)    in 6 hand(s)
T7o         -1.6bb      ($2.15)    in 13 hand(s)
86s         -1.2bb      ($1.17)    in 7 hand(s)
K4o         -1.8bb      ($2.00)    in 11 hand(s)
Q2s         -1.9bb      ($1.30)    in 7 hand(s)
KTs         -1.9bb      ($0.75)    in 4 hand(s)
A4o         -1.6bb      ($1.93)    in 10 hand(s)
87o         -2.0bb      ($1.40)    in 7 hand(s)
J6o         -2.1bb      ($1.45)    in 7 hand(s)
63s         -2.4bb      ($1.65)    in 7 hand(s)
T4o         -2.4bb      ($1.75)    in 7 hand(s)
J7s         -2.7bb      ($0.80)    in 3 hand(s)
85o         -2.6bb      ($4.15)    in 15 hand(s)
22          -2.9bb      ($2.57)    in 9 hand(s)
T5o         -3.0bb      ($0.90)    in 3 hand(s)
J9s         -0.7bb      ($3.05)    in 10 hand(s)
K2s         -3.3bb      ($2.65)    in 8 hand(s)
Q4s         -3.4bb      ($1.70)    in 5 hand(s)
JTo         -3.6bb      ($3.60)    in 10 hand(s)
33          -3.7bb      ($4.40)    in 12 hand(s)
97s         -3.7bb      ($2.20)    in 6 hand(s)
K8s         -3.7bb      ($2.59)    in 7 hand(s)
66          -3.2bb      ($3.35)    in 9 hand(s)
54s         -3.1bb      ($1.90)    in 5 hand(s)
84s         -3.8bb      ($1.91)    in 5 hand(s)
Q3s         -4.2bb      ($1.70)    in 4 hand(s)
72s         -4.5bb      ($2.25)    in 5 hand(s)
85s         -4.8bb      ($4.30)    in 9 hand(s)
KTo         -5.5bb      ($6.46)    in 11 hand(s)
K5s         -5.9bb      ($3.53)    in 6 hand(s)
A6s         -6.0bb      ($2.40)    in 4 hand(s)
QJs         -6.9bb      ($4.17)    in 6 hand(s)
Q8o         -7.4bb      ($6.69)    in 9 hand(s)
A8o         -8.7bb      ($6.98)    in 8 hand(s)
QJo         -8.9bb      ($10.73)   in 12 hand(s)
T2s         -9.2bb      ($4.58)    in 5 hand(s)
83s         -9.2bb      ($5.51)    in 6 hand(s)
AA          -9.3bb      ($7.41)    in 8 hand(s)
88          -8.2bb      ($10.06)   in 10 hand(s)
KQo         -11.4bb     ($20.64)   in 18 hand(s)
K6s         -11.7bb     ($11.74)   in 10 hand(s)
Q9s         -12.0bb     ($10.76)   in 9 hand(s)
QTs         -12.1bb     ($6.06)    in 5 hand(s)
KQs         -14.0bb     ($11.18)   in 8 hand(s)
99          -19.0bb     ($22.15)   in 14 hand(s)
T9s         -17.5bb     ($8.75)    in 5 hand(s)
87s         -41.7bb     ($12.52)   in 3 hand(s)
```
