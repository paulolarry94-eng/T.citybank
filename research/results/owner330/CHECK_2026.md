# The 3:30 scanner on Jan-Oct 2026 (not a clean test: the owner built the idea on this period)

Markets: XAUUSD, EURUSD, GBPUSD, USDJPY, EURGBP (the ones with 2026 minute data here). Net R after RoboForex Prime published costs. Same five markets in 2011-19 and 2020-22 for comparison. Cycle at 3.6% = mean return per 10-trade cycle at the risk where 95% of bootstrapped 360-trade lifecycles stay inside a 3.6% drawdown (negative edge: the loss per cycle).

| Configuration | 2026 trades | 2026 net R | 2026 gross R | 2026 win rate | 2026 cycle at 3.6% | 2011-19 net R | 2020-22 net R |
|---|---|---|---|---|---|---|---|
| anchor wat1530, entry B3, target 3, be 0 | 83 | +0.288 | +0.434 | 37% | +0.49% | -0.232 | -0.244 |
| anchor wat1530, entry B3, target 3, be 1 | 83 | +0.275 | +0.421 | 28% | +0.42% | -0.216 | -0.252 |
| anchor wat1530, entry B6, target 3, be 0 | 84 | +0.274 | +0.421 | 37% | +0.46% | -0.219 | -0.231 |
| anchor wat1530, entry B6, target 3, be 1 | 84 | +0.262 | +0.409 | 27% | +0.40% | -0.201 | -0.241 |
| anchor wat1530, entry B12, target 3, be 0 | 85 | +0.259 | +0.408 | 36% | +0.44% | -0.224 | -0.249 |
| anchor wat1530, entry B12, target 3, be 1 | 85 | +0.247 | +0.396 | 27% | +0.37% | -0.205 | -0.259 |
| anchor wat1530, entry B3, target 2, be 0 | 83 | +0.219 | +0.365 | 43% | +0.47% | -0.208 | -0.233 |
| anchor wat1530, entry B6, target 2, be 0 | 84 | +0.206 | +0.353 | 43% | +0.44% | -0.194 | -0.229 |
| anchor wat1530, entry B3, target 2, be 1 | 83 | +0.203 | +0.349 | 36% | +0.34% | -0.200 | -0.263 |
| anchor wat1530, entry B12, target 2, be 0 | 85 | +0.192 | +0.341 | 42% | +0.41% | -0.199 | -0.248 |
| anchor wat1530, entry B6, target 2, be 1 | 84 | +0.191 | +0.337 | 36% | +0.31% | -0.182 | -0.258 |
| anchor wat1530, entry B12, target 2, be 1 | 85 | +0.177 | +0.325 | 35% | +0.28% | -0.187 | -0.276 |
| anchor wat1530, entry B3, target 4, be 0 | 83 | +0.164 | +0.310 | 34% | +0.13% | -0.250 | -0.211 |
| anchor wat1530, entry A, target 3, be 0 | 93 | +0.162 | +0.307 | 34% | +0.16% | -0.230 | -0.175 |
| anchor wat1530, entry B6, target 4, be 0 | 84 | +0.152 | +0.299 | 33% | +0.12% | -0.234 | -0.205 |
| anchor wat1530, entry B12, target 4, be 0 | 85 | +0.139 | +0.287 | 33% | +0.11% | -0.246 | -0.224 |
| anchor wat1530, entry B3, target 4, be 1 | 83 | +0.134 | +0.280 | 22% | +0.13% | -0.220 | -0.255 |
| anchor wat1530, entry B6, target 4, be 1 | 84 | +0.122 | +0.269 | 21% | +0.12% | -0.208 | -0.248 |
| anchor wat1530, entry B12, target 4, be 1 | 85 | +0.109 | +0.258 | 21% | +0.11% | -0.218 | -0.266 |
| anchor wat1530, entry A, target 3, be 1 | 93 | +0.104 | +0.250 | 25% | +0.11% | -0.217 | -0.201 |
| anchor wat1530, entry A, target 4, be 0 | 93 | +0.095 | +0.240 | 31% | +0.06% | -0.231 | -0.170 |
| anchor wat1530, entry A, target 2, be 0 | 93 | +0.053 | +0.199 | 38% | +0.06% | -0.177 | -0.197 |
| anchor wat1530, entry A, target 2, be 1 | 93 | +0.029 | +0.175 | 31% | +0.03% | -0.165 | -0.200 |
| anchor wat1530, entry A, target 4, be 1 | 93 | -0.019 | +0.126 | 19% | -0.01% | -0.207 | -0.189 |
| anchor ny0930, entry B3, target 2, be 1 | 112 | -0.102 | +0.033 | 25% | -0.04% | -0.155 | -0.193 |
| anchor ny0930, entry B3, target 3, be 0 | 112 | -0.103 | +0.032 | 25% | -0.02% | -0.168 | -0.227 |
| anchor ny0930, entry B6, target 2, be 1 | 114 | -0.109 | +0.025 | 25% | -0.04% | -0.156 | -0.199 |
| anchor ny0930, entry B12, target 2, be 1 | 114 | -0.109 | +0.025 | 25% | -0.04% | -0.155 | -0.202 |
| anchor ny0930, entry B6, target 3, be 0 | 114 | -0.110 | +0.024 | 25% | -0.03% | -0.177 | -0.241 |
| anchor ny0930, entry B12, target 3, be 0 | 114 | -0.110 | +0.024 | 25% | -0.03% | -0.176 | -0.237 |
| anchor ny0930, entry B6, target 2, be 0 | 114 | -0.124 | +0.009 | 30% | -0.03% | -0.159 | -0.209 |
| anchor ny0930, entry B12, target 2, be 0 | 114 | -0.124 | +0.009 | 30% | -0.03% | -0.153 | -0.212 |
| anchor ny0930, entry B3, target 3, be 1 | 112 | -0.129 | +0.006 | 16% | -0.04% | -0.164 | -0.229 |
| anchor ny0930, entry B6, target 3, be 1 | 114 | -0.136 | -0.002 | 16% | -0.05% | -0.169 | -0.240 |
| anchor ny0930, entry B12, target 3, be 1 | 114 | -0.136 | -0.002 | 16% | -0.05% | -0.170 | -0.237 |
| anchor ny0930, entry B3, target 2, be 0 | 112 | -0.136 | -0.001 | 30% | -0.04% | -0.157 | -0.204 |
| anchor ny0930, entry A, target 3, be 0 | 126 | -0.141 | -0.015 | 25% | -0.03% | -0.113 | -0.195 |
| anchor ny0930, entry A, target 3, be 1 | 126 | -0.148 | -0.022 | 17% | -0.04% | -0.109 | -0.186 |
| anchor ny0930, entry A, target 2, be 1 | 126 | -0.162 | -0.036 | 23% | -0.05% | -0.099 | -0.134 |
| anchor ny0930, entry B3, target 4, be 0 | 112 | -0.168 | -0.034 | 22% | -0.04% | -0.164 | -0.228 |
| anchor ny0930, entry A, target 4, be 0 | 126 | -0.169 | -0.042 | 22% | -0.04% | -0.131 | -0.162 |
| anchor ny0930, entry B6, target 4, be 0 | 114 | -0.174 | -0.041 | 22% | -0.04% | -0.174 | -0.242 |
| anchor ny0930, entry B12, target 4, be 0 | 114 | -0.174 | -0.041 | 22% | -0.04% | -0.177 | -0.233 |
| anchor ny0930, entry A, target 4, be 1 | 126 | -0.194 | -0.068 | 14% | -0.05% | -0.119 | -0.143 |
| anchor ny0930, entry A, target 2, be 0 | 126 | -0.208 | -0.082 | 27% | -0.05% | -0.094 | -0.151 |
| anchor ny0930, entry B3, target 4, be 1 | 112 | -0.235 | -0.100 | 12% | -0.06% | -0.150 | -0.196 |
| anchor ny0930, entry B6, target 4, be 1 | 114 | -0.240 | -0.106 | 11% | -0.06% | -0.161 | -0.207 |
| anchor ny0930, entry B12, target 4, be 1 | 114 | -0.240 | -0.106 | 11% | -0.06% | -0.164 | -0.200 |
