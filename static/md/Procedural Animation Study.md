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

Essentially, this parenting structure moves the pivots and ground targets to follow the body's orientation and its position. I separated the body from the main spider transform so I could keep its transform preserved locally in case it is needed for systems like pathfinding. This is a preference thing though so if your goal isn't to use it as a mob in a game, you can probably structure it as so:

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

`Pivots` and `Ground Targets` are not actually required in both cases as they are just there for organization. The `Legs` parent, however, is required and needs to be at the origin with no orientation or else it can mess with the inverse kinematics in each leg.

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

I used a normal `for` loop here as we need `i` for alternating legs and to explain the if statement, here's what we want to check: 

- `Vector3.Distance(...) > maxLegDelta` - that the distance is large enough to move the IK target to the ground target
- `(i % 2 == offset) == groupOneMoving` 
    - `groupOne` in this case would be the `leg0` of that group and by using the offset in `i % 2 == offset` we can add an offset so that both sides don't move the same index leg at the same time.

- `!leg.isStepping` - that the IK target is not already interpolating towards the ground target. This one is important!

## The Math behind the Code

If we were doing this completely from scratch this section would be quite a bit longer but since we can utilize Unity's built in mathematics libraries it makes our lives easier.

### Body Height Calculation

Since this is a script that runs per frame, we can't have something where it depends on the next frame. Meaning that we cannot have a circular dependency. If we really wanted to solve for the body's absolute position as in it lies in the middle of the four furthest legs plus a local y offset, it will just be stuck in place since we are overriding any movement. To avoid this, we will just solve for height as it looks natural enough and still provides enough freedom for the spider to move.

<img src="/static/images/devlogs/spider/Height Leg Setup Diagram.png">

First, we need to find the mid-point of the four furthest legs. For the sake of modularity, I decided that it would be the four legs if all legs in between each side are removed (essentially just the corners).

What we need to solve for to calculate the height is the $t$ value where the vectors pointing to the opposite legs intersect. We will call them $\vec p$ and $\vec q$ and the points $p_1, p_2, q_1, q_2$ where the $p$ points make up $\vec p$ and the $q$ points make up $\vec q$.

These points we can get by projecting the points onto a plane that has the body's up vector as the normal. Given the body's normalized up vector is $B$ and our points are named $l_f,l_r,r_f,r_r$ where $l$ is left, $r$ is right and $_f$ is front, $_r$ is rear:
$$
p_1=\frac{l_f\cdot B}{||B||^2}B\\
$$
$$
p_2=\frac{r_r\cdot B}{||B||^2}B\\
$$
$$
q_1=\frac{r_f\cdot B}{||B||^2}B\\
$$
$$
q_2=\frac{l_r\cdot B}{||B||^2}B
$$


Using [Cramer's Rule](https://en.wikipedia.org/wiki/Cramer%27s_rule#Explicit_formulas_for_small_systems), we can solve for the value $t$ using this formula:
$$
t=\frac{(q_{1x}-p_{1x})(q_{2z}-q_{1z})-(q_{1z}-p_{1z})(q_{2x}-q_{1x})}{(p_{2x}-p_{1x})(q_{2z}-q_{1z})-(p_{2z}-p_{1z})(q_{2x}-q_{1x})}
$$
After getting $t$, we can now find the midpoint by subbing in the values like so:
$$
(x,z)=(p_1x,p_1z)+t\cdot\vec p
$$

Now we need to calculate the $t$ values per vector, so $t_p$ and $t_q$. To do so, we need the positions of the joints. We don't want to use $\vec p$ or $\vec q$ here.
<div class="math">
$$
t_p=\frac{x-l _{fx}}{(r _r-l _f) _x}
$$
$$
t_q=\frac{x-r _{fx}}{(l _r-r _f) _x}
$$
</div>
Next we calculate the y-position of both $\vec p$ and $\vec q$ when we plug in their respective $t$ values:
<div class="math">
$$
y_{p}=(r _r-l _f) _y\cdot t _p+l _{fy}
$$
$$
y_{q}=(l _r-r _f) _y\cdot t _q+r _{fy}
$$
</div>
These values are probably pretty different so we just take the average of the two and use it as the desired height. Since we do want to be able to tweak the value of the body and not fix it to the desired height, let's introduce a controllable external variable, $d_y$ which represents the distance from the desired height.

Finally we get our height which is:
$$
\frac{y_p+y_q}2+d_y
$$

### Body Tilt Calculation

Calculating the body's tilt is another way we can make the body's movements seem more natural. To do this, we need to create a plane that somewhat accommodates all four of the same points used in height calculations.

<img src="/static/images/devlogs/spider/Tilt Calculation Diagram.png">

There are more accurate ways of getting a plane to fit the four points using different algorithms but since it is a game and we need to accommodate lower-end specs, we use an easier and less computationally expensive way.

First, we take all the normal vectors that we can make using different combinations of adjacent vectors. This means that these two vectors should share one point. To get these normal vectors, we just take the cross product then normalize it. Let's get the cross products first:
<div class="math">
$$
c_1=(l_f-r_f)\times(r_r-r_f)
$$
$$
c_2=(r_f-r_r)\times(l_r-r_r)
$$
$$
c_3=(r_r-l_r)\times(l_f-l_r)
$$
$$
c_4=(l_r-l_f)\times(r_f-l_f)
$$
$$
n_1=\frac{c_1}{|c_1|}
$$
$$
n_2=\frac{c_2}{|c_2|}
$$
$$
n_3=\frac{c_3}{|c_3|}
$$
$$
n_4=\frac{c_4}{|c_4|}
$$
</div>
After getting these normal vectors, we take the average, $n=\frac{n_1+n_2+n_3+n_4}4$. We then project the body's forward vector onto a plane that uses $n$ as its normal vector. We'll call this $B_f$ which stands for body forward. Using quaternions, we can set the body's forward to be equal to $B_f$ and the tilt calculations are complete.

# Full Script Explanation

For the sake of simplicity (and not writing documentation for my second order dynamics system), I will use the spider controller that uses linear interpolation instead.

## Variables

### The Leg Class

This class has quite a bit of variables and this is stored per leg:

```csharp
public Transform pivot;
public Transform groundTarget;
public ThreeLinkV2 leg;

// below are all hidden in the inspector
public bool initialized = false;

public Vector3 startPosition, targetPosition;
public Vector3 startUp, targetUp;

public float restTimer;
public float startInterpolationTime;
public bool isStepping = false;

public Vector3 rawUp;
public Quaternion skewRotation;
```

#### References

- `pivot` - the "shoulder" position on the body. Essentially the position the leg should be fixed to.
- `groundTarget` - the desired landing point on the ground.
- `leg` - reference to the IK solver. Only the third link length and IK target are accessed through this script.

If `pivot` and `groundTarget` were on a 2D plane, `pivot = (0, 1)` and `groundTarget = (2, 3)`, then intuitively the distance between where the leg's end effector and the `pivot` would aim to be $2\sqrt2$ units apart.

#### Stepping Interpolation

- `initialized` - whether the leg has touched the ground at least once and has valid starting values.
- `startPosition`, `targetPosition` - the start and end positions for the step interpolation.
- `startUp`, `targetUp` - the start and end up vectors for rotation in the interpolation. 
- `restTimer` - how long the leg has been idle before forcing a step to correct its "posture". Essentially ensures that the spider isn't in some half-way step.
- `startInterpolationTime` - used in interpolation since it lerps over a certain interval. 
- `isStepping` - whether the leg is currently interpolating. Needed otherwise it will stay frozen at `startPosition` forever.

`startUp` and `targetUp` could be replaced with `Quaternion startRot, targetRot` while using `Quaternion.Slerp`. The up vectors only exists since this was adapted from a system that only accepts vectors.

#### Leaning/Velocity-based Rotation

- `rawUp` - the unmodified up vector used as the base for leaning.
- `skewRotation` - the velocity-based rotation applied on `rawUp`.

### Float Parameters

```csharp
// Cosmetic Settings
float distToLegCentre = 0.5f;

// Raycast Settings
LayerMask groundMask;
float maxRaycastDist = 5f;
float minDelta = 0.25f;
float maxDelta = 2f;

//Smoothing Settings
float bodyTiltLerpSpeed = 10f;
float velocitySmoothSpeed = 2f;
```

#### Cosmetic Settings

This doesn't change much with the code but just allows for some tweaks to make the spider look how you want it to.

- `distToLegCentre` - controls how far above the computed average between $\vec p$ and $\vec q$ the body should lie. (Refer to [body height calculation](#Body Height Calculation))

#### Raycast Settings

- `groundMask` - whatever layer the legs should be able to walk on/see. 
- `maxRaycastDist` - how max distance the raycast can go
- `minDelta` - if the distance between a leg's IK target and the `hit.point` of the raycast is greater than this value, **after idling for a specified amount of time**, it will correct itself and take a step to be closer to `hit.point`.
- `maxDelta` - if the distance between a leg's IK target and `hit.point` is greater than this value, it will take a step. **Does not require idling.**

#### Smoothing Settings

These control the speed at which some values interpolate (using lerp or slerp). When these are used they are multiplied by `Time.deltaTime` to ensure that it stays consistent between different frame rates.

- `bodyTiltLerpSpeed` - how quickly the body tilts towards its comfortable resting position.
- `velocitySmoothSpeed` - how much to smooth the velocity calculations. **This is crucial as it fixes the jitteryness that comes with differentiating over frames.** If this is too high, the body will follow the actual position weirdly and might be a bit off.

### Body Settings

```csharp
Transform body;
Transform legParent;
```

There are only two variables here. `body` is what should be the physical body. `legParent` is an important one, it has to contain all legs that are to be attached to the body. **This must be separate from `body` as all children under this transform has its local position and rotation frozen.**

### Velocity-Based Settings

```csharp
[MinMaxSlider(0, 2, true)] Vector2 legStepTime;
[MinMaxSlider(0, 90, true)] Vector2 maxFrontLegsLeanAngle;
[MinMaxSlider(0, 90, true)] Vector2 maxHindLegsLeanAngle;

AnimationCurve tVelocityCurve;
float theoreticalMaxVelocity = 15f;
float maxLeadDist = 3f;
```

#### Sliders

These "min max sliders" are two values each. For example, for `legStepTime` there's actually `minLegStepTime` and `maxLegStepTime` defined through the inspector. Of course they are still accessed by `legStepTime.x` and `legStepTime.y` but it just makes the devX better. This only works with Odin Inspector so if you don't have it just use two separate float values for each.

- `legStepTime` - this is two values. Depending on the velocity of the spider, it will interpolate over towards the `max` value. This affects how long each step takes. In theory, it should take quicker steps when its moving faster.
- `maxFrontLegsLeanAngle`, `maxHindLegsLeanAngle` - these control how far a leg can lean away/push off from the ground. It controls the angle that it does so. **This does not mean that every step will be at this angle, that is interpolated using the equation $\frac{\text{distance}}{\text{maxDelta}}$ **.

#### Other

These other variables control some other behaviours related to velocity-based animation.

- `tVelocityCurve` - this controls how the `t` value is computed. **This should always start at $(0,0)$ and end at $(1,1)$**. Its purpose is just to give more control to how quickly the step time/lean angle changes kick in.
- `theoreticalMaxVelocity` - this is how we calculate `t`. We divide the current velocity, $v$, by this value, $v_{max}$, like so $\frac v{v_{max}}$ in order to get the value to substitute into `tVelocityCurve` to get our final `t` value. **The value before substituting into `tVelocityCurve` must be clamped between $[0,1]$.**

### Leg Settings

```csharp
Leg[] leftLegs;
Leg[] rightLegs;

AnimationCurve legStepHeightCurve;
float legRotSmoothSpeed = 10f;
float timeBeforeRest = 0.5f;
```

#### Leg Groups

`leftLegs` & `rightLegs` are the groups of legs on either side of the body. If you are coding this yourself, it is possible to combine the two but because of what I'm trying to do and because I'm not good enough at computer science, I decided to do it this way. The main reason for this is to get a way to separate the alternating legs and finding the legs needed for both the body height calculation and the body tilt calculations.

#### Other

These mostly cover cosmetic changes but are still important nonetheless

- `legStepHeightCurve` - this controls the height over the step. It should start at $(0,0)$ and end at $(1,0)$. The height of the step can be adjusted but this curve should be normalized.
- `legRotSmoothSpeed` - how quick the leg's up vector matches `-hit.normal` using an `slerp`. Like other smoothing/lerp speed variables, this is multiplied by `Time.deltaTimme` whenever used.
- `timeBeforeRest` - how long it takes before taking another step while idling. It will only take this step if the distance between `hit.point` and the IK target exceeds `minDelta`.

### Private Variables

```csharp
int numSteps, stepsCompleted;
bool groupOneMoving;

Vector3 prevBodyPos;
Vector3 rawVelocity, velocity;
float vMag;

float stepTime, leadDist;
float frontLeanAngle, hindLeanAngle;

bool onGround;
Transform rf, rr, lf, lr;
```

These variables are read-only values. The reason they are private is because they only really help debug stuff when shown so there's no need for them to exist in the inspector.

#### Stepping

These are used for stepping. `numSteps` and `stepsCompleted` are required but `groupOneMoving` can be dropped if you want all of the legs to move together. 

- `numSteps`, `stepsCompleted` - these are used to track when a leg group and is what allows for alternating legs. Specifically, `numSteps` is how many steps the system is waiting for to be completed. `stepsCompleted` is the counter for this and once they exceed or are equal to `numSteps`, it will reset and start the steps for the other leg group.
- `groupOneMoving` - is a boolean that flips whenever a leg group finishing moving. This just controls which legs move. For example, if leg group one was `lf, rr` and leg group two was `lr, rf`, `lf` and `rr` will take a step together then once finished `lr` and `rf` will take one together.

#### Velocity 

These are calculated and used only in the `Update` loop. These are used to calculate the interpolated `stepTime`, `leadDist` and the two `leanAngles`.

- `prevBodyPos` - this is just last frame's position of the body. It's used to calculate the `rawVelocity`.
- `rawVelocity` - this is the velocity computed by simply subtracting the current position by `prevBodyPos` then divided by `Time.deltaTime`. **This is, however, projected onto a plane constructed by `body.up`.** The reason for this is to not skew the magnitude when moving up and down. 
- `velocity` - this is a smoothed version of `rawVelocity`. The reason for this is because it causes quite a bit of jitteryness without this. If you're curious, just do `Debug.DrawRay(body.pos, rawVelocity);` and you will see how unstable it is. This just prevents weird jitteryness in other parts of the code.
- `vMag` - this is just the magnitude of the `velocity`, it's completely optional but makes debugging easier.

#### Velocity-Based

These are all calculated using their respective "min max sliders" and a computed `t` value. Since the `t` value is so important the calculation is as follows: 

`float t = tVelocityCurve.Evaluate(Mathf.Clamp01(vMag / theoreticalMaxVelocity));`

Essentially what this does is that it first uses the magnitude of the velocity and transforms it into a value normalized by `theoreticalMaxVelocity`. This does mean that it can go above `1` hence why we add the clamp. After we plug it into the defined curve that gives us more control on how `t` should change depending on the velocity.

- `stepTime` - this is the time that a step takes given the current `t` value. This should decrease the faster the spider is moving.
- `leadDist` - this is how far to lead each step as when it starts moving quickly, it'll lag behind quite a bit. This should increase the faster the spider is moving. **The minimum should be 0 as it will make the spider's resting position have leaded steps otherwise.**
- `frontLeanAngle`, `hindLeanAngle` - this is how far the `hit.normal` should be rotated around `body.right`. It should increase the faster the spider is moving. This is used to make the legs somewhat "push off" the ground to take a step.

#### Other

These are just some uncategorized variables that don't really fit in any of the other groups.

- `onGround` - this is just if all legs are on the ground or not. The calculation for this is kinda janky and I'll probably fix this later.
- `Transform rf, rr, lf, lr` - these variables are technically optional but makes the code so much easier to read. These are just references to the joints that are used in both the body height calculation and the body tilt calculation.

## Code Logic Explanation

### Start

```csharp
    //  Define points for body calculations
    rf = rightLegs[0].leg.joints[1].jointOrigin;
    rr = rightLegs[^1].leg.joints[1].jointOrigin;

    lf = leftLegs[0].leg.joints[1].jointOrigin;
    lr = leftLegs[^1].leg.joints[1].jointOrigin;

    velocity = Vector3.zero;
```

This should be fairly self explanatory but it just sets the values to be something. Also using `^` before a number while indexing makes it index from the opposite side. 

### Update Loop

#### Freezing LegParent

The next few ones are fairly long so its going to be separated into chunks.

```csharp
legParent.position = Vector3.zero;
legParent.rotation = Quaternion.identity;
```

These two lines anchor the `legParent` at $(0,0,0)$ and resets its rotation. **These lines are crucial as it prevents the legs from doubling its own y-angle when rotating the parent.** The reason why is because the inverse kinematics script that I had wrote in my [other devlog](https://portfolio.paidvbux.com/devlog/inverse-kinematics), already calculates and applies the y-angle while in 3D. This means that it applies this angle **on top** of the already rotated angle due to parenting.

#### After Leg Initialization

This is inside an if statement that uses [`legsInitialized()`](#legsInitialized()) to check whether all the legs are initialized. Access to the documentation of these functions are here: [`CalculateBodyPosition()`](#CalculateBodyPosition()) and [`CalculateBodyTilt()`](#CalculateBodyTilt()).

```csharp
CalculateBodyPosition();
CalculateBodyTilt();
```

These two lines above just calculate the position and the tilt of the body. **These can only be called after the legs are initialized because the body's position and tilt depend on the legs' positions.**

```csharp
rawVelocity = Vector3.ProjectOnPlane((body.position - prevBodyPos) / Time.deltaTime, body.up);

velocity = Vector3.Lerp(velocity, rawVelocity, Time.deltaTime * velocitySmoothSpeed);
vMag = velocity.magnitude;

float t = tVelocityCurve.Evaluate(Mathf.Clamp01(vMag / theoreticalMaxVelocity));

stepTime = Mathf.Lerp(legStepTime.y, legStepTime.x, t);

leadDist = Mathf.Lerp(0, maxLeadDist, t);
frontLeanAngle = Mathf.Lerp(maxFrontLegsLeanAngle.x, maxFrontLegsLeanAngle.y, t);
hindLeanAngle = Mathf.Lerp(maxHindLegsLeanAngle.x, maxHindLegsLeanAngle.y, t);
```

The code above calculates the velocity and all of the velocity-based variables that are to be used later in other functions. For example, `stepTime` is used later to determine how long each step is going to take.

##### `t` Calculation

Let's talk more about how the math behind this code actually works. We'll go line by line and I'll explain why I wanted to make it the way it is. So first, we have the calculation for `rawVelocity`. It is fairly simple where we just take a vector from the last frame to this frame then divide it by `Time.deltaTime` but we do want to project this onto a plane. The reason being is because we don't want any changes vertically to affect any of our calculations. In the diagram, `body.right` and `body.forward` are two coplanar vectors that lie on the plane we project the vector `body.position - prevBodyPos` onto.

<img src="/static/images/devlogs/spider/Raw Velocity Diagram.png">

This value isn't very stable and just one frame drop can cause it to jitter out of control. We need to take this into account and apply some smoothing. To do this, we can use a simple lerp between the current value of the velocity and `rawVelocity`. Using `velocitySmoothSpeed` we can fine-tune this in real-time in the editor.

All of this velocity calculation stuff is just so we can computer our `t` value used in calculating the `stepTime`, `leadDist` and both `leanAngles`. To finish off this calculation, we divide the magnitude of the current velocity by the theoretical max, normalizing this value between $0$ and $1$. Of course it still can go over if the spider's velocity is higher than the theoretical max so we just need to clamp this value. Lastly we just plug this clamped value into our `t` curve and scale it accordingly.

##### Velocity-Based Calculations

The `t` value we just calculated is to be plugged into a lerp with the two values to get a middle value. It's important that `t` does not exceed `1` and does not go below `0` or it might not match the values you plugged into the equation. 

#### Finishing Lines

```csharp
UpdateLegGroup(leftLegs, 0);
UpdateLegGroup(rightLegs, 1);

prevBodyPos = body.position;
```

The first two lines of this section do a whole bunch of stuff and calculations that I'll talk about [later](#UpdateLegGroup()). The last line just updates `prevBodyPos` since the value isn't used after this line.

### User Defined Functions

#### UpdateLegGroup()

#### UpdateLegPosition()

#### InterpolateLeg()

#### CalculateBodyPosition()

#### CalculateBodyTilt()

#### legsInitialized()

