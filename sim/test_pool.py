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

def test_cpmm_market_buy():
    P = AMMPool(1000000, 1000000)
    U = CPMM(P)
    assert U.invariant() == 1000000000000
    U.market_order(500000, "BUY", 0)
    assert U.invariant() >= 1000000000000
    assert P.reserves[0] == 500000
    assert P.reserves[1] >= 2000000

def test_oracle_pool():
    P = AMMPool(1000000, 1000000)
    oracle = [
        {"ts": 1000, "p": 1.1},
        {"ts": 1001, "p": 1.2},
        {"ts": 1002, "p": 1.5}
    ]
    O = OraclePool(P,oracle)
    
    O.market_order_buy(100000,999,0)
    assert O.pool.reserves[0] == 900000
    assert O.pool.reserves[1] >= 1110000 # may be unequal due to floating point error

    amt0, amt1 = O.market_order_buy(100000,1002,1)
    assert amt0 >= 100000 / 1.5

    with pytest.raises(ValueError):
        O.market_order_buy(1,1004,0)
