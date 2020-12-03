#normal stress stringers due to bending
def string_stress_normal(x, y, b):
    M_y =
    M_x =
    I_yy =
    I_xx =
    I_xy =
    #b = #span location
    # x = #max distance to centroid
    # y = #max distance to centroid
    sigma = ((((M_x*I_yy)-(M_y*I_xy))*y)+(((M_y*I_xx)-(M_x*I_xy))*x))/((I_xx*I_yy)-(I_xy)**2)
    return sigma

def margin_of_safety(applied_stress):
    failure_stress = 310000000 #failurestress al6061-t6 in Pa(N/m**2)
    mos = failure_stress/applied_stress
    return mos