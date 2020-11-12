import numpy as np
import scipy as sp
from scipy import interpolate


"""
Output of this function is a numpy array, where [1] is the second data point etc. In that data point:
[0] is the y-span, [1] is the chord, [2] the induced angle of attack, [3] the Cl, [5] the induced Cd, [7] is Cm around c/4
"""
def main_wing_xflr5(name):
    main_wing = np.genfromtxt(name, skip_header=40, skip_footer=1029, usecols=(0,1,2,3,5,7))
    return main_wing

def rolling_moment_coef_xlfr5(name):
    f = open(name, 'r')
    lines = f.readlines()
    rolling_moment_coef = float(lines[12].split()[2])
    f.close()
    return rolling_moment_coef

data = main_wing_xflr5('MainWing_a0.00_v10.00ms.txt')
rolling_moment_coef = rolling_moment_coef_xlfr5('MainWing_a0.00_v10.00ms.txt')

"""
Y-span varies from 0 to 
"""
chord = sp.interpolate.interp1d(data[:,0], data[:,1], kind='cubic', fill_value="extrapolate")
angle_induced = sp.interpolate.interp1d(data[:,0], data[:,2], kind='cubic', fill_value="extrapolate")
lift_coef = sp.interpolate.interp1d(data[:,0], data[:,3], kind='cubic', fill_value="extrapolate")
drag_induced = sp.interpolate.interp1d(data[:,0], data[:,4], kind='cubic', fill_value="extrapolate")
moment_coef = sp.interpolate.interp1d(data[:,0], data[:,5], kind='cubic', fill_value="extrapolate")