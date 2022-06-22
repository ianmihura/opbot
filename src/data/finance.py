# https://github.com/hashABCD/opstrat/blob/main/opstrat/blackscholes.py
import numpy as np
from scipy.stats import norm
import pdb


def black_scholes(
        K: float = 60, 
        St: float = 62,
        v: float = 0.32, 
        r: float = 0.04, 
        t: float = 40,
        type: str = 'c') -> dict:
    """Calculates all Black Scholes information: IV, greeks & fair value
    K : Strike Price
    St: Current Stock Price
    v : Volatility % (sigma)
    r : Risk free rate %
    t : Time to expiration in days
    type: Type of option 'c' for call 'p' for put
        default: 'c'
    """
    # default option: call
    try:
        type=type.lower()
        if (type != 'c' and type != 'p'):
            type = 'c'
    except:
        type = 'c'

    #Check time 
    try:
        #convert time in days to years
        t=t/365
    except:
        raise TypeError("Enter numerical value for time")

    #Check risk free rate 
    try:
        r=r+0
    except:
        raise TypeError("Enter numerical value for risk free rate")
    
    #Check volatility
    try:
        v=v+0
    except:
        raise TypeError("Enter numerical value for volatility")  

    #Check Stock Price
    try:
        St=St+0
    except:
        raise TypeError("Enter numerical value for stock price")
    
    #Check Exercise Price
    try:
        K=K+0
    except:
        raise TypeError("Enter numerical value for Exercise price")    
    
    #1. CALCULATE OPTION BASE VALUES
    # pdb.set_trace()
    val, d1, N_d1, N_d2 = bs(K, St, v, r, t, type)

    val_int = max(0,St-K) if type == 'c' else max(0,K-St)
    val_ext = val - val_int

    value = {'val':val, 'val_int':val_int, 'val_ext':val_ext}

    #2. CALCULATE OPTION IV
    #initial guess = 100
    #evaluate for that guess

    #3. CALCULATE OPTION GREEKS
    if type=='c':
        delta=N_d1
        theta=(-((St*v*np.exp(-np.power(d1,2)/2))/(np.sqrt(8*np.pi*t)))-(N_d2*r*K*np.exp(-r*t)))/365
        rho=t*K*N_d2*np.exp(-r*t)/100
    else:
        delta=-N_d1
        theta=(-((St*v*np.exp(-np.power(d1,2)/2))/(np.sqrt(8*np.pi*t)))+(N_d2*r*K*np.exp(-r*t)))/365
        rho=-t*K*N_d2*np.exp(-r*t)/100

    gamma=(np.exp(-np.power(d1,2)/2))/(St*v*np.sqrt(2*np.pi*t))
    vega=(St*np.sqrt(t)*np.exp(-np.power(d1,2)/2))/(np.sqrt(2*np.pi)*100)
    
    greeks={'delta':delta, 'gamma':gamma, 'theta':theta, 'vega':vega, 'rho':rho}

    return {'value':value, 'greeks':greeks}

def bs(
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
    val_int: Fair intrinsic value
    val_time: Fair time value
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


#TODO document and check values
def implied_volatility(K, St, r, t, market_price, type='c', tol=0.0001, max_iter=200, v_init=1):
    """Calculate IV of an Option
    """

    # Assume initial aprox
    v_old = v_init

    for i in range(max_iter):
        # Calculate Black Scholes fair price for v_old, sigma_n
        bs_price, d1, _, _ = bs(K, St, v_old, r, t/365, type)

        # Volatility decay, c'(sigma_n)
        vega = (St*np.sqrt(t/365)*np.exp(-np.power(d1/100,2)/2))/(np.sqrt(2*np.pi)*100) * 100
        
        # New implied volatility, sigma_n+1
        v_new = v_old - (bs_price - market_price)/vega

        if (abs(v_old - v_new) < tol or abs(bs_price - market_price) < tol):
            break
    
        v_old = v_new
    
    return v_new

# TODO: volatilities and greeks give veeeeery different values
market_price = 1018.2
St = 20210
K = 17000
t = 36
r = 0.04
v = 0.9835
type = 'p'

b = black_scholes(K, St, v, r, t, type)
iv = implied_volatility(K, St, r, t, market_price, type)

print(b, iv)
