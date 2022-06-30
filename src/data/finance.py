# https://github.com/hashABCD/opstrat/blob/main/opstrat/blackscholes.py
# https://github.com/yassinemaaroufi/MibianLib/blob/master/mibian/__init__.py
import numpy as np
from scipy.stats import norm


def metrics(
        K: float = 60, 
        St: float = 62,
        v: float = 0.32, 
        r: float = 0.04, 
        t: float = 40,
        type: str = 'c',
        market_price: float = 1000) -> dict:
    """Calculates all Black Scholes information: IV, greeks & fair value
    K : Strike Price
    St: Current Stock Price (underlying)
    v : Volatility % (sigma)
    r : Risk free rate %
    t : Time to expiration in days
    type: Type of option 'c' for call 'p' for put
        default: 'c'
    market_price : Market price of the contract
    """
    #Check time 
    try:
        #convert time in days to years
        t=t/365
    except:
        raise TypeError("Enter numerical value for time")
    
    #1. CALCULATE OPTION BASE VALUES
    val, d1, N_d1, N_d2 = black_scholes(K, St, v, r, t, type)

    val_int = max(0,St-K) if type == 'c' else max(0,K-St)
    val_ext = val - val_int

    #2. CALCULATE OPTION IV
    iv = implied_volatility(K, St, r, t, type, market_price)
    
    #3. CALCULATE OPTION GREEKS
    if type=='c':
        delta=N_d1
        theta=(-((St*v*np.exp(-np.power(d1,2)/2))/(np.sqrt(8*np.pi*t)))-(N_d2*r*K*np.exp(-r*t)))/365
        # theta=(-St*np.exp(-r*t)*norm.pdf(d1)*v/(2*t**0.5))/100
        rho=t*K*N_d2*np.exp(-r*t)/100
    else:
        delta=-N_d1
        theta=(-((St*v*np.exp(-np.power(d1,2)/2))/(np.sqrt(8*np.pi*t)))+(N_d2*r*K*np.exp(-r*t)))/365
        rho=-t*K*N_d2*np.exp(-r*t)/100

    # gamma=(np.exp(-np.power(d1,2)/2))/(St*v*np.sqrt(2*np.pi*t))
    gamma=norm.pdf(d1)*np.exp(-r*t)/(St*v*t)

    # vega=(St*np.sqrt(t)*np.exp(-np.power(d1,2)/2))/(np.sqrt(2*np.pi)*100)
    vega=St*np.exp(-r*t)*norm.pdf(d1)*t**0.5/100
    
    return {
        'val': val, 
        'val_int': val_int, 
        'val_ext': val_ext, 
        'd': delta,
        'g': gamma,
        't': theta,
        'v': vega,
        'r': rho,
        'iv': iv}


def black_scholes(
        K: float = 60,
        St: float = 62,
        v: float = 0.32,
        r: float = 0.04,
        t: float = 40,
        type: str = 'c'):
    """Calculates Black Scholes fair value 
    K : Strike Price
    St: Current Stock Price
    v : Volatility % (sigma)
    r : Risk free rate %
    t : Time to expiration in days
    type: Type of option 'c' for call 'p' for put
        default: 'c'
    
    returns:
    val: Fair value
    d1: d1 term
    N_d1: Normalized d1 term
    N_d2: Normalized d2 term
    """
    d1=(np.log(St/K)+(r+(np.power(v,2)/2))*t)/v*(np.sqrt(t))
    d2=d1-(v*np.sqrt(t))

    if type=='c':
        N_d1=norm.cdf(d1)
        N_d2=norm.cdf(d2)
    else:
        N_d1=norm.cdf(-d1)
        N_d2=norm.cdf(-d2)

    A=(St*N_d1)
    B=(K*N_d2*(np.exp(-r*t)))

    val = A-B if type=='c' else B-A

    # Returns values useful for greek calculations
    return val, d1, N_d1, N_d2


def implied_volatility(
        K: float = 60,
        St: float = 62,
        r: float = 0.04,
        t: float = 0.027,
        type: str = 'c',
        market_price: float = 1000,
        tol: float = 0.0001, 
        max_iter: int = 200, 
        v_init: float = 1.0):
    """Calculate IV of an Option
    K : Strike Price
    St: Current Stock Price
    r : Risk free rate %
    t : Time to expiration in days/365
    type: Type of option 'c' for call 'p' for put
        default: 'c'
    market_price : Market price of the contract
    tol : Error tolerance
    max_iter : Max amount of interations
    v_init : Initial volatility to assume (best if near to real volatility)
    """
    # Assume initial aprox
    v_old = v_init

    for i in range(max_iter):
        # Calculate Black Scholes fair price for v_old, sigma_n
        bs_price, d1, _, _ = black_scholes(K, St, v_old, r, t, type)

        # Volatility decay, c'(sigma_n)
        vega = (St*np.sqrt(t)*np.exp(-np.power(d1/100,2)/2))/(np.sqrt(2*np.pi)*100) * 100
        
        # New implied volatility, sigma_n+1
        v_new = v_old - (bs_price - market_price)/vega

        if (abs(v_old - v_new) < tol or abs(bs_price - market_price) < tol):
            break
    
        v_old = v_new
    
    return v_new


# Values are very different for those in Deribit web. Why is this?
# TODO: test this with real data, mean squared error
# market_price = 679.2
# K = 23000
# St = 20053
# v = 0.9112
# r = 0.04
# t = 29
# type = 'c'

# b = metrics(K, St, v, r, t, type, market_price)
# print(b)
