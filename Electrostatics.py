import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from scipy.sparse import csc_matrix
import scipy.sparse.linalg

"""
Translation to Python3 of the FORTRAN77 example code of: Nathan Ida, Jao Bastos, 1992-1997
(ref: Electromagnetics and calculation of fields
      https://doi.org/10.1007/978-1-4684-0526-2)

by: Guillaume Verez, 2022
"""

########################################################
# User inputs
########################################################

n_elem_x = 20                         # number of elements in the x direction  
n_elem_y = 20                         # number of elements in the y direction  
permittivity_list = [1, 10]          # relative permittivities of the outside and the material of the square
imposed_potentials_values = [100, 0] # imposed potential at Y = max and Y = 0

########################################################
# Initialization
########################################################

element_mat = []
X = []
Y = []

for i in range(n_elem_y + 1):
    for j in range(n_elem_x + 1):
        if i != n_elem_y and j != n_elem_x:
            element_mat.append([i*(n_elem_x+1)+j, (i+1)*(n_elem_x+1)+1+j, i*(n_elem_x+1)+1+j])
            element_mat.append([i*(n_elem_x+1)+j, (i+1)*(n_elem_x+1)+j, (i+1)*(n_elem_x+1)+1+j])
        X.append(10/n_elem_x*j)
        Y.append(10-10/n_elem_y*i)

number_elements = len(element_mat)
number_nodes = (n_elem_y+1)*(n_elem_x+1)

imposed_potentials_nodes = np.zeros((len(imposed_potentials_values), n_elem_x+1), dtype = int)

for i in range(n_elem_x + 1):
    imposed_potentials_nodes[0][i] = i
    imposed_potentials_nodes[1][i] = number_nodes-1-i

########################################################
# Create the total "stiffness" matrix for triangular (3 nodes) elements
########################################################

patches = []
color_material = []
globalS = np.zeros((number_nodes, number_nodes))

for i in range(number_elements):
    localS = np.zeros((3, 3))
    current_element_node = [element_mat[i][0], element_mat[i][1], element_mat[i][2]]
    x1 = X[current_element_node[0]]
    y1 = Y[current_element_node[0]]
    x2 = X[current_element_node[1]]
    y2 = Y[current_element_node[1]]
    x3 = X[current_element_node[2]]
    y3 = Y[current_element_node[2]]

    # create visually the element
    polygon = Polygon(np.array([[x1, y1], [x2, y2], [x3, y3]]), False)
    patches.append(polygon)

    # create the material color and assign the element material
    if ((x3 <= 8 and x1 >= 4) and (y1 <= 8 and y2 >= 4)):
        permittivity = permittivity_list[1]
        color_material.append(1.)
    else:
        permittivity = permittivity_list[0]
        color_material.append(0.)

    q1 = y2 - y3
    q2 = y3 - y1
    q3 = y1 - y2
    r1 = x3 - x2
    r2 = x1 - x3
    r3 = x2 - x1
    determinant = x2*y3 + x1*y2 + x3*y1 - x1*y3 - x3*y2 - x2*y1
    localS[0][0] = q1*q1 + r1*r1
    localS[0][1] = q1*q2 + r1*r2
    localS[0][2] = q1*q3 + r1*r3
    localS[1][0] = localS[0][1]
    localS[1][1] = q2*q2 + r2*r2
    localS[1][2] = q2*q3 + r2*r3
    localS[2][0] = localS[0][2]
    localS[2][1] = localS[1][2]
    localS[2][2] = q3*q3 + r3*r3
    localS *= permittivity/(2*determinant)
    # Assemble the localS(3,3) into the global matrix globalS(number_nodes, number_nodes)
    for k in range(3):
        for j in range(3):
            globalS[current_element_node[k]][current_element_node[j]] = globalS[current_element_node[k]][current_element_node[j]] + localS[k][j]

########################################################
# Insert the boundary conditions
########################################################

source_vect = np.zeros(number_nodes)

for i in range(np.size(imposed_potentials_values)): # for all values of imposed potentials in the list
    for j in range(n_elem_x+1): # all the nodes that are on the line where the potential is imposed
        for k in range(number_nodes):
            globalS[imposed_potentials_nodes[i][j]][k] = 0 # zero the coefficients in the corresponding line of globalS
        globalS[imposed_potentials_nodes[i][j]][imposed_potentials_nodes[i][j]] = 1 # then set the diagonal term to 1
        source_vect[imposed_potentials_nodes[i][j]] = imposed_potentials_values[i] # place the imposed potential on the right hand side

########################################################
# Solve the matrix system 
########################################################

potential_vec = scipy.sparse.linalg.spsolve(csc_matrix(globalS), source_vect)

########################################################
# Print the results
########################################################

def electric_field_intensity(element_number):
    # E = - grad(V)
    current_element_node = [element_mat[element_number][0], element_mat[element_number][1], element_mat[element_number][2]]
    x1 = X[current_element_node[0]]
    y1 = Y[current_element_node[0]]
    x2 = X[current_element_node[1]]
    y2 = Y[current_element_node[1]]
    x3 = X[current_element_node[2]]
    y3 = Y[current_element_node[2]]
    q1 = y2 - y3
    q2 = y3 - y1
    q3 = y1 - y2
    r1 = x3 - x2
    r2 = x1 - x3
    r3 = x2 - x1
    potential = [potential_vec[current_element_node[0]], potential_vec[current_element_node[1]], potential_vec[current_element_node[2]]]
    determinant = x2*y3 + x1*y2 + x3*y1 - x1*y3 - x3*y2 - x2*y1
    EX = -(q1*potential[0] + q2*potential[1] + q3*potential[2])/determinant
    EY = -(r1*potential[0] + r2*potential[1] + r3*potential[2])/determinant  
    return EX, EY

EMOD_vec = []

for i in range(number_elements):
    EX, EY = electric_field_intensity(i)
    EMOD = np.sqrt(EX**2 + EY**2)
    EMOD_vec.append(EMOD)

fig, axs = plt.subplots(1, 2, figsize=(20, 10))

p = PatchCollection(patches, alpha=1, edgecolor = 'white') # instead of 'cyan'
colors = np.array(color_material)
p.set_array(colors)
axs[0].add_collection(p)
clb = fig.colorbar(p, ax = axs[0], fraction=0.05)
axs[0].set_xlim([0, 10])
axs[0].set_ylim([0, 10])
axs[0].axis('off')
axs[0].set_aspect(1.)
clb.ax.set_title('Material type', fontsize = 12)

p = PatchCollection(patches, alpha=1, edgecolor = 'face')
colors = np.array(EMOD_vec)
p.set_array(colors)
axs[1].add_collection(p)
clb = fig.colorbar(p, ax = axs[1], fraction=0.05)
axs[1].set_xlim([0, 10])
axs[1].set_ylim([0, 10])
axs[1].axis('off')
axs[1].set_aspect(1.)
clb.ax.set_title('Field intensity', fontsize = 12)

axs[1].tricontour(X, Y, potential_vec, levels = 5)
