[TOC]
# What is Inverse Kinematics?

Forward kinematics is a way to calculate an end effector's position and rotation given the number of joints, the distance between each joint and the angle each joint is rotated. Inverse kinematics does the opposite: given the end effector's position and rotation and try to solve for each joint's rotation. 

## Importance of Inverse Kinematics

Why do we need inverse kinematics? The simple answer is for very precise robotic arm movements. In fact, we as humans have this built into our brains!

Try it out! Use your wrist as an end effector and try to move it in a line as straight as possible. While you're doing this, you can see how your elbow bends without you even thinking about bending it. This is what we call inverse kinematics. 

## Procedural Animation

Inverse kinematics is mostly used in robotics but it can be adapted for procedural animation! You might even see it already built into rigging/animation software like *Blender* where they use IK targets to move arms around. 

We have many reasons for using inverse kinematics in procedural animation. One of the main reasons is its modularity, being able to be used for limbs from arms to legs to even fingers!. This is especially important as it prevents problems like floating feet when walking down slopes.

# The Math behind Inverse Kinematics

Now that we know what inverse kinematics is and what it's used for, we can talk about the mathematics behind inverse kinematics. For the sake of my sanity, I will not be talking about the solutions for anything past a three-link solution.

## Two-Link Inverse Kinematics

<img src="/static/images/devlogs/inverse-kinematics/Two-Link Diagram.png">

While this problem might seem daunting at first, it really isn't that hard of a problem to solve. This is especially apparent when we draw a diagram, but first we should know what we have and are looking for. First, what we know:

- $O$ - origin's position
- $E$ - end effector's position
- $l_1, l_2$ - the first and second link's length respectively
- $d$ - the distance between $O$ and $E$
- $\theta_E$ - the angle from the origin to the end effector (be careful when calculating this and make sure to use $\text{atan2}(y,x)$ instead of the normal trig functions or else the signs are going to act weird)

Now that we know what we get to work with, let's define what we need to try and solve for:

- $\theta_0, \theta_1$ - the calculated angle for the first and second joints respectively

### Solving the System

<img src="/static/images/devlogs/inverse-kinematics/Three-Link Target Diagram.png">

The easiest way to understand the problem is to draw a diagram (see top right).

Using this diagram, it is much easier to see that we are essentially just solving a triangle. If you know how to use <a href="https://en.wikipedia.org/wiki/Law_of_cosines" target="_blank" class="info-hover">law of cosines</a>, its very easy to see where this is going but for those of you who don't, I will explain below.

Essentially, our problem trickles down to a triangle where we need to solve the internal angles of the triangle. The first step is to solve for $\theta_0$ by using the internal angle opposite from $l_2$. This internal angle, $\theta_a$, can be solved for using the <a href="https://en.wikipedia.org/wiki/Law_of_cosines" target="_blank" class="info-hover">law of cosines</a>. Below is a symbolic solution for $\theta_a$ and $\theta_0$.

<p>

$$
\begin{align*}
l_2^2&=d^2+l_1^2-2dl_2\cos\theta_a\\
2dl_2\cos\theta_a&=d^2+l_1^2-l_2^2\\
\cos\theta_a&=\frac{d^2+l_1^2-l_2^2}{2dl_2}\\
\theta_a&=\cos^{-1}\left(\frac{d^2+l_1^2-l_2^2}{2dl_2}\right),\frac{d^2+l_1^2-l_2^2}{2dl_2}\in[-1,1]\\
\text{Since }\theta_a&=\theta_0+\theta_E,\text{ therefore }\theta_0=\theta_a-\theta_E
\end{align*}
$$

</p>

<span class="clear"></span>
Next we need to calculate $\theta_1$. This is practically the same, so just repeat the process. (If you are using degrees, swap $\pi$ for $180^\circ$)

<p>

$$
\begin{align*}
\theta_b&=\cos^{-1}\left(\frac{l_1^2+l_2^2-d^2}{2l_1l_2}\right)\\
\text{Since }\theta_1&\text{ is the exterior angle,}\\
\text{then }\theta_1&=\pi-\theta_b.
\end{align*}
$$

</p>

Now that we have $\theta_0$ and $\theta_1$, we can finally orient our arm to have the end effector be at the target position! Just apply the rotations onto your joints and it should work properly!

## Three-Link Inverse Kinematics in $\mathbb{R}^3$

Starting this chapter, I want to preface that this is surprisingly easy to do. We can pretty much just reduce this problem into a two-link problem in 2D. By doing so, we can remove a degree of freedom and add it back later after the harder calculations are done. 

First, let's define our known variables. Most variables are the same but some are changed for example:

- $O$ - origin's position in $\mathbb{R}^3$
- $E$ - end effector's position in $\mathbb{R}^3$
- $l_1, l_2$ - the first and second link lengths respectively

We also introduce some new variables so that we don't end up with infinite solutions:

- $l_3$ - since we are doing a three-link problem we do need the third link length
- $E_y$ - end effector's up vector in $\mathbb{R}^3$ (this can be done using the rotation but it's easier with the up vector)
- $O_x$, $O_y$, $O_z$ - unit vectors that define $O$'s local space

Now we need to talk about what we are trying to find. I moved $d$ and $\theta_E$ here since they are calculated fairly differently compared to their 2D counterparts.

- $\theta_0,\theta_1,\theta_2$ - the calculated angles for joints 1, 2 and 3 respectively
- $\theta_E$ - the angle on the projected plane from $O$ to $P_T$ (defined later)
- $d$ - the distance from $O$ to $P_T$ (defined later)

### Solving the System

<img src="/static/images/devlogs/inverse-kinematics/Three-Link Diagram.png">

The easiest way to understand and solve this problem is by projecting the entire equation onto a plane and solving as if it was a system in $\mathbb{R}^2$.  Projecting something onto a plane might sound scary but we can just fake it by rotating the entire system to be on the xy-plane then rotating it back after. 

To do this, we do have to define another variable, $\theta_y$. Assuming that the y-axis is up, <a href="https://en.wikipedia.org/wiki/Right-hand_rule" target="_blank" class="info-hover">x-axis is left</a> and z-axis is forward, $\theta_y$ would be the angle we rotate around the y-axis. First we want to make sure that everything is calculated locally so if $O$ is not $(0,0,0)$ then it won't accidentally calculate a wrong end effector position. 

So let's define $E_L$ as the end effector position with respect to the origin's position: $E_L=E-O$. We can actually simplify this problem further into a two-link problem if we just use the up vector, $E_y$, and the third-link length, $l_3$, to offset the entire system: $P_T=E_L-l_3E_y$, assuming the last joint respects the $E_y$ condition. This gives us the local position of an intermediate target. 

Using $P_T=(x_T,y_T,z_T)$ we can finally solve for $\theta_y$:

<p>

$$
\theta_y=\text{atan2}(x_T,z_T)
$$

</p>

Now that we have $\theta_y$ we can fake the projection of $P_T$ onto the xy-plane. Since we are literally just flattening the z-plane onto the xy-plane, we can just get $P_T$ in $\mathbb{R}^2$ by just replacing the x-value with the magnitude of $P_T$ on the xz plane. I know that might have sounded like gibberish but essentially what we want to do is just replace the $x$ component with $r_T=\sqrt{x_T^2+z_T^2}$. So now $P_T$ should look like $(r_T,y_T,0)$ symbolically. 

After we project it, we can finally solve for $\theta_E$ and $d$:

<p>

$$
\begin{align*}
\theta_E&=\text{atan2}(y_T,r_T)\\
d&=\sqrt{y_T^2+r_T^2}
\end{align*}
$$

</p>

Now we have everything we need and should be able to shove all of this information into our <a href="/devlog#solving-the-system">two-link solver</a> where instead of $E$ we just use $P_T$. Assuming you did that, we now have $\theta_0$ and $\theta_1$. 

We have two options from here, we can take the easy way out which leads to really weird edge cases or we can do the hard way where it looks somewhat natural.  

### The Unnatural Easy Way

The easy way is really straightforward but the downside is that if $P_T$ isn't lying in the same plane as $O$ and $E$, then it will look very weird. If you do want to do this way and you don't really care how the system responds to the last joint's orientation, then you can quite literally just set the last joint's up vector to be $E_y$.

### The Natural Hard Way

To make it more natural we need to solve for, $\theta_2$. This one is a bit harder than the other $\theta$'s but it's easier to understand once we draw a diagram. To do this we need the up and forward vector of the 3rd joint (given we rotated over the x-axis), namely $J_y, J_z$. Finally, to calculate $\theta_2$ we need to find the $x$ and $y$ values in the 3rd joint's coordinate frame, we will call them $j_y$ and $j_z$:

<p>

$$
\begin{align*}
j_y&=J_y\cdot E_y\\
j_z&=J_z\cdot E_y\\
\theta_2&=\text{atan2}(j_z,j_y)
\end{align*}
$$



</p>

Now once we rotate all the joints by their respective $\theta$ values it should work, right? No, we still haven't rotated the system so that $O$, $P_T$ and $E$ all lie on the same plane. To do this we need to calculate another angle, $\beta$, which is the roll on the origin we need to rotate it by to align all three points onto the same plane. Since the roll angle will be about $O_z$, we need to project $E_y$ onto the $O_x, O_y$ plane to remove the $O_z$ component. We use the dot products between a transformed $E_y$ (we'll call $E_T$) and the axes of $O$ and put it into the $\text{atan2}$ function to calculate $\beta$:

<p>

$$
\begin{align*}
\text{Let }O&_x,O_y,O_z\text{ be the axes of }O.\\\\
E_T&=O_x(E_y\cdot O_x)+O_y(E_y\cdot O_y),\ \because |O_x|, |O_y|=1
\end{align*}
$$

</p>

Using this, we can calculate $\beta$ ($E_T^x,E_T^y$ are the $x$ and $y$ components of $E_T$):
$$
\beta=\text{atan2}(E_T^y,E_T^x)
$$
If you are doing this in code, or you just don't want that many equations, you can simply ignore $E_T$'s calculations and just have:
$$
\beta=\text{atan2}(E_y\cdot O_y,E_y\cdot O_x)
$$
You might notice that substituting $E_T^y$ and $E_T^x$ doesn't necessarily always equal the dot products in the line above, but since $O_x$, $O_y$ and $O_z$ are all perpendicular unit vectors, they end up being equal.

To ensure your math will work out, please rotate the angles in this specific order before doing the next step. For example, it is crucial you rotate $O$ by $\theta_y$ before you calculate $\beta$ or else your calculations will be off and it might not align with where it's supposed to go. If you need it, here are the rotations in order:

1. Rotate the base $O$ around the y-axis by $\theta_y$.
2. Rotate the first joint by $\theta_0$. (you can also use -$\theta_0$)
3. Rotate the second joint by $-\theta_1$. (use $\theta_1$ if you used $-\theta_0$ in the previous step)
4. Rotate the third joint by $-\theta_2$.
5. Finally, rotate the base around its Z-axis by the roll angle $\beta$.


<div class="clear"></div>

#  Implementation in Unity C\#

Coding this Unity is actually pretty simple. I'll show how to code it in 2D then later project it into a 3D space. I really hope that you actually try and understand the math and how it works instead of just copying the code.

### 2D Implementation

In case you didn't read the math behind it, the problem we are essentially solving is just completing a triangle given all three side lengths. To do this we will just need to solve for some stuff before we can apply the cosine law.

I do want to just state that I will be solving this in a xy-plane. If you are making this for a 2D game in Unreal Engine for example, you will just need to replace the y-axis with the z-axis.

There are two ways we can actually solve this in Unity but it just depends on the use case:

- Bone Joints System - Calculates the rotation and applies it on the joints to have the end effector reach the target
- Position System - Calculates the position of each joint and sets their positions to it. Rotations are completely ignored in this system. (Don't use this if you have a skinned mesh renderer like a bone)

The "better" solution is often the bone joints system as it should be cheaper and is fairly easy to understand. Inverse kinematics is also used most of the time for animation so its likely the system is already setup for this way.

Honestly for the second system, I really don't know what you could use it for. The only time I've personally used it is for debugging and checking if my math works or if it's Unity that's broken. Anyways, the main drawback of this system is more setup and it not having really having any rotation built-in.

#### Setup for Both Systems

Anyways, we let's define the variables we know:

```csharp
public Transform origin; // also known as the shoulder joint transform
public Transform target; // what we are trying to reach

public Transform joint1; // the intermediate joint, the one between the origin and end effector
public Transform endEffector; // the transform for the end effector
public float l1, l2; // the link lengths

//	These are only used if solving a 3-link system
public Transform joint2; // the second-last joint 
public float l3; // the final link length
```

Next let's define what we'll need to solve for:

```csharp
public float d; // distance between origin and target
public float angI; // the angle from the axis to the vector made from origin - target
public float ang1; // the angle of the first joint

public float ang2; // the angle of the second joint (used only in 3-link systems)

```

<img src="/static/images/devlogs/inverse-kinematics/2D Unity Implementation Diagram.png">

Now we need to calculate these values. It should be pretty simple since we can use the math library that Unity provides:

This code below should allow you to calculate the values correctly. There might be some offsets you still have to apply like $\pi - \theta$ or something similar but its different depending on your setup. Also make sure to convert all your angles back to degrees as it might cause some errors otherwise.

```csharp
//	Calculate distance & angI first
d = Vector3.Distance(origin.position, target.position); // Vector2.Distance also works

Vector2 localTargetPos = new Vector2(target.position.x - origin.position.x, target.position.y - origin.position.y);
angI = Mathf.Atan2(localTargetPos.y, localTargetPos.x); // Atan2 uses y then x idk why lol

//	There might be offsets you might have to add when calculating
ang1 = Mathf.Acos((l1*l1 + d*d - l2*l2) / (2 * l1 * d)); // ang1 is opposite of l2
ang2 = 2 * Mathf.PI - Mathf.Acos((l1*l1 + l2*l2 - d*d) / (2 * l1 * l2)); // its an exterior angle so offset accordingly
```



