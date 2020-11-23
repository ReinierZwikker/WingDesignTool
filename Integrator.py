import numpy as np


def trapz_area(prev_value, current_value, length_step):
    return prev_value + 0.5 * (current_value - prev_value) * length_step


class Integration:

    def __init__(self, function, LUT_rounding):
        self.LUT = {}
        self.__function = function
        self.__LUT_rounding = LUT_rounding

    def integrate(self, start, stop, length_step, *args):
        integral_value = 0
        for location in np.arange(start, stop, length_step):
            if round(location, self.__LUT_rounding) in self.LUT:
                integral_value += self.LUT[round(location, self.__LUT_rounding)]
            else:
                # print("Cannot find value in LUT!")
                prev_value = self.__function(location - length_step, length_step, *args)
                current_value = self.__function(location, length_step, *args)
                value = trapz_area(prev_value, current_value, length_step)
                integral_value += value
                self.LUT[round(location, self.__LUT_rounding)] = value
        return integral_value

    def get_value(self, location, *args):
        if round(location, self.__LUT_rounding) in self.LUT:
            return self.LUT[round(location, self.__LUT_rounding)]
        else:
            # print("integrating for other function")
            return self.integrate(location, *args)
