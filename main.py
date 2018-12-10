import os
import datacleaning as dc
import algorithm as al
import result as rs
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    
    '''
    ############################################################################################
    This part declares the value of the variables we use in the project
    ############################################################################################
    
    '''
    files = ('SP400','SP500')
    delay = 252
    window = 60
    factor = 15
    k = 8.4
    sbo = 2
    sso = 2
    sbc = 0.75
    ssc = 0.5
    r = 0.00
    tran_cost = 0.0005
    leverage = 1
    start_val = 100
    name_pnl = 'pnl'
    
    '''
    ############################################################################################
    This part do the basic data cleaning
    ############################################################################################
        
    '''
    # make a directory to store the original data
    if not os.path.exists('pickle'):
        os.makedirs('pickle')
        print "pickle directory made"
    # make a directory to store the intermediate data
    if not os.path.exists('process_result'):
        os.makedirs('process_result')
        print "process_result directory made"
    # cleaning the original data and put the data into three files price volumn and dps
    if not os.path.isfile('pickle/price_original.pkl'):
        data = dc.data_Cleaning(files)
        price_original = data[0]
        dps_original = data[2]
        ret_original = find_Return(price_original)
        ret_original.to_pickle('pickle/ret_original.pkl')
        print "price_original.pkl created"
        print "dps_original.pkl created"
        print "ret_original.pkl created"
    else:
        price_original = pd.read_pickle('pickle/price_original.pkl')
        dps_original = pd.read_pickle('pickle/dps_original.pkl')
        ret_original = pd.read_pickle('pickle/ret_original.pkl')


    '''
    ############################################################################################
    This part finds the PCA factors we need
    ############################################################################################
    
    '''
    # erase the stock with nan at beginning
    if not os.path.isfile('process_result/price_factor.pkl'):
        price_factor = dc.erase_Nan(price_original,30)
        price_factor.to_pickle('process_result/price_factor.pkl')
        print "price_factor.pkl created"
    else:
        price_factor = pd.read_pickle('process_result/price_factor.pkl')
    # find the returns for the remaining stocks
    if not os.path.isfile('process_result/ret_factor.pkl'):
        ret_factor = al.find_Return(price_factor)
        ret_factor.to_pickle('process_result/ret_factor.pkl')
        print "ret_factor.pkl created"
    else:
        ret_factor = pd.read_pickle('process_result/ret_factor.pkl')
    # find the returns of the maximum 15 factors
    if not os.path.isfile('process_result/ret_factorret.pkl'):
        ret_factorret, weight = al.find_Factor(ret_factor, delay, factor)
        ret_factorret.to_pickle('process_result/ret_factorret.pkl')
        print "ret_factorret.pkl created"
    else:
        ret_factorret = pd.read_pickle('process_result/ret_factorret.pkl')





    '''
    ############################################################################################
    This part implement the back testing trading algo
    ############################################################################################
    
    '''
    if not os.path.isfile('pickle/' + name_pnl + '.pkl'):
        pnl = pd.Series(start_val, index = price_original.index[delay-1:])
        position_stock = pd.DataFrame(0,columns = price_original.columns, index = ['stock']+range(15))
        position_stock_before = pd.Series(0, index = price_original.columns)
        for t in range(delay-1,len(price_original.index)-1):
            #find the window price of all stocks
            price_t = price_original[(t-window):(t+1)]
            # eliminate the nan
            price_t = dc.erase_Nan(price_t,0)
            #find the return of this period
            ret_t = al.find_Return(price_t)
            # find the residual of this period
            ret_factorret_t = ret_factorret[(t-window+1):(t+1)]
            res_t, coef_t = al.find_Residue(ret_t,ret_factorret_t)
            # find the s-score of the target stocks of this period
            target = al.find_Target_sscore(res_t, k)
            # find the strategy for this time period:
            for i in position_stock.columns:
                if not i in target.index :
                    if position_stock[i]['stock'] != 0:
                        position_stock[i] = 0
                else:
                    if position_stock[i]['stock'] == 0:
                        if target[i] < -sbo:
                            position_stock[i]['stock'] = leverage
                            position_stock[i][1:] = -leverage * coef_t[i]
                        elif target[i] > sso:
                            position_stock[i]['stock'] = - leverageß
                            position_stock[i][1:] = leverage * coef_t[i]
                    elif position_stock[i][0] >0 and target[i] > -ssc:
                        position_stock[i] = 0
                    elif position_stock[i][0] <0 and target[i] < sbc:
                        position_stock[i] = 0
            # calculate the pnl for the next period
            dps_t = dps_original.iloc[t+1]
            pri_t = price_original.iloc[t+1]
            temp = (dps_t/pri_t).fillna(0)
            position_stock_temp = pd.Series(0,index = price_original.columns)
            fac_sum = position_stock.sum(axis = 1)[1:]
            for i in weight.columns:
                position_stock_temp = sum(weight[i] * fac_sum)
            position_stock_temp = position_stock_temp + position_stock.iloc[0]
            change = sum(abs(position_stock_temp - position_stock_before))
            position_stock_before = position_stock_temp
            pnl.iloc[t-delay + 2] = pnl.iloc[t-delay + 1] * ( 1 + r /252.0) + np.dot(position_stock.loc['stock'], ret_original.iloc[t]+temp) + np.dot(position_stock.sum(axis = 1)[1:], ret_factorret.iloc[t]) - position_stock.sum().sum() * r /252.0 - change * tran_cost
            print pnl.iloc[t-delay + 2]
        pnl.to_pickle('pickle/'+name_pnl+'.pkl')
        print name_pnl+'.pkl created'
    else:
        pnl = pd.read_pickle('pickle/' + name_pnl + '.pkl')
    
    
    
        
    '''
    ############################################################################################
    This part gave us the result
    ############################################################################################
    
    '''
    
    sharpe_ratio = rs.find_Sharpe_Ratio(pnl,r)
    maximum_drawdowns = rs.find_Maximum_Drawdown(pnl)
    cumulative_return = rs.find_Cumulative_Return(pnl)

if __name__ == "__main__":
    main()