import pytest
from pool import *

def test_swap():
    P = AMMPool(1000000, 1000000)
    P.swap(-500000, 300000)
    assert P.reserves[0] == 500000
    P.swap(-500000, 100000)
    assert P.reserves[0] == 0
    x = P.reserves[1]
    with pytest.raises(ReserveDepletedError) as e:
        P.swap(-500000, 1000000)
        assert e.args[0] == 0
    assert P.reserves[0] == 0 and P.reserves[1] == x

def test_swap_history():
    P = AMMPoolHistory(1000000, 1000000)
    P.swap(-500000, 300000, 1234)
    assert P.reserves[0] == 500000
    P.swap(-500000, 100000, 1356)
    assert P.reserves[0] == 0
    x = P.reserves[1]

    assert len(P.history) == 3
    with pytest.raises(ReserveDepletedError) as e:
        P.swap(-500000, 1000000, 1665)
        assert e.args[0] == 0
    assert P.reserves[0] == 0 and P.reserves[1] == x

    import pandas as pd
    df = pd.DataFrame(P.history)

def test_cpmm_market_buy():
    P = AMMPool(1000000, 1000000)
    U = CPMM(P)
    assert U.invariant() == 1000000000000
    U.market_order(500000, "BUY", 0)
    assert U.invariant() >= 1000000000000
    assert P.reserves[0] == 500000
    assert P.reserves[1] >= 2000000

def test_oracle_pool():
    P = AMMPoolHistory(1000000, 1000000)
    oracle = [
        {"ts": 1000, "p": 1.1},
        {"ts": 1001, "p": 1.2},
        {"ts": 1002, "p": 1.5}
    ]
    O = OraclePool(P,oracle)
    
    O.market_order_buy(100000,0,999)
    assert O.pool.reserves[0] == 900000
    assert O.pool.reserves[1] >= 1110000 # may be unequal due to floating point error

    amt0, amt1 = O.market_order_buy(100000,1,1002)
    assert amt0 >= 100000 / 1.5
    amt0, amt1 = O.market_order_buy(100000,1,1002)
    amt0, amt1 = O.market_order_buy(100000,1,1002)

    with pytest.raises(ValueError):
        O.market_order_buy(1,0,1004)

def test_conc_liq_pool():
    P = AMMPool(1000000, 1000000)
    oracle = [
        {"ts": 1000, "p": 1.1},
        {"ts": 1001, "p": 1.5},
        {"ts": 1002, "p": 2}
    ]
    C = ConcLiquidityPool(P,oracle)

    assert C.market_order_sell(100000, 1, 1000) # (890000, 1100000)
    assert not C.market_order_sell(100000, 1, 1001) # would be (740000, 1200000); reject
    assert C.market_order_sell(100000, 0, 1002) # (990000, 1050000)
    assert not C.market_order_sell(10, 1, 1002) # unbalanced, reject trade

def test_baulking():
    P = AMMPoolHistory(1000000, 1000000)
    oracle = [
        {"ts": 1000, "p": 1.1},
        {"ts": 1001, "p": 1.2},
        {"ts": 1002, "p": 1.5}
    ]
    oracle2 = [
        {"ts": 1000, "p": 1.1},
        {"ts": 1001, "p": 1.2},
        {"ts": 1002, "p": 1.3}
    ]
    O = OraclePool(P,oracle)
    T = AMMWithBaulking(O, {entry["ts"]: entry["p"] for entry in oracle2})

    x,y = T.maybe_market_order_sell(1000, 0, 1001)
    assert x==1000 and y==-1200
    r0, r1 = P.reserves

    x,y = T.maybe_market_order_sell(1000, 1, 1002)
    assert x==0 and y==0
    assert P.reserves[0] == r0 and P.reserves[1] == r1
