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

<div class="float-right diagram" alt="Labelled Diagram" style="--src: url('/static/images/Inverse Kinematics/Labelled Diagram.png'); margin-left: 1rem;"></div>

### List of Known Variables

- $O$ - origin's position
- $E$ - end effector's position
- $E_R$ - end effector's rotation (not needed)
- $l_1$ - the first link's length
- $l_2$ - the second link's length
- $d$ - the distance between $O$ and $E$
- $\theta_E$ - see labeled diagram

### Unknowns/What we need to find

- $\theta_0$ - see labeled diagram
- $\theta_1$ - see labeled diagram
- $P_0$ - the position at which the joint sits at (optional)

### Solving the System

The easiest way to understand the problem is to draw a diagram (see top right).


Using this diagram, it is much easier to see that we are essentially just solving a triangle. If you know how to use <a href="https://en.wikipedia.org/wiki/Law_of_cosines" target="_blank" class="info-hover">cosine law<span class="info-box">
<span class="info-title">Cosine law states:</span>
<span>$a^2=b^2+c^2-2bc\cos A$</span>
<span class="subtext">$a, b, c$ - side lengths</span>
<span class="subtext">$A$ - angle opposite side length $a$</span>
</span></a>, its very easy to see where this is going but for those of you who don't, I will explain below.

Essentially, our problem trickles down to a triangle where we need to solve the internal angles of the triangle. The first step is to solve for $\theta_0$ by using the internal angle opposite from $l_2$. This internal angle, let's call it $\theta_2$, can be solved for using the <a href="https://en.wikipedia.org/wiki/Law_of_cosines" target="_blank" class="info-hover">cosine law<span class="info-box">
<span class="info-title">Cosine law states:</span>
<span>$a^2=b^2+c^2-2bc\cos A$</span>
<span class="subtext">$a, b, c$ - side lengths</span>
<span class="subtext">$A$ - angle opposite side length $a$</span>
</span></a>.

<span class="clear"></span>
Next we need to calculate $\theta_1$. This is practically the same, we just reuse the cosine law. 

## Three Link Inverse Kinematics in 3D

## 3D Implementation in Unity
