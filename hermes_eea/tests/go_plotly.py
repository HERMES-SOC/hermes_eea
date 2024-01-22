import os
import sys
import numpy as np
import math

os.environ['CDF_LIB'] = '/Users/rstrub/Work-FPI/cdf37_0-dist/src/lib'

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from spacepy import pycdf

def read_data(file):
  try:
    cdffile = cdf = pycdf.CDF(file)
    len = len(py[EpochStr][:])
    print("file len:",len)
  except Exception:
    if not os.path.exists(file):
        print(file + " does not exist")
        return None
  return cdffile

def diff(a,b):
   if abs(a+b) != 0:
       return abs((a-b)/((a+b)/2.0))
   else:
       return 0

def tolerance(y1,y2):

    tolerance = abs(y1.max() - y2.max())
    tolerance = .01 # 1 percent
    tolerance = .0004 # 1 percent
    tolerance = 0

    yy1 = []
    yy2 = []
    x3 = []
  
    for i in range(0,len(y1)):
       if diff(y1[i],y2[i]) >= tolerance:
         print(y1[i],y2[i],diff(y1[i],y2[i]))
         yy1.append(y1[i])
         yy2.append(y2[i])
         x3.append(i)


    return [np.array(yy1),np.array(yy2),np.array(x3)]



def prepare_data(var,far=1600):
    

    y1     =  mycdf[var][0:far]
    y2     =  newcdf[var][0:far] # len(y1.shape) == 1

    return [y1,y2]

def draw_plot(y1,y2,x_axis,variable):

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=x_axis,
                   y=y1,
                   mode="markers+lines",
                   marker=dict(
                      color="red",
                      size=12),
                   name="golden"),
        secondary_y=True,
    )
    
    fig.add_trace(
        go.Scatter(x=x_axis,
                   y=y2,
                   mode="markers+lines",
                   marker=dict(
                      color="orange",
                      size=12),
                   name="newfile"),
        secondary_y=True,
    )

    #fig.add_trace( go.Scatter(x=orgx, y=orgpy, mode="markers", marker=dict( color="blue", size=6), name="py org data"), secondary_y=True,)
    #fig.add_trace( go.Scatter(x=orgx, y=orgidl, mode="markers", marker=dict( color="black", size=6), name="idl org data"), secondary_y=True,)
    
    # Add figure title
    fig.update_layout(
        title_text=variable
    )
    
    # Set x-axis title
    fig.update_xaxes(title_text="n")
    
    # Set y-axes titles
    fig.update_yaxes(title_text="<b>primary</b> yaxis title", secondary_y=True)
    fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)
    
    fig.show()



golden = "hermes_eea/tests/hermes_eea_l1_20000101T170901_v1.0.0.cdf"
artifact = "/Users/rstrub/Downloads/processed-files/hermes_eea_l1_20000101T170901_v1.0.0.cdf"

mycdf = read_data(golden)
newcdf = read_data(artifact)
mylist = [item[0] for item in list(mycdf.items())]
for item in mylist:
    print(item,len(mycdf[item[:]]),mycdf[item].shape)

variables = mylist

# graph stats:
var = 1
variable = variables[var]
x_axis_length = mycdf[variables[var]].shape[0]
orgx = np.arange(0,x_axis_length,1)

[y1,y2] = prepare_data(variable,  x_axis_length)
[tol_y1,tol_y2,remaining_x] = tolerance(y1,y2)

draw_plot(y1,y2,remaining_x,variable)

