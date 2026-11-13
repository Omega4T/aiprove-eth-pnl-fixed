# aiprove-eth-pnl-fixed

Entry for the [AIProve](https://aiprove.fun) bounty `eth-pnl-fixed` — highest
backtest PnL on the fixed ETH dataset (1,440 real Binance ETH/USDT 1-min
bars, 24h window ending 2026-11-13 12:17 UTC). Deadline: 20 Nov 2026 13:49 UTC.
Rewards: 1st 1,000,000 / 2nd 600,000 / 3rd 400,000 PROVE.

## Strategy: momentum ignition

`strategy.py` exports `positions(bars) -> list of -1/0/1` (one position per
bar, 1 ETH per unit). Enter **only on rare large moves**: z-score of close
vs 120-bar SMA, threshold ±3.0; exit when z crosses 0 or after 240 bars.
Three parameters total (window=120, z=3.0, max_hold=240). Stdlib only, no
lookahead (position[i] uses bars[0..i-1]; filled at bar i's open).

Why this shape: 1-min moves average 0.07% while a round trip costs
~0.10–0.20%, so any strategy that trades often bleeds fees. Ignition fires
9 times in 1,440 bars and catches the two real moves of the day (the
840–959 drop and the 1200–1319 recovery).

## Validated results (per 1 ETH, net of costs)

| scenario | net PnL | fees | trades | max DD |
|---|---:|---:|---:|---:|
| 5 bps round trip | +$59.26 | $4.48 | 9 | $70.00 |
| 10 bps round trip | +$54.77 | $8.97 | 9 | $73.02 |
| 20 bps round trip (realistic taker) | +$45.80 | $17.94 | 9 | $79.05 |

Walk-forward (fit first 2/3, test last 1/3): IS +$22.69, OOS +$31.10.
Robustness: profitable on time-reversed data (+$29.13) and on every shifted
window tested (+$22.69 / +$67.40 / +$78.76). The z∈[2.5,3.0] ×
window∈[120,150] neighbourhood is uniformly profitable — a plateau, not a
knife-edge peak. An ATR trailing-exit variant was tried and REJECTED: it cut
net PnL to -$61 by chopping winners (documented in RESULTS.md).

## Verify

```sh
python3 run.py [bars.csv]
```
