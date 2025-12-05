# DISC-013: Animation Distribution Strategy - Sharing URLs

## Base URL
https://quoted.it.com/demo-promo

## UTM-Tagged URLs for Distribution

### Reddit Posts
**r/contractors**
```
https://quoted.it.com/demo-promo?utm_source=reddit&utm_campaign=contractors_demo
```

**r/smallbusiness**
```
https://quoted.it.com/demo-promo?utm_source=reddit&utm_campaign=smallbiz_demo
```

**r/Entrepreneur**
```
https://quoted.it.com/demo-promo?utm_source=reddit&utm_campaign=entrepreneur_demo
```

### Facebook Groups
**Contractor Groups**
```
https://quoted.it.com/demo-promo?utm_source=facebook&utm_campaign=contractor_groups
```

**Small Business Groups**
```
https://quoted.it.com/demo-promo?utm_source=facebook&utm_campaign=smallbiz_groups
```

### Twitter/X
```
https://quoted.it.com/demo-promo?utm_source=twitter&utm_campaign=demo_video
```

### LinkedIn
```
https://quoted.it.com/demo-promo?utm_source=linkedin&utm_campaign=contractor_demo
```

### Email Signature
```
https://quoted.it.com/demo-promo?utm_source=email&utm_campaign=signature
```

### YouTube Video Description
```
https://quoted.it.com/demo-promo?utm_source=youtube&utm_campaign=video_description
```

## Pre-Written Social Copy

### Reddit Post Template (r/contractors)
**Title:** "Built a tool to turn voice notes into professional quotes in 60 seconds - watch demo"

**Body:**
```
I got sick of spending 3 hours on quotes for leads that ghosted me, so I built this.

Describe the job out loud (like you're talking to your crew), and it generates a professional PDF quote. Takes about 60 seconds total.

No signup required to watch the demo: [link]

Still in beta - 9 spots left if anyone wants to try it.

Would love feedback from other contractors on what's missing.
```

### Facebook Post Template
```
🎤 Voice to Quote in 60 Seconds

Stop wasting hours on tire-kickers. Watch how contractors are quoting jobs from the truck using just voice.

No signup required to see the demo 👇
[link]

#Contractors #SmallBusiness #Quotes #Efficiency
```

### Twitter/X Thread
```
Tweet 1:
Ever spend 3 hours on a quote for a customer who ghosts you?

I built a tool to fix this. Watch it generate a professional quote from a voice note in 60 seconds:
[link]

Tweet 2:
How it works:
1. Describe the job out loud (like talking to your crew)
2. AI generates structured quote with line items
3. Export PDF or share instantly

No typing. No spreadsheets. No wasted afternoons.

Tweet 3:
Beta is open - 9 spots left. No credit card for trial.

Built for contractors, but works for consultants, designers, freelancers - anyone who prices work.
```

### LinkedIn Post
```
The average contractor spends 6 hours/week writing quotes.

Half of those leads never respond.

I built a tool to solve this: voice-to-quote in 60 seconds.

Describe the job naturally, get a professional PDF quote. No forms, no spreadsheets.

Watch the demo (no signup required): [link]

Still in beta - limited spots available. Would love feedback from the network.

#Contractors #SmallBusiness #Productivity #Efficiency
```

## PostHog Event Tracking

All clicks on `/demo-promo` are tracked with these events:

1. **demo_promo_view** - Page load
   - Captures: `utm_source`, `utm_campaign`

2. **demo_animation_start** - Demo iframe loads
   - Captures: `utm_source`, `utm_campaign`, `page: 'demo-promo'`

3. **demo_promo_cta_click** - CTA button clicked
   - Captures: `utm_source`, `utm_campaign`, `cta_location` (nav/post-demo)

## Attribution Dashboard

View conversion funnel in PostHog:
1. Login to PostHog
2. Navigate to Insights → Funnels
3. Create funnel:
   - Step 1: demo_promo_view
   - Step 2: demo_animation_start
   - Step 3: demo_promo_cta_click
   - Step 4: auth_signup_started (from /app)

4. Group by: `utm_source` and `utm_campaign`

## A/B Testing Variants

Future variants to test:
1. **Headline variations:**
   - Current: "See voice-to-quote in 60 seconds"
   - Test A: "Watch contractors quote jobs from the truck"
   - Test B: "Stop wasting hours on tire-kickers"

2. **CTA variations:**
   - Current: "Try Now" / "Start Free Trial"
   - Test A: "Get Early Access" / "Join Beta"
   - Test B: "Watch Demo" / "See It Work"

3. **Social proof variations:**
   - Current: "9 beta spots left"
   - Test A: "68 contractors already joined"
   - Test B: "Average time saved: 6 hours/week"

## Success Metrics

Track weekly:
- Views: demo_promo_view count
- Engagement: demo_animation_start / demo_promo_view (watch rate)
- Conversion: demo_promo_cta_click / demo_animation_start (interest rate)
- Signups: auth_signup_started / demo_promo_cta_click (signup rate)

Target metrics:
- Watch rate: >60% (60% of visitors watch demo)
- Interest rate: >40% (40% of watchers click CTA)
- Signup rate: >25% (25% of CTA clicks start signup)

**Overall funnel target:** 6% view-to-signup rate
