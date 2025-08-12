# In this assignment, you will build a win probability estimator for Texas Hold’em poker using
# **Monte Carlo Tree Search (MCTS)** with **UCB1** as the selection strategy. Your bot
# will estimate the probability of winning based solely on its two pre-flop hole cards.
# MCTS builds a search tree where each node corresponds to a partially revealed poker
# world (e.g., opponent cards, flop, turn, river). UCB1 will guide the exploration of this tree
# to more promising branches over time.
# You will compare your estimated probabilities against a provided table of known pre-flop
# win rates.
# Figure 1: Preflop winrates
# Simplified Game Model
# • Players: 2 (your bot vs. one opponent).
# • No betting or folding: All hands are played to showdown.
# • Single Decision Point: Estimate win probability pre-flop based on your two hole
# cards.
# • Hidden Information:
# 1
# – Opponent’s hole cards.
# – All 5 community cards (flop, turn, river).
# • Win Condition: The player with the best 5-card hand at showdown wins.
# Estimator Requirements
# Your estimator must:
# • Accept your two hole cards as input.
# • Implement Monte Carlo Tree Search with:
# – Selection: Use UCB1 to choose child nodes:
# UCB1(i) = wi
# ni
# + c ·
# r ln N
# ni
# where wi is the number of wins, ni is the number of simulations for child i, N is
# the number of simulations for the parent, and c is an exploration constant (e.g.,√2).
# – Expansion: Limit the number of children at each level to 1000 randomly sam-
# pled unique possibilities (e.g., 1000 opponent hole card combos, 1000 flop com-
# bos, 1000 turn cards, 1000 river cards.).
# – Simulation: Complete random rollouts to the river for unvisited leaf nodes.
# – Backpropagation: Update win/loss statistics up the tree.
# • Perform as many simulations as needed to produce a stable win probability estimate.
# • Output:
# estimated win probability = your wins
# simulations
# • Compare your result to the corresponding value from the provided ground-truth pre-flop
# odds table.
# Tree Structure
# Nodes in your MCTS tree should represent different stages of revealed information:
# • Root: Your two known hole cards.
# • Level 1: 1000 sampled opponent hole card combos.
# • Level 2: 1000 sampled flops (3 cards).
# • Level 3: 1000 sampled turn cards (1 card).
# • Level 4: 1000 sampled river cards (1 card) – Perform full hand evaluation and propagate
# the result.
# 2
# Technical Guidelines
# • Card Representation: Use any format that supports efficient lookup and uniqueness
# checking.
# • Deck Management: Carefully track which cards are already drawn at each node.
# • Hand Evaluation: Implement Texas Hold’em hand ranking, including kickers and
# tiebreaks.
# • Efficiency: Focus on minimizing redundant computations. Consider caching evaluated
# hand scores if needed.
# • Programming Language: Any language is acceptable.
# • From Scratch: All logic, including tree search, UCB1, and hand evaluation, must be
# implemented by you.
# Deliverables
# Submit a link to a public GitHub repository containing:
# • A link to your public repo
# Hints and Best Practices
# • Tree Depth: Always explore down to a full 5-card board (flop + turn + river).
# • Random Sampling: At each node, sample a random subset of 1000 legal children.
# • Selection: use UCB1-guided traversal.
# • Comparison: Your estimator may be off by a few percentage points.