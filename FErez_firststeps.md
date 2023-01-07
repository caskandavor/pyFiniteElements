# Create the machine
This app is concerned with electric motor design. You need to start with **Winding layout**, in order to setup the pole-slot configuration. You can't yet change the number of phases (fixed to 3) so the number of slot is a multiple of 3. The number of rotor poles is a multiple of two, as they work in pairs (North and South poles). To go on, *save* the configuration, which will show you:
- the [star of slots](https://api.semanticscholar.org/CorpusID:109340999), colored by phase
- the winding layout as in [Emetor](https://www.emetor.com/windings/)
- the [winding factor](https://en.wikipedia.org/wiki/Winding_factor)
- the shape of the [MMF](https://en.wikipedia.org/wiki/Magnetomotive_force)
            
The next is to create the **Geometry**. You can choose between external or internal rotor, different types of slots and poles shapes, if you want to model the shaft, if you want to have a slotless, coreless or yokeless machine, and change the magnet magnetization. More geometries will be added in the future, so be patient. In this section, you must be very careful with the inputs, as a wrong geometry (intersecting lines) is not always caught, which makes the Triangle mesher crash, hence the entire app. In order to help you, a geometry debugger is provided right under the images. It's better to always use it when you are unsure (unless you already used these parameters and you know it's going to work). If you are looking for the units, they are in the **Configuration** section. Anyways, you must use the *Mesh* button to be able to go on, which will show you the meshed geometry. You can turn the rotor to ensure everything works fine.
            
At this phase, you can save your geometry using **File management**. In this section, you have 4 buttons given in this order:
- Refresh
- Save
- Load
- Delete
You need to input the *File name* anytime you wish to use a button, except *Refresh* that needs to be used anytime you open this section. The local path to where the geometry files (.txt) are placed is given, in case you want to back-up.


# Electromagnetics 
Now that the geometry is created, you can proceed to a **Single-step** computation, just to make sure that results are coherent. If not, try to increase the number of elements (first slider), the bounding-box size (second slider), or go back to **Configuration** and change the mesher options.
                
All the electromagnetics computations are achieved in magnetostatics, which means no transient effects are taken into account. When you see multiple steps being calculated, they are fully independent from each other. The most simple case if when [saturation](https://en.wikipedia.org/wiki/Saturation_(magnetic)) is not taken into account (= linear relation between B and H). The iron permeability is constant and it is then very quick to create the matrix system and solve it.

In the linear case, a single *stiffness* matrix **K** and the *source* vector Q are created. For the non-linear case, a Jacobian matrix **J** is also created, which takes into account the derivative of the reluctivity. The source vector is non-zero for coil and magnet elements (the electromagnetic sources). The stiffness matrix is an image of the geometric relationship between elements. For all computations except **FE losses**, there are no boundary conditions, which makes the construction and manipulation of matrices much faster, the drawback is that the flux lines are not bounded but to compute the torque it is

With these matrices, the [magnetic vector potential](https://en.wikipedia.org/wiki/Magnetic_vector_potential) noted A is computed. In the linear case, it is very straightforward and quick, as the matrix system to be solved is:

**K** x A = Q

It is solved using [LAPACK's DPOSV](https://netlib.org/lapack/explore-html/dc/de9/group__double_p_osolve_ga9ce56acceb70eb6484a768eaa841f70d.html)
For the non-linear case, the [Newton-Raphson method](https://en.wikipedia.org/wiki/Newton%27s_method) is used. It is an iterative approach and bear in mind that by nature it [can](https://en.wikipedia.org/wiki/Newton%27s_method#Failure_analysis) fail... You can change the convergence criterium in the **Configuration** section. The idea is to minimize a residual term R:

**J** x ΔA = R

**J** x ΔA = -(**K** x A - Q)

First, the right hand side needs to be computed using [LAPACK's DSPMV](https://netlib.org/lapack/explore-html/d7/d15/group__double__blas__level2_gab746575c4f7dd4eec72e8110d42cefe9.html). Then, using [LAPACK's DPOSV](https://netlib.org/lapack/explore-html/dc/de9/group__double_p_osolve_ga9ce56acceb70eb6484a768eaa841f70d.html) the equation can be solved for ΔA. In this way, at step m+1, we compute A@(m+1) = A@(m) + DeltaA@(m+1) (for the very first step, the linear system is solved to serve as an estimate).

Each time the potential vector is computed, the flux density B is calculated from it (B = ∇ ⨯ A). Note that the values of B (constant for each element made of 3 nodes) are less precise than the ones of A (at each node). You may thus increase the number of elements for better localized values. The default number of layers in the air-gap is 3 (no plan to change it for now) so it gives a dense mesh at its neighbourghood.

The torque computation is not the best, I use the simplest method which is the [Maxwell stress tensor](https://en.wikipedia.org/wiki/Maxwell_stress_tensor)



# External parties
The mesh is achived thanks to [Triangle by J. Shewchuk](https://www.cs.cmu.edu/~quake/triangle.html), wrapped in Swift by [W. Townsend](https://github.com/wtsnz/Triangle).

Electric motor and derivation of quantities with finite elements was realized with the help of many scientific papers and books, as well as [D. Meeker's FEMM](https://www.femm.info/wiki/HomePage) that can only be recommended to use, especially with its Python API.

For the windings, I am using [L. Alberti's Koil embedded in Dolomite](https://gitlab.com/LuigiAlberti/dolomites-python).

I got all the ressources for coding 2D magnetostatics from [N. Ida and J. Bastos, Electromagnetics and calculation of fields](https://link.springer.com/book/10.1007/978-1-4612-0661-3).
