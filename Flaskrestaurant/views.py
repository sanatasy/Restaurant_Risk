from flask import render_template
from flask import request
from flaskrestaur import app
import pandas as pd
import model 
import numpy as np
#import io
#import matplotlib.pyplot as plt 
#from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure
from flask import Flask, make_response
from bokeh.embed import components

#plt.switch_backend('agg')

#import data 
df = pd.read_pickle('restaurant_final_data_2519')


@app.route('/input')
def restaurants_input():
   return render_template("input.html", longitude=40.739, latitude=-73.9885, zoom=13)

@app.route('/output')

def restaurants_output(df=df):
 #query_results = df
 #pull 'street address' from input field and store it
 address = request.args.get('feature')
 the_result = model.run_model(address, df)
 #get diff from average 
 block_avg = model.get_block_avg(address, df)
 diff = round( the_result - block_avg, 2) 
 diff_direction = 'fewer' if diff<0 else 'more'
 #get plot 
 plot1 = model.make_plot1(address, df)
 plot2 = model.make_plot2(address, df)
 #Embed plot into HTML via Flask Render
 script1, div1 = components(plot1)
 script2, div2 = components(plot2)
 #get recommended locations 
 tab = model.rec_locations(address, df)
 locs = []
 for i in range(0, tab.shape[0]):
     locs.append(dict(block = tab.iloc[i]['census_block'], 
                     zips = tab.iloc[i]['Zip_Code'], 
                     borough = tab.iloc[i]['Borough'], 
                     years = tab.iloc[i]['block_duration']))



 return render_template("output.html", the_result = the_result, locs = locs, diff = diff, diff_direction = diff_direction, 
                       plot1=plot1, script1=script1, div1=div1, script2=script2, div2=div2)


