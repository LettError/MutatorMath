DesignSpace Factors
===================

In MutatorMath instances are calculated by multiplying all masters with a specific factor and then adding it all up. Determining the factors is then a important job. The code has to deal with all sorts of edge cases and extrapolation; but the basic structure is not so complex. 

These graphs were made with Drawbot and represent actual factors calculated by MutatorMath. It is a two dimensional designspace with four masters. The axes are gray. The third dimension is the value of the factors of the masters: 0 in the plane, 1 up in space. 

![master at the origin](designSpace_neutral.jpg)

The master at the <em>origin</em>, the place where all dimensions are 0. The master at the origin is called <em>neutral</em>. All other on-axis masters in the designspace are relative to this neutral. That means that the neutral is subtracted from each. At the end of the calculation the neutral is added again to <em>inflate</em> the instance. So the factor for the neutral is 1, it is part of everything. The factors of the neutral master form a box.

![on-axis master one](designSpace_on-axis-one.jpg)

Now we insert the second master at Location(A=1, B=0). It is <em>on-axis</em> because only one of its dimensions (A) has magnitude. Its factor is 1 along the line A=1. Note its factor is 0 at the origin and at the line A=0 (and all other axes if we had more). In this designspace the influence of this master forms a wedge.

![on-axis master two](designSpace_on-axis-two.jpg)

Next we insert a another on-axis master, but now at Location(A=0, B=1). This factor is 1 along the line B=1. It it also 0 at the origin. This is another wedge.

![off-axis master](designSpace_off-axis.jpg)

But we also want to include masters at other locations, what about Location(A=1, B=1) for instance? We can see that at that location both on-axis masters are at full force, and even the neutral is added with factor 1.
