"""Momentum ignition strategy for AIProve eth-pnl-fixed.

Self-contained (stdlib only). Entry for the bounty:
  positions(bars) -> list of -1/0/1, one position per bar.
  bars: list of dicts {minute, open, high, low, close, volume}.
  position[i] uses only bars[0..i-1] (signal from bar i-1's close, filled at
  bar i's open). No lookahead.

Logic: enter only on rare large moves. z = (close - SMA(120)) / stdev(120).
Long when z > +3.0, short when z < -3.0. Exit when z crosses 0 or after
240 bars. Fires ~9 times in 1440 bars, so fees stay small.

Validated (see ../RESULTS.md): net +$54.77 per 1 ETH at 10 bps round trip,
+$45.80 at 20 bps; IS +$22.69 / OOS +$31.10; profitable on reversed time
(+$29.13) and on every shifted window tested.
"""


def _sma(values, period):
    out = []
    s = 0.0
    for i, v in enumerate(values):
        s += v
        if i >= period:
            s -= values[i - period]
        out.append(s / min(i + 1, period))
    return out


def _stdev(values, period):
    out = []
    for i in range(len(values)):
        w = values[max(0, i - period + 1):i + 1]
        m = sum(w) / len(w)
        var = sum((x - m) ** 2 for x in w) / len(w)
        out.append(var ** 0.5)
    return out


def positions(bars, window=120, z=3.0, max_hold=240):
    closes = [b["close"] for b in bars]
    m = _sma(closes, window)
    s = _stdev(closes, window)
    pos = [0] * len(bars)
    cur = 0
    held = 0
    for i in range(1, len(bars)):
        zi = (closes[i - 1] - m[i - 1]) / s[i - 1] if s[i - 1] > 0 else 0.0
        if cur == 0:
            if zi > z:
                cur = 1
                held = 0
            elif zi < -z:
                cur = -1
                held = 0
        else:
            held += 1
            if (cur == 1 and zi <= 0) or (cur == -1 and zi >= 0) or held >= max_hold:
                cur = 0
        pos[i] = cur
    return pos
