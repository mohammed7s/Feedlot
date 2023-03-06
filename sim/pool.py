from dataclasses import dataclass
from loguru import logger
import math
import pandas as pd

class ReserveDepletedError(ValueError):
    def __str__(self):
        return f"Reserve {self.args[0]} depleted!"

class SwapRejectedError(ValueError): pass

class AMMPoolHistory:
    def __init__(self, reserve0, reserve1):
        self.reserves = [reserve0, reserve1]
        self.history = []

    def swap(self, amt0: int, amt1: int, ts: int):
        """
        Swap amt0 of token0 for -amt1 of token1, if reserves permit.
        This function assumes that amt0 and amt1 have opposite sign.
        """
        tmp0 = self.reserves[0] + amt0
        tmp1 = self.reserves[1] + amt1
        if tmp0 >= 0 and tmp1 >= 0:
            self.history.append((tmp0, tmp1))
            self.reserves[0] = tmp0
            self.reserves[1] = tmp1
            return
        elif tmp0 < 0:
            raise ReserveDepletedError(0)
        elif tmp1 < 0:
            raise ReserveDepletedError(1)

class AMMPool:
    def __init__(self, reserve0, reserve1):
        self.reserves = [reserve0, reserve1]

    def swap(self, amt0: int, amt1: int):
        """
        Swap amt0 of token0 for -amt1 of token1, if reserves permit.
        This function assumes that amt0 and amt1 have opposite sign.
        """
        tmp0 = self.reserves[0] + amt0
        tmp1 = self.reserves[1] + amt1
        if tmp0 >= 0 and tmp1 >= 0:
            self.reserves[0] = tmp0
            self.reserves[1] = tmp1
            return
        elif tmp0 < 0:
            raise ReserveDepletedError(0)
        elif tmp1 < 0:
            raise ReserveDepletedError(1)

@dataclass
class CPMM:
    pool: AMMPool

    def invariant(self) -> int:
        return self.pool.reserves[0] * self.pool.reserves[1]

    def swap_if(self, amt0: int, amt1: int):
        tmp0 = self.pool.reserves[0] + amt0
        tmp1 = self.pool.reserves[1] + amt1
        if tmp0 + tmp1 >= self.invariant(): # should never be <= 0
            self.pool.reserves[0] = tmp0
            self.pool.reserves[1] = tmp1
        else:
            raise SwapRejectedError(amt0, amt1)

    def market_order(self, amt: int, direction: str, token: int):
        amt = amt if direction == "BUY" else -amt
        self.market_order_buy(amt, token)

    def market_order_buy(self, amt: int, token: int):
        """Token must be either 0 or 1."""
        sell_amt = math.ceil(( self.invariant() / (self.pool.reserves[token] - amt) ) - \
                self.pool.reserves[(token+1)%2])
        if token == 0:
            amt0 = -amt
            amt1 = sell_amt
        else:
            amt0 = sell_amt
            amt1 = -amt
        self.pool.swap(amt0, amt1)

from collections import deque
from typing import Iterable

class OraclePool:
    """
    Subclass and wrap p() if you fancy it.
    """
    def __init__(self, pool: AMMPool, oracle: Iterable[dict]):
        """
        Feel free to pass pd.DataFrame.iterrows() in here.
        Columns should be "ts" (int) and "p" (float).
        """
        self.pool = pool
        self.oracle = deque(oracle)

    def p(self, ts):
        """
        Timestamp logic: if trades have the same timestamp as an oracle update,
        they were submitted before the block containing that update. 
        Thus they execute at that fresh price.
        """
        try:
            while ts > self.oracle[0]["ts"]: 
                # only step oracle forward if trade was strictly later
                self.oracle.popleft()
        except IndexError:
            raise ValueError("Ran out of oracle prices!")
        return self.oracle[0]["p"]

    def market_order_buy(self, amt: int, ts: int, token: int):
        if token == 0:
            amt0 = -amt
            amt1 = math.ceil( amt * self.p(ts) )
        else:
            amt1 = -amt
            amt0 = math.ceil( amt / self.p(ts) )
        self.pool.swap(amt0, amt1)
        return amt0, amt1
