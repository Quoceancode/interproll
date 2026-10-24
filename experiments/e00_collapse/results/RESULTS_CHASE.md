# e00 — Chase's interpretation

_Written by Chase. Claude does not write in this file. Facts: `RESULTS_FACTS.md`. Compare with
`RESULTS_AGENT_INTERPRETATION.md` only after finishing this file._

**Date started:**
**Date finished:**

## 1. The metrics
- What does D measure, and why isn't a spread-out forecast automatically skilled?
- What does a daily rank IC of 0.02 mean in practice? How would you explain it to someone outside finance?
- Why use a moving-block bootstrap instead of an ordinary bootstrap over days?
- What does the Holm correction protect against here, and what does it not cover?
- What does Ties detect that D does not?

## 2. The verdicts
- Did any arm collapse under the pre-registered rule? Does that answer the question you care about?
- What does the A−B IC gap tell you, and what doesn't it?
- Is H1 confirmed? What would you need to say so without hedging?
- Why was H2 falsified?
- What does the per-year breakdown add beyond the full-period numbers?

## 3. The exploratory checks
- How should A's IC be compared with the reversal and momentum baselines?
- What could explain the opposite signs of corr(forecast, −r_t) for A and B?
- Why are the predictive intervals for A and B so narrow, and what would change your mind about the cause?
- What does it mean that trailing volatility predicts |r| at least as well as the models' spread?

## 4. Weaknesses
- Which design choices most limit what e00 can claim?
- What would you change in the pre-registration if you ran it again?

## 5. Conclusions and next steps
- What is your one-paragraph conclusion from e00?
- What should e01 test first, and what result would falsify it?

## 6. After comparing with the agent interpretation
- Where do you disagree, and why?
- What did you see that it missed, or vice versa?
