from freegames import vector
from random import choice, uniform, seed
from copy import deepcopy
from utils import PriorityQueue
import math

seed(42)

# defining move vectors.
MOVES = {
    'up': vector(0, 5),
    'left': vector(-5, 0),
    'down': vector(0, -5),
    'right': vector(5, 0),
    'stop': vector(0, 0)
}

LEARNING_MOVES = {n: m * 4 for n, m in MOVES.items()}

def distance(v1, v2):
    "Calculate the euclidean distance between v1 and v2."
    return abs(v1 - v2)

class Agent():
    """
    Base Agent class representing characters in the game.
    """
    def __init__(self, position):
        self.position = position.copy()
        self.possible_moves = MOVES

    def valid_moves(self, pos, valid):
        "Return the move vectors which are valid in the tiles at @pos."
        return [n for n, m in self.possible_moves.items() if valid(pos + m) and n != "stop"]
    
    def change_speed(self, ratio):
        "Change the move vectors by the given @ratio."
        self.possible_moves = {n: m * ratio for n, m in self.possible_moves.items()}

    def best_chase(self, chaser_pos, chasee_pos, valid):
        "Calculate the best action to take when chasing from @chaser_pos to @chasee_pos with A* search algorithm."
        pq = PriorityQueue()
        chaser_pos = chaser_pos.copy()
        fringe = set()
        fringe.add(chaser_pos)
        i = 0
        pq.push((0 + distance(chaser_pos, chasee_pos), 0, i, chaser_pos, []))
        while True:
            try:
                _, cost, _, cnt_pos, moves = pq.pop()
                if distance(cnt_pos, chasee_pos) < 20:
                    return moves[0]
                for n in self.valid_moves(cnt_pos, valid):
                    if (cnt_pos + self.possible_moves[n]) in fringe:
                        continue
                    nxt_pos = cnt_pos + self.possible_moves[n]
                    fringe.add(nxt_pos)
                    nmoves = moves.copy()
                    nmoves.append(n)
                    i += 1
                    pq.push((cost + 1 + distance(nxt_pos, chasee_pos), cost + 1, i, nxt_pos, nmoves))
            except IndexError:
                break
        return "stop" # theoretically, it won't reach here

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given state."
        raise NotImplementedError

    def move(self, valid, state):
        "Move this agent using the result of self.will_move."
        m = self.will_move(valid, state)
        if valid(self.position + m):
            self.position.move(m)

class PacmanAgent(Agent):
    """
    Abstract class for pacman agents.
    """
    def if_keyboard(self):
        "Return if this is a keyboard agent."
        raise NotImplementedError

class KeyboardAgent(PacmanAgent):
    """
    Pacman agent class for playing using keyboard.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.aim = self.possible_moves['stop']

    def if_keyboard(self):
        "Return if this is a keyboard agent."
        return True

    def change_aim(self, valid, name):
        "Change aiming direction when pressing arrow keys."
        if valid(self.position + self.possible_moves[name]):
            self.aim = self.possible_moves[name] * 2

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given state."
        if valid(self.position + self.aim):
            return self.aim
        else:
            return self.possible_moves['stop']

class GhostAgent(Agent):
    """
    Base ghost agent class and always takes action that minimize euclidean distance.
    """
    def __init__(self, i, *args):
        super().__init__(*args)
        self.i = i

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given state."
        "Minimize euclidean distance."
        minn = ''
        mind = float('inf')
        for n in self.valid_moves(self.position, valid):
            m = self.possible_moves[n]
            d = distance(state['pacman_pos'], self.position + m)
            if d < mind:
                minn = n
                mind = d
        return self.possible_moves[minn]

class AstarGhostAgent(GhostAgent):
    """
    Ghost agent class that always chases pacman with A* search.
    """
    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given state."
        "A* search."
        return self.possible_moves[self.best_chase(self.position, state['pacman_pos'], valid)]

class VIRandomGhostAgent(GhostAgent):
    """
    Value iteration ghost agent class that is used in the MDP algorithm.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.possible_moves = LEARNING_MOVES # move one entire grid at one time, which makes MDP states easier to define.

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given state."
        "0.8 of the time: A* search, 0.2 of the time: randomly pick others."
        vms = self.valid_moves(self.position, valid)
        P = uniform(0, 1)
        minn = self.best_chase(self.position, state['pacman_pos'], valid)
        if P > 0.8 and len(vms) > 1:
            vms.remove(minn)
            return self.possible_moves[choice(vms)]
        else:
            return self.possible_moves[minn]

class UXGhostAgent(GhostAgent):
    """
    Ghost agent class that aim to enhance user experience, based on the truly used method in original Pacman Game.
    There're two modes this ghost has, chase and spread:
        chase: chasing pacman with A* search
        spread: going to the assigned corner of this ghost with A* search
    And it frequently switching bewteen these two modes.
    """
    def __init__(self, game, *args):
        super().__init__(*args)
        self.mode = "chase"
        self.change_to = "spread"
        self.move_in_mode = {
            "chase": self.chasing,
            "spread": self.spreading
        }
        self.duration = {
            "chase": 20,
            "spread": 40
        }
        self.game = game
        self.counter = 0

    def spread_corner(self, state):
        "Where to go when in spread mode."
        if self.position == self.game.corners[self.i]:
            self.mode = "chase"
            return state['pacman_pos']
        else:
            return self.game.corners[self.i]
    
    def change_mode(self):
        "Change the mode if time has passed for a specific duration."
        self.counter += 1
        if self.counter == self.duration[self.change_to]:
            self.counter = 0
            self.mode = self.change_to 
            self.change_to = "chase" if self.change_to == "spread" else "spread"

    def chasing(self, valid, state):
        "Action to take in chase mode."
        return self.best_chase(self.position, state['pacman_pos'], valid)

    def spreading(self, valid, state):
        "Action to take in spread mode."
        return self.best_chase(self.position, self.spread_corner(state), valid)

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given state."
        return self.possible_moves[self.move_in_mode[self.mode](valid, state)]