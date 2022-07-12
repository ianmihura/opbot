# https://github.com/hashABCD/opstrat/blob/main/opstrat/blackscholes.py
# https://github.com/yassinemaaroufi/MibianLib/blob/master/mibian/__init__.py
import numpy as np
import pandas as pd
from scipy.stats import norm
from datetime import datetime
from math import log, sqrt, exp


def get_d1(s, k, r, T, sigma, q=0):
    """d1 term for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    """
    return (log(s / k) + (r - q + sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))

def get_d2(s, k, r, T, sigma, q=0):
    """d2 term for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    """
    return (log(s / k) + (r - q - sigma ** 2 * 0.5) * T) / (sigma * sqrt(T))

def bsm_price(s, k, r, T, sigma, q=0, is_call=True):
    """Black-Scholes Model - Fair price calculation
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    is_call: Contract is call (False is a put)
    """
    sigma = sigma if sigma else sigma
    d1 = get_d1(s, k, r, T, sigma)
    d2 = d1 - sigma * sqrt(T)
    if is_call:
        return exp(-r*T) * (s * exp((r - q)*T) * norm.cdf(d1) - k * norm.cdf(d2))
    else:
        return exp(-r*T) * (k * norm.cdf(-d2) - (s * exp((r - q)*T) * norm.cdf(-d1)))

def delta(s, k, r, T, sigma, q=0, is_call=True):
    """Delta variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    is_call: Contract is call (False is a put)
    """
    if is_call:
        return exp(-q * T) * norm.cdf(get_d1(s, k, r, T, sigma))
    else:
        return exp(-q * T) * (norm.cdf(get_d1(s, k, r, T, sigma))-1)

def gamma(s, k, r, T, sigma, q=0):
    """Gamma variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    """
    return norm.pdf(get_d1(s, k, r, T, sigma)) * exp(-q * T) / (s * sigma * sqrt(T))

def vega(s, k, r, T, sigma, q=0):
    """Vega variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    """
    return s * sqrt(T) * norm.pdf(get_d1(s, k, r, T, sigma)) * exp(-q * T) / 100

def theta(s, k, r, T, sigma, q=0, is_call=True):
    """Theta variable for the Black-Scholes Model
    s: Underlying asset price
    k: Option strike
    r: Continuous risk-free rate
    T: Time to expiry in years (days / 365)
    sigma: Underlying volatility
    q: Dividend continuous rate
    is_call: Contract is call (False is a put)
    """
    d1 = get_d1(s, k, r, T, sigma)
    d2 = d1 - sigma * sqrt(T)
    if is_call:
        return -s * norm.pdf(d1) * sigma * exp(-q*T) / (2 * sqrt(T)) \
                    + q * s * norm.cdf(d1) * exp(-q*T) \
                    - r * k * exp(-r*T) * norm.cdf(d2) / 365
    else:
        return -s * norm.pdf(d1) * sigma * exp(-q * T) / (2 * sqrt(T)) \
                    - q * s * norm.cdf(-d1) * exp(-q * T) \
                    + r * k * exp(-r * T) * norm.cdf(-d2) / 365

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
        price = bsm_price(s, k, r, T, mid_vol)
        if is_call:
            lower_price = bsm_price(s, k, r, T, lower_vol)
            
            if (lower_price - p) * (price - p) > 0:
                lower_vol = mid_vol
            else:
                upper_vol = mid_vol
            if abs(price - p) < precision: break 
            if mid_vol > max_vol - 5 :
                mid_vol = 0.000001
                break

        else:
            upper_price = bsm_price(s, k, r, T, upper_vol)

            if (upper_price - p) * (price - p) > 0:
                upper_vol = mid_vol
            else:
                lower_vol = mid_vol
            if abs(price - p) < precision: break 
            if iteration > 50: break

    return mid_vol

def metrics(s, k, r, T, sigma, p, q=0, is_call=True):
    return {
        'delta': delta(s, k, r, T, sigma, q, is_call),
        'gamma': gamma(s, k, r, T, sigma, q),
        'vega': vega(s, k, r, T, sigma, q),
        'theta': theta(s, k, r, T, sigma, q, is_call),
        'rho': rho(s, k, r, T, sigma, is_call),
        'iv': iv(s, k, r, T, p, is_call),
    }


# https://medium.com/swlh/calculating-option-premiums-using-the-black-scholes-model-in-python-e9ed227afbee
# def metrics_2(K,S,sigma,r,T,is_call,Price):
#     T = T/365
    
#     if is_call:
#         return {
#             'delta': call_delta(S,K,T,r,sigma),
#             'gamma': call_gamma(S,K,T,r,sigma),
#             'theta': call_theta(S,K,T,r,sigma),
#             'vega': call_vega(S,K,T,r,sigma),
#             'rho': call_rho(S,K,T,r,sigma),
#             'iv': call_implied_volatility(Price,S,K,T,r)
#         }
#     else:
#         return {
#             'delta': put_delta(S,K,T,r,sigma),
#             'gamma': put_gamma(S,K,T,r,sigma),
#             'theta': put_theta(S,K,T,r,sigma),
#             'vega': put_vega(S,K,T,r,sigma),
#             'rho': put_rho(S,K,T,r,sigma),
#             'iv': put_implied_volatility(Price,S,K,T,r)
#         }
        

# def d1(S,K,T,r,sigma):
#     return(log(S/K)+(r+((sigma**2)/2.))*T)/(sigma*sqrt(T))

# def d2(S,K,T,r,sigma):
#     return d1(S,K,T,r,sigma)-sigma*sqrt(T)

# def bs_call(S,K,T,r,sigma):
#     return S*norm.cdf(d1(S,K,T,r,sigma))-K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma))

# def bs_put(S,K,T,r,sigma):
#     return K*exp(-r*T)-S*bs_call(S,K,T,r,sigma)

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

# def call_delta(S,K,T,r,sigma):
#     return norm.cdf(d1(S,K,T,r,sigma))
# def call_gamma(S,K,T,r,sigma):
#     return norm.pdf(d1(S,K,T,r,sigma))/(S*sigma*sqrt(T))
# def call_vega(S,K,T,r,sigma):
#     return 0.01*(S*norm.pdf(d1(S,K,T,r,sigma))*sqrt(T))
# def call_theta(S,K,T,r,sigma):
#     return 0.01*(-(S*norm.pdf(d1(S,K,T,r,sigma))*sigma)/(2*sqrt(T)) - r*K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma)))
# def call_rho(S,K,T,r,sigma):
#     return 0.01*(K*T*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma)))
    
# def put_delta(S,K,T,r,sigma):
#     return -norm.cdf(-d1(S,K,T,r,sigma))
# def put_gamma(S,K,T,r,sigma):
#     return norm.pdf(d1(S,K,T,r,sigma))/(S*sigma*sqrt(T))
# def put_vega(S,K,T,r,sigma):
#     return 0.01*(S*norm.pdf(d1(S,K,T,r,sigma))*sqrt(T))
# def put_theta(S,K,T,r,sigma):
#     return 0.01*(-(S*norm.pdf(d1(S,K,T,r,sigma))*sigma)/(2*sqrt(T)) + r*K*exp(-r*T)*norm.cdf(-d2(S,K,T,r,sigma)))
# def put_rho(S,K,T,r,sigma):
#     return 0.01*(-K*T*exp(-r*T)*norm.cdf(-d2(S,K,T,r,sigma)))


# def metrics(
#         K: float = 60, 
#         St: float = 62,
#         v: float = 0.32, 
#         r: float = 0.04, 
#         t: float = 40,
#         is_call: bool = True,
#         market_price: float = 1000,
#         c: str = '') -> dict:
#     """Calculates all Black Scholes information: IV, greeks & fair value
#     K : Strike Price
#     St: Current Stock Price (underlying)
#     v : Volatility % (sigma)
#     r : Risk free rate %
#     t : Time to expiration in days
#     is_call: True if is call, False if is put
#         default: True
#     market_price : Market price of the contract
#     """
#     #convert time in days to years
#     t=t/365
    
#     #1. CALCULATE OPTION BASE VALUES
#     val, d1, N_d1, N_d2 = black_scholes(K, St, v, r, t, is_call)

#     val_int = max(0,St-K) if is_call else max(0,K-St)
#     val_ext = val - val_int

#     #2. CALCULATE OPTION IV
#     # iv = call_implied_volatility(market_price, St, K, t, r)
#     # iv = implied_volatility(K, St, r, t, is_call, market_price)
#     iv = iv_2('c', market_price, St, K, r, t, 0)
    
#     #3. CALCULATE OPTION GREEKS
#     if is_call:
#         delta=N_d1
#         # theta=(-((St*v*np.exp(-np.power(d1,2)/2))/(np.sqrt(8*np.pi*t)))-(N_d2*r*K*np.exp(-r*t)))/365
#         theta=(-St*np.exp(-r*t)*norm.pdf(d1)*v/(2*t**0.5))/100
#         rho=t*K*N_d2*np.exp(-r*t)/100
#     else:
#         delta=-N_d1
#         theta=(-((St*v*np.exp(-np.power(d1,2)/2))/(np.sqrt(8*np.pi*t)))+(N_d2*r*K*np.exp(-r*t)))/365
#         rho=-t*K*N_d2*np.exp(-r*t)/100

#     # gamma=(np.exp(-np.power(d1,2)/2))/(St*v*np.sqrt(2*np.pi*t))
#     gamma=norm.pdf(d1)*np.exp(-r*t)/(St*v*t)

#     # vega=(St*np.sqrt(t)*np.exp(-np.power(d1,2)/2))/(np.sqrt(2*np.pi)*100)
#     vega=St*np.exp(-r*t)*norm.pdf(d1)*t**0.5/100
    
#     return {
#         'value': val, 
#         'value_int': val_int, 
#         'value_ext': val_ext, 
#         'delta': delta,
#         'gamma': gamma,
#         'theta': theta,
#         'vega': vega,
#         'rho': rho,
#         'iv': iv}


# def compute_volatility(underlying_action: pd.Series) -> pd.Series:
#     """Computes volatility for underlying data. The series passed should be
#     indexed by time, specifically by a timestamp represented either by an int
#     or a float.
#     """
#     output_data = underlying_action.copy().fillna(0)
#     output_data.index = list(map(lambda x: datetime.fromtimestamp(x), output_data.index))
#     log_returns = np.log(output_data/output_data.shift())
#     volatility = log_returns.rolling('30D').std() * (252 ** 1/2)
#     volatility.index = list(map(datetime.timestamp, volatility.index))
#     volatility = volatility[~volatility.index.duplicated(keep='first')]
#     return volatility


# def black_scholes(
#         K: float = 60,
#         St: float = 62,
#         v: float = 0.32,
#         r: float = 0.04,
#         t: float = 40,
#         is_call: bool = True):
#     """Calculates Black Scholes fair value 
#     K : Strike Price
#     St: Current Stock Price
#     v : Volatility % (sigma)
#     r : Risk free rate %
#     t : Time to expiration in days
#     is_call: True if is call, False if is put
#         default: True
    
#     returns:
#     val: Fair value
#     d1: d1 term
#     N_d1: Normalized d1 term
#     N_d2: Normalized d2 term
#     """
#     d1=(np.log(St/K)+(r+(np.power(v,2)/2))*t)/v*(np.sqrt(t))
#     d2=d1-(v*np.sqrt(t))

#     if is_call:
#         N_d1=norm.cdf(d1)
#         N_d2=norm.cdf(d2)
#     else:
#         N_d1=norm.cdf(-d1)
#         N_d2=norm.cdf(-d2)

#     A=(St*N_d1)
#     B=(K*N_d2*(np.exp(-r*t)))

#     val = A-B if is_call else B-A

#     # Returns values useful for greek calculations
#     return val, d1, N_d1, N_d2


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
#     """Calculate IV of an Option
#     K : Strike Price
#     St: Current Stock Price
#     r : Risk free rate %
#     t : Time to expiration in days/365
#     is_call: True if is call, False if is put
#         default: True
#     market_price : Market price of the contract
#     tol : Error tolerance
#     max_iter : Max amount of interations
#     v_init : Initial volatility to assume (best if near to real volatility)
#     """
#     # Assume initial aprox
#     v_old = v_init

#     for i in range(max_iter):
#         # Calculate Black Scholes fair price for v_old, sigma_n
#         bs_price, d1, _, _ = black_scholes(K, St, v_old, r, t, is_call)

#         # Volatility decay, c'(sigma_n)
#         # vega = (St*np.sqrt(t)*np.exp(-np.power(d1/100,2)/2))/(np.sqrt(2*np.pi)*100) * 100
#         vega = St * sqrt(t) * norm.pdf(d1)
        
#         # New implied volatility, sigma_n+1
#         v_new = v_old - (bs_price - market_price)/vega

#         if (abs(v_old - v_new) < tol or abs(bs_price - market_price) < tol):
#             break
    
#         v_old = v_new
    
#     return v_new
