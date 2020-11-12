#1) Numbers of parts:
# number of spars (3)
# number of top stringers
# number of bottom stringers

#4) Masses:
# stringer
# spar(s)
# top plate 
# bottom plate

#5) Wing properties: (from the sheet)
# wingspan 
# thickness to chord
# taper ratio
# root chord
# tip chord

#6) Thicknesses:
# thickness of top/bottom plates
# thickness of the spars

#----------------------------------------------




#---------------------------------------------
# GEOMETRY

#1) Position (from airfoil)
#horizontal stuff: 
# chord_lenght = interval from root (import) to tip (import) #will vary over the lenght, variable c ?

# Front spar position  F_SP_POS = 0.15*chord_lenght 
# Rear spar position   R_SP_POS = 0.6*chord_lenght 


# Front spar lenght (height)  F_SP_LEN = b = thickness with respect to chord  (b)
# Rear spar lenght (height)   R_SP_LEN = c = thickness with respect to chord   (c)
# Top plate lenght            T_PL_LEN = a =chord_lenght - T_SP_POS - (1-R_SP_POS)  (a) 
# Bottom plate lenght         B_PL_LEN = d = SQRT((T_PL_LEN)^2 + ( F_SP_LEN - R_SP_LEN)^2)  (d)

# if using angle alpha:
# Bottom plate lenght  B_PL_LEN = T_PL_LEN / cos(alpha)
# angle alpha 

#2) Thicknesses:
# thickness of top/bottom plates
# thickness of the spars


#---------------------------------------------


# CENTROID CALCULATIONS 

# Thin wall assumption !

# centroid of a trapezoid formula:
# x position = (a * (2 * c + b )) / (3(c + b)) (from c)
# y position = 


#calculated from wingbox geometry (centroid of trapezoid) and should be a centroid of a wing as well (flexural axis)

#  x - with respect to chord lenght
#  y - from centroid, with respect to span 
#  z - height from centroid

