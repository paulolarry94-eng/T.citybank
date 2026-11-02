# Replay check: the scanner on the owner's example days (Oct 2026, anchor 15:30 Nigerian time)

Owner's calls from the owner's charts; scanner on our data (TradingView prices differ slightly). Times are WAT.

| Market | Date | Owner | Anchor candle (open / close vs EMA before it) | Scanner, entry A | Scanner, entry B6 |
|---|---|---|---|---|---|
| XAUUSD | 2026-10-20 | no trade: the 15:30 candle does not cross the EMA | o 4153.32 / c 4142.94 vs EMA 4128.53: no cross | no setup | no setup |
| XAUUSD | 2026-10-21 | invalid: the 15:30 body stays above the EMA | o 4133.33 / c 4130.38 vs EMA 4130.14: no cross | no setup | no setup |
| XAUUSD | 2026-10-29 | SELL; reference M5 16:40; entry 4022.67 (low), stop 4025.98 (high), 3R hit ~17:30 | o 4029.92 / c 4026.56 vs EMA 4026.58: SELL | SELL ref 16:40; in 16:45 @ 4022.71, stop 4026.16; out 17:12 target +3.00R | SELL ref 16:40; in 16:51 @ 4022.71, stop 4026.16; out 17:12 target +3.00R |
| GBPUSD | 2026-10-28 (news day) | BUY; 16:00 no setup (closed above the range); reference 16:55; entry 1.3302, stop 1.3298, 4R 1.3318 hit | o 1.32893 / c 1.32999 vs EMA 1.32894: BUY | BUY ref 16:55; in 17:03 @ 1.33028, stop 1.32980; out 19:21 stop -1.00R | BUY ref 16:55; no fill |
| GBPUSD | 2026-10-27 | SELL; displaced reference 16:05, entry at its 50% 1.3321, stop 1.3325, 4R 1.3305 | o 1.33296 / c 1.33237 vs EMA 1.33247: SELL | SELL ref 16:05 (displaced); in 16:32 @ 1.33210, stop 1.33253; out 21:00 time +1.00R | SELL ref 16:05 (displaced); in 16:32 @ 1.33210, stop 1.33253; out 21:00 time +1.00R |
| GBPUSD | 2026-10-23 | reference formed but price never broke it: no entry | o 1.33739 / c 1.33852 vs EMA 1.33760: BUY | BUY ref 16:10; no fill | BUY ref 16:10; no fill |
| GBPUSD | 2026-10-15 | SELL; entry about 17:20 at 1.3252, stop 1.3258, target 1.3243 (a loss) | o 1.32598 / c 1.32528 vs EMA 1.32543: SELL | SELL ref 16:45; in 17:03 @ 1.32516, stop 1.32564; out 17:26 stop -1.00R | SELL ref 16:45; in 17:16 @ 1.32516, stop 1.32564; out 17:26 stop -1.00R |
| EURGBP | 2026-10-23 | SELL bias; M5 broke above the range: no trade | o 0.83736 / c 0.83697 vs EMA 0.83719: SELL | no setup | no setup |
| EURGBP | 2026-10-27 | BUY; reference 16:00 (high 0.83674, low 0.83647); entered on the pullback ~16:35 | o 0.83657 / c 0.83673 vs EMA 0.83670: BUY | BUY ref 18:45; no fill | BUY ref 18:45; no fill |
| USDJPY | 2026-10-27 | owner's test; my answer: invalid anchor (opened on/below the EMA), no trade | o 157.77 / c 157.72 vs EMA 157.78: no cross | no setup | no setup |
