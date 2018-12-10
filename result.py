import algorithm as al
import math

def find_Sharpe_Ratio(pnl,r):
    mean = math.log(pnl.iloc[len(pnl.index)-1]/pnl.iloc[0])/(len(pnl.index)) * 252.0
    print mean
    ret = al.find_Return(pnl)
    std = ret.std() * math.sqrt(252)
    return (mean - r)/std

def find_Maximum_Drawdown(pnl):
    ret = al.find_Return(pnl)
    r = ret.add(1).cumprod()
    dd = r.div(r.cummax()).sub(1)
    mdd = dd.min()
    end = dd.argmin()
    start = r.loc[:end].argmax()
    return mdd

def find_Cumulative_Return(pnl):
    return (pnl.iloc[len(pnl.index)-1] - pnl.iloc[0]) / pnl.iloc[0]


