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



### Body Tilt Calculation



# Full Script Explanation

For the sake of simplicity (and not writing documentation for my second order dynamics system), I will use the spider controller that uses linear interpolation instead.

## Variables

### The Leg Class

This class has quite a bit of variables and this is stored per leg:

```csharp
public Transform pivot;
public Transform groundTarget;
public ThreeLinkV2 leg;

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

## Personal Working Script

This uses Odin so the editor stuff won't quite work unless you have it installed. It also uses some stuff using a second order dynamics system so replace it with another interpolation method (i.e. lerp) if need be.

```csharp
using ProceduralAnimation.Runtime.Dynamics;
using Sirenix.OdinInspector;
using System.Collections;
using Unity.Profiling;
using Unity.VisualScripting.YamlDotNet.Core.Tokens;
using UnityEngine;

namespace ProceduralAnimation.Runtime {
    /// <summary>
    /// Body controller of a spider with an even number of legs.
    /// </summary>
    /// <remarks>
    /// MINIMUM 4 LEGS
    /// <======== Hierarchy Setup ========>
    /// Parent (Spider)
    ///     - Body
    ///         - Pivots
    ///         - Ground Targets
    ///     - Legs
    /// <======== Other Conditions ========>
    /// Legs in each of the lists "leftLegs" and "rightLegs" 
    /// must be setup in order (front to back).
    /// <============ Features ============>
    /// If the spider rests for a specified amount of time but
    /// the leg's end effector's distance to the target is less
    /// than minDelta, it will correct itself.
    /// </remarks>
    public class SpiderController : MonoBehaviour {
        [System.Serializable]
        public class Leg {
            [Tooltip("The shoulder transform")] public Transform pivot;
            [Tooltip("The target where the leg's end effector should land")] public Transform groundTarget;
            [Tooltip("The reference to the three link solver")] public ThreeLinkV2 leg;
            [HideInInspector] public bool initialized = false; //   self-explanatory

            //  Used for calculating the interpolated positions
            [HideInInspector] public Vector3 startPosition; //  The start interpolation position
            [HideInInspector] public Vector3 targetPosition; // The end interpolation position
            [HideInInspector] public SecondOrderDynamics positionFilter; // Filter for position calculations

            [HideInInspector] public Vector3 startUp; //    The start interpolation up vector
            [HideInInspector] public Vector3 targetUp; //   The end interpolation vector
            [HideInInspector] public SecondOrderDynamics upFilter; //   Filter for up vector calculations

            [HideInInspector] public float restTimer; //    Internal timer to check whether to snap back to rest position
            [HideInInspector] public float startInterpolationTime; //   What time it started moving
            [HideInInspector] public bool isStepping = false; //    If it is currently being moved by any filters. Used to prevent more than one filter

            [HideInInspector] public Vector3 rawUp; //  Used for distance based rotation

            //  Distance based rotation is always applied but velocity is only applied when moving
            [HideInInspector] public Quaternion skewRotation;
        }

        [Title("Cosmetic Settings")]
        [Tooltip("This controls how much higher than the centre of leg heights it is "), FoldoutGroup("Float Parameters"), SerializeField] float distToLegCentre = 0.5f;

        [Title("Raycast Settings")]
        [Tooltip("Should be set to anything the spider can walk on"), FoldoutGroup("Float Parameters"), SerializeField] LayerMask groundMask;
        [Tooltip("Half is above the ground target and the other half is below"), FoldoutGroup("Float Parameters"), SerializeField, MinValue(0)] float maxRaycastDist = 5f;
        [Tooltip("Refer to Features section in the summary of this class"), FoldoutGroup("Float Parameters"), SerializeField, MinValue(0)] float minDelta = 0.25f;
        [Tooltip("Max distance before it takes a step"), FoldoutGroup("Float Parameters"), SerializeField, MinValue(0)] float maxDelta = 2f;

        [Title("Smoothing Settings")]
        [Tooltip("The speed that it lerps the tilt"), FoldoutGroup("Float Parameters"), SerializeField, MinValue(0)] float bodyTiltLerpSpeed = 10f;
        [Tooltip("The speed that it lerps the tilt"), FoldoutGroup("Float Parameters"), SerializeField, MinValue(0)] float velocitySmoothSpeed = 2f;

        [FoldoutGroup("Body Settings"), SerializeField] Transform body;
        [FoldoutGroup("Body Settings"), SerializeField] Transform legParent;

        [Tooltip("The curve that the t value is evaluated for velocity based variables"), FoldoutGroup("Velocity-Based Settings"), SerializeField]
        AnimationCurve tVelocityCurve
            = AnimationCurve.EaseInOut(0, 0, 1, 1);
        [Tooltip("Used to calculate the offset for ground targets and also the dynamic step time. If this spider is controlled by a script, set it to the run speed."), FoldoutGroup("Velocity-Based Settings"), SerializeField, MinValue(0)] float theoreticalMaxVelocity = 15f;
        [Tooltip("How long each step takes"), FoldoutGroup("Velocity-Based Settings"), SerializeField, MinMaxSlider(0, 2, true)] Vector2 legStepTime = new Vector2(0.05f, 0.25f);
        [Tooltip("How much to rotate the legs closest to the velocity's direction forward"), FoldoutGroup("Velocity-Based Settings"), SerializeField, MinMaxSlider(0, 90, true)] Vector2 maxFrontLegsLeanAngle = new Vector2(15F, 30f);
        [Tooltip("How much to rotate the legs furthest to the velocity's direction forward"), FoldoutGroup("Velocity-Based Settings"), SerializeField, MinMaxSlider(0, 90, true)] Vector2 maxHindLegsLeanAngle = new Vector2(30f, 45f);
        [Tooltip("How far to offset the hind legs forwards and front legs backwards"), FoldoutGroup("Velocity-Based Settings"), SerializeField] float maxLeadDist = 3f;


        //  These are used for calculating the coefficients for the interpolation used in moving the body
        [Title("Body Interpolation Settings")]
        [FoldoutGroup("Body Settings"), SerializeField, InlineEditor(InlineEditorObjectFieldModes.Hidden)] SecondOrderSettings bodyPosSettings;
        [FoldoutGroup("Body Settings"), HideIf("@bodyPosSettings == null"), Button("Remove Scriptable Object Reference")] void RemoveBodySettings() { bodyPosSettings = null; }
        [FoldoutGroup("Leg Settings"), SerializeField] Leg[] leftLegs;
        [FoldoutGroup("Leg Settings"), SerializeField] Leg[] rightLegs;

        [Title("Leg Step Settings")]
        [Tooltip("Step height over time. Must start and at (0, 0) and end at (1, 0)."), FoldoutGroup("Leg Settings"), SerializeField]
        AnimationCurve legStepHeightCurve
            = new AnimationCurve(new Keyframe(0, 0), new Keyframe(0.5f, 1), new Keyframe(1, 0));

        [Title("Leg Lean Settings")]
        [FoldoutGroup("Leg Settings"), SerializeField] float legRotSmoothSpeed = 10f;

        [Title("Other Leg Settings")]
        [Tooltip("How long before moving to rest position (refer to minDelta)"), FoldoutGroup("Leg Settings"), SerializeField, MinValue(0)] float timeBeforeRest = 0.5f;

        //  These are used for calculating the coefficients for the interpolation used in moving the legs
        [Title("Leg Interpolation Settings")]
        [FoldoutGroup("Leg Settings"), SerializeField, InlineEditor(InlineEditorObjectFieldModes.Hidden)] SecondOrderSettings legSettings;
        [FoldoutGroup("Leg Settings"), HideIf("@legSettings == null"), Button("Remove Scriptable Object Reference")] void RemoveLegSettings() { legSettings = null; }

        /// <summary>
        /// When showDebugTools is on, the lines are as follows:
        ///     White lines - the diagonal lines from the furthest legs projected onto the xz plane
        ///     Green Lines - the diagonal lines but unprojected
        ///     Cyan Lines - Raycast calculated using groundTarget and its up vector. Also shows hit.point and the normal
        ///     Magenta Lines - Raycast calculated using the other hit.point and the direction from pivot to it. Also shows hit.point and the normal
        ///     
        /// At the center of the body transform, there are 5 lines:
        ///     Non-white lines - the normal vector of the plane made from 3 of the leg joints
        ///     White Line - the average of all these lines
        /// </summary>
        [FoldoutGroup("Debug"), SerializeField] bool showBodyDebugTools;
        [FoldoutGroup("Debug"), SerializeField] bool showLegDebugTools;
        [FoldoutGroup("Debug"), SerializeField] bool showRaycastDebugTools;
        [Tooltip("If it is grounded (can be improved but im too lazy)"), FoldoutGroup("Debug"), ShowIf("showLegDebugTools"), ShowInInspector, ReadOnly] bool onGround;
        [Tooltip("Number of steps in this group"), FoldoutGroup("Debug"), ShowIf("showLegDebugTools"), ShowInInspector, ReadOnly] int numSteps = 0;
        [Tooltip("Number of steps completed by the group"), FoldoutGroup("Debug"), ShowIf("showLegDebugTools"), ShowInInspector, ReadOnly] int stepsCompleted = 0;
        [Tooltip("If group one is moving or not. Group one is arbitrary up to the setup."), FoldoutGroup("Debug"), ShowIf("showLegDebugTools"), ShowInInspector, ReadOnly] bool groupOneMoving;
        [Tooltip("Magnitude of velocity"), FoldoutGroup("Debug"), ShowIf("showBodyDebugTools"), ShowInInspector, ReadOnly] float vMag;
        [Tooltip("The interpolated step time and lead distance"), FoldoutGroup("Debug"), ShowIf("showLegDebugTools"), ShowInInspector, ReadOnly] float stepTime, leadDist;
        [Tooltip("The interpolated front lean angle and hind lean angle"), FoldoutGroup("Debug"), ShowIf("showLegDebugTools"), ShowInInspector, ReadOnly] float frontLeanAngle, hindLeanAngle;

        SecondOrderDynamics positionFilter; //  Filter for interpolating the body's position

        //  Used in body calculations
        Transform rf, rr, lf, lr;
        Vector3 prevBodyPos;
        Vector3 rawVelocity, velocity;

        void Start() {
            //  Define points for body calculations
            rf = rightLegs[0].leg.joints[1].jointOrigin;
            rr = rightLegs[^1].leg.joints[1].jointOrigin;

            lf = leftLegs[0].leg.joints[1].jointOrigin;
            lr = leftLegs[^1].leg.joints[1].jointOrigin;

            velocity = Vector3.zero;
        }

        void Update() {
            // Global Position 0'd so that IKTargets don't move with the body
            legParent.position = Vector3.zero;
            legParent.rotation = Quaternion.identity;

            if (legsInitialized()) {
                CalculateBodyPosition();
                CalculateBodyTilt();

                //  Calculate velocity and its magnitude
                rawVelocity = Vector3.ProjectOnPlane((body.position - prevBodyPos) / Time.deltaTime, body.up);

                //  Smooth the velocity so small movements don't set velocity insanely high for no reason
                velocity = Vector3.Lerp(velocity, rawVelocity, Time.deltaTime * velocitySmoothSpeed);
                vMag = velocity.magnitude;

                //  Calculate t value to interpolate between min and max values for velocity based variables (t is the y value of a sigmoid function)
                float t = tVelocityCurve.Evaluate(Mathf.Clamp01(vMag / theoreticalMaxVelocity));

                //  Dynamically change step time, lead distance and lean angle
                stepTime = Mathf.Lerp(legStepTime.y, legStepTime.x, t); //  Swapped the order because faster spider means lower step time

                leadDist = Mathf.Lerp(0, maxLeadDist, t);
                frontLeanAngle = Mathf.Lerp(maxFrontLegsLeanAngle.x, maxFrontLegsLeanAngle.y, t);
                hindLeanAngle = Mathf.Lerp(maxHindLegsLeanAngle.x, maxHindLegsLeanAngle.y, t);
            }

            UpdateLegGroup(leftLegs, 0);
            UpdateLegGroup(rightLegs, 1);

            prevBodyPos = body.position;
        }

        /// <summary>
        /// Updates a group of legs iteratively. Moves the raycast targets and checks the distances between them.
        /// </summary>
        /// <param name="legGroup">Leg group to be updated.</param>
        /// <param name="legGroup">Offset used in alternating legs. Whichever one has an offset of 0 has priority of first leg movement.</param>
        void UpdateLegGroup(Leg[] legGroup, int offset) {
            for (int i = 0; i < legGroup.Length; i++) {
                Leg leg = legGroup[i];
                leg.leg.transform.position = leg.pivot.position;

                //  Create an offset using the velocity's direction and the lead distance
                Vector3 groundPos = leg.groundTarget.position + velocity.normalized * leadDist;

                //  Shoot raycast at desired location straight down
                RaycastHit hit;
                onGround = Physics.Raycast(groundPos + leg.groundTarget.up *
                    maxRaycastDist / 2, -leg.groundTarget.up, out hit, maxRaycastDist, groundMask);

                //  Calculate distance from raycast hit point and target's position
                float dist = Vector3.Distance(hit.point, leg.leg.target.position);

                if (leg.initialized) {
                    //  Vector to rotate velocityLean around and used to calculate the dot product to make sure distance based rotation isn't being weird
                    Vector3 orthoVelocity = Vector3.Cross(velocity.normalized, body.up).normalized;

                    //  Get max lean angle by interpolating between the max front and max hind leg lean angle
                    float dot = Vector3.Dot(velocity.normalized, Vector3.ProjectOnPlane(leg.leg.target.position - leg.pivot.position, body.up).normalized);

                    //  Lerp using how parallel the velocity is with the vector given from the target to the pivot
                    float maxLeanAngle = Mathf.Lerp(hindLeanAngle, frontLeanAngle, (dot + 1) / 2);

                    //  Lean angle calculated using distance
                    float distanceLean = -maxLeanAngle * Mathf.Clamp01(dist / maxDelta);

                    //  Make Quaternion
                    leg.skewRotation = Quaternion.Slerp(leg.skewRotation, Quaternion.AngleAxis(distanceLean, orthoVelocity), Time.deltaTime * legRotSmoothSpeed);

                    //  Apply rotation
                    leg.leg.target.up = leg.skewRotation * leg.rawUp;

                    // Debug Controls
                    if (showRaycastDebugTools) {
                        Debug.DrawRay(leg.groundTarget.position + leg.groundTarget.up * maxRaycastDist / 2, -leg.groundTarget.up * maxRaycastDist, Color.cyan);

                        //  Ground Target Vector
                        Debug.DrawRay(groundPos, hit.normal);
                    }

                    if (showLegDebugTools) {
                        //  Rotation vectors
                        Debug.DrawRay(leg.leg.target.position, body.up, Color.green);
                        Debug.DrawRay(leg.leg.target.position, orthoVelocity, Color.red);
                        Debug.DrawRay(leg.leg.target.position, velocity.normalized, Color.blue);
                    }
                }

                if (leg.isStepping || (groupOneMoving != (i % 2 == offset) && leg.initialized))
                    continue;

                //  Start leg end effector interpolation
                if ((onGround && dist > maxDelta) || !leg.initialized
                || (leg.restTimer < 0f && Vector3.Distance(hit.point, leg.leg.target.position) > minDelta))
                    UpdateLegPosition(leg, hit.point, hit.normal);

                //  Decrease leg's rest timer, clamp so that it doesn't break if player somehow waits past the negative float limit
                leg.restTimer -= leg.restTimer < 0 ? 0 : Time.deltaTime;
            }
        }

        /// <summary>
        /// Moves a leg's end effector towards a point using a second order system.
        /// </summary>
        /// <param name="leg">Leg to be moved.</param>
        /// <param name="pos">Position to be moved to.</param>
        /// <param name="normal">Ground normal.</param>
        void UpdateLegPosition(Leg leg, Vector3 pos, Vector3 normal) {
            //  Initialize the leg
            if (!leg.initialized) {
                //  Place legs onto ground
                leg.leg.target.position = pos;
                leg.leg.target.up = -normal;
                leg.rawUp = -normal;

                //  Create SecondOrderDynamics classes
                leg.positionFilter = new SecondOrderDynamics(legSettings, leg.leg.target.position);
                leg.upFilter = new SecondOrderDynamics(legSettings, leg.leg.target.up);

                //  Zero out Quaternions
                leg.skewRotation = Quaternion.identity;

                leg.initialized = true;
                return;
            }

            if (!leg.isStepping) {
                //  Reset rest timer if taking a step
                leg.restTimer = timeBeforeRest;

                //  Set initial conditions for interpolation
                leg.startInterpolationTime = Time.time;
                leg.startPosition = leg.leg.target.position;
                leg.startUp = leg.leg.target.up;

                //  Set target conditions
                leg.targetPosition = pos;
                leg.targetUp = -normal;

                leg.rawUp = -normal;

                //  Ensure that legs won't lerp again once started
                leg.isStepping = true;

                //  Counter for alternating steps
                numSteps++;

                StartCoroutine(InterpolateLeg(leg));
            }
        }

        /// <summary>
        /// The loop that moves the leg using a second order system. (This can be changed to lerp if needed)
        /// </summary>
        /// <param name="leg">Leg to be moved.</param>
        IEnumerator InterpolateLeg(Leg leg) {
            float t = 0f; //    Timer for each step [0, 1]
            float localStepTime = stepTime;

            while (t < 1f) {
                //  Calculate t for lerping
                t = Mathf.Min(1f, (Time.time - leg.startInterpolationTime) / localStepTime);

                //  Add height to each step using sin
                float height = legStepHeightCurve.Evaluate(t);

                //  Calculate target position
                Vector3 targetPos = Vector3.Lerp(leg.startPosition, leg.targetPosition, t) + body.up * height;

                //  Calculate the target's up vector
                Quaternion startRot = Quaternion.LookRotation(leg.leg.target.forward, leg.startUp);
                Quaternion endRot = Quaternion.LookRotation(leg.leg.target.forward, leg.targetUp);

                Quaternion rot = Quaternion.Slerp(startRot, endRot, t);

                Vector3 targetUp = rot * Vector3.up;

                //  Apply filters then apply to target transform
                leg.leg.target.position = leg.positionFilter.Update(Time.deltaTime, targetPos);
                leg.leg.target.up = leg.upFilter.Update(Time.deltaTime, targetUp);

                yield return null;
            }

            //  Check whether the group is done with their step to move to the next group
            if (++stepsCompleted >= numSteps) {
                groupOneMoving = !groupOneMoving;
                stepsCompleted = 0;
                numSteps = 0;
            }

            leg.isStepping = false;
        }

        /// <summary>
        /// Calculates the body's height using the positions of its legs and then moves it using a second order system.
        /// </summary>
        void CalculateBodyPosition() {
            //  Define projected points
            Vector3 p1 = Vector3.ProjectOnPlane(lf.position, body.up);
            Vector3 p2 = Vector3.ProjectOnPlane(rr.position, body.up);

            Vector3 q1 = Vector3.ProjectOnPlane(rf.position, body.up);
            Vector3 q2 = Vector3.ProjectOnPlane(lr.position, body.up);

            //  Calculate t value to solve for points on other lines
            float t = ((q1.x - p1.x) * (q2.z - q1.z) - (q1.z - p1.z) * (q2.x - q1.x)) / ((p2.x - p1.x) * (q2.z - q1.z) - (p2.z - p1.z) * (q2.x - q1.x));

            float x = p1.x + t * (p2.x - p1.x);
            float z = p1.z + t * (p2.z - p1.z);

            //  Calculate t values per vector for the non-projected points
            float pT = (x - lf.position.x) / (rr.position - lf.position).x;
            float qT = (x - rf.position.x) / (lr.position - rf.position).x;

            float pY = (rr.position - lf.position).y * pT + lf.position.y;
            float qY = (lr.position - rf.position).y * qT + rf.position.y;

            float desiredY = (pY + qY) / 2 + distToLegCentre;
            Vector3 targetPos = Vector3.up * desiredY;

            //  Create Second Order Dynamics Instance
            if (positionFilter == null)
                positionFilter = new SecondOrderDynamics(bodyPosSettings, targetPos);

            //  Turn off when raycast doesn't hit ground
            Vector3 desiredPos = positionFilter.Update(Time.deltaTime, targetPos);

            if (onGround)
                body.localPosition = desiredPos;

            if (showBodyDebugTools) {
                Debug.DrawRay(new Vector3(x, 0, z), Vector3.up, Color.red);
                Debug.DrawRay(q1, q2 - q1);
                Debug.DrawRay(p1, p2 - p1);

                Debug.DrawRay(rf.position, lr.position - rf.position, Color.green);
                Debug.DrawRay(lf.position, rr.position - lf.position, Color.green);
            }
        }

        /// <summary>
        /// Calculates the tilt of the body using all possible normals of the four furthest legs.
        /// </summary>
        void CalculateBodyTilt() {
            //  Calculate normals for all possible planes formed by the four points
            Vector3 norm1 = Vector3.Cross(lf.position - rf.position, rr.position - rf.position).normalized;
            Vector3 norm2 = Vector3.Cross(rf.position - rr.position, lr.position - rr.position).normalized;
            Vector3 norm3 = Vector3.Cross(rr.position - lr.position, lf.position - lr.position).normalized;
            Vector3 norm4 = Vector3.Cross(lr.position - lf.position, rf.position - lf.position).normalized;

            //  Average vectors to use as the normal vector of the plane
            Vector3 avg = (norm1 + norm2 + norm3 + norm4) / 4;

            //  Get the forward vector of the body on the plane
            Vector3 bodyForward = Vector3.ProjectOnPlane(body.forward, avg).normalized;

            //  Apply the rotation onto the body
            Quaternion rotation = Quaternion.LookRotation(bodyForward);
            body.rotation = Quaternion.Slerp(body.rotation, rotation, Time.deltaTime * bodyTiltLerpSpeed);

            if (showBodyDebugTools) {
                Debug.DrawRay(body.position, norm1, Color.yellow);
                Debug.DrawRay(body.position, norm2, Color.red);
                Debug.DrawRay(body.position, norm3, Color.green);
                Debug.DrawRay(body.position, norm4, Color.blue);

                Debug.DrawRay(body.position, avg);
            }
        }

        /// <summary>
        /// Checks if all legs are initialized.
        /// </summary>
        /// <returns>False if any legs aren't initialized, otherwise true.</returns>
        bool legsInitialized() {
            foreach (Leg l in leftLegs) if (!l.initialized) return false;
            foreach (Leg r in rightLegs) if (!r.initialized) return false;
            return true;
        }
    }
}
```





