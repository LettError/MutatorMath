DesignSpace Factors
===================

In MutatorMath instances are calculated by multiplying all masters with a specific factor and then adding it all up. Determining the factors is then a important job. The code has to deal with all sorts of edge cases and extrapolation; but the basic structure is not so complex. 

These graphs were made with Drawbot and represent actual factors calculated by MutatorMath.

![master at the origin](designSpace_neutral.jpg)

The master at the origin, the place where all dimensions are 0. The master at the origin is called <em>neutral</em>. All other masters in the designspace are relative to this neutral. That means that the neutral is subtracted from each. At the end of the calculation the neutral is added again to <em>inflate</em> the instance. So the neutral is part of everything. 

![on-axis master one](designSpace_on-axis-one.jpg)

Now we insert the second master at Location(A=1, B=1). It is <em>on-axis</em> because only one of its dimensions has magnitude. Its factor is 1 along the line A=1. Note its factor is 0 at the origin. In this designspace the influence of this master forms a wedge.

![on-axis master two](designSpace_on-axis-two.jpg)
![off-axis master](designSpace_off-axis.jpg)
