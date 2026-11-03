# Cycle league — ema4_flip_v4

Every configuration, all markets in time order, fills before 2023 (the 2023-25 holdout stays closed). A cycle = 10 trades, a lifecycle = 360 trades. 'At 3.6%' = risk set so 95% of bootstrapped lifecycles stay inside a 3.6% drawdown. Edge quality needed for +2% per cycle inside 3.6%: 0.42.

| # | Configuration | Trades/yr | Win rate | Edge quality s (2011-19) | Cycle at 3.6% | at 5% | Positive cycles | Worst cycle | Months per lifecycle | Lifecycles | Lifecycle returns | s 2020-22 | Cycle at 3.6% 2020-22 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c34, tf M15 | 4.1 | 58% | +0.269 | +1.757% | +2.440% | 100% | +0.89% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 2 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c4, tf M15 | 3.9 | 57% | +0.253 | +2.419% | +3.359% | 67% | -0.32% | 1098.5 | 0 | - | +0.000 | +0.000% |
| 3 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop all4, tf M15 | 4.1 | 58% | +0.239 | +1.179% | +1.637% | 67% | -0.01% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 4 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c4, tf M15 | 4.2 | 56% | +0.227 | +1.031% | +1.431% | 67% | -0.01% | 1029.8 | 0 | - | +0.123 | +0.140% |
| 5 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c34, tf M15 | 4.2 | 56% | +0.226 | +1.123% | +1.559% | 100% | +0.26% | 1029.8 | 0 | - | +0.109 | +0.125% |
| 6 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf H4 | 3.9 | 53% | +0.216 | +1.630% | +2.264% | 100% | +0.11% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 7 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.194 | +0.995% | +1.382% | 100% | +0.17% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 8 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.191 | +1.124% | +1.561% | 67% | -0.13% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 9 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c4, tf M15 | 4.1 | 39% | +0.188 | +2.550% | +3.542% | 100% | +0.19% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 10 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop all4, tf M15 | 4.5 | 56% | +0.184 | +0.581% | +0.806% | 67% | -0.11% | 969.2 | 0 | - | +0.152 | +0.234% |
| 11 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf M30 | 11.4 | 58% | +0.180 | +0.350% | +0.486% | 60% | -0.41% | 377.3 | 0 | - | +0.007 | -0.051% |
| 12 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf H1 | 3.2 | 64% | +0.179 | +1.227% | +1.704% | 100% | +1.42% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 13 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf H1 | 3.3 | 50% | +0.175 | +0.914% | +1.270% | 100% | +0.55% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 14 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.167 | +0.273% | +0.379% | 33% | -0.29% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 15 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf H1 | 3.3 | 50% | +0.164 | +0.924% | +1.283% | 100% | +0.57% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 16 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.164 | +0.564% | +0.783% | 67% | -0.08% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 17 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c34, tf M15 | 4.2 | 38% | +0.163 | +2.024% | +2.811% | 100% | +0.10% | 1029.8 | 0 | - | +0.000 | +0.000% |
| 18 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf H1 | 3.2 | 54% | +0.162 | +1.040% | +1.444% | 100% | +0.90% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 19 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.152 | +0.513% | +0.712% | 67% | -0.08% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 20 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.151 | +0.148% | +0.205% | 33% | -0.31% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 21 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop all4, tf M15 | 4.2 | 38% | +0.149 | +1.769% | +2.457% | 100% | +0.16% | 1029.8 | 0 | - | +0.000 | +0.000% |
| 22 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf M30 | 11.2 | 57% | +0.149 | +0.321% | +0.446% | 78% | -0.91% | 385.0 | 0 | - | -0.136 | -0.078% |
| 23 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf M30 | 11.3 | 57% | +0.146 | +0.314% | +0.435% | 78% | -0.62% | 381.1 | 0 | - | -0.101 | -0.083% |
| 24 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf H1 | 3.3 | 46% | +0.137 | +1.023% | +1.421% | 100% | +0.56% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 25 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf H1 | 5.8 | 45% | +0.137 | +0.285% | +0.395% | 50% | -0.44% | 739.4 | 0 | - | +0.038 | +0.518% |
| 26 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf H1 | 5.8 | 45% | +0.137 | +0.263% | +0.366% | 50% | -0.46% | 739.4 | 0 | - | +0.038 | +0.518% |
| 27 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf H1 | 6.0 | 44% | +0.134 | +0.534% | +0.741% | 40% | -0.29% | 724.6 | 0 | - | +0.163 | +2.988% |
| 28 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf H1 | 3.3 | 46% | +0.134 | +0.519% | +0.721% | 50% | -0.47% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 29 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf H1 | 5.8 | 45% | +0.131 | +0.245% | +0.340% | 50% | -0.42% | 739.4 | 0 | - | +0.115 | +1.555% |
| 30 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf H1 | 5.8 | 45% | +0.131 | +0.226% | +0.315% | 50% | -0.43% | 739.4 | 0 | - | +0.115 | +1.555% |
| 31 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf H1 | 3.3 | 46% | +0.128 | +0.846% | +1.175% | 100% | +0.59% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 32 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf H1 | 3.1 | 41% | +0.128 | +0.282% | +0.391% | 100% | +0.07% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 33 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c4, tf M15 | 4.3 | 36% | +0.128 | +1.521% | +2.112% | 100% | +0.01% | 998.6 | 0 | - | +0.141 | +0.130% |
| 34 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.128 | +0.346% | +0.481% | 33% | -0.14% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 35 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.128 | +0.346% | +0.481% | 33% | -0.14% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 36 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.128 | +0.346% | +0.481% | 33% | -0.14% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 37 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf M30 | 11.2 | 44% | +0.127 | +0.180% | +0.250% | 56% | -0.69% | 385.0 | 0 | - | -0.062 | -0.082% |
| 38 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf H4 | 3.9 | 53% | +0.125 | +0.358% | +0.497% | 33% | -0.09% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 39 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf H4 | 3.9 | 53% | +0.125 | +0.358% | +0.497% | 33% | -0.09% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 40 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf H4 | 3.9 | 53% | +0.125 | +0.358% | +0.497% | 33% | -0.09% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 41 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c34, tf M15 | 4.3 | 36% | +0.123 | +1.355% | +1.882% | 67% | -0.00% | 998.6 | 0 | - | +0.125 | +0.110% |
| 42 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf H1 | 3.3 | 50% | +0.122 | +0.680% | +0.945% | 100% | +0.24% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 43 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf H1 | 5.8 | 45% | +0.121 | +0.242% | +0.336% | 75% | -0.47% | 739.4 | 0 | - | +0.038 | +0.518% |
| 44 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf M30 | 11.4 | 45% | +0.121 | +0.182% | +0.252% | 60% | -0.70% | 377.3 | 0 | - | +0.022 | -0.049% |
| 45 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.121 | +0.397% | +0.552% | 33% | -0.07% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 46 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.121 | +0.397% | +0.552% | 33% | -0.07% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 47 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.121 | +0.397% | +0.552% | 33% | -0.07% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 48 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf M30 | 11.2 | 44% | +0.120 | +0.157% | +0.218% | 67% | -0.73% | 385.0 | 0 | - | -0.156 | -0.086% |
| 49 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf H4 | 3.9 | 50% | +0.120 | +0.091% | +0.127% | 33% | -0.34% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 50 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf M30 | 11.3 | 46% | +0.118 | +0.155% | +0.215% | 56% | -0.62% | 381.1 | 0 | - | -0.055 | -0.077% |
| 51 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf H1 | 6.0 | 44% | +0.118 | +0.387% | +0.538% | 40% | -0.29% | 724.6 | 0 | - | +0.212 | +4.200% |
| 52 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf M30 | 11.4 | 46% | +0.118 | +0.140% | +0.195% | 50% | -0.57% | 377.3 | 0 | - | -0.076 | -0.082% |
| 53 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf H1 | 3.3 | 54% | +0.118 | +0.490% | +0.680% | 100% | +0.09% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 54 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf H4 | 3.9 | 50% | +0.117 | +0.084% | +0.116% | 33% | -0.36% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 55 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf H4 | 3.9 | 50% | +0.116 | +0.071% | +0.099% | 33% | -0.34% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 56 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf H1 | 3.3 | 46% | +0.116 | +0.334% | +0.464% | 50% | -0.46% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 57 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop all4, tf H1 | 5.8 | 41% | +0.113 | +0.168% | +0.234% | 50% | -0.42% | 739.4 | 0 | - | -0.035 | +0.164% |
| 58 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf H1 | 5.8 | 45% | +0.112 | +0.191% | +0.266% | 75% | -0.43% | 739.4 | 0 | - | +0.117 | +1.576% |
| 59 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf H4 | 3.9 | 50% | +0.110 | +0.077% | +0.106% | 33% | -0.33% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 60 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf H1 | 3.3 | 54% | +0.109 | +0.434% | +0.603% | 100% | +0.09% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 61 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf H1 | 3.3 | 50% | +0.108 | +0.669% | +0.929% | 100% | +0.12% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 62 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf H1 | 6.0 | 46% | +0.108 | +0.204% | +0.283% | 40% | -0.16% | 724.6 | 0 | - | +0.116 | +1.668% |
| 63 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf M30 | 11.3 | 44% | +0.108 | +0.125% | +0.173% | 56% | -0.70% | 381.1 | 0 | - | -0.133 | -0.086% |
| 64 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.107 | +0.183% | +0.254% | 33% | -0.28% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 65 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf H4 | 3.9 | 53% | +0.107 | +0.183% | +0.254% | 33% | -0.28% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 66 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf M30 | 11.3 | 44% | +0.107 | +0.131% | +0.181% | 44% | -0.55% | 381.1 | 0 | - | +0.027 | -0.030% |
| 67 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf H1 | 6.0 | 46% | +0.107 | +0.187% | +0.260% | 40% | -0.17% | 724.6 | 0 | - | +0.116 | +1.668% |
| 68 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf H1 | 6.0 | 44% | +0.106 | +0.335% | +0.465% | 40% | -0.30% | 724.6 | 0 | - | +0.197 | +4.063% |
| 69 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf M30 | 11.4 | 45% | +0.106 | +0.134% | +0.186% | 60% | -0.64% | 377.3 | 0 | - | -0.002 | -0.060% |
| 70 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf M30 | 11.4 | 46% | +0.105 | +0.114% | +0.158% | 50% | -0.55% | 377.3 | 0 | - | -0.085 | -0.082% |
| 71 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf M30 | 11.3 | 43% | +0.105 | +0.115% | +0.160% | 44% | -0.61% | 381.1 | 0 | - | +0.010 | -0.052% |
| 72 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf M30 | 11.4 | 45% | +0.104 | +0.147% | +0.204% | 60% | -0.61% | 377.3 | 0 | - | +0.006 | -0.050% |
| 73 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf H1 | 3.3 | 50% | +0.103 | +0.479% | +0.665% | 100% | +0.26% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 74 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf M30 | 11.3 | 55% | +0.102 | +0.152% | +0.211% | 67% | -0.64% | 381.1 | 0 | - | -0.062 | -0.067% |
| 75 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c34, tf H1 | 5.8 | 41% | +0.102 | +0.138% | +0.192% | 50% | -0.40% | 739.4 | 0 | - | +0.046 | +0.820% |
| 76 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf M30 | 11.4 | 46% | +0.100 | +0.112% | +0.156% | 50% | -0.52% | 377.3 | 0 | - | -0.068 | -0.079% |
| 77 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf H4 | 3.9 | 47% | +0.099 | -0.013% | -0.018% | 33% | -0.19% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 78 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf H1 | 3.1 | 44% | +0.099 | +0.263% | +0.365% | 50% | -0.17% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 79 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.098 | +0.091% | +0.126% | 33% | -0.30% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 80 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf H4 | 3.9 | 53% | +0.098 | +0.091% | +0.126% | 33% | -0.30% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 81 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf H1 | 3.3 | 46% | +0.095 | +0.285% | +0.395% | 50% | -0.47% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 82 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf M30 | 11.2 | 41% | +0.095 | +0.176% | +0.244% | 67% | -0.25% | 385.0 | 0 | - | -0.081 | -0.080% |
| 83 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf H1 | 3.3 | 46% | +0.095 | +0.267% | +0.370% | 50% | -0.44% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 84 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c4, tf H1 | 6.0 | 42% | +0.093 | +0.121% | +0.168% | 60% | -0.38% | 724.6 | 0 | - | +0.034 | +0.735% |
| 85 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf H4 | 3.9 | 47% | +0.092 | -0.012% | -0.017% | 33% | -0.19% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 86 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c4, tf M15 | 3.9 | 30% | +0.092 | +1.068% | +1.484% | 67% | -0.57% | 1098.5 | 0 | - | +0.000 | +0.000% |
| 87 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf H4 | 3.9 | 50% | +0.089 | +0.027% | +0.038% | 33% | -0.34% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 88 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf H4 | 8.7 | 45% | +0.089 | +0.081% | +0.113% | 71% | -0.28% | 497.1 | 0 | - | -0.020 | -0.063% |
| 89 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf H1 | 3.2 | 46% | +0.088 | +0.184% | +0.255% | 100% | +0.31% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 90 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf H1 | 3.3 | 50% | +0.087 | +0.456% | +0.634% | 100% | +0.26% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 91 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop all4, tf M15 | 4.6 | 34% | +0.087 | +0.750% | +1.042% | 33% | -0.36% | 941.5 | 0 | - | +0.158 | +0.185% |
| 92 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf H1 | 3.3 | 54% | +0.085 | +0.417% | +0.579% | 100% | +0.10% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 93 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf H4 | 3.9 | 47% | +0.085 | -0.015% | -0.020% | 33% | -0.19% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 94 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c4, tf M15 | 3.9 | 27% | +0.084 | +1.228% | +1.706% | 33% | -0.16% | 1098.5 | 0 | - | +0.000 | +0.000% |
| 95 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf H1 | 13.0 | 47% | +0.084 | +0.135% | +0.187% | 73% | -0.82% | 332.3 | 0 | - | -0.141 | -0.046% |
| 96 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf H1 | 6.0 | 46% | +0.084 | +0.149% | +0.207% | 40% | -0.20% | 724.6 | 0 | - | +0.111 | +1.574% |
| 97 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf H1 | 3.2 | 57% | +0.079 | +0.161% | +0.224% | 100% | +0.37% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 98 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf H4 | 3.9 | 47% | +0.079 | -0.020% | -0.028% | 33% | -0.19% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 99 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf M30 | 11.3 | 40% | +0.078 | +0.128% | +0.178% | 56% | -0.56% | 381.1 | 0 | - | -0.024 | -0.072% |
| 100 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf H4 | 8.7 | 43% | +0.076 | +0.086% | +0.119% | 57% | -0.30% | 497.1 | 0 | - | -0.067 | -0.070% |
| 101 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf H4 | 3.9 | 47% | +0.075 | -0.019% | -0.026% | 33% | -0.18% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 102 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf M30 | 11.3 | 42% | +0.075 | +0.118% | +0.164% | 56% | -0.43% | 381.1 | 0 | - | +0.101 | +0.036% |
| 103 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf M30 | 5.4 | 38% | +0.073 | +0.066% | +0.092% | 50% | -0.47% | 799.4 | 0 | - | +0.000 | +0.000% |
| 104 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf H1 | 13.0 | 47% | +0.073 | +0.106% | +0.147% | 73% | -0.75% | 332.3 | 0 | - | -0.109 | -0.039% |
| 105 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf H4 | 8.7 | 45% | +0.073 | +0.046% | +0.064% | 57% | -0.38% | 497.1 | 0 | - | +0.065 | +0.128% |
| 106 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf H1 | 3.1 | 56% | +0.072 | +0.327% | +0.454% | 100% | +0.57% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 107 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf H1 | 3.0 | 38% | +0.072 | +0.013% | +0.018% | 50% | -0.23% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 108 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf H1 | 3.3 | 58% | +0.071 | +0.843% | +1.171% | 100% | +0.51% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 109 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf H1 | 3.0 | 42% | +0.071 | +0.062% | +0.086% | 50% | -0.41% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 110 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf H1 | 5.8 | 47% | +0.070 | +0.135% | +0.187% | 75% | -0.30% | 739.4 | 0 | - | +0.126 | +1.156% |
| 111 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf M30 | 11.2 | 36% | +0.068 | +0.126% | +0.174% | 78% | -0.55% | 385.0 | 0 | - | -0.113 | -0.086% |
| 112 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf M30 | 11.4 | 53% | +0.067 | +0.051% | +0.071% | 50% | -0.30% | 377.3 | 0 | - | -0.028 | -0.057% |
| 113 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf H4 | 3.9 | 47% | +0.066 | -0.022% | -0.031% | 33% | -0.18% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 114 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf H1 | 3.0 | 42% | +0.065 | +0.530% | +0.736% | 50% | -0.62% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 115 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf H4 | 8.7 | 47% | +0.063 | +0.080% | +0.111% | 57% | -0.53% | 497.1 | 0 | - | +0.009 | -0.031% |
| 116 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.063 | +0.034% | +0.047% | 43% | -0.82% | 503.8 | 0 | - | +0.061 | +0.155% |
| 117 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf H1 | 3.0 | 54% | +0.062 | +1.000% | +1.389% | 50% | +0.00% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 118 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf H1 | 5.8 | 47% | +0.059 | +0.092% | +0.127% | 75% | -0.27% | 739.4 | 0 | - | +0.161 | +1.322% |
| 119 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf M30 | 5.6 | 41% | +0.056 | +0.097% | +0.134% | 50% | -0.66% | 766.8 | 0 | - | +0.000 | +0.000% |
| 120 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf H4 | 8.6 | 47% | +0.056 | +0.064% | +0.088% | 43% | -0.52% | 503.8 | 0 | - | +0.013 | -0.019% |
| 121 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf H1 | 13.0 | 49% | +0.054 | +0.095% | +0.132% | 64% | -0.59% | 332.3 | 0 | - | -0.124 | -0.041% |
| 122 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf H1 | 3.0 | 42% | +0.053 | +0.465% | +0.646% | 50% | -0.57% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 123 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf H1 | 3.3 | 42% | +0.053 | +0.310% | +0.430% | 50% | -0.38% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 124 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf H4 | 8.6 | 45% | +0.053 | +0.051% | +0.071% | 57% | -0.97% | 503.8 | 0 | - | +0.051 | +0.052% |
| 125 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf H1 | 6.0 | 48% | +0.053 | +0.096% | +0.133% | 40% | -0.29% | 724.6 | 0 | - | +0.148 | +1.280% |
| 126 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf M30 | 11.2 | 34% | +0.051 | +0.110% | +0.153% | 78% | -0.53% | 385.0 | 0 | - | -0.106 | -0.088% |
| 127 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf H4 | 3.9 | 50% | +0.050 | -0.001% | -0.001% | 33% | -0.30% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 128 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf M30 | 11.3 | 38% | +0.050 | +0.098% | +0.136% | 78% | -0.70% | 381.1 | 0 | - | -0.018 | -0.080% |
| 129 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf M30 | 11.4 | 52% | +0.049 | +0.016% | +0.022% | 40% | -0.22% | 377.3 | 0 | - | +0.009 | -0.051% |
| 130 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf H1 | 13.0 | 42% | +0.048 | +0.045% | +0.062% | 46% | -0.51% | 332.3 | 0 | - | -0.103 | -0.035% |
| 131 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf M30 | 5.6 | 41% | +0.047 | +0.074% | +0.102% | 50% | -0.62% | 766.8 | 0 | - | +0.000 | +0.000% |
| 132 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf H1 | 3.3 | 46% | +0.047 | +0.404% | +0.561% | 100% | +0.09% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 133 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf M5 | 5.8 | 36% | +0.047 | +0.256% | +0.356% | 60% | -0.59% | 742.3 | 0 | - | +0.000 | +0.000% |
| 134 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf H1 | 3.3 | 38% | +0.046 | +0.243% | +0.337% | 50% | -0.30% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 135 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf H4 | 3.9 | 50% | +0.046 | -0.017% | -0.024% | 33% | -0.29% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 136 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf M30 | 5.6 | 41% | +0.046 | +0.060% | +0.083% | 50% | -0.63% | 766.8 | 0 | - | +0.000 | +0.000% |
| 137 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf M30 | 11.3 | 34% | +0.046 | +0.097% | +0.135% | 67% | -0.73% | 381.1 | 0 | - | -0.048 | -0.083% |
| 138 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf M30 | 48.4 | 32% | +0.046 | +0.048% | +0.067% | 49% | -0.66% | 89.2 | 1 | +3.5% | -0.052 | -0.046% |
| 139 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c34, tf M15 | 4.1 | 36% | +0.044 | +0.259% | +0.360% | 33% | -0.25% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 140 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf M30 | 5.4 | 38% | +0.044 | +0.154% | +0.214% | 50% | -0.48% | 799.4 | 0 | - | +0.000 | +0.000% |
| 141 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf M5 | 5.8 | 36% | +0.044 | +0.253% | +0.352% | 60% | -0.61% | 742.3 | 0 | - | +0.000 | +0.000% |
| 142 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf H1 | 3.3 | 38% | +0.043 | +0.284% | +0.394% | 50% | -0.20% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 143 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf M30 | 5.5 | 38% | +0.042 | +0.038% | +0.052% | 50% | -0.48% | 782.7 | 0 | - | +0.000 | +0.000% |
| 144 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf H1 | 13.0 | 41% | +0.042 | +0.028% | +0.039% | 55% | -0.39% | 332.3 | 0 | - | -0.092 | -0.027% |
| 145 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf M5 | 5.8 | 30% | +0.042 | +0.328% | +0.455% | 60% | -0.97% | 742.3 | 0 | - | +0.000 | +0.000% |
| 146 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c34, tf M15 | 4.1 | 29% | +0.040 | +0.771% | +1.071% | 33% | -0.57% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 147 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf M30 | 49.1 | 36% | +0.040 | +0.043% | +0.060% | 44% | -0.50% | 88.0 | 1 | +2.9% | -0.073 | -0.048% |
| 148 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf M30 | 49.1 | 39% | +0.039 | +0.040% | +0.055% | 49% | -0.56% | 88.0 | 1 | +1.3% | -0.099 | -0.066% |
| 149 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop all4, tf M15 | 4.1 | 36% | +0.038 | +0.239% | +0.332% | 33% | -0.25% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 150 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf M30 | 49.1 | 39% | +0.038 | +0.042% | +0.058% | 51% | -0.56% | 88.0 | 1 | +2.1% | -0.048 | -0.044% |
| 151 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.037 | +0.014% | +0.019% | 57% | -0.92% | 503.8 | 0 | - | +0.060 | +0.113% |
| 152 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf H1 | 26.4 | 51% | +0.036 | +0.075% | +0.103% | 56% | -0.69% | 163.3 | 0 | - | -0.180 | -0.063% |
| 153 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf M30 | 11.3 | 35% | +0.036 | +0.061% | +0.085% | 78% | -0.69% | 381.1 | 0 | - | -0.052 | -0.083% |
| 154 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf H1 | 3.2 | 54% | +0.036 | -0.015% | -0.021% | 50% | -0.08% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 155 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf M30 | 5.6 | 41% | +0.034 | +0.033% | +0.046% | 75% | -0.65% | 766.8 | 0 | - | +0.000 | +0.000% |
| 156 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf M5 | 4.4 | 34% | +0.033 | +0.246% | +0.342% | 33% | -0.55% | 976.7 | 0 | - | +0.000 | +0.000% |
| 157 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf M30 | 5.6 | 41% | +0.032 | +0.052% | +0.072% | 50% | -0.57% | 766.8 | 0 | - | +0.000 | +0.000% |
| 158 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf H1 | 21.5 | 41% | +0.032 | +0.046% | +0.064% | 42% | -0.44% | 200.8 | 0 | - | -0.155 | -0.063% |
| 159 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf H4 | 8.7 | 47% | +0.032 | +0.003% | +0.004% | 57% | -0.32% | 497.1 | 0 | - | -0.109 | -0.070% |
| 160 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf H4 | 8.7 | 43% | +0.031 | -0.004% | -0.006% | 57% | -0.40% | 497.1 | 0 | - | -0.067 | -0.070% |
| 161 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf M30 | 49.1 | 35% | +0.031 | +0.031% | +0.043% | 49% | -0.43% | 88.0 | 1 | +1.8% | -0.060 | -0.047% |
| 162 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf M30 | 5.4 | 28% | +0.030 | +0.076% | +0.106% | 50% | -0.40% | 799.4 | 0 | - | +0.000 | +0.000% |
| 163 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c34, tf M15 | 4.1 | 26% | +0.030 | +0.731% | +1.016% | 33% | -0.23% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 164 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf M5 | 4.4 | 29% | +0.030 | +0.276% | +0.383% | 67% | -0.55% | 976.7 | 0 | - | +0.000 | +0.000% |
| 165 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf H1 | 13.0 | 43% | +0.029 | +0.038% | +0.053% | 36% | -0.48% | 332.3 | 0 | - | -0.056 | -0.012% |
| 166 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf H1 | 3.2 | 46% | +0.029 | -0.002% | -0.002% | 100% | +0.01% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 167 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf H1 | 13.0 | 44% | +0.027 | +0.032% | +0.045% | 46% | -0.57% | 332.3 | 0 | - | -0.072 | -0.029% |
| 168 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf H4 | 8.7 | 45% | +0.027 | -0.013% | -0.018% | 57% | -0.41% | 497.1 | 0 | - | +0.072 | +0.201% |
| 169 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf H4 | 8.7 | 45% | +0.027 | -0.013% | -0.018% | 57% | -0.41% | 497.1 | 0 | - | +0.098 | +0.383% |
| 170 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf H1 | 3.0 | 35% | +0.026 | -0.007% | -0.009% | 50% | -0.15% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 171 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf M30 | 49.4 | 40% | +0.025 | +0.023% | +0.033% | 50% | -0.55% | 87.4 | 1 | +0.5% | -0.124 | -0.068% |
| 172 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf H1 | 25.2 | 39% | +0.025 | +0.051% | +0.071% | 59% | -0.56% | 171.3 | 0 | - | -0.199 | -0.073% |
| 173 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf H1 | 12.7 | 34% | +0.025 | +0.019% | +0.026% | 36% | -0.48% | 341.1 | 0 | - | +0.061 | +0.110% |
| 174 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf H1 | 3.0 | 54% | +0.025 | +0.269% | +0.373% | 50% | -0.83% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 175 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf M30 | 48.4 | 33% | +0.025 | +0.023% | +0.032% | 46% | -0.54% | 89.2 | 1 | +2.1% | -0.089 | -0.056% |
| 176 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf H1 | 26.2 | 39% | +0.025 | +0.054% | +0.075% | 39% | -0.55% | 164.7 | 0 | - | -0.215 | -0.065% |
| 177 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf H1 | 21.5 | 40% | +0.025 | +0.036% | +0.050% | 47% | -0.57% | 200.8 | 0 | - | -0.122 | -0.057% |
| 178 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf M5 | 5.4 | 28% | +0.024 | +0.115% | +0.160% | 50% | -0.40% | 806.8 | 0 | - | +0.000 | +0.000% |
| 179 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf M30 | 49.0 | 40% | +0.024 | +0.022% | +0.030% | 49% | -0.53% | 88.2 | 1 | +0.2% | -0.108 | -0.065% |
| 180 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf H1 | 25.2 | 35% | +0.023 | +0.045% | +0.062% | 50% | -0.50% | 171.3 | 0 | - | -0.141 | -0.063% |
| 181 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf M5 | 5.4 | 28% | +0.023 | +0.098% | +0.136% | 50% | -0.49% | 806.8 | 0 | - | +0.000 | +0.000% |
| 182 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf M30 | 7.1 | 28% | +0.023 | -0.005% | -0.007% | 50% | -0.19% | 606.7 | 0 | - | -0.051 | -0.077% |
| 183 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf H1 | 13.0 | 52% | +0.023 | +0.044% | +0.061% | 64% | -0.51% | 332.3 | 0 | - | -0.169 | -0.057% |
| 184 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf H4 | 8.6 | 45% | +0.023 | -0.007% | -0.010% | 43% | -0.63% | 503.8 | 0 | - | +0.002 | -0.031% |
| 185 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c4, tf M30 | 14.5 | 33% | +0.023 | +0.013% | +0.018% | 54% | -0.72% | 298.8 | 0 | - | -0.174 | -0.081% |
| 186 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf M30 | 11.4 | 37% | +0.022 | +0.018% | +0.024% | 60% | -0.61% | 377.3 | 0 | - | -0.052 | -0.083% |
| 187 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf M5 | 4.4 | 29% | +0.022 | +0.218% | +0.303% | 67% | -0.54% | 976.7 | 0 | - | +0.000 | +0.000% |
| 188 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf M30 | 94.2 | 35% | +0.021 | +0.019% | +0.027% | 45% | -0.48% | 45.9 | 2 | +1.9%, +0.4% | -0.040 | -0.029% |
| 189 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf H1 | 3.3 | 35% | +0.021 | +0.214% | +0.297% | 50% | -0.47% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 190 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf H1 | 25.2 | 32% | +0.021 | +0.039% | +0.054% | 41% | -0.38% | 171.3 | 0 | - | -0.227 | -0.073% |
| 191 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf H4 | 8.6 | 45% | +0.021 | -0.012% | -0.016% | 57% | -0.80% | 503.8 | 0 | - | +0.015 | +0.080% |
| 192 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf H4 | 8.6 | 45% | +0.021 | -0.012% | -0.016% | 57% | -0.80% | 503.8 | 0 | - | +0.057 | +0.272% |
| 193 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf H4 | 8.6 | 45% | +0.021 | -0.012% | -0.016% | 57% | -0.80% | 503.8 | 0 | - | +0.055 | +0.258% |
| 194 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c4, tf M15 | 4.2 | 34% | +0.020 | +0.233% | +0.323% | 33% | -0.26% | 1029.8 | 0 | - | +0.117 | +0.082% |
| 195 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf M30 | 49.1 | 40% | +0.020 | +0.023% | +0.033% | 56% | -0.61% | 88.0 | 1 | +1.1% | -0.053 | -0.041% |
| 196 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf M30 | 5.6 | 37% | +0.019 | +0.042% | +0.059% | 50% | -0.61% | 766.8 | 0 | - | +0.000 | +0.000% |
| 197 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf H1 | 3.0 | 54% | +0.019 | +0.483% | +0.670% | 0% | -0.54% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 198 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c34, tf M15 | 15.3 | 32% | +0.019 | +0.005% | +0.006% | 33% | -0.36% | 281.5 | 0 | - | -0.137 | -0.074% |
| 199 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf H1 | 3.3 | 35% | +0.019 | +0.184% | +0.255% | 50% | -0.47% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 200 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf H1 | 27.0 | 51% | +0.018 | +0.035% | +0.049% | 62% | -0.85% | 159.9 | 0 | - | -0.169 | -0.062% |
| 201 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf M5 | 21.8 | 28% | +0.017 | +0.044% | +0.062% | 53% | -0.74% | 197.8 | 0 | - | -0.104 | -0.059% |
| 202 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf H4 | 3.9 | 50% | +0.017 | -0.012% | -0.016% | 33% | -0.27% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 203 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf M30 | 49.0 | 40% | +0.017 | +0.014% | +0.020% | 44% | -0.55% | 88.2 | 1 | -0.1% | -0.101 | -0.064% |
| 204 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf M30 | 49.4 | 36% | +0.016 | +0.010% | +0.014% | 48% | -0.53% | 87.4 | 1 | +1.4% | -0.063 | -0.044% |
| 205 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf H1 | 25.2 | 32% | +0.016 | +0.032% | +0.045% | 50% | -0.63% | 171.3 | 0 | - | -0.129 | -0.058% |
| 206 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c34, tf M15 | 15.3 | 32% | +0.015 | -0.002% | -0.003% | 42% | -0.37% | 281.5 | 0 | - | -0.046 | -0.052% |
| 207 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf M30 | 48.4 | 36% | +0.015 | +0.012% | +0.016% | 44% | -0.54% | 89.2 | 1 | +0.5% | -0.090 | -0.063% |
| 208 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf H4 | 8.7 | 42% | +0.015 | -0.020% | -0.028% | 57% | -0.42% | 497.1 | 0 | - | -0.035 | -0.064% |
| 209 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c34, tf M30 | 14.7 | 33% | +0.015 | -0.009% | -0.013% | 46% | -0.45% | 294.2 | 0 | - | -0.290 | -0.074% |
| 210 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf M30 | 11.3 | 36% | +0.015 | +0.038% | +0.053% | 44% | -0.54% | 381.1 | 0 | - | -0.015 | -0.081% |
| 211 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c4, tf H4 | 8.7 | 43% | +0.015 | -0.017% | -0.024% | 57% | -0.35% | 497.1 | 0 | - | -0.075 | -0.071% |
| 212 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.015 | -0.019% | -0.027% | 43% | -0.66% | 503.8 | 0 | - | +0.066 | +0.213% |
| 213 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.015 | -0.019% | -0.027% | 43% | -0.66% | 503.8 | 0 | - | +0.092 | +0.402% |
| 214 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf H1 | 26.2 | 51% | +0.014 | +0.043% | +0.060% | 52% | -0.73% | 164.7 | 0 | - | -0.193 | -0.066% |
| 215 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf M30 | 94.2 | 38% | +0.014 | +0.011% | +0.015% | 48% | -0.54% | 45.9 | 2 | +0.9%, +0.5% | -0.033 | -0.028% |
| 216 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf M30 | 49.2 | 40% | +0.014 | +0.017% | +0.023% | 42% | -0.58% | 87.8 | 1 | +0.6% | -0.049 | -0.042% |
| 217 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf M30 | 49.1 | 32% | +0.013 | +0.009% | +0.013% | 42% | -0.34% | 88.0 | 1 | +1.1% | -0.030 | -0.035% |
| 218 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c4, tf M30 | 14.5 | 31% | +0.013 | -0.003% | -0.005% | 54% | -0.56% | 298.8 | 0 | - | -0.193 | -0.083% |
| 219 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf H1 | 3.3 | 38% | +0.012 | +0.062% | +0.086% | 50% | -0.16% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 220 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf H1 | 27.0 | 44% | +0.012 | +0.022% | +0.031% | 50% | -0.65% | 159.9 | 0 | - | -0.084 | -0.040% |
| 221 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf H4 | 8.7 | 43% | +0.012 | -0.027% | -0.037% | 57% | -0.44% | 497.1 | 0 | - | +0.134 | +0.608% |
| 222 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c4, tf M15 | 14.9 | 33% | +0.011 | -0.000% | -0.000% | 58% | -0.39% | 290.7 | 0 | - | -0.147 | -0.074% |
| 223 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf M30 | 93.5 | 31% | +0.011 | +0.009% | +0.012% | 46% | -0.53% | 46.2 | 2 | +1.2%, -0.2% | -0.067 | -0.040% |
| 224 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.011 | -0.018% | -0.025% | 57% | -0.75% | 503.8 | 0 | - | +0.086 | +0.351% |
| 225 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.011 | -0.018% | -0.025% | 57% | -0.75% | 503.8 | 0 | - | +0.099 | +0.476% |
| 226 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf H4 | 8.6 | 45% | +0.011 | -0.018% | -0.025% | 57% | -0.75% | 503.8 | 0 | - | +0.099 | +0.476% |
| 227 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf H1 | 44.8 | 34% | +0.010 | +0.019% | +0.026% | 42% | -0.37% | 96.4 | 1 | +0.2% | -0.110 | -0.049% |
| 228 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop all4, tf M15 | 4.1 | 29% | +0.010 | +0.568% | +0.789% | 33% | -0.55% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 229 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf M5 | 24.6 | 27% | +0.010 | -0.020% | -0.028% | 50% | -0.29% | 175.4 | 0 | - | -0.074 | -0.051% |
| 230 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop all4, tf M15 | 4.1 | 26% | +0.009 | +0.500% | +0.694% | 33% | -0.46% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 231 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf M30 | 49.4 | 40% | +0.009 | +0.010% | +0.014% | 46% | -0.60% | 87.4 | 1 | +0.5% | -0.054 | -0.044% |
| 232 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf M30 | 49.2 | 40% | +0.009 | +0.010% | +0.014% | 44% | -0.74% | 87.8 | 1 | +0.3% | -0.052 | -0.044% |
| 233 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf M30 | 49.1 | 37% | +0.008 | +0.008% | +0.011% | 51% | -0.44% | 88.0 | 1 | +0.9% | -0.053 | -0.046% |
| 234 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c34, tf H4 | 3.9 | 50% | +0.008 | -0.027% | -0.037% | 33% | -0.25% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 235 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf H4 | 8.6 | 44% | +0.008 | -0.026% | -0.036% | 43% | -0.69% | 503.8 | 0 | - | +0.080 | +0.315% |
| 236 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf M30 | 49.1 | 37% | +0.007 | +0.005% | +0.007% | 44% | -0.43% | 88.0 | 1 | -0.2% | -0.096 | -0.065% |
| 237 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf H1 | 13.0 | 30% | +0.007 | +0.020% | +0.027% | 55% | -0.49% | 332.3 | 0 | - | -0.104 | -0.045% |
| 238 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf H4 | 8.6 | 45% | +0.007 | -0.025% | -0.035% | 43% | -0.66% | 503.8 | 0 | - | -0.009 | -0.003% |
| 239 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf H4 | 8.6 | 45% | +0.007 | -0.025% | -0.035% | 43% | -0.66% | 503.8 | 0 | - | +0.035 | +0.134% |
| 240 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf H4 | 8.6 | 45% | +0.007 | -0.025% | -0.035% | 43% | -0.66% | 503.8 | 0 | - | +0.047 | +0.186% |
| 241 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf H1 | 12.7 | 34% | +0.007 | +0.010% | +0.014% | 27% | -0.43% | 341.1 | 0 | - | -0.039 | -0.023% |
| 242 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c4, tf M30 | 14.5 | 32% | +0.007 | -0.016% | -0.022% | 38% | -0.41% | 298.8 | 0 | - | -0.288 | -0.074% |
| 243 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c34, tf M30 | 14.9 | 40% | +0.007 | -0.004% | -0.006% | 54% | -0.70% | 289.8 | 0 | - | -0.338 | -0.085% |
| 244 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf M30 | 93.5 | 33% | +0.007 | +0.005% | +0.007% | 46% | -0.58% | 46.2 | 2 | +0.0%, +0.3% | -0.055 | -0.038% |
| 245 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf M30 | 5.5 | 38% | +0.006 | +0.066% | +0.091% | 50% | -0.46% | 782.7 | 0 | - | +0.000 | +0.000% |
| 246 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf H4 | 8.6 | 44% | +0.006 | -0.026% | -0.036% | 43% | -0.68% | 503.8 | 0 | - | +0.070 | +0.241% |
| 247 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf M30 | 5.6 | 43% | +0.005 | +0.053% | +0.074% | 50% | -0.61% | 766.8 | 0 | - | +0.000 | +0.000% |
| 248 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf M30 | 49.1 | 33% | +0.005 | +0.002% | +0.003% | 46% | -0.36% | 88.0 | 1 | +1.1% | -0.080 | -0.050% |
| 249 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf H4 | 8.6 | 44% | +0.005 | -0.026% | -0.036% | 57% | -0.63% | 503.8 | 0 | - | +0.095 | +0.339% |
| 250 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf M30 | 11.4 | 40% | +0.005 | -0.008% | -0.011% | 50% | -0.55% | 377.3 | 0 | - | +0.022 | -0.059% |
| 251 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf H1 | 5.7 | 44% | +0.004 | +0.013% | +0.018% | 25% | -0.18% | 754.8 | 0 | - | +0.164 | +3.091% |
| 252 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf H1 | 13.0 | 52% | +0.004 | +0.023% | +0.033% | 46% | -0.44% | 332.3 | 0 | - | -0.079 | -0.048% |
| 253 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf H1 | 3.0 | 38% | +0.004 | +0.017% | +0.023% | 50% | -0.33% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 254 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf M30 | 48.4 | 37% | +0.003 | +0.003% | +0.004% | 46% | -0.56% | 89.2 | 1 | +1.2% | -0.054 | -0.047% |
| 255 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop all4, tf H4 | 3.9 | 50% | +0.003 | -0.022% | -0.031% | 33% | -0.26% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 256 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf H1 | 12.7 | 34% | +0.003 | -0.001% | -0.001% | 36% | -0.45% | 341.1 | 0 | - | +0.059 | +0.057% |
| 257 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf H1 | 21.5 | 39% | +0.003 | +0.017% | +0.024% | 42% | -0.53% | 200.8 | 0 | - | -0.102 | -0.053% |
| 258 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop all4, tf M15 | 15.5 | 32% | +0.003 | -0.015% | -0.021% | 33% | -0.31% | 279.3 | 0 | - | -0.108 | -0.072% |
| 259 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf H1 | 26.4 | 37% | +0.003 | +0.022% | +0.031% | 39% | -0.36% | 163.3 | 0 | - | -0.439 | -0.085% |
| 260 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf M30 | 11.4 | 37% | +0.002 | +0.003% | +0.004% | 60% | -0.55% | 377.3 | 0 | - | -0.090 | -0.085% |
| 261 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c4, tf M15 | 15.2 | 33% | +0.002 | -0.014% | -0.019% | 42% | -0.33% | 283.8 | 0 | - | -0.061 | -0.054% |
| 262 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf M30 | 94.5 | 38% | +0.001 | -0.001% | -0.002% | 44% | -0.62% | 45.7 | 2 | +0.8%, -0.9% | -0.074 | -0.048% |
| 263 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf M30 | 48.7 | 40% | +0.001 | -0.001% | -0.001% | 42% | -0.48% | 88.8 | 1 | +1.0% | -0.070 | -0.046% |
| 264 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf H1 | 3.3 | 35% | +0.001 | +0.127% | +0.176% | 50% | -0.41% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 265 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop all4, tf M15 | 15.7 | 47% | +0.001 | +0.022% | +0.031% | 50% | -0.51% | 275.0 | 0 | - | +0.093 | +0.200% |
| 266 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf M30 | 49.0 | 39% | +0.001 | -0.001% | -0.001% | 40% | -0.45% | 88.2 | 1 | +0.9% | -0.069 | -0.044% |
| 267 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf M30 | 94.4 | 39% | -0.001 | -0.002% | -0.003% | 46% | -0.52% | 45.8 | 2 | -0.2%, +0.7% | -0.065 | -0.035% |
| 268 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf H1 | 26.0 | 36% | -0.001 | +0.014% | +0.019% | 44% | -0.54% | 166.1 | 0 | - | -0.210 | -0.066% |
| 269 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf H1 | 13.0 | 40% | -0.001 | -0.004% | -0.006% | 55% | -0.43% | 332.3 | 0 | - | -0.101 | -0.036% |
| 270 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c4, tf M15 | 3.9 | 33% | -0.001 | +0.239% | +0.331% | 33% | -0.77% | 1098.5 | 0 | - | +0.000 | +0.000% |
| 271 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf H1 | 3.3 | 42% | -0.002 | +0.110% | +0.153% | 50% | -0.33% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 272 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf H1 | 25.2 | 34% | -0.002 | +0.012% | +0.017% | 50% | -0.33% | 171.3 | 0 | - | -0.362 | -0.082% |
| 273 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf M5 | 23.4 | 23% | -0.003 | -0.030% | -0.041% | 35% | -0.37% | 184.6 | 0 | - | -0.052 | -0.046% |
| 274 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf H4 | 8.6 | 44% | -0.003 | -0.030% | -0.042% | 43% | -0.66% | 503.8 | 0 | - | +0.118 | +0.542% |
| 275 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf H4 | 8.7 | 40% | -0.004 | -0.034% | -0.047% | 43% | -0.34% | 497.1 | 0 | - | -0.112 | -0.067% |
| 276 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf M5 | 53.7 | 35% | -0.004 | -0.010% | -0.014% | 46% | -0.61% | 80.5 | 1 | -0.4% | -0.120 | -0.054% |
| 277 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf M30 | 94.2 | 33% | -0.004 | -0.004% | -0.005% | 44% | -0.48% | 45.9 | 2 | +0.8%, -0.3% | -0.037 | -0.028% |
| 278 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf M5 | 21.8 | 23% | -0.004 | +0.022% | +0.031% | 47% | -0.55% | 197.8 | 0 | - | -0.077 | -0.047% |
| 279 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf H1 | 26.2 | 39% | -0.004 | +0.013% | +0.018% | 39% | -0.51% | 164.7 | 0 | - | -0.300 | -0.075% |
| 280 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf M30 | 28.1 | 36% | -0.004 | +0.001% | +0.001% | 50% | -0.52% | 153.7 | 0 | - | +0.036 | +0.012% |
| 281 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf H1 | 12.9 | 37% | -0.005 | -0.006% | -0.008% | 36% | -0.42% | 335.2 | 0 | - | -0.038 | +0.001% |
| 282 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf H1 | 44.5 | 36% | -0.005 | +0.005% | +0.007% | 49% | -0.48% | 97.1 | 1 | -0.9% | -0.131 | -0.053% |
| 283 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf M5 | 54.1 | 35% | -0.005 | -0.011% | -0.016% | 54% | -0.43% | 79.8 | 1 | -0.7% | -0.111 | -0.052% |
| 284 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf M30 | 49.4 | 34% | -0.005 | -0.007% | -0.010% | 52% | -0.47% | 87.4 | 1 | +0.2% | -0.084 | -0.054% |
| 285 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf M30 | 94.5 | 32% | -0.006 | -0.006% | -0.009% | 48% | -0.50% | 45.7 | 2 | +0.9%, -0.4% | -0.059 | -0.037% |
| 286 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf M30 | 49.4 | 38% | -0.006 | -0.005% | -0.007% | 52% | -0.43% | 87.4 | 1 | +0.3% | -0.079 | -0.049% |
| 287 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf H4 | 3.9 | 50% | -0.006 | -0.029% | -0.040% | 33% | -0.28% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 288 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c34, tf M15 | 15.2 | 46% | -0.006 | +0.013% | +0.017% | 50% | -0.62% | 283.8 | 0 | - | +0.054 | +0.078% |
| 289 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf H1 | 13.0 | 30% | -0.006 | +0.004% | +0.005% | 55% | -0.42% | 332.3 | 0 | - | -0.097 | -0.044% |
| 290 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c34, tf H4 | 3.9 | 50% | -0.006 | -0.025% | -0.035% | 33% | -0.24% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 291 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf M15 | 7.2 | 27% | -0.007 | +0.091% | +0.127% | 20% | -0.23% | 598.2 | 0 | - | +0.015 | +0.082% |
| 292 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop all4, tf M30 | 14.7 | 38% | -0.007 | -0.015% | -0.021% | 54% | -0.64% | 294.2 | 0 | - | -0.311 | -0.086% |
| 293 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c34, tf H4 | 8.7 | 43% | -0.007 | -0.036% | -0.050% | 57% | -0.30% | 497.1 | 0 | - | +0.111 | +0.488% |
| 294 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf M5 | 23.4 | 26% | -0.008 | -0.034% | -0.047% | 50% | -0.40% | 184.6 | 0 | - | -0.082 | -0.048% |
| 295 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf M30 | 94.8 | 36% | -0.008 | -0.009% | -0.013% | 47% | -0.55% | 45.5 | 2 | -0.2%, -1.0% | -0.083 | -0.050% |
| 296 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf M5 | 5.2 | 27% | -0.009 | +0.098% | +0.136% | 25% | -0.42% | 824.8 | 0 | - | +0.000 | +0.000% |
| 297 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop all4, tf M15 | 15.8 | 32% | -0.009 | -0.025% | -0.035% | 31% | -0.32% | 272.8 | 0 | - | -0.018 | -0.044% |
| 298 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf M30 | 95.0 | 38% | -0.009 | -0.006% | -0.009% | 41% | -0.60% | 45.5 | 2 | -0.6%, -1.0% | -0.109 | -0.054% |
| 299 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf H1 | 26.2 | 41% | -0.009 | +0.012% | +0.017% | 44% | -0.54% | 164.7 | 0 | - | -0.211 | -0.069% |
| 300 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf M30 | 49.0 | 36% | -0.009 | -0.009% | -0.013% | 42% | -0.39% | 88.2 | 1 | +0.5% | -0.074 | -0.048% |
| 301 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf M30 | 5.4 | 30% | -0.009 | +0.057% | +0.080% | 25% | -0.53% | 799.4 | 0 | - | +0.000 | +0.000% |
| 302 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf M30 | 94.7 | 38% | -0.009 | -0.009% | -0.012% | 45% | -0.60% | 45.6 | 2 | -0.0%, -0.2% | -0.041 | -0.028% |
| 303 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf M30 | 94.5 | 33% | -0.010 | -0.010% | -0.014% | 51% | -0.53% | 45.7 | 2 | +0.3%, -0.4% | -0.062 | -0.038% |
| 304 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c4, tf M15 | 3.9 | 40% | -0.010 | -0.038% | -0.053% | 33% | -0.25% | 1098.5 | 0 | - | +0.000 | +0.000% |
| 305 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf M30 | 95.1 | 37% | -0.011 | -0.008% | -0.012% | 42% | -0.61% | 45.4 | 2 | -0.8%, -0.9% | -0.099 | -0.051% |
| 306 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf M30 | 5.6 | 39% | -0.011 | +0.038% | +0.053% | 75% | -0.67% | 766.8 | 0 | - | +0.000 | +0.000% |
| 307 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf H1 | 26.7 | 50% | -0.011 | +0.008% | +0.011% | 61% | -0.62% | 162.0 | 0 | - | -0.226 | -0.065% |
| 308 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c34, tf M30 | 14.7 | 36% | -0.011 | -0.018% | -0.026% | 54% | -0.58% | 294.2 | 0 | - | -0.276 | -0.085% |
| 309 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf H1 | 5.6 | 40% | -0.011 | -0.056% | -0.077% | 0% | -0.20% | 770.9 | 0 | - | +0.086 | +0.989% |
| 310 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf M30 | 94.5 | 36% | -0.012 | -0.011% | -0.015% | 46% | -0.60% | 45.7 | 2 | -0.1%, -0.1% | -0.071 | -0.043% |
| 311 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf H1 | 13.0 | 29% | -0.012 | -0.009% | -0.013% | 55% | -0.49% | 332.3 | 0 | - | -0.093 | -0.041% |
| 312 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf H1 | 3.1 | 33% | -0.012 | -0.028% | -0.039% | 100% | +0.02% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 313 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf M30 | 11.4 | 36% | -0.012 | -0.007% | -0.010% | 50% | -0.52% | 377.3 | 0 | - | -0.019 | -0.081% |
| 314 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf H1 | 27.0 | 41% | -0.012 | -0.003% | -0.004% | 42% | -0.44% | 159.9 | 0 | - | -0.127 | -0.050% |
| 315 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c4, tf H4 | 3.9 | 50% | -0.013 | -0.026% | -0.037% | 33% | -0.24% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 316 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf M30 | 96.0 | 38% | -0.013 | -0.010% | -0.014% | 42% | -0.52% | 45.0 | 2 | -0.8%, -1.4% | -0.125 | -0.057% |
| 317 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf M30 | 96.0 | 38% | -0.013 | -0.010% | -0.013% | 46% | -0.64% | 45.0 | 2 | -0.5%, -1.6% | -0.126 | -0.058% |
| 318 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf H1 | 13.0 | 49% | -0.013 | -0.004% | -0.006% | 36% | -0.34% | 332.3 | 0 | - | -0.105 | -0.052% |
| 319 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop all4, tf H4 | 3.9 | 50% | -0.013 | -0.024% | -0.033% | 33% | -0.24% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 320 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf M30 | 48.7 | 48% | -0.014 | -0.009% | -0.013% | 44% | -0.59% | 88.8 | 1 | +0.0% | +0.007 | -0.019% |
| 321 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c4, tf M15 | 4.2 | 25% | -0.014 | +0.381% | +0.529% | 33% | -0.56% | 1029.8 | 0 | - | +0.216 | +0.873% |
| 322 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf M30 | 52.5 | 27% | -0.014 | -0.016% | -0.023% | 55% | -0.47% | 82.3 | 1 | -0.0% | +0.032 | -0.003% |
| 323 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf M30 | 49.1 | 39% | -0.014 | -0.008% | -0.012% | 46% | -0.40% | 88.0 | 1 | -0.1% | -0.032 | -0.029% |
| 324 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf M30 | 93.7 | 37% | -0.014 | -0.011% | -0.016% | 40% | -0.44% | 46.1 | 2 | -1.0%, -0.9% | -0.099 | -0.052% |
| 325 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf M30 | 49.0 | 35% | -0.014 | -0.014% | -0.020% | 37% | -0.36% | 88.2 | 1 | +0.1% | -0.039 | -0.038% |
| 326 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf H1 | 3.0 | 33% | -0.014 | +0.048% | +0.066% | 50% | -0.32% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 327 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf H4 | 8.6 | 40% | -0.014 | -0.040% | -0.055% | 43% | -0.31% | 503.8 | 0 | - | +0.088 | +0.399% |
| 328 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf H1 | 26.1 | 36% | -0.015 | +0.002% | +0.003% | 44% | -0.40% | 165.4 | 0 | - | -0.389 | -0.083% |
| 329 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf M30 | 5.6 | 35% | -0.015 | +0.033% | +0.045% | 50% | -0.59% | 766.8 | 0 | - | +0.000 | +0.000% |
| 330 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf M30 | 7.1 | 25% | -0.015 | -0.033% | -0.045% | 33% | -0.22% | 606.7 | 0 | - | -0.065 | -0.074% |
| 331 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf M30 | 49.1 | 48% | -0.016 | -0.010% | -0.014% | 49% | -0.62% | 88.0 | 1 | -0.4% | -0.005 | -0.021% |
| 332 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf H1 | 3.3 | 38% | -0.016 | -0.006% | -0.008% | 50% | -0.16% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 333 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf H1 | 13.0 | 43% | -0.016 | -0.017% | -0.023% | 55% | -0.39% | 332.3 | 0 | - | -0.093 | -0.034% |
| 334 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf H1 | 13.0 | 40% | -0.016 | -0.005% | -0.007% | 36% | -0.33% | 332.3 | 0 | - | -0.154 | -0.060% |
| 335 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf H4 | 8.6 | 40% | -0.016 | -0.040% | -0.055% | 43% | -0.32% | 503.8 | 0 | - | +0.055 | +0.271% |
| 336 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf M15 | 15.5 | 37% | -0.017 | -0.022% | -0.031% | 54% | -0.29% | 278.6 | 0 | - | +0.208 | +1.078% |
| 337 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf M30 | 93.7 | 35% | -0.017 | -0.014% | -0.019% | 40% | -0.49% | 46.1 | 2 | -1.0%, -0.6% | -0.081 | -0.050% |
| 338 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf H1 | 27.0 | 41% | -0.017 | -0.006% | -0.009% | 50% | -0.47% | 159.9 | 0 | - | -0.039 | -0.021% |
| 339 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf H4 | 8.7 | 40% | -0.017 | -0.041% | -0.058% | 57% | -0.33% | 497.1 | 0 | - | +0.108 | +0.492% |
| 340 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf M30 | 48.7 | 36% | -0.017 | -0.015% | -0.021% | 44% | -0.38% | 88.8 | 1 | -0.0% | -0.053 | -0.046% |
| 341 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf H1 | 12.9 | 36% | -0.018 | -0.023% | -0.032% | 46% | -0.40% | 335.2 | 0 | - | -0.016 | +0.012% |
| 342 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf M30 | 93.5 | 36% | -0.018 | -0.014% | -0.020% | 49% | -0.60% | 46.2 | 2 | -0.8%, +0.1% | -0.060 | -0.041% |
| 343 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf M30 | 94.0 | 39% | -0.018 | -0.014% | -0.019% | 44% | -0.44% | 46.0 | 2 | -0.0%, +0.1% | -0.058 | -0.033% |
| 344 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf M5 | 5.2 | 27% | -0.018 | +0.082% | +0.114% | 25% | -0.47% | 824.8 | 0 | - | +0.000 | +0.000% |
| 345 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c4, tf M30 | 14.5 | 36% | -0.019 | -0.022% | -0.030% | 46% | -0.59% | 298.8 | 0 | - | -0.289 | -0.086% |
| 346 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf M30 | 94.7 | 38% | -0.019 | -0.016% | -0.022% | 46% | -0.55% | 45.6 | 2 | -0.2%, -1.4% | -0.113 | -0.056% |
| 347 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf H1 | 12.7 | 31% | -0.019 | -0.018% | -0.024% | 27% | -0.28% | 341.1 | 0 | - | -0.089 | -0.048% |
| 348 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf H1 | 45.1 | 36% | -0.019 | -0.010% | -0.014% | 38% | -0.36% | 95.7 | 1 | -1.1% | -0.231 | -0.066% |
| 349 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf H1 | 27.0 | 37% | -0.020 | -0.009% | -0.012% | 50% | -0.42% | 159.9 | 0 | - | -0.382 | -0.083% |
| 350 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf H4 | 8.6 | 40% | -0.020 | -0.042% | -0.058% | 43% | -0.32% | 503.8 | 0 | - | +0.078 | +0.349% |
| 351 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf M30 | 5.6 | 51% | -0.020 | -0.044% | -0.061% | 50% | -0.37% | 766.8 | 0 | - | +0.000 | +0.000% |
| 352 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf H1 | 13.2 | 34% | -0.020 | -0.016% | -0.022% | 36% | -0.30% | 326.7 | 0 | - | -0.123 | -0.056% |
| 353 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf H1 | 3.5 | 53% | -0.021 | -0.052% | -0.072% | 67% | -0.21% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 354 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf H1 | 21.9 | 34% | -0.021 | -0.011% | -0.015% | 37% | -0.40% | 197.7 | 0 | - | -0.101 | -0.048% |
| 355 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf M5 | 53.7 | 28% | -0.021 | -0.025% | -0.034% | 42% | -0.46% | 80.5 | 1 | -0.7% | -0.111 | -0.051% |
| 356 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf M30 | 28.1 | 28% | -0.021 | -0.015% | -0.021% | 50% | -0.48% | 153.7 | 0 | - | -0.030 | -0.045% |
| 357 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop all4, tf M30 | 14.7 | 33% | -0.021 | -0.029% | -0.040% | 38% | -0.38% | 294.2 | 0 | - | -0.320 | -0.076% |
| 358 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf H1 | 45.7 | 35% | -0.021 | -0.011% | -0.016% | 30% | -0.37% | 94.5 | 1 | -0.8% | -0.152 | -0.053% |
| 359 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf M30 | 7.1 | 25% | -0.021 | -0.051% | -0.070% | 50% | -0.29% | 606.7 | 0 | - | -0.346 | -0.071% |
| 360 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf M30 | 95.1 | 38% | -0.021 | -0.018% | -0.024% | 44% | -0.45% | 45.4 | 2 | -0.1%, -1.9% | -0.108 | -0.055% |
| 361 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf H1 | 22.0 | 39% | -0.021 | -0.010% | -0.014% | 42% | -0.42% | 196.7 | 0 | - | -0.049 | -0.026% |
| 362 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf H1 | 5.6 | 45% | -0.021 | -0.030% | -0.041% | 25% | -0.26% | 770.9 | 0 | - | +0.226 | +1.664% |
| 363 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf H1 | 45.7 | 36% | -0.022 | -0.014% | -0.019% | 35% | -0.36% | 94.5 | 1 | -0.9% | -0.174 | -0.058% |
| 364 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf M30 | 96.0 | 39% | -0.022 | -0.016% | -0.022% | 45% | -0.66% | 45.0 | 2 | -0.7%, -1.6% | -0.116 | -0.056% |
| 365 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf M30 | 94.7 | 34% | -0.022 | -0.017% | -0.024% | 40% | -0.50% | 45.6 | 2 | +0.0%, -0.8% | -0.044 | -0.027% |
| 366 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf H1 | 26.0 | 38% | -0.022 | -0.003% | -0.005% | 39% | -0.54% | 166.1 | 0 | - | -0.191 | -0.068% |
| 367 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf H1 | 21.5 | 38% | -0.022 | -0.010% | -0.014% | 32% | -0.29% | 200.8 | 0 | - | -0.109 | -0.053% |
| 368 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf M30 | 48.4 | 38% | -0.023 | -0.016% | -0.022% | 42% | -0.49% | 89.2 | 1 | -0.3% | -0.035 | -0.034% |
| 369 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop all4, tf M15 | 15.2 | 50% | -0.023 | -0.027% | -0.038% | 42% | -0.40% | 283.8 | 0 | - | -0.101 | -0.055% |
| 370 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf H4 | 3.9 | 47% | -0.023 | -0.036% | -0.051% | 33% | -0.29% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 371 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop all4, tf H1 | 5.6 | 38% | -0.023 | -0.059% | -0.081% | 25% | -0.21% | 770.9 | 0 | - | -0.018 | +0.235% |
| 372 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c34, tf M15 | 4.1 | 39% | -0.023 | -0.047% | -0.065% | 33% | -0.23% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 373 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf H1 | 44.5 | 38% | -0.023 | -0.008% | -0.012% | 54% | -0.49% | 97.1 | 1 | -1.2% | -0.088 | -0.042% |
| 374 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf M5 | 25.2 | 26% | -0.023 | -0.029% | -0.041% | 36% | -0.36% | 171.5 | 0 | - | -0.044 | -0.046% |
| 375 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf M30 | 94.4 | 36% | -0.023 | -0.017% | -0.024% | 46% | -0.48% | 45.8 | 2 | -0.4%, -0.5% | -0.059 | -0.033% |
| 376 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf M30 | 7.0 | 27% | -0.023 | -0.030% | -0.041% | 50% | -0.29% | 616.9 | 0 | - | +0.022 | -0.020% |
| 377 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf M5 | 22.9 | 27% | -0.024 | -0.006% | -0.009% | 45% | -0.49% | 189.0 | 0 | - | -0.052 | -0.036% |
| 378 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c4, tf M30 | 14.5 | 29% | -0.024 | -0.023% | -0.031% | 46% | -0.56% | 298.8 | 0 | - | -0.332 | -0.085% |
| 379 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop all4, tf H4 | 8.6 | 44% | -0.024 | -0.041% | -0.057% | 43% | -0.50% | 503.8 | 0 | - | +0.077 | +0.259% |
| 380 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf M30 | 7.8 | 36% | -0.024 | -0.034% | -0.048% | 43% | -0.44% | 554.3 | 0 | - | -0.172 | -0.083% |
| 381 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf M5 | 54.4 | 34% | -0.024 | -0.024% | -0.034% | 50% | -0.39% | 79.5 | 1 | -1.0% | -0.111 | -0.053% |
| 382 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf H1 | 3.0 | 33% | -0.024 | +0.027% | +0.037% | 50% | -0.31% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 383 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c34, tf H4 | 8.6 | 44% | -0.024 | -0.042% | -0.058% | 43% | -0.54% | 503.8 | 0 | - | +0.051 | +0.172% |
| 384 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c4, tf H4 | 8.6 | 44% | -0.024 | -0.042% | -0.058% | 43% | -0.51% | 503.8 | 0 | - | +0.056 | +0.184% |
| 385 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf M30 | 5.6 | 45% | -0.025 | -0.011% | -0.015% | 25% | -0.51% | 766.8 | 0 | - | +0.000 | +0.000% |
| 386 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf H1 | 3.0 | 33% | -0.025 | +0.001% | +0.002% | 50% | -0.28% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 387 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf H1 | 13.1 | 43% | -0.025 | -0.005% | -0.006% | 46% | -0.32% | 329.5 | 0 | - | -0.214 | -0.063% |
| 388 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf H1 | 27.1 | 41% | -0.025 | -0.010% | -0.014% | 46% | -0.39% | 159.3 | 0 | - | -0.241 | -0.069% |
| 389 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c4, tf H1 | 7.2 | 38% | -0.025 | -0.021% | -0.029% | 50% | -0.36% | 597.7 | 0 | - | -0.344 | -0.084% |
| 390 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf H1 | 45.6 | 36% | -0.025 | -0.014% | -0.019% | 40% | -0.47% | 94.8 | 1 | -0.9% | -0.163 | -0.053% |
| 391 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf H1 | 12.7 | 25% | -0.025 | -0.019% | -0.027% | 46% | -0.38% | 341.1 | 0 | - | -0.022 | -0.000% |
| 392 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf H1 | 25.2 | 48% | -0.026 | -0.002% | -0.003% | 50% | -0.55% | 171.3 | 0 | - | -0.198 | -0.067% |
| 393 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf H4 | 4.7 | 42% | -0.026 | -0.040% | -0.055% | 50% | -0.28% | 917.0 | 0 | - | -0.079 | -0.053% |
| 394 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c4, tf H1 | 7.2 | 39% | -0.027 | -0.018% | -0.025% | 17% | -0.33% | 597.7 | 0 | - | -0.041 | +0.141% |
| 395 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf H1 | 13.0 | 34% | -0.028 | -0.022% | -0.030% | 46% | -0.33% | 332.3 | 0 | - | -0.088 | -0.051% |
| 396 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c4, tf M15 | 15.0 | 37% | -0.028 | -0.020% | -0.027% | 50% | -0.56% | 288.4 | 0 | - | +0.021 | +0.019% |
| 397 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf H1 | 25.2 | 25% | -0.028 | -0.015% | -0.021% | 27% | -0.25% | 171.3 | 0 | - | -0.140 | -0.059% |
| 398 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf M15 | 15.4 | 35% | -0.028 | -0.020% | -0.027% | 46% | -0.45% | 280.8 | 0 | - | +0.196 | +0.702% |
| 399 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf M30 | 28.1 | 36% | -0.028 | -0.023% | -0.033% | 42% | -0.35% | 153.7 | 0 | - | -0.266 | -0.074% |
| 400 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c34, tf M30 | 14.9 | 33% | -0.028 | -0.034% | -0.047% | 31% | -0.36% | 289.8 | 0 | - | -0.273 | -0.073% |
| 401 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf H1 | 21.6 | 35% | -0.028 | -0.016% | -0.023% | 42% | -0.43% | 199.7 | 0 | - | -0.022 | -0.012% |
| 402 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf H1 | 5.6 | 40% | -0.028 | -0.048% | -0.067% | 25% | -0.25% | 770.9 | 0 | - | +0.086 | +0.989% |
| 403 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf M5 | 17.2 | 20% | -0.028 | -0.046% | -0.064% | 27% | -0.20% | 251.8 | 0 | - | +0.065 | +0.042% |
| 404 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.028 | -0.075% | -0.105% | 33% | -0.13% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 405 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c4, tf M30 | 14.8 | 33% | -0.029 | -0.034% | -0.048% | 31% | -0.36% | 292.0 | 0 | - | -0.316 | -0.076% |
| 406 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf M5 | 21.2 | 22% | -0.029 | -0.002% | -0.003% | 44% | -0.45% | 204.2 | 0 | - | -0.105 | -0.050% |
| 407 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop all4, tf H1 | 21.6 | 32% | -0.029 | -0.015% | -0.020% | 53% | -0.37% | 199.7 | 0 | - | -0.123 | -0.055% |
| 408 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf M30 | 52.6 | 32% | -0.029 | -0.029% | -0.041% | 36% | -0.38% | 82.1 | 1 | -0.5% | -0.082 | -0.050% |
| 409 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf M5 | 5.2 | 22% | -0.029 | +0.088% | +0.123% | 25% | -0.34% | 824.8 | 0 | - | +0.000 | +0.000% |
| 410 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c34, tf M5 | 46.5 | 30% | -0.029 | -0.023% | -0.031% | 46% | -0.49% | 93.0 | 1 | -0.9% | +0.010 | +0.014% |
| 411 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf M5 | 5.7 | 33% | -0.029 | +0.061% | +0.085% | 50% | -0.43% | 757.4 | 0 | - | +0.000 | +0.000% |
| 412 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf H1 | 45.0 | 40% | -0.030 | -0.016% | -0.022% | 35% | -0.39% | 95.9 | 1 | -0.9% | -0.162 | -0.058% |
| 413 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf H1 | 44.6 | 39% | -0.030 | -0.013% | -0.018% | 44% | -0.48% | 96.9 | 1 | -1.2% | -0.197 | -0.061% |
| 414 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf H4 | 8.6 | 40% | -0.030 | -0.045% | -0.063% | 43% | -0.30% | 503.8 | 0 | - | +0.098 | +0.461% |
| 415 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c4, tf M15 | 15.2 | 46% | -0.030 | -0.012% | -0.017% | 58% | -0.49% | 283.8 | 0 | - | +0.033 | +0.042% |
| 416 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c34, tf M30 | 14.7 | 31% | -0.030 | -0.035% | -0.049% | 54% | -0.49% | 294.2 | 0 | - | -0.199 | -0.083% |
| 417 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop all4, tf M15 | 27.6 | 32% | -0.030 | -0.016% | -0.023% | 33% | -0.46% | 156.4 | 0 | - | +0.104 | +0.187% |
| 418 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf M5 | 5.9 | 33% | -0.030 | +0.059% | +0.081% | 40% | -0.47% | 727.7 | 0 | - | +0.000 | +0.000% |
| 419 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf M5 | 5.9 | 33% | -0.031 | +0.053% | +0.074% | 40% | -0.44% | 727.7 | 0 | - | +0.000 | +0.000% |
| 420 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c34, tf M30 | 14.7 | 30% | -0.031 | -0.027% | -0.038% | 46% | -0.57% | 294.2 | 0 | - | -0.331 | -0.085% |
| 421 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf M30 | 48.7 | 37% | -0.031 | -0.023% | -0.032% | 42% | -0.37% | 88.8 | 1 | -0.2% | -0.066 | -0.048% |
| 422 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf H1 | 26.8 | 40% | -0.031 | -0.012% | -0.016% | 48% | -0.35% | 161.3 | 0 | - | -0.269 | -0.068% |
| 423 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop all4, tf M15 | 28.2 | 42% | -0.032 | -0.016% | -0.022% | 38% | -0.57% | 153.3 | 0 | - | +0.131 | +0.342% |
| 424 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf M30 | 11.4 | 39% | -0.032 | -0.033% | -0.046% | 50% | -0.45% | 377.3 | 0 | - | +0.004 | -0.062% |
| 425 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf H1 | 26.4 | 39% | -0.032 | -0.015% | -0.020% | 39% | -0.40% | 163.3 | 0 | - | -0.272 | -0.070% |
| 426 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf M30 | 94.3 | 35% | -0.032 | -0.024% | -0.033% | 51% | -0.46% | 45.8 | 2 | -0.5%, -0.5% | -0.068 | -0.037% |
| 427 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf M30 | 94.2 | 47% | -0.032 | -0.024% | -0.034% | 39% | -0.45% | 45.9 | 2 | -1.4%, +0.1% | +0.004 | -0.005% |
| 428 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf H1 | 5.7 | 40% | -0.032 | -0.059% | -0.082% | 0% | -0.15% | 754.8 | 0 | - | +0.085 | +1.002% |
| 429 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf M30 | 11.4 | 36% | -0.032 | -0.023% | -0.031% | 40% | -0.46% | 377.3 | 0 | - | -0.052 | -0.083% |
| 430 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf M15 | 14.9 | 28% | -0.032 | -0.026% | -0.036% | 33% | -0.36% | 289.7 | 0 | - | +0.225 | +0.947% |
| 431 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c34, tf M15 | 15.2 | 44% | -0.032 | -0.011% | -0.015% | 50% | -0.46% | 283.8 | 0 | - | -0.059 | -0.045% |
| 432 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf H1 | 26.0 | 33% | -0.032 | -0.016% | -0.022% | 39% | -0.41% | 166.1 | 0 | - | -0.155 | -0.057% |
| 433 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf H1 | 26.2 | 36% | -0.032 | -0.016% | -0.022% | 39% | -0.45% | 164.7 | 0 | - | -0.198 | -0.063% |
| 434 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf H1 | 6.0 | 38% | -0.033 | -0.018% | -0.025% | 40% | -0.31% | 724.6 | 0 | - | +0.444 | +9.068% |
| 435 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c4, tf M30 | 95.5 | 30% | -0.033 | -0.023% | -0.032% | 34% | -0.38% | 45.2 | 2 | -0.3%, -1.7% | -0.129 | -0.056% |
| 436 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf H1 | 13.0 | 42% | -0.033 | -0.026% | -0.036% | 36% | -0.35% | 332.3 | 0 | - | -0.021 | -0.015% |
| 437 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf H1 | 13.0 | 49% | -0.033 | -0.009% | -0.012% | 36% | -0.34% | 332.3 | 0 | - | -0.200 | -0.062% |
| 438 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf M15 | 11.4 | 31% | -0.033 | -0.034% | -0.047% | 50% | -0.38% | 377.3 | 0 | - | -0.040 | +0.125% |
| 439 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c4, tf M15 | 14.7 | 49% | -0.033 | -0.027% | -0.037% | 42% | -0.31% | 293.1 | 0 | - | -0.025 | -0.022% |
| 440 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf H1 | 5.6 | 40% | -0.033 | -0.063% | -0.087% | 0% | -0.19% | 770.9 | 0 | - | +0.086 | +0.989% |
| 441 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf M30 | 94.7 | 33% | -0.033 | -0.025% | -0.034% | 41% | -0.47% | 45.6 | 2 | -0.5%, -0.7% | -0.074 | -0.041% |
| 442 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf M30 | 94.6 | 38% | -0.034 | -0.024% | -0.033% | 42% | -0.54% | 45.7 | 2 | -0.5%, -1.6% | -0.092 | -0.051% |
| 443 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c34, tf M30 | 14.7 | 39% | -0.034 | -0.032% | -0.045% | 38% | -0.44% | 294.2 | 0 | - | -0.335 | -0.086% |
| 444 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf M30 | 93.8 | 36% | -0.034 | -0.024% | -0.033% | 42% | -0.49% | 46.0 | 2 | -0.2%, -0.9% | -0.082 | -0.042% |
| 445 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf H1 | 13.0 | 45% | -0.034 | -0.020% | -0.028% | 46% | -0.41% | 332.3 | 0 | - | -0.114 | -0.039% |
| 446 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf H1 | 5.7 | 44% | -0.034 | -0.033% | -0.046% | 25% | -0.16% | 754.8 | 0 | - | +0.208 | +4.232% |
| 447 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf H1 | 45.3 | 34% | -0.034 | -0.020% | -0.028% | 38% | -0.45% | 95.5 | 1 | -1.2% | -0.174 | -0.059% |
| 448 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c34, tf M30 | 95.6 | 30% | -0.034 | -0.024% | -0.033% | 36% | -0.44% | 45.2 | 2 | -0.5%, -1.6% | -0.129 | -0.054% |
| 449 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf M30 | 94.0 | 47% | -0.034 | -0.023% | -0.032% | 40% | -0.54% | 46.0 | 2 | -0.9%, -0.5% | -0.025 | -0.023% |
| 450 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop all4, tf M30 | 14.7 | 33% | -0.035 | -0.036% | -0.050% | 54% | -0.54% | 294.2 | 0 | - | -0.310 | -0.086% |
| 451 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf M5 | 25.2 | 32% | -0.035 | -0.039% | -0.054% | 36% | -0.44% | 171.5 | 0 | - | -0.040 | -0.036% |
| 452 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf M5 | 54.1 | 28% | -0.035 | -0.029% | -0.041% | 50% | -0.45% | 79.8 | 1 | -1.1% | -0.098 | -0.048% |
| 453 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf M30 | 49.4 | 48% | -0.035 | -0.022% | -0.030% | 48% | -0.56% | 87.4 | 1 | -0.6% | -0.017 | -0.028% |
| 454 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf M30 | 49.0 | 47% | -0.035 | -0.021% | -0.029% | 49% | -0.52% | 88.2 | 1 | -0.5% | -0.011 | -0.024% |
| 455 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf H1 | 21.5 | 37% | -0.035 | -0.020% | -0.028% | 37% | -0.37% | 200.8 | 0 | - | -0.082 | -0.046% |
| 456 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf M15 | 11.4 | 22% | -0.035 | -0.029% | -0.040% | 40% | -0.35% | 377.3 | 0 | - | +0.127 | +0.715% |
| 457 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf M30 | 94.0 | 36% | -0.035 | -0.024% | -0.033% | 46% | -0.50% | 46.0 | 2 | -0.5%, -0.9% | -0.049 | -0.030% |
| 458 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf M30 | 7.7 | 33% | -0.035 | -0.035% | -0.049% | 33% | -0.34% | 560.8 | 0 | - | -0.158 | -0.085% |
| 459 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf H1 | 44.7 | 38% | -0.035 | -0.017% | -0.023% | 45% | -0.42% | 96.6 | 1 | -1.4% | -0.088 | -0.039% |
| 460 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c4, tf H4 | 3.9 | 50% | -0.035 | -0.040% | -0.055% | 33% | -0.25% | 1103.2 | 0 | - | +0.000 | +0.000% |
| 461 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf M5 | 5.4 | 22% | -0.036 | +0.057% | +0.079% | 25% | -0.27% | 806.8 | 0 | - | +0.000 | +0.000% |
| 462 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf M15 | 14.9 | 35% | -0.036 | -0.031% | -0.043% | 33% | -0.31% | 289.7 | 0 | - | +0.198 | +0.850% |
| 463 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf H1 | 22.0 | 37% | -0.036 | -0.022% | -0.031% | 37% | -0.46% | 196.7 | 0 | - | -0.082 | -0.044% |
| 464 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c4, tf M30 | 14.5 | 38% | -0.037 | -0.035% | -0.049% | 38% | -0.43% | 298.8 | 0 | - | -0.303 | -0.084% |
| 465 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf H1 | 12.7 | 36% | -0.037 | -0.024% | -0.033% | 27% | -0.39% | 341.1 | 0 | - | -0.019 | -0.020% |
| 466 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf M5 | 5.7 | 31% | -0.038 | +0.044% | +0.061% | 50% | -0.35% | 757.4 | 0 | - | +0.000 | +0.000% |
| 467 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c4, tf M15 | 14.7 | 29% | -0.038 | -0.018% | -0.025% | 33% | -0.43% | 293.1 | 0 | - | +0.003 | -0.022% |
| 468 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf M30 | 5.6 | 31% | -0.038 | +0.040% | +0.056% | 50% | -0.53% | 766.8 | 0 | - | +0.000 | +0.000% |
| 469 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop all4, tf M15 | 15.2 | 46% | -0.039 | -0.020% | -0.027% | 50% | -0.43% | 283.8 | 0 | - | -0.050 | -0.043% |
| 470 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf H1 | 22.0 | 37% | -0.039 | -0.020% | -0.028% | 32% | -0.45% | 196.7 | 0 | - | -0.071 | -0.040% |
| 471 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop all4, tf M30 | 95.4 | 30% | -0.039 | -0.027% | -0.037% | 35% | -0.38% | 45.3 | 2 | -0.5%, -1.6% | -0.117 | -0.052% |
| 472 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf M5 | 22.0 | 31% | -0.040 | -0.018% | -0.025% | 37% | -0.49% | 196.8 | 0 | - | -0.047 | -0.041% |
| 473 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf M5 | 22.9 | 33% | -0.040 | -0.015% | -0.020% | 45% | -0.58% | 189.0 | 0 | - | -0.003 | -0.012% |
| 474 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf M15 | 7.8 | 33% | -0.040 | -0.004% | -0.005% | 33% | -0.35% | 551.4 | 0 | - | +0.105 | +0.118% |
| 475 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf M30 | 5.4 | 49% | -0.040 | -0.022% | -0.030% | 50% | -0.45% | 799.4 | 0 | - | +0.000 | +0.000% |
| 476 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf H1 | 26.7 | 42% | -0.040 | -0.021% | -0.030% | 44% | -0.45% | 162.0 | 0 | - | -0.155 | -0.048% |
| 477 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf M30 | 5.4 | 38% | -0.040 | -0.014% | -0.020% | 25% | -0.33% | 799.4 | 0 | - | +0.000 | +0.000% |
| 478 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c34, tf M30 | 95.0 | 29% | -0.040 | -0.028% | -0.039% | 39% | -0.41% | 45.5 | 2 | -0.8%, -1.6% | -0.105 | -0.052% |
| 479 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf H1 | 26.0 | 49% | -0.040 | -0.012% | -0.017% | 48% | -0.45% | 166.1 | 0 | - | -0.147 | -0.062% |
| 480 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf H1 | 44.8 | 45% | -0.040 | -0.019% | -0.026% | 50% | -0.46% | 96.4 | 1 | -1.5% | -0.110 | -0.047% |
| 481 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c34, tf M5 | 46.5 | 35% | -0.040 | -0.031% | -0.043% | 37% | -0.47% | 93.0 | 1 | -1.4% | -0.057 | -0.035% |
| 482 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf H1 | 45.3 | 45% | -0.041 | -0.024% | -0.033% | 42% | -0.47% | 95.5 | 1 | -1.1% | -0.043 | -0.026% |
| 483 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf M5 | 22.1 | 20% | -0.041 | -0.052% | -0.072% | 21% | -0.19% | 195.9 | 0 | - | +0.020 | -0.009% |
| 484 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop all4, tf M15 | 15.2 | 37% | -0.041 | -0.025% | -0.035% | 42% | -0.56% | 283.8 | 0 | - | -0.081 | -0.055% |
| 485 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf M30 | 94.4 | 47% | -0.041 | -0.026% | -0.036% | 43% | -0.53% | 45.8 | 2 | -1.4%, -0.1% | -0.040 | -0.026% |
| 486 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf H1 | 21.4 | 38% | -0.041 | -0.023% | -0.032% | 32% | -0.40% | 201.8 | 0 | - | -0.147 | -0.063% |
| 487 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf H1 | 21.4 | 36% | -0.041 | -0.025% | -0.034% | 26% | -0.35% | 201.8 | 0 | - | -0.116 | -0.057% |
| 488 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c4, tf M30 | 93.8 | 29% | -0.041 | -0.029% | -0.041% | 37% | -0.34% | 46.0 | 2 | -1.2%, -1.3% | -0.090 | -0.048% |
| 489 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf M30 | 5.6 | 45% | -0.042 | -0.020% | -0.028% | 25% | -0.48% | 766.8 | 0 | - | +0.000 | +0.000% |
| 490 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf H1 | 13.0 | 43% | -0.042 | -0.021% | -0.029% | 36% | -0.36% | 332.3 | 0 | - | -0.010 | -0.025% |
| 491 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf M30 | 5.6 | 49% | -0.042 | -0.024% | -0.034% | 75% | -0.48% | 766.8 | 0 | - | +0.000 | +0.000% |
| 492 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf M15 | 7.5 | 26% | -0.042 | -0.010% | -0.014% | 17% | -0.60% | 578.5 | 0 | - | +0.042 | +0.128% |
| 493 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf M5 | 24.6 | 31% | -0.042 | -0.044% | -0.061% | 41% | -0.27% | 175.4 | 0 | - | -0.018 | -0.023% |
| 494 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop all4, tf M30 | 94.8 | 29% | -0.042 | -0.029% | -0.040% | 33% | -0.46% | 45.5 | 2 | -0.7%, -1.8% | -0.085 | -0.045% |
| 495 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf H1 | 3.2 | 43% | -0.043 | -0.049% | -0.068% | 50% | -0.12% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 496 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf M15 | 174.5 | 29% | -0.043 | -0.028% | -0.039% | 43% | -0.47% | 24.8 | 4 | -0.3%, -1.3%, -2.6%, +0.5% | +0.001 | -0.002% |
| 497 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf M15 | 15.1 | 27% | -0.043 | -0.033% | -0.046% | 42% | -0.40% | 285.2 | 0 | - | +0.078 | +0.030% |
| 498 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c4, tf M15 | 3.9 | 47% | -0.043 | -0.022% | -0.031% | 33% | -0.18% | 1098.5 | 0 | - | +0.000 | +0.000% |
| 499 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf H1 | 6.0 | 38% | -0.043 | -0.025% | -0.035% | 40% | -0.30% | 724.6 | 0 | - | +0.451 | +10.407% |
| 500 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop all4, tf M15 | 27.2 | 29% | -0.043 | -0.026% | -0.035% | 44% | -0.39% | 159.1 | 0 | - | -0.015 | -0.019% |
| 501 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf H1 | 26.7 | 36% | -0.043 | -0.025% | -0.035% | 39% | -0.32% | 162.0 | 0 | - | -0.363 | -0.083% |
| 502 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c34, tf M15 | 15.3 | 40% | -0.043 | -0.030% | -0.042% | 50% | -0.43% | 281.5 | 0 | - | -0.088 | -0.045% |
| 503 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf M30 | 49.1 | 22% | -0.043 | -0.029% | -0.040% | 34% | -0.39% | 87.9 | 1 | -0.6% | -0.020 | -0.029% |
| 504 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop all4, tf H4 | 8.6 | 44% | -0.043 | -0.049% | -0.068% | 43% | -0.52% | 503.8 | 0 | - | +0.028 | +0.083% |
| 505 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c34, tf H1 | 5.6 | 38% | -0.044 | -0.063% | -0.087% | 25% | -0.20% | 770.9 | 0 | - | +0.086 | +1.412% |
| 506 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf M5 | 5.7 | 26% | -0.044 | +0.064% | +0.089% | 50% | -0.63% | 757.4 | 0 | - | +0.000 | +0.000% |
| 507 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf H1 | 21.4 | 36% | -0.044 | -0.028% | -0.039% | 26% | -0.34% | 201.8 | 0 | - | -0.096 | -0.052% |
| 508 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf H1 | 27.3 | 36% | -0.045 | -0.027% | -0.038% | 46% | -0.36% | 158.0 | 0 | - | -0.394 | -0.084% |
| 509 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf H1 | 13.0 | 40% | -0.045 | -0.028% | -0.039% | 36% | -0.36% | 332.3 | 0 | - | -0.141 | -0.053% |
| 510 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c4, tf M30 | 14.8 | 30% | -0.045 | -0.031% | -0.043% | 38% | -0.52% | 292.0 | 0 | - | -0.330 | -0.083% |
| 511 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c34, tf M15 | 27.3 | 30% | -0.045 | -0.027% | -0.037% | 44% | -0.43% | 158.4 | 0 | - | +0.095 | +0.160% |
| 512 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf H1 | 3.0 | 38% | -0.046 | -0.037% | -0.051% | 50% | -0.16% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 513 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c4, tf H1 | 44.9 | 30% | -0.046 | -0.028% | -0.039% | 35% | -0.35% | 96.2 | 1 | -1.6% | -0.143 | -0.056% |
| 514 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf M5 | 21.8 | 32% | -0.046 | -0.021% | -0.030% | 37% | -0.58% | 197.8 | 0 | - | -0.027 | -0.041% |
| 515 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c34, tf H1 | 21.6 | 32% | -0.046 | -0.026% | -0.036% | 42% | -0.32% | 199.7 | 0 | - | -0.092 | -0.044% |
| 516 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf M15 | 88.4 | 26% | -0.047 | -0.032% | -0.045% | 35% | -0.32% | 48.9 | 2 | -0.8%, -1.1% | -0.082 | -0.049% |
| 517 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf M5 | 37.3 | 26% | -0.047 | -0.030% | -0.042% | 42% | -0.43% | 115.8 | 0 | - | -0.111 | -0.059% |
| 518 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf M30 | 52.5 | 33% | -0.047 | -0.037% | -0.052% | 40% | -0.51% | 82.3 | 1 | -1.4% | +0.101 | +0.129% |
| 519 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf H1 | 45.0 | 39% | -0.047 | -0.028% | -0.038% | 32% | -0.37% | 95.9 | 1 | -1.1% | -0.149 | -0.056% |
| 520 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf M15 | 14.4 | 27% | -0.047 | -0.030% | -0.041% | 42% | -0.30% | 299.2 | 0 | - | +0.123 | +0.247% |
| 521 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf M30 | 52.5 | 28% | -0.047 | -0.035% | -0.049% | 47% | -0.42% | 82.3 | 1 | -1.3% | +0.021 | -0.008% |
| 522 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop all4, tf M30 | 11.3 | 38% | -0.047 | -0.028% | -0.038% | 56% | -0.36% | 381.1 | 0 | - | -0.102 | -0.078% |
| 523 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf M30 | 7.0 | 23% | -0.048 | -0.050% | -0.070% | 50% | -0.20% | 616.9 | 0 | - | -0.036 | -0.067% |
| 524 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf H1 | 3.2 | 43% | -0.048 | -0.047% | -0.065% | 50% | -0.08% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 525 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf M5 | 22.9 | 23% | -0.048 | -0.018% | -0.025% | 45% | -0.41% | 189.0 | 0 | - | -0.072 | -0.049% |
| 526 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf M5 | 5.9 | 24% | -0.048 | +0.020% | +0.028% | 40% | -0.60% | 727.7 | 0 | - | +0.000 | +0.000% |
| 527 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf M15 | 174.4 | 27% | -0.048 | -0.031% | -0.042% | 44% | -0.44% | 24.8 | 4 | -0.3%, -1.1%, -2.8%, +0.6% | -0.025 | -0.021% |
| 528 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf M5 | 14.7 | 23% | -0.048 | -0.024% | -0.034% | 33% | -0.34% | 293.6 | 0 | - | -0.102 | -0.046% |
| 529 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c34, tf H1 | 7.2 | 38% | -0.048 | -0.029% | -0.040% | 17% | -0.35% | 597.7 | 0 | - | -0.057 | +0.091% |
| 530 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c34, tf M15 | 15.2 | 35% | -0.049 | -0.031% | -0.043% | 42% | -0.51% | 283.8 | 0 | - | -0.035 | -0.035% |
| 531 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c34, tf M15 | 27.7 | 40% | -0.049 | -0.025% | -0.035% | 38% | -0.41% | 155.8 | 0 | - | +0.106 | +0.207% |
| 532 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf H1 | 44.6 | 36% | -0.049 | -0.027% | -0.037% | 31% | -0.40% | 96.9 | 1 | -1.8% | -0.234 | -0.067% |
| 533 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf H1 | 13.1 | 41% | -0.049 | -0.025% | -0.034% | 46% | -0.30% | 329.5 | 0 | - | -0.187 | -0.060% |
| 534 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c4, tf M30 | 11.4 | 39% | -0.049 | -0.031% | -0.044% | 50% | -0.41% | 377.3 | 0 | - | -0.115 | -0.083% |
| 535 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c34, tf M30 | 14.9 | 30% | -0.049 | -0.033% | -0.045% | 38% | -0.53% | 289.8 | 0 | - | -0.313 | -0.083% |
| 536 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf M15 | 87.6 | 29% | -0.050 | -0.031% | -0.044% | 42% | -0.43% | 49.3 | 2 | -1.2%, -1.3% | +0.019 | +0.015% |
| 537 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf M15 | 15.1 | 33% | -0.050 | -0.041% | -0.057% | 25% | -0.33% | 285.2 | 0 | - | +0.006 | -0.044% |
| 538 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf M30 | 54.3 | 34% | -0.050 | -0.037% | -0.051% | 40% | -0.39% | 79.5 | 1 | -1.2% | +0.000 | -0.011% |
| 539 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c34, tf M15 | 15.2 | 48% | -0.050 | -0.039% | -0.054% | 50% | -0.51% | 283.8 | 0 | - | -0.025 | -0.023% |
| 540 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf M5 | 35.7 | 22% | -0.051 | -0.028% | -0.039% | 48% | -0.38% | 121.0 | 0 | - | -0.103 | -0.057% |
| 541 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf M5 | 5.7 | 22% | -0.051 | +0.057% | +0.079% | 50% | -0.43% | 757.4 | 0 | - | +0.000 | +0.000% |
| 542 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf M15 | 174.7 | 30% | -0.051 | -0.033% | -0.045% | 42% | -0.42% | 24.7 | 4 | -0.3%, -1.5%, -2.4%, -0.0% | +0.004 | +0.003% |
| 543 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf H1 | 26.4 | 40% | -0.051 | -0.030% | -0.042% | 39% | -0.32% | 163.3 | 0 | - | -0.127 | -0.056% |
| 544 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf M5 | 21.9 | 24% | -0.051 | -0.063% | -0.087% | 21% | -0.23% | 196.9 | 0 | - | +0.004 | -0.041% |
| 545 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c34, tf H1 | 7.3 | 35% | -0.051 | -0.023% | -0.031% | 17% | -0.34% | 588.5 | 0 | - | -0.233 | -0.049% |
| 546 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop all4, tf M15 | 15.2 | 29% | -0.051 | -0.028% | -0.040% | 50% | -0.41% | 283.8 | 0 | - | -0.174 | -0.072% |
| 547 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf M15 | 44.7 | 24% | -0.051 | -0.034% | -0.047% | 30% | -0.29% | 96.6 | 1 | -1.1% | -0.136 | -0.059% |
| 548 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf H1 | 21.9 | 34% | -0.051 | -0.030% | -0.042% | 26% | -0.31% | 197.7 | 0 | - | -0.064 | -0.033% |
| 549 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf M30 | 54.3 | 30% | -0.052 | -0.036% | -0.050% | 40% | -0.41% | 79.5 | 1 | -1.3% | -0.009 | -0.010% |
| 550 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop all4, tf M30 | 14.9 | 39% | -0.052 | -0.040% | -0.055% | 46% | -0.49% | 289.8 | 0 | - | -0.311 | -0.084% |
| 551 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf M5 | 17.8 | 19% | -0.052 | -0.021% | -0.029% | 40% | -0.33% | 242.3 | 0 | - | -0.153 | -0.062% |
| 552 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf M15 | 88.2 | 23% | -0.052 | -0.034% | -0.048% | 33% | -0.36% | 49.0 | 2 | -0.7%, -1.4% | -0.034 | -0.028% |
| 553 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf M30 | 28.8 | 48% | -0.052 | -0.038% | -0.053% | 32% | -0.47% | 150.1 | 0 | - | -0.036 | -0.028% |
| 554 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf H1 | 21.6 | 34% | -0.052 | -0.033% | -0.046% | 42% | -0.37% | 199.7 | 0 | - | -0.036 | -0.024% |
| 555 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf M5 | 23.0 | 32% | -0.052 | -0.023% | -0.032% | 40% | -0.49% | 188.0 | 0 | - | -0.042 | -0.036% |
| 556 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c4, tf M15 | 14.7 | 43% | -0.053 | -0.027% | -0.038% | 42% | -0.35% | 293.1 | 0 | - | -0.064 | -0.045% |
| 557 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf M15 | 175.4 | 33% | -0.053 | -0.034% | -0.047% | 39% | -0.39% | 24.6 | 4 | -1.2%, -1.9%, -0.3%, -0.2% | +0.033 | +0.030% |
| 558 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf H1 | 26.4 | 37% | -0.053 | -0.027% | -0.038% | 44% | -0.34% | 163.3 | 0 | - | -0.187 | -0.057% |
| 559 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf M15 | 176.8 | 31% | -0.053 | -0.034% | -0.047% | 41% | -0.42% | 24.4 | 4 | -0.6%, -0.3%, -3.1%, -0.1% | -0.027 | -0.024% |
| 560 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf M30 | 94.7 | 47% | -0.053 | -0.032% | -0.045% | 46% | -0.63% | 45.6 | 2 | -1.5%, -0.6% | -0.019 | -0.015% |
| 561 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf M30 | 11.4 | 39% | -0.053 | -0.039% | -0.055% | 50% | -0.37% | 377.3 | 0 | - | -0.088 | -0.084% |
| 562 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf M5 | 19.7 | 25% | -0.054 | -0.017% | -0.024% | 53% | -0.41% | 219.6 | 0 | - | -0.043 | -0.017% |
| 563 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf M5 | 23.8 | 23% | -0.054 | -0.032% | -0.044% | 38% | -0.25% | 181.2 | 0 | - | -0.042 | -0.044% |
| 564 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf M5 | 19.6 | 19% | -0.054 | -0.056% | -0.077% | 18% | -0.17% | 220.1 | 0 | - | +0.057 | +0.048% |
| 565 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf M15 | 178.9 | 36% | -0.054 | -0.034% | -0.048% | 39% | -0.46% | 24.1 | 4 | -0.4%, -1.7%, -1.3%, -0.6% | +0.047 | +0.050% |
| 566 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf H1 | 13.0 | 28% | -0.054 | -0.035% | -0.049% | 36% | -0.30% | 332.3 | 0 | - | -0.083 | -0.044% |
| 567 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf H1 | 13.3 | 34% | -0.054 | -0.038% | -0.053% | 46% | -0.36% | 323.9 | 0 | - | -0.162 | -0.057% |
| 568 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf M30 | 11.4 | 37% | -0.054 | -0.036% | -0.050% | 30% | -0.36% | 377.3 | 0 | - | -0.082 | -0.084% |
| 569 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf H1 | 26.7 | 39% | -0.054 | -0.029% | -0.040% | 44% | -0.35% | 162.0 | 0 | - | -0.086 | -0.029% |
| 570 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf H1 | 26.4 | 28% | -0.054 | -0.029% | -0.041% | 35% | -0.36% | 163.3 | 0 | - | -0.225 | -0.069% |
| 571 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf M5 | 5.9 | 24% | -0.055 | +0.016% | +0.022% | 40% | -0.59% | 727.7 | 0 | - | +0.000 | +0.000% |
| 572 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf H1 | 44.9 | 36% | -0.055 | -0.036% | -0.050% | 35% | -0.33% | 96.2 | 1 | -1.6% | -0.181 | -0.062% |
| 573 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c4, tf M30 | 49.4 | 30% | -0.055 | -0.034% | -0.048% | 43% | -0.35% | 87.4 | 1 | -1.4% | -0.106 | -0.061% |
| 574 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf H1 | 22.1 | 34% | -0.055 | -0.033% | -0.046% | 32% | -0.40% | 195.7 | 0 | - | -0.024 | -0.010% |
| 575 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf M5 | 53.8 | 36% | -0.055 | -0.043% | -0.059% | 42% | -0.33% | 80.3 | 1 | -1.1% | +0.025 | +0.034% |
| 576 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop all4, tf M30 | 49.1 | 30% | -0.055 | -0.035% | -0.048% | 35% | -0.33% | 88.0 | 1 | -1.3% | -0.074 | -0.053% |
| 577 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf M5 | 37.3 | 22% | -0.055 | -0.032% | -0.044% | 33% | -0.36% | 115.8 | 0 | - | -0.097 | -0.057% |
| 578 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf M30 | 28.8 | 34% | -0.055 | -0.036% | -0.051% | 40% | -0.36% | 150.1 | 0 | - | -0.096 | -0.055% |
| 579 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop all4, tf M5 | 47.3 | 35% | -0.055 | -0.037% | -0.051% | 29% | -0.41% | 91.4 | 1 | -1.2% | -0.025 | -0.017% |
| 580 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf M15 | 87.6 | 26% | -0.055 | -0.033% | -0.046% | 41% | -0.37% | 49.3 | 2 | -0.7%, -1.5% | -0.013 | -0.013% |
| 581 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf H1 | 45.0 | 40% | -0.055 | -0.030% | -0.041% | 35% | -0.37% | 95.9 | 1 | -1.4% | -0.134 | -0.051% |
| 582 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop all4, tf M30 | 49.2 | 30% | -0.056 | -0.035% | -0.049% | 40% | -0.34% | 87.8 | 1 | -1.4% | -0.064 | -0.049% |
| 583 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf H1 | 26.0 | 35% | -0.056 | -0.027% | -0.037% | 30% | -0.34% | 166.1 | 0 | - | -0.258 | -0.072% |
| 584 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf M5 | 51.8 | 22% | -0.056 | -0.039% | -0.055% | 44% | -0.37% | 83.4 | 1 | -1.1% | -0.076 | -0.038% |
| 585 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf M5 | 5.8 | 26% | -0.056 | +0.047% | +0.065% | 40% | -0.44% | 742.3 | 0 | - | +0.000 | +0.000% |
| 586 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c4, tf M15 | 26.9 | 29% | -0.056 | -0.032% | -0.045% | 35% | -0.40% | 160.4 | 0 | - | +0.037 | +0.040% |
| 587 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c4, tf M15 | 15.0 | 48% | -0.056 | -0.033% | -0.046% | 50% | -0.46% | 288.4 | 0 | - | -0.038 | -0.030% |
| 588 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop all4, tf M15 | 15.8 | 40% | -0.056 | -0.040% | -0.056% | 46% | -0.43% | 272.8 | 0 | - | -0.073 | -0.038% |
| 589 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf M30 | 49.2 | 25% | -0.056 | -0.037% | -0.051% | 36% | -0.36% | 87.7 | 1 | -1.2% | -0.131 | -0.060% |
| 590 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf H1 | 5.7 | 40% | -0.056 | -0.067% | -0.093% | 0% | -0.19% | 754.8 | 0 | - | +0.092 | +1.189% |
| 591 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf H1 | 6.0 | 38% | -0.056 | -0.035% | -0.048% | 40% | -0.28% | 724.6 | 0 | - | +0.431 | +9.452% |
| 592 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf H1 | 44.5 | 34% | -0.056 | -0.029% | -0.041% | 38% | -0.39% | 97.1 | 1 | -2.1% | -0.117 | -0.051% |
| 593 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf M30 | 11.4 | 37% | -0.056 | -0.038% | -0.053% | 30% | -0.36% | 377.3 | 0 | - | -0.045 | -0.082% |
| 594 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf M5 | 25.2 | 21% | -0.057 | -0.044% | -0.061% | 32% | -0.29% | 171.5 | 0 | - | -0.040 | -0.045% |
| 595 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf M15 | 10.4 | 26% | -0.057 | -0.048% | -0.067% | 22% | -0.27% | 413.8 | 0 | - | +0.098 | +0.497% |
| 596 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf M30 | 28.1 | 29% | -0.057 | -0.036% | -0.050% | 46% | -0.43% | 153.7 | 0 | - | -0.061 | -0.050% |
| 597 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c4, tf H1 | 5.7 | 40% | -0.057 | -0.067% | -0.093% | 0% | -0.19% | 754.8 | 0 | - | +0.033 | +0.698% |
| 598 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf H1 | 44.8 | 44% | -0.057 | -0.029% | -0.041% | 42% | -0.50% | 96.4 | 1 | -1.5% | -0.152 | -0.054% |
| 599 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c4, tf M30 | 14.8 | 36% | -0.057 | -0.043% | -0.060% | 46% | -0.46% | 292.0 | 0 | - | -0.325 | -0.085% |
| 600 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c34, tf M30 | 49.2 | 30% | -0.057 | -0.035% | -0.049% | 40% | -0.36% | 87.8 | 1 | -1.4% | -0.075 | -0.052% |
| 601 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf M30 | 28.8 | 29% | -0.057 | -0.037% | -0.051% | 36% | -0.30% | 150.1 | 0 | - | -0.036 | -0.044% |
| 602 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop all4, tf M30 | 14.9 | 48% | -0.057 | -0.045% | -0.062% | 38% | -0.37% | 289.8 | 0 | - | -0.198 | -0.079% |
| 603 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf M5 | 24.6 | 21% | -0.058 | -0.045% | -0.063% | 32% | -0.29% | 175.4 | 0 | - | -0.012 | -0.032% |
| 604 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf M15 | 11.4 | 24% | -0.058 | -0.046% | -0.064% | 40% | -0.20% | 377.3 | 0 | - | +0.105 | +0.574% |
| 605 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf M30 | 7.8 | 27% | -0.058 | -0.049% | -0.068% | 43% | -0.32% | 554.3 | 0 | - | -0.042 | -0.072% |
| 606 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop all4, tf M30 | 14.9 | 33% | -0.058 | -0.044% | -0.061% | 38% | -0.36% | 289.8 | 0 | - | -0.268 | -0.071% |
| 607 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf M15 | 87.5 | 30% | -0.058 | -0.034% | -0.047% | 38% | -0.41% | 49.4 | 2 | -1.4%, -1.2% | +0.045 | +0.043% |
| 608 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c4, tf H1 | 22.1 | 32% | -0.058 | -0.032% | -0.045% | 37% | -0.42% | 195.7 | 0 | - | -0.076 | -0.038% |
| 609 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf M30 | 50.9 | 27% | -0.058 | -0.041% | -0.057% | 38% | -0.36% | 84.8 | 1 | -1.4% | -0.131 | -0.063% |
| 610 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf M30 | 49.2 | 21% | -0.058 | -0.036% | -0.050% | 32% | -0.28% | 87.7 | 1 | -0.9% | -0.093 | -0.052% |
| 611 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf M30 | 26.6 | 22% | -0.058 | -0.029% | -0.040% | 39% | -0.36% | 162.5 | 0 | - | -0.140 | -0.066% |
| 612 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf H1 | 5.7 | 38% | -0.059 | -0.047% | -0.065% | 25% | -0.27% | 754.8 | 0 | - | +0.434 | +8.694% |
| 613 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop all4, tf M30 | 11.4 | 39% | -0.059 | -0.034% | -0.048% | 50% | -0.42% | 377.3 | 0 | - | -0.124 | -0.081% |
| 614 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf M15 | 49.8 | 25% | -0.059 | -0.041% | -0.057% | 34% | -0.36% | 86.7 | 1 | -1.3% | -0.063 | -0.043% |
| 615 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf M15 | 174.6 | 28% | -0.059 | -0.038% | -0.052% | 42% | -0.40% | 24.7 | 4 | -0.6%, -1.1%, -2.4%, -0.8% | -0.014 | -0.014% |
| 616 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c34, tf M30 | 14.9 | 41% | -0.059 | -0.045% | -0.063% | 31% | -0.38% | 289.8 | 0 | - | -0.358 | -0.086% |
| 617 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf H1 | 21.6 | 36% | -0.059 | -0.032% | -0.045% | 53% | -0.42% | 199.7 | 0 | - | +0.008 | +0.015% |
| 618 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop all4, tf M30 | 14.7 | 30% | -0.059 | -0.040% | -0.056% | 38% | -0.47% | 294.2 | 0 | - | -0.326 | -0.084% |
| 619 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf H4 | 4.6 | 41% | -0.060 | -0.046% | -0.064% | 33% | -0.36% | 940.5 | 0 | - | +0.079 | +0.251% |
| 620 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf M5 | 49.8 | 22% | -0.060 | -0.040% | -0.056% | 36% | -0.36% | 86.8 | 1 | -1.0% | -0.121 | -0.052% |
| 621 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf M5 | 54.2 | 36% | -0.060 | -0.045% | -0.062% | 42% | -0.33% | 79.6 | 1 | -1.4% | +0.045 | +0.068% |
| 622 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c4, tf H1 | 7.2 | 36% | -0.060 | -0.026% | -0.037% | 17% | -0.30% | 597.7 | 0 | - | -0.230 | -0.050% |
| 623 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop all4, tf M5 | 45.5 | 28% | -0.060 | -0.035% | -0.049% | 42% | -0.35% | 95.0 | 1 | -1.7% | -0.044 | -0.025% |
| 624 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c34, tf M5 | 79.7 | 34% | -0.060 | -0.038% | -0.053% | 39% | -0.40% | 54.2 | 1 | -0.9% | -0.049 | -0.034% |
| 625 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf M15 | 7.2 | 32% | -0.060 | -0.043% | -0.060% | 20% | -0.17% | 598.2 | 0 | - | -0.145 | -0.070% |
| 626 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf M30 | 50.8 | 23% | -0.061 | -0.038% | -0.052% | 40% | -0.38% | 85.0 | 1 | -0.6% | +0.008 | -0.019% |
| 627 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c4, tf M30 | 48.4 | 29% | -0.061 | -0.037% | -0.052% | 42% | -0.33% | 89.2 | 1 | -1.2% | -0.076 | -0.055% |
| 628 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf H1 | 26.4 | 36% | -0.061 | -0.031% | -0.043% | 35% | -0.32% | 163.3 | 0 | - | -0.235 | -0.063% |
| 629 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf M5 | 53.6 | 24% | -0.061 | -0.042% | -0.059% | 42% | -0.35% | 80.6 | 1 | -1.0% | -0.150 | -0.058% |
| 630 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf H1 | 12.9 | 36% | -0.061 | -0.038% | -0.053% | 27% | -0.34% | 335.2 | 0 | - | -0.101 | -0.051% |
| 631 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf H1 | 26.7 | 38% | -0.061 | -0.032% | -0.045% | 35% | -0.31% | 162.0 | 0 | - | -0.177 | -0.052% |
| 632 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf H1 | 3.1 | 37% | -0.061 | -0.048% | -0.066% | 50% | -0.12% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 633 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf M15 | 87.9 | 32% | -0.062 | -0.036% | -0.051% | 42% | -0.39% | 49.2 | 2 | -2.3%, -0.0% | +0.043 | +0.042% |
| 634 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf M15 | 101.4 | 27% | -0.062 | -0.039% | -0.054% | 39% | -0.36% | 42.6 | 2 | -0.0%, -2.4% | -0.021 | -0.019% |
| 635 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf H1 | 21.5 | 36% | -0.062 | -0.032% | -0.044% | 32% | -0.34% | 200.8 | 0 | - | -0.071 | -0.042% |
| 636 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf M30 | 7.7 | 28% | -0.062 | -0.050% | -0.070% | 17% | -0.33% | 562.3 | 0 | - | -0.073 | -0.075% |
| 637 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf M30 | 52.6 | 22% | -0.062 | -0.039% | -0.054% | 32% | -0.29% | 82.1 | 1 | -1.5% | -0.073 | -0.046% |
| 638 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf M5 | 480.5 | 27% | -0.062 | -0.038% | -0.052% | 39% | -0.40% | 9.0 | 12 | -0.5%, -1.0%, -2.3%, +0.6%, -2.2%, +0.5%, -2.2%, -0.1%, -2.9%, -4.2%, -0.5%, -1.2% | -0.053 | -0.035% |
| 639 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf M5 | 25.3 | 20% | -0.062 | -0.052% | -0.073% | 23% | -0.20% | 170.7 | 0 | - | -0.022 | -0.032% |
| 640 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf M30 | 54.4 | 29% | -0.062 | -0.041% | -0.057% | 44% | -0.43% | 79.4 | 1 | -1.5% | -0.039 | -0.032% |
| 641 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf M5 | 24.7 | 20% | -0.063 | -0.052% | -0.072% | 27% | -0.21% | 174.6 | 0 | - | +0.011 | -0.011% |
| 642 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf M15 | 11.0 | 26% | -0.063 | -0.046% | -0.064% | 22% | -0.25% | 392.7 | 0 | - | +0.065 | +0.294% |
| 643 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf M30 | 5.6 | 49% | -0.063 | -0.058% | -0.081% | 50% | -0.33% | 766.8 | 0 | - | +0.000 | +0.000% |
| 644 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf H1 | 3.0 | 33% | -0.063 | -0.046% | -0.064% | 0% | -0.20% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 645 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf M15 | 10.9 | 26% | -0.063 | -0.052% | -0.072% | 22% | -0.22% | 396.7 | 0 | - | -0.119 | -0.028% |
| 646 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf M30 | 54.4 | 28% | -0.063 | -0.041% | -0.057% | 44% | -0.42% | 79.4 | 1 | -1.5% | +0.017 | -0.006% |
| 647 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf H1 | 45.1 | 44% | -0.063 | -0.032% | -0.044% | 48% | -0.46% | 95.7 | 1 | -1.6% | -0.074 | -0.031% |
| 648 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf M15 | 177.6 | 35% | -0.063 | -0.039% | -0.054% | 36% | -0.42% | 24.3 | 4 | -0.9%, -1.6%, -1.3%, -0.8% | +0.038 | +0.036% |
| 649 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf M30 | 7.0 | 18% | -0.064 | -0.032% | -0.045% | 33% | -0.20% | 616.9 | 0 | - | +0.169 | +0.126% |
| 650 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf M15 | 171.7 | 31% | -0.064 | -0.039% | -0.054% | 36% | -0.41% | 25.2 | 4 | -0.9%, -2.2%, -1.5%, -0.6% | +0.033 | +0.033% |
| 651 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf M30 | 50.9 | 21% | -0.064 | -0.037% | -0.052% | 33% | -0.30% | 84.8 | 1 | -1.2% | -0.110 | -0.056% |
| 652 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf M30 | 55.0 | 24% | -0.064 | -0.039% | -0.054% | 31% | -0.30% | 78.6 | 1 | -1.3% | -0.108 | -0.052% |
| 653 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf H1 | 45.0 | 44% | -0.064 | -0.032% | -0.045% | 42% | -0.40% | 95.9 | 1 | -1.9% | -0.122 | -0.048% |
| 654 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf M30 | 48.4 | 47% | -0.064 | -0.042% | -0.058% | 40% | -0.42% | 89.2 | 1 | -1.4% | +0.018 | +0.008% |
| 655 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf H1 | 44.9 | 37% | -0.065 | -0.034% | -0.047% | 40% | -0.40% | 96.2 | 1 | -1.7% | -0.153 | -0.051% |
| 656 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf H1 | 45.3 | 39% | -0.065 | -0.033% | -0.045% | 48% | -0.54% | 95.5 | 1 | -1.8% | -0.138 | -0.050% |
| 657 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf H1 | 3.2 | 43% | -0.065 | -0.046% | -0.064% | 50% | -0.09% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 658 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf M15 | 171.1 | 27% | -0.065 | -0.040% | -0.056% | 39% | -0.41% | 25.2 | 4 | -0.8%, -1.9%, -2.9%, -0.3% | +0.026 | +0.025% |
| 659 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf M15 | 39.7 | 21% | -0.065 | -0.039% | -0.055% | 29% | -0.27% | 108.9 | 0 | - | -0.149 | -0.060% |
| 660 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf M30 | 54.9 | 24% | -0.066 | -0.040% | -0.056% | 33% | -0.32% | 78.7 | 1 | -1.2% | -0.124 | -0.058% |
| 661 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf M5 | 470.9 | 23% | -0.066 | -0.040% | -0.056% | 35% | -0.50% | 9.2 | 11 | -0.4%, -1.7%, -3.6%, -0.8%, -2.8%, -0.4%, -1.8%, -0.9%, -0.5%, -2.6%, -0.8% | -0.040 | -0.027% |
| 662 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf M15 | 177.1 | 32% | -0.066 | -0.040% | -0.055% | 40% | -0.43% | 24.4 | 4 | -0.6%, -0.3%, -3.4%, -0.7% | -0.014 | -0.013% |
| 663 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf M30 | 28.7 | 46% | -0.066 | -0.040% | -0.055% | 44% | -0.34% | 150.7 | 0 | - | -0.016 | -0.020% |
| 664 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf M30 | 5.6 | 45% | -0.066 | -0.035% | -0.049% | 25% | -0.42% | 766.8 | 0 | - | +0.000 | +0.000% |
| 665 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf M15 | 87.5 | 27% | -0.066 | -0.037% | -0.051% | 40% | -0.35% | 49.4 | 2 | -1.0%, -1.6% | +0.001 | -0.007% |
| 666 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf M15 | 14.4 | 33% | -0.067 | -0.047% | -0.065% | 33% | -0.29% | 299.2 | 0 | - | -0.040 | -0.053% |
| 667 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf H1 | 12.9 | 38% | -0.067 | -0.037% | -0.051% | 46% | -0.34% | 335.2 | 0 | - | -0.020 | -0.029% |
| 668 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf H1 | 44.6 | 36% | -0.067 | -0.035% | -0.049% | 33% | -0.38% | 96.9 | 1 | -2.0% | -0.202 | -0.062% |
| 669 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.067 | -0.079% | -0.109% | 33% | -0.13% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 670 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf M5 | 39.4 | 26% | -0.067 | -0.039% | -0.054% | 32% | -0.39% | 109.5 | 0 | - | -0.075 | -0.047% |
| 671 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c34, tf M5 | 79.6 | 28% | -0.067 | -0.039% | -0.055% | 38% | -0.40% | 54.3 | 1 | -0.7% | +0.004 | -0.002% |
| 672 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf M30 | 28.6 | 47% | -0.067 | -0.041% | -0.058% | 44% | -0.41% | 151.3 | 0 | - | +0.037 | +0.017% |
| 673 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf M5 | 119.4 | 22% | -0.067 | -0.039% | -0.055% | 29% | -0.33% | 36.2 | 2 | -0.3%, -0.6% | -0.117 | -0.054% |
| 674 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf M5 | 53.0 | 34% | -0.067 | -0.047% | -0.066% | 43% | -0.33% | 81.5 | 1 | -1.1% | +0.046 | +0.068% |
| 675 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf M15 | 177.7 | 34% | -0.067 | -0.040% | -0.056% | 35% | -0.37% | 24.3 | 4 | -0.9%, -1.8%, -1.1%, -1.3% | +0.016 | +0.009% |
| 676 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf M5 | 248.7 | 27% | -0.067 | -0.039% | -0.055% | 40% | -0.42% | 17.4 | 6 | -1.2%, -1.2%, -1.9%, -1.2%, -2.1%, -0.8% | -0.030 | -0.022% |
| 677 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c34, tf M15 | 15.2 | 30% | -0.067 | -0.036% | -0.049% | 42% | -0.43% | 283.8 | 0 | - | -0.010 | -0.024% |
| 678 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf H1 | 21.6 | 34% | -0.067 | -0.038% | -0.052% | 21% | -0.33% | 199.7 | 0 | - | -0.049 | -0.032% |
| 679 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf H1 | 5.6 | 38% | -0.067 | -0.069% | -0.096% | 0% | -0.17% | 770.9 | 0 | - | +0.151 | +1.951% |
| 680 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf H1 | 13.2 | 33% | -0.068 | -0.049% | -0.067% | 27% | -0.35% | 326.7 | 0 | - | -0.120 | -0.050% |
| 681 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf M30 | 54.4 | 34% | -0.068 | -0.046% | -0.063% | 42% | -0.35% | 79.4 | 1 | -1.8% | -0.144 | -0.061% |
| 682 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf M30 | 54.4 | 32% | -0.068 | -0.044% | -0.062% | 44% | -0.44% | 79.4 | 1 | -1.2% | +0.018 | +0.003% |
| 683 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c34, tf M30 | 11.4 | 39% | -0.068 | -0.040% | -0.055% | 50% | -0.38% | 377.3 | 0 | - | -0.136 | -0.084% |
| 684 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c34, tf M5 | 13.1 | 34% | -0.068 | -0.027% | -0.038% | 64% | -0.51% | 328.5 | 0 | - | -0.225 | -0.074% |
| 685 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf M5 | 52.7 | 22% | -0.068 | -0.044% | -0.061% | 40% | -0.34% | 82.0 | 1 | -1.2% | -0.068 | -0.034% |
| 686 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf M15 | 88.0 | 33% | -0.068 | -0.038% | -0.052% | 38% | -0.38% | 49.1 | 2 | -2.2%, -0.3% | +0.055 | +0.052% |
| 687 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c4, tf M5 | 46.0 | 28% | -0.068 | -0.042% | -0.059% | 35% | -0.41% | 93.9 | 1 | -1.4% | -0.022 | -0.014% |
| 688 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf M5 | 23.4 | 27% | -0.069 | -0.062% | -0.086% | 25% | -0.28% | 184.6 | 0 | - | +0.044 | -0.003% |
| 689 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf M5 | 54.1 | 27% | -0.069 | -0.044% | -0.061% | 46% | -0.38% | 79.8 | 1 | -1.5% | -0.079 | -0.044% |
| 690 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c4, tf M15 | 14.7 | 25% | -0.069 | -0.036% | -0.050% | 42% | -0.38% | 293.1 | 0 | - | -0.154 | -0.070% |
| 691 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf M15 | 90.3 | 35% | -0.069 | -0.039% | -0.054% | 40% | -0.44% | 47.8 | 2 | -2.5%, -0.3% | +0.080 | +0.087% |
| 692 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c34, tf M30 | 11.3 | 37% | -0.069 | -0.039% | -0.054% | 56% | -0.37% | 381.1 | 0 | - | -0.127 | -0.084% |
| 693 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf M5 | 483.2 | 33% | -0.069 | -0.040% | -0.056% | 38% | -0.47% | 8.9 | 12 | -0.4%, +0.2%, -2.6%, +0.4%, -2.6%, -0.5%, -2.3%, +0.2%, -2.9%, -3.8%, -1.2%, -1.8% | -0.072 | -0.042% |
| 694 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf M15 | 15.4 | 28% | -0.069 | -0.041% | -0.057% | 46% | -0.30% | 280.8 | 0 | - | +0.228 | +0.908% |
| 695 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c4, tf H1 | 7.2 | 36% | -0.069 | -0.050% | -0.069% | 33% | -0.29% | 597.7 | 0 | - | -0.344 | -0.084% |
| 696 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf M5 | 25.3 | 30% | -0.069 | -0.061% | -0.085% | 27% | -0.28% | 170.7 | 0 | - | +0.059 | -0.001% |
| 697 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf M15 | 7.7 | 32% | -0.069 | -0.050% | -0.069% | 33% | -0.30% | 560.2 | 0 | - | -0.153 | -0.076% |
| 698 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf M5 | 4.4 | 26% | -0.069 | +0.019% | +0.026% | 33% | -0.25% | 976.7 | 0 | - | +0.000 | +0.000% |
| 699 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c4, tf M15 | 4.2 | 25% | -0.069 | +0.099% | +0.137% | 33% | -0.42% | 1029.8 | 0 | - | +0.167 | +0.393% |
| 700 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf M30 | 54.3 | 28% | -0.069 | -0.043% | -0.060% | 42% | -0.40% | 79.5 | 1 | -1.6% | -0.027 | -0.023% |
| 701 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf M5 | 23.5 | 20% | -0.069 | -0.054% | -0.076% | 24% | -0.24% | 183.7 | 0 | - | +0.006 | -0.012% |
| 702 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf M5 | 52.9 | 25% | -0.069 | -0.044% | -0.062% | 40% | -0.37% | 81.6 | 1 | -1.2% | -0.057 | -0.033% |
| 703 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf H1 | 45.5 | 44% | -0.069 | -0.035% | -0.049% | 40% | -0.45% | 95.0 | 1 | -1.7% | -0.091 | -0.040% |
| 704 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf M15 | 175.9 | 34% | -0.070 | -0.041% | -0.057% | 34% | -0.36% | 24.6 | 4 | -1.4%, -1.9%, -0.6%, -1.1% | +0.033 | +0.031% |
| 705 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf M30 | 54.4 | 45% | -0.070 | -0.047% | -0.065% | 38% | -0.43% | 79.4 | 1 | -1.9% | -0.013 | -0.013% |
| 706 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf M30 | 54.5 | 32% | -0.070 | -0.047% | -0.065% | 41% | -0.40% | 79.2 | 1 | -1.6% | -0.120 | -0.056% |
| 707 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf M30 | 28.8 | 36% | -0.070 | -0.046% | -0.063% | 44% | -0.33% | 150.1 | 0 | - | -0.284 | -0.075% |
| 708 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf H1 | 12.9 | 26% | -0.070 | -0.043% | -0.060% | 36% | -0.31% | 335.2 | 0 | - | -0.049 | -0.026% |
| 709 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop all4, tf M5 | 47.3 | 29% | -0.070 | -0.041% | -0.057% | 36% | -0.43% | 91.4 | 1 | -1.1% | +0.011 | +0.018% |
| 710 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf M15 | 11.6 | 18% | -0.070 | -0.052% | -0.073% | 40% | -0.26% | 373.6 | 0 | - | +0.121 | +0.889% |
| 711 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf M15 | 86.5 | 30% | -0.070 | -0.040% | -0.055% | 39% | -0.42% | 49.9 | 2 | -2.5%, -0.5% | +0.045 | +0.044% |
| 712 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf M15 | 10.3 | 18% | -0.070 | -0.048% | -0.067% | 33% | -0.27% | 418.3 | 0 | - | +0.167 | +0.865% |
| 713 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf M15 | 174.7 | 34% | -0.070 | -0.040% | -0.056% | 44% | -0.42% | 24.7 | 4 | -0.4%, -2.0%, -2.5%, -0.5% | +0.001 | -0.000% |
| 714 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf H1 | 21.5 | 42% | -0.070 | -0.034% | -0.047% | 32% | -0.28% | 200.8 | 0 | - | -0.023 | -0.022% |
| 715 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf M5 | 246.6 | 27% | -0.070 | -0.042% | -0.058% | 36% | -0.44% | 17.5 | 6 | -1.1%, -2.4%, -1.3%, -1.0%, -2.3%, -0.7% | -0.046 | -0.030% |
| 716 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf M5 | 249.1 | 33% | -0.070 | -0.041% | -0.057% | 38% | -0.47% | 17.3 | 6 | -0.6%, -1.8%, -1.5%, -1.9%, -1.5%, -1.1% | -0.060 | -0.036% |
| 717 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop all4, tf M5 | 80.6 | 34% | -0.070 | -0.041% | -0.058% | 36% | -0.48% | 53.6 | 2 | -1.2%, -2.0% | -0.034 | -0.027% |
| 718 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c34, tf M30 | 49.2 | 29% | -0.070 | -0.041% | -0.057% | 33% | -0.32% | 87.8 | 1 | -1.5% | -0.090 | -0.057% |
| 719 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf M5 | 19.7 | 20% | -0.070 | -0.028% | -0.039% | 41% | -0.35% | 219.6 | 0 | - | -0.118 | -0.044% |
| 720 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf M5 | 479.8 | 27% | -0.070 | -0.041% | -0.057% | 38% | -0.38% | 9.0 | 11 | -0.5%, -0.6%, -3.1%, -0.3%, -2.4%, +0.9%, -2.8%, -0.6%, -2.7%, -3.4%, -0.9% | -0.056 | -0.035% |
| 721 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop all4, tf M15 | 20.5 | 26% | -0.071 | -0.045% | -0.062% | 22% | -0.23% | 210.3 | 0 | - | +0.081 | +0.337% |
| 722 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf M30 | 49.1 | 46% | -0.071 | -0.040% | -0.056% | 35% | -0.46% | 88.0 | 1 | -1.5% | -0.006 | -0.022% |
| 723 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf M5 | 241.0 | 22% | -0.071 | -0.040% | -0.055% | 37% | -0.33% | 17.9 | 6 | -1.1%, -0.0%, -0.1%, -0.8%, -4.0%, -2.6% | -0.114 | -0.055% |
| 724 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf M5 | 242.6 | 23% | -0.071 | -0.041% | -0.057% | 34% | -0.42% | 17.8 | 6 | -2.4%, -2.3%, -2.4%, -0.1%, -1.9%, -0.1% | -0.007 | -0.004% |
| 725 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop all4, tf M30 | 14.7 | 40% | -0.071 | -0.049% | -0.068% | 31% | -0.36% | 294.2 | 0 | - | -0.383 | -0.088% |
| 726 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c34, tf M30 | 14.7 | 29% | -0.071 | -0.052% | -0.072% | 54% | -0.39% | 294.2 | 0 | - | -0.226 | -0.084% |
| 727 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf M5 | 119.5 | 25% | -0.072 | -0.041% | -0.056% | 40% | -0.36% | 36.2 | 2 | -0.9%, -0.9% | -0.128 | -0.057% |
| 728 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf M5 | 17.8 | 24% | -0.072 | -0.030% | -0.041% | 47% | -0.32% | 242.3 | 0 | - | -0.087 | -0.052% |
| 729 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf M5 | 484.8 | 33% | -0.072 | -0.042% | -0.058% | 38% | -0.45% | 8.9 | 12 | -0.5%, +0.1%, -2.5%, +0.5%, -2.4%, -0.5%, -2.3%, -0.2%, -2.8%, -3.6%, -1.9%, -1.7% | -0.065 | -0.040% |
| 730 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c4, tf M15 | 15.2 | 39% | -0.072 | -0.043% | -0.060% | 50% | -0.40% | 283.8 | 0 | - | -0.095 | -0.048% |
| 731 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf M30 | 54.4 | 30% | -0.072 | -0.044% | -0.060% | 40% | -0.39% | 79.4 | 1 | -1.4% | -0.013 | -0.014% |
| 732 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf M15 | 171.0 | 25% | -0.072 | -0.042% | -0.058% | 38% | -0.39% | 25.3 | 4 | -0.8%, -1.8%, -2.8%, -0.5% | -0.011 | -0.012% |
| 733 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf H1 | 5.7 | 38% | -0.072 | -0.053% | -0.073% | 25% | -0.27% | 754.8 | 0 | - | +0.442 | +10.070% |
| 734 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf M5 | 473.3 | 26% | -0.072 | -0.042% | -0.058% | 38% | -0.53% | 9.1 | 11 | -0.9%, -0.7%, -3.7%, -0.5%, -2.9%, -0.3%, -1.5%, -0.7%, -1.1%, -2.8%, -1.9% | -0.069 | -0.041% |
| 735 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf M15 | 175.6 | 29% | -0.072 | -0.043% | -0.060% | 37% | -0.36% | 24.6 | 4 | -0.8%, -0.8%, -2.6%, -1.2% | -0.011 | -0.012% |
| 736 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf M5 | 478.5 | 24% | -0.073 | -0.042% | -0.059% | 37% | -0.35% | 9.0 | 11 | -0.6%, -1.6%, -2.3%, +0.8%, -2.1%, +0.0%, -2.7%, -1.1%, -2.3%, -3.6%, -1.1% | -0.063 | -0.039% |
| 737 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf H1 | 44.9 | 39% | -0.073 | -0.036% | -0.050% | 42% | -0.40% | 96.2 | 1 | -1.7% | -0.119 | -0.041% |
| 738 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf M15 | 86.3 | 27% | -0.073 | -0.039% | -0.054% | 40% | -0.36% | 50.1 | 2 | -2.0%, -1.6% | +0.047 | +0.048% |
| 739 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf H1 | 13.3 | 34% | -0.073 | -0.047% | -0.065% | 36% | -0.31% | 323.9 | 0 | - | -0.138 | -0.054% |
| 740 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf M5 | 54.5 | 36% | -0.073 | -0.050% | -0.069% | 42% | -0.32% | 79.3 | 1 | -1.6% | +0.042 | +0.061% |
| 741 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c4, tf M30 | 8.3 | 32% | -0.073 | -0.062% | -0.086% | 29% | -0.26% | 518.1 | 0 | - | -0.284 | -0.068% |
| 742 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf H1 | 21.6 | 34% | -0.073 | -0.039% | -0.054% | 26% | -0.33% | 199.7 | 0 | - | -0.021 | -0.014% |
| 743 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf M5 | 21.2 | 28% | -0.073 | -0.031% | -0.044% | 28% | -0.41% | 204.2 | 0 | - | -0.052 | -0.033% |
| 744 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf M5 | 457.5 | 22% | -0.073 | -0.042% | -0.058% | 35% | -0.50% | 9.4 | 11 | -0.2%, -1.8%, -4.3%, -1.7%, -1.0%, -1.2%, -1.4%, -0.5%, -0.3%, -2.6%, -1.3% | -0.038 | -0.027% |
| 745 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf M5 | 52.9 | 31% | -0.073 | -0.049% | -0.067% | 38% | -0.30% | 81.6 | 1 | -1.7% | -0.046 | -0.037% |
| 746 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf H1 | 45.7 | 36% | -0.073 | -0.045% | -0.062% | 30% | -0.33% | 94.5 | 1 | -2.3% | -0.305 | -0.074% |
| 747 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf M15 | 10.3 | 24% | -0.073 | -0.059% | -0.082% | 22% | -0.30% | 418.3 | 0 | - | -0.090 | -0.013% |
| 748 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf M30 | 5.5 | 29% | -0.073 | -0.014% | -0.020% | 25% | -0.34% | 782.7 | 0 | - | +0.000 | +0.000% |
| 749 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf M15 | 101.9 | 33% | -0.073 | -0.044% | -0.061% | 34% | -0.34% | 42.4 | 2 | -0.5%, -2.6% | -0.026 | -0.023% |
| 750 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c4, tf M15 | 14.7 | 33% | -0.073 | -0.042% | -0.059% | 33% | -0.42% | 293.1 | 0 | - | -0.041 | -0.037% |
| 751 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c34, tf M15 | 15.2 | 38% | -0.074 | -0.037% | -0.051% | 58% | -0.38% | 283.8 | 0 | - | -0.065 | -0.035% |
| 752 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf M15 | 46.7 | 28% | -0.074 | -0.043% | -0.060% | 32% | -0.34% | 92.5 | 1 | -1.9% | -0.202 | -0.069% |
| 753 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf H1 | 3.2 | 39% | -0.074 | -0.057% | -0.079% | 50% | -0.09% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 754 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf M5 | 37.5 | 30% | -0.074 | -0.044% | -0.061% | 39% | -0.29% | 115.2 | 0 | - | -0.068 | -0.041% |
| 755 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop all4, tf M5 | 481.6 | 28% | -0.074 | -0.042% | -0.058% | 37% | -0.42% | 9.0 | 12 | -0.3%, -1.8%, -2.9%, +0.3%, -2.3%, +0.3%, -1.5%, -0.6%, -2.6%, -3.7%, -0.9%, -1.9% | -0.052 | -0.034% |
| 756 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c34, tf M15 | 4.2 | 25% | -0.074 | +0.042% | +0.058% | 0% | -0.28% | 1029.8 | 0 | - | +0.210 | +0.846% |
| 757 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf M5 | 19.7 | 27% | -0.075 | -0.030% | -0.041% | 35% | -0.37% | 219.6 | 0 | - | -0.088 | -0.048% |
| 758 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf M5 | 250.0 | 33% | -0.075 | -0.044% | -0.060% | 40% | -0.45% | 17.3 | 6 | -0.1%, -2.3%, -1.7%, -2.1%, -1.1%, -1.7% | -0.040 | -0.027% |
| 759 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop all4, tf M15 | 15.2 | 30% | -0.075 | -0.044% | -0.062% | 33% | -0.36% | 283.8 | 0 | - | -0.051 | -0.047% |
| 760 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c4, tf M5 | 43.5 | 22% | -0.075 | -0.041% | -0.057% | 40% | -0.33% | 99.2 | 1 | -1.3% | -0.012 | -0.004% |
| 761 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf M5 | 477.9 | 24% | -0.075 | -0.042% | -0.058% | 35% | -0.39% | 9.0 | 11 | -0.4%, -1.1%, -3.3%, -0.4%, -2.0%, +0.3%, -2.7%, -1.4%, -2.1%, -3.2%, -0.8% | -0.059 | -0.036% |
| 762 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf M15 | 177.2 | 35% | -0.075 | -0.041% | -0.057% | 41% | -0.45% | 24.4 | 4 | -0.3%, -1.6%, -3.4%, -0.2% | +0.006 | +0.004% |
| 763 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf M30 | 55.3 | 24% | -0.075 | -0.044% | -0.061% | 31% | -0.32% | 78.1 | 1 | -1.4% | -0.102 | -0.051% |
| 764 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c4, tf M30 | 11.2 | 37% | -0.075 | -0.041% | -0.057% | 56% | -0.35% | 385.0 | 0 | - | -0.087 | -0.081% |
| 765 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop all4, tf H1 | 7.2 | 44% | -0.075 | -0.036% | -0.050% | 33% | -0.37% | 597.7 | 0 | - | -0.070 | +0.081% |
| 766 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf M15 | 11.3 | 20% | -0.075 | -0.053% | -0.074% | 30% | -0.26% | 381.0 | 0 | - | +0.129 | +0.808% |
| 767 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf M15 | 7.8 | 27% | -0.075 | -0.045% | -0.063% | 33% | -0.24% | 551.4 | 0 | - | +0.101 | +0.509% |
| 768 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf M15 | 77.1 | 23% | -0.075 | -0.043% | -0.059% | 26% | -0.28% | 56.0 | 1 | -1.6% | -0.075 | -0.048% |
| 769 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop all4, tf H1 | 21.5 | 31% | -0.076 | -0.044% | -0.061% | 42% | -0.32% | 200.8 | 0 | - | -0.122 | -0.054% |
| 770 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf M5 | 243.1 | 26% | -0.076 | -0.043% | -0.059% | 35% | -0.52% | 17.8 | 6 | -1.7%, -2.5%, -1.9%, -0.0%, -2.5%, -0.9% | -0.031 | -0.021% |
| 771 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop all4, tf M15 | 4.1 | 39% | -0.076 | -0.072% | -0.099% | 0% | -0.14% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 772 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf H1 | 45.3 | 36% | -0.076 | -0.040% | -0.055% | 40% | -0.46% | 95.5 | 1 | -1.7% | -0.172 | -0.057% |
| 773 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c4, tf H1 | 7.2 | 44% | -0.076 | -0.036% | -0.049% | 33% | -0.39% | 597.7 | 0 | - | +0.030 | +0.276% |
| 774 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf M5 | 147.4 | 20% | -0.076 | -0.047% | -0.066% | 33% | -0.27% | 29.3 | 3 | -1.8%, -0.1%, -2.9% | -0.124 | -0.061% |
| 775 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop all4, tf M5 | 77.5 | 27% | -0.076 | -0.043% | -0.060% | 35% | -0.38% | 55.8 | 1 | -1.4% | -0.041 | -0.030% |
| 776 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf M15 | 176.1 | 28% | -0.076 | -0.044% | -0.061% | 40% | -0.38% | 24.5 | 4 | -0.4%, -1.7%, -2.6%, -0.6% | -0.017 | -0.016% |
| 777 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop all4, tf M15 | 15.3 | 39% | -0.077 | -0.044% | -0.061% | 42% | -0.39% | 281.5 | 0 | - | -0.045 | -0.021% |
| 778 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf H1 | 44.9 | 37% | -0.077 | -0.040% | -0.056% | 38% | -0.37% | 96.2 | 1 | -1.7% | -0.158 | -0.053% |
| 779 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop all4, tf M15 | 21.3 | 26% | -0.077 | -0.045% | -0.063% | 32% | -0.20% | 202.5 | 0 | - | +0.106 | +0.417% |
| 780 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf M5 | 105.2 | 25% | -0.077 | -0.045% | -0.063% | 34% | -0.31% | 41.0 | 2 | -1.8%, -1.7% | -0.123 | -0.058% |
| 781 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf H1 | 45.3 | 37% | -0.077 | -0.039% | -0.055% | 35% | -0.48% | 95.5 | 1 | -2.0% | -0.190 | -0.059% |
| 782 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf M5 | 5.8 | 28% | -0.077 | -0.031% | -0.043% | 20% | -0.26% | 742.3 | 0 | - | +0.000 | +0.000% |
| 783 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c34, tf M15 | 27.0 | 27% | -0.077 | -0.045% | -0.062% | 39% | -0.33% | 159.8 | 0 | - | -0.148 | -0.068% |
| 784 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf M30 | 94.5 | 46% | -0.077 | -0.045% | -0.062% | 35% | -0.57% | 45.7 | 2 | -2.2%, -1.0% | +0.010 | +0.003% |
| 785 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c34, tf M15 | 15.2 | 26% | -0.077 | -0.041% | -0.057% | 33% | -0.35% | 283.8 | 0 | - | -0.169 | -0.072% |
| 786 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf M5 | 33.3 | 21% | -0.077 | -0.042% | -0.058% | 34% | -0.27% | 129.6 | 0 | - | -0.126 | -0.065% |
| 787 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop all4, tf M30 | 14.9 | 30% | -0.077 | -0.044% | -0.060% | 38% | -0.46% | 289.8 | 0 | - | -0.311 | -0.083% |
| 788 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf H1 | 5.6 | 43% | -0.077 | -0.065% | -0.090% | 0% | -0.21% | 770.9 | 0 | - | +0.288 | +2.486% |
| 789 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf M5 | 4.4 | 21% | -0.078 | +0.053% | +0.074% | 67% | -0.46% | 976.7 | 0 | - | +0.000 | +0.000% |
| 790 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf M5 | 24.7 | 28% | -0.078 | -0.063% | -0.088% | 27% | -0.26% | 174.6 | 0 | - | +0.055 | -0.006% |
| 791 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf M15 | 46.5 | 22% | -0.078 | -0.045% | -0.063% | 42% | -0.31% | 92.9 | 1 | -1.5% | -0.044 | -0.023% |
| 792 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf M5 | 246.2 | 23% | -0.078 | -0.045% | -0.063% | 33% | -0.35% | 17.5 | 6 | -1.5%, -2.4%, -1.9%, -0.9%, -2.2%, -0.8% | -0.051 | -0.033% |
| 793 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c34, tf H1 | 44.7 | 34% | -0.078 | -0.038% | -0.053% | 32% | -0.38% | 96.6 | 1 | -2.2% | -0.163 | -0.058% |
| 794 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop all4, tf M5 | 77.5 | 24% | -0.079 | -0.042% | -0.058% | 35% | -0.33% | 55.8 | 1 | -0.9% | +0.006 | +0.001% |
| 795 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf H1 | 3.3 | 42% | -0.079 | -0.030% | -0.042% | 0% | -0.21% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 796 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf M5 | 233.2 | 21% | -0.079 | -0.044% | -0.061% | 32% | -0.32% | 18.5 | 5 | -0.8%, -2.1%, -0.0%, -1.1%, -3.3% | -0.126 | -0.060% |
| 797 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf M5 | 248.0 | 24% | -0.079 | -0.045% | -0.062% | 34% | -0.34% | 17.4 | 6 | -1.5%, -1.3%, -1.9%, -2.0%, -2.0%, -0.7% | -0.046 | -0.031% |
| 798 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf M5 | 249.2 | 27% | -0.079 | -0.045% | -0.062% | 36% | -0.38% | 17.3 | 6 | -1.4%, -2.0%, -1.9%, -1.4%, -1.3%, -1.2% | -0.022 | -0.017% |
| 799 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf M30 | 28.7 | 37% | -0.079 | -0.049% | -0.067% | 40% | -0.26% | 150.7 | 0 | - | -0.259 | -0.074% |
| 800 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c34, tf M5 | 79.6 | 25% | -0.079 | -0.043% | -0.060% | 38% | -0.34% | 54.3 | 1 | -0.3% | +0.025 | +0.018% |
| 801 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf M30 | 49.1 | 24% | -0.079 | -0.048% | -0.066% | 30% | -0.37% | 87.9 | 1 | -1.2% | -0.025 | -0.030% |
| 802 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c34, tf M5 | 46.5 | 25% | -0.079 | -0.044% | -0.062% | 39% | -0.36% | 93.0 | 1 | -1.1% | +0.011 | +0.012% |
| 803 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf H1 | 5.7 | 42% | -0.079 | -0.057% | -0.080% | 25% | -0.21% | 754.8 | 0 | - | +0.206 | +4.627% |
| 804 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf M5 | 4.4 | 24% | -0.079 | +0.019% | +0.027% | 33% | -0.29% | 976.7 | 0 | - | +0.000 | +0.000% |
| 805 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop all4, tf M5 | 45.5 | 25% | -0.079 | -0.043% | -0.060% | 40% | -0.34% | 95.0 | 1 | -1.4% | -0.004 | +0.004% |
| 806 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf M15 | 175.8 | 31% | -0.080 | -0.045% | -0.063% | 36% | -0.40% | 24.6 | 4 | -0.8%, -0.7%, -2.9%, -1.6% | -0.005 | -0.007% |
| 807 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf M15 | 174.6 | 33% | -0.080 | -0.043% | -0.059% | 42% | -0.44% | 24.7 | 4 | -1.1%, -2.1%, -2.6%, +0.1% | +0.030 | +0.028% |
| 808 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf H1 | 21.6 | 35% | -0.080 | -0.041% | -0.057% | 32% | -0.33% | 199.7 | 0 | - | -0.000 | +0.001% |
| 809 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf M30 | 7.7 | 26% | -0.080 | -0.054% | -0.075% | 33% | -0.25% | 560.8 | 0 | - | -0.095 | -0.078% |
| 810 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c4, tf M5 | 12.4 | 23% | -0.080 | -0.035% | -0.048% | 50% | -0.38% | 349.6 | 0 | - | -0.394 | -0.091% |
| 811 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c4, tf M5 | 78.7 | 24% | -0.080 | -0.043% | -0.059% | 33% | -0.33% | 54.9 | 1 | -0.3% | +0.021 | +0.015% |
| 812 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf M5 | 23.4 | 30% | -0.081 | -0.057% | -0.080% | 40% | -0.33% | 184.6 | 0 | - | -0.024 | -0.017% |
| 813 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf M5 | 5.8 | 28% | -0.081 | -0.030% | -0.042% | 20% | -0.28% | 742.3 | 0 | - | +0.000 | +0.000% |
| 814 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c34, tf M15 | 4.2 | 38% | -0.081 | -0.068% | -0.095% | 0% | -0.15% | 1029.8 | 0 | - | +0.104 | +0.167% |
| 815 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf M5 | 14.7 | 18% | -0.081 | -0.039% | -0.054% | 25% | -0.29% | 293.6 | 0 | - | -0.123 | -0.043% |
| 816 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf M30 | 28.1 | 46% | -0.081 | -0.050% | -0.070% | 25% | -0.28% | 153.7 | 0 | - | -0.096 | -0.055% |
| 817 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf M5 | 51.8 | 24% | -0.081 | -0.048% | -0.067% | 44% | -0.32% | 83.4 | 1 | -1.2% | -0.041 | -0.026% |
| 818 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf M5 | 33.3 | 24% | -0.081 | -0.042% | -0.058% | 31% | -0.29% | 129.6 | 0 | - | -0.056 | -0.038% |
| 819 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf M15 | 95.0 | 23% | -0.081 | -0.046% | -0.064% | 38% | -0.33% | 45.5 | 2 | -1.3%, -1.8% | -0.025 | -0.019% |
| 820 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf M30 | 26.6 | 28% | -0.081 | -0.045% | -0.062% | 30% | -0.26% | 162.5 | 0 | - | -0.326 | -0.080% |
| 821 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf M30 | 54.4 | 34% | -0.081 | -0.047% | -0.066% | 42% | -0.40% | 79.4 | 1 | -1.9% | +0.008 | -0.011% |
| 822 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf M15 | 89.0 | 34% | -0.082 | -0.043% | -0.059% | 39% | -0.36% | 48.6 | 2 | -2.5%, -0.7% | +0.062 | +0.055% |
| 823 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf H1 | 27.0 | 29% | -0.082 | -0.040% | -0.056% | 25% | -0.29% | 159.9 | 0 | - | -0.257 | -0.072% |
| 824 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c34, tf M5 | 54.7 | 26% | -0.082 | -0.051% | -0.070% | 31% | -0.27% | 79.0 | 1 | -2.1% | -0.061 | -0.040% |
| 825 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c34, tf M30 | 14.9 | 34% | -0.082 | -0.057% | -0.080% | 46% | -0.39% | 289.8 | 0 | - | -0.249 | -0.082% |
| 826 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf M5 | 114.8 | 20% | -0.082 | -0.045% | -0.063% | 31% | -0.31% | 37.6 | 2 | -1.5%, -0.7% | -0.122 | -0.058% |
| 827 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf M30 | 28.7 | 34% | -0.082 | -0.044% | -0.061% | 40% | -0.33% | 150.7 | 0 | - | -0.045 | -0.041% |
| 828 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf M5 | 211.1 | 20% | -0.083 | -0.047% | -0.066% | 30% | -0.36% | 20.5 | 5 | -1.2%, -1.5%, -2.3%, -1.0%, -2.8% | -0.117 | -0.056% |
| 829 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf H1 | 26.2 | 28% | -0.083 | -0.041% | -0.057% | 22% | -0.23% | 164.7 | 0 | - | -0.254 | -0.072% |
| 830 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf M5 | 123.8 | 25% | -0.083 | -0.046% | -0.063% | 39% | -0.36% | 34.9 | 3 | -0.9%, -1.2%, -2.8% | -0.087 | -0.047% |
| 831 | buffer 0.5, clear 0.05, entry close, exit 4R, grade AB, stop all4, tf M5 | 480.0 | 25% | -0.083 | -0.045% | -0.063% | 36% | -0.38% | 9.0 | 11 | -0.5%, -1.2%, -2.7%, +0.3%, -2.6%, -0.1%, -2.5%, -1.0%, -2.4%, -3.3%, -1.2% | -0.062 | -0.038% |
| 832 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf M15 | 11.0 | 16% | -0.083 | -0.057% | -0.079% | 22% | -0.22% | 392.7 | 0 | - | +0.178 | +2.313% |
| 833 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c4, tf M5 | 46.0 | 25% | -0.083 | -0.045% | -0.063% | 42% | -0.34% | 93.9 | 1 | -1.2% | -0.000 | +0.002% |
| 834 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf M15 | 44.6 | 21% | -0.083 | -0.045% | -0.063% | 33% | -0.30% | 96.9 | 1 | -1.5% | -0.029 | -0.021% |
| 835 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf M15 | 10.9 | 19% | -0.084 | -0.053% | -0.074% | 33% | -0.23% | 396.7 | 0 | - | +0.088 | +0.640% |
| 836 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf H1 | 12.9 | 47% | -0.084 | -0.038% | -0.052% | 46% | -0.33% | 335.2 | 0 | - | +0.017 | -0.028% |
| 837 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf H1 | 21.7 | 32% | -0.084 | -0.047% | -0.065% | 47% | -0.33% | 198.7 | 0 | - | -0.002 | +0.007% |
| 838 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf H1 | 5.7 | 40% | -0.084 | -0.071% | -0.099% | 0% | -0.17% | 754.8 | 0 | - | +0.056 | +0.380% |
| 839 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.084 | -0.079% | -0.109% | 0% | -0.16% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 840 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf M5 | 35.8 | 28% | -0.084 | -0.045% | -0.062% | 29% | -0.36% | 120.6 | 0 | - | -0.055 | -0.036% |
| 841 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf M30 | 7.8 | 44% | -0.084 | -0.043% | -0.059% | 43% | -0.32% | 554.3 | 0 | - | -0.062 | -0.077% |
| 842 | buffer 0.0, clear 0.05, entry close, exit 4R, grade AB, stop c4, tf M5 | 436.8 | 21% | -0.084 | -0.046% | -0.063% | 38% | -0.39% | 9.9 | 10 | +0.2%, -2.0%, -2.6%, -2.2%, -1.3%, -1.2%, -1.3%, -1.9%, -2.3%, -1.8% | -0.042 | -0.029% |
| 843 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c4, tf H1 | 45.8 | 30% | -0.084 | -0.042% | -0.059% | 24% | -0.31% | 94.3 | 1 | -1.8% | -0.192 | -0.063% |
| 844 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop all4, tf M15 | 15.5 | 47% | -0.084 | -0.045% | -0.063% | 42% | -0.36% | 279.3 | 0 | - | -0.015 | -0.010% |
| 845 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop all4, tf M30 | 8.5 | 33% | -0.084 | -0.063% | -0.087% | 14% | -0.21% | 511.2 | 0 | - | -0.287 | -0.067% |
| 846 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf M15 | 13.6 | 22% | -0.084 | -0.053% | -0.073% | 27% | -0.31% | 316.8 | 0 | - | +0.023 | -0.053% |
| 847 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf H1 | 46.2 | 37% | -0.084 | -0.050% | -0.070% | 32% | -0.38% | 93.6 | 1 | -2.3% | -0.241 | -0.068% |
| 848 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf H1 | 26.7 | 29% | -0.084 | -0.041% | -0.057% | 35% | -0.30% | 162.0 | 0 | - | -0.241 | -0.070% |
| 849 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf M15 | 50.1 | 31% | -0.085 | -0.052% | -0.072% | 41% | -0.32% | 86.3 | 1 | -2.3% | -0.062 | -0.039% |
| 850 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf M5 | 51.9 | 33% | -0.085 | -0.052% | -0.072% | 39% | -0.30% | 83.2 | 1 | -1.2% | +0.069 | +0.128% |
| 851 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop all4, tf M5 | 54.9 | 26% | -0.085 | -0.052% | -0.072% | 31% | -0.27% | 78.7 | 1 | -2.2% | -0.077 | -0.046% |
| 852 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf M15 | 87.5 | 34% | -0.085 | -0.043% | -0.060% | 40% | -0.42% | 49.4 | 2 | -1.8%, -1.5% | +0.017 | +0.012% |
| 853 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf H1 | 44.7 | 34% | -0.085 | -0.040% | -0.056% | 35% | -0.30% | 96.6 | 1 | -2.3% | -0.136 | -0.052% |
| 854 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c34, tf M5 | 459.6 | 25% | -0.085 | -0.045% | -0.062% | 38% | -0.38% | 9.4 | 11 | -0.4%, -1.1%, -4.4%, -1.2%, -1.9%, -1.3%, -0.8%, -0.5%, -1.1%, -3.3%, -0.7% | -0.057 | -0.036% |
| 855 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf M15 | 88.2 | 25% | -0.085 | -0.047% | -0.066% | 35% | -0.34% | 49.0 | 2 | -1.4%, -1.7% | -0.046 | -0.034% |
| 856 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf M15 | 15.1 | 22% | -0.085 | -0.049% | -0.068% | 25% | -0.27% | 285.2 | 0 | - | +0.135 | +0.113% |
| 857 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c4, tf M15 | 14.9 | 28% | -0.085 | -0.036% | -0.050% | 42% | -0.36% | 290.7 | 0 | - | +0.003 | -0.019% |
| 858 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf H1 | 3.2 | 39% | -0.085 | -0.056% | -0.078% | 50% | -0.08% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 859 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf H1 | 45.6 | 36% | -0.085 | -0.048% | -0.067% | 35% | -0.44% | 94.8 | 1 | -2.0% | -0.245 | -0.069% |
| 860 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf M5 | 21.2 | 24% | -0.086 | -0.035% | -0.049% | 39% | -0.40% | 204.2 | 0 | - | -0.067 | -0.044% |
| 861 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf M5 | 248.8 | 25% | -0.086 | -0.047% | -0.066% | 35% | -0.34% | 17.4 | 6 | -0.6%, -2.2%, -2.8%, -1.6%, -1.6%, -0.9% | -0.041 | -0.030% |
| 862 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf M5 | 53.9 | 24% | -0.086 | -0.050% | -0.069% | 33% | -0.32% | 80.1 | 1 | -1.2% | -0.134 | -0.055% |
| 863 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf M15 | 86.3 | 24% | -0.086 | -0.043% | -0.060% | 42% | -0.32% | 50.1 | 2 | -1.9%, -1.7% | +0.012 | +0.006% |
| 864 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c4, tf M15 | 4.2 | 38% | -0.086 | -0.071% | -0.099% | 0% | -0.14% | 1029.8 | 0 | - | +0.111 | +0.176% |
| 865 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf M30 | 93.5 | 46% | -0.086 | -0.048% | -0.067% | 37% | -0.41% | 46.2 | 2 | -2.2%, -1.4% | +0.015 | +0.011% |
| 866 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf M15 | 88.8 | 33% | -0.086 | -0.044% | -0.061% | 37% | -0.38% | 48.7 | 2 | -2.4%, -0.7% | +0.034 | +0.016% |
| 867 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c4, tf M5 | 54.2 | 26% | -0.086 | -0.052% | -0.073% | 33% | -0.28% | 79.6 | 1 | -2.1% | -0.073 | -0.045% |
| 868 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c4, tf M15 | 27.4 | 39% | -0.086 | -0.042% | -0.058% | 30% | -0.33% | 157.7 | 0 | - | +0.039 | +0.027% |
| 869 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c34, tf M15 | 20.8 | 25% | -0.086 | -0.050% | -0.069% | 28% | -0.22% | 208.0 | 0 | - | +0.092 | +0.484% |
| 870 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf M5 | 211.5 | 24% | -0.086 | -0.048% | -0.067% | 31% | -0.35% | 20.4 | 5 | -1.1%, -2.0%, -1.5%, -1.7%, -2.6% | -0.139 | -0.064% |
| 871 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf H1 | 21.6 | 34% | -0.086 | -0.048% | -0.066% | 42% | -0.32% | 199.7 | 0 | - | -0.117 | -0.055% |
| 872 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf M5 | 5.8 | 44% | -0.086 | -0.007% | -0.009% | 40% | -0.41% | 742.3 | 0 | - | +0.000 | +0.000% |
| 873 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c34, tf M15 | 15.0 | 47% | -0.086 | -0.046% | -0.064% | 42% | -0.41% | 288.4 | 0 | - | -0.044 | -0.035% |
| 874 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop all4, tf M15 | 27.3 | 39% | -0.086 | -0.043% | -0.060% | 26% | -0.34% | 158.4 | 0 | - | +0.021 | -0.000% |
| 875 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.087 | -0.078% | -0.108% | 33% | -0.14% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 876 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf M15 | 101.5 | 29% | -0.087 | -0.047% | -0.065% | 37% | -0.33% | 42.6 | 2 | -0.8%, -2.4% | -0.024 | -0.022% |
| 877 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop all4, tf M15 | 89.5 | 30% | -0.087 | -0.044% | -0.061% | 38% | -0.38% | 48.3 | 2 | -1.1%, -2.1% | +0.031 | +0.018% |
| 878 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c34, tf M15 | 27.2 | 37% | -0.087 | -0.045% | -0.063% | 39% | -0.30% | 159.1 | 0 | - | -0.015 | -0.028% |
| 879 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf M30 | 7.9 | 44% | -0.087 | -0.052% | -0.072% | 29% | -0.24% | 546.5 | 0 | - | -0.063 | -0.066% |
| 880 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c34, tf M15 | 88.1 | 26% | -0.087 | -0.046% | -0.064% | 37% | -0.30% | 49.0 | 2 | -2.3%, -1.3% | -0.009 | -0.018% |
| 881 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop all4, tf M5 | 53.4 | 26% | -0.087 | -0.054% | -0.075% | 36% | -0.28% | 81.0 | 1 | -2.0% | -0.054 | -0.039% |
| 882 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf H4 | 4.7 | 45% | -0.087 | -0.059% | -0.082% | 25% | -0.19% | 917.0 | 0 | - | +0.051 | +0.005% |
| 883 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c4, tf M5 | 78.7 | 27% | -0.087 | -0.046% | -0.064% | 34% | -0.36% | 54.9 | 1 | -0.9% | +0.002 | -0.002% |
| 884 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c34, tf M30 | 8.5 | 33% | -0.087 | -0.064% | -0.089% | 14% | -0.21% | 511.2 | 0 | - | -0.291 | -0.066% |
| 885 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf M15 | 95.0 | 26% | -0.088 | -0.049% | -0.068% | 39% | -0.35% | 45.5 | 2 | -1.8%, -1.4% | -0.029 | -0.025% |
| 886 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf M5 | 5.7 | 22% | -0.088 | -0.018% | -0.025% | 50% | -0.26% | 757.4 | 0 | - | +0.000 | +0.000% |
| 887 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf M5 | 120.0 | 29% | -0.088 | -0.047% | -0.065% | 37% | -0.35% | 36.0 | 2 | -1.1%, -2.2% | -0.099 | -0.051% |
| 888 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf M15 | 21.3 | 34% | -0.088 | -0.048% | -0.067% | 37% | -0.34% | 202.5 | 0 | - | +0.133 | +0.682% |
| 889 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c4, tf H1 | 21.7 | 31% | -0.088 | -0.049% | -0.068% | 37% | -0.33% | 198.7 | 0 | - | -0.056 | -0.026% |
| 890 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c4, tf M5 | 46.0 | 32% | -0.088 | -0.051% | -0.071% | 32% | -0.36% | 93.9 | 1 | -1.8% | -0.061 | -0.037% |
| 891 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop all4, tf M5 | 474.8 | 31% | -0.088 | -0.046% | -0.064% | 37% | -0.42% | 9.1 | 11 | -1.4%, -1.8%, -3.9%, -0.8%, -2.6%, -0.3%, -1.9%, +0.1%, -1.7%, -2.6%, -2.0% | -0.058 | -0.037% |
| 892 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf M5 | 33.3 | 26% | -0.089 | -0.047% | -0.065% | 38% | -0.28% | 129.6 | 0 | - | -0.132 | -0.066% |
| 893 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf M5 | 227.4 | 21% | -0.089 | -0.047% | -0.065% | 30% | -0.46% | 19.0 | 5 | -1.7%, -2.9%, -2.2%, -0.2%, -2.6% | -0.020 | -0.016% |
| 894 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf M5 | 246.9 | 32% | -0.089 | -0.048% | -0.066% | 38% | -0.41% | 17.5 | 6 | -1.2%, -2.6%, -1.1%, -1.5%, -2.2%, -1.6% | -0.058 | -0.036% |
| 895 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c4, tf M30 | 8.6 | 33% | -0.089 | -0.063% | -0.088% | 14% | -0.20% | 504.4 | 0 | - | -0.284 | -0.074% |
| 896 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c34, tf M5 | 74.5 | 22% | -0.089 | -0.047% | -0.066% | 36% | -0.32% | 58.0 | 1 | -1.4% | +0.027 | +0.025% |
| 897 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf M30 | 54.5 | 44% | -0.089 | -0.053% | -0.074% | 37% | -0.33% | 79.2 | 1 | -2.2% | +0.032 | +0.019% |
| 898 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf M5 | 482.3 | 32% | -0.089 | -0.046% | -0.064% | 37% | -0.40% | 9.0 | 12 | -0.6%, -0.8%, -3.3%, -0.6%, -2.2%, -0.4%, -3.2%, +0.3%, -2.4%, -3.6%, -1.1%, -1.8% | -0.070 | -0.041% |
| 899 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf M15 | 46.5 | 25% | -0.089 | -0.050% | -0.069% | 39% | -0.33% | 92.9 | 1 | -1.7% | +0.001 | +0.007% |
| 900 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf M5 | 241.6 | 24% | -0.090 | -0.047% | -0.065% | 32% | -0.34% | 17.9 | 6 | -1.1%, -0.6%, -1.4%, -1.1%, -3.7%, -2.4% | -0.136 | -0.060% |
| 901 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop all4, tf M5 | 45.5 | 32% | -0.090 | -0.048% | -0.066% | 38% | -0.35% | 95.0 | 1 | -2.2% | -0.065 | -0.035% |
| 902 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf M15 | 49.8 | 27% | -0.090 | -0.051% | -0.071% | 36% | -0.33% | 86.7 | 1 | -1.9% | -0.036 | -0.027% |
| 903 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop all4, tf M15 | 27.3 | 46% | -0.090 | -0.050% | -0.069% | 35% | -0.35% | 158.4 | 0 | - | +0.048 | +0.028% |
| 904 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf M5 | 39.7 | 31% | -0.090 | -0.049% | -0.068% | 29% | -0.30% | 108.9 | 0 | - | -0.079 | -0.044% |
| 905 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf M15 | 95.3 | 28% | -0.090 | -0.049% | -0.069% | 28% | -0.32% | 45.3 | 2 | -1.4%, -2.0% | -0.114 | -0.058% |
| 906 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop all4, tf M15 | 27.5 | 28% | -0.090 | -0.045% | -0.062% | 29% | -0.31% | 157.1 | 0 | - | +0.074 | +0.045% |
| 907 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf M5 | 105.0 | 19% | -0.090 | -0.049% | -0.068% | 30% | -0.30% | 41.1 | 2 | -2.1%, -0.8% | -0.111 | -0.053% |
| 908 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf M15 | 176.3 | 34% | -0.090 | -0.047% | -0.065% | 39% | -0.40% | 24.5 | 4 | -0.8%, -2.3%, -2.7%, -0.7% | +0.001 | -0.001% |
| 909 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf M5 | 17.0 | 23% | -0.090 | -0.060% | -0.083% | 33% | -0.23% | 253.4 | 0 | - | -0.019 | -0.056% |
| 910 | buffer 0.0, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf M5 | 236.2 | 22% | -0.090 | -0.048% | -0.066% | 32% | -0.47% | 18.3 | 5 | -1.9%, -3.8%, -1.8%, -0.4%, -1.8% | -0.012 | -0.009% |
| 911 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf M30 | 5.5 | 25% | -0.091 | -0.008% | -0.011% | 50% | -0.31% | 782.7 | 0 | - | +0.000 | +0.000% |
| 912 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf M15 | 14.9 | 32% | -0.091 | -0.049% | -0.068% | 25% | -0.32% | 289.7 | 0 | - | +0.081 | +0.098% |
| 913 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf H1 | 5.7 | 38% | -0.091 | -0.059% | -0.082% | 25% | -0.24% | 754.8 | 0 | - | +0.411 | +8.399% |
| 914 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c4, tf M15 | 26.1 | 28% | -0.091 | -0.045% | -0.063% | 36% | -0.26% | 165.4 | 0 | - | +0.058 | +0.049% |
| 915 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c4, tf M15 | 26.0 | 36% | -0.091 | -0.049% | -0.068% | 27% | -0.28% | 166.1 | 0 | - | -0.056 | -0.044% |
| 916 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf M30 | 7.7 | 30% | -0.091 | -0.062% | -0.086% | 17% | -0.29% | 562.3 | 0 | - | -0.134 | -0.082% |
| 917 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf M5 | 35.7 | 24% | -0.092 | -0.044% | -0.061% | 42% | -0.35% | 121.0 | 0 | - | -0.100 | -0.053% |
| 918 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf M5 | 49.8 | 24% | -0.092 | -0.049% | -0.069% | 34% | -0.32% | 86.8 | 1 | -1.3% | -0.070 | -0.039% |
| 919 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop all4, tf M15 | 28.3 | 28% | -0.092 | -0.046% | -0.063% | 29% | -0.35% | 152.6 | 0 | - | +0.093 | +0.084% |
| 920 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf M30 | 50.8 | 24% | -0.092 | -0.051% | -0.071% | 38% | -0.35% | 85.0 | 1 | -1.3% | -0.028 | -0.035% |
| 921 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c34, tf M5 | 44.4 | 23% | -0.092 | -0.049% | -0.068% | 33% | -0.33% | 97.2 | 1 | -1.7% | +0.020 | +0.033% |
| 922 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop all4, tf M15 | 15.3 | 29% | -0.092 | -0.046% | -0.064% | 50% | -0.35% | 281.5 | 0 | - | +0.040 | +0.025% |
| 923 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf M5 | 147.9 | 20% | -0.092 | -0.052% | -0.072% | 24% | -0.23% | 29.2 | 3 | -2.7%, -0.5%, -3.0% | -0.094 | -0.059% |
| 924 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop all4, tf M5 | 80.5 | 26% | -0.092 | -0.048% | -0.067% | 33% | -0.34% | 53.7 | 2 | -0.8%, -2.8% | -0.010 | -0.015% |
| 925 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c34, tf M15 | 14.9 | 29% | -0.092 | -0.041% | -0.056% | 50% | -0.38% | 290.7 | 0 | - | +0.011 | -0.012% |
| 926 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf M15 | 9.3 | 25% | -0.092 | -0.065% | -0.091% | 12% | -0.16% | 463.7 | 0 | - | +0.117 | +0.678% |
| 927 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf M30 | 54.4 | 24% | -0.092 | -0.051% | -0.070% | 33% | -0.34% | 79.4 | 1 | -1.6% | -0.024 | -0.021% |
| 928 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf H1 | 5.6 | 38% | -0.092 | -0.073% | -0.101% | 0% | -0.16% | 770.9 | 0 | - | +0.154 | +2.013% |
| 929 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop all4, tf M15 | 88.2 | 26% | -0.093 | -0.048% | -0.067% | 30% | -0.29% | 49.0 | 2 | -2.2%, -1.8% | -0.009 | -0.021% |
| 930 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf M30 | 5.6 | 37% | -0.093 | -0.048% | -0.067% | 25% | -0.37% | 766.8 | 0 | - | +0.000 | +0.000% |
| 931 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf M5 | 250.0 | 22% | -0.093 | -0.047% | -0.065% | 35% | -0.35% | 17.3 | 6 | -1.8%, -1.1%, -0.3%, -1.2%, -3.3%, -2.0% | -0.110 | -0.054% |
| 932 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf M5 | 250.4 | 25% | -0.093 | -0.049% | -0.068% | 34% | -0.34% | 17.3 | 6 | -1.2%, -0.9%, -0.6%, -1.8%, -3.1%, -2.4% | -0.108 | -0.054% |
| 933 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c4, tf M30 | 8.3 | 24% | -0.093 | -0.044% | -0.061% | 43% | -0.27% | 518.1 | 0 | - | -0.203 | -0.086% |
| 934 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf H1 | 3.0 | 33% | -0.093 | -0.053% | -0.073% | 0% | -0.20% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 935 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf M5 | 243.4 | 31% | -0.093 | -0.048% | -0.066% | 34% | -0.45% | 17.8 | 6 | -2.5%, -3.0%, -1.1%, -0.4%, -2.3%, -1.2% | -0.039 | -0.029% |
| 936 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c4, tf M15 | 4.2 | 44% | -0.093 | -0.042% | -0.059% | 0% | -0.20% | 1029.8 | 0 | - | +0.236 | +1.477% |
| 937 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c4, tf M5 | 78.8 | 32% | -0.093 | -0.049% | -0.069% | 40% | -0.34% | 54.8 | 1 | -1.5% | -0.052 | -0.035% |
| 938 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c34, tf H1 | 7.2 | 34% | -0.093 | -0.054% | -0.075% | 33% | -0.25% | 597.7 | 0 | - | -0.387 | -0.086% |
| 939 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop all4, tf H1 | 45.1 | 30% | -0.093 | -0.047% | -0.065% | 28% | -0.29% | 95.7 | 1 | -2.3% | -0.250 | -0.068% |
| 940 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf H1 | 46.3 | 37% | -0.094 | -0.053% | -0.074% | 27% | -0.38% | 93.4 | 1 | -2.3% | -0.256 | -0.072% |
| 941 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf M15 | 15.6 | 45% | -0.094 | -0.052% | -0.073% | 31% | -0.21% | 276.5 | 0 | - | +0.208 | +0.514% |
| 942 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf M30 | 29.1 | 34% | -0.094 | -0.055% | -0.076% | 32% | -0.32% | 148.3 | 0 | - | -0.204 | -0.069% |
| 943 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c4, tf M30 | 14.8 | 39% | -0.094 | -0.053% | -0.074% | 31% | -0.28% | 292.0 | 0 | - | -0.359 | -0.087% |
| 944 | buffer 0.0, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf M5 | 438.1 | 24% | -0.094 | -0.048% | -0.067% | 38% | -0.45% | 9.9 | 10 | -0.4%, -2.2%, -3.0%, -1.8%, -1.6%, -1.1%, -1.4%, -1.6%, -2.4%, -1.9% | -0.058 | -0.037% |
| 945 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c34, tf M15 | 15.0 | 35% | -0.094 | -0.047% | -0.065% | 42% | -0.44% | 288.4 | 0 | - | +0.022 | +0.025% |
| 946 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c34, tf M5 | 79.8 | 35% | -0.094 | -0.052% | -0.072% | 37% | -0.38% | 54.1 | 1 | -1.2% | -0.041 | -0.030% |
| 947 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop all4, tf M15 | 27.2 | 30% | -0.094 | -0.051% | -0.071% | 39% | -0.31% | 159.1 | 0 | - | -0.017 | -0.015% |
| 948 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop all4, tf M15 | 89.5 | 34% | -0.094 | -0.045% | -0.063% | 39% | -0.42% | 48.3 | 2 | -1.9%, -1.4% | +0.040 | +0.036% |
| 949 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf H1 | 5.6 | 38% | -0.094 | -0.071% | -0.099% | 0% | -0.20% | 770.9 | 0 | - | +0.138 | +1.443% |
| 950 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf M5 | 5.2 | 20% | -0.094 | +0.017% | +0.024% | 25% | -0.39% | 824.8 | 0 | - | +0.000 | +0.000% |
| 951 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf M5 | 29.0 | 23% | -0.094 | -0.048% | -0.067% | 44% | -0.27% | 148.8 | 0 | - | -0.088 | -0.059% |
| 952 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c4, tf M15 | 26.0 | 46% | -0.095 | -0.051% | -0.071% | 27% | -0.24% | 166.1 | 0 | - | -0.035 | -0.038% |
| 953 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf M5 | 54.2 | 45% | -0.095 | -0.052% | -0.072% | 35% | -0.42% | 79.6 | 1 | -1.9% | -0.061 | -0.041% |
| 954 | buffer 0.5, clear 0.05, entry close, exit 3R, grade AB, stop c4, tf M15 | 176.1 | 29% | -0.095 | -0.049% | -0.068% | 35% | -0.37% | 24.5 | 4 | -0.9%, -2.0%, -2.8%, -1.0% | -0.029 | -0.023% |
| 955 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf M15 | 20.4 | 25% | -0.095 | -0.053% | -0.074% | 28% | -0.33% | 211.5 | 0 | - | +0.064 | +0.167% |
| 956 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop all4, tf M15 | 27.2 | 34% | -0.095 | -0.050% | -0.069% | 35% | -0.37% | 159.1 | 0 | - | +0.013 | +0.006% |
| 957 | buffer 0.5, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf M15 | 175.9 | 34% | -0.095 | -0.049% | -0.068% | 39% | -0.42% | 24.6 | 4 | -0.8%, -1.7%, -2.9%, -1.4% | +0.000 | -0.001% |
| 958 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop all4, tf M15 | 89.5 | 29% | -0.095 | -0.046% | -0.065% | 34% | -0.34% | 48.3 | 2 | -1.4%, -1.9% | -0.003 | -0.015% |
| 959 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c4, tf M15 | 86.6 | 26% | -0.096 | -0.048% | -0.067% | 34% | -0.30% | 49.9 | 2 | -2.3%, -1.5% | -0.008 | -0.017% |
| 960 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c34, tf M5 | 44.4 | 26% | -0.096 | -0.049% | -0.069% | 41% | -0.35% | 97.2 | 1 | -1.8% | -0.035 | -0.017% |
| 961 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf M5 | 236.6 | 24% | -0.096 | -0.049% | -0.068% | 33% | -0.50% | 18.3 | 5 | -1.3%, -3.6%, -1.4%, -0.5%, -2.2% | -0.030 | -0.022% |
| 962 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c34, tf H1 | 45.1 | 30% | -0.096 | -0.047% | -0.065% | 25% | -0.31% | 95.7 | 1 | -2.2% | -0.196 | -0.063% |
| 963 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf M15 | 8.0 | 45% | -0.096 | -0.049% | -0.068% | 17% | -0.22% | 542.9 | 0 | - | +0.177 | +0.266% |
| 964 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop all4, tf M15 | 27.6 | 32% | -0.096 | -0.052% | -0.072% | 29% | -0.34% | 156.4 | 0 | - | +0.066 | +0.095% |
| 965 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf M5 | 51.8 | 30% | -0.096 | -0.055% | -0.076% | 33% | -0.38% | 83.4 | 1 | -1.3% | -0.060 | -0.045% |
| 966 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c34, tf M5 | 52.2 | 26% | -0.096 | -0.055% | -0.077% | 33% | -0.30% | 82.7 | 1 | -2.2% | -0.042 | -0.033% |
| 967 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf H1 | 46.3 | 36% | -0.097 | -0.052% | -0.072% | 29% | -0.32% | 93.4 | 1 | -2.3% | -0.203 | -0.063% |
| 968 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf M5 | 123.8 | 30% | -0.097 | -0.050% | -0.069% | 38% | -0.40% | 34.9 | 3 | -1.8%, -2.0%, -1.6% | -0.092 | -0.050% |
| 969 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop all4, tf M5 | 77.6 | 32% | -0.097 | -0.049% | -0.068% | 33% | -0.39% | 55.7 | 1 | -1.6% | -0.031 | -0.023% |
| 970 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf M15 | 77.2 | 26% | -0.097 | -0.047% | -0.066% | 35% | -0.28% | 55.9 | 1 | -1.6% | -0.132 | -0.061% |
| 971 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf M5 | 123.7 | 21% | -0.097 | -0.050% | -0.069% | 32% | -0.30% | 34.9 | 3 | -0.9%, -1.6%, -2.8% | -0.119 | -0.056% |
| 972 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf M5 | 53.8 | 45% | -0.097 | -0.055% | -0.076% | 31% | -0.32% | 80.3 | 1 | -1.9% | -0.059 | -0.036% |
| 973 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c34, tf M15 | 27.3 | 31% | -0.098 | -0.054% | -0.074% | 30% | -0.33% | 158.4 | 0 | - | +0.046 | +0.059% |
| 974 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c4, tf M5 | 72.2 | 21% | -0.098 | -0.051% | -0.071% | 34% | -0.31% | 59.8 | 1 | -1.1% | +0.013 | +0.007% |
| 975 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf M15 | 11.3 | 23% | -0.098 | -0.059% | -0.082% | 20% | -0.27% | 381.0 | 0 | - | +0.107 | +0.651% |
| 976 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf M15 | 20.7 | 22% | -0.098 | -0.052% | -0.073% | 39% | -0.29% | 209.2 | 0 | - | +0.100 | +0.326% |
| 977 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf H1 | 12.7 | 44% | -0.099 | -0.048% | -0.067% | 36% | -0.24% | 341.1 | 0 | - | -0.083 | -0.048% |
| 978 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop all4, tf M5 | 80.5 | 28% | -0.099 | -0.050% | -0.069% | 33% | -0.36% | 53.7 | 2 | -0.9%, -2.8% | -0.010 | -0.014% |
| 979 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c34, tf M15 | 27.3 | 27% | -0.099 | -0.048% | -0.066% | 26% | -0.26% | 158.4 | 0 | - | +0.082 | +0.096% |
| 980 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf M15 | 88.4 | 31% | -0.099 | -0.050% | -0.069% | 32% | -0.37% | 48.9 | 2 | -1.2%, -2.0% | -0.054 | -0.038% |
| 981 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf M15 | 11.4 | 28% | -0.099 | -0.053% | -0.074% | 20% | -0.26% | 377.3 | 0 | - | +0.039 | +0.333% |
| 982 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf M5 | 234.0 | 26% | -0.100 | -0.051% | -0.071% | 32% | -0.34% | 18.5 | 5 | -1.4%, -1.9%, -1.2%, -1.6%, -3.5% | -0.116 | -0.058% |
| 983 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c34, tf M5 | 74.5 | 26% | -0.100 | -0.051% | -0.071% | 32% | -0.35% | 58.0 | 1 | -1.2% | -0.018 | -0.016% |
| 984 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf M30 | 54.5 | 44% | -0.100 | -0.057% | -0.079% | 31% | -0.33% | 79.2 | 1 | -2.0% | -0.042 | -0.029% |
| 985 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.100 | -0.082% | -0.114% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 986 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf M15 | 11.6 | 28% | -0.100 | -0.054% | -0.074% | 30% | -0.25% | 373.6 | 0 | - | -0.036 | +0.027% |
| 987 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c34, tf M15 | 176.5 | 26% | -0.100 | -0.052% | -0.072% | 34% | -0.31% | 24.5 | 4 | -1.5%, -2.5%, -1.5%, -1.9% | +0.004 | +0.000% |
| 988 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf M30 | 26.6 | 21% | -0.100 | -0.046% | -0.064% | 22% | -0.23% | 162.5 | 0 | - | -0.115 | -0.056% |
| 989 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf M30 | 7.7 | 44% | -0.100 | -0.071% | -0.099% | 17% | -0.23% | 560.8 | 0 | - | -0.099 | -0.074% |
| 990 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf M15 | 20.7 | 23% | -0.100 | -0.055% | -0.076% | 33% | -0.30% | 209.2 | 0 | - | +0.095 | +0.286% |
| 991 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf M5 | 115.0 | 27% | -0.100 | -0.051% | -0.071% | 30% | -0.32% | 37.6 | 2 | -1.6%, -2.3% | -0.086 | -0.047% |
| 992 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf M5 | 37.3 | 30% | -0.100 | -0.051% | -0.070% | 33% | -0.36% | 115.8 | 0 | - | -0.086 | -0.044% |
| 993 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf M30 | 27.3 | 23% | -0.100 | -0.048% | -0.066% | 33% | -0.34% | 158.4 | 0 | - | -0.055 | -0.053% |
| 994 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf M5 | 29.0 | 19% | -0.101 | -0.047% | -0.066% | 32% | -0.28% | 148.8 | 0 | - | -0.141 | -0.066% |
| 995 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf M30 | 28.7 | 29% | -0.101 | -0.049% | -0.068% | 40% | -0.32% | 150.7 | 0 | - | -0.021 | -0.028% |
| 996 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf M15 | 100.1 | 31% | -0.101 | -0.051% | -0.071% | 24% | -0.28% | 43.1 | 2 | -0.8%, -2.7% | -0.026 | -0.023% |
| 997 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf M5 | 105.9 | 20% | -0.101 | -0.054% | -0.075% | 25% | -0.24% | 40.8 | 2 | -2.6%, -2.3% | -0.113 | -0.055% |
| 998 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf M5 | 49.9 | 31% | -0.101 | -0.057% | -0.079% | 36% | -0.27% | 86.6 | 1 | -1.4% | +0.048 | +0.087% |
| 999 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c34, tf M30 | 8.6 | 33% | -0.101 | -0.065% | -0.091% | 14% | -0.20% | 504.4 | 0 | - | -0.290 | -0.073% |
| 1000 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop all4, tf M30 | 14.9 | 41% | -0.101 | -0.057% | -0.079% | 31% | -0.32% | 289.8 | 0 | - | -0.369 | -0.087% |
| 1001 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf M15 | 99.6 | 25% | -0.101 | -0.052% | -0.072% | 33% | -0.31% | 43.4 | 2 | -0.6%, -2.9% | +0.006 | +0.006% |
| 1002 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop all4, tf M15 | 15.5 | 35% | -0.101 | -0.052% | -0.072% | 33% | -0.30% | 279.3 | 0 | - | +0.059 | +0.099% |
| 1003 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf M30 | 5.6 | 31% | -0.101 | -0.037% | -0.051% | 50% | -0.34% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1004 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c34, tf M15 | 88.2 | 29% | -0.102 | -0.049% | -0.068% | 37% | -0.36% | 49.0 | 2 | -1.3%, -2.3% | +0.034 | +0.021% |
| 1005 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c4, tf M15 | 172.6 | 26% | -0.102 | -0.052% | -0.072% | 34% | -0.32% | 25.0 | 4 | -1.4%, -2.3%, -2.2%, -1.7% | +0.000 | -0.004% |
| 1006 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf H4 | 4.6 | 41% | -0.102 | -0.063% | -0.087% | 33% | -0.30% | 940.5 | 0 | - | +0.015 | +0.090% |
| 1007 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf M15 | 14.4 | 34% | -0.102 | -0.051% | -0.070% | 33% | -0.28% | 299.2 | 0 | - | +0.051 | +0.021% |
| 1008 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf M30 | 5.5 | 38% | -0.102 | -0.036% | -0.050% | 25% | -0.28% | 782.7 | 0 | - | +0.000 | +0.000% |
| 1009 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c34, tf M15 | 27.8 | 28% | -0.102 | -0.049% | -0.067% | 33% | -0.34% | 155.2 | 0 | - | +0.092 | +0.117% |
| 1010 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf M30 | 54.7 | 34% | -0.102 | -0.056% | -0.077% | 35% | -0.34% | 79.0 | 1 | -2.2% | -0.113 | -0.057% |
| 1011 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c34, tf H1 | 21.7 | 30% | -0.102 | -0.052% | -0.072% | 42% | -0.33% | 198.7 | 0 | - | -0.077 | -0.038% |
| 1012 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c4, tf M5 | 12.4 | 26% | -0.103 | -0.037% | -0.052% | 50% | -0.35% | 349.6 | 0 | - | -0.369 | -0.085% |
| 1013 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf M5 | 17.0 | 20% | -0.103 | -0.069% | -0.096% | 27% | -0.21% | 253.4 | 0 | - | +0.080 | +0.058% |
| 1014 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf M5 | 185.2 | 18% | -0.103 | -0.053% | -0.074% | 26% | -0.28% | 23.3 | 4 | -2.5%, -3.0%, -1.3%, -1.0% | -0.127 | -0.058% |
| 1015 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c34, tf M15 | 4.2 | 25% | -0.103 | +0.001% | +0.001% | 0% | -0.29% | 1029.8 | 0 | - | +0.159 | +0.375% |
| 1016 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf H1 | 3.5 | 43% | -0.103 | -0.063% | -0.087% | 33% | -0.10% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 1017 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c4, tf M15 | 27.0 | 34% | -0.103 | -0.055% | -0.076% | 26% | -0.34% | 159.8 | 0 | - | +0.037 | +0.057% |
| 1018 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf M15 | 175.0 | 44% | -0.103 | -0.050% | -0.070% | 32% | -0.45% | 24.7 | 4 | -1.7%, -3.1%, -1.5%, -0.3% | -0.028 | -0.024% |
| 1019 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf M15 | 11.3 | 29% | -0.104 | -0.066% | -0.092% | 30% | -0.26% | 381.0 | 0 | - | -0.039 | +0.126% |
| 1020 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf M15 | 97.9 | 30% | -0.104 | -0.052% | -0.073% | 31% | -0.34% | 44.1 | 2 | -0.7%, -2.4% | -0.064 | -0.042% |
| 1021 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf M15 | 10.3 | 28% | -0.104 | -0.051% | -0.071% | 33% | -0.23% | 418.3 | 0 | - | +0.058 | +0.180% |
| 1022 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c4, tf M5 | 50.2 | 26% | -0.104 | -0.057% | -0.079% | 29% | -0.25% | 86.0 | 1 | -2.5% | -0.051 | -0.035% |
| 1023 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf M5 | 119.6 | 30% | -0.104 | -0.051% | -0.071% | 35% | -0.37% | 36.1 | 2 | -1.9%, -1.8% | -0.105 | -0.052% |
| 1024 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf M5 | 105.0 | 23% | -0.104 | -0.051% | -0.071% | 34% | -0.30% | 41.1 | 2 | -2.5%, -0.7% | -0.083 | -0.045% |
| 1025 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf M5 | 244.5 | 33% | -0.104 | -0.052% | -0.072% | 32% | -0.43% | 17.7 | 6 | -1.7%, -1.6%, -2.4%, -1.5%, -2.3%, -1.9% | -0.016 | -0.015% |
| 1026 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop all4, tf M5 | 80.7 | 35% | -0.104 | -0.054% | -0.075% | 31% | -0.35% | 53.5 | 2 | -1.2%, -2.8% | -0.046 | -0.033% |
| 1027 | buffer 0.0, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf M5 | 227.7 | 24% | -0.104 | -0.051% | -0.072% | 34% | -0.44% | 19.0 | 5 | -1.7%, -2.9%, -1.8%, -0.1%, -3.0% | -0.025 | -0.019% |
| 1028 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf H1 | 3.2 | 39% | -0.104 | -0.063% | -0.087% | 50% | -0.05% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1029 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c4, tf M15 | 88.8 | 26% | -0.104 | -0.051% | -0.071% | 32% | -0.35% | 48.7 | 2 | -2.6%, -1.4% | -0.014 | -0.022% |
| 1030 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf M30 | 5.6 | 39% | -0.105 | -0.056% | -0.078% | 25% | -0.34% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1031 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop all4, tf H1 | 7.2 | 36% | -0.105 | -0.060% | -0.084% | 33% | -0.26% | 597.7 | 0 | - | -0.373 | -0.086% |
| 1032 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c34, tf M15 | 89.1 | 26% | -0.105 | -0.051% | -0.071% | 29% | -0.29% | 48.5 | 2 | -2.4%, -1.6% | -0.006 | -0.016% |
| 1033 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf M15 | 15.3 | 24% | -0.105 | -0.058% | -0.080% | 42% | -0.23% | 282.9 | 0 | - | +0.228 | +1.133% |
| 1034 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop all4, tf H1 | 45.6 | 30% | -0.105 | -0.049% | -0.067% | 30% | -0.30% | 94.8 | 1 | -2.1% | -0.243 | -0.069% |
| 1035 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf M5 | 243.4 | 28% | -0.105 | -0.052% | -0.072% | 35% | -0.33% | 17.7 | 6 | -1.6%, -0.6%, -1.8%, -1.7%, -3.3%, -2.3% | -0.118 | -0.059% |
| 1036 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf M30 | 26.6 | 23% | -0.105 | -0.052% | -0.073% | 26% | -0.23% | 162.5 | 0 | - | -0.169 | -0.069% |
| 1037 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c34, tf M5 | 74.6 | 32% | -0.105 | -0.054% | -0.075% | 32% | -0.32% | 57.9 | 1 | -1.2% | -0.038 | -0.030% |
| 1038 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c4, tf M15 | 88.1 | 26% | -0.105 | -0.049% | -0.068% | 28% | -0.31% | 49.0 | 2 | -1.6%, -1.8% | +0.013 | -0.000% |
| 1039 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf M5 | 114.8 | 23% | -0.105 | -0.051% | -0.071% | 30% | -0.31% | 37.6 | 2 | -1.5%, -1.4% | -0.137 | -0.061% |
| 1040 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c34, tf H1 | 45.5 | 30% | -0.105 | -0.049% | -0.068% | 35% | -0.33% | 95.0 | 1 | -2.0% | -0.218 | -0.065% |
| 1041 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf M5 | 39.4 | 30% | -0.105 | -0.053% | -0.073% | 32% | -0.33% | 109.5 | 0 | - | -0.054 | -0.033% |
| 1042 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf M15 | 87.6 | 44% | -0.105 | -0.050% | -0.070% | 32% | -0.45% | 49.3 | 2 | -2.5%, -0.8% | +0.009 | +0.013% |
| 1043 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf M5 | 17.8 | 21% | -0.106 | -0.044% | -0.061% | 47% | -0.31% | 242.3 | 0 | - | -0.082 | -0.036% |
| 1044 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf M15 | 77.0 | 20% | -0.106 | -0.051% | -0.071% | 34% | -0.27% | 56.1 | 1 | -2.1% | -0.015 | -0.018% |
| 1045 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c4, tf M5 | 13.0 | 33% | -0.106 | -0.046% | -0.065% | 55% | -0.38% | 331.4 | 0 | - | -0.338 | -0.081% |
| 1046 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf M30 | 28.6 | 34% | -0.106 | -0.051% | -0.071% | 48% | -0.36% | 151.3 | 0 | - | -0.016 | -0.039% |
| 1047 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c4, tf M15 | 14.7 | 36% | -0.106 | -0.050% | -0.069% | 42% | -0.30% | 293.1 | 0 | - | -0.092 | -0.046% |
| 1048 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop all4, tf M15 | 4.5 | 38% | -0.106 | -0.060% | -0.084% | 33% | -0.27% | 969.2 | 0 | - | +0.132 | +0.246% |
| 1049 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf M30 | 27.3 | 30% | -0.107 | -0.053% | -0.073% | 25% | -0.30% | 158.4 | 0 | - | -0.270 | -0.077% |
| 1050 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf M15 | 10.9 | 22% | -0.107 | -0.063% | -0.088% | 11% | -0.25% | 396.7 | 0 | - | +0.102 | +0.612% |
| 1051 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf M30 | 28.7 | 38% | -0.107 | -0.056% | -0.077% | 28% | -0.26% | 150.7 | 0 | - | -0.217 | -0.073% |
| 1052 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c4, tf M15 | 25.9 | 24% | -0.107 | -0.056% | -0.078% | 32% | -0.28% | 166.8 | 0 | - | -0.156 | -0.072% |
| 1053 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c4, tf M15 | 21.0 | 26% | -0.107 | -0.055% | -0.077% | 28% | -0.22% | 205.8 | 0 | - | +0.114 | +0.539% |
| 1054 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf M5 | 21.9 | 24% | -0.107 | -0.067% | -0.093% | 32% | -0.24% | 196.9 | 0 | - | -0.069 | -0.059% |
| 1055 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c4, tf M5 | 78.9 | 34% | -0.107 | -0.054% | -0.076% | 34% | -0.38% | 54.7 | 1 | -1.4% | -0.057 | -0.038% |
| 1056 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf M5 | 250.1 | 35% | -0.107 | -0.052% | -0.072% | 31% | -0.41% | 17.3 | 6 | -1.6%, -1.3%, -2.1%, -3.4%, -1.2%, -1.4% | -0.028 | -0.021% |
| 1057 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf M5 | 185.5 | 22% | -0.107 | -0.055% | -0.077% | 32% | -0.28% | 23.3 | 4 | -2.1%, -2.6%, -0.9%, -2.6% | -0.114 | -0.057% |
| 1058 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf M5 | 477.8 | 32% | -0.107 | -0.053% | -0.074% | 33% | -0.41% | 9.0 | 11 | -0.9%, -1.8%, -2.2%, -1.3%, -2.8%, -0.4%, -2.9%, -1.6%, -1.6%, -3.8%, -1.6% | -0.044 | -0.031% |
| 1059 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf M15 | 7.7 | 24% | -0.107 | -0.052% | -0.073% | 33% | -0.42% | 560.2 | 0 | - | -0.106 | -0.062% |
| 1060 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf M5 | 23.8 | 18% | -0.108 | -0.050% | -0.069% | 33% | -0.26% | 181.2 | 0 | - | -0.082 | -0.045% |
| 1061 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf M5 | 121.3 | 19% | -0.108 | -0.055% | -0.076% | 19% | -0.23% | 35.6 | 3 | -3.2%, -2.4%, -0.4% | -0.113 | -0.056% |
| 1062 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf M15 | 48.8 | 23% | -0.108 | -0.056% | -0.078% | 28% | -0.31% | 88.5 | 1 | -1.9% | -0.034 | -0.027% |
| 1063 | buffer 0.5, clear 0.1, entry close, exit 4R, grade AB, stop c34, tf M15 | 88.2 | 28% | -0.108 | -0.049% | -0.068% | 33% | -0.31% | 49.0 | 2 | -1.5%, -1.9% | +0.011 | -0.002% |
| 1064 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c34, tf M15 | 27.0 | 28% | -0.108 | -0.054% | -0.076% | 30% | -0.31% | 159.8 | 0 | - | -0.067 | -0.052% |
| 1065 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c34, tf M15 | 21.0 | 26% | -0.108 | -0.056% | -0.078% | 28% | -0.21% | 205.8 | 0 | - | +0.108 | +0.471% |
| 1066 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop all4, tf M30 | 14.7 | 45% | -0.108 | -0.060% | -0.083% | 23% | -0.31% | 294.2 | 0 | - | -0.232 | -0.079% |
| 1067 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf M5 | 211.2 | 22% | -0.108 | -0.054% | -0.075% | 33% | -0.36% | 20.5 | 5 | -1.6%, -2.3%, -2.4%, -0.8%, -3.0% | -0.106 | -0.055% |
| 1068 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf M5 | 124.5 | 30% | -0.108 | -0.054% | -0.074% | 27% | -0.34% | 34.7 | 3 | -1.4%, -2.4%, -2.1% | -0.114 | -0.055% |
| 1069 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.108 | -0.080% | -0.111% | 0% | -0.15% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1070 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c34, tf M5 | 460.8 | 30% | -0.108 | -0.051% | -0.071% | 35% | -0.41% | 9.4 | 11 | -1.0%, -1.8%, -4.0%, -2.1%, -1.2%, -1.9%, -1.3%, -0.9%, -1.0%, -3.2%, -1.4% | -0.071 | -0.042% |
| 1071 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf M30 | 7.8 | 30% | -0.108 | -0.065% | -0.090% | 43% | -0.32% | 554.3 | 0 | - | -0.020 | -0.073% |
| 1072 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf M15 | 86.3 | 44% | -0.109 | -0.052% | -0.072% | 40% | -0.48% | 50.1 | 2 | -2.6%, -1.2% | -0.011 | -0.006% |
| 1073 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop all4, tf M15 | 90.4 | 26% | -0.109 | -0.052% | -0.073% | 30% | -0.28% | 47.8 | 2 | -2.6%, -1.5% | -0.013 | -0.023% |
| 1074 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf M30 | 29.0 | 33% | -0.109 | -0.059% | -0.082% | 40% | -0.29% | 148.9 | 0 | - | -0.223 | -0.072% |
| 1075 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf M5 | 233.3 | 23% | -0.109 | -0.053% | -0.074% | 33% | -0.32% | 18.5 | 5 | -1.0%, -2.5%, -0.9%, -2.0%, -3.3% | -0.149 | -0.063% |
| 1076 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c4, tf M5 | 72.3 | 30% | -0.109 | -0.055% | -0.077% | 33% | -0.34% | 59.7 | 1 | -1.4% | -0.027 | -0.027% |
| 1077 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c4, tf M15 | 25.9 | 26% | -0.109 | -0.054% | -0.076% | 32% | -0.30% | 166.8 | 0 | - | -0.035 | -0.047% |
| 1078 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf M15 | 101.5 | 33% | -0.110 | -0.053% | -0.074% | 31% | -0.34% | 42.6 | 2 | -1.8%, -1.8% | -0.018 | -0.017% |
| 1079 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf M5 | 91.8 | 18% | -0.110 | -0.054% | -0.074% | 24% | -0.27% | 47.1 | 2 | -3.0%, -1.0% | -0.071 | -0.046% |
| 1080 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf M5 | 485.5 | 33% | -0.110 | -0.053% | -0.074% | 34% | -0.37% | 8.9 | 12 | -0.8%, -1.7%, -2.1%, -1.5%, -2.4%, +0.1%, -3.5%, -1.9%, -1.8%, -3.9%, -1.3%, -2.6% | -0.054 | -0.035% |
| 1081 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf M15 | 175.0 | 44% | -0.110 | -0.052% | -0.072% | 31% | -0.44% | 24.7 | 4 | -2.1%, -2.9%, -1.3%, -0.8% | -0.017 | -0.017% |
| 1082 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf M5 | 488.5 | 34% | -0.110 | -0.053% | -0.074% | 32% | -0.44% | 8.8 | 12 | -0.7%, -1.7%, -1.6%, -1.2%, -2.2%, -0.7%, -3.2%, -2.0%, -2.1%, -3.5%, -1.5%, -2.6% | -0.052 | -0.034% |
| 1083 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf M30 | 7.9 | 35% | -0.110 | -0.064% | -0.089% | 43% | -0.19% | 546.5 | 0 | - | -0.242 | -0.086% |
| 1084 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop all4, tf M5 | 12.9 | 46% | -0.110 | -0.055% | -0.076% | 46% | -0.29% | 334.3 | 0 | - | -0.188 | -0.079% |
| 1085 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c4, tf M15 | 27.4 | 28% | -0.110 | -0.050% | -0.069% | 22% | -0.23% | 157.7 | 0 | - | +0.082 | +0.090% |
| 1086 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c34, tf M5 | 13.1 | 36% | -0.110 | -0.050% | -0.069% | 46% | -0.28% | 328.5 | 0 | - | -0.216 | -0.078% |
| 1087 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop all4, tf M30 | 8.6 | 33% | -0.110 | -0.066% | -0.092% | 14% | -0.18% | 504.4 | 0 | - | -0.272 | -0.069% |
| 1088 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf M15 | 89.1 | 28% | -0.110 | -0.052% | -0.073% | 27% | -0.26% | 48.5 | 2 | -1.6%, -1.6% | -0.141 | -0.064% |
| 1089 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf M15 | 44.6 | 24% | -0.110 | -0.053% | -0.074% | 31% | -0.29% | 96.9 | 1 | -1.8% | +0.012 | +0.024% |
| 1090 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf M15 | 49.8 | 31% | -0.110 | -0.057% | -0.079% | 34% | -0.35% | 86.7 | 1 | -2.2% | +0.022 | +0.041% |
| 1091 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf M30 | 28.8 | 26% | -0.110 | -0.054% | -0.075% | 36% | -0.29% | 150.1 | 0 | - | -0.105 | -0.061% |
| 1092 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop all4, tf M5 | 77.6 | 34% | -0.111 | -0.055% | -0.076% | 36% | -0.38% | 55.7 | 1 | -1.3% | -0.049 | -0.037% |
| 1093 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf M5 | 54.1 | 23% | -0.111 | -0.056% | -0.078% | 35% | -0.30% | 79.8 | 1 | -1.5% | -0.125 | -0.055% |
| 1094 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf M30 | 28.8 | 25% | -0.111 | -0.052% | -0.072% | 24% | -0.25% | 150.1 | 0 | - | -0.134 | -0.061% |
| 1095 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c4, tf M30 | 14.8 | 31% | -0.111 | -0.062% | -0.086% | 31% | -0.33% | 292.0 | 0 | - | -0.236 | -0.081% |
| 1096 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf M5 | 19.7 | 28% | -0.111 | -0.042% | -0.058% | 29% | -0.36% | 219.6 | 0 | - | -0.052 | -0.038% |
| 1097 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf M5 | 19.5 | 20% | -0.111 | -0.072% | -0.100% | 18% | -0.20% | 221.4 | 0 | - | +0.116 | +0.131% |
| 1098 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf M5 | 49.8 | 29% | -0.111 | -0.057% | -0.079% | 27% | -0.26% | 86.8 | 1 | -1.5% | -0.061 | -0.044% |
| 1099 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf H1 | 26.0 | 26% | -0.111 | -0.049% | -0.068% | 17% | -0.27% | 166.1 | 0 | - | -0.201 | -0.066% |
| 1100 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf M5 | 247.7 | 34% | -0.111 | -0.054% | -0.075% | 31% | -0.38% | 17.4 | 6 | -1.8%, -1.6%, -2.1%, -2.6%, -1.8%, -1.4% | -0.035 | -0.026% |
| 1101 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf M15 | 21.2 | 23% | -0.111 | -0.057% | -0.079% | 33% | -0.22% | 203.6 | 0 | - | +0.159 | +0.767% |
| 1102 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf M30 | 28.2 | 32% | -0.111 | -0.059% | -0.082% | 40% | -0.30% | 153.1 | 0 | - | -0.223 | -0.071% |
| 1103 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf M15 | 15.1 | 30% | -0.111 | -0.057% | -0.079% | 17% | -0.31% | 285.2 | 0 | - | -0.128 | -0.081% |
| 1104 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf M5 | 33.3 | 29% | -0.112 | -0.051% | -0.071% | 28% | -0.26% | 129.6 | 0 | - | -0.097 | -0.055% |
| 1105 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf M5 | 39.4 | 22% | -0.112 | -0.053% | -0.074% | 32% | -0.29% | 109.5 | 0 | - | -0.084 | -0.052% |
| 1106 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop all4, tf M15 | 27.7 | 35% | -0.112 | -0.055% | -0.076% | 38% | -0.32% | 155.8 | 0 | - | +0.088 | +0.162% |
| 1107 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c4, tf M5 | 13.0 | 36% | -0.112 | -0.050% | -0.070% | 36% | -0.25% | 331.4 | 0 | - | -0.289 | -0.084% |
| 1108 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf M15 | 88.2 | 33% | -0.112 | -0.052% | -0.073% | 40% | -0.36% | 49.0 | 2 | -2.0%, -1.9% | +0.018 | +0.009% |
| 1109 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop all4, tf M15 | 176.9 | 26% | -0.112 | -0.054% | -0.075% | 28% | -0.27% | 24.4 | 4 | -1.4%, -3.0%, -1.2%, -2.0% | -0.012 | -0.015% |
| 1110 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf M30 | 28.9 | 32% | -0.112 | -0.060% | -0.083% | 36% | -0.28% | 149.5 | 0 | - | -0.230 | -0.071% |
| 1111 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf M15 | 87.6 | 31% | -0.112 | -0.051% | -0.071% | 38% | -0.37% | 49.3 | 2 | -2.0%, -1.8% | +0.036 | +0.035% |
| 1112 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf M15 | 39.8 | 24% | -0.112 | -0.052% | -0.073% | 26% | -0.29% | 108.6 | 0 | - | -0.186 | -0.067% |
| 1113 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf M15 | 97.7 | 26% | -0.112 | -0.054% | -0.075% | 30% | -0.32% | 44.2 | 2 | -1.5%, -1.8% | -0.021 | -0.019% |
| 1114 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf M15 | 171.1 | 31% | -0.112 | -0.054% | -0.075% | 37% | -0.37% | 25.2 | 4 | -1.5%, -2.8%, -2.2%, -1.1% | +0.022 | +0.020% |
| 1115 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf M15 | 87.5 | 44% | -0.113 | -0.052% | -0.073% | 37% | -0.43% | 49.4 | 2 | -2.9%, -0.7% | +0.034 | +0.037% |
| 1116 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf M30 | 28.1 | 23% | -0.113 | -0.050% | -0.070% | 25% | -0.23% | 153.7 | 0 | - | -0.075 | -0.042% |
| 1117 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf M5 | 54.5 | 44% | -0.113 | -0.057% | -0.079% | 25% | -0.38% | 79.3 | 1 | -2.1% | -0.056 | -0.043% |
| 1118 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf M15 | 20.4 | 22% | -0.113 | -0.056% | -0.078% | 28% | -0.29% | 211.5 | 0 | - | +0.091 | +0.282% |
| 1119 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop all4, tf M5 | 47.3 | 26% | -0.113 | -0.053% | -0.074% | 33% | -0.32% | 91.4 | 1 | -1.4% | -0.034 | -0.032% |
| 1120 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf M30 | 26.6 | 29% | -0.113 | -0.057% | -0.080% | 26% | -0.33% | 162.5 | 0 | - | +0.028 | +0.063% |
| 1121 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c34, tf M15 | 27.0 | 32% | -0.113 | -0.057% | -0.079% | 39% | -0.33% | 159.8 | 0 | - | +0.030 | +0.003% |
| 1122 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf M5 | 35.7 | 29% | -0.113 | -0.053% | -0.074% | 32% | -0.40% | 121.0 | 0 | - | -0.075 | -0.041% |
| 1123 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf M5 | 116.4 | 19% | -0.114 | -0.055% | -0.077% | 23% | -0.26% | 37.1 | 2 | -3.3%, -2.2% | -0.095 | -0.052% |
| 1124 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf H1 | 3.2 | 39% | -0.114 | -0.057% | -0.080% | 50% | -0.09% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1125 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf M30 | 28.8 | 25% | -0.114 | -0.052% | -0.072% | 28% | -0.24% | 150.1 | 0 | - | -0.075 | -0.043% |
| 1126 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop all4, tf M5 | 13.3 | 32% | -0.114 | -0.051% | -0.071% | 46% | -0.36% | 325.7 | 0 | - | -0.199 | -0.073% |
| 1127 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c4, tf M15 | 26.9 | 29% | -0.114 | -0.057% | -0.080% | 30% | -0.31% | 160.4 | 0 | - | -0.010 | -0.008% |
| 1128 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c34, tf M15 | 27.4 | 34% | -0.114 | -0.058% | -0.081% | 30% | -0.36% | 157.7 | 0 | - | +0.084 | +0.194% |
| 1129 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf M5 | 21.9 | 22% | -0.115 | -0.070% | -0.098% | 21% | -0.28% | 196.9 | 0 | - | -0.038 | -0.033% |
| 1130 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c4, tf M5 | 43.5 | 24% | -0.115 | -0.053% | -0.074% | 26% | -0.30% | 99.2 | 1 | -1.8% | -0.054 | -0.028% |
| 1131 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf M15 | 14.8 | 23% | -0.115 | -0.058% | -0.080% | 25% | -0.24% | 292.0 | 0 | - | +0.252 | +1.607% |
| 1132 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf M5 | 25.2 | 44% | -0.116 | -0.059% | -0.081% | 27% | -0.25% | 171.5 | 0 | - | -0.084 | -0.058% |
| 1133 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c34, tf M15 | 27.2 | 45% | -0.116 | -0.059% | -0.081% | 22% | -0.43% | 159.1 | 0 | - | -0.023 | -0.036% |
| 1134 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf M5 | 19.5 | 22% | -0.116 | -0.067% | -0.093% | 24% | -0.24% | 221.4 | 0 | - | -0.005 | -0.040% |
| 1135 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf M5 | 249.8 | 44% | -0.116 | -0.054% | -0.074% | 30% | -0.58% | 17.3 | 6 | -1.9%, -2.5%, -1.9%, -2.4%, -1.6%, -1.1% | -0.061 | -0.035% |
| 1136 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf H1 | 3.5 | 40% | -0.116 | -0.064% | -0.090% | 33% | -0.09% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 1137 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c34, tf M5 | 462.4 | 31% | -0.116 | -0.055% | -0.076% | 33% | -0.33% | 9.3 | 11 | -1.3%, -1.8%, -2.7%, -2.6%, -0.9%, -2.2%, -1.5%, -2.1%, -1.0%, -3.7%, -1.4% | -0.036 | -0.027% |
| 1138 | buffer 0.5, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf M15 | 88.1 | 33% | -0.116 | -0.053% | -0.073% | 35% | -0.34% | 49.0 | 2 | -2.3%, -1.7% | +0.010 | +0.001% |
| 1139 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf M15 | 10.3 | 21% | -0.116 | -0.059% | -0.081% | 33% | -0.26% | 418.3 | 0 | - | +0.084 | +0.373% |
| 1140 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf M15 | 21.2 | 25% | -0.116 | -0.059% | -0.082% | 28% | -0.21% | 203.6 | 0 | - | +0.122 | +0.471% |
| 1141 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf H1 | 21.9 | 33% | -0.116 | -0.056% | -0.078% | 42% | -0.32% | 197.7 | 0 | - | -0.061 | -0.034% |
| 1142 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c34, tf M15 | 27.5 | 45% | -0.116 | -0.058% | -0.081% | 33% | -0.43% | 157.1 | 0 | - | +0.048 | +0.045% |
| 1143 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf M5 | 24.6 | 43% | -0.117 | -0.060% | -0.083% | 23% | -0.25% | 175.4 | 0 | - | -0.052 | -0.042% |
| 1144 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf M30 | 28.6 | 30% | -0.117 | -0.053% | -0.074% | 32% | -0.30% | 151.3 | 0 | - | -0.114 | -0.065% |
| 1145 | buffer 0.5, clear 0.05, entry close, exit trail2, grade AB, stop all4, tf M5 | 491.5 | 34% | -0.117 | -0.055% | -0.076% | 34% | -0.40% | 8.8 | 12 | -1.0%, -1.8%, -1.6%, -1.2%, -2.7%, -0.5%, -2.8%, -2.3%, -2.2%, -3.2%, -2.3%, -2.2% | -0.057 | -0.037% |
| 1146 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf M30 | 7.1 | 16% | -0.117 | -0.064% | -0.089% | 17% | -0.17% | 606.7 | 0 | - | +0.154 | +0.021% |
| 1147 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c4, tf M15 | 178.7 | 27% | -0.117 | -0.056% | -0.077% | 29% | -0.31% | 24.2 | 4 | -1.7%, -3.2%, -1.1%, -1.9% | -0.024 | -0.023% |
| 1148 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf H1 | 22.0 | 40% | -0.117 | -0.049% | -0.068% | 37% | -0.34% | 196.7 | 0 | - | +0.017 | -0.001% |
| 1149 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf M30 | 28.7 | 28% | -0.117 | -0.053% | -0.073% | 40% | -0.29% | 150.7 | 0 | - | -0.099 | -0.057% |
| 1150 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c34, tf M15 | 14.9 | 30% | -0.118 | -0.055% | -0.076% | 42% | -0.33% | 290.7 | 0 | - | +0.002 | -0.010% |
| 1151 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf M30 | 7.8 | 29% | -0.118 | -0.065% | -0.090% | 29% | -0.25% | 554.3 | 0 | - | -0.383 | -0.074% |
| 1152 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf M30 | 52.5 | 43% | -0.118 | -0.061% | -0.084% | 23% | -0.31% | 82.3 | 1 | -2.1% | +0.003 | -0.007% |
| 1153 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf M5 | 251.1 | 30% | -0.118 | -0.056% | -0.078% | 36% | -0.47% | 17.2 | 6 | -1.6%, -1.7%, -1.4%, -1.6%, -3.0%, -2.2% | -0.108 | -0.054% |
| 1154 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c4, tf M15 | 27.2 | 45% | -0.118 | -0.057% | -0.079% | 22% | -0.35% | 159.1 | 0 | - | +0.059 | +0.054% |
| 1155 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf M5 | 487.4 | 44% | -0.119 | -0.055% | -0.076% | 30% | -0.43% | 8.9 | 12 | -1.7%, -0.9%, -2.3%, -1.6%, -2.3%, -2.0%, -2.9%, -1.1%, -2.7%, -2.9%, -0.8%, -2.9% | -0.089 | -0.049% |
| 1156 | buffer 0.5, clear 0.1, entry close, exit 3R, grade AB, stop c4, tf M15 | 88.1 | 28% | -0.119 | -0.053% | -0.074% | 33% | -0.33% | 49.0 | 2 | -2.1%, -1.9% | -0.002 | -0.010% |
| 1157 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf M15 | 49.1 | 28% | -0.119 | -0.056% | -0.077% | 21% | -0.27% | 88.0 | 1 | -2.2% | -0.069 | -0.043% |
| 1158 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop all4, tf M15 | 180.0 | 27% | -0.119 | -0.056% | -0.078% | 30% | -0.32% | 24.0 | 4 | -1.5%, -3.0%, -1.6%, -1.7% | -0.024 | -0.023% |
| 1159 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf M5 | 76.2 | 20% | -0.119 | -0.058% | -0.080% | 22% | -0.23% | 56.7 | 1 | -2.9% | -0.064 | -0.044% |
| 1160 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf M15 | 45.0 | 25% | -0.119 | -0.055% | -0.076% | 22% | -0.27% | 95.9 | 1 | -1.8% | -0.166 | -0.064% |
| 1161 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf M5 | 147.5 | 17% | -0.119 | -0.056% | -0.078% | 26% | -0.26% | 29.3 | 3 | -2.7%, -1.8%, -2.1% | -0.124 | -0.060% |
| 1162 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf M15 | 12.3 | 18% | -0.119 | -0.065% | -0.090% | 20% | -0.16% | 350.3 | 0 | - | -0.013 | -0.055% |
| 1163 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf M15 | 10.9 | 18% | -0.119 | -0.065% | -0.091% | 11% | -0.20% | 396.7 | 0 | - | +0.103 | +0.729% |
| 1164 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf M5 | 147.6 | 24% | -0.119 | -0.057% | -0.079% | 28% | -0.27% | 29.3 | 3 | -2.7%, -0.7%, -2.5% | -0.127 | -0.060% |
| 1165 | buffer 0.0, clear 0.05, entry close, exit 2R, grade AB, stop c4, tf M5 | 439.0 | 29% | -0.119 | -0.054% | -0.075% | 33% | -0.42% | 9.8 | 10 | -1.2%, -2.0%, -2.9%, -2.7%, -1.6%, -1.5%, -2.0%, -2.1%, -1.7%, -2.0% | -0.059 | -0.037% |
| 1166 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf H1 | 21.7 | 40% | -0.119 | -0.051% | -0.071% | 42% | -0.35% | 198.7 | 0 | - | +0.003 | -0.016% |
| 1167 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop all4, tf M5 | 45.5 | 44% | -0.120 | -0.055% | -0.076% | 25% | -0.41% | 95.0 | 1 | -2.4% | -0.071 | -0.039% |
| 1168 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf H4 | 4.6 | 41% | -0.120 | -0.068% | -0.094% | 33% | -0.26% | 940.5 | 0 | - | -0.061 | +0.147% |
| 1169 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf M15 | 20.9 | 22% | -0.120 | -0.058% | -0.081% | 22% | -0.23% | 206.9 | 0 | - | +0.139 | +0.589% |
| 1170 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop all4, tf M5 | 13.3 | 37% | -0.120 | -0.052% | -0.072% | 36% | -0.30% | 325.7 | 0 | - | -0.220 | -0.079% |
| 1171 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf M5 | 4.4 | 42% | -0.120 | -0.028% | -0.039% | 0% | -0.29% | 976.7 | 0 | - | +0.000 | +0.000% |
| 1172 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf M15 | 99.8 | 27% | -0.120 | -0.056% | -0.078% | 33% | -0.32% | 43.3 | 2 | -1.5%, -2.2% | -0.006 | -0.006% |
| 1173 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf M15 | 177.4 | 44% | -0.120 | -0.054% | -0.075% | 32% | -0.46% | 24.4 | 4 | -1.6%, -2.7%, -2.3%, -0.9% | +0.015 | +0.011% |
| 1174 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf M30 | 49.1 | 28% | -0.120 | -0.060% | -0.083% | 34% | -0.27% | 87.9 | 1 | -2.0% | +0.012 | +0.009% |
| 1175 | buffer 0.0, clear 0.05, entry close, exit trail2, grade AB, stop c4, tf M5 | 440.1 | 29% | -0.120 | -0.056% | -0.078% | 31% | -0.42% | 9.8 | 10 | -1.2%, -2.0%, -1.6%, -3.1%, -0.9%, -1.7%, -2.8%, -1.9%, -2.6%, -2.4% | -0.033 | -0.024% |
| 1176 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf M5 | 485.6 | 44% | -0.120 | -0.055% | -0.076% | 28% | -0.47% | 8.9 | 12 | -1.5%, -1.4%, -2.4%, -1.3%, -2.2%, -2.0%, -3.2%, -1.3%, -2.4%, -3.6%, -0.6%, -1.9% | -0.100 | -0.050% |
| 1177 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c4, tf M15 | 14.9 | 29% | -0.120 | -0.054% | -0.075% | 33% | -0.31% | 290.7 | 0 | - | -0.006 | -0.016% |
| 1178 | buffer 0.5, clear 0.1, entry close, exit trail2, grade AB, stop all4, tf M5 | 251.6 | 35% | -0.120 | -0.055% | -0.076% | 34% | -0.43% | 17.2 | 6 | -1.5%, -1.6%, -2.3%, -3.0%, -1.5%, -1.6% | -0.035 | -0.025% |
| 1179 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c34, tf M15 | 178.6 | 27% | -0.121 | -0.056% | -0.078% | 28% | -0.37% | 24.2 | 4 | -1.7%, -2.9%, -1.3%, -2.2% | -0.011 | -0.014% |
| 1180 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf M5 | 252.8 | 29% | -0.121 | -0.056% | -0.078% | 33% | -0.43% | 17.1 | 6 | -1.7%, -1.6%, -1.5%, -1.4%, -3.2%, -2.3% | -0.131 | -0.060% |
| 1181 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf M5 | 53.0 | 44% | -0.121 | -0.056% | -0.078% | 36% | -0.36% | 81.5 | 1 | -1.9% | -0.038 | -0.026% |
| 1182 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop all4, tf M5 | 12.9 | 26% | -0.121 | -0.049% | -0.069% | 46% | -0.28% | 334.3 | 0 | - | -0.282 | -0.084% |
| 1183 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf M5 | 76.0 | 17% | -0.121 | -0.057% | -0.079% | 25% | -0.25% | 56.8 | 1 | -2.8% | -0.030 | -0.024% |
| 1184 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop all4, tf M15 | 27.7 | 45% | -0.122 | -0.058% | -0.081% | 38% | -0.29% | 155.8 | 0 | - | +0.056 | +0.075% |
| 1185 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c34, tf M15 | 4.2 | 28% | -0.122 | -0.012% | -0.017% | 0% | -0.40% | 1029.8 | 0 | - | +0.108 | +0.073% |
| 1186 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf M15 | 11.4 | 28% | -0.122 | -0.065% | -0.090% | 30% | -0.20% | 377.3 | 0 | - | +0.028 | +0.185% |
| 1187 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf M5 | 247.7 | 44% | -0.122 | -0.056% | -0.078% | 30% | -0.47% | 17.4 | 6 | -2.1%, -2.6%, -1.9%, -1.9%, -1.8%, -1.5% | -0.062 | -0.036% |
| 1188 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c34, tf H1 | 7.2 | 42% | -0.122 | -0.047% | -0.066% | 33% | -0.35% | 597.7 | 0 | - | +0.003 | +0.185% |
| 1189 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf M5 | 250.6 | 44% | -0.122 | -0.056% | -0.078% | 30% | -0.39% | 17.2 | 6 | -1.7%, -2.9%, -1.9%, -2.4%, -1.0%, -1.8% | -0.055 | -0.036% |
| 1190 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf M30 | 27.3 | 30% | -0.122 | -0.058% | -0.080% | 21% | -0.29% | 158.4 | 0 | - | -0.001 | -0.027% |
| 1191 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf M30 | 28.6 | 31% | -0.122 | -0.054% | -0.075% | 44% | -0.31% | 151.3 | 0 | - | -0.031 | -0.043% |
| 1192 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf M30 | 27.3 | 21% | -0.122 | -0.052% | -0.073% | 17% | -0.25% | 158.4 | 0 | - | -0.115 | -0.056% |
| 1193 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf M15 | 47.6 | 28% | -0.122 | -0.057% | -0.079% | 26% | -0.25% | 90.7 | 1 | -2.4% | -0.118 | -0.056% |
| 1194 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop all4, tf M5 | 246.0 | 27% | -0.123 | -0.056% | -0.078% | 29% | -0.37% | 17.6 | 6 | -1.6%, -2.8%, -3.0%, -2.1%, -2.3%, +0.1% | -0.060 | -0.039% |
| 1195 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf M15 | 11.0 | 16% | -0.123 | -0.065% | -0.091% | 22% | -0.22% | 392.7 | 0 | - | +0.176 | +2.558% |
| 1196 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf M5 | 125.9 | 19% | -0.123 | -0.059% | -0.081% | 21% | -0.25% | 34.3 | 3 | -3.0%, -2.8%, -0.3% | -0.147 | -0.062% |
| 1197 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf H1 | 5.7 | 42% | -0.123 | -0.076% | -0.106% | 0% | -0.23% | 754.8 | 0 | - | +0.240 | +2.017% |
| 1198 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf M5 | 5.2 | 24% | -0.123 | -0.039% | -0.054% | 25% | -0.17% | 824.8 | 0 | - | +0.000 | +0.000% |
| 1199 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf M15 | 47.4 | 26% | -0.123 | -0.056% | -0.078% | 26% | -0.23% | 91.2 | 1 | -1.9% | -0.183 | -0.068% |
| 1200 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.123 | -0.083% | -0.115% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1201 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf M15 | 171.6 | 44% | -0.123 | -0.055% | -0.077% | 32% | -0.37% | 25.2 | 4 | -1.8%, -3.2%, -1.9%, -1.1% | -0.029 | -0.023% |
| 1202 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf M15 | 95.2 | 30% | -0.124 | -0.059% | -0.082% | 28% | -0.33% | 45.4 | 2 | -1.7%, -2.4% | -0.032 | -0.025% |
| 1203 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf H1 | 3.1 | 33% | -0.124 | -0.070% | -0.097% | 50% | -0.20% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 1204 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c34, tf M30 | 14.9 | 45% | -0.124 | -0.059% | -0.082% | 38% | -0.39% | 289.8 | 0 | - | -0.271 | -0.082% |
| 1205 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf H1 | 3.2 | 43% | -0.124 | -0.056% | -0.078% | 50% | -0.09% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1206 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop all4, tf M5 | 77.6 | 44% | -0.124 | -0.059% | -0.082% | 23% | -0.41% | 55.7 | 1 | -1.7% | -0.080 | -0.046% |
| 1207 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c34, tf M5 | 236.7 | 30% | -0.125 | -0.055% | -0.077% | 31% | -0.42% | 18.3 | 5 | -1.9%, -3.4%, -1.0%, -0.9%, -2.4% | -0.046 | -0.034% |
| 1208 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf H1 | 3.2 | 39% | -0.125 | -0.056% | -0.078% | 50% | -0.08% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1209 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf M5 | 91.9 | 22% | -0.125 | -0.059% | -0.081% | 30% | -0.26% | 47.0 | 2 | -3.0%, -1.7% | -0.065 | -0.043% |
| 1210 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf M15 | 44.6 | 29% | -0.125 | -0.058% | -0.080% | 23% | -0.23% | 96.9 | 1 | -2.0% | -0.020 | -0.012% |
| 1211 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf M15 | 47.4 | 24% | -0.125 | -0.060% | -0.083% | 29% | -0.28% | 91.2 | 1 | -2.2% | -0.048 | -0.031% |
| 1212 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf M30 | 5.6 | 33% | -0.125 | -0.051% | -0.071% | 50% | -0.30% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1213 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf H1 | 21.5 | 39% | -0.126 | -0.051% | -0.070% | 32% | -0.25% | 200.8 | 0 | - | -0.032 | -0.029% |
| 1214 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf M15 | 20.9 | 23% | -0.126 | -0.061% | -0.084% | 28% | -0.24% | 206.9 | 0 | - | +0.152 | +0.664% |
| 1215 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf M15 | 11.0 | 26% | -0.126 | -0.063% | -0.087% | 22% | -0.23% | 392.7 | 0 | - | +0.101 | +0.535% |
| 1216 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf M30 | 55.4 | 31% | -0.126 | -0.059% | -0.082% | 26% | -0.38% | 77.9 | 1 | -2.8% | -0.224 | -0.071% |
| 1217 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf M5 | 244.0 | 44% | -0.126 | -0.056% | -0.078% | 27% | -0.41% | 17.7 | 6 | -2.2%, -2.6%, -1.9%, -1.7%, -1.5%, -2.4% | -0.073 | -0.042% |
| 1218 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c34, tf M5 | 13.1 | 37% | -0.126 | -0.058% | -0.081% | 36% | -0.25% | 328.5 | 0 | - | -0.079 | -0.063% |
| 1219 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf M15 | 44.9 | 19% | -0.126 | -0.058% | -0.081% | 25% | -0.20% | 96.2 | 1 | -2.4% | -0.079 | -0.047% |
| 1220 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf M30 | 50.8 | 29% | -0.126 | -0.061% | -0.085% | 29% | -0.37% | 85.0 | 1 | -1.9% | +0.023 | +0.011% |
| 1221 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c4, tf M5 | 72.2 | 24% | -0.127 | -0.059% | -0.082% | 31% | -0.32% | 59.8 | 1 | -1.5% | -0.042 | -0.032% |
| 1222 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop all4, tf H1 | 7.3 | 35% | -0.127 | -0.053% | -0.073% | 17% | -0.30% | 588.5 | 0 | - | -0.280 | -0.059% |
| 1223 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf M5 | 5.8 | 20% | -0.127 | -0.033% | -0.046% | 40% | -0.47% | 742.3 | 0 | - | +0.000 | +0.000% |
| 1224 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf H1 | 21.4 | 40% | -0.127 | -0.051% | -0.071% | 42% | -0.31% | 201.8 | 0 | - | -0.006 | -0.020% |
| 1225 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf M5 | 17.0 | 28% | -0.127 | -0.064% | -0.089% | 20% | -0.23% | 253.4 | 0 | - | -0.082 | -0.059% |
| 1226 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf M5 | 5.4 | 28% | -0.128 | -0.039% | -0.054% | 25% | -0.30% | 806.8 | 0 | - | +0.000 | +0.000% |
| 1227 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf M5 | 23.4 | 43% | -0.128 | -0.062% | -0.087% | 30% | -0.25% | 184.6 | 0 | - | -0.085 | -0.051% |
| 1228 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf M15 | 10.9 | 28% | -0.129 | -0.071% | -0.098% | 33% | -0.18% | 396.7 | 0 | - | -0.135 | -0.022% |
| 1229 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf M15 | 20.7 | 32% | -0.129 | -0.060% | -0.083% | 28% | -0.34% | 209.2 | 0 | - | +0.117 | +0.697% |
| 1230 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf M15 | 12.3 | 29% | -0.129 | -0.060% | -0.083% | 20% | -0.23% | 350.3 | 0 | - | -0.097 | -0.075% |
| 1231 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.129 | -0.074% | -0.103% | 67% | -0.19% | 940.5 | 0 | - | +0.225 | +5.017% |
| 1232 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf M5 | 242.1 | 29% | -0.129 | -0.058% | -0.080% | 31% | -0.35% | 17.8 | 6 | -2.0%, -1.3%, -2.5%, -1.3%, -3.1%, -2.2% | -0.142 | -0.062% |
| 1233 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop all4, tf H1 | 7.2 | 38% | -0.129 | -0.054% | -0.075% | 17% | -0.28% | 597.7 | 0 | - | -0.183 | -0.044% |
| 1234 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf M15 | 20.4 | 32% | -0.129 | -0.060% | -0.083% | 22% | -0.23% | 211.5 | 0 | - | +0.106 | +0.616% |
| 1235 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf M15 | 77.0 | 23% | -0.130 | -0.056% | -0.078% | 32% | -0.28% | 56.1 | 1 | -2.2% | -0.027 | -0.024% |
| 1236 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf M15 | 86.3 | 30% | -0.130 | -0.055% | -0.077% | 39% | -0.34% | 50.1 | 2 | -2.8%, -1.6% | +0.068 | +0.079% |
| 1237 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf M15 | 20.9 | 24% | -0.130 | -0.063% | -0.087% | 28% | -0.26% | 206.9 | 0 | - | +0.107 | +0.363% |
| 1238 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c34, tf M5 | 46.5 | 35% | -0.130 | -0.061% | -0.084% | 37% | -0.34% | 93.0 | 1 | -2.1% | -0.023 | -0.017% |
| 1239 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf M15 | 10.9 | 21% | -0.130 | -0.063% | -0.088% | 22% | -0.24% | 396.7 | 0 | - | +0.080 | +0.364% |
| 1240 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf M5 | 484.6 | 44% | -0.130 | -0.057% | -0.079% | 29% | -0.40% | 8.9 | 12 | -1.3%, -1.5%, -2.8%, -1.6%, -2.2%, -1.1%, -4.0%, -1.5%, -2.3%, -3.5%, -1.1%, -2.2% | -0.088 | -0.046% |
| 1241 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c34, tf M5 | 237.3 | 31% | -0.130 | -0.057% | -0.079% | 28% | -0.36% | 18.2 | 5 | -1.8%, -2.6%, -2.6%, -1.5%, -2.1% | -0.008 | -0.010% |
| 1242 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf M15 | 7.5 | 30% | -0.130 | -0.056% | -0.077% | 33% | -0.31% | 578.5 | 0 | - | -0.092 | -0.061% |
| 1243 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c4, tf M5 | 12.4 | 44% | -0.130 | -0.064% | -0.089% | 20% | -0.24% | 349.6 | 0 | - | -0.298 | -0.087% |
| 1244 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf M15 | 20.9 | 24% | -0.130 | -0.063% | -0.088% | 22% | -0.24% | 206.9 | 0 | - | +0.093 | +0.296% |
| 1245 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf M5 | 21.2 | 28% | -0.131 | -0.052% | -0.072% | 22% | -0.38% | 204.2 | 0 | - | -0.087 | -0.052% |
| 1246 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf M15 | 176.8 | 43% | -0.131 | -0.058% | -0.080% | 34% | -0.36% | 24.4 | 4 | -1.8%, -3.3%, -2.0%, -0.9% | -0.032 | -0.027% |
| 1247 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop all4, tf M5 | 476.8 | 44% | -0.131 | -0.057% | -0.079% | 30% | -0.47% | 9.1 | 11 | -1.6%, -1.7%, -3.0%, -2.0%, -2.7%, -1.1%, -3.7%, -1.3%, -2.0%, -2.2%, -1.8% | -0.098 | -0.051% |
| 1248 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf M30 | 7.9 | 27% | -0.131 | -0.066% | -0.091% | 29% | -0.19% | 546.5 | 0 | - | -0.106 | -0.077% |
| 1249 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf M30 | 55.2 | 31% | -0.132 | -0.060% | -0.083% | 33% | -0.35% | 78.2 | 1 | -2.6% | -0.212 | -0.069% |
| 1250 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf M5 | 92.3 | 20% | -0.132 | -0.062% | -0.086% | 23% | -0.21% | 46.8 | 2 | -3.4%, -1.7% | -0.046 | -0.033% |
| 1251 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop all4, tf M5 | 12.9 | 35% | -0.132 | -0.055% | -0.077% | 27% | -0.26% | 334.3 | 0 | - | -0.264 | -0.084% |
| 1252 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c4, tf M30 | 8.3 | 26% | -0.132 | -0.057% | -0.080% | 43% | -0.24% | 518.1 | 0 | - | -0.256 | -0.086% |
| 1253 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c4, tf M5 | 13.0 | 36% | -0.132 | -0.059% | -0.082% | 27% | -0.24% | 331.4 | 0 | - | -0.109 | -0.070% |
| 1254 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c34, tf M30 | 8.5 | 31% | -0.132 | -0.057% | -0.079% | 43% | -0.20% | 511.2 | 0 | - | -0.377 | -0.089% |
| 1255 | buffer 0.0, clear 0.1, entry close, exit 2R, grade AB, stop c4, tf M5 | 227.8 | 29% | -0.133 | -0.057% | -0.079% | 32% | -0.32% | 19.0 | 5 | -2.4%, -3.2%, -2.2%, -0.5%, -2.2% | -0.036 | -0.027% |
| 1256 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf H4 | 4.6 | 36% | -0.133 | -0.075% | -0.104% | 67% | -0.18% | 940.5 | 0 | - | +0.102 | +1.117% |
| 1257 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c4, tf M5 | 46.0 | 34% | -0.133 | -0.060% | -0.083% | 35% | -0.27% | 93.9 | 1 | -2.1% | -0.035 | -0.026% |
| 1258 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf M5 | 185.4 | 21% | -0.133 | -0.059% | -0.082% | 33% | -0.29% | 23.3 | 4 | -2.8%, -2.9%, -1.5%, -1.9% | -0.103 | -0.052% |
| 1259 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf M15 | 39.6 | 18% | -0.133 | -0.059% | -0.082% | 31% | -0.25% | 109.2 | 0 | - | +0.003 | +0.004% |
| 1260 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf M15 | 11.4 | 17% | -0.133 | -0.065% | -0.090% | 30% | -0.18% | 377.3 | 0 | - | +0.149 | +1.422% |
| 1261 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop all4, tf M15 | 4.5 | 24% | -0.134 | -0.035% | -0.049% | 0% | -0.23% | 969.2 | 0 | - | +0.224 | +1.145% |
| 1262 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf M15 | 48.8 | 24% | -0.134 | -0.061% | -0.084% | 23% | -0.30% | 88.5 | 1 | -2.0% | -0.022 | -0.015% |
| 1263 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf M30 | 5.6 | 31% | -0.134 | -0.049% | -0.068% | 50% | -0.31% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1264 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf M30 | 52.9 | 29% | -0.134 | -0.061% | -0.084% | 36% | -0.33% | 81.6 | 1 | -2.5% | -0.192 | -0.069% |
| 1265 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf M15 | 97.7 | 30% | -0.134 | -0.061% | -0.084% | 30% | -0.35% | 44.2 | 2 | -1.7%, -2.2% | -0.050 | -0.036% |
| 1266 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf M5 | 76.0 | 20% | -0.134 | -0.061% | -0.084% | 31% | -0.24% | 56.8 | 1 | -2.6% | -0.061 | -0.040% |
| 1267 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c34, tf M5 | 13.1 | 26% | -0.135 | -0.057% | -0.079% | 27% | -0.23% | 328.5 | 0 | - | -0.163 | -0.076% |
| 1268 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf M5 | 29.0 | 21% | -0.135 | -0.056% | -0.078% | 28% | -0.28% | 148.8 | 0 | - | -0.085 | -0.045% |
| 1269 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf M15 | 14.4 | 22% | -0.135 | -0.062% | -0.086% | 33% | -0.24% | 299.2 | 0 | - | +0.202 | +0.779% |
| 1270 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf M15 | 21.0 | 33% | -0.135 | -0.062% | -0.086% | 28% | -0.30% | 205.8 | 0 | - | +0.115 | +0.642% |
| 1271 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c34, tf H1 | 7.2 | 34% | -0.135 | -0.059% | -0.082% | 33% | -0.24% | 597.7 | 0 | - | -0.387 | -0.086% |
| 1272 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c4, tf M5 | 229.7 | 26% | -0.135 | -0.058% | -0.081% | 29% | -0.39% | 18.8 | 5 | -2.2%, -2.8%, -3.0%, -1.4%, -1.7% | -0.055 | -0.036% |
| 1273 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c34, tf M5 | 252.8 | 27% | -0.135 | -0.058% | -0.081% | 26% | -0.31% | 17.1 | 6 | -1.5%, -2.9%, -2.9%, -3.2%, -1.8%, -0.6% | -0.074 | -0.044% |
| 1274 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop all4, tf M30 | 8.5 | 31% | -0.135 | -0.057% | -0.079% | 43% | -0.20% | 511.2 | 0 | - | -0.380 | -0.089% |
| 1275 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf M15 | 46.5 | 29% | -0.135 | -0.060% | -0.084% | 32% | -0.32% | 92.9 | 1 | -2.4% | +0.008 | +0.031% |
| 1276 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf M5 | 114.9 | 28% | -0.136 | -0.058% | -0.081% | 29% | -0.33% | 37.6 | 2 | -2.2%, -1.9% | -0.107 | -0.051% |
| 1277 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf M5 | 14.7 | 20% | -0.136 | -0.057% | -0.079% | 25% | -0.27% | 293.6 | 0 | - | -0.106 | -0.055% |
| 1278 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf M15 | 13.8 | 43% | -0.136 | -0.063% | -0.088% | 18% | -0.19% | 314.1 | 0 | - | -0.175 | -0.084% |
| 1279 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop all4, tf M15 | 4.1 | 42% | -0.136 | -0.082% | -0.113% | 0% | -0.14% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 1280 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf M30 | 7.7 | 27% | -0.136 | -0.067% | -0.093% | 17% | -0.27% | 560.8 | 0 | - | +0.010 | -0.076% |
| 1281 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf M30 | 55.8 | 31% | -0.136 | -0.061% | -0.085% | 38% | -0.32% | 77.5 | 1 | -2.8% | -0.213 | -0.069% |
| 1282 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop all4, tf M5 | 80.7 | 44% | -0.136 | -0.059% | -0.083% | 32% | -0.38% | 53.5 | 2 | -2.5%, -1.9% | -0.057 | -0.037% |
| 1283 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf M15 | 15.3 | 43% | -0.137 | -0.063% | -0.087% | 25% | -0.27% | 282.9 | 0 | - | -0.126 | -0.079% |
| 1284 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c34, tf M15 | 4.1 | 42% | -0.137 | -0.082% | -0.114% | 0% | -0.14% | 1063.0 | 0 | - | +0.000 | +0.000% |
| 1285 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c34, tf M30 | 8.5 | 35% | -0.137 | -0.064% | -0.088% | 14% | -0.18% | 511.2 | 0 | - | -0.445 | -0.088% |
| 1286 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf M5 | 25.3 | 24% | -0.138 | -0.067% | -0.094% | 36% | -0.23% | 170.7 | 0 | - | -0.028 | -0.032% |
| 1287 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf M15 | 96.3 | 28% | -0.138 | -0.059% | -0.083% | 24% | -0.28% | 44.8 | 2 | -1.9%, -1.6% | -0.152 | -0.064% |
| 1288 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c4, tf M15 | 20.7 | 24% | -0.138 | -0.060% | -0.084% | 17% | -0.22% | 209.2 | 0 | - | +0.111 | +0.631% |
| 1289 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf M30 | 28.9 | 25% | -0.138 | -0.057% | -0.079% | 28% | -0.24% | 149.5 | 0 | - | -0.084 | -0.047% |
| 1290 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf M5 | 147.5 | 20% | -0.138 | -0.059% | -0.083% | 30% | -0.27% | 29.3 | 3 | -2.9%, -1.7%, -2.2% | -0.129 | -0.059% |
| 1291 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf M5 | 33.3 | 28% | -0.138 | -0.062% | -0.087% | 31% | -0.23% | 129.6 | 0 | - | -0.018 | -0.036% |
| 1292 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf M15 | 39.8 | 18% | -0.138 | -0.062% | -0.086% | 26% | -0.20% | 108.6 | 0 | - | -0.068 | -0.042% |
| 1293 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf M5 | 233.5 | 28% | -0.138 | -0.059% | -0.082% | 32% | -0.32% | 18.5 | 5 | -2.4%, -2.1%, -1.9%, -1.8%, -2.8% | -0.135 | -0.061% |
| 1294 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop all4, tf M15 | 89.5 | 43% | -0.138 | -0.056% | -0.078% | 31% | -0.38% | 48.3 | 2 | -2.5%, -1.6% | +0.079 | +0.111% |
| 1295 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop c4, tf M5 | 250.3 | 26% | -0.138 | -0.059% | -0.081% | 28% | -0.36% | 17.3 | 6 | -1.6%, -2.9%, -2.9%, -3.3%, -1.3%, -0.5% | -0.068 | -0.041% |
| 1296 | buffer 0.0, clear 0.1, entry close, exit trail2, grade AB, stop c4, tf M5 | 228.3 | 30% | -0.138 | -0.059% | -0.082% | 28% | -0.31% | 18.9 | 5 | -1.8%, -2.4%, -3.2%, -0.9%, -2.1% | -0.009 | -0.009% |
| 1297 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c4, tf M5 | 12.5 | 24% | -0.139 | -0.065% | -0.090% | 27% | -0.21% | 346.5 | 0 | - | -0.137 | -0.078% |
| 1298 | buffer 0.5, clear 0.1, entry close, exit ema, grade AB, stop all4, tf M5 | 254.5 | 27% | -0.139 | -0.058% | -0.081% | 25% | -0.28% | 17.0 | 6 | -1.6%, -2.8%, -2.7%, -3.0%, -1.8%, -1.2% | -0.086 | -0.047% |
| 1299 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c4, tf M5 | 443.0 | 26% | -0.139 | -0.059% | -0.082% | 28% | -0.33% | 9.8 | 11 | -1.4%, -2.0%, -2.3%, -3.4%, -1.2%, -1.7%, -3.3%, -1.8%, -2.7%, -1.0%, -2.5% | -0.043 | -0.030% |
| 1300 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop all4, tf M5 | 13.3 | 38% | -0.139 | -0.060% | -0.083% | 36% | -0.24% | 325.7 | 0 | - | -0.086 | -0.066% |
| 1301 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c4, tf M5 | 12.4 | 32% | -0.139 | -0.058% | -0.081% | 40% | -0.19% | 349.6 | 0 | - | -0.399 | -0.089% |
| 1302 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf M5 | 21.9 | 17% | -0.139 | -0.073% | -0.101% | 21% | -0.21% | 196.9 | 0 | - | -0.065 | -0.054% |
| 1303 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf M15 | 21.0 | 33% | -0.140 | -0.062% | -0.086% | 28% | -0.30% | 205.8 | 0 | - | +0.089 | +0.484% |
| 1304 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop all4, tf M15 | 28.3 | 35% | -0.140 | -0.059% | -0.082% | 33% | -0.34% | 152.6 | 0 | - | -0.108 | -0.055% |
| 1305 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf M15 | 49.8 | 28% | -0.140 | -0.059% | -0.082% | 27% | -0.23% | 86.7 | 1 | -1.8% | -0.179 | -0.070% |
| 1306 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf M5 | 5.4 | 24% | -0.140 | -0.048% | -0.067% | 25% | -0.16% | 806.8 | 0 | - | +0.000 | +0.000% |
| 1307 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop all4, tf M5 | 47.3 | 36% | -0.141 | -0.062% | -0.086% | 36% | -0.31% | 91.4 | 1 | -2.0% | -0.021 | -0.017% |
| 1308 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf M15 | 10.4 | 15% | -0.141 | -0.066% | -0.091% | 22% | -0.19% | 413.8 | 0 | - | +0.188 | +2.774% |
| 1309 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c34, tf M5 | 12.8 | 25% | -0.141 | -0.052% | -0.072% | 36% | -0.27% | 337.3 | 0 | - | -0.154 | -0.066% |
| 1310 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop all4, tf M5 | 12.9 | 37% | -0.141 | -0.059% | -0.082% | 27% | -0.22% | 334.3 | 0 | - | -0.110 | -0.073% |
| 1311 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf M5 | 76.0 | 24% | -0.141 | -0.061% | -0.085% | 28% | -0.27% | 56.8 | 1 | -2.2% | -0.074 | -0.047% |
| 1312 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf M5 | 213.2 | 20% | -0.142 | -0.063% | -0.087% | 21% | -0.32% | 20.3 | 5 | -2.0%, -3.3%, -1.6%, -2.8%, -1.7% | -0.109 | -0.059% |
| 1313 | buffer 0.0, clear 0.1, entry close, exit ema, grade AB, stop c34, tf M5 | 239.0 | 26% | -0.142 | -0.060% | -0.083% | 26% | -0.40% | 18.1 | 5 | -2.1%, -3.0%, -2.6%, -1.7%, -3.2% | -0.040 | -0.029% |
| 1314 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf M5 | 106.5 | 26% | -0.142 | -0.061% | -0.085% | 28% | -0.28% | 40.6 | 2 | -1.5%, -2.2% | -0.099 | -0.051% |
| 1315 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf M30 | 5.6 | 45% | -0.142 | -0.068% | -0.094% | 25% | -0.28% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1316 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf M15 | 77.1 | 29% | -0.142 | -0.058% | -0.081% | 33% | -0.31% | 56.0 | 1 | -1.9% | -0.018 | -0.018% |
| 1317 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c34, tf M5 | 44.4 | 32% | -0.143 | -0.061% | -0.084% | 36% | -0.28% | 97.2 | 1 | -2.3% | -0.006 | -0.006% |
| 1318 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c34, tf M5 | 13.3 | 24% | -0.143 | -0.067% | -0.093% | 18% | -0.27% | 325.7 | 0 | - | -0.074 | -0.065% |
| 1319 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c34, tf M5 | 79.8 | 43% | -0.143 | -0.062% | -0.086% | 27% | -0.37% | 54.1 | 1 | -2.3% | -0.079 | -0.045% |
| 1320 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf M15 | 9.2 | 27% | -0.143 | -0.071% | -0.098% | 0% | -0.27% | 469.3 | 0 | - | +0.058 | +0.180% |
| 1321 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf M5 | 186.5 | 25% | -0.143 | -0.062% | -0.086% | 23% | -0.27% | 23.2 | 4 | -2.5%, -2.2%, -1.4%, -2.5% | -0.130 | -0.059% |
| 1322 | buffer 0.5, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf M15 | 176.3 | 43% | -0.143 | -0.060% | -0.083% | 30% | -0.44% | 24.5 | 4 | -1.7%, -2.8%, -2.3%, -1.7% | -0.015 | -0.014% |
| 1323 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf M30 | 51.0 | 27% | -0.143 | -0.063% | -0.087% | 18% | -0.28% | 84.6 | 1 | -2.6% | -0.189 | -0.069% |
| 1324 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c34, tf M5 | 46.5 | 43% | -0.143 | -0.062% | -0.086% | 27% | -0.29% | 93.0 | 1 | -2.3% | -0.090 | -0.047% |
| 1325 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c4, tf M5 | 13.1 | 23% | -0.144 | -0.066% | -0.092% | 9% | -0.24% | 328.5 | 0 | - | -0.137 | -0.076% |
| 1326 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c4, tf M30 | 8.3 | 34% | -0.144 | -0.067% | -0.093% | 43% | -0.19% | 518.1 | 0 | - | -0.445 | -0.089% |
| 1327 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop all4, tf M5 | 47.3 | 43% | -0.144 | -0.060% | -0.084% | 24% | -0.31% | 91.4 | 1 | -2.0% | -0.047 | -0.033% |
| 1328 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf M5 | 213.9 | 26% | -0.144 | -0.061% | -0.085% | 31% | -0.27% | 20.2 | 5 | -1.4%, -2.6%, -1.5%, -2.7%, -2.9% | -0.137 | -0.062% |
| 1329 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop all4, tf M5 | 45.5 | 34% | -0.144 | -0.060% | -0.084% | 32% | -0.34% | 95.0 | 1 | -2.2% | -0.001 | -0.004% |
| 1330 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.145 | -0.076% | -0.105% | 33% | -0.20% | 940.5 | 0 | - | +0.129 | +1.738% |
| 1331 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop all4, tf M5 | 482.0 | 26% | -0.145 | -0.060% | -0.084% | 26% | -0.40% | 9.0 | 12 | -0.9%, -2.0%, -3.1%, -2.2%, -2.7%, -0.8%, -3.6%, -1.8%, -2.6%, -3.1%, -0.7%, -2.3% | -0.050 | -0.034% |
| 1332 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf M30 | 5.5 | 44% | -0.145 | -0.060% | -0.083% | 50% | -0.24% | 782.7 | 0 | - | +0.000 | +0.000% |
| 1333 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf M5 | 35.8 | 42% | -0.145 | -0.063% | -0.087% | 29% | -0.29% | 120.6 | 0 | - | -0.129 | -0.051% |
| 1334 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf M5 | 54.0 | 34% | -0.145 | -0.061% | -0.085% | 27% | -0.29% | 80.0 | 1 | -1.9% | -0.087 | -0.047% |
| 1335 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf M15 | 7.7 | 21% | -0.146 | -0.063% | -0.087% | 33% | -0.29% | 560.2 | 0 | - | -0.014 | -0.021% |
| 1336 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c4, tf M5 | 43.5 | 30% | -0.146 | -0.060% | -0.083% | 34% | -0.24% | 99.2 | 1 | -2.1% | -0.022 | -0.019% |
| 1337 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf M15 | 86.5 | 32% | -0.147 | -0.060% | -0.084% | 32% | -0.35% | 49.9 | 2 | -2.4%, -1.8% | -0.099 | -0.049% |
| 1338 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf M15 | 172.3 | 32% | -0.147 | -0.061% | -0.084% | 32% | -0.33% | 25.1 | 4 | -2.4%, -3.1%, -1.9%, -1.2% | -0.096 | -0.051% |
| 1339 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf M15 | 20.7 | 41% | -0.147 | -0.061% | -0.085% | 28% | -0.22% | 209.2 | 0 | - | +0.068 | +0.264% |
| 1340 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf M30 | 7.7 | 28% | -0.147 | -0.070% | -0.098% | 17% | -0.21% | 562.3 | 0 | - | -0.394 | -0.074% |
| 1341 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf M15 | 99.8 | 31% | -0.148 | -0.062% | -0.086% | 30% | -0.33% | 43.3 | 2 | -1.8%, -2.1% | -0.033 | -0.026% |
| 1342 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf M15 | 97.7 | 22% | -0.148 | -0.062% | -0.086% | 25% | -0.26% | 44.2 | 2 | -1.1%, -3.2% | -0.017 | -0.019% |
| 1343 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf M15 | 47.1 | 20% | -0.148 | -0.065% | -0.091% | 33% | -0.23% | 91.8 | 1 | -2.8% | -0.121 | -0.056% |
| 1344 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf M30 | 7.0 | 18% | -0.148 | -0.063% | -0.087% | 17% | -0.17% | 616.9 | 0 | - | +0.167 | +0.478% |
| 1345 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf M5 | 24.7 | 23% | -0.148 | -0.068% | -0.094% | 36% | -0.20% | 174.6 | 0 | - | +0.011 | -0.006% |
| 1346 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c4, tf M5 | 72.3 | 32% | -0.148 | -0.063% | -0.088% | 23% | -0.27% | 59.7 | 1 | -2.4% | -0.028 | -0.029% |
| 1347 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c34, tf M5 | 12.8 | 34% | -0.148 | -0.063% | -0.087% | 18% | -0.22% | 337.3 | 0 | - | -0.104 | -0.071% |
| 1348 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop all4, tf M5 | 12.9 | 31% | -0.149 | -0.060% | -0.084% | 27% | -0.25% | 334.3 | 0 | - | -0.242 | -0.079% |
| 1349 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf M30 | 49.2 | 26% | -0.149 | -0.063% | -0.087% | 20% | -0.27% | 87.7 | 1 | -2.4% | -0.199 | -0.070% |
| 1350 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf M5 | 23.8 | 26% | -0.149 | -0.063% | -0.087% | 29% | -0.24% | 181.2 | 0 | - | -0.063 | -0.051% |
| 1351 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf M5 | 23.8 | 20% | -0.149 | -0.062% | -0.086% | 33% | -0.25% | 181.2 | 0 | - | -0.032 | -0.037% |
| 1352 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf M15 | 13.6 | 25% | -0.149 | -0.069% | -0.096% | 18% | -0.24% | 316.8 | 0 | - | -0.050 | -0.066% |
| 1353 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop all4, tf M15 | 15.3 | 29% | -0.149 | -0.063% | -0.088% | 42% | -0.29% | 281.5 | 0 | - | +0.035 | +0.026% |
| 1354 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf M5 | 23.4 | 23% | -0.149 | -0.068% | -0.095% | 30% | -0.22% | 184.6 | 0 | - | -0.000 | -0.011% |
| 1355 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf M30 | 7.7 | 26% | -0.149 | -0.070% | -0.097% | 17% | -0.21% | 560.8 | 0 | - | -0.379 | -0.072% |
| 1356 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf M5 | 35.8 | 27% | -0.150 | -0.063% | -0.088% | 19% | -0.22% | 120.6 | 0 | - | +0.020 | +0.004% |
| 1357 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf M15 | 20.4 | 28% | -0.150 | -0.062% | -0.086% | 28% | -0.31% | 211.5 | 0 | - | +0.050 | +0.291% |
| 1358 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c34, tf M30 | 14.9 | 31% | -0.150 | -0.066% | -0.092% | 38% | -0.30% | 289.8 | 0 | - | -0.215 | -0.080% |
| 1359 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf M5 | 211.7 | 27% | -0.150 | -0.061% | -0.085% | 23% | -0.46% | 20.4 | 5 | -2.0%, -2.1%, -2.8%, -1.5%, -3.0% | -0.128 | -0.059% |
| 1360 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c34, tf M5 | 12.9 | 24% | -0.150 | -0.068% | -0.095% | 27% | -0.22% | 334.3 | 0 | - | -0.137 | -0.077% |
| 1361 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf M15 | 7.4 | 19% | -0.150 | -0.055% | -0.076% | 20% | -0.17% | 582.1 | 0 | - | +0.043 | +0.030% |
| 1362 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf M5 | 92.2 | 25% | -0.150 | -0.063% | -0.088% | 28% | -0.28% | 46.8 | 2 | -2.4%, -2.0% | -0.057 | -0.036% |
| 1363 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf M5 | 91.8 | 20% | -0.150 | -0.062% | -0.087% | 23% | -0.27% | 47.1 | 2 | -3.1%, -1.5% | -0.045 | -0.030% |
| 1364 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c34, tf M5 | 12.8 | 21% | -0.150 | -0.060% | -0.083% | 46% | -0.24% | 337.3 | 0 | - | -0.159 | -0.078% |
| 1365 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf M5 | 105.4 | 27% | -0.151 | -0.060% | -0.084% | 31% | -0.30% | 41.0 | 2 | -2.1%, -2.2% | -0.113 | -0.055% |
| 1366 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf M15 | 102.2 | 42% | -0.151 | -0.062% | -0.085% | 31% | -0.41% | 42.3 | 2 | -1.8%, -2.5% | -0.047 | -0.035% |
| 1367 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf M5 | 76.0 | 20% | -0.151 | -0.063% | -0.087% | 31% | -0.26% | 56.8 | 1 | -2.9% | -0.070 | -0.040% |
| 1368 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf M15 | 88.5 | 33% | -0.151 | -0.063% | -0.087% | 32% | -0.32% | 48.8 | 2 | -2.7%, -1.8% | -0.078 | -0.042% |
| 1369 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf M30 | 27.3 | 24% | -0.151 | -0.061% | -0.085% | 21% | -0.30% | 158.4 | 0 | - | -0.117 | -0.063% |
| 1370 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf M15 | 7.2 | 20% | -0.151 | -0.065% | -0.090% | 20% | -0.28% | 598.2 | 0 | - | +0.064 | +0.361% |
| 1371 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf M15 | 7.4 | 29% | -0.151 | -0.062% | -0.085% | 0% | -0.17% | 582.1 | 0 | - | -0.101 | -0.070% |
| 1372 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf M15 | 11.6 | 42% | -0.152 | -0.066% | -0.091% | 20% | -0.26% | 373.6 | 0 | - | -0.089 | -0.002% |
| 1373 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf M15 | 88.2 | 33% | -0.152 | -0.062% | -0.086% | 30% | -0.27% | 49.0 | 2 | -2.6%, -1.6% | -0.082 | -0.043% |
| 1374 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf M5 | 5.7 | 41% | -0.152 | -0.049% | -0.067% | 50% | -0.25% | 757.4 | 0 | - | +0.000 | +0.000% |
| 1375 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c34, tf M5 | 462.0 | 42% | -0.152 | -0.060% | -0.083% | 28% | -0.40% | 9.4 | 11 | -1.9%, -2.2%, -3.4%, -2.2%, -1.5%, -2.7%, -1.6%, -2.4%, -1.1%, -2.9%, -2.0% | -0.095 | -0.049% |
| 1376 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf M5 | 186.4 | 19% | -0.152 | -0.065% | -0.090% | 23% | -0.25% | 23.2 | 4 | -2.7%, -2.7%, -2.2%, -2.9% | -0.075 | -0.050% |
| 1377 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c34, tf M5 | 74.6 | 32% | -0.153 | -0.064% | -0.088% | 27% | -0.24% | 57.9 | 1 | -2.3% | -0.049 | -0.035% |
| 1378 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c4, tf M5 | 12.4 | 33% | -0.153 | -0.063% | -0.088% | 20% | -0.19% | 349.6 | 0 | - | -0.145 | -0.074% |
| 1379 | buffer 0.0, clear 0.05, entry close, exit ema, grade AB, stop c34, tf M5 | 466.0 | 26% | -0.153 | -0.062% | -0.086% | 27% | -0.32% | 9.3 | 11 | -1.5%, -1.9%, -3.2%, -2.7%, -1.6%, -1.6%, -2.9%, -2.2%, -2.2%, -3.3%, -1.5% | -0.036 | -0.027% |
| 1380 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf M15 | 9.2 | 20% | -0.153 | -0.076% | -0.105% | 12% | -0.20% | 469.3 | 0 | - | -0.050 | +0.037% |
| 1381 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf M15 | 88.1 | 42% | -0.153 | -0.061% | -0.085% | 33% | -0.33% | 49.0 | 2 | -2.7%, -1.6% | +0.010 | +0.004% |
| 1382 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf M5 | 17.8 | 24% | -0.153 | -0.058% | -0.081% | 33% | -0.25% | 242.3 | 0 | - | -0.007 | -0.002% |
| 1383 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf M15 | 13.6 | 30% | -0.153 | -0.070% | -0.097% | 18% | -0.25% | 316.8 | 0 | - | -0.152 | -0.080% |
| 1384 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c34, tf M15 | 27.8 | 34% | -0.153 | -0.060% | -0.083% | 38% | -0.38% | 155.2 | 0 | - | -0.130 | -0.060% |
| 1385 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop all4, tf H1 | 7.2 | 36% | -0.153 | -0.066% | -0.091% | 33% | -0.25% | 597.7 | 0 | - | -0.373 | -0.086% |
| 1386 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf M5 | 76.0 | 26% | -0.154 | -0.062% | -0.086% | 28% | -0.29% | 56.8 | 1 | -2.9% | -0.058 | -0.038% |
| 1387 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf H1 | 21.7 | 39% | -0.154 | -0.060% | -0.083% | 37% | -0.29% | 198.7 | 0 | - | +0.004 | -0.010% |
| 1388 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf M5 | 120.2 | 42% | -0.154 | -0.060% | -0.084% | 29% | -0.36% | 36.0 | 3 | -1.6%, -2.3%, -2.5% | -0.145 | -0.062% |
| 1389 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf M5 | 441.2 | 32% | -0.154 | -0.063% | -0.087% | 25% | -0.32% | 9.8 | 11 | -2.0%, -2.2%, -1.6%, -2.8%, -2.9%, -2.2%, -2.9%, -1.9%, -1.4%, -2.5%, -2.6% | -0.045 | -0.030% |
| 1390 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf M15 | 20.9 | 28% | -0.154 | -0.064% | -0.089% | 22% | -0.26% | 206.9 | 0 | - | +0.053 | +0.283% |
| 1391 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c34, tf M30 | 8.6 | 32% | -0.154 | -0.062% | -0.086% | 43% | -0.20% | 504.4 | 0 | - | -0.305 | -0.088% |
| 1392 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf M5 | 17.0 | 16% | -0.154 | -0.069% | -0.096% | 27% | -0.20% | 253.4 | 0 | - | -0.004 | -0.023% |
| 1393 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c34, tf M5 | 12.8 | 43% | -0.154 | -0.065% | -0.090% | 18% | -0.28% | 337.3 | 0 | - | -0.156 | -0.077% |
| 1394 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop all4, tf M5 | 13.4 | 25% | -0.154 | -0.068% | -0.094% | 18% | -0.26% | 323.0 | 0 | - | -0.065 | -0.066% |
| 1395 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf M15 | 176.4 | 32% | -0.154 | -0.062% | -0.086% | 31% | -0.35% | 24.5 | 4 | -2.2%, -3.5%, -1.8%, -1.4% | -0.084 | -0.048% |
| 1396 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c4, tf M5 | 78.9 | 42% | -0.155 | -0.064% | -0.088% | 26% | -0.30% | 54.7 | 1 | -2.4% | -0.090 | -0.048% |
| 1397 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf M15 | 51.0 | 28% | -0.155 | -0.063% | -0.087% | 24% | -0.28% | 84.8 | 1 | -2.1% | -0.215 | -0.075% |
| 1398 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c34, tf M5 | 495.2 | 26% | -0.155 | -0.062% | -0.086% | 26% | -0.30% | 8.7 | 12 | -1.1%, -2.0%, -3.2%, -1.6%, -3.3%, -1.4%, -2.7%, -3.7%, -1.4%, -2.8%, -1.6%, -1.7% | -0.060 | -0.039% |
| 1399 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c4, tf M30 | 14.5 | 42% | -0.155 | -0.063% | -0.087% | 31% | -0.30% | 298.8 | 0 | - | +0.048 | +0.070% |
| 1400 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf M5 | 37.4 | 41% | -0.156 | -0.067% | -0.093% | 18% | -0.23% | 115.5 | 0 | - | -0.090 | -0.042% |
| 1401 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c4, tf M30 | 8.6 | 36% | -0.156 | -0.067% | -0.093% | 29% | -0.21% | 504.4 | 0 | - | -0.470 | -0.089% |
| 1402 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf M5 | 51.9 | 42% | -0.156 | -0.064% | -0.089% | 26% | -0.32% | 83.2 | 1 | -1.9% | +0.000 | +0.004% |
| 1403 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop c4, tf M5 | 491.9 | 26% | -0.156 | -0.062% | -0.087% | 25% | -0.31% | 8.8 | 12 | -1.1%, -2.0%, -3.2%, -2.0%, -3.3%, -0.6%, -3.6%, -3.3%, -1.6%, -2.8%, -1.4%, -2.0% | -0.056 | -0.037% |
| 1404 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c34, tf M5 | 74.6 | 29% | -0.156 | -0.064% | -0.088% | 35% | -0.30% | 57.9 | 1 | -1.8% | -0.037 | -0.027% |
| 1405 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c34, tf M15 | 4.2 | 41% | -0.156 | -0.077% | -0.107% | 0% | -0.21% | 1029.8 | 0 | - | +0.123 | +0.267% |
| 1406 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf M5 | 21.8 | 41% | -0.157 | -0.059% | -0.082% | 32% | -0.34% | 197.8 | 0 | - | -0.102 | -0.056% |
| 1407 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf M15 | 50.2 | 41% | -0.157 | -0.065% | -0.090% | 25% | -0.29% | 86.1 | 1 | -2.6% | +0.024 | +0.043% |
| 1408 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c34, tf M5 | 12.8 | 33% | -0.157 | -0.062% | -0.086% | 36% | -0.19% | 337.3 | 0 | - | -0.269 | -0.083% |
| 1409 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c34, tf H4 | 4.7 | 38% | -0.157 | -0.079% | -0.110% | 25% | -0.14% | 917.0 | 0 | - | +0.105 | +1.274% |
| 1410 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf M5 | 236.9 | 27% | -0.157 | -0.063% | -0.087% | 27% | -0.28% | 18.2 | 5 | -1.9%, -2.3%, -2.1%, -1.3%, -3.4% | -0.136 | -0.062% |
| 1411 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c4, tf H1 | 7.6 | 36% | -0.157 | -0.061% | -0.085% | 17% | -0.22% | 571.0 | 0 | - | -0.292 | -0.087% |
| 1412 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf M5 | 54.5 | 34% | -0.157 | -0.063% | -0.087% | 27% | -0.29% | 79.3 | 1 | -2.1% | -0.101 | -0.052% |
| 1413 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf M5 | 21.2 | 24% | -0.158 | -0.061% | -0.084% | 28% | -0.27% | 204.2 | 0 | - | -0.053 | -0.030% |
| 1414 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf M5 | 116.2 | 26% | -0.158 | -0.064% | -0.089% | 27% | -0.26% | 37.2 | 2 | -1.8%, -2.1% | -0.113 | -0.055% |
| 1415 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf M5 | 237.3 | 19% | -0.158 | -0.065% | -0.091% | 21% | -0.27% | 18.2 | 5 | -2.5%, -3.5%, -1.6%, -2.6%, -3.4% | -0.116 | -0.061% |
| 1416 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf M30 | 7.8 | 23% | -0.158 | -0.066% | -0.091% | 29% | -0.30% | 554.3 | 0 | - | +0.097 | -0.001% |
| 1417 | buffer 0.5, clear 0.05, entry close, exit ema, grade AB, stop all4, tf M5 | 498.7 | 26% | -0.158 | -0.062% | -0.087% | 25% | -0.36% | 8.7 | 12 | -1.1%, -2.1%, -3.1%, -1.6%, -3.4%, -1.0%, -2.6%, -3.7%, -1.6%, -3.0%, -1.8%, -1.4% | -0.065 | -0.041% |
| 1418 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf M5 | 464.9 | 32% | -0.159 | -0.063% | -0.087% | 24% | -0.33% | 9.3 | 11 | -2.0%, -2.1%, -2.7%, -2.2%, -2.9%, -2.9%, -1.2%, -2.4%, -1.1%, -3.0%, -2.5% | -0.058 | -0.037% |
| 1419 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop all4, tf M15 | 4.5 | 24% | -0.159 | -0.053% | -0.074% | 0% | -0.21% | 969.2 | 0 | - | +0.175 | +0.549% |
| 1420 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf M15 | 89.4 | 33% | -0.159 | -0.065% | -0.090% | 32% | -0.27% | 48.3 | 2 | -2.6%, -2.0% | -0.122 | -0.056% |
| 1421 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf M5 | 147.6 | 26% | -0.159 | -0.063% | -0.087% | 24% | -0.29% | 29.3 | 3 | -2.6%, -2.0%, -2.6% | -0.120 | -0.056% |
| 1422 | buffer 0.0, clear 0.05, entry close, exit 1R, grade AB, stop c4, tf M5 | 439.7 | 42% | -0.159 | -0.062% | -0.087% | 24% | -0.40% | 9.8 | 10 | -1.9%, -2.5%, -2.7%, -2.1%, -2.2%, -2.1%, -2.8%, -3.5%, -1.3%, -1.9% | -0.097 | -0.049% |
| 1423 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf M15 | 20.5 | 19% | -0.159 | -0.065% | -0.090% | 28% | -0.24% | 210.3 | 0 | - | +0.137 | +0.507% |
| 1424 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c34, tf M5 | 44.4 | 29% | -0.159 | -0.064% | -0.089% | 33% | -0.33% | 97.2 | 1 | -2.4% | -0.085 | -0.044% |
| 1425 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf M5 | 29.0 | 26% | -0.160 | -0.065% | -0.090% | 20% | -0.22% | 148.8 | 0 | - | +0.015 | -0.013% |
| 1426 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf H1 | 3.5 | 40% | -0.160 | -0.065% | -0.090% | 33% | -0.11% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 1427 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf M5 | 21.9 | 27% | -0.160 | -0.072% | -0.100% | 21% | -0.20% | 196.9 | 0 | - | -0.055 | -0.049% |
| 1428 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf M30 | 27.3 | 29% | -0.160 | -0.066% | -0.092% | 21% | -0.27% | 158.4 | 0 | - | -0.235 | -0.075% |
| 1429 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf H1 | 3.5 | 40% | -0.160 | -0.066% | -0.091% | 33% | -0.11% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 1430 | buffer 0.5, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf M15 | 88.2 | 42% | -0.160 | -0.063% | -0.087% | 30% | -0.34% | 49.0 | 2 | -2.5%, -1.8% | +0.039 | +0.039% |
| 1431 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c34, tf M30 | 8.6 | 36% | -0.160 | -0.067% | -0.093% | 29% | -0.20% | 504.4 | 0 | - | -0.471 | -0.088% |
| 1432 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf M15 | 91.1 | 34% | -0.161 | -0.064% | -0.089% | 32% | -0.31% | 47.4 | 2 | -2.6%, -2.1% | -0.091 | -0.049% |
| 1433 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop all4, tf M30 | 8.5 | 35% | -0.161 | -0.067% | -0.093% | 14% | -0.19% | 511.2 | 0 | - | -0.451 | -0.088% |
| 1434 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf H1 | 3.2 | 32% | -0.161 | -0.080% | -0.112% | 50% | -0.13% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1435 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf M5 | 121.7 | 27% | -0.161 | -0.064% | -0.089% | 21% | -0.26% | 35.5 | 3 | -1.7%, -2.0%, -3.3% | -0.136 | -0.060% |
| 1436 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf M15 | 20.7 | 27% | -0.161 | -0.064% | -0.089% | 33% | -0.28% | 209.2 | 0 | - | +0.122 | +0.761% |
| 1437 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf M15 | 47.4 | 20% | -0.162 | -0.066% | -0.092% | 24% | -0.23% | 91.2 | 1 | -2.5% | -0.050 | -0.035% |
| 1438 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf M5 | 14.7 | 26% | -0.162 | -0.060% | -0.083% | 17% | -0.30% | 293.6 | 0 | - | -0.129 | -0.065% |
| 1439 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c4, tf M30 | 8.3 | 30% | -0.162 | -0.062% | -0.086% | 43% | -0.18% | 518.1 | 0 | - | -0.375 | -0.089% |
| 1440 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf M15 | 48.2 | 27% | -0.162 | -0.064% | -0.089% | 21% | -0.32% | 89.7 | 1 | -2.2% | -0.199 | -0.068% |
| 1441 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf M15 | 88.7 | 42% | -0.163 | -0.064% | -0.089% | 24% | -0.32% | 48.7 | 2 | -2.0%, -2.1% | -0.081 | -0.048% |
| 1442 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf M15 | 89.6 | 34% | -0.163 | -0.064% | -0.089% | 30% | -0.24% | 48.2 | 2 | -2.5%, -2.1% | -0.100 | -0.051% |
| 1443 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c34, tf M5 | 237.5 | 42% | -0.163 | -0.063% | -0.087% | 24% | -0.38% | 18.2 | 5 | -2.7%, -2.8%, -1.7%, -1.7%, -2.0% | -0.061 | -0.036% |
| 1444 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf M15 | 13.6 | 23% | -0.163 | -0.068% | -0.095% | 27% | -0.26% | 316.8 | 0 | - | -0.041 | -0.071% |
| 1445 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf M30 | 7.0 | 25% | -0.163 | -0.064% | -0.089% | 33% | -0.26% | 616.9 | 0 | - | -0.324 | -0.067% |
| 1446 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop all4, tf M30 | 8.6 | 42% | -0.164 | -0.065% | -0.090% | 57% | -0.25% | 504.4 | 0 | - | -0.181 | -0.069% |
| 1447 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf M30 | 7.0 | 25% | -0.164 | -0.057% | -0.080% | 33% | -0.20% | 616.9 | 0 | - | +0.079 | +0.115% |
| 1448 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf M5 | 246.7 | 19% | -0.164 | -0.066% | -0.092% | 19% | -0.32% | 17.5 | 6 | -2.3%, -3.3%, -2.4%, -2.6%, -2.8%, -0.9% | -0.113 | -0.061% |
| 1449 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf M5 | 481.6 | 33% | -0.164 | -0.064% | -0.089% | 25% | -0.39% | 9.0 | 12 | -1.5%, -1.9%, -2.9%, -2.0%, -3.0%, -2.2%, -3.2%, -1.4%, -2.0%, -2.4%, -2.3%, -3.1% | -0.072 | -0.042% |
| 1450 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf M15 | 7.6 | 42% | -0.164 | -0.067% | -0.092% | 17% | -0.27% | 569.2 | 0 | - | -0.012 | -0.053% |
| 1451 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.164 | -0.084% | -0.117% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1452 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf M5 | 22.0 | 25% | -0.164 | -0.063% | -0.087% | 21% | -0.28% | 196.8 | 0 | - | -0.083 | -0.048% |
| 1453 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf M5 | 49.9 | 42% | -0.164 | -0.065% | -0.090% | 23% | -0.31% | 86.6 | 1 | -2.1% | -0.061 | -0.038% |
| 1454 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop all4, tf M5 | 13.0 | 24% | -0.164 | -0.071% | -0.099% | 27% | -0.19% | 331.4 | 0 | - | -0.114 | -0.076% |
| 1455 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop all4, tf M30 | 8.6 | 33% | -0.164 | -0.064% | -0.089% | 43% | -0.20% | 504.4 | 0 | - | -0.221 | -0.086% |
| 1456 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c4, tf M5 | 46.0 | 42% | -0.165 | -0.066% | -0.091% | 22% | -0.27% | 93.9 | 1 | -2.3% | -0.128 | -0.055% |
| 1457 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf M5 | 23.8 | 26% | -0.165 | -0.065% | -0.090% | 19% | -0.21% | 181.2 | 0 | - | +0.032 | -0.016% |
| 1458 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf M15 | 89.1 | 20% | -0.165 | -0.066% | -0.092% | 23% | -0.26% | 48.5 | 2 | -2.4%, -2.6% | -0.027 | -0.026% |
| 1459 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf M30 | 7.7 | 18% | -0.165 | -0.071% | -0.099% | 17% | -0.19% | 560.8 | 0 | - | -0.022 | -0.084% |
| 1460 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf M5 | 124.5 | 41% | -0.165 | -0.063% | -0.087% | 22% | -0.39% | 34.7 | 3 | -1.9%, -2.3%, -2.4% | -0.159 | -0.064% |
| 1461 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf M30 | 26.6 | 28% | -0.165 | -0.065% | -0.090% | 22% | -0.24% | 162.5 | 0 | - | -0.308 | -0.079% |
| 1462 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf M15 | 21.2 | 28% | -0.166 | -0.067% | -0.093% | 17% | -0.22% | 203.6 | 0 | - | +0.092 | +0.482% |
| 1463 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop all4, tf M5 | 80.8 | 35% | -0.166 | -0.066% | -0.091% | 24% | -0.30% | 53.4 | 2 | -2.4%, -2.4% | -0.047 | -0.034% |
| 1464 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop all4, tf M5 | 77.6 | 34% | -0.166 | -0.065% | -0.091% | 26% | -0.27% | 55.7 | 1 | -2.2% | -0.054 | -0.039% |
| 1465 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop all4, tf M5 | 13.3 | 25% | -0.166 | -0.062% | -0.087% | 27% | -0.19% | 325.7 | 0 | - | -0.152 | -0.077% |
| 1466 | buffer 0.0, clear 0.1, entry close, exit 1R, grade AB, stop c4, tf M5 | 228.2 | 42% | -0.166 | -0.064% | -0.089% | 20% | -0.39% | 18.9 | 5 | -2.5%, -2.2%, -3.0%, -1.8%, -2.4% | -0.086 | -0.044% |
| 1467 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf M15 | 101.7 | 29% | -0.167 | -0.065% | -0.090% | 21% | -0.28% | 42.5 | 2 | -2.0%, -2.0% | -0.164 | -0.065% |
| 1468 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf M5 | 248.5 | 27% | -0.167 | -0.064% | -0.088% | 26% | -0.33% | 17.4 | 6 | -2.1%, -1.7%, -2.0%, -1.9%, -3.0%, -2.8% | -0.147 | -0.063% |
| 1469 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf M15 | 39.6 | 27% | -0.167 | -0.064% | -0.089% | 26% | -0.28% | 109.2 | 0 | - | -0.037 | -0.023% |
| 1470 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf M15 | 15.0 | 42% | -0.167 | -0.065% | -0.090% | 42% | -0.21% | 287.4 | 0 | - | +0.113 | +0.161% |
| 1471 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf M15 | 47.8 | 20% | -0.167 | -0.069% | -0.096% | 21% | -0.21% | 90.3 | 1 | -2.8% | -0.086 | -0.048% |
| 1472 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf M15 | 103.7 | 29% | -0.167 | -0.064% | -0.089% | 20% | -0.26% | 41.7 | 2 | -1.9%, -2.1% | -0.182 | -0.068% |
| 1473 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf M15 | 20.5 | 40% | -0.168 | -0.061% | -0.085% | 22% | -0.29% | 210.3 | 0 | - | +0.084 | +0.353% |
| 1474 | buffer 0.0, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf M15 | 177.4 | 32% | -0.168 | -0.066% | -0.091% | 30% | -0.30% | 24.4 | 4 | -2.6%, -3.2%, -1.8%, -2.0% | -0.071 | -0.045% |
| 1475 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c34, tf M5 | 79.9 | 34% | -0.168 | -0.067% | -0.093% | 25% | -0.26% | 54.0 | 1 | -2.5% | -0.047 | -0.034% |
| 1476 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c4, tf M15 | 25.9 | 29% | -0.168 | -0.067% | -0.093% | 23% | -0.26% | 166.8 | 0 | - | -0.055 | -0.049% |
| 1477 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c34, tf M30 | 14.7 | 42% | -0.168 | -0.064% | -0.089% | 23% | -0.30% | 294.2 | 0 | - | -0.052 | -0.043% |
| 1478 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c4, tf M5 | 43.5 | 28% | -0.168 | -0.062% | -0.087% | 26% | -0.23% | 99.2 | 1 | -2.3% | -0.105 | -0.052% |
| 1479 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf M5 | 494.8 | 34% | -0.168 | -0.064% | -0.089% | 27% | -0.43% | 8.7 | 12 | -1.3%, -1.7%, -2.7%, -1.1%, -3.0%, -2.6%, -3.1%, -2.6%, -2.3%, -1.9%, -3.0%, -2.2% | -0.081 | -0.044% |
| 1480 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf M15 | 6.9 | 14% | -0.169 | -0.065% | -0.091% | 0% | -0.10% | 624.5 | 0 | - | -0.046 | -0.008% |
| 1481 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf M15 | 20.9 | 27% | -0.169 | -0.070% | -0.097% | 17% | -0.23% | 206.9 | 0 | - | +0.075 | +0.392% |
| 1482 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf M5 | 185.9 | 26% | -0.169 | -0.064% | -0.089% | 27% | -0.36% | 23.2 | 4 | -2.5%, -3.3%, -1.9%, -1.8% | -0.111 | -0.053% |
| 1483 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf M30 | 5.6 | 33% | -0.169 | -0.062% | -0.087% | 50% | -0.28% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1484 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.169 | -0.083% | -0.116% | 0% | -0.13% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1485 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf M5 | 5.2 | 27% | -0.169 | -0.043% | -0.060% | 25% | -0.29% | 824.8 | 0 | - | +0.000 | +0.000% |
| 1486 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf H1 | 3.0 | 29% | -0.169 | -0.082% | -0.114% | 0% | -0.13% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 1487 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf M15 | 20.5 | 30% | -0.170 | -0.064% | -0.089% | 28% | -0.29% | 210.3 | 0 | - | +0.154 | +1.166% |
| 1488 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf M15 | 10.4 | 42% | -0.170 | -0.070% | -0.097% | 11% | -0.23% | 413.8 | 0 | - | -0.034 | -0.038% |
| 1489 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c4, tf M5 | 72.3 | 28% | -0.170 | -0.067% | -0.093% | 27% | -0.32% | 59.7 | 1 | -2.1% | -0.037 | -0.031% |
| 1490 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf M5 | 19.7 | 25% | -0.170 | -0.063% | -0.087% | 35% | -0.27% | 219.6 | 0 | - | -0.049 | -0.034% |
| 1491 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c4, tf M5 | 13.0 | 23% | -0.170 | -0.065% | -0.090% | 36% | -0.20% | 331.4 | 0 | - | -0.183 | -0.080% |
| 1492 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf M30 | 7.8 | 21% | -0.170 | -0.070% | -0.097% | 43% | -0.27% | 554.3 | 0 | - | -0.052 | -0.086% |
| 1493 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop all4, tf M30 | 14.7 | 30% | -0.170 | -0.068% | -0.095% | 38% | -0.30% | 294.2 | 0 | - | -0.267 | -0.086% |
| 1494 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf M15 | 12.3 | 20% | -0.171 | -0.077% | -0.107% | 20% | -0.15% | 350.3 | 0 | - | -0.077 | -0.071% |
| 1495 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf M15 | 181.3 | 34% | -0.171 | -0.065% | -0.091% | 30% | -0.36% | 23.8 | 4 | -2.6%, -2.7%, -2.5%, -1.8% | -0.095 | -0.054% |
| 1496 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf M5 | 490.8 | 33% | -0.171 | -0.064% | -0.088% | 27% | -0.40% | 8.8 | 12 | -1.2%, -1.7%, -2.7%, -1.2%, -2.8%, -2.0%, -3.5%, -2.4%, -2.8%, -1.7%, -2.9%, -2.6% | -0.069 | -0.040% |
| 1497 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop all4, tf M5 | 498.2 | 34% | -0.171 | -0.065% | -0.090% | 27% | -0.46% | 8.7 | 12 | -1.5%, -1.6%, -2.5%, -1.2%, -2.9%, -2.3%, -3.0%, -2.8%, -2.4%, -2.0%, -3.0%, -2.2% | -0.087 | -0.046% |
| 1498 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf M30 | 7.9 | 30% | -0.172 | -0.070% | -0.098% | 29% | -0.25% | 546.5 | 0 | - | -0.402 | -0.076% |
| 1499 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c34, tf M15 | 27.2 | 32% | -0.172 | -0.064% | -0.090% | 22% | -0.25% | 159.1 | 0 | - | -0.170 | -0.062% |
| 1500 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf M30 | 7.9 | 28% | -0.172 | -0.075% | -0.104% | 14% | -0.17% | 546.5 | 0 | - | +0.013 | -0.040% |
| 1501 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf M5 | 5.7 | 24% | -0.173 | -0.059% | -0.082% | 25% | -0.12% | 757.4 | 0 | - | +0.000 | +0.000% |
| 1502 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.173 | -0.086% | -0.119% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1503 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf M5 | 37.5 | 26% | -0.173 | -0.067% | -0.093% | 24% | -0.23% | 115.2 | 0 | - | -0.006 | -0.015% |
| 1504 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf M5 | 115.5 | 41% | -0.173 | -0.063% | -0.088% | 23% | -0.31% | 37.4 | 2 | -1.9%, -2.2% | -0.152 | -0.061% |
| 1505 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf M15 | 48.8 | 29% | -0.173 | -0.068% | -0.094% | 21% | -0.24% | 88.5 | 1 | -2.4% | +0.005 | +0.016% |
| 1506 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf M15 | 7.8 | 41% | -0.173 | -0.061% | -0.085% | 17% | -0.25% | 551.4 | 0 | - | -0.179 | -0.086% |
| 1507 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf M5 | 54.7 | 34% | -0.174 | -0.065% | -0.090% | 26% | -0.28% | 79.0 | 1 | -2.2% | -0.107 | -0.054% |
| 1508 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf M15 | 12.3 | 22% | -0.174 | -0.071% | -0.099% | 30% | -0.19% | 350.3 | 0 | - | -0.048 | -0.062% |
| 1509 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.175 | -0.077% | -0.106% | 33% | -0.18% | 940.5 | 0 | - | +0.153 | +2.771% |
| 1510 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.175 | -0.077% | -0.106% | 33% | -0.18% | 940.5 | 0 | - | +0.181 | +3.835% |
| 1511 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.175 | -0.077% | -0.106% | 33% | -0.18% | 940.5 | 0 | - | +0.182 | +3.877% |
| 1512 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf M15 | 49.4 | 20% | -0.175 | -0.069% | -0.096% | 23% | -0.23% | 87.4 | 1 | -2.8% | -0.081 | -0.046% |
| 1513 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c4, tf H1 | 7.6 | 34% | -0.175 | -0.058% | -0.080% | 17% | -0.30% | 571.0 | 0 | - | -0.240 | -0.045% |
| 1514 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c34, tf H1 | 7.6 | 34% | -0.175 | -0.063% | -0.087% | 17% | -0.20% | 571.0 | 0 | - | -0.320 | -0.088% |
| 1515 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf H4 | 4.6 | 36% | -0.175 | -0.078% | -0.109% | 67% | -0.20% | 940.5 | 0 | - | +0.124 | +1.684% |
| 1516 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.175 | -0.077% | -0.107% | 33% | -0.20% | 940.5 | 0 | - | +0.054 | +0.920% |
| 1517 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.175 | -0.077% | -0.107% | 33% | -0.20% | 940.5 | 0 | - | +0.086 | +1.320% |
| 1518 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf M5 | 249.4 | 34% | -0.176 | -0.065% | -0.090% | 24% | -0.32% | 17.3 | 6 | -1.1%, -2.5%, -2.7%, -3.4%, -1.5%, -2.6% | -0.061 | -0.038% |
| 1519 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf M15 | 20.5 | 20% | -0.176 | -0.067% | -0.093% | 28% | -0.25% | 210.3 | 0 | - | +0.097 | +0.330% |
| 1520 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c4, tf M15 | 179.5 | 33% | -0.176 | -0.066% | -0.091% | 28% | -0.32% | 24.1 | 4 | -2.6%, -2.9%, -2.2%, -1.9% | -0.122 | -0.059% |
| 1521 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c34, tf M5 | 13.1 | 23% | -0.176 | -0.064% | -0.089% | 36% | -0.22% | 328.5 | 0 | - | -0.167 | -0.080% |
| 1522 | buffer 0.5, clear 0.05, entry close, exit trail1, grade AB, stop c34, tf M15 | 179.7 | 33% | -0.176 | -0.066% | -0.092% | 24% | -0.37% | 24.0 | 4 | -2.7%, -2.9%, -2.1%, -2.0% | -0.101 | -0.054% |
| 1523 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf M5 | 19.5 | 16% | -0.177 | -0.074% | -0.102% | 24% | -0.19% | 221.4 | 0 | - | +0.041 | +0.003% |
| 1524 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf M5 | 251.9 | 35% | -0.177 | -0.065% | -0.090% | 28% | -0.35% | 17.1 | 6 | -1.2%, -2.7%, -2.7%, -3.0%, -1.9%, -2.2% | -0.070 | -0.042% |
| 1525 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf M15 | 47.4 | 28% | -0.177 | -0.069% | -0.096% | 14% | -0.21% | 91.2 | 1 | -2.7% | -0.031 | -0.018% |
| 1526 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c4, tf M5 | 79.0 | 34% | -0.177 | -0.067% | -0.093% | 23% | -0.29% | 54.7 | 1 | -2.6% | -0.048 | -0.036% |
| 1527 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf M30 | 5.6 | 31% | -0.177 | -0.060% | -0.084% | 50% | -0.28% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1528 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf M15 | 14.6 | 41% | -0.178 | -0.066% | -0.092% | 33% | -0.20% | 296.7 | 0 | - | -0.018 | -0.057% |
| 1529 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop all4, tf M30 | 14.9 | 33% | -0.178 | -0.068% | -0.095% | 38% | -0.28% | 289.8 | 0 | - | -0.195 | -0.080% |
| 1530 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf M5 | 244.2 | 41% | -0.178 | -0.064% | -0.089% | 25% | -0.36% | 17.7 | 6 | -2.2%, -1.8%, -2.2%, -2.3%, -2.4%, -3.0% | -0.172 | -0.067% |
| 1531 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf H4 | 4.7 | 32% | -0.178 | -0.068% | -0.095% | 50% | -0.15% | 917.0 | 0 | - | -0.041 | -0.082% |
| 1532 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf M15 | 77.6 | 18% | -0.178 | -0.066% | -0.092% | 23% | -0.21% | 55.7 | 1 | -2.5% | -0.031 | -0.027% |
| 1533 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf M5 | 256.5 | 19% | -0.179 | -0.068% | -0.095% | 20% | -0.32% | 16.8 | 6 | -2.4%, -3.2%, -2.9%, -2.0%, -3.1%, -1.2% | -0.132 | -0.065% |
| 1534 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf M5 | 228.3 | 33% | -0.179 | -0.065% | -0.091% | 24% | -0.32% | 18.9 | 5 | -1.8%, -2.4%, -3.4%, -1.3%, -2.9% | -0.052 | -0.034% |
| 1535 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop all4, tf M15 | 27.4 | 33% | -0.179 | -0.065% | -0.090% | 22% | -0.33% | 157.7 | 0 | - | -0.109 | -0.053% |
| 1536 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf M15 | 98.9 | 29% | -0.179 | -0.066% | -0.091% | 27% | -0.24% | 43.7 | 2 | -2.4%, -1.7% | -0.184 | -0.068% |
| 1537 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf M15 | 7.7 | 21% | -0.179 | -0.071% | -0.099% | 17% | -0.23% | 560.2 | 0 | - | +0.100 | +0.652% |
| 1538 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf M15 | 96.1 | 20% | -0.179 | -0.070% | -0.097% | 21% | -0.27% | 44.9 | 2 | -2.2%, -3.2% | -0.091 | -0.051% |
| 1539 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop all4, tf H1 | 7.6 | 36% | -0.180 | -0.066% | -0.091% | 17% | -0.21% | 571.0 | 0 | - | -0.326 | -0.089% |
| 1540 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf H1 | 21.7 | 31% | -0.180 | -0.068% | -0.095% | 21% | -0.26% | 198.7 | 0 | - | -0.072 | -0.037% |
| 1541 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf M15 | 12.5 | 41% | -0.180 | -0.064% | -0.089% | 20% | -0.23% | 347.0 | 0 | - | -0.245 | -0.085% |
| 1542 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c34, tf M5 | 44.4 | 41% | -0.181 | -0.066% | -0.092% | 23% | -0.30% | 97.2 | 1 | -2.6% | -0.091 | -0.043% |
| 1543 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf M5 | 252.8 | 41% | -0.181 | -0.065% | -0.091% | 22% | -0.34% | 17.1 | 6 | -2.1%, -2.4%, -1.6%, -2.3%, -2.8%, -2.6% | -0.167 | -0.065% |
| 1544 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf M5 | 245.4 | 34% | -0.181 | -0.066% | -0.092% | 26% | -0.36% | 17.6 | 6 | -1.3%, -2.5%, -2.8%, -2.6%, -2.2%, -2.7% | -0.061 | -0.040% |
| 1545 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf M30 | 7.0 | 40% | -0.181 | -0.074% | -0.103% | 17% | -0.18% | 616.9 | 0 | - | +0.039 | +0.016% |
| 1546 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf M5 | 92.0 | 26% | -0.181 | -0.067% | -0.093% | 21% | -0.28% | 47.0 | 2 | -3.1%, -1.7% | -0.032 | -0.024% |
| 1547 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c34, tf H4 | 4.6 | 36% | -0.181 | -0.077% | -0.107% | 33% | -0.16% | 940.5 | 0 | - | -0.002 | +0.387% |
| 1548 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf H4 | 4.6 | 36% | -0.181 | -0.077% | -0.107% | 33% | -0.16% | 940.5 | 0 | - | +0.048 | +0.743% |
| 1549 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf H4 | 4.6 | 36% | -0.181 | -0.077% | -0.107% | 33% | -0.16% | 940.5 | 0 | - | +0.083 | +1.095% |
| 1550 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf M5 | 237.8 | 34% | -0.182 | -0.066% | -0.092% | 26% | -0.37% | 18.2 | 5 | -1.8%, -2.7%, -2.8%, -1.7%, -2.9% | -0.045 | -0.031% |
| 1551 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf H1 | 3.0 | 29% | -0.182 | -0.080% | -0.111% | 0% | -0.14% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 1552 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c34, tf H4 | 4.7 | 38% | -0.182 | -0.081% | -0.112% | 25% | -0.13% | 917.0 | 0 | - | -0.028 | +0.031% |
| 1553 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c34, tf H4 | 4.7 | 38% | -0.182 | -0.081% | -0.112% | 25% | -0.13% | 917.0 | 0 | - | +0.012 | +0.251% |
| 1554 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c34, tf M5 | 74.6 | 41% | -0.182 | -0.068% | -0.094% | 20% | -0.31% | 57.9 | 1 | -1.9% | -0.081 | -0.045% |
| 1555 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf M30 | 27.3 | 41% | -0.183 | -0.071% | -0.099% | 17% | -0.26% | 158.4 | 0 | - | -0.136 | -0.067% |
| 1556 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf M15 | 7.5 | 31% | -0.183 | -0.070% | -0.097% | 17% | -0.22% | 578.5 | 0 | - | +0.067 | +0.809% |
| 1557 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf M15 | 95.7 | 41% | -0.184 | -0.068% | -0.094% | 21% | -0.36% | 45.2 | 2 | -1.7%, -2.6% | -0.048 | -0.033% |
| 1558 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf H1 | 22.0 | 32% | -0.184 | -0.069% | -0.096% | 16% | -0.38% | 196.7 | 0 | - | -0.170 | -0.067% |
| 1559 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf M5 | 5.8 | 40% | -0.184 | -0.050% | -0.070% | 20% | -0.38% | 742.3 | 0 | - | +0.000 | +0.000% |
| 1560 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c4, tf M15 | 27.4 | 33% | -0.184 | -0.065% | -0.090% | 30% | -0.34% | 157.7 | 0 | - | -0.160 | -0.065% |
| 1561 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c34, tf M5 | 44.4 | 34% | -0.185 | -0.069% | -0.096% | 18% | -0.30% | 97.2 | 1 | -2.5% | -0.007 | -0.007% |
| 1562 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c34, tf H1 | 7.3 | 32% | -0.185 | -0.052% | -0.072% | 33% | -0.25% | 588.5 | 0 | - | -0.281 | -0.077% |
| 1563 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c4, tf M5 | 13.0 | 24% | -0.186 | -0.068% | -0.095% | 27% | -0.19% | 331.4 | 0 | - | -0.282 | -0.085% |
| 1564 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c34, tf M5 | 12.8 | 28% | -0.187 | -0.064% | -0.089% | 27% | -0.26% | 337.3 | 0 | - | -0.234 | -0.078% |
| 1565 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf M5 | 253.5 | 35% | -0.187 | -0.067% | -0.092% | 23% | -0.39% | 17.0 | 6 | -1.2%, -2.9%, -2.4%, -3.2%, -1.8%, -2.9% | -0.075 | -0.044% |
| 1566 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c4, tf M5 | 46.0 | 35% | -0.187 | -0.069% | -0.096% | 32% | -0.26% | 93.9 | 1 | -2.5% | -0.017 | -0.013% |
| 1567 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop all4, tf M30 | 8.6 | 36% | -0.187 | -0.070% | -0.097% | 29% | -0.19% | 504.4 | 0 | - | -0.462 | -0.088% |
| 1568 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c4, tf M5 | 72.3 | 41% | -0.188 | -0.069% | -0.096% | 19% | -0.30% | 59.7 | 1 | -1.9% | -0.101 | -0.053% |
| 1569 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf M5 | 259.5 | 27% | -0.188 | -0.067% | -0.093% | 22% | -0.31% | 16.6 | 6 | -2.2%, -2.0%, -2.3%, -1.3%, -3.2%, -3.1% | -0.163 | -0.065% |
| 1570 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf M15 | 44.8 | 41% | -0.189 | -0.068% | -0.094% | 20% | -0.21% | 96.4 | 1 | -2.2% | -0.076 | -0.043% |
| 1571 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf M5 | 23.0 | 26% | -0.189 | -0.065% | -0.090% | 25% | -0.30% | 188.0 | 0 | - | -0.091 | -0.050% |
| 1572 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop all4, tf M5 | 47.3 | 36% | -0.189 | -0.069% | -0.095% | 26% | -0.31% | 91.4 | 1 | -2.3% | -0.006 | -0.003% |
| 1573 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf M15 | 50.4 | 20% | -0.189 | -0.072% | -0.100% | 18% | -0.20% | 85.7 | 1 | -2.8% | -0.124 | -0.057% |
| 1574 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf M30 | 5.6 | 22% | -0.189 | -0.061% | -0.085% | 50% | -0.25% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1575 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf M15 | 46.8 | 40% | -0.189 | -0.067% | -0.093% | 17% | -0.35% | 92.3 | 1 | -2.4% | -0.017 | +0.001% |
| 1576 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf M5 | 127.1 | 26% | -0.190 | -0.069% | -0.096% | 22% | -0.28% | 34.0 | 3 | -1.9%, -2.4%, -3.0% | -0.154 | -0.063% |
| 1577 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf M15 | 39.6 | 20% | -0.190 | -0.068% | -0.094% | 34% | -0.24% | 109.2 | 0 | - | -0.007 | +0.000% |
| 1578 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop all4, tf M15 | 4.5 | 26% | -0.191 | -0.058% | -0.081% | 33% | -0.23% | 969.2 | 0 | - | +0.128 | +0.150% |
| 1579 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop all4, tf M30 | 14.9 | 34% | -0.191 | -0.070% | -0.097% | 31% | -0.27% | 289.8 | 0 | - | -0.255 | -0.082% |
| 1580 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf M15 | 100.4 | 41% | -0.191 | -0.068% | -0.094% | 22% | -0.25% | 43.0 | 2 | -1.7%, -2.5% | -0.051 | -0.035% |
| 1581 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c4, tf M30 | 8.3 | 23% | -0.191 | -0.071% | -0.099% | 29% | -0.19% | 518.1 | 0 | - | -0.187 | -0.076% |
| 1582 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c4, tf M30 | 14.8 | 28% | -0.191 | -0.071% | -0.099% | 31% | -0.25% | 292.0 | 0 | - | -0.164 | -0.077% |
| 1583 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf M15 | 7.8 | 33% | -0.191 | -0.070% | -0.097% | 17% | -0.19% | 551.4 | 0 | - | +0.093 | +0.943% |
| 1584 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.191 | -0.077% | -0.107% | 67% | -0.20% | 940.5 | 0 | - | +0.011 | +0.488% |
| 1585 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop all4, tf M5 | 12.9 | 21% | -0.192 | -0.066% | -0.092% | 36% | -0.20% | 334.3 | 0 | - | -0.183 | -0.080% |
| 1586 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf M15 | 7.8 | 30% | -0.192 | -0.066% | -0.092% | 17% | -0.20% | 551.4 | 0 | - | -0.334 | -0.092% |
| 1587 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf M30 | 7.7 | 20% | -0.192 | -0.073% | -0.101% | 17% | -0.19% | 560.8 | 0 | - | -0.032 | -0.084% |
| 1588 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf M5 | 53.0 | 33% | -0.192 | -0.066% | -0.092% | 23% | -0.32% | 81.5 | 1 | -2.2% | -0.090 | -0.049% |
| 1589 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c4, tf H1 | 7.2 | 33% | -0.192 | -0.051% | -0.071% | 33% | -0.27% | 597.7 | 0 | - | -0.267 | -0.077% |
| 1590 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf M5 | 19.5 | 25% | -0.192 | -0.075% | -0.104% | 24% | -0.18% | 221.4 | 0 | - | +0.081 | +0.037% |
| 1591 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf M5 | 14.7 | 24% | -0.193 | -0.066% | -0.091% | 25% | -0.23% | 293.6 | 0 | - | -0.074 | -0.038% |
| 1592 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf M5 | 235.3 | 40% | -0.193 | -0.067% | -0.093% | 20% | -0.38% | 18.4 | 5 | -2.3%, -2.3%, -1.9%, -2.3%, -3.2% | -0.169 | -0.064% |
| 1593 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf M5 | 33.3 | 40% | -0.193 | -0.068% | -0.095% | 14% | -0.23% | 129.6 | 0 | - | -0.136 | -0.058% |
| 1594 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c4, tf M5 | 43.5 | 41% | -0.193 | -0.067% | -0.093% | 21% | -0.28% | 99.2 | 1 | -2.7% | -0.158 | -0.060% |
| 1595 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c34, tf H1 | 7.7 | 34% | -0.193 | -0.062% | -0.086% | 17% | -0.27% | 562.6 | 0 | - | -0.239 | -0.044% |
| 1596 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop all4, tf H1 | 21.7 | 31% | -0.193 | -0.072% | -0.100% | 21% | -0.27% | 198.7 | 0 | - | -0.197 | -0.071% |
| 1597 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf M5 | 17.0 | 18% | -0.194 | -0.075% | -0.104% | 27% | -0.21% | 253.4 | 0 | - | -0.074 | -0.049% |
| 1598 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c34, tf M5 | 80.2 | 25% | -0.194 | -0.070% | -0.098% | 21% | -0.26% | 53.9 | 1 | -2.2% | -0.015 | -0.032% |
| 1599 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop all4, tf M5 | 45.5 | 35% | -0.194 | -0.070% | -0.097% | 20% | -0.23% | 95.0 | 1 | -2.5% | -0.004 | -0.006% |
| 1600 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf M30 | 49.2 | 39% | -0.194 | -0.072% | -0.100% | 16% | -0.23% | 87.7 | 1 | -2.6% | -0.054 | -0.037% |
| 1601 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c34, tf M30 | 8.5 | 24% | -0.194 | -0.071% | -0.099% | 29% | -0.15% | 511.2 | 0 | - | -0.311 | -0.089% |
| 1602 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf M30 | 7.1 | 39% | -0.194 | -0.077% | -0.107% | 0% | -0.14% | 606.7 | 0 | - | -0.022 | -0.045% |
| 1603 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf M5 | 51.9 | 33% | -0.195 | -0.067% | -0.093% | 22% | -0.24% | 83.2 | 1 | -2.2% | -0.098 | -0.051% |
| 1604 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf M5 | 22.9 | 40% | -0.196 | -0.062% | -0.086% | 35% | -0.37% | 189.0 | 0 | - | -0.019 | -0.019% |
| 1605 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf M15 | 102.9 | 20% | -0.196 | -0.070% | -0.097% | 22% | -0.27% | 42.0 | 2 | -2.0%, -3.0% | -0.107 | -0.056% |
| 1606 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c4, tf M5 | 43.5 | 33% | -0.196 | -0.069% | -0.096% | 24% | -0.23% | 99.2 | 1 | -2.4% | -0.015 | -0.015% |
| 1607 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf M30 | 26.6 | 40% | -0.197 | -0.070% | -0.098% | 13% | -0.20% | 162.5 | 0 | - | -0.056 | -0.046% |
| 1608 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.197 | -0.085% | -0.118% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1609 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf M15 | 7.5 | 40% | -0.197 | -0.061% | -0.085% | 33% | -0.24% | 572.4 | 0 | - | -0.157 | -0.085% |
| 1610 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf H1 | 3.0 | 33% | -0.197 | -0.079% | -0.110% | 0% | -0.15% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 1611 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf M5 | 39.7 | 27% | -0.198 | -0.069% | -0.096% | 31% | -0.27% | 108.9 | 0 | - | +0.001 | -0.010% |
| 1612 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf M5 | 5.8 | 18% | -0.198 | -0.061% | -0.085% | 20% | -0.32% | 742.3 | 0 | - | +0.000 | +0.000% |
| 1613 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf H1 | 3.3 | 31% | -0.198 | -0.089% | -0.123% | 0% | -0.10% | 1313.9 | 0 | - | +0.000 | +0.000% |
| 1614 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c4, tf M5 | 12.4 | 28% | -0.199 | -0.064% | -0.088% | 30% | -0.20% | 349.6 | 0 | - | -0.280 | -0.087% |
| 1615 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf M5 | 21.2 | 39% | -0.199 | -0.063% | -0.087% | 22% | -0.29% | 204.2 | 0 | - | -0.180 | -0.068% |
| 1616 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf M15 | 15.9 | 29% | -0.199 | -0.072% | -0.100% | 15% | -0.19% | 272.4 | 0 | - | -0.097 | -0.069% |
| 1617 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf M15 | 7.3 | 20% | -0.199 | -0.069% | -0.096% | 33% | -0.22% | 588.2 | 0 | - | +0.059 | +0.305% |
| 1618 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c4, tf H1 | 7.6 | 36% | -0.199 | -0.063% | -0.088% | 17% | -0.21% | 571.0 | 0 | - | -0.115 | -0.024% |
| 1619 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c34, tf M5 | 46.5 | 36% | -0.200 | -0.070% | -0.098% | 29% | -0.28% | 93.0 | 1 | -2.5% | -0.014 | -0.010% |
| 1620 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf M5 | 19.5 | 18% | -0.201 | -0.077% | -0.107% | 24% | -0.21% | 221.4 | 0 | - | +0.067 | +0.041% |
| 1621 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf M15 | 98.2 | 40% | -0.201 | -0.068% | -0.095% | 20% | -0.28% | 44.0 | 2 | -1.8%, -2.5% | -0.077 | -0.045% |
| 1622 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c34, tf M30 | 8.5 | 23% | -0.201 | -0.072% | -0.100% | 29% | -0.16% | 511.2 | 0 | - | -0.214 | -0.087% |
| 1623 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf M5 | 49.9 | 32% | -0.201 | -0.069% | -0.095% | 16% | -0.28% | 86.6 | 1 | -2.2% | -0.126 | -0.056% |
| 1624 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop all4, tf M5 | 77.7 | 25% | -0.201 | -0.071% | -0.099% | 17% | -0.29% | 55.6 | 1 | -2.0% | -0.029 | -0.042% |
| 1625 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf M30 | 7.7 | 39% | -0.201 | -0.072% | -0.100% | 17% | -0.26% | 562.3 | 0 | - | -0.127 | -0.086% |
| 1626 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf M15 | 11.4 | 39% | -0.202 | -0.072% | -0.100% | 0% | -0.21% | 377.3 | 0 | - | -0.090 | +0.035% |
| 1627 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf M15 | 98.8 | 20% | -0.202 | -0.071% | -0.098% | 20% | -0.26% | 43.7 | 2 | -2.2%, -3.2% | -0.066 | -0.044% |
| 1628 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c34, tf M30 | 8.5 | 24% | -0.202 | -0.072% | -0.101% | 14% | -0.16% | 511.2 | 0 | - | -0.206 | -0.078% |
| 1629 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf M15 | 12.5 | 25% | -0.203 | -0.077% | -0.107% | 10% | -0.22% | 347.0 | 0 | - | -0.189 | -0.085% |
| 1630 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.203 | -0.083% | -0.115% | 0% | -0.14% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1631 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c4, tf M30 | 14.8 | 41% | -0.203 | -0.070% | -0.097% | 23% | -0.28% | 292.0 | 0 | - | -0.210 | -0.078% |
| 1632 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop all4, tf H1 | 7.6 | 39% | -0.203 | -0.062% | -0.086% | 33% | -0.21% | 571.0 | 0 | - | -0.026 | +0.093% |
| 1633 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop all4, tf M5 | 81.1 | 25% | -0.203 | -0.071% | -0.099% | 24% | -0.31% | 53.3 | 2 | -2.2%, -3.0% | -0.018 | -0.033% |
| 1634 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf M5 | 105.5 | 40% | -0.205 | -0.068% | -0.095% | 19% | -0.34% | 41.0 | 2 | -2.0%, -2.6% | -0.178 | -0.064% |
| 1635 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c4, tf M30 | 8.6 | 24% | -0.205 | -0.073% | -0.101% | 29% | -0.16% | 504.4 | 0 | - | -0.183 | -0.078% |
| 1636 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf M5 | 39.5 | 39% | -0.207 | -0.070% | -0.097% | 17% | -0.22% | 109.2 | 0 | - | -0.065 | -0.036% |
| 1637 | buffer 0.0, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf H1 | 21.9 | 31% | -0.207 | -0.075% | -0.104% | 16% | -0.26% | 197.7 | 0 | - | -0.133 | -0.058% |
| 1638 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop all4, tf M30 | 8.5 | 24% | -0.208 | -0.072% | -0.101% | 14% | -0.16% | 511.2 | 0 | - | -0.196 | -0.077% |
| 1639 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf M15 | 15.3 | 28% | -0.208 | -0.073% | -0.101% | 17% | -0.26% | 282.9 | 0 | - | -0.117 | -0.072% |
| 1640 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c4, tf M5 | 79.2 | 24% | -0.208 | -0.071% | -0.099% | 21% | -0.31% | 54.6 | 1 | -2.3% | -0.024 | -0.037% |
| 1641 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf M15 | 7.4 | 20% | -0.209 | -0.065% | -0.091% | 0% | -0.17% | 582.1 | 0 | - | +0.029 | -0.036% |
| 1642 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.210 | -0.087% | -0.121% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1643 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c4, tf M15 | 26.0 | 31% | -0.210 | -0.070% | -0.098% | 18% | -0.24% | 166.1 | 0 | - | -0.197 | -0.066% |
| 1644 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf M15 | 20.4 | 38% | -0.211 | -0.070% | -0.097% | 28% | -0.28% | 211.5 | 0 | - | -0.020 | +0.045% |
| 1645 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf H1 | 3.0 | 33% | -0.211 | -0.080% | -0.112% | 0% | -0.14% | 1423.3 | 0 | - | +0.000 | +0.000% |
| 1646 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf M30 | 50.8 | 38% | -0.211 | -0.073% | -0.101% | 20% | -0.28% | 85.0 | 1 | -2.5% | -0.065 | -0.044% |
| 1647 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c4, tf H1 | 7.6 | 39% | -0.212 | -0.063% | -0.087% | 33% | -0.24% | 571.0 | 0 | - | +0.069 | +0.325% |
| 1648 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c34, tf H1 | 22.0 | 31% | -0.212 | -0.072% | -0.100% | 21% | -0.33% | 196.7 | 0 | - | -0.125 | -0.057% |
| 1649 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c4, tf M5 | 13.0 | 41% | -0.212 | -0.072% | -0.100% | 18% | -0.26% | 331.4 | 0 | - | -0.386 | -0.086% |
| 1650 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf M15 | 101.1 | 20% | -0.212 | -0.072% | -0.100% | 21% | -0.25% | 42.7 | 2 | -2.0%, -3.4% | -0.060 | -0.042% |
| 1651 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf M5 | 29.0 | 39% | -0.213 | -0.071% | -0.099% | 24% | -0.25% | 148.8 | 0 | - | -0.168 | -0.066% |
| 1652 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c4, tf M5 | 72.5 | 24% | -0.213 | -0.072% | -0.099% | 27% | -0.26% | 59.6 | 1 | -2.1% | +0.005 | -0.025% |
| 1653 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf M15 | 49.2 | 39% | -0.213 | -0.071% | -0.098% | 20% | -0.25% | 87.8 | 1 | -2.4% | +0.015 | +0.036% |
| 1654 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf M30 | 7.7 | 23% | -0.213 | -0.073% | -0.101% | 33% | -0.20% | 562.3 | 0 | - | -0.014 | -0.069% |
| 1655 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf M15 | 11.0 | 40% | -0.214 | -0.075% | -0.104% | 22% | -0.21% | 392.7 | 0 | - | +0.007 | +0.013% |
| 1656 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf M15 | 11.3 | 25% | -0.215 | -0.075% | -0.104% | 30% | -0.23% | 381.0 | 0 | - | +0.029 | +0.247% |
| 1657 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf M15 | 8.2 | 30% | -0.216 | -0.072% | -0.100% | 17% | -0.17% | 526.7 | 0 | - | -0.374 | -0.091% |
| 1658 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf M30 | 7.1 | 23% | -0.216 | -0.073% | -0.101% | 0% | -0.12% | 606.7 | 0 | - | +0.008 | -0.076% |
| 1659 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf H4 | 4.7 | 38% | -0.217 | -0.063% | -0.088% | 25% | -0.15% | 917.0 | 0 | - | -0.039 | -0.075% |
| 1660 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c34, tf M30 | 8.6 | 24% | -0.217 | -0.074% | -0.102% | 29% | -0.16% | 504.4 | 0 | - | -0.196 | -0.080% |
| 1661 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c34, tf M5 | 13.1 | 40% | -0.217 | -0.075% | -0.104% | 18% | -0.26% | 328.5 | 0 | - | -0.277 | -0.083% |
| 1662 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf M5 | 212.4 | 39% | -0.218 | -0.069% | -0.095% | 20% | -0.39% | 20.3 | 5 | -1.8%, -2.7%, -3.3%, -2.0%, -2.8% | -0.185 | -0.067% |
| 1663 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf M5 | 5.2 | 38% | -0.218 | -0.064% | -0.088% | 25% | -0.19% | 824.8 | 0 | - | +0.000 | +0.000% |
| 1664 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop all4, tf M30 | 8.5 | 24% | -0.218 | -0.073% | -0.101% | 29% | -0.14% | 511.2 | 0 | - | -0.316 | -0.089% |
| 1665 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade AB, stop c4, tf H4 | 4.6 | 36% | -0.218 | -0.080% | -0.111% | 33% | -0.19% | 940.5 | 0 | - | -0.006 | +0.377% |
| 1666 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf H4 | 4.6 | 36% | -0.218 | -0.080% | -0.111% | 33% | -0.19% | 940.5 | 0 | - | +0.077 | +0.971% |
| 1667 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf H4 | 4.6 | 36% | -0.218 | -0.080% | -0.111% | 33% | -0.19% | 940.5 | 0 | - | +0.095 | +1.347% |
| 1668 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf M30 | 7.1 | 16% | -0.218 | -0.078% | -0.108% | 0% | -0.14% | 606.7 | 0 | - | +0.093 | -0.053% |
| 1669 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf M5 | 21.9 | 39% | -0.219 | -0.079% | -0.110% | 5% | -0.20% | 196.9 | 0 | - | -0.093 | -0.055% |
| 1670 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf H1 | 3.2 | 32% | -0.219 | -0.081% | -0.112% | 50% | -0.17% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1671 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf M15 | 10.9 | 24% | -0.220 | -0.075% | -0.104% | 11% | -0.21% | 396.7 | 0 | - | +0.079 | +0.432% |
| 1672 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c34, tf M5 | 74.7 | 24% | -0.220 | -0.072% | -0.101% | 21% | -0.27% | 57.8 | 1 | -2.2% | -0.000 | -0.026% |
| 1673 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf H4 | 4.7 | 32% | -0.220 | -0.076% | -0.106% | 25% | -0.13% | 917.0 | 0 | - | +0.130 | +1.606% |
| 1674 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf M15 | 9.3 | 16% | -0.221 | -0.080% | -0.111% | 12% | -0.16% | 463.7 | 0 | - | +0.198 | +3.234% |
| 1675 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf M5 | 29.0 | 24% | -0.221 | -0.070% | -0.097% | 24% | -0.26% | 148.8 | 0 | - | -0.076 | -0.047% |
| 1676 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf M15 | 6.9 | 24% | -0.222 | -0.069% | -0.096% | 20% | -0.17% | 624.5 | 0 | - | -0.102 | -0.070% |
| 1677 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf M15 | 77.3 | 39% | -0.222 | -0.070% | -0.098% | 16% | -0.26% | 55.9 | 1 | -2.5% | -0.143 | -0.060% |
| 1678 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade AB, stop all4, tf H4 | 4.6 | 36% | -0.223 | -0.079% | -0.110% | 33% | -0.17% | 940.5 | 0 | - | +0.152 | +2.628% |
| 1679 | buffer 0.5, clear 0.1, entry close, exit trail1, grade AB, stop c4, tf H1 | 22.2 | 31% | -0.223 | -0.074% | -0.103% | 16% | -0.31% | 194.7 | 0 | - | -0.081 | -0.043% |
| 1680 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf M15 | 15.7 | 17% | -0.223 | -0.072% | -0.101% | 23% | -0.17% | 274.4 | 0 | - | +0.067 | -0.017% |
| 1681 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c34, tf H1 | 7.2 | 27% | -0.223 | -0.069% | -0.096% | 33% | -0.22% | 597.7 | 0 | - | -0.412 | -0.090% |
| 1682 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf M5 | 92.1 | 39% | -0.223 | -0.072% | -0.100% | 13% | -0.26% | 46.9 | 2 | -2.7%, -2.3% | -0.144 | -0.059% |
| 1683 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.224 | -0.085% | -0.118% | 0% | -0.14% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1684 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf M15 | 11.0 | 38% | -0.224 | -0.076% | -0.105% | 11% | -0.18% | 392.7 | 0 | - | -0.096 | +0.003% |
| 1685 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf M30 | 7.9 | 22% | -0.225 | -0.077% | -0.106% | 29% | -0.21% | 546.5 | 0 | - | +0.108 | +0.080% |
| 1686 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop all4, tf M5 | 45.6 | 25% | -0.226 | -0.074% | -0.103% | 20% | -0.20% | 94.8 | 1 | -2.6% | -0.081 | -0.048% |
| 1687 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c34, tf H1 | 7.6 | 37% | -0.226 | -0.063% | -0.088% | 33% | -0.23% | 571.0 | 0 | - | -0.027 | +0.105% |
| 1688 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf M5 | 17.8 | 38% | -0.228 | -0.064% | -0.088% | 27% | -0.26% | 242.3 | 0 | - | -0.202 | -0.077% |
| 1689 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c34, tf M30 | 8.6 | 26% | -0.228 | -0.074% | -0.103% | 29% | -0.15% | 504.4 | 0 | - | -0.215 | -0.086% |
| 1690 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop all4, tf M30 | 8.6 | 24% | -0.228 | -0.074% | -0.103% | 14% | -0.16% | 504.4 | 0 | - | -0.178 | -0.077% |
| 1691 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf M15 | 14.7 | 27% | -0.228 | -0.076% | -0.106% | 8% | -0.25% | 294.3 | 0 | - | -0.205 | -0.082% |
| 1692 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c4, tf H1 | 7.2 | 28% | -0.229 | -0.069% | -0.096% | 33% | -0.22% | 597.7 | 0 | - | -0.401 | -0.089% |
| 1693 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c4, tf M30 | 8.6 | 24% | -0.229 | -0.074% | -0.103% | 14% | -0.14% | 504.4 | 0 | - | -0.207 | -0.086% |
| 1694 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf M5 | 5.4 | 37% | -0.230 | -0.066% | -0.091% | 25% | -0.16% | 806.8 | 0 | - | +0.000 | +0.000% |
| 1695 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c4, tf M5 | 43.7 | 23% | -0.230 | -0.073% | -0.102% | 18% | -0.20% | 98.9 | 1 | -2.6% | -0.051 | -0.034% |
| 1696 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c34, tf M5 | 46.7 | 25% | -0.230 | -0.075% | -0.104% | 22% | -0.22% | 92.5 | 1 | -2.5% | -0.081 | -0.045% |
| 1697 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf M30 | 7.7 | 17% | -0.230 | -0.075% | -0.104% | 33% | -0.25% | 562.3 | 0 | - | +0.034 | -0.071% |
| 1698 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf M5 | 19.7 | 38% | -0.230 | -0.066% | -0.092% | 18% | -0.20% | 219.6 | 0 | - | -0.193 | -0.069% |
| 1699 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf M15 | 9.3 | 39% | -0.230 | -0.084% | -0.116% | 0% | -0.19% | 463.7 | 0 | - | -0.034 | -0.037% |
| 1700 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop all4, tf M5 | 47.5 | 25% | -0.232 | -0.075% | -0.104% | 17% | -0.22% | 91.0 | 1 | -2.4% | -0.086 | -0.048% |
| 1701 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf H4 | 4.6 | 31% | -0.233 | -0.081% | -0.112% | 33% | -0.17% | 940.5 | 0 | - | +0.153 | +2.771% |
| 1702 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c4, tf M5 | 46.1 | 24% | -0.233 | -0.075% | -0.104% | 20% | -0.19% | 93.6 | 1 | -2.6% | -0.098 | -0.052% |
| 1703 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop all4, tf H1 | 7.7 | 34% | -0.233 | -0.068% | -0.095% | 17% | -0.26% | 562.6 | 0 | - | -0.275 | -0.053% |
| 1704 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf M5 | 17.0 | 38% | -0.234 | -0.077% | -0.106% | 13% | -0.20% | 253.4 | 0 | - | -0.152 | -0.066% |
| 1705 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c34, tf M5 | 44.6 | 24% | -0.234 | -0.074% | -0.103% | 23% | -0.21% | 96.9 | 1 | -2.6% | -0.058 | -0.038% |
| 1706 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf M15 | 6.9 | 16% | -0.234 | -0.074% | -0.102% | 20% | -0.13% | 624.5 | 0 | - | -0.053 | -0.047% |
| 1707 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c34, tf H1 | 7.6 | 34% | -0.234 | -0.067% | -0.093% | 17% | -0.19% | 571.0 | 0 | - | -0.133 | -0.041% |
| 1708 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf M15 | 9.2 | 12% | -0.234 | -0.082% | -0.114% | 0% | -0.16% | 469.3 | 0 | - | +0.189 | +1.035% |
| 1709 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c4, tf M30 | 8.6 | 28% | -0.234 | -0.072% | -0.100% | 29% | -0.16% | 504.4 | 0 | - | -0.313 | -0.089% |
| 1710 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf M15 | 7.2 | 30% | -0.235 | -0.075% | -0.105% | 20% | -0.22% | 598.2 | 0 | - | +0.042 | +0.722% |
| 1711 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf M15 | 20.9 | 38% | -0.236 | -0.073% | -0.101% | 28% | -0.26% | 206.9 | 0 | - | +0.075 | +0.380% |
| 1712 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf M5 | 23.8 | 38% | -0.236 | -0.073% | -0.102% | 10% | -0.19% | 181.2 | 0 | - | -0.172 | -0.071% |
| 1713 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf M5 | 76.1 | 38% | -0.236 | -0.073% | -0.101% | 13% | -0.25% | 56.8 | 1 | -3.0% | -0.137 | -0.058% |
| 1714 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf M5 | 14.7 | 38% | -0.237 | -0.070% | -0.097% | 25% | -0.29% | 293.6 | 0 | - | -0.209 | -0.081% |
| 1715 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.238 | -0.087% | -0.121% | 0% | -0.14% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1716 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf M5 | 17.8 | 23% | -0.239 | -0.067% | -0.093% | 27% | -0.24% | 242.3 | 0 | - | -0.075 | -0.049% |
| 1717 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop all4, tf M30 | 8.6 | 28% | -0.240 | -0.072% | -0.100% | 14% | -0.23% | 504.4 | 0 | - | -0.070 | -0.079% |
| 1718 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c34, tf M30 | 8.6 | 25% | -0.240 | -0.072% | -0.099% | 14% | -0.22% | 504.4 | 0 | - | -0.137 | -0.083% |
| 1719 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c34, tf M5 | 186.1 | 38% | -0.241 | -0.073% | -0.101% | 12% | -0.38% | 23.2 | 4 | -2.4%, -3.2%, -2.6%, -2.4% | -0.193 | -0.067% |
| 1720 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c4, tf M30 | 8.3 | 38% | -0.241 | -0.069% | -0.095% | 29% | -0.22% | 518.1 | 0 | - | -0.061 | +0.024% |
| 1721 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop all4, tf M30 | 8.5 | 37% | -0.241 | -0.069% | -0.095% | 43% | -0.24% | 511.2 | 0 | - | -0.247 | -0.081% |
| 1722 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf M15 | 15.4 | 17% | -0.242 | -0.074% | -0.103% | 15% | -0.19% | 280.8 | 0 | - | +0.045 | -0.033% |
| 1723 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf H1 | 3.2 | 32% | -0.243 | -0.083% | -0.115% | 0% | -0.12% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1724 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop all4, tf H1 | 7.6 | 36% | -0.243 | -0.070% | -0.097% | 17% | -0.20% | 571.0 | 0 | - | -0.326 | -0.089% |
| 1725 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf M15 | 20.5 | 24% | -0.243 | -0.072% | -0.100% | 17% | -0.24% | 210.3 | 0 | - | +0.195 | +1.182% |
| 1726 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop all4, tf M5 | 13.3 | 22% | -0.245 | -0.072% | -0.100% | 27% | -0.18% | 325.7 | 0 | - | -0.157 | -0.081% |
| 1727 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf M15 | 47.7 | 38% | -0.246 | -0.074% | -0.102% | 14% | -0.22% | 90.5 | 1 | -2.7% | -0.037 | -0.017% |
| 1728 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf M15 | 7.5 | 28% | -0.247 | -0.078% | -0.109% | 17% | -0.20% | 578.5 | 0 | - | -0.350 | -0.091% |
| 1729 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c34, tf H4 | 4.6 | 31% | -0.248 | -0.081% | -0.113% | 33% | -0.18% | 940.5 | 0 | - | +0.145 | +2.324% |
| 1730 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf M30 | 5.6 | 22% | -0.248 | -0.071% | -0.098% | 50% | -0.22% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1731 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf M15 | 10.9 | 23% | -0.249 | -0.073% | -0.101% | 11% | -0.20% | 396.7 | 0 | - | -0.019 | +0.121% |
| 1732 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf M15 | 39.8 | 38% | -0.249 | -0.076% | -0.105% | 14% | -0.24% | 108.6 | 0 | - | -0.158 | -0.063% |
| 1733 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf M15 | 7.0 | 38% | -0.251 | -0.072% | -0.100% | 0% | -0.14% | 613.3 | 0 | - | -0.317 | -0.085% |
| 1734 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c4, tf H1 | 7.6 | 34% | -0.252 | -0.066% | -0.091% | 17% | -0.20% | 571.0 | 0 | - | -0.292 | -0.087% |
| 1735 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf M5 | 23.8 | 19% | -0.252 | -0.073% | -0.101% | 29% | -0.18% | 181.2 | 0 | - | +0.009 | -0.050% |
| 1736 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf M30 | 5.6 | 22% | -0.253 | -0.071% | -0.099% | 50% | -0.22% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1737 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop all4, tf H1 | 7.2 | 28% | -0.253 | -0.076% | -0.106% | 33% | -0.19% | 597.7 | 0 | - | -0.397 | -0.090% |
| 1738 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop all4, tf H4 | 4.6 | 31% | -0.254 | -0.082% | -0.114% | 33% | -0.17% | 940.5 | 0 | - | +0.133 | +2.233% |
| 1739 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade AB, stop c4, tf M5 | 147.8 | 38% | -0.254 | -0.074% | -0.102% | 14% | -0.30% | 29.2 | 3 | -3.1%, -2.1%, -2.9% | -0.186 | -0.067% |
| 1740 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf M15 | 20.9 | 37% | -0.257 | -0.076% | -0.106% | 22% | -0.26% | 206.9 | 0 | - | +0.046 | +0.250% |
| 1741 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop all4, tf H1 | 7.3 | 32% | -0.258 | -0.062% | -0.086% | 33% | -0.23% | 588.5 | 0 | - | -0.314 | -0.081% |
| 1742 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop all4, tf M5 | 13.3 | 38% | -0.261 | -0.078% | -0.108% | 18% | -0.22% | 325.7 | 0 | - | -0.214 | -0.085% |
| 1743 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop all4, tf H1 | 3.9 | 29% | -0.262 | -0.089% | -0.124% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1744 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf M15 | 21.2 | 36% | -0.264 | -0.076% | -0.106% | 17% | -0.26% | 203.6 | 0 | - | +0.049 | +0.227% |
| 1745 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf M5 | 19.5 | 37% | -0.265 | -0.079% | -0.110% | 12% | -0.18% | 221.4 | 0 | - | -0.033 | -0.037% |
| 1746 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf M5 | 21.8 | 19% | -0.266 | -0.076% | -0.106% | 21% | -0.21% | 197.8 | 0 | - | -0.083 | -0.038% |
| 1747 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf M30 | 5.6 | 22% | -0.267 | -0.074% | -0.103% | 25% | -0.20% | 766.8 | 0 | - | +0.000 | +0.000% |
| 1748 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c4, tf M30 | 8.6 | 21% | -0.269 | -0.077% | -0.107% | 14% | -0.20% | 504.4 | 0 | - | -0.132 | -0.083% |
| 1749 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf M5 | 5.4 | 15% | -0.271 | -0.060% | -0.083% | 25% | -0.23% | 806.8 | 0 | - | +0.000 | +0.000% |
| 1750 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf M15 | 7.0 | 27% | -0.273 | -0.070% | -0.097% | 20% | -0.21% | 613.3 | 0 | - | -0.381 | -0.091% |
| 1751 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c34, tf H1 | 7.6 | 33% | -0.274 | -0.067% | -0.093% | 17% | -0.19% | 571.0 | 0 | - | -0.320 | -0.088% |
| 1752 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop all4, tf H1 | 3.9 | 26% | -0.275 | -0.088% | -0.122% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1753 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf M15 | 7.3 | 37% | -0.276 | -0.079% | -0.110% | 0% | -0.15% | 588.2 | 0 | - | -0.079 | -0.065% |
| 1754 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf M15 | 13.8 | 24% | -0.277 | -0.080% | -0.111% | 18% | -0.18% | 314.1 | 0 | - | -0.139 | -0.079% |
| 1755 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf M15 | 12.5 | 17% | -0.277 | -0.080% | -0.111% | 10% | -0.19% | 347.0 | 0 | - | +0.096 | +0.102% |
| 1756 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf M30 | 4.8 | 36% | -0.278 | -0.084% | -0.117% | 0% | -0.12% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1757 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf M30 | 7.7 | 14% | -0.278 | -0.080% | -0.111% | 17% | -0.20% | 562.3 | 0 | - | +0.011 | -0.078% |
| 1758 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf M5 | 14.7 | 19% | -0.279 | -0.074% | -0.103% | 25% | -0.21% | 293.6 | 0 | - | -0.030 | -0.007% |
| 1759 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.280 | -0.087% | -0.121% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1760 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c34, tf M30 | 8.5 | 36% | -0.281 | -0.071% | -0.099% | 29% | -0.21% | 511.2 | 0 | - | -0.207 | -0.075% |
| 1761 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf M5 | 22.9 | 20% | -0.281 | -0.077% | -0.108% | 20% | -0.22% | 189.0 | 0 | - | -0.100 | -0.044% |
| 1762 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf M30 | 7.9 | 22% | -0.282 | -0.079% | -0.110% | 14% | -0.19% | 546.5 | 0 | - | -0.066 | -0.085% |
| 1763 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop all4, tf H1 | 7.6 | 34% | -0.285 | -0.070% | -0.098% | 17% | -0.20% | 571.0 | 0 | - | -0.326 | -0.089% |
| 1764 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c34, tf M30 | 8.6 | 37% | -0.287 | -0.072% | -0.100% | 29% | -0.21% | 504.4 | 0 | - | -0.313 | -0.084% |
| 1765 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf M30 | 4.8 | 20% | -0.289 | -0.083% | -0.115% | 0% | -0.14% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1766 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop all4, tf H1 | 3.9 | 26% | -0.292 | -0.089% | -0.124% | 0% | -0.13% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1767 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop all4, tf M15 | 4.5 | 35% | -0.293 | -0.084% | -0.116% | 33% | -0.17% | 969.2 | 0 | - | +0.039 | -0.001% |
| 1768 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf M15 | 21.6 | 33% | -0.294 | -0.078% | -0.108% | 10% | -0.19% | 200.4 | 0 | - | -0.197 | -0.073% |
| 1769 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf M15 | 21.2 | 33% | -0.294 | -0.077% | -0.107% | 17% | -0.17% | 203.6 | 0 | - | -0.235 | -0.078% |
| 1770 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf H4 | 4.6 | 31% | -0.295 | -0.085% | -0.118% | 33% | -0.17% | 940.5 | 0 | - | +0.158 | +2.933% |
| 1771 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf M15 | 21.2 | 33% | -0.296 | -0.079% | -0.110% | 11% | -0.17% | 203.6 | 0 | - | -0.234 | -0.078% |
| 1772 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf M5 | 37.4 | 20% | -0.299 | -0.079% | -0.110% | 15% | -0.20% | 115.5 | 0 | - | -0.028 | -0.057% |
| 1773 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade AB, stop c4, tf H4 | 4.7 | 28% | -0.299 | -0.080% | -0.112% | 25% | -0.12% | 917.0 | 0 | - | -0.154 | -0.085% |
| 1774 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade AB, stop c4, tf H4 | 4.7 | 28% | -0.301 | -0.085% | -0.118% | 0% | -0.10% | 917.0 | 0 | - | -0.020 | -0.073% |
| 1775 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf H1 | 3.0 | 27% | -0.304 | -0.079% | -0.110% | 0% | -0.20% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 1776 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf M15 | 20.5 | 32% | -0.304 | -0.079% | -0.109% | 11% | -0.22% | 210.3 | 0 | - | -0.207 | -0.075% |
| 1777 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf M15 | 7.5 | 15% | -0.305 | -0.074% | -0.103% | 17% | -0.16% | 572.4 | 0 | - | -0.519 | -0.091% |
| 1778 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf M15 | 13.8 | 16% | -0.307 | -0.081% | -0.113% | 9% | -0.18% | 314.1 | 0 | - | +0.100 | +0.112% |
| 1779 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop all4, tf M30 | 8.6 | 28% | -0.308 | -0.077% | -0.106% | 14% | -0.21% | 504.4 | 0 | - | -0.139 | -0.083% |
| 1780 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf M15 | 14.6 | 18% | -0.309 | -0.081% | -0.112% | 8% | -0.17% | 296.7 | 0 | - | +0.074 | +0.035% |
| 1781 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf M15 | 20.7 | 32% | -0.310 | -0.078% | -0.109% | 11% | -0.20% | 209.2 | 0 | - | -0.203 | -0.075% |
| 1782 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop all4, tf M30 | 8.5 | 21% | -0.311 | -0.076% | -0.106% | 14% | -0.20% | 511.2 | 0 | - | -0.218 | -0.087% |
| 1783 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c34, tf H1 | 3.9 | 26% | -0.311 | -0.089% | -0.123% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1784 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c34, tf H1 | 7.6 | 27% | -0.311 | -0.077% | -0.108% | 17% | -0.17% | 571.0 | 0 | - | -0.375 | -0.089% |
| 1785 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c34, tf H1 | 3.9 | 26% | -0.312 | -0.087% | -0.121% | 0% | -0.14% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1786 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf M15 | 15.1 | 17% | -0.314 | -0.081% | -0.112% | 8% | -0.18% | 285.2 | 0 | - | +0.090 | +0.065% |
| 1787 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c34, tf H1 | 3.9 | 26% | -0.314 | -0.089% | -0.124% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1788 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf M15 | 15.4 | 24% | -0.314 | -0.080% | -0.111% | 8% | -0.21% | 280.8 | 0 | - | -0.144 | -0.078% |
| 1789 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf M15 | 20.5 | 31% | -0.315 | -0.079% | -0.110% | 17% | -0.18% | 210.3 | 0 | - | -0.175 | -0.072% |
| 1790 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c4, tf H1 | 7.6 | 31% | -0.315 | -0.067% | -0.093% | 17% | -0.20% | 571.0 | 0 | - | -0.306 | -0.079% |
| 1791 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c34, tf H1 | 7.7 | 31% | -0.316 | -0.067% | -0.093% | 17% | -0.21% | 562.6 | 0 | - | -0.319 | -0.079% |
| 1792 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop all4, tf H1 | 3.9 | 32% | -0.319 | -0.087% | -0.121% | 33% | -0.11% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1793 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c4, tf H1 | 7.6 | 28% | -0.319 | -0.078% | -0.108% | 17% | -0.16% | 571.0 | 0 | - | -0.367 | -0.088% |
| 1794 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf M5 | 39.5 | 19% | -0.319 | -0.080% | -0.111% | 9% | -0.18% | 109.2 | 0 | - | -0.040 | -0.058% |
| 1795 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf M30 | 4.8 | 23% | -0.322 | -0.084% | -0.116% | 0% | -0.14% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1796 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c4, tf H1 | 4.0 | 29% | -0.323 | -0.089% | -0.124% | 0% | -0.14% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1797 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf M5 | 17.8 | 17% | -0.324 | -0.076% | -0.106% | 20% | -0.18% | 242.3 | 0 | - | -0.057 | -0.024% |
| 1798 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf M15 | 7.0 | 14% | -0.324 | -0.071% | -0.099% | 20% | -0.16% | 613.3 | 0 | - | -0.703 | -0.091% |
| 1799 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade AB, stop c4, tf H4 | 4.7 | 28% | -0.324 | -0.086% | -0.119% | 0% | -0.10% | 917.0 | 0 | - | -0.126 | -0.081% |
| 1800 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade AB, stop c4, tf H4 | 4.7 | 28% | -0.324 | -0.086% | -0.119% | 0% | -0.10% | 917.0 | 0 | - | -0.073 | -0.078% |
| 1801 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf H1 | 3.2 | 29% | -0.325 | -0.071% | -0.099% | 0% | -0.03% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1802 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf M5 | 21.2 | 18% | -0.330 | -0.079% | -0.110% | 22% | -0.20% | 204.2 | 0 | - | -0.064 | -0.026% |
| 1803 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf M30 | 4.8 | 33% | -0.330 | -0.082% | -0.114% | 0% | -0.11% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1804 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf M30 | 4.9 | 32% | -0.330 | -0.085% | -0.118% | 0% | -0.18% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1805 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop all4, tf H1 | 7.6 | 27% | -0.331 | -0.080% | -0.111% | 17% | -0.17% | 571.0 | 0 | - | -0.367 | -0.088% |
| 1806 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf M30 | 4.9 | 32% | -0.332 | -0.082% | -0.113% | 25% | -0.26% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1807 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c4, tf H1 | 4.0 | 29% | -0.333 | -0.090% | -0.125% | 0% | -0.13% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1808 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf M15 | 9.2 | 13% | -0.335 | -0.085% | -0.118% | 0% | -0.15% | 469.3 | 0 | - | +0.155 | +0.846% |
| 1809 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf H1 | 3.5 | 30% | -0.336 | -0.089% | -0.124% | 0% | -0.11% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 1810 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf M5 | 29.0 | 19% | -0.336 | -0.078% | -0.109% | 16% | -0.18% | 148.8 | 0 | - | +0.001 | -0.050% |
| 1811 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf H1 | 3.2 | 29% | -0.338 | -0.076% | -0.106% | 0% | -0.07% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1812 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf M5 | 19.7 | 18% | -0.341 | -0.080% | -0.111% | 18% | -0.20% | 219.6 | 0 | - | -0.100 | -0.046% |
| 1813 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop all4, tf H1 | 7.7 | 31% | -0.342 | -0.069% | -0.096% | 17% | -0.20% | 562.6 | 0 | - | -0.337 | -0.081% |
| 1814 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.342 | -0.087% | -0.121% | 0% | -0.13% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1815 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf M15 | 8.0 | 14% | -0.345 | -0.078% | -0.108% | 17% | -0.17% | 542.9 | 0 | - | -0.560 | -0.090% |
| 1816 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c4, tf H1 | 4.0 | 29% | -0.347 | -0.090% | -0.125% | 0% | -0.14% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1817 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf M15 | 7.3 | 15% | -0.349 | -0.079% | -0.110% | 17% | -0.14% | 588.2 | 0 | - | -0.564 | -0.092% |
| 1818 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c4, tf M30 | 8.6 | 34% | -0.349 | -0.077% | -0.106% | 29% | -0.18% | 504.4 | 0 | - | -0.241 | -0.082% |
| 1819 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf M15 | 7.7 | 14% | -0.351 | -0.077% | -0.107% | 17% | -0.14% | 560.2 | 0 | - | -0.524 | -0.091% |
| 1820 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf M15 | 7.7 | 27% | -0.351 | -0.081% | -0.112% | 0% | -0.21% | 560.2 | 0 | - | -0.366 | -0.084% |
| 1821 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.352 | -0.088% | -0.123% | 0% | -0.13% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1822 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf M15 | 7.5 | 25% | -0.356 | -0.077% | -0.106% | 17% | -0.20% | 572.4 | 0 | - | -0.238 | -0.091% |
| 1823 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf M15 | 8.1 | 14% | -0.360 | -0.079% | -0.109% | 17% | -0.13% | 534.7 | 0 | - | -0.505 | -0.090% |
| 1824 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf M15 | 8.0 | 26% | -0.364 | -0.078% | -0.108% | 17% | -0.20% | 542.9 | 0 | - | -0.383 | -0.091% |
| 1825 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf M5 | 33.3 | 19% | -0.367 | -0.081% | -0.113% | 7% | -0.16% | 129.6 | 0 | - | -0.029 | -0.059% |
| 1826 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf M5 | 35.8 | 19% | -0.367 | -0.081% | -0.113% | 10% | -0.20% | 120.6 | 0 | - | -0.028 | -0.060% |
| 1827 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf M30 | 4.8 | 20% | -0.378 | -0.088% | -0.122% | 0% | -0.13% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1828 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf M30 | 4.3 | 31% | -0.380 | -0.084% | -0.117% | 0% | -0.10% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1829 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf M30 | 4.9 | 20% | -0.385 | -0.087% | -0.122% | 0% | -0.14% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1830 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf M15 | 7.4 | 24% | -0.389 | -0.080% | -0.111% | 20% | -0.15% | 582.1 | 0 | - | -0.059 | -0.025% |
| 1831 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf H1 | 3.2 | 29% | -0.392 | -0.077% | -0.108% | 0% | -0.05% | 1331.4 | 0 | - | +0.000 | +0.000% |
| 1832 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf H1 | 3.5 | 27% | -0.402 | -0.082% | -0.114% | 0% | -0.18% | 1242.6 | 0 | - | +0.000 | +0.000% |
| 1833 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c4, tf H1 | 4.0 | 31% | -0.402 | -0.090% | -0.126% | 0% | -0.14% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1834 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf M30 | 4.4 | 31% | -0.404 | -0.089% | -0.123% | 0% | -0.12% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1835 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf M30 | 4.4 | 17% | -0.407 | -0.080% | -0.111% | 33% | -0.18% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1836 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf M30 | 4.9 | 20% | -0.414 | -0.089% | -0.124% | 0% | -0.13% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1837 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf M30 | 4.9 | 25% | -0.416 | -0.089% | -0.123% | 0% | -0.16% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1838 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c34, tf H1 | 3.9 | 29% | -0.418 | -0.089% | -0.123% | 0% | -0.12% | 1098.6 | 0 | - | +0.000 | +0.000% |
| 1839 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf H1 | 3.0 | 23% | -0.435 | -0.076% | -0.106% | 0% | -0.09% | 1433.8 | 0 | - | +0.000 | +0.000% |
| 1840 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf H1 | 3.1 | 22% | -0.440 | -0.077% | -0.107% | 0% | -0.07% | 1380.7 | 0 | - | +0.000 | +0.000% |
| 1841 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf M30 | 4.8 | 23% | -0.440 | -0.088% | -0.122% | 0% | -0.12% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1842 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf M30 | 4.9 | 18% | -0.444 | -0.086% | -0.120% | 0% | -0.13% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1843 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop all4, tf H1 | 4.0 | 31% | -0.451 | -0.091% | -0.126% | 0% | -0.14% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1844 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf M30 | 4.9 | 25% | -0.452 | -0.090% | -0.125% | 0% | -0.15% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1845 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf M30 | 4.8 | 15% | -0.457 | -0.082% | -0.114% | 0% | -0.15% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1846 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop all4, tf H1 | 4.0 | 31% | -0.464 | -0.091% | -0.127% | 0% | -0.14% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1847 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf M30 | 5.4 | 19% | -0.477 | -0.080% | -0.111% | 25% | -0.14% | 799.4 | 0 | - | +0.000 | +0.000% |
| 1848 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf M15 | 6.9 | 18% | -0.489 | -0.081% | -0.112% | 0% | -0.12% | 624.5 | 0 | - | -0.084 | -0.026% |
| 1849 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c34, tf H1 | 4.0 | 31% | -0.493 | -0.091% | -0.127% | 0% | -0.13% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1850 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf M30 | 4.4 | 8% | -0.493 | -0.080% | -0.111% | 0% | -0.13% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1851 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c34, tf H1 | 4.0 | 31% | -0.498 | -0.092% | -0.127% | 0% | -0.13% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1852 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf M30 | 5.5 | 19% | -0.503 | -0.079% | -0.110% | 25% | -0.15% | 782.7 | 0 | - | +0.000 | +0.000% |
| 1853 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c4, tf H1 | 4.0 | 31% | -0.517 | -0.092% | -0.128% | 0% | -0.13% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1854 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf M30 | 4.9 | 12% | -0.523 | -0.090% | -0.125% | 0% | -0.12% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1855 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c4, tf H1 | 4.0 | 31% | -0.525 | -0.092% | -0.127% | 0% | -0.13% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1856 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf H4 | 4.7 | 20% | -0.528 | -0.088% | -0.123% | 0% | -0.12% | 917.0 | 0 | - | +0.110 | +1.329% |
| 1857 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c34, tf H4 | 4.6 | 18% | -0.529 | -0.092% | -0.127% | 0% | -0.12% | 940.5 | 0 | - | +0.042 | +0.674% |
| 1858 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf H4 | 4.6 | 18% | -0.551 | -0.092% | -0.127% | 0% | -0.11% | 940.5 | 0 | - | +0.040 | +0.512% |
| 1859 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf M30 | 4.9 | 15% | -0.553 | -0.086% | -0.119% | 0% | -0.18% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1860 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf H4 | 4.7 | 18% | -0.553 | -0.089% | -0.123% | 0% | -0.12% | 917.0 | 0 | - | -0.360 | -0.088% |
| 1861 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade AB, stop c4, tf H4 | 4.6 | 18% | -0.555 | -0.092% | -0.128% | 0% | -0.13% | 940.5 | 0 | - | +0.039 | +0.723% |
| 1862 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop all4, tf H1 | 4.0 | 31% | -0.558 | -0.090% | -0.125% | 0% | -0.16% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1863 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf M30 | 4.4 | 8% | -0.558 | -0.085% | -0.118% | 0% | -0.12% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1864 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop all4, tf H1 | 4.0 | 31% | -0.573 | -0.090% | -0.125% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1865 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade AB, stop all4, tf H4 | 4.6 | 18% | -0.583 | -0.091% | -0.126% | 0% | -0.13% | 940.5 | 0 | - | +0.085 | +0.989% |
| 1866 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c34, tf H1 | 4.0 | 31% | -0.584 | -0.091% | -0.126% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1867 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c34, tf H1 | 4.0 | 31% | -0.594 | -0.091% | -0.126% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1868 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c4, tf H1 | 4.0 | 31% | -0.596 | -0.091% | -0.126% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1869 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf M30 | 4.9 | 10% | -0.598 | -0.090% | -0.124% | 0% | -0.15% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1870 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf M30 | 4.9 | 12% | -0.604 | -0.092% | -0.127% | 0% | -0.12% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1871 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c4, tf H1 | 4.0 | 31% | -0.605 | -0.091% | -0.126% | 0% | -0.15% | 1067.2 | 0 | - | +0.000 | +0.000% |
| 1872 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf M30 | 4.9 | 18% | -0.623 | -0.089% | -0.123% | 0% | -0.16% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1873 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf M30 | 4.3 | 11% | -0.633 | -0.083% | -0.115% | 0% | -0.16% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1874 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf M30 | 4.9 | 18% | -0.656 | -0.089% | -0.123% | 0% | -0.17% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1875 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf M30 | 4.3 | 17% | -0.660 | -0.088% | -0.123% | 0% | -0.15% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1876 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf M30 | 4.8 | 8% | -0.667 | -0.089% | -0.123% | 0% | -0.10% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1877 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf M30 | 4.8 | 15% | -0.694 | -0.091% | -0.126% | 0% | -0.15% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1878 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf M30 | 4.4 | 17% | -0.694 | -0.092% | -0.128% | 0% | -0.14% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1879 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf M30 | 4.9 | 10% | -0.695 | -0.091% | -0.127% | 0% | -0.15% | 877.6 | 0 | - | +0.000 | +0.000% |
| 1880 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf M30 | 4.8 | 10% | -0.698 | -0.086% | -0.120% | 0% | -0.11% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1881 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf M30 | 4.3 | 20% | -0.729 | -0.089% | -0.124% | 0% | -0.14% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1882 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf M30 | 4.8 | 15% | -0.746 | -0.092% | -0.128% | 0% | -0.14% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1883 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf M30 | 4.3 | 14% | -0.757 | -0.093% | -0.130% | 0% | -0.12% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1884 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf M30 | 4.4 | 19% | -0.786 | -0.093% | -0.129% | 0% | -0.13% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1885 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf M30 | 4.8 | 5% | -0.802 | -0.091% | -0.127% | 0% | -0.12% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1886 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf M30 | 4.8 | 5% | -0.814 | -0.092% | -0.127% | 0% | -0.12% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1887 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf M30 | 4.4 | 17% | -0.966 | -0.093% | -0.129% | 0% | -0.12% | 975.1 | 0 | - | +0.000 | +0.000% |
| 1888 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf M30 | 4.8 | 5% | -0.981 | -0.093% | -0.129% | 0% | -0.11% | 900.1 | 0 | - | +0.000 | +0.000% |
| 1889 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf M30 | 4.3 | 3% | -1.581 | -0.094% | -0.130% | 0% | -0.12% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1890 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf M30 | 4.3 | 3% | -1.581 | -0.094% | -0.130% | 0% | -0.12% | 1003.0 | 0 | - | +0.000 | +0.000% |
| 1891 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1892 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1893 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1894 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1895 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1896 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1897 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1898 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1899 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1900 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1901 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1902 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1903 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1904 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1905 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1906 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1907 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1908 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1909 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1910 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1911 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1912 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1913 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1914 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1915 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1916 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1917 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1918 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1919 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1920 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1921 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1922 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1923 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1924 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1925 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1926 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1927 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1928 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1929 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1930 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1931 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1932 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf M15 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1933 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1934 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1935 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1936 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1937 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1938 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1939 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1940 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1941 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1942 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1943 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1944 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1945 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1946 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1947 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1948 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1949 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1950 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1951 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1952 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1953 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1954 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1955 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1956 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1957 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1958 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1959 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1960 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1961 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1962 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1963 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1964 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1965 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1966 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1967 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1968 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1969 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1970 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1971 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1972 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1973 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1974 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1975 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1976 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1977 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1978 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1979 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1980 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1981 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1982 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1983 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1984 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1985 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1986 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1987 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1988 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1989 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1990 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1991 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1992 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1993 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1994 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1995 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1996 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1997 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1998 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 1999 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2000 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2001 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2002 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c34, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2003 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2004 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2005 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2006 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2007 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2008 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2009 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2010 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2011 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2012 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2013 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2014 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2015 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2016 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop all4, tf M30 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2017 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2018 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2019 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2020 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2021 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2022 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2023 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2024 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2025 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2026 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2027 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2028 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2029 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2030 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2031 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2032 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2033 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2034 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2035 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2036 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2037 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2038 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2039 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2040 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2041 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2042 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2043 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2044 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2045 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2046 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2047 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2048 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2049 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2050 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2051 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2052 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2053 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2054 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2055 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2056 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2057 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2058 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2059 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2060 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2061 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2062 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2063 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2064 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2065 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2066 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2067 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2068 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2069 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2070 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2071 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2072 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2073 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2074 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2075 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2076 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2077 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2078 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2079 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2080 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2081 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2082 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2083 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2084 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2085 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2086 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2087 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2088 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2089 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2090 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2091 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2092 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2093 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2094 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2095 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2096 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2097 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2098 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2099 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2100 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2101 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2102 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2103 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2104 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2105 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2106 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2107 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2108 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2109 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2110 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2111 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2112 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2113 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2114 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2115 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2116 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2117 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2118 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2119 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2120 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2121 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2122 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2123 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2124 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2125 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2126 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2127 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2128 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c34, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2129 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2130 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2131 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2132 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2133 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2134 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2135 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2136 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2137 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2138 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2139 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2140 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2141 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2142 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop all4, tf H1 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2143 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2144 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2145 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2146 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2147 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2148 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2149 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2150 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2151 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2152 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2153 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2154 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2155 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2156 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2157 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2158 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2159 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2160 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2161 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2162 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2163 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2164 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2165 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2166 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2167 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2168 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2169 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2170 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2171 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2172 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2173 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2174 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2175 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2176 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2177 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2178 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2179 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2180 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2181 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2182 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2183 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2184 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2185 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2186 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2187 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2188 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2189 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2190 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2191 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2192 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2193 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2194 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2195 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2196 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2197 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2198 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2199 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2200 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2201 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2202 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2203 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2204 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2205 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2206 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2207 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2208 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2209 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2210 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2211 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2212 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2213 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2214 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2215 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2216 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2217 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2218 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2219 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2220 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2221 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2222 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2223 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2224 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2225 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2226 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2227 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2228 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2229 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2230 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2231 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2232 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2233 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2234 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2235 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2236 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2237 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2238 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2239 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2240 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2241 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2242 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2243 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2244 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2245 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2246 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2247 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2248 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2249 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2250 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2251 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2252 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2253 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2254 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2255 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2256 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2257 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2258 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2259 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2260 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2261 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2262 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2263 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2264 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2265 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2266 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2267 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2268 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2269 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2270 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2271 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2272 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2273 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2274 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2275 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2276 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2277 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2278 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2279 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2280 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2281 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2282 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2283 | buffer 0.0, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2284 | buffer 0.0, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2285 | buffer 0.0, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2286 | buffer 0.0, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2287 | buffer 0.0, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2288 | buffer 0.0, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2289 | buffer 0.0, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2290 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2291 | buffer 0.0, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2292 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2293 | buffer 0.0, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2294 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2295 | buffer 0.0, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2296 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2297 | buffer 0.0, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2298 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2299 | buffer 0.0, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2300 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2301 | buffer 0.0, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2302 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2303 | buffer 0.0, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2304 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2305 | buffer 0.0, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2306 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2307 | buffer 0.0, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2308 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2309 | buffer 0.0, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2310 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2311 | buffer 0.0, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2312 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2313 | buffer 0.0, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2314 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2315 | buffer 0.0, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2316 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2317 | buffer 0.0, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2318 | buffer 0.5, clear 0.05, entry mid50, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2319 | buffer 0.5, clear 0.05, entry mid50, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2320 | buffer 0.5, clear 0.05, entry mid50, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2321 | buffer 0.5, clear 0.05, entry mid50, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2322 | buffer 0.5, clear 0.05, entry mid50, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2323 | buffer 0.5, clear 0.05, entry mid50, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2324 | buffer 0.5, clear 0.05, entry mid50, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2325 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2326 | buffer 0.5, clear 0.1, entry mid50, exit 1R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2327 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2328 | buffer 0.5, clear 0.1, entry mid50, exit 2R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2329 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2330 | buffer 0.5, clear 0.1, entry mid50, exit 3R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2331 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2332 | buffer 0.5, clear 0.1, entry mid50, exit 4R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2333 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2334 | buffer 0.5, clear 0.1, entry mid50, exit trail1, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2335 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2336 | buffer 0.5, clear 0.1, entry mid50, exit trail2, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2337 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2338 | buffer 0.5, clear 0.1, entry mid50, exit ema, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2339 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2340 | buffer 0.5, clear 0.2, entry mid50, exit 1R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2341 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2342 | buffer 0.5, clear 0.2, entry mid50, exit 2R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2343 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2344 | buffer 0.5, clear 0.2, entry mid50, exit 3R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2345 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2346 | buffer 0.5, clear 0.2, entry mid50, exit 4R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2347 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2348 | buffer 0.5, clear 0.2, entry mid50, exit trail1, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2349 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2350 | buffer 0.5, clear 0.2, entry mid50, exit trail2, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2351 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2352 | buffer 0.5, clear 0.2, entry mid50, exit ema, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2353 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2354 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2355 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2356 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2357 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2358 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2359 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2360 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2361 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2362 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2363 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2364 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2365 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2366 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2367 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2368 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2369 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2370 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2371 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2372 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2373 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2374 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2375 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2376 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2377 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2378 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2379 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2380 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2381 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2382 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2383 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2384 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2385 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2386 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2387 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2388 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2389 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2390 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2391 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2392 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2393 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2394 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2395 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2396 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2397 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2398 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2399 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2400 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2401 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2402 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2403 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2404 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2405 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2406 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2407 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2408 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2409 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2410 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2411 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2412 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2413 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2414 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2415 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2416 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2417 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2418 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2419 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2420 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2421 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2422 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2423 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2424 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2425 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2426 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2427 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2428 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2429 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2430 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2431 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2432 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2433 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2434 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2435 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2436 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2437 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2438 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2439 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2440 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2441 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2442 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2443 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2444 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2445 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2446 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2447 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2448 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2449 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2450 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2451 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2452 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2453 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2454 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2455 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2456 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2457 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2458 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2459 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2460 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2461 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2462 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2463 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2464 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop c34, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2465 | buffer 0.0, clear 0.05, entry close, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2466 | buffer 0.0, clear 0.05, entry close, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2467 | buffer 0.0, clear 0.05, entry close, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2468 | buffer 0.0, clear 0.05, entry close, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2469 | buffer 0.0, clear 0.05, entry close, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2470 | buffer 0.0, clear 0.05, entry close, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2471 | buffer 0.0, clear 0.05, entry close, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2472 | buffer 0.0, clear 0.1, entry close, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2473 | buffer 0.0, clear 0.1, entry close, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2474 | buffer 0.0, clear 0.1, entry close, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2475 | buffer 0.0, clear 0.1, entry close, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2476 | buffer 0.0, clear 0.1, entry close, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2477 | buffer 0.0, clear 0.1, entry close, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2478 | buffer 0.0, clear 0.1, entry close, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2479 | buffer 0.0, clear 0.2, entry close, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2480 | buffer 0.0, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2481 | buffer 0.0, clear 0.2, entry close, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2482 | buffer 0.0, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2483 | buffer 0.0, clear 0.2, entry close, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2484 | buffer 0.0, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2485 | buffer 0.0, clear 0.2, entry close, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2486 | buffer 0.0, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2487 | buffer 0.0, clear 0.2, entry close, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2488 | buffer 0.0, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2489 | buffer 0.0, clear 0.2, entry close, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2490 | buffer 0.0, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2491 | buffer 0.0, clear 0.2, entry close, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2492 | buffer 0.0, clear 0.2, entry close, exit ema, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2493 | buffer 0.5, clear 0.05, entry close, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2494 | buffer 0.5, clear 0.05, entry close, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2495 | buffer 0.5, clear 0.05, entry close, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2496 | buffer 0.5, clear 0.05, entry close, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2497 | buffer 0.5, clear 0.05, entry close, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2498 | buffer 0.5, clear 0.05, entry close, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2499 | buffer 0.5, clear 0.05, entry close, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2500 | buffer 0.5, clear 0.1, entry close, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2501 | buffer 0.5, clear 0.1, entry close, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2502 | buffer 0.5, clear 0.1, entry close, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2503 | buffer 0.5, clear 0.1, entry close, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2504 | buffer 0.5, clear 0.1, entry close, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2505 | buffer 0.5, clear 0.1, entry close, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2506 | buffer 0.5, clear 0.1, entry close, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2507 | buffer 0.5, clear 0.2, entry close, exit 1R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2508 | buffer 0.5, clear 0.2, entry close, exit 1R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2509 | buffer 0.5, clear 0.2, entry close, exit 2R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2510 | buffer 0.5, clear 0.2, entry close, exit 2R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2511 | buffer 0.5, clear 0.2, entry close, exit 3R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2512 | buffer 0.5, clear 0.2, entry close, exit 3R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2513 | buffer 0.5, clear 0.2, entry close, exit 4R, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2514 | buffer 0.5, clear 0.2, entry close, exit 4R, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2515 | buffer 0.5, clear 0.2, entry close, exit trail1, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2516 | buffer 0.5, clear 0.2, entry close, exit trail1, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2517 | buffer 0.5, clear 0.2, entry close, exit trail2, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2518 | buffer 0.5, clear 0.2, entry close, exit trail2, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2519 | buffer 0.5, clear 0.2, entry close, exit ema, grade A, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
| 2520 | buffer 0.5, clear 0.2, entry close, exit ema, grade AB, stop all4, tf H4 | - | 0% | +0.000 | +0.000% | +0.000% | 0% | - | - | 0 | - | +0.000 | +0.000% |
