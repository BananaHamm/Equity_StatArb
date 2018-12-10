import pandas as pd
import math


# Clean the original data to three xlsx, price, volumn and dps
def data_Cleaning(files):
    # Combining the files together and delete the NaN columns
    data = pd.read_excel('data/'+files[0]+'.xlsx')
    data.to_pickle('pickle/' + files[0] + '.pkl')
    data = data.dropna(axis = 1, how = 'all')
    if len(files) >1 :
        for file in files[1:]:
            #print file
            data_t = pd.read_excel('data/'+file+'.xlsx')
            data_t.to_pickle('pickle/' + file + '.pkl')
            data_t = data_t.dropna(axis = 1, how = 'all')
            data = pd.concat([data,data_t],axis = 1)

    # rename the columns start from zero
    data.columns = range(len(data.columns))
    
    # Align the rows with respect of time
    data_alin = data[range(4)]
    data_align.index = data[0]
    data_align = data_align.drop(labels = 0, axis = 1)
    data_align = data_align.dropna(how = 'all')
    
    '''
        Optimization : use multi-thread to speed up the merging process
    '''
    
    for i in range(1,len(data.columns)/4):
        data_temp = data[range(i * 4, i * 4 + 4)]
        data_temp.index = data[i * 4]
        data_temp = data_temp.drop(labels = 4 * i, axis = 1)
        data_temp = data_temp.dropna(how = 'all')
        data_align = pd.concat([data_align,data_temp],axis = 1)
        #print i
    data_align = data_align.drop('Date')
    p = range(1,len(data.columns),4)
    v = range(2,len(data.columns),4)
    d = range(3,len(data.columns),4)
    price_original = data_align[p]
    price_original.columns = range(904)
    volumn_original = data_align[v]
    volumn_original.columns = range(904)
    dps_original = data_align[d]
    dps_original.columns = range(904)
    price_original.to_excel('data/price.xlsx')
    volumn_original.to_excel('data/volumn.xlsx')
    dps_original.to_excel('data/dps.xlsx')
    price_original.to_pickle('pickle/price_original.pkl')
    volumn_original.to_pickle('pickle/volumn_orignal.pkl')
    dps_original.to_pickle('pickle/dps_original.pkl')

    return price_original,volumn_original,dps_original


# eliminate the nan
def erase_Nan(price,nan_num):
    price_nan = price.dropna(axis = 1,thresh = len(price)-nan_num)
    return price_nan


