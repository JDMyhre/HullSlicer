Calculates where the waterline will be on a hull design. Takes an STL and slices it in 0.1 mm increments from y_min to y_max values of the model and then integrates the cross sectional areas to calculate the volume below a certain value of y. The program asks how many of these hulls there will be, as well as how much weight will be on them, and calculates where the waterline will be by solving the equilibrium equation where the mass of the volume of water displaced by the hull(s) is equal to the weight of the hull(s).

*Orientation of the model in the file must be +y up, but location with respect to origin doesn't matter.
*Hulls must be filled in solid for this program to work.
