import pickle

try:
    from InertialLoadingCalculator import inertial_loading_calculator
except ModuleNotFoundError:
    import sys
    from os import path

    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from InertialLoadingCalculator import inertial_loading_calculator


def ask_for_number(message):
    success = False
    while not success:
        try:
            success = True
            return float(input(message))
        except ValueError:
            success = False
            print("Please only fill in numbers")


# MAIN

print("\n\tWing Design Tool")
print("\t\t\tB05\n")

try:
    with open('./InertialLoadingCalculator/data.pickle', 'rb') as file:
        pass
    if input("Inertial Loading Data found. Do you want to update it? (Y/n): ").lower() == 'y':
        inertial_loading_calculator.calculate_inertial_loading(ask_for_number("Please fill in a step length (smaller is slower): "))
except FileNotFoundError:
    print("No Inertial Loading Data found. Generating it.")
    inertial_loading_calculator.calculate_inertial_loading(ask_for_number("Please fill in a step length (smaller is slower): "))

try:
    with open('./InertialLoadingCalculator/data.pickle', 'rb') as file:
        inertial_loading_data = pickle.load(file)
except FileNotFoundError:
    print("FATAL ERROR: Inertial Loading calculation failed, stopping")
    raise SystemExit

if input("Do you want to plot this data? (Y/n): ").lower() == 'y':
    inertial_loading_calculator.plot_inertial_loading(*inertial_loading_data[1::])

