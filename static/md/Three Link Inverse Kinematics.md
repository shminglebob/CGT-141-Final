[TOC]
# What is Inverse Kinematics?

Forward kinematics, the predecessor of inverse kinematics, is a way to calculate an end effectors position and rotation given the number of joints, the distance between each joint and the angle each joint is rotated. Inverse kinematics however is the opposite of that where you are given the end effectors position and rotation and you want to solve for how much each joint is rotated. 

## Importance of Inverse Kinematics

So now the question is why do we need inverse kinematics? The simple answer to this question is we need it for very precise robotic arm movements. In fact, this is so important that even we as humans have this built into our brains!

Try it out! Use your wrist as an end effector and try to move it in a line as straight as possible. While you're doing this, you can see how your elbow bends without you even thinking about bending it. This is what we call inverse kinematics. 

## Procedural Animation

Inverse kinematics is mostly used in robotics but it can be adapted for procedural animation! You might even see it already built into rigging/animation software like blender where they use IK targets to move arms around. 

We have many reasons for using inverse kinematics in procedural animation. I would say one of the main reasons that its great is due to its modularity, being able to be used for limbs like arms and legs. Using inverse kinematics in procedural animation is great since it can prevent problems like floating feet when walking down slopes.

# Two Link Inverse Kinematics Calculations

# Three Link Inverse Kinematics Calculations

# 3D Implementation in Unity
