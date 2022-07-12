# https://github.com/hashABCD/opstrat/blob/main/opstrat/blackscholes.py
# https://github.com/yassinemaaroufi/MibianLib/blob/master/mibian/__init__.py
# https://www.quantconnect.com/tutorials/introduction-to-options/the-greek-letters
# https://medium.com/swlh/calculating-option-premiums-using-the-black-scholes-model-in-python-e9ed227afbee
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
from math import log, sqrt, exp


def get_d1(s, k, r, T, sigma):
    """d1 term for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return (log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))


def get_d2(s, k, r, T, sigma):
    """d2 term for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return (log(s / k) + (r - sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))


def bsm_price(s, k, r, T, sigma, is_call=True):
    """Black-Scholes Model - Fair price calculation
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    sigma = sigma if sigma else sigma
    d1 = get_d1(s, k, r, T, sigma)
    d2 = d1 - sigma * sqrt(T)
    if is_call:
        return exp(-r*T) * (s * exp((r)*T) * norm.cdf(d1) - k * norm.cdf(d2))
    else:
        return exp(-r*T) * (k * norm.cdf(-d2) - (s * exp((r)*T) * norm.cdf(-d1)))


def delta(s, k, r, T, sigma,is_call=True):
    """Delta variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    if is_call:
        return norm.cdf(get_d1(s, k, r, T, sigma))
    else:
        return norm.cdf(get_d1(s, k, r, T, sigma)) - 1


def gamma(s, k, r, T, sigma):
    """Gamma variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return norm.pdf(get_d1(s, k, r, T, sigma)) / (s * sigma * sqrt(T))


def vega(s, k, r, T, sigma):
    """Vega variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return s * sqrt(T) * norm.pdf(get_d1(s, k, r, T, sigma)) / 100


def theta(s, k, r, T, sigma, is_call=True):
    """Theta variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    d1 = get_d1(s, k, r, T, sigma)
    d2 = d1 - sigma * sqrt(T)
    if is_call:
        return -s * norm.pdf(d1) * sigma / (2 * sqrt(T)) - r * k * exp(-r*T) * norm.cdf(d2) / 365
    else:
        return -s * norm.pdf(d1) * sigma / (2 * sqrt(T)) + r * k * exp(-r * T) * norm.cdf(-d2) / 365


def rho(s, k, r, T, sigma, is_call=True):
    """Rho variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    if is_call:
        return k * T * (exp(-r*T)) * norm.cdf(get_d2(s, k, r, T, sigma)) / 100
    else:
        return -k * T * (exp(-r*T)) * norm.cdf(-get_d2(s, k, r, T, sigma)) / 100


def iv(s, k, r, T, p, is_call=True):
    """Implied volatility (Black-Scholes price) - bisection method
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    p: Contract price in the open market
    is_call: Contract is call (False is a put)
    """
    precision = 0.00001
    max_vol = 500.0
    min_vol = 0.0001
    iteration = 0

    upper_vol = 500.0
    lower_vol = 0.0001

    while 1:
        iteration +=1
        mid_vol = (upper_vol + lower_vol)/2.0
        price = bsm_price(s, k, r, T, mid_vol, is_call)
        if is_call:
            lower_price = bsm_price(s, k, r, T, lower_vol, is_call)
            
            if (lower_price - p) * (price - p) > 0:
                lower_vol = mid_vol
            else:
                upper_vol = mid_vol
            if abs(price - p) < precision: break 
            if mid_vol > max_vol - 5 :
                mid_vol = min_vol
                break

        else: #TODO: put IV has 54% correlation with actual iv. call IV has 88%
            upper_price = bsm_price(s, k, r, T, upper_vol, is_call)

            if (upper_price - p) * (price - p) > 0:
                upper_vol = mid_vol
            else:
                lower_vol = mid_vol
            if abs(price - p) < precision: break 
            if iteration > 50: break
            if mid_vol < min_vol:
                mid_vol = min_vol
                break

    return mid_vol


def metrics(s, k, r, T, sigma, p, is_call=True):
    """Implied volatility (Black-Scholes price) - bisection method
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    p: Contract price in the open market
    is_call: Contract is call (False is a put)
    """
    return {
        # 'delta': delta(s, k, r, T, sigma, is_call),
        # 'gamma': gamma(s, k, r, T, sigma),
        # 'vega': vega(s, k, r, T, sigma),
        # 'theta': theta(s, k, r, T, sigma, is_call),
        # 'rho': rho(s, k, r, T, sigma, is_call),
        # 'iv_rn': implied_volatility(s, k, r, T, p, is_call),
        'iv_bi': iv(s, k, r, T, p, is_call),
        # 'value': bsm_price(s, k, r, T, sigma, is_call),
    }


# # TODO: make this into dx/dy, Newton's approach
# def call_implied_volatility(Price, S, K, T, r):
#     sigma = 0.5
#     while sigma < 2:
#         Price_implied = S * \
#             norm.cdf(d1(S, K, T, r, sigma))-K*exp(-r*T) * \
#             norm.cdf(d2(S, K, T, r, sigma))
#         # print(sigma)
#         # print(Price,Price_implied)
#         if Price-Price_implied < 0.001:
#             return sigma
#         sigma += 0.01
#     return 1

# def put_implied_volatility(Price, S, K, T, r):
#     sigma = 0.001
#     while sigma < 1:
#         Price_implied = K*exp(-r*T)-S+bs_call(S, K, T, r, sigma)
#         if Price-(Price_implied) < 0.001:
#             return sigma
#         sigma += 0.001
#     return 1


def volatility(underlying: pd.Series) -> pd.Series:
    """Computes volatility for underlying data. The series passed should be
    indexed by time, specifically by a timestamp represented either by an int
    or a float.
    """
    output_data = underlying.copy().fillna(0)
    output_data.index = list(map(lambda x: datetime.fromtimestamp(x), output_data.index))
    log_returns = np.log(output_data/output_data.shift())
    volatility = log_returns.rolling('30D').std() * (252 ** 1/2)
    volatility.index = list(map(datetime.timestamp, volatility.index))
    volatility = volatility[~volatility.index.duplicated(keep='first')]
    return volatility


# def implied_volatility(
#         K: float = 60,
#         St: float = 62,
#         r: float = 0.04,
#         t: float = 0.027,
#         is_call: bool = True,
#         market_price: float = 1000,
#         tol: float = 0.0001, 
#         max_iter: int = 200, 
#         v_init: float = 1.0):
def implied_volatility(s, k, r, T, p, is_call, v_init=1.0, max_iter: int = 200, tol: float = 0.0001):
    """Calculate IV of an Option
    K : Strike Price
    St: Current Stock Price
    r : Risk free rate %
    t : Time to expiration in days/365
    is_call: True if is call, False if is put
        default: True
    market_price : Market price of the contract
    tol : Error tolerance
    max_iter : Max amount of interations
    v_init : Initial volatility to assume (best if near to real volatility)
    """
    # Assume initial aprox
    v_old = v_init

    for i in range(max_iter):
        # Calculate Black Scholes fair price for v_old, sigma_n
        bs_price = bsm_price(s, k, r, T, v_old, is_call)

        # Volatility decay, c'(sigma_n)
        _vega = vega(s, k, r, T, v_old) * 100

        if not bool(vega):
            return v_old
        
        # New implied volatility, sigma_n+1
        v_new = v_old - (bs_price - p) / _vega

        if (abs(v_old - v_new) < tol or abs(bs_price - p) < tol):
            break
    
        v_old = v_new
    
    return v_new
