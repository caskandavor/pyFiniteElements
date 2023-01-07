# Create the machine
This app is concerned with electric motor design. You need to start with **Winding layout**, in order to setup the pole-slot configuration. You can't yet change the number of phases (fixed to 3) so the number of slot is a multiple of 3. The number of rotor poles is a multiple of two, as they work in pairs (North and South poles). To go on, *save* the configuration, which will show you:
- the [star of slots](https://api.semanticscholar.org/CorpusID:109340999), coloured by phase
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

All the electromagnetic computations are achieved in magnetostatic, which means no transient effects are taken into account. When you see multiple steps being calculated, they are fully independent from each other. The most simple case if when [saturation](https://en.wikipedia.org/wiki/Saturation_(magnetic)) is not taken into account (= linear relation between B and H). The iron permeability is constant and it is then very quick to create the matrix system and solve it.

In the linear case, a single *stiffness* matrix **K** and the *source* vector Q are created. For the non-linear case, a Jacobian matrix **J** is also created, which takes into account the derivative of the reluctivity. The source vector is non-zero for coil and magnet elements (the electromagnetic sources). The stiffness matrix is an image of the geometric relationship between elements. For all computations except **FE losses**, there are no boundary conditions, which makes the construction and manipulation of matrices much faster, the drawback is that the flux lines are not bounded but to compute the torque it is

With these matrices, the [magnetic vector potential](https://en.wikipedia.org/wiki/Magnetic_vector_potential) noted A is computed. In the linear case, it is very straightforward and quick, as the matrix system to be solved is:

**K** x A = Q

It is solved using [LAPACK's DPOSV](https://netlib.org/lapack/explore-html/dc/de9/group__double_p_osolve_ga9ce56acceb70eb6484a768eaa841f70d.html)
For the non-linear case, the [Newton-Raphson method](https://en.wikipedia.org/wiki/Newton%27s_method) is used. It is an iterative approach and bear in mind that by nature it [can](https://en.wikipedia.org/wiki/Newton%27s_method#Failure_analysis) fail... You can change the convergence criterium in the **Configuration** section. The idea is to minimise a residual term R:

**J** x ΔA = R

**J** x ΔA = -(**K** x A - Q)

First, the right hand side needs to be computed using [LAPACK's DSPMV](https://netlib.org/lapack/explore-html/d7/d15/group__double__blas__level2_gab746575c4f7dd4eec72e8110d42cefe9.html). Then, using [LAPACK's DPOSV](https://netlib.org/lapack/explore-html/dc/de9/group__double_p_osolve_ga9ce56acceb70eb6484a768eaa841f70d.html) the equation can be solved for ΔA. In this way, at step m+1, we compute A@(m+1) = A@(m) + DeltaA@(m+1) (for the very first step, the linear system is solved to serve as an estimate).

Each time the potential vector is computed, the [flux density](https://en.wikipedia.org/wiki/Magnetic_field) B is calculated from it (B = ∇ ⨯ A). Note that the values of B (constant for each element made of 3 nodes) are less precise than the ones of A (at each node). You may thus increase the number of elements for better localised values. The default number of layers in the air-gap is 3 (no plan to change it for now) so it gives a dense mesh at its neighbourhood.

The [torque computation](https://en.wikipedia.org/wiki/Torque) is not the most precise. I use the simplest method which is the [Maxwell stress tensor](https://en.wikipedia.org/wiki/Maxwell_stress_tensor) which basically solves the integral of:

Brad x Btan x r³

The [flux-linkage](https://en.wikipedia.org/wiki/Flux_linkage) is computed from the double integration of the potential vector in a phase.  A is expressed in  Wb/m and Wb = Henry x Ampere. The double integral is in Henry.Ampere.m² and we need to divide by the coil area to get the flux linkage in Wb = Henry.Ampere, and thus the inductance in Henry can be found with the ampere-turns. To do so, I perform the integration in a very simple manner: I calculate the volume under the 2D surface of each element. The volume, related to the plane A=0, is what is under the values of A (z direction) of each corner of a triangular element. The equation of the volume of such a triangle is simply the average of A (z) for the three nodes, multiplied by the area (xy).

The [back-EMF](https://en.wikipedia.org/wiki/Counter-electromotive_force) is computed from the derivative of the flux linkage multiplied by the rotational speed.

# Noise and vibrations
[Natural frequencies](https://en.wikipedia.org/wiki/Natural_frequency) of the stator can be computed, with or without a frame, and with or without the windings (meshed or not, their mass accounted or not). Frequencies of a concentric rings can also be computed in another section. In the **Configuration** section, the number of frequencies to plot as well as the number of frames and the scale factor for their visualisation can be changed. The **Materials** section allow to change the [mass density](https://en.wikipedia.org/wiki/Density), [Young's modulus](https://en.wikipedia.org/wiki/Young%27s_modulus) and [Poisson's ratio](https://en.wikipedia.org/wiki/Poisson%27s_ratio).

Two matrices are computed, the mass **M** and the stiffness **K**. In these computations, *plane stress* elements are used, and NOT plane strain. The system to be solved is called an [eigenvalue problem](https://en.wikipedia.org/wiki/Eigenvalues_and_eigenvectors) for undamped vibrations:

K x X = ω² x M x X

Where ω are natural frequencies and X is the eigenvector which allows to show the deformation corresponding to each frequency. The system is solved using [LAPACK's DSPGVX](https://netlib.org/lapack/explore-html/dc/dd2/group__double_o_t_h_e_reigen_ga059beb16ce5345c3a2dfbf9692650401.html)

The **Noise sources** section is a way to find analytically the source of noise in synchronous machines, as in the book of [Gieras, Wang and Lai](https://www.taylorfrancis.com/books/mono/10.1201/9781420027730/noise-polyphase-electric-motors-jacek-gieras-joseph-cho-lai-chong-wang). For clarity and also because you might not have all parameters, it is decomposed in separate parts: magnetics, PWM, mechanical, rolling bearings, plain bearings and aeraulic.

# Motor post-processing
The **FE losses** section computes losses according to a method given in [D. Meeker's FEMM](https://www.femm.info/wiki/SPMLoss). The flux versus time predicted by the finite element model will not be sinusoidal, because it will be including all effects of the motor's geometry as the rotor moves past the stator. If the stator steel were described by linear material properties, the losses could be rigorously decomposed into elements occurring at different frequencies which are summed to obtain the total loss. Even though the material properties are not linear, a widely used approximate method of estimating core losses is to assume that the losses can still be decomposed into multiple components occurring at multiple time harmonics.

As a result, we need to run an analysis through an entire spin of the rotor and record element centroid flux density and vector potential (using the mesh from the first iteration) at every step. This information will then be used to estimate core losses.

It is mandatory to use a boundary condition for the potential vector. If not set, the potential vector can completely vary from one value to another depending on the mesh, even if in one computation everything looks normal, it is just that it has no reference value. So, to keep consistant values of A during multiple steps, it is necessary to use a boundary condition. Interestingly enough, it does not seem necessary for the computation of inductance, and also for computing the flux density, that both use the potential vector in their own way. For this computation, I observe strange results if the number of layers of air elements at inner and outer boundaries is not high enough (apparently at least 3). So play with the second slider to have enough elements.

In the **Winding fill** section, two approximate [filling methods](https://en.wikipedia.org/wiki/Coil_winding_technology) for placing coil turns into the slot are shown. You can specify the diameter of the wire and insulation percentage, from real gauge types:
- [American Wire Gauge](https://en.wikipedia.org/wiki/American_wire_gauge)
- [IEC 60228](https://en.wikipedia.org/wiki/IEC_60228)
- [Standard Wire Gauge](https://en.wikipedia.org/wiki/Standard_wire_gauge)

The **Global values** section is an analytical way of finding global quantities such as resistance and motor constants equivalents for a coil, a phase or terminal values. They depend on the number of coils in series and the number of parallel circuits per phase. Two main parameters need to be given. First, what is called R01coil is the geometrical resistance (independent on the number of turns) of 1 coil. It is clear for tooth winding where the coil is basically a torus around a teeth. It is automatically calculated for a given geometry and for distributed winding an equivalent is also calculated. Alternatively a specific value can be given. Then, the γ1phase expressed in N.m/At is a constant given by a **Multi-step** magnetostatic analysis run with ampere-turns imposed on a single phase. The maximum value will be given in the results of this computation and can then be used in the **Global values** section.

The **Mapping** section is also an analytical computation, starting from same parameters than **Global values** and more advanced ones to compute the losses for different speeds. Indeed, mapping refers to maps of efficiency. Other maps are also shown: mechanical power, motor losses, copper losses, stator iron losses, voltage, currents and current density. Some input parameters can be left blank if unknown.

# Heat transfer
**Steady-state** heat transfer computation is achieved by assigning different levels of losses in the stator core, the coils, the rotor core and in the magnets. When comparing the local heat generation of each element with an averaged value per region, there are no difference as in the end, the temperatures become homogeneous. So, to easen the computation, only the losses per region are computed, so that the mesh between electromagnetic and thermal parts can be different (adding a frame with cooling, a different shaft etc.).

The heat transfer coefficient can be automatically calculated or given as an input.

Computed temperatures can be high but remember it is a steady-state computation, what the machine could reach if run non-stop for a "long" time. In practice, a machine can be run with a duty cycle or other modes of operations which will alleviate the thermal stress. As a result, this type of computation is best used for comparison between designs.

A stiffness matrix **K** is calculated, along with a force vector F. The stiffness matrix takes into account the conduction while both **K** and F take into account convection. The matrix equation to be solved is:

**K** x T = F

The temperature vector T is computed using [LAPACK's DPOSV](https://netlib.org/lapack/explore-html/dc/de9/group__double_p_osolve_ga9ce56acceb70eb6484a768eaa841f70d.html).



# External parties
The mesh is achieved thanks to [Triangle by J. Shewchuk](https://www.cs.cmu.edu/~quake/triangle.html), wrapped in Swift by [W. Townsend](https://github.com/wtsnz/Triangle).

Electric motor and derivation of quantities with finite elements was realised with the help of many scientific papers and books, as well as [D. Meeker's FEMM](https://www.femm.info/wiki/HomePage) that can only be recommended to use, especially with its Python API.

For the windings, I am using [L. Alberti's Koil embedded in Dolomite](https://gitlab.com/LuigiAlberti/dolomites-python).

I got all the ressources for coding 2D magnetostatics from [N. Ida and J. Bastos, Electromagnetics and calculation of fields](https://link.springer.com/book/10.1007/978-1-4612-0661-3).
