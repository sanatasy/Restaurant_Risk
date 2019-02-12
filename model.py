# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 13:51:03 2019

@author: Sanata
"""

import pandas as pd 
import numpy as np 
from sklearn import preprocessing
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt 



#import dataset 
df = pd.read_pickle('restaurant_final_data_2519')

def address_exists(input_, df):
    input_ = input_.upper()
    if all(df.street_address!=input_):
        return False 
    else:
        return True 


def run_model(input_, df):
    input_ = input_.upper() 
    #remove chains 
    dat = df[df.is_chain==0]
    
    #get vars 
    Xvar = [#restaurant-level
              'on_avenue',
              #block-level restaurant features 
              'nrest_by_block', 
              'chains_by_block', 
              'block_duration',  'n_sales_250k', 
              'n_sales_500k', 'n_sales_1m', 
              #block-level location features 
               #'rent_by_block',
              #block-level census features 
              'mean_block_income',
              'total_block_pop', 'block_pop_dens', 
              'pct_white',  
              'pct_hisp', 'pct_black', 
              'pct_25_34', 
               
              'BRONX', 'BROOKLYN', 'STATEN ISLAND', 'QUEENS']
    
    y = ['n_years_open', 'open5']
    
    yvar = y[0]
    sub = dat[Xvar + [yvar]].dropna()
    #df_scaled = preprocessing.scale(df)
    mod_frame = sub[Xvar]
    y = sub[yvar]
    
    #split the data 
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(mod_frame, y, test_size=0.25, random_state=0)
    
    #fit model 
    from sklearn.linear_model import LinearRegression
    lr = LinearRegression().fit(X_train, y_train)
    
    #get y-hat 
    lookup = df.street_address==input_
    obs = pd.DataFrame( df.loc[lookup, Xvar].iloc[0]).T     
    y_pred = list( lr.predict(obs) )
    pred = round(y_pred[0], 1)
    
    return pred 

def get_block_avg(input_, df):
    input_ = input_.upper() 
    
    lookup = df.street_address==input_
    obs = pd.DataFrame( df.loc[lookup, :].iloc[0]).T 
    sub = df.drop_duplicates('Building_ID_No')
    avg = sub.loc[sub.Id.isin(obs.Id), 'block_duration'].mean()
    return avg 

    

def rec_locations(input_, df):
    input_ = input_.upper() 
    
    lookup = df.street_address==input_
    obs = pd.DataFrame( df.loc[lookup, :].iloc[0]).T 
    
    
    sub = df.drop_duplicates('Building_ID_No')
    #append obs to the end 
    sub = sub.append(obs)
    
    keep_vars = [ 'Id',
                #block census data 
                'block_pop_dens', 'med_block_income', 
                'pct_hisp', 'pct_white', 
                'pct_black', 'pct_asian', 
                'pct_under18', 'pct_18_24', 
                'pct_25_34', 'pct_35_44',
                'pct_45_59', 
                #restaurant block data 
                'nrest_by_block', 'n_sales_500k',
                'chains_by_block'
                ]
    
    locs = sub[keep_vars].dropna()
    
    #get the indexes of locations with the same census block id 
    idx = locs.Id.isin(obs.Id)
    
    #make matrix 
    keep_vars.remove('Id')
    l = sub[keep_vars].dropna() #unique locations 
    m = np.array(l)
    
      
    #scale
    m_scaled = preprocessing.scale(m)
    
   #calculate cosine similarity 
    test = cosine_similarity(m_scaled[l.shape[0]-1, :].reshape(1, -1), m_scaled[-idx, :]).transpose()
    test2 = pd.DataFrame(test, index = locs.Id[-idx], columns=['sim_score'])
    out = (test2
           .sort_values(by = 'sim_score', ascending=False)
           .reset_index()
           .drop_duplicates('sim_score')
           .drop_duplicates('Id')
           )
    #get block durations 
    out2 = out.join(df[['Id', 'block_duration', 'Zip_Code', 'Borough']], 
                    lsuffix='l', rsuffix='r')
    out2 = out2.rename(index=str, columns = {'Idl':'Id'})
    
    #get max duration 
    out3 = out2[(out2.Borough.isin(obs.Borough)) & (out2.block_duration >= obs.block_duration.iloc[0])].sort_values(by = [ 'sim_score', 'block_duration'], ascending=[False, False])
    out3['census_block'] = out3.Id.apply(lambda x: str(x)[-4:])
    out4 = out3[['census_block', 'Zip_Code', 'Borough' , 'block_duration']]
    out4.loc[:, 'block_duration'] = round(out4.block_duration, 1)
    out4.drop_duplicates('census_block', inplace=True)
    out4.drop_duplicates('block_duration', inplace=True)
    if out4.shape[0] < 3:
        return out4
    else: 
        return out4[:3]
    
#run_model('499 East 163 Street')
def plot_bars(input_, df):
    input_ = input_.upper() 
    lookup = (df.street_address == input_)
    obs = pd.DataFrame( df.loc[lookup, :].iloc[0]).T 
    
    sub = df[df.Borough.isin(obs.Borough)].drop_duplicates('Building_ID_No')
    success = sub[sub.open5==1]
    
    stats = ['nrest_by_block','chains_by_block', 'n_sales_1m', 'pct_white']
    
    m = obs[stats].apply('mean')
    s = success[stats].apply('mean')
    
    return m, s 


def make_plot(address, df):
     #plot comparison bars 
 m, s = plot_bars(address, df)
 # width of the bars
 barWidth = 0.3
 # Choose the height of the blue bars
 bars1 = m[:2] 
 # Choose the height of the cyan bars
 bars2 = s[:2]
 # The x position of bars
 r1 = np.arange(len(bars1))
 r2 = [x + barWidth for x in r1]
 
 #plot
 fig = plt.figure() 
 ax1 = fig.add_subplot(111)
 # Create blue bars
 ax1.bar(r1, bars1, width = barWidth, color = 'blue', edgecolor = 'black',  capsize=7, label='Your location')
 # Create cyan bars
 ax1.bar(r2, bars2, width = barWidth, color = 'cyan', edgecolor = 'black',  capsize=7, label='Successful locations')
 # general layout
 ax1.set_xticks([r + (barWidth-.1) for r in range(len(bars1))])
 ax1.set_xticklabels(['N restaurants by block','N chains by block'])
 ax1.legend(prop={'size':6})


 
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.transform import factor_cmap



def make_plot1(address, df):
    m, s = plot_bars(address, df)
    data = {'stats': ['N restaurants', 'N chains'],
         'm': m[:2].tolist(),
        's': s[:2].tolist()}
    stats = ['N restaurants', 'N chains']
    groups = ['My Loc', 'Success Locs']
    
    palette = ["#c9d9d3", "#718dbf", "#e84d60"]
    x = [ (stat, group) for stat in stats for group in groups]
    counts = sum(zip(data['m'], data['s']), ()) # like an hstack
    
    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), plot_height=350, title="Comparing Neighbors",
               toolbar_location=None, tools="")
    
    p.vbar(x='x', top='counts', width=0.5, source=source, line_color="white",
           fill_color=factor_cmap('x', palette=palette, factors=groups, start=1, end=2))#, 
           #legend=[value(x) for x in groups])
    
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = "horizontal"
    p.xgrid.grid_line_color = None
    
    return p 

def make_plot2(address, df):
    m, s = plot_bars(address, df)
    data = {'stats': ['Prop $1M Sales', 'Prop White'],
         'm': m[:2].tolist(),
        's': s[:2].tolist()}
    stats = ['Prop $1M Sales', 'Prop White']
    groups = ['My Location', 'Successful Locations']
    
    palette = ["#c9d9d3", "#718dbf", "#e84d60"]
    x = [ (stat, group) for stat in stats for group in groups]
    counts = sum(zip(data['m'], data['s']), ()) # like an hstack
    
    source = ColumnDataSource(data=dict(x=x, counts=counts))

    p = figure(x_range=FactorRange(*x), plot_height=350, title="Comparing Demographics",
               toolbar_location=None, tools="")
    
    p.vbar(x='x', top='counts', width=0.5, source=source, line_color="white",
           fill_color=factor_cmap('x', palette=palette, factors=groups, start=1, end=2))#, 
           #legend=[value(x) for x in groups])
    
    p.y_range.start = 0
    p.x_range.range_padding = 0.1
    p.xaxis.major_label_orientation = 'horizontal'
    p.xgrid.grid_line_color = None

    
    return p 


    
    

 