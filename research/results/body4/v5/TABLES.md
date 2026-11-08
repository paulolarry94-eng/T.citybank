# Body-engulf range v5: tables (built by research/body4/tables_v5.py from study_v5.json and LOOK_2023_25.json)

R per trade is after spread, commission and slippage (RoboForex Prime published costs). Swaps are zero in every v5
setting: the safe window closes everything at 20:30 UTC, before the 22:00 UTC rollover, so the swap-free result is the
same number. 12 markets pooled. 2023-25 = the owner's logged look (description only, except the 4 primaries).

## 1. Paired comparisons (same timeframe and settings, only one thing changed; both sides >= 100 trades)

| Change | Period | Pairs | Share where the change is better | Mean change in R per trade |
|---|---|---|---|---|
| loose engulf instead of strict | 2011-19 | 240 | 26% | -0.013R |
| loose engulf instead of strict | 2020-22 | 182 | 56% | +0.004R |
| loose engulf instead of strict | 2023-25 (look) | 176 | 55% | +0.005R |
| layering on instead of off | 2011-19 | 176 | 62% | +0.030R |
| layering on instead of off | 2020-22 | 102 | 75% | +0.060R |
| layering on instead of off | 2023-25 (look) | 96 | 56% | +0.027R |

## 2a. Main settings at 2R (entry 50%, stop at the range end, breakeven at 75% on, lookback on): trades, R per trade

| Timeframe | strict engulf, no layering | strict engulf + layering | loose engulf, no layering | loose engulf + layering |
|---|---|---|---|---|
| M1 2011-19 | 23,692, -0.440R | 154, -0.239R | 67,562, -0.470R | 1,085, -0.450R |
| M5 2011-19 | 7,649, -0.240R | 57, -0.207R | 21,355, -0.257R | 379, -0.113R |
| M15 2011-19 | 3,032, -0.144R | 24, -0.133R | 8,457, -0.147R | 129, -0.037R |
| M30 2011-19 | 1,652, -0.105R | 8, -0.152R | 4,614, -0.122R | 76, +0.053R |
| H1 2011-19 | 807, -0.122R | 3, -0.646R | 2,384, -0.108R | 48, -0.153R |
| H4 2011-19 | 180, -0.064R | 2 trades | 502, -0.096R | 8, -0.286R |
| M1 2020-22 | 10,368, -0.413R | 70, -0.364R | 34,382, -0.417R | 561, -0.349R |
| M5 2020-22 | 2,873, -0.242R | 24, -0.226R | 9,409, -0.218R | 181, -0.191R |
| M15 2020-22 | 1,051, -0.123R | 11, +0.369R | 3,308, -0.140R | 57, -0.278R |
| M30 2020-22 | 535, -0.170R | 3, -0.847R | 1,669, -0.127R | 31, -0.143R |
| H1 2020-22 | 266, +0.041R | 4, +1.226R | 826, +0.011R | 21, +0.639R |
| H4 2020-22 | 46, -0.239R | 0 trades | 170, -0.092R | 2 trades |
| M1 2023-25 | 8,904, -0.421R | 42, -0.382R | 33,937, -0.436R | 579, -0.479R |
| M5 2023-25 | 2,627, -0.292R | 15, -0.704R | 9,056, -0.263R | 165, -0.260R |
| M15 2023-25 | 1,035, -0.139R | 5, -0.123R | 3,273, -0.152R | 48, -0.066R |
| M30 2023-25 | 500, -0.163R | 1 trades | 1,654, -0.107R | 25, -0.302R |
| H1 2023-25 | 266, -0.199R | 2 trades | 816, -0.112R | 15, +0.290R |
| H4 2023-25 | 44, -0.034R | 0 trades | 153, -0.080R | 3, -0.103R |

## 2b. Main settings at 10R (entry 50%, stop at the range end, breakeven at 75% on, lookback on): trades, R per trade

| Timeframe | strict engulf, no layering | strict engulf + layering | loose engulf, no layering | loose engulf + layering |
|---|---|---|---|---|
| M1 2011-19 | 31,381, -0.416R | 218, -0.477R | 81,358, -0.449R | 1,499, -0.514R |
| M5 2011-19 | 9,609, -0.244R | 82, -0.446R | 25,059, -0.243R | 490, -0.119R |
| M15 2011-19 | 3,679, -0.144R | 29, +0.038R | 9,855, -0.157R | 154, -0.072R |
| M30 2011-19 | 1,914, -0.110R | 9, -0.258R | 5,277, -0.136R | 88, +0.133R |
| H1 2011-19 | 926, -0.121R | 4, -0.743R | 2,658, -0.103R | 53, -0.051R |
| H4 2011-19 | 186, -0.050R | 2 trades | 520, -0.115R | 8, -0.286R |
| M1 2020-22 | 13,872, -0.419R | 100, -0.193R | 40,362, -0.404R | 784, -0.245R |
| M5 2020-22 | 3,766, -0.271R | 28, +0.191R | 11,011, -0.212R | 234, -0.084R |
| M15 2020-22 | 1,292, -0.056R | 11, +0.003R | 3,865, -0.080R | 71, -0.236R |
| M30 2020-22 | 638, -0.132R | 3, -0.847R | 1,957, -0.089R | 34, -0.040R |
| H1 2020-22 | 324, -0.034R | 4, +2.422R | 951, -0.063R | 22, +0.452R |
| H4 2020-22 | 48, -0.256R | 0 trades | 176, -0.123R | 2 trades |
| M1 2023-25 | 12,090, -0.408R | 64, -0.257R | 40,296, -0.429R | 826, -0.555R |
| M5 2023-25 | 3,449, -0.260R | 24, -0.392R | 10,773, -0.241R | 235, -0.202R |
| M15 2023-25 | 1,244, -0.148R | 5, -0.123R | 3,810, -0.189R | 56, +0.255R |
| M30 2023-25 | 594, -0.069R | 1 trades | 1,912, -0.071R | 28, -0.331R |
| H1 2023-25 | 303, -0.261R | 2 trades | 931, -0.116R | 16, -0.159R |
| H4 2023-25 | 47, -0.014R | 0 trades | 161, -0.036R | 4, -0.354R |

## 3. Before costs (spread, commission and slippage set to 0), main settings, 2011-19 / 2020-22 (2023-25 was not run before costs)

| Timeframe | Target | strict engulf, no layering | strict engulf + layering | loose engulf, no layering | loose engulf + layering |
|---|---|---|---|---|---|
| M1 | 2R | 26,241, -0.092R / 11,549, -0.092R | 173, +0.030R / 73, -0.019R | 79,957, -0.109R / 39,555, -0.073R | 1,256, -0.111R / 626, -0.018R |
| M1 | 3R | 30,580, -0.066R / 13,557, -0.065R | 203, +0.105R / 82, +0.092R | 91,524, -0.084R / 45,133, -0.052R | 1,459, -0.063R / 749, +0.050R |
| M1 | 5R | 33,628, -0.060R / 14,926, -0.051R | 220, +0.077R / 98, +0.027R | 97,586, -0.071R / 47,554, -0.035R | 1,642, -0.076R / 824, +0.058R |
| M1 | 10R | 34,659, -0.044R / 15,397, -0.048R | 239, +0.035R / 105, +0.292R | 95,539, -0.047R / 45,536, -0.016R | 1,761, -0.095R / 869, +0.107R |
| M5 | 2R | 8,035, -0.037R / 2,986, -0.048R | 60, -0.041R / 25, -0.212R | 23,082, -0.032R / 9,828, -0.022R | 426, +0.089R / 191, -0.021R |
| M5 | 3R | 9,146, -0.032R / 3,499, -0.003R | 69, -0.065R / 28, -0.011R | 25,716, -0.025R / 11,021, -0.006R | 473, +0.146R / 222, +0.032R |
| M5 | 5R | 9,864, -0.018R / 3,795, -0.029R | 74, -0.161R / 29, -0.100R | 27,033, -0.013R / 11,499, +0.005R | 513, +0.115R / 240, +0.081R |
| M5 | 10R | 10,072, -0.022R / 3,901, -0.068R | 83, -0.275R / 29, +0.281R | 26,863, +0.015R / 11,407, -0.009R | 539, +0.167R / 245, +0.069R |
| M15 | 2R | 3,158, +0.005R / 1,087, +0.039R | 24, -0.055R / 11, +0.456R | 8,871, +0.016R / 3,387, +0.011R | 133, +0.058R / 59, -0.118R |
| M15 | 3R | 3,547, +0.016R / 1,212, +0.060R | 25, +0.197R / 11, +0.547R | 9,821, +0.018R / 3,740, +0.028R | 143, +0.005R / 68, -0.034R |
| M15 | 5R | 3,730, +0.025R / 1,290, +0.042R | 28, +0.184R / 11, +0.663R | 10,212, +0.024R / 3,900, +0.052R | 154, +0.018R / 72, -0.061R |
| M15 | 10R | 3,809, +0.033R / 1,321, +0.108R | 29, +0.123R / 11, +0.114R | 10,296, +0.032R / 3,934, +0.071R | 160, +0.005R / 73, -0.125R |
| M30 | 2R | 1,687, +0.003R / 539, -0.054R | 8, -0.120R / 3, -0.805R | 4,729, +0.011R / 1,687, -0.012R | 80, +0.188R / 30, -0.067R |
| M30 | 3R | 1,836, -0.019R / 610, -0.035R | 8, -0.084R / 3, -0.805R | 5,133, -0.004R / 1,886, +0.029R | 83, +0.214R / 33, -0.087R |
| M30 | 5R | 1,937, -0.020R / 641, -0.002R | 8, -0.084R / 3, -0.805R | 5,356, -0.003R / 1,964, +0.051R | 87, +0.358R / 33, -0.122R |
| M30 | 10R | 1,950, -0.001R / 646, -0.003R | 9, -0.186R / 3, -0.805R | 5,396, -0.000R / 1,985, +0.031R | 89, +0.278R / 34, +0.076R |
| H1 | 2R | 819, -0.029R / 265, +0.113R | 3, -0.592R / 4, +1.250R | 2,440, +0.010R / 834, +0.090R | 50, -0.037R / 21, +0.668R |
| H1 | 3R | 899, -0.024R / 303, +0.042R | 3, -0.592R / 4, +0.705R | 2,625, +0.009R / 913, +0.063R | 52, -0.017R / 22, +0.610R |
| H1 | 5R | 937, -0.018R / 324, +0.017R | 4, -0.694R / 4, +1.205R | 2,711, +0.006R / 954, +0.009R | 54, -0.034R / 22, +0.514R |
| H1 | 10R | 940, -0.006R / 325, +0.042R | 4, -0.694R / 4, +2.455R | 2,722, +0.021R / 959, +0.022R | 55, +0.056R / 22, +0.487R |
| H4 | 2R | 179, -0.024R / 46, -0.210R | 2 trades / 0 trades | 505, -0.038R / 173, -0.045R | 8, -0.229R / 2 trades |
| H4 | 3R | 184, -0.045R / 47, -0.207R | 2 trades / 0 trades | 518, -0.071R / 176, -0.070R | 8, -0.229R / 2 trades |
| H4 | 5R | 185, -0.035R / 48, -0.222R | 2 trades / 0 trades | 523, -0.070R / 178, -0.071R | 8, -0.229R / 2 trades |
| H4 | 10R | 185, -0.008R / 48, -0.222R | 2 trades / 0 trades | 523, -0.056R / 179, -0.076R | 8, -0.229R / 2 trades |

## 4. The 4 PRIMARY settings (chosen on 2011-22 before the look) in each period

| Combination | Setting | Period | Trades | R per trade | t | Profit factor | Target hit | Markets positive |
|---|---|---|---|---|---|---|---|---|
| strict engulf, no layering | M15: engulf=body, layer=none, target=10, be=1, buffer=0.2, lookback=1 | 2011-19 | 3,688 | -0.085R | -2.69 | 0.879 | 1.2% | 3 of 12 |
| strict engulf, no layering | M15: engulf=body, layer=none, target=10, be=1, buffer=0.2, lookback=1 | 2020-22 | 1,292 | -0.017R | -0.3 | 0.975 | 1.8% | 6 of 12 |
| strict engulf, no layering | M15: engulf=body, layer=none, target=10, be=1, buffer=0.2, lookback=1 | 2023-25 | 1,236 | -0.129R | -2.43 | 0.821 | 0.7% | 1 of 12 |
| strict engulf + layering | M1: engulf=body, layer=on, target=10, be=1, buffer=0.2, lookback=1 | 2011-19 | 232 | -0.241R | -1.27 | 0.767 | 6.9% | 2 of 12 |
| strict engulf + layering | M1: engulf=body, layer=on, target=10, be=1, buffer=0.2, lookback=1 | 2020-22 | 102 | +0.016R | 0.05 | 1.016 | 7.8% | 4 of 12 |
| strict engulf + layering | M1: engulf=body, layer=on, target=10, be=1, buffer=0.2, lookback=1 | 2023-25 | 74 | -0.384R | -1.18 | 0.647 | 6.8% | 4 of 12 |
| loose engulf, no layering | H1: engulf=loose, layer=none, target=10, be=0, buffer=0.0, lookback=0 | 2011-19 | 5,060 | -0.098R | -3.96 | 0.852 | 0.8% | 3 of 12 |
| loose engulf, no layering | H1: engulf=loose, layer=none, target=10, be=0, buffer=0.0, lookback=0 | 2020-22 | 1,831 | -0.015R | -0.35 | 0.976 | 0.9% | 6 of 12 |
| loose engulf, no layering | H1: engulf=loose, layer=none, target=10, be=0, buffer=0.0, lookback=0 | 2023-25 | 1,836 | -0.133R | -3.29 | 0.804 | 0.7% | 1 of 12 |
| loose engulf + layering | M5: engulf=loose, layer=on, target=5, be=0, buffer=0.2, lookback=1 | 2011-19 | 501 | -0.034R | -0.37 | 0.958 | 11.4% | 5 of 12 |
| loose engulf + layering | M5: engulf=loose, layer=on, target=5, be=0, buffer=0.2, lookback=1 | 2020-22 | 233 | +0.213R | 1.46 | 1.286 | 15.0% | 7 of 12 |
| loose engulf + layering | M5: engulf=loose, layer=on, target=5, be=0, buffer=0.2, lookback=1 | 2023-25 | 229 | -0.067R | -0.5 | 0.917 | 10.5% | 4 of 12 |

### Per market, 2023-25

| Market | strict engulf, no layering | strict engulf + layering | loose engulf, no layering | loose engulf + layering |
|---|---|---|---|---|
| XAGUSD | 74, -0.074R | 4, -1.456R | 151, -0.209R | 15, -0.214R |
| XAUUSD | 142, -0.051R | 14, +0.434R | 156, -0.203R | 27, +0.239R |
| EURUSD | 160, -0.217R | 10, +0.302R | 156, -0.050R | 22, +0.265R |
| GBPUSD | 138, -0.169R | 10, -1.176R | 167, -0.110R | 14, +0.052R |
| US500 | 68, -0.109R | 3, +2.555R | 176, -0.024R | 17, -0.359R |
| USDJPY | 145, -0.128R | 4, -1.109R | 149, +0.089R | 19, -0.162R |
| WTI | 84, -0.230R | 5, -1.095R | 160, -0.159R | 16, -0.792R |
| EURGBP | 127, -0.023R | 8, -1.261R | 141, -0.205R | 16, -0.026R |
| JP225 | 52, -0.180R | 4, -1.135R | 122, -0.218R | 20, -0.151R |
| UK100 | 88, +0.092R | 7, -1.257R | 142, -0.154R | 18, -0.169R |
| GER40 | 70, -0.116R | 2 trades | 133, -0.002R | 26, -0.320R |
| NAS100 | 88, -0.358R | 3, +2.616R | 183, -0.332R | 19, +0.602R |

## 5. All 768 settings in 2023-25 (description only: picking one from here would be hindsight)

| Combination | Settings with >= 100 trades | Positive | Median R per trade | Best (its 2011-22 result) |
|---|---|---|---|---|
| strict engulf, no layering | 160 | 0 (0%) | -0.192R | M30: engulf=body, layer=none, target=10, be=1, buffer=0.2, lookback=1: 589 trades, -0.026R, t -0.36 (2,553 trades, -0.089R in 2011-22) |
| strict engulf + layering | 16 | 0 (0%) | -0.200R | M1: engulf=body, layer=on, target=10, be=1, buffer=0.2, lookback=0: 268 trades, -0.089R, t -0.47 (1,235 trades, -0.290R in 2011-22) |
| loose engulf, no layering | 192 | 16 (8%) | -0.125R | H4: engulf=loose, layer=none, target=2, be=1, buffer=0.2, lookback=0: 331 trades, +0.052R, t 1.12 (1,368 trades, -0.099R in 2011-22) |
| loose engulf + layering | 80 | 0 (0%) | -0.245R | M15: engulf=loose, layer=on, target=2, be=1, buffer=0.0, lookback=0: 148 trades, -0.046R, t -0.44 (625 trades, -0.124R in 2011-22) |
| all four | 448 | 16 (4%) | -0.178R | H4: engulf=loose, layer=none, target=2, be=1, buffer=0.2, lookback=0: 331 trades, +0.052R, t 1.12 (1,368 trades, -0.099R in 2011-22) |

## 6. 2023-25 by timeframe (all settings with >= 100 trades)

| Timeframe | Settings | Positive | Median R per trade |
|---|---|---|---|
| M1 | 112 | 0 | -0.383R |
| M5 | 96 | 0 | -0.222R |
| M15 | 80 | 0 | -0.129R |
| M30 | 64 | 0 | -0.059R |
| H1 | 64 | 0 | -0.152R |
| H4 | 32 | 16 | -0.004R |

