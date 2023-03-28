import numpy as np
rng = np.random.default_rng(seed=1345235)

DATA_START = 1609459200 # doesn't actually matter

def generate_uniform_zi_orders(length: int, max_size: int, rate: float, start_ts=DATA_START):
    """
    Generate uniformly random orders with Poisson arrivals.
    Return an iterator over (timestamp, order_amount) pairs where order_amount
    can be negative, indicating an order in the opposite direction.
    """
    intervals = rng.exponential(rate, length)
    arrivals = intervals.cumsum()
    orders = rng.uniform(low=-max_size, high=max_size, size=length)
    return zip(arrivals, orders)

def generate_exponential_zi_orders(length: int, mean_size: int, mean_interval: float, start_ts=DATA_START):
    """
    Generate rounded exponential random orders with Poisson arrivals.
    Return an iterator over (timestamp, order_amount) pairs where order_amount
    can be negative, indicating an order in the opposite direction.
    """
    intervals = rng.exponential(mean_interval, length)
    arrivals = intervals.cumsum()
    orders = np.round(rng.exponential(mean_size, size=length))
    signs = rng.choice([-1,1], size=length)
    return zip(arrivals, signs*orders)
