[TOC]

# Introduction

While I was just starting out in game development, a few videos (specifically by [Codeer](https://www.youtube.com/Codeer) and [t3ssel8r](https://www.youtube.com/t3ssel8r)) popped up on my recommended showcasing procedurally animated creatures. After watching some videos, I decided to try and create my own system. Now that I have built the core system behind a procedurally animated spider, I wanted to cover all of the math, code and logic for anyone interested.

# Technical Details

Since I have another [devlog](https://portfolio.paidvbux.com/devlog/inverse-kinematics) on how the leg joint orientations are calculated, I will not be covering it in here. We can also simplify the system to only calculate the target position and completely ignore anything to do with the legs. Therefore, we would only really need to calculate target position/orientation along with the body position/orientation.

## Parenting Structure

Since I did make this in Unity, how the objects are parented is crucial to making the spider controller actually work. Here's how I parented the objects in my project:

```text
Spider (what is moved and everything follows it)
-> Body (the rendered body)
    -> Pivots
        -> Pivot 1..n
    -> Ground Targets
        -> Ground Target 1..n
-> Legs
    -> Leg 1..n
        -> IK Target 1..n
```

Essentially, this parenting structure moves the pivots and ground targets to follow the body's orientation and its position. I separated the body from the main spider transform so I could keep its transform preserved locally in case it is needed for systems like pathfinding. This is a preference thing though so if your goal isn't to use it as a mob in a game, then you can probably structure it as so:

> [!note] 
>
> `Pivots` and `Ground Targets` are not actually required in both cases as they are just there for organization. The `Legs` parent, however, is required and needs to be at the origin with no orientation or else it can mess with the inverse kinematics in each leg.

```text
Body
->   Pivots
    ->   Pivot 1..n
->   Ground Targets
    ->   Ground Target 1..n
->   Legs
    ->   Leg 1..n
        ->   IK Target 1..n
```

## Logic Flow

Now that we got the parenting structure out of the way, let's talk about the logic of how we are going to move each leg and how I came to my answer.

### Leg Logic

The legs have two "targets", the ground target and the IK target. The inverse kinematics target (IK target) is just the end effector of the actual IK system and the ground target is used to calculate where to place the IK target. 

I made the ground targets shoot a raycast straight down from their position to calculate the IK target position. <span class="small-text">This must be changed if you wanted to incorporate wall-climbing.</span> 

We then simply interpolate the leg's end effector towards the ground target if the distance is greater than `maxLegDelta`.

### Update Loop

Since that was only the leg logic, we do need to talk about the role that it plays within the scope of the entire update loop. This leg logic is only used for detecting when to move the IK target and then moving the legs towards that target then repeating it. 

There are still other things we need to calculate like the body's height and orientation which are both based off the leg positions. The body's transform should be calculated before the legs but after the legs are initialized.

Using this we can form a basic update loop like so:

> [!important]
>
> The leg parent's position and rotation must be zeroed or else it will cause errors when rotating the spider.

```csharp
void Update() {
    //	Make sure the leg parent's position and rotation are zeroed to prevent errors
    legParent.position = Vector3.zero;
    legParent.rotation = Quaternion.identity;
    
    if (legsInitialized) {
        CalculateBodyHeight();
        CalculateBodyTilt();
    }
    
    UpdateLegs();
}
```

Although this could work, if we wanted the spider to look more realistic (and not like a water skipper), we will need to figure out a way to alternate the legs. 

So let's separate our legs into two leg groups, the left legs and the right legs, and give each of them an offset (as to not have both legs across from each other to move in sync). Now `UpdateLegs()` should be replaced by something like this:

```csharp
UpdateLegGroup(leftLegs, 0);
UpdateLegGroup(rightLegs, 1);
```

Let's now define `UpdateLegGroup()` to actually incorporate this: 

> [!warning]
>
> Don't use `foreach` here as we need `i` for calculating the alternating legs. 

```csharp
void UpdateLegGroup(Legs[] legGroup, int offset) {
    for (int i = 0; i < legGroup.Length; i++) {	
    	Leg leg = legGroup[i];
        
        //	Anchor the leg's "shoulder" to be at the pivot.
        leg.transform.position = leg.pivot.position; 
        
        if (Vector3.Distance(leg.target.position, leg.groundTarget.position) > maxLegDelta 
            && ((i % 2 == offset) == groupOneMoving) && !leg.isStepping) {
			//	Most likely a thread due to it needing to be interpolated over time
            StartCoroutine(MoveIKTarget(leg.target, leg.groundTarget.position));
        }
    }
}
```

To explain the boolean that I used in the if statement, what we want to check: 

- `Vector3.Distance(...) > maxLegDelta` - that the distance is large enough to move the IK target to the ground target
- `(i % 2 == offset) == groupOneMoving` 
    - `groupOne` in this case would be the `leg0` of that group and by using the offset in `i % 2 == offset` we can add an offset so that both sides don't move the same index leg at the same time.

- `!leg.isStepping` - that the IK target is not already interpolating towards the ground target. This one is important!

## The Math behind the Code

If we were doing this completely from scratch this section would be quite a bit longer but since we can utilize Unity's built in mathematics libraries it makes our lives easier.

### Body Height Calculation

### Body Tilt Calculation







































