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
        self.history = [{"ts": 0, "reserve0": reserve0, "reserve1": reserve1}]

    def swap(self, amt0: int, amt1: int, ts: int):
        """
        Swap amt0 of token0 for -amt1 of token1, if reserves permit.
        This function assumes that amt0 and amt1 have opposite sign.
        """
        tmp0 = self.reserves[0] + amt0
        tmp1 = self.reserves[1] + amt1
        if tmp0 >= 0 and tmp1 >= 0:
            self.history.append({"ts": ts, "reserve0": tmp0, "reserve1": tmp1})
            self.reserves[0] = tmp0
            self.reserves[1] = tmp1
            return amt0, amt1
        elif tmp0 < 0:
            raise ReserveDepletedError(0)
        elif tmp1 < 0:
            raise ReserveDepletedError(1)

class AMMPool:
    def __init__(self, reserve0, reserve1):
        self.reserves = [reserve0, reserve1]

    def swap(self, amt0: int, amt1: int, *args, **kwargs):
        """
        Swap amt0 of token0 for -amt1 of token1, if reserves permit.
        This function assumes that amt0 and amt1 have opposite sign.
        """
        tmp0 = self.reserves[0] + amt0
        tmp1 = self.reserves[1] + amt1
        if tmp0 >= 0 and tmp1 >= 0:
            self.reserves[0] = tmp0
            self.reserves[1] = tmp1
            return amt0, amt1
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

    def market_order(self, amt: int, direction: str, token: int, *args, **kwargs):
        amt = amt if direction == "BUY" else -amt
        return self.market_order_buy(amt, token, *args, **kwargs)

    def market_order_sell(self, amt: int, token: int, *args, **kwargs):
        """Token must be either 0 or 1."""
        return self.market_order_buy(-amt, token, *args, **kwargs)

    def market_order_buy(self, amt: int, token: int, *args, **kwargs):
        """Token must be either 0 or 1."""
        sell_amt = math.ceil(( self.invariant() / (self.pool.reserves[token] - amt) ) - \
                self.pool.reserves[(token+1)%2])
        if token == 0:
            amt0 = -amt
            amt1 = sell_amt
        else:
            amt0 = sell_amt
            amt1 = -amt
        return self.pool.swap(amt0, amt1, *args, **kwargs)

from collections import deque
from typing import Iterable

class OraclePool:
    """
    Subclass and wrap p() if you fancy it.
    token 1 is the numeraire.
    """
    def __init__(self, pool: AMMPool, oracle: Iterable[dict]):
        """
        Feel free to pass pd.DataFrame.iterrows() in here.
        Columns should be "ts" (int) and "p" (price; float).
        """
        self.pool = pool
        self.oracle = deque(oracle)

    def p(self, ts) -> float:
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

    def market_order_sell(self, amt: int, token: int, ts: int):
        return self.market_order_buy(-amt, token, ts) # this only works if spread is zero!

    def market_order_buy(self, amt: int, token: int, ts: int):
        if token == 0:
            amt0 = -amt
            amt1 = math.ceil( amt * self.p(ts) )
        else:
            amt1 = -amt
            amt0 = math.ceil( amt / self.p(ts) )
        self.pool.swap(amt0, amt1, ts)
        return amt0, amt1

class ConcLiquidityPool(OraclePool):
    """
    Concentrated liquidity with PL pricing curve.

    Initialise as follows:
      P = AMMPoolHistory(starting_reserve_0, starting_reserve_1)
      C = ConcLiquidityPool(P)

      trades = df[["trades_timestamp", "sell_amount", "sell_token_symbol"]]

    Replace the token symbols with 0 and 1:
      trades["sell_token"] = trades["sell_token_symbol"].replace("USDC", 0).replace("WETH", 1)

    Run sim:
      for trade in trades.iterrows():
          C.market_order_sell(trade["sell_amount"], trade["trades_timestamp"], trades["sell_token"])

    Retrieve inventory history for analysis:
      results = pd.DataFrame(C.pool.history)
    """
    def __init__(self, *args, tol=2, **kwargs):
        super().__init__(*args, **kwargs)
        self.tol = 2

    def balance(self, ts):
        return self.pool.reserves[0] / (self.p(ts) * self.pool.reserves[1])

    def market_order_sell(self, amt: int, token: int, ts: int) -> bool:
        p_ext = self.p(ts)
        logger.debug(f"Oracle price: {p_ext}")
        balance = self.pool.reserves[0] / (p_ext * self.pool.reserves[1])
        if token == 0:
            logger.debug("We're selling token 0.")
            new_x = self.pool.reserves[0] + amt
            new_y = self.pool.reserves[1] - amt * p_ext
            new_balance = new_x / (p_ext * new_y)
        else:
            logger.debug("We're selling token 1.")
            new_x = self.pool.reserves[0] - amt / p_ext
            new_y = self.pool.reserves[1] + amt
            new_balance = new_x / (p_ext * new_y)

        logger.debug(f"New x: {new_x}")
        logger.debug(f"New y: {new_y}")
        logger.debug(f"New balance would be {new_balance}.")

        # conditionals
        if new_balance > self.tol and token == 0: # reject
            return False
        elif new_balance < 1/self.tol and token == 1: # reject
            return False
        else: # new_bal in [1/self.tol, self.tol]
            if token == 0:
                self.pool.swap(amt, -amt/p_ext)
            else:
                self.pool.swap(-p_ext*amt, amt)
            return True


padding = 1.03

@dataclass
class AMMWithBaulking:
    """
    This class must be initiated with a price feed that includes all
    timestamps at which trades occur.
    """
    amm: CPMM # or whatever AMM class
    target_prices: dict[int, float] # or pd.Series

    def maybe_market_order_sell(self, amt, token, ts):
        amt0, amt1 = self.amm.market_order_sell(amt, token, ts)
        if token == 0 and - amt1 / max(amt0, 1) < self.target_prices[ts] / padding:
            self.amm.pool.swap(-amt0, -amt1, ts) # undo the swap
            return 0, 0
        elif token == 1 and - amt1 / max(amt0, 1) > self.target_prices[ts] * padding:
            self.amm.pool.swap(-amt0, -amt1, ts) # undo the swap
            return 0, 0
        return amt0, amt1
