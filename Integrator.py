import numpy as np


def trapz_area(prev_value, current_value, length_step):
    return (prev_value + 0.5 * (current_value - prev_value)) * length_step


class Integration:

    def __init__(self, function, start_point, end_point, flip_sign=False, verbose=False):
        self.LUT = {}
        self.__function = function
        self.__start_point = start_point
        self.__end_point = end_point
        self.__flip_sign = flip_sign
        self.__LUT_rounding = 10
        self.__verbose = verbose

    def integrate(self, location, length_step, *args):
        if self.__verbose:
            print("\nnew integral\n")
        integral_value = 0
        for location_i in np.arange(location + (length_step / 2), self.__end_point + length_step, length_step):
            if round(location_i, self.__LUT_rounding) in self.LUT:
                integral_value += self.LUT[round(location_i, self.__LUT_rounding)]
                if self.__verbose:
                    print(f"retrieved {location_i:.10f} {self.LUT[round(location_i, self.__LUT_rounding)]:.1f}\ttotal {integral_value:.1f}")
            else:
                # print("Cannot find value in LUT!")
                prev_value = self.__function(location_i - (length_step / 2), *args)
                next_value = self.__function(location_i + (length_step / 2), *args)
                value = trapz_area(prev_value, next_value, length_step)
                integral_value += value
                if self.__verbose:
                    print(f"prev {location_i - (length_step / 2):.10f} {prev_value:.1f}\tcurr {location_i + (length_step / 2):.10f} {next_value:.1f}\tvalue {value:.1f}\ttotal {integral_value:.1f}")
                self.LUT[round(location_i, self.__LUT_rounding)] = value
        if self.__flip_sign:
            return -integral_value
        else:
            return integral_value

    def get_value(self, location, *args):
        if round(location, self.__LUT_rounding) in self.LUT:
            return self.LUT[round(location, self.__LUT_rounding)]
        else:
            return self.integrate(location, *args)
