
Program that parses logs from Pokernow and gives profit/loss breakdowns of various situations.

Sample Output:

```
-- Summary --
Hands:      2170 (in 13 sessions)
Saw Flop:   200 time(s) (9.22%)
Net Gain:   $393.41

-- Situational Breakdowns --
Premiums (JJ+, AQ+):            40.8bb      $130.58     in 32 hand(s)   [VPIP=96.9%, WIN=71.9%, WaSD=76.5%]
IP Post-Flop:                   22.5bb      $196.05     in 87 hand(s)   [VPIP=98.9%, WIN=52.9%, WaSD=52.9%]
2-way Flops:                    21.3bb      $366.81     in 172 hand(s)  [VPIP=98.3%, WIN=54.7%, WaSD=54.7%]
Gets to Showdown:               17.6bb      $352.87     in 200 hand(s)  [VPIP=97.5%, WIN=52.5%, WaSD=52.5%]
OoP Post-Flop:                  16.3bb      $167.40     in 103 hand(s)  [VPIP=97.1%, WIN=52.4%, WaSD=52.4%]
Mid S Ax (AJ-A6s):              7.8bb       $29.62      in 38 hand(s)   [VPIP=92.1%, WIN=31.6%, WaSD=63.6%]
Low S Ax (A5-A2s):              7.3bb       $17.63      in 24 hand(s)   [VPIP=83.3%, WIN=25.0%, WaSD=99.9%]
Low Pairs (66-22):              6.0bb       $27.10      in 45 hand(s)   [VPIP=93.3%, WIN=20.0%, WaSD=70.0%]
Mid oS Ax (AJ-A6o):             4.8bb       $49.58      in 104 hand(s)  [VPIP=69.2%, WIN=26.0%, WaSD=47.6%]
Mid Position:                   3.5bb       $146.51     in 422 hand(s)  [VPIP=36.5%, WIN=15.2%, WaSD=69.8%]
UTG:                            3.3bb       $104.35     in 315 hand(s)  [VPIP=33.7%, WIN= 8.6%, WaSD=58.3%]
BTN:                            2.6bb       $98.33      in 384 hand(s)  [VPIP=40.9%, WIN=15.4%, WaSD=51.2%]
Low oS Ax (A5-A2o):             2.3bb       $22.21      in 96 hand(s)   [VPIP=27.1%, WIN=10.4%, WaSD=57.1%]
as BB:                          2.2bb       $80.76      in 370 hand(s)  [VPIP=37.0%, WIN=17.6%, WaSD=52.3%]
Early Position:                 2.1bb       $92.71      in 450 hand(s)  [VPIP=39.1%, WIN=12.7%, WaSD=52.2%]
from Blinds:                    1.8bb       $135.38     in 742 hand(s)  [VPIP=36.7%, WIN=15.8%, WaSD=50.6%]
All Hands:                      1.8bb       $393.41     in 2170 hand(s) [VPIP=34.5%, WIN=11.8%, WaSD=52.5%]
as SB:                          1.5bb       $54.62      in 372 hand(s)  [VPIP=36.3%, WIN=14.0%, WaSD=48.7%]
Doesn't get to Showdown:        1.3bb       $72.94      in 553 hand(s)  [VPIP=99.9%, WIN=24.6%, WaSD= 0.0%]
Late Position:                  0.8bb       $48.45      in 620 hand(s)  [VPIP=36.9%, WIN=11.9%, WaSD=45.6%]
Junky oS Kx (KT-K2o):           0.3bb       $5.58       in 168 hand(s)  [VPIP=17.9%, WIN= 7.1%, WaSD=66.7%]
Junky oS Qx (QT-Q2o):           0.1bb       $1.85       in 197 hand(s)  [VPIP=18.8%, WIN= 6.6%, WaSD=50.0%]
3-way Flops:                    -0.6bb      ($1.27)     in 21 hand(s)   [VPIP=90.5%, WIN=38.1%, WaSD=38.1%]
Suited Kx (KT-K2s):             -0.9bb      ($6.11)     in 66 hand(s)   [VPIP=83.3%, WIN=18.2%, WaSD=42.9%]
High S Connectors (AK-JTs):     -1.1bb      ($3.09)     in 28 hand(s)   [VPIP=89.3%, WIN=28.6%, WaSD=41.7%]
High S Gappers (AQ-J9s):        -1.4bb      ($2.71)     in 19 hand(s)   [VPIP=84.2%, WIN=15.8%, WaSD= 0.0%]
Low S Connectors (32-65s):      -1.7bb      ($2.70)     in 16 hand(s)   [VPIP=68.8%, WIN=25.0%, WaSD=50.0%]
Suited Qx (QT-Q2s):             -1.7bb      ($11.23)    in 66 hand(s)   [VPIP=63.6%, WIN= 9.1%, WaSD=28.6%]
Mid Pairs (TT-77):              -3.7bb      ($15.15)    in 41 hand(s)   [VPIP=92.7%, WIN=31.7%, WaSD=50.0%]
Mid S Connectors (T9-76s):      -4.4bb      ($8.88)     in 20 hand(s)   [VPIP=95.0%, WIN=25.0%, WaSD=16.7%]
Broadways (KQ KJ QJ):           -5.9bb      ($41.10)    in 70 hand(s)   [VPIP=82.9%, WIN=18.6%, WaSD=25.0%]
4-way+ Flops:                   -18.1bb     ($12.67)    in 7 hand(s)    [VPIP=99.9%, WIN=42.9%, WaSD=42.9%]

-- Per-Hand Stats --
KK          82.2bb      $73.97     in 9 hand(s)
AKo         59.3bb      $106.67    in 18 hand(s)
JJ          56.1bb      $56.10     in 10 hand(s)
75s         55.8bb      $16.73     in 3 hand(s)
AJs         27.7bb      $13.86     in 5 hand(s)
44          27.5bb      $24.75     in 9 hand(s)
J8s         25.4bb      $20.28     in 8 hand(s)
QQ          19.8bb      $7.92      in 4 hand(s)
TT          18.5bb      $9.24      in 5 hand(s)
KJs         18.2bb      $7.30      in 4 hand(s)
55          17.5bb      $12.22     in 7 hand(s)
98s         16.5bb      $9.92      in 6 hand(s)
T8s         15.5bb      $13.96     in 9 hand(s)
A7s         15.4bb      $12.35     in 8 hand(s)
AKs         15.1bb      $10.56     in 7 hand(s)
A3s         14.2bb      $8.55      in 6 hand(s)
AQo         14.2bb      $31.20     in 22 hand(s)
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
A9o         8.7bb       $13.87     in 16 hand(s)
A7o         8.6bb       $11.99     in 14 hand(s)
77          8.0bb       $10.42     in 13 hand(s)
AJo         7.8bb       $17.97     in 23 hand(s)
97o         7.5bb       $8.27      in 11 hand(s)
A5o         6.4bb       $10.21     in 16 hand(s)
K3s         5.8bb       $3.49      in 6 hand(s)
A2s         5.3bb       $2.67      in 5 hand(s)
42o         5.1bb       $4.55      in 9 hand(s)
76s         4.9bb       $2.47      in 5 hand(s)
52s         4.9bb       $2.45      in 5 hand(s)
QTo         4.4bb       $9.76      in 22 hand(s)
J2s         4.3bb       $2.15      in 5 hand(s)
54o         3.7bb       $3.00      in 8 hand(s)
Q8s         3.4bb       $3.05      in 9 hand(s)
76o         3.2bb       $2.55      in 8 hand(s)
JTs         2.8bb       $1.70      in 6 hand(s)
T2o         2.6bb       $1.55      in 6 hand(s)
72o         2.4bb       $2.19      in 9 hand(s)
Q7o         2.4bb       $3.40      in 14 hand(s)
65o         2.1bb       $1.24      in 6 hand(s)
J9o         1.7bb       $1.00      in 6 hand(s)
96o         1.5bb       $1.50      in 10 hand(s)
K9s         1.3bb       $1.05      in 8 hand(s)
K2o         1.1bb       $1.24      in 11 hand(s)
62s         1.1bb       $0.55      in 5 hand(s)
T9o         1.0bb       $1.15      in 11 hand(s)
82s         1.0bb       $0.50      in 5 hand(s)
J5o         1.0bb       $0.50      in 5 hand(s)
32s         0.8bb       $0.40      in 5 hand(s)
63o         0.7bb       $0.70      in 10 hand(s)
K3o         0.6bb       $0.50      in 9 hand(s)
A9s         0.5bb       $0.36      in 7 hand(s)
A8s         0.4bb       $0.31      in 8 hand(s)
T6s         0.4bb       $0.15      in 4 hand(s)
94o         -0.0bb      $0.00      in 6 hand(s)
84o         -0.1bb      ($0.05)    in 5 hand(s)
74o         -0.2bb      ($0.20)    in 11 hand(s)
ATo         -0.2bb      ($0.23)    in 10 hand(s)
Q3o         -0.3bb      ($0.35)    in 13 hand(s)
53o         -0.5bb      ($0.20)    in 4 hand(s)
43o         -0.6bb      ($0.35)    in 6 hand(s)
52o         -0.6bb      ($0.25)    in 4 hand(s)
T3o         -0.7bb      ($0.60)    in 9 hand(s)
92o         -0.7bb      ($0.75)    in 11 hand(s)
82o         -0.7bb      ($0.35)    in 5 hand(s)
95o         -0.7bb      ($0.35)    in 5 hand(s)
K5o         -0.7bb      ($0.50)    in 7 hand(s)
93o         -0.7bb      ($0.50)    in 7 hand(s)
K8o         -0.7bb      ($0.50)    in 7 hand(s)
T6o         -0.7bb      ($0.65)    in 9 hand(s)
J3o         -0.8bb      ($0.30)    in 4 hand(s)
83o         -0.8bb      ($0.60)    in 8 hand(s)
86o         -0.8bb      ($0.45)    in 6 hand(s)
J7o         -0.8bb      ($0.45)    in 6 hand(s)
T3s         -0.8bb      ($0.30)    in 4 hand(s)
Q6o         -0.8bb      ($0.75)    in 9 hand(s)
32o         -0.8bb      ($0.50)    in 6 hand(s)
75o         -0.8bb      ($0.85)    in 10 hand(s)
K6o         -0.9bb      ($0.70)    in 8 hand(s)
J9s         -0.9bb      ($0.70)    in 8 hand(s)
62o         -0.9bb      ($0.55)    in 6 hand(s)
KJo         -1.0bb      ($1.78)    in 18 hand(s)
64o         -1.0bb      ($0.30)    in 3 hand(s)
Q2o         -1.0bb      ($0.30)    in 3 hand(s)
Q4o         -1.0bb      ($1.40)    in 14 hand(s)
A5s         -1.1bb      ($0.55)    in 5 hand(s)
73o         -1.1bb      ($0.80)    in 7 hand(s)
T8o         -1.3bb      ($1.05)    in 8 hand(s)
J2o         -1.4bb      ($0.95)    in 7 hand(s)
86s         -1.4bb      ($0.82)    in 6 hand(s)
Q6s         -1.4bb      ($0.55)    in 4 hand(s)
98o         -1.5bb      ($1.75)    in 12 hand(s)
J4s         -1.5bb      ($0.45)    in 3 hand(s)
Q5o         -1.5bb      ($0.60)    in 4 hand(s)
73s         -1.5bb      ($0.90)    in 6 hand(s)
Q9o         -1.5bb      ($1.22)    in 8 hand(s)
K7o         -1.5bb      ($1.07)    in 7 hand(s)
42s         -1.7bb      ($0.85)    in 5 hand(s)
T7o         -1.8bb      ($2.10)    in 12 hand(s)
A4o         -1.8bb      ($1.58)    in 9 hand(s)
K4o         -1.8bb      ($2.00)    in 11 hand(s)
Q2s         -1.9bb      ($1.30)    in 7 hand(s)
KTs         -1.9bb      ($0.75)    in 4 hand(s)
87o         -2.0bb      ($1.40)    in 7 hand(s)
J6o         -2.1bb      ($1.45)    in 7 hand(s)
63s         -2.4bb      ($1.65)    in 7 hand(s)
J7s         -2.7bb      ($0.80)    in 3 hand(s)
T4o         -2.8bb      ($1.65)    in 6 hand(s)
22          -2.9bb      ($2.57)    in 9 hand(s)
T5o         -3.0bb      ($0.90)    in 3 hand(s)
85o         -3.0bb      ($3.95)    in 13 hand(s)
K2s         -3.3bb      ($2.65)    in 8 hand(s)
Q4s         -3.4bb      ($1.70)    in 5 hand(s)
A3o         -3.4bb      ($2.40)    in 7 hand(s)
JTo         -3.6bb      ($3.60)    in 10 hand(s)
33          -3.7bb      ($4.40)    in 12 hand(s)
97s         -3.7bb      ($2.20)    in 6 hand(s)
K8s         -3.7bb      ($2.59)    in 7 hand(s)
84s         -3.8bb      ($1.91)    in 5 hand(s)
54s         -3.9bb      ($1.55)    in 4 hand(s)
66          -4.1bb      ($2.90)    in 7 hand(s)
Q3s         -4.2bb      ($1.70)    in 4 hand(s)
72s         -4.5bb      ($2.25)    in 5 hand(s)
85s         -4.8bb      ($4.30)    in 9 hand(s)
K5s         -5.9bb      ($3.53)    in 6 hand(s)
A6s         -6.0bb      ($2.40)    in 4 hand(s)
KTo         -6.1bb      ($6.09)    in 10 hand(s)
QJs         -6.9bb      ($4.17)    in 6 hand(s)
Q8o         -7.4bb      ($6.69)    in 9 hand(s)
A8o         -8.7bb      ($6.98)    in 8 hand(s)
QJo         -8.9bb      ($10.73)   in 12 hand(s)
T2s         -9.2bb      ($4.58)    in 5 hand(s)
83s         -9.2bb      ($5.51)    in 6 hand(s)
AA          -9.3bb      ($7.41)    in 8 hand(s)
88          -10.2bb     ($8.16)    in 8 hand(s)
K6s         -11.7bb     ($11.74)   in 10 hand(s)
Q9s         -12.0bb     ($10.76)   in 9 hand(s)
KQo         -12.1bb     ($20.54)   in 17 hand(s)
QTs         -12.1bb     ($6.06)    in 5 hand(s)
KQs         -14.0bb     ($11.18)   in 8 hand(s)
T9s         -17.5bb     ($8.75)    in 5 hand(s)
99          -20.5bb     ($26.65)   in 13 hand(s)
87s         -41.7bb     ($12.52)   in 3 hand(s)

-- Per-Hand Profit Table --
            A           K           Q           J           T           9           8           7           6           5           4           3           2           
A           -9.3 (8)    15.1 (7)    -16.2 (2)   27.7 (5)    12.8 (4)    0.5 (7)     0.4 (8)     15.4 (8)    -6.0 (4)    -1.1 (5)    9.9 (7)     14.2 (6)    5.3 (5)     
K           59.3 (18)   82.2 (9)    -14.0 (8)   18.2 (4)    -1.9 (4)    1.3 (8)     -3.7 (7)    11.8 (9)    -11.7 (10)  -5.9 (6)    0.0 (0)     5.8 (6)     -3.3 (8)    
Q           14.2 (22)   -12.1 (17)  19.8 (4)    -6.9 (6)    -12.1 (5)   -12.0 (9)   3.4 (9)     -2.5 (2)    -1.4 (4)    13.8 (6)    -3.4 (5)    -4.2 (4)    -1.9 (7)    
J           7.8 (23)    -1.0 (18)   -8.9 (12)   56.1 (10)   2.8 (6)     -0.9 (8)    25.4 (8)    -2.7 (3)    -1.0 (1)    -3.0 (1)    -1.5 (3)    -2.0 (2)    4.3 (5)     
T           -0.2 (10)   -6.1 (10)   4.4 (22)    -3.6 (10)   18.5 (5)    -17.5 (5)   15.5 (9)    8.8 (4)     0.4 (4)     -1.0 (1)    -9.5 (2)    -0.8 (4)    -9.2 (5)    
9           8.7 (16)    12.2 (12)   -1.5 (8)    1.7 (6)     1.0 (11)    -20.5 (13)  16.5 (6)    -3.7 (6)    9.9 (3)     -3.5 (1)    0.0 (0)     0.0 (0)     0.0 (0)     
8           -8.7 (8)    -0.7 (7)    -7.4 (9)    13.1 (6)    -1.3 (8)    -1.5 (12)   -10.2 (8)   -41.7 (3)   -1.4 (6)    -4.8 (9)    -3.8 (5)    -9.2 (6)    1.0 (5)     
7           8.6 (14)    -1.5 (7)    2.4 (14)    -0.8 (6)    -1.8 (12)   7.5 (11)    -2.0 (7)    8.0 (13)    4.9 (5)     55.8 (3)    -0.8 (2)    -1.5 (6)    -4.5 (5)    
6           10.8 (12)   -0.9 (8)    -0.8 (9)    -2.1 (7)    -0.7 (9)    1.5 (10)    -0.8 (6)    3.2 (8)     -4.1 (7)    -6.0 (2)    8.1 (2)     -2.4 (7)    1.1 (5)     
5           6.4 (16)    -0.7 (7)    -1.5 (4)    1.0 (5)     -3.0 (3)    -0.7 (5)    -3.0 (13)   -0.8 (10)   2.1 (6)     17.5 (7)    -3.9 (4)    8.9 (6)     4.9 (5)     
4           -1.8 (9)    -1.8 (11)   -1.0 (14)   -3.0 (1)    -2.8 (6)    -0.0 (6)    -0.1 (5)    -0.2 (11)   -1.0 (3)    3.7 (8)     27.5 (9)    -1.8 (2)    -1.7 (5)    
3           -3.4 (7)    0.6 (9)     -0.3 (13)   -0.8 (4)    -0.7 (9)    -0.7 (7)    -0.8 (8)    -1.1 (7)    0.7 (10)    -0.5 (4)    -0.6 (6)    -3.7 (12)   0.8 (5)     
2           10.7 (15)   1.1 (11)    -1.0 (3)    -1.4 (7)    2.6 (6)     -0.7 (11)   -0.7 (5)    2.4 (9)     -0.9 (6)    -0.6 (4)    5.1 (9)     -0.8 (6)    -2.9 (9)
```
