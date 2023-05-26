
try:
    from ulab import numpy as np
except:
    import numpy as np


dist=0
min_idx=0
def brackets(value,array):
    #decide how to handle values outside the map
    dist = array-value
    min_idx = np.argmin(abs(dist))
    if dist[min_idx]<0:
        return (min_idx,min_idx+1)
    else:
        return (min_idx-1,min_idx)

x_idx=0
y_idx=0
x_vals=0
y_vals=0
Q11=0
Q12=0
Q21=0
Q22=0
r1=0
r2=0

def interp2d(coords,table):
    # print(coords)
    x_idx = brackets(coords[0],table['x_bins'])
    xmax = len(table['x_bins'])-1
    # print(x_idx)
    if x_idx[0]<0:
        x_idx = (0,x_idx[1])
    if x_idx[1]>xmax:
        x_idx = (x_idx[0],xmax) 
    # print(x_idx)
        
    y_idx = brackets(coords[1],table['y_bins'])
    ymax = len(table['y_bins'])-1
    # print(y_idx)
    if y_idx[0]<0:
        y_idx = (0,y_idx[1])
    if y_idx[1]>ymax:
        y_idx = (y_idx[0],ymax) 
    # print(y_idx)

    x_vals = [table['x_bins'][x_idx[0]], table['x_bins'][x_idx[1]]]
    y_vals = [table['y_bins'][y_idx[0]], table['y_bins'][y_idx[1]]]
    # print(x_vals)
    # print(y_vals)
    Q11=table['array'][x_idx[0],y_idx[0]]
    Q12=table['array'][x_idx[0],y_idx[1]]
    Q21=table['array'][x_idx[1],y_idx[0]]
    Q22=table['array'][x_idx[1],y_idx[1]]
    if x_vals[0] == x_vals[1]:
        r1 = Q21
        r2 = Q21
    else:
        r1=(coords[0]-x_vals[0])*(Q21-Q11)/(x_vals[1]-x_vals[0])+Q11
        r2=(coords[0]-x_vals[0])*(Q22-Q12)/(x_vals[1]-x_vals[0])+Q12
        
    if y_vals[0]==y_vals[1]:
        ret =  r2
    else:
        ret = (coords[1]-y_vals[0])*(r2-r1)/(y_vals[1]-y_vals[0])+r1
    # print(ret)
    return ret

