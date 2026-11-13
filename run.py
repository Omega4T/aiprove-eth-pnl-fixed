"""Verify runner: replay strategy.py over bars.csv and print the PnL.
Usage: python3 run.py [bars.csv]  (default: ../challenges/eth-backtest/bars.csv
if present, else expects bars.csv next to this file).
Stdlib only. This is a verification aid; the graded artifact is strategy.py.
"""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategy import positions


def load_bars(path):
    bars = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            bars.append({k: (int(v) if k == "minute" else float(v)) for k, v in r.items()})
    return bars


def run(bars, pos, rt_bps=10.0):
    fill = rt_bps / 2.0 / 10000.0
    prev, prev_close, equity, fees, trades, peak, max_dd = 0, bars[0]["open"], 0.0, 0.0, 0, 0.0, 0.0
    for i, b in enumerate(bars):
        p = pos[i]
        d = p - prev
        if d:
            fee = abs(d) * fill * b["open"]
            fees += fee
            trades += 1
            equity -= fee
        gap = (b["open"] - prev_close) if i > 0 else 0.0
        equity += prev * gap + p * (b["close"] - b["open"])
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        prev, prev_close = p, b["close"]
    return equity, fees, trades, max_dd


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "bars.csv"
    if not os.path.exists(path):
        alt = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "..", "challenges", "eth-backtest", "bars.csv")
        path = alt if os.path.exists(alt) else path
    bars = load_bars(path)
    pos = positions(bars)
    for rt in (5.0, 10.0, 20.0):
        net, fees, trades, dd = run(bars, pos, rt_bps=rt)
        print(f"round-trip {rt:>4.0f} bps: net PnL ${net:>7.2f}  fees ${fees:>5.2f}  "
              f"trades {trades}  max drawdown ${dd:.2f}")
