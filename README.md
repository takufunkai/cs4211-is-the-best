# CS4211 Project Notes

# Purpose of project:

We are supposed to extend the existing tennis model (any 1 of the 3) to predict the outcome of a specific match-up

We can do this by figuring out the probabilities of moves made by 2 specific players. For example, in the tennis data set, we find Tennis Player John and determine the probability that he does a BackHand_Crosscourt deuce stroke, then manually change the probability found in the pcase for deuce stroke.

We can also **extend** the project by keeping track of the last 2 moves made by a player, and use it to improve the accuracy of the probabilities

For mid-term presentation, we just need to

1. do some improvements to the model
2. do a powerpoint presentation to explain our improvements and findings

# Initial strategy

- we can just choose any sport as long as can have some data from somewhere to derive probability values
- probabilities just stay static\*\*, so probabilities are derived from data (take from website that records every move for u or just watch some tennis match lol // since we also need to present how we get our data)

### Extending the project

for the tennis model, we can also go about taking into account 2 previous shots in 2 ways:

1. take into account their current position on the court before their next hit
2. just take note what kind of shot they hit previously (maybe see if got pattern, but this way has alot of permutations 💀)

# Syntax of the PAT language:

- pcase just means probability case
- with prob; just means with probability (we are guessing it just prints the probability of the winning player...?)
