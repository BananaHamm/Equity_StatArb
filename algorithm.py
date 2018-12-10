import pandas as pd
import numpy as np
import math
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression


# find return
def find_Return(price):
    ret = (price - price.shift(1))/price
    ret = ret.drop(ret.index[0])
    # fill the nan values with 0
    ret = ret.fillna(value = 0)
    return ret


# Using PCA to find factors we need. fac_num total number of factors, delay total number of days we use
def find_Factor(ret, delay, fac_num):
    # standardize the return
    mean = ret.mean(axis = 0)
    std = ret.std(axis = 0)
    std_ret = (ret - mean)/std
    
    #PCA process
    pca = PCA(n_components = fac_num)
    pca.fit(std_ret[0:delay])
    weight = pd.DataFrame(pca.components_)
    weight.columns = std.index
    weight = weight/std
    factor_ret = pd.DataFrame(np.dot(ret, weight.transpose()),index = ret.index)
    return factor_ret, weight


def find_Residue(ret,ret_factorret):
    #storing the residues
    res = pd.DataFrame(columns = ret.columns, index = ret.index)
    coef = pd.DataFrame(columns = ret.columns, index = range(15))
    ols = LinearRegression()
    for i in ret.columns:
        ols.fit(ret_factorret, ret[i])
        res[i] = ret[i]-ols.intercept_-np.dot(ret_factorret, ols.coef_)
        coef[i] = ols.coef_
    return res,coef

def find_Target_sscore(res, k):
    cum_res = res.cumsum()
    m = pd.Series(index = cum_res.columns)
    sigma_eq = pd.Series(index = cum_res.columns)
    for i in cum_res.columns:
        b = cum_res[i].autocorr()
        if -math.log(b) * 252 > k:
            temp = (cum_res[i]-cum_res[i].shift(1)* b)[1:]
            a = temp.mean()
            cosi =temp - a
            m[i] = a/(1-b)
            sigma_eq[i]=math.sqrt(cosi.var()/(1-b*b))
    m = m.dropna()
    m = m - m.mean()
    sigma_eq = sigma_eq.dropna()
    s_score = -m/sigma_eq
    return s_score
