import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
try:
    import Importer.xflr5 as aerodynamic_data
except ModuleNotFoundError:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    import Importer.xflr5 as aerodynamic_data
import numpy as np

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(aerodynamic_data.chord_function.x, np.zeros(aerodynamic_data.chord_function.x.shape))
ax.plot(aerodynamic_data.chord_function.x, np.zeros(aerodynamic_data.chord_function.x.shape), aerodynamic_data.lift_coef_function_10.spanwise_location,
        label='lift coef 10')
ax.plot(aerodynamic_data.chord_function.x, np.zeros(aerodynamic_data.chord_function.x.shape), aerodynamic_data.lift_coef_function_0.spanwise_location,
        label='lift coef 0')
ax.plot(aerodynamic_data.chord_function.x, aerodynamic_data.drag_induced_function_0.spanwise_location, np.zeros(aerodynamic_data.chord_function.x.shape),
        label='drag induced 0')
ax.plot(aerodynamic_data.chord_function.x, aerodynamic_data.drag_induced_function_10.spanwise_location, np.zeros(aerodynamic_data.chord_function.x.shape),
        label='drag induced 10')
plt.legend()
plt.show()
