import random
import math
from collections import Counter
from typing import List, Optional

MAX_CHILDREN_PER_NODE = 1000 #maxed at 1000 children
UCB1_C = math.sqrt(2)  

# Structure Stages 
PRE_FLOP = 'root'   # known hands
PRE_OPP  = 'opp'    # 2 cards
PRE_FLOP_BOARD = 'flop'  #flop 3 cards
PRE_TURN = 'turn'   # turn 4 cards
PRE_RIVER = 'river' # river 5 cards


SUITS = ["club", "heart", "spade", "diamond"] #suits
RANKS = [f"{i:2d}" for i in range(2, 15)]  # 11 - Jack , 12 - Queen, 13 - King, 14 - Ace

def make_deck():
    return [f"{r}{s}" for r in RANKS for s in SUITS] #format to print as rank(#) and then suit type 

class Deck:
    def __init__(self, deck=None): #starts deck
        self.deck = list(deck) if deck else make_deck()

    def draw_cards(self, n):#draws random cards from the deck 
        drawn = random.sample(self.deck, n)
        for card in drawn:
            self.deck.remove(card)
        return drawn

    def copy_deck(self):
        return Deck(self.deck) #copy of the deck 

def rank_of(card: str): #rank # is the first two 
    return int(card[:2])

def suit_of(card: str): #suit after rank
    return card[2:]

def evaluate(total_cards: List[str]):
    ranks = [rank_of(c) for c in total_cards] #evauates the 5 best of 7 
    suits = [suit_of(c) for c in total_cards]
    rc = Counter(ranks)
    uniq = sorted(rc.keys(), reverse=True)

    # checking for a flush 
    suit_card = Counter(suits)
    flush_suit = None
    for suit, cnt in suit_card.items():
        if cnt >= 5: #same suit 5+ times
            flush_suit = suit
            break

    def straight_top(vals: List[int]): #5 ranks in a row 
        unit = sorted(set(vals), reverse=True)
        if 14 in unit:
            unit.append(1)  #makes ace lowest
        run = 1
        for u in range(len(unit) - 1):
            if unit[u] - 1 == unit[u+1]:
                run += 1
                if run >= 5:
                    return unit[u - 3]
            elif unit[u] != unit[u+1]:
                run = 1
        return None

    #checking straight flush
    if flush_suit is not None:
        straight_flush = [r for r, s in zip(ranks, suits) if s == flush_suit]
        st = straight_top(straight_flush)
        if st is not None:
            return [8, st]

    #four of a kind
    fours = [r for r, cnt in rc.items() if cnt == 4]
    if fours:
        four = max(fours)
        next_highest = [r for r in uniq if r != four]
        return [7, four, next_highest[0]]

    #full house
    triplets = sorted([r for r, cnt in rc.items() if cnt == 3], reverse=True) # looks for 3 of a kind 
    pairs = sorted([r for r, cnt in rc.items() if cnt == 2], reverse=True) # two of a kind 
    if triplets:
        if len(triplets) >= 2:
            return [6, triplets[0], triplets[1]] # then full house
        if pairs:
            return [6, triplets[0], pairs[0]]

    #straight
    straight = straight_top(uniq) #looks for a straight 
    if straight is not None:
        return [4, straight]

    #two pair
    if len(pairs) >= 2:
        p1, p2 = pairs[:2]
        next_highest = max([r for r in uniq if r not in (p1, p2)])
        return [2, p1, p2, next_highest]
    if len(pairs) == 1: # one pair 
        p = pairs[0]
        nh = [r for r in uniq if r != p][:3]
        return [1, p] + nh

    #determine high card
    top5 = uniq[:5]
    return [0] + top5

def compare_cards(handof7: List[str], opp7: List[str]): #compare hands 
    hand = evaluate(handof7)
    opp = evaluate(opp7)
    if hand > opp:
        return 1.0
    if hand == opp: #tie 
        return 0.5
    return 0.0

class Node: #structure for MCT
    #initializing
    def __init__(self, parent, deck: Deck, world: List[str], stage: str, max_children=MAX_CHILDREN_PER_NODE):
        self.parent = parent
        self.deck = deck
        self.world = list(world)
        self.stage = stage
        self.children: List["Node"] = []
        self.visited: List[List[str]] = []  # list of tried child
        self.max_children = max_children
        self.wins = 0.0
        self.sim = 0

    def is_terminal(self):
        return self.stage == PRE_RIVER # check the pre river stage 

    def count_ofcards(self):
        if self.stage == PRE_FLOP:
            return 2   # opponent card
        if self.stage == PRE_OPP:
            return 3   # flop community 
        if self.stage == PRE_FLOP_BOARD:
            return 1   # turn community 
        if self.stage == PRE_TURN:
            return 1   # river community 
        return 0

    def child_stage(self): #next stage
        if self.stage == PRE_FLOP:
            return PRE_OPP
        if self.stage == PRE_OPP:
            return PRE_FLOP_BOARD
        if self.stage == PRE_FLOP_BOARD:
            return PRE_TURN
        if self.stage == PRE_TURN:
            return PRE_RIVER
        return PRE_RIVER

    def remaining_cards(self, hand: List[str]): #unused cards 
        used = set(hand) | set(self.world)
        p = self
        while p is not None:
            if p.stage == PRE_OPP:
                used |= set(p.world[:2])
                break
            p = p.parent
        return [c for c in self.deck.deck if c not in used]

    def children_atNode(self, hand: List[str]): #caclc for children @ node
        rem = self.remaining_cards(hand)
        need = self.count_ofcards()
        if need == 0:
            return 0
        if need == 1:
            return len(rem)
        if need == 2:
            from math import comb
            return comb(len(rem), 2)
        if need == 3:
            from math import comb
            return comb(len(rem), 3)
        return 0

    def random_child(self, hand: List[str]): # combo for children 
        total = self.children_atNode(hand)
        cap = min(self.max_children, total)
        if len(self.visited) >= cap:
            return None

        remain = self.remaining_cards(hand)
        need = self.count_ofcards()
        for _ in range(3000):
            pick = sorted(random.sample(remain, need))
            if pick not in self.visited:
                self.visited.append(pick)
                return pick
        return None

    def expand_one_child(self, hand: List[str]):#expand a child node
        if self.is_terminal():
            return None
        content = self.random_child(hand)
        if content is None:
            return None

        child_deck = self.deck.copy_deck()  #copy and remove the unneeded 
        for c in content:
            if c in child_deck.deck:
                child_deck.deck.remove(c)

        if self.stage == PRE_FLOP: #create child node
            child_world = content              # opp
        elif self.stage == PRE_OPP:
            child_world = content              # flop
        else:
            child_world = self.world + content # turn & river

        child = Node(self, child_deck, child_world, self.child_stage(), self.max_children)
        self.children.append(child)
        return child

    def ucb1_child(self, c: float): #UCB1 strat + math 
        unvisited = [ch for ch in self.children if ch.sim == 0] #unviisted nodes 
        if unvisited:
            return random.choice(unvisited)
        if not self.children:
            return None
        lnN = math.log(self.sim) if self.sim > 0 else 0.0
        best, best_val = None, -1e18
        for ch in self.children:
            exploit = ch.wins / ch.sim
            explore = c * math.sqrt(lnN / ch.sim)
            val = exploit + explore
            if val > best_val:
                best_val = val
                best = ch
        return best

def recon_opponent(node: Node, hand: List[str]): # get opp hand 
    p = node
    while p is not None:
        if p.stage == PRE_OPP:
            return p.world[:2]
        p = p.parent
    remain = node.remaining_cards(hand)
    return random.sample(remain, 2)

def recon_board(node: Node):
    if node.stage == PRE_OPP or node.stage == PRE_FLOP:
        return []
    if node.stage == PRE_FLOP_BOARD:
        return node.world[:3]
    if node.stage == PRE_TURN:
        return node.world[:4]
    if node.stage == PRE_RIVER:
        return node.world[:5]
    return []

def rollout_from(node: Node, hand: List[str]): #running a rollot from river to get result 
    opp = recon_opponent(node, hand)
    board = recon_board(node)
    used = set(hand) | set(opp) | set(board)
    remain = [c for c in make_deck() if c not in used]
    need = 5 - len(board) # how many cards needed 
    if need > 0:
        draw = random.sample(remain, need)
        board = board + draw #add to the board 
    return compare_cards(hand + board, opp + board)

def mcts(root: Node, hand: List[str], c: float = UCB1_C, max_sims: int = 10000):
    wins = 0.0
    sims = 0
    while sims < max_sims:
        node = root
        path = [node]

        #selection 
        while not node.is_terminal():
            # only expand if there is space 
            can_expand = (len(node.visited) <
                          min(node.max_children, node.children_atNode(hand)))
            if can_expand: #add child if can 
                child = node.expand_one_child(hand)
                if child is not None:
                    node = child
                    path.append(node)
                    break  
            #if can't expand select ucb1 child 
            nxt = node.ucb1_child(c)
            if nxt is None:
                break
            node = nxt
            path.append(node)

       #simulation 
        if node.is_terminal():
            opp = recon_opponent(node, hand)
            board = recon_board(node)
            result = compare_cards(hand + board, opp + board)
        else:
            result = rollout_from(node, hand)

    

       # back propagation (keeping track)
        for nd in path:
            nd.sim += 1
            nd.wins += result
            
        wins += result
        sims += 1  

    return wins / sims if sims > 0 else 0.0, wins, sims #estimated win probablity 

def print_stats(wins: float, sims: int, label: str):
    pct = 100.0 * wins / sims if sims else 0.0
    print(f"{label} estimated win probability: {pct:.2f}%") #printing out the win probability 
def game():
    deck = Deck()
    hand = deck.draw_cards(2)
    opponent = deck.draw_cards(2)
    for c in opponent: deck.deck.append(c)

    print(f"Preflop Deck: {hand}")

    # Pre-flop
    est, win, sim = mcts(Node(None, deck, [], PRE_FLOP, MAX_CHILDREN_PER_NODE), hand, max_sims=10000)
    print_stats(win, sim, "Pre-flop")

    # Flop
    flop = deck.draw_cards(3)
    print(f"Flop community cards: {flop}")
    flop_deck = deck.copy_deck()
    for c in flop:
        if c in flop_deck.deck: flop_deck.deck.remove(c)
    est, win, sim = mcts(Node(None, flop_deck, flop, PRE_FLOP_BOARD, MAX_CHILDREN_PER_NODE), hand, max_sims=10000)
    print_stats(win, sim, "Flop")

    # Turn
    turn = deck.draw_cards(1)
    turn_world = flop + turn
    print(f"Turn community cards: {turn_world}")
    turn_deck = deck.copy_deck()
    for c in turn:
        if c in turn_deck.deck: turn_deck.deck.remove(c)
    est, win, sim = mcts(Node(None, turn_deck, turn_world, PRE_TURN, MAX_CHILDREN_PER_NODE), hand, max_sims=10000)
    print_stats(win, sim, "Turn")

    # River
    river = deck.draw_cards(1)
    river_world = turn_world + river
    print(f"River community cards: {river_world}")
    river_deck = deck.copy_deck()
    for c in river:
        if c in river_deck.deck: river_deck.deck.remove(c)
    est, win, sim = mcts(Node(None, river_deck, river_world, PRE_RIVER, MAX_CHILDREN_PER_NODE), hand, max_sims=10000)
    print_stats(win, sim, "River")

if __name__ == "__main__":
    game()