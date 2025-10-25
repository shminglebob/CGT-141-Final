[TOC]
# What is Inverse Kinematics?

Forward kinematics, the predecessor of inverse kinematics, is a way to calculate an end effectors position and rotation given the number of joints, the distance between each joint and the angle each joint is rotated. Inverse kinematics however is the opposite of that where you are given the end effectors position and rotation and you want to solve for how much each joint is rotated. 

## Importance of Inverse Kinematics

So now the question is why do we need inverse kinematics? The simple answer to this question is we need it for very precise robotic arm movements. In fact, this is so important that even we as humans have this built into our brains!

Try it out! Use your wrist as an end effector and try to move it in a line as straight as possible. While you're doing this, you can see how your elbow bends without you even thinking about bending it. This is what we call inverse kinematics. 

## Procedural Animation

Inverse kinematics is mostly used in robotics but it can be adapted for procedural animation! You might even see it already built into rigging/animation software like blender where they use IK targets to move arms around. 

We have many reasons for using inverse kinematics in procedural animation. I would say one of the main reasons that its great is due to its modularity, being able to be used for limbs like arms and legs. Using inverse kinematics in procedural animation is great since it can prevent problems like floating feet when walking down slopes.

# The Math behind Inverse Kinematics

Now that you know what inverse kinematics is and what it's used for, we can talk about the mathematics behind inverse kinematics. For the sake of my sanity, I will not be talking about the solutions for anything past a three link solution.

## Two Link Inverse Kinematics

<div class="float-right diagram" style="--src: url('/static/images/Inverse Kinematics/Labelled Diagram.png'); margin-left: 1rem;"></div>

While this problem might seem daunting at first, it really isn't that hard of a problem to solve. This is especially apparent when we draw a diagram, but first we should know what we have and are looking for. First, what we know:

- $O$ - origin's position
- $E$ - end effector's position
- $l_1, l_2$ - the first and second link's length respectively
- $d$ - the distance between $O$ and $E$
- $\theta_E$ - the angle from the origin to the end effector (be careful when calculating this and make sure to use atan2$\frac y x$ instead of the normal trig functions or else the signs are going to act weird)

Now that we know what we get to work with, let's define what we need to try and solve for:

- $\theta_0, \theta_1$ - the calculated angle for the first and second joints respectively

### Solving the System

The easiest way to understand the problem is to draw a diagram (see top right).


Using this diagram, it is much easier to see that we are essentially just solving a triangle. If you know how to use <a href="https://en.wikipedia.org/wiki/Law_of_cosines" target="_blank" class="info-hover">cosine law</a>, its very easy to see where this is going but for those of you who don't, I will explain below.

Essentially, our problem trickles down to a triangle where we need to solve the internal angles of the triangle. The first step is to solve for $\theta_0$ by using the internal angle opposite from $l_2$. This internal angle, $\theta_a$, can be solved for using the <a href="https://en.wikipedia.org/wiki/Law_of_cosines" target="_blank" class="info-hover">cosine law</a>. Below is a symbolic solution for $\theta_a$ and $\theta_0$.

<p>

$$
\begin{align*}
l_2^2&=d^2+l_1^2-2dl_2\cos\theta_a\\
2dl_2\cos\theta_a&=d^2+l_1^2-l_2^2\\
\cos\theta_a&=\frac{d^2+l_1^2-l_2^2}{2dl_2}\\
\theta_a&=\cos^{-1}\left(\frac{d^2+l_1^2-l_2^2}{2dl_2}\right)\\
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

## Three Link Inverse Kinematics in $\mathbb{R}^3$

Starting this chapter, I do want to state that this is surprisingly easier to do as most of you had probably thought. We can pretty much just reduce this problem into a two link problem in 2D. So this chapter will mostly just talk about how we can do that.

First, let's define our known variables. Most variables are the same but some are changed for example:

- $O$ - origin's position in $\mathbb{R}^3$
- $E$ - end effector's position in $\mathbb{R}^3$
- $l_1, l_2$ - the first and second link lengths respectively

We also introduce some new variables so that we don't end up with infinite solutions:

- $l_3$ - since we are doing a three link problem we do need the third link length
- $E_{up}$ - end effector's up vector in $\mathbb{R}^3$ (this can be done using the rotation but it's easier with the up vector)

Now we need to talk about what we are trying to find. I moved $d$ and $\theta_E$ here since they are calculated fairly differently compared to their 2D counterparts.

- $\theta_0,\theta_1,\theta_2$ - the calculated angles for joints 1, 2 and 3 respectively

### Solving the System

The easiest way to understand and solve this problem is by projecting the entire equation onto a plane and solving as if it was a system in $\mathbb{R}^2$.  Projecting something onto a plane might sound scary but we can just fake it by rotating the entire system to be on the xy-plane then rotating it back after. 

To do this, we do have to define another variable, $\theta_y$. Assuming that the y-axis is up, <a href="https://en.wikipedia.org/wiki/Right-hand_rule" target="_blank" class="info-hover">x-axis is left<span class="info-box"><span class="info-title">Unity uses left-hand rule. The x-axis is right instead.</span></span></a> and z-axis is forward, $\theta_y$ would be the angle we rotate around the y-axis. First we want to make sure that everything is calculated locally so if $O$ is not $(0,0,0)$ then it won't accidentally calculate a wrong end effector position. 

So let's define $E_L$ as the end effector position in respect to the origin's position: $E_L=E-O$. We can actually simplify this problem further into a two-link problem if we just use the up vector, $E_{up}$, and the third link length, $l_3$, to offset the entire system: $P_T=E-O-l_3E_{up}$. This gives us the local position of an intermediate target. 

Using $P_T=(x_T,y_T,z_T)$ we can finally solve for $\theta_y$:

<p>

$$
\theta_y=\text{atan2}\left(\frac{y_T}{x_T}\right)
$$

</p>

Now that we have $\theta_y$ we should fake the projection of $P_T$ onto the xy-plane. Since we are literally just flattening the z-plane onto the xy-plane, we can just get $P_T$ in $\mathbb{R}^2$ by just replacing the x-value with the magnitude of $P_T$ on the xz plane. I know that might have sounded like gibberish but essentially what we want to do is just replace $x_T$ with $\sqrt{x_T^2+z_T^2}$. So now $P_T$ should look like $(\sqrt{x_T^2+z_T^2},y_T,0)$ symbolically. 

We should just be able to shove all of this information into our two link solver where instead of $E$ we just use $P_T$. 

#  3D Implementation in Unity
