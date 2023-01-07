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
