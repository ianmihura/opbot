# https://github.com/hashABCD/opstrat/blob/main/opstrat/blackscholes.py
# https://github.com/yassinemaaroufi/MibianLib/blob/master/mibian/__init__.py
# https://www.quantconnect.com/tutorials/introduction-to-options/the-greek-letters
# https://medium.com/swlh/calculating-option-premiums-using-the-black-scholes-model-in-python-e9ed227afbee

import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
from math import log, sqrt, exp


def get_d1(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float) -> float:
    """d1 term for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return (log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))


def get_d2(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float) -> float:
    """d2 term for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return (log(s / k) + (r - sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))


def bsm_price(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float, 
    is_call: bool) -> float:
    """Black-Scholes Model - Fair price calculation
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    d1 = (log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if is_call:
        return exp(-r*T) * (s * exp((r)*T) * norm.cdf(d1) - k * norm.cdf(d2))
    else:
        return exp(-r*T) * (k * norm.cdf(-d2) - (s * exp((r)*T) * norm.cdf(-d1)))


def delta(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float, 
    is_call: bool) -> float:
    """Delta variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    if is_call:
        return norm.cdf((log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T)))
    else:
        return norm.cdf((log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))) - 1


def gamma(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float) -> float:
    """Gamma variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return norm.pdf((log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))) / (s * sigma * sqrt(T))


def vega(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float) -> float:
    """Vega variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    """
    return s * sqrt(T) * norm.pdf((log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))) / 100


def theta(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float, 
    is_call: bool) -> float:
    """Theta variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    d1 = (log(s / k) + (r + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))
    if is_call:
        return -s * norm.pdf(d1) * sigma / (2 * sqrt(T)) - r * k * exp(-r*T) * norm.cdf(d1 - sigma * sqrt(T)) / 365
    else:
        return -s * norm.pdf(d1) * sigma / (2 * sqrt(T)) + r * k * exp(-r * T) * norm.cdf(-(d1 - sigma * sqrt(T))) / 365


def rho(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float, 
    is_call: bool) -> float:
    """Rho variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    is_call: Contract is call (False is a put)
    """
    if is_call:
        return k * T * (exp(-r*T)) * norm.cdf((log(s / k) + (r - sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))) / 100
    else:
        return -k * T * (exp(-r*T)) * norm.cdf(-(log(s / k) + (r - sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))) / 100


def iv(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    p: float, 
    is_call: bool) -> float:
    """Implied volatility (Black-Scholes price) - bisection method
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    p: Contract price in the open market
    is_call: Contract is call (False is a put)
    """
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
            if abs(price - p) < 0.00001: break 
            if mid_vol > 500.0 - 5 :
                mid_vol = 0.0001
                break

        else: #TODO: put IV has 54% correlation with deribit iv
            upper_price = bsm_price(s, k, r, T, upper_vol, is_call)

            if (upper_price - p) * (price - p) > 0:
                upper_vol = mid_vol
            else:
                lower_vol = mid_vol
            if abs(price - p) < 0.00001: break 
            if iteration > 50: break
            if mid_vol < 0.0001:
                mid_vol = 0.0001
                break

    return mid_vol


def metrics(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    sigma: float, 
    p: float, 
    is_call: bool) -> dict:
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
        'delta': delta(s, k, r, T, sigma, is_call),
        'gamma': gamma(s, k, r, T, sigma),
        'vega': vega(s, k, r, T, sigma),
        'theta': theta(s, k, r, T, sigma, is_call),
        'rho': rho(s, k, r, T, sigma, is_call),
        # 'iv_rn': implied_volatility(s, k, r, T, p, is_call),
        'iv': iv(s, k, r, T, p, is_call),
        'value': bsm_price(s, k, r, T, sigma, is_call),
    }


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


def implied_volatility(
    s: float, 
    k: float, 
    r: float, 
    T: float, 
    p: float, 
    is_call: bool, 
    v_init: float = 1.0, 
    max_iter: int = 200, 
    tol: float = 0.0001) -> float:
    """Calculate IV of an Option
    s : Current Stock Price
    k : Strike Price
    r : Risk free rate %
    T : Time to expiration in days/365
    p : Market price of the contract
    is_call: True if is call, False if is put
        default: True
    v_init : Initial volatility to assume (best if near to real volatility)
    max_iter : Max amount of interations
    tol : Error tolerance
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
