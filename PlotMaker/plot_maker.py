import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import Importer.xflr5 as aerodynamic_data
import numpy as np

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot(aerodynamic_data.chord_function.x, np.zeros(aerodynamic_data.chord_function.x.shape))
ax.plot(aerodynamic_data.chord_function.x, np.zeros(aerodynamic_data.chord_function.x.shape), aerodynamic_data.lift_coef_function_10.y,
        label='lift coef 10')
ax.plot(aerodynamic_data.chord_function.x, np.zeros(aerodynamic_data.chord_function.x.shape), aerodynamic_data.lift_coef_function_0.y,
        label='lift coef 0')
ax.plot(aerodynamic_data.chord_function.x, aerodynamic_data.drag_induced_function_0.y, np.zeros(aerodynamic_data.chord_function.x.shape),
        label='drag induced 0')
ax.plot(aerodynamic_data.chord_function.x, aerodynamic_data.drag_induced_function_10.y, np.zeros(aerodynamic_data.chord_function.x.shape),
        label='drag induced 10')
plt.legend()
plt.show()
