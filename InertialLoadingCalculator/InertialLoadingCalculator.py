### ------ Workpackage 4.1: Inertial loading calculations ------ ###
import scipy

#Import basic geometry
from database import wingspan as b
from database import fuselagediamter as d_fus

r_fus = d_fus/2

#Import lift distribution function
from filename import liftfunctionname as L

#Import weight and location of the engine

from database import weightengine as W_eng
from database import ylocationengine as y_eng

#Calculate/Import the weight of the wing (use fraction from class II)

from database import weightwing as W_wing

#Calculate final lift distribution
L_final = L - W_wing

#Calculate the moment function from the tip to the engine (excluding engine)
#Moment @ tip equals zero

M1 = scipy.integrate.quad(L_final,y_eng,b/2)

#Calculate the moment function from the engine (including) to the fuselage
#Moment @ engine equals the max moment minus the weight of the engine

M2 = scipy.integrate.quad(L_final,r_fus,y_eng)

hi!

