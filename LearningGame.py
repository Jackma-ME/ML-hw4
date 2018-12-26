from Game import Game
from freegames import floor, vector
import IntelligentAgents as Agents
from copy import deepcopy
from utils import PriorityQueue
from collections import deque
import math

class LearningGame(Game):
    """
    Specialized Game class for reinforcement learning.
    """
    def init_agents(self, pacmanAgent = "key", challenge = False):
        "Initialize agents with respect to the given type (@pacmanAgent)."
        self.ghosts = [Agents.VIRandomGhostAgent(0, self.state['ghost%d_pos' % (i + 1)]) for i in range(1)]
        if pacmanAgent == "key":
            self.pacman = Agents.KeyboardAgent(self.state['pacman_pos'])
            self.pacman.change_speed(2)
        elif pacmanAgent == "rein":
            self.pacman = Agents.ApproximateQLearningAgent(1000, 0.1, 0.7, self, 0.5, self.state['pacman_pos'])
        else:
            print("invalid agent name, use default agent instead (keyboard)")
            self.pacman = Agents.KeyboardAgent(self.state['pacman_pos'])
            self.pacman.change_speed(2)
        if challenge:
            self.ghosts = [Agents.AstarGhostAgent(0, self.state['ghost%d_pos' % (i + 1)]) for i in range(1)]
            self.ghosts[0].change_speed(4)

    def initialize(self):
        "Initialize game state."
        self.tiles = [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
            0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0,
            0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ]
        self.total_food = self.tiles.count(1)
        self.state = {'score': 0, 'pacman_pos': vector(-40, -80),
                            'ghost1_pos': vector(-180, 160),
                            'food_num': self.tiles.count(1),
                            'tiles': self.tiles}

    def move(self):
        "Move pacman and all ghosts, 0.1 discount from the score for every time unit passed."
        super().move()
        self.state['score'] = round(self.state['score'] - 0.1, 1)

    def nextstate(self, agent, param1 = None, param2 = None):
        "Return the updated state for the given @agent and action(@param1, @param2)."
        if agent == "sim_ghost_best_Q": # ghost take the best action from the given Q-state (current state)
            state = self.state
            end = self.end_game()
            if end == 0:
                for i in range(len(self.ghosts)):
                    ghost = self.ghosts[i]
                    temp = ghost.position
                    ghost.position = state['ghost%d_pos' % (i + 1)]
                    aim = self.ghosts[i].will_move(self.valid, self.state)
                    ghost.position = temp
                    state['ghost%d_pos' % (i + 1)] = state['ghost%d_pos' % (i + 1)] + aim
                end = self.end_game()
                if end == 0:
                    state['score'] = round(state['score'] - 0.1, 1)
                elif end == 1:
                    state['score'] -= 200
            return state

        if agent == "sim_pac": # move the pacman due to given action (@param1) from the given state (@param2) or current state if @param2 is not given
            state = self.state if param2 is None else deepcopy(param2)
            tiles = state['tiles']
            aim = param1
            state["pacman_pos"] = state["pacman_pos"] + aim
            index = self.offset(state["pacman_pos"])

            if tiles[index] == 1:
                tiles[index] = 2
                state['score'] += 1
                state['food_num'] -= 1

            end = self.end_game()
            if end == 2:
                state['score'] += 100
            elif end == 1:
                state['score'] -= 200
            return state

        return super().nextstate(agent, param1, param2)

    def valid_moves(self, pos, possible_moves = Agents.LEARNING_MOVES):
        "Return the move vectors (from @possible_moves) which are valid in the tiles at @pos."
        return [n for n, m in possible_moves.items() if self.valid(pos + m) and n != "stop"]

    def Astar_distance(self, chaser_pos, chasee_pos):
        "Calculate the distance between @chaser_pos and @chasee_pos with A* search algorithm."
        pq = PriorityQueue()
        chaser_pos = chaser_pos.copy()
        fringe = set()
        fringe.add(chaser_pos)
        i = 0
        pq.push((0 + Agents.distance(chaser_pos, chasee_pos), 0, i, chaser_pos))
        while True:
            try:
                _, cost, _, cnt_pos = pq.pop()
                if Agents.distance(cnt_pos, chasee_pos) < 20:
                    return cost
                for n in self.valid_moves(cnt_pos):
                    if (cnt_pos + Agents.LEARNING_MOVES[n]) in fringe:
                        continue
                    nxt_pos = cnt_pos + Agents.LEARNING_MOVES[n]
                    fringe.add(nxt_pos)
                    i += 1
                    pq.push((cost + 1 + Agents.distance(nxt_pos, chasee_pos), cost + 1, i, nxt_pos))
            except IndexError:
                break
        return float('inf') # theoretically, it won't reach here

    def BFS(self, chaser_pos, tiles):
        "Calculate the distance between @chaser_pos and closest food from it in the @tiles with BFS algorithm."
        q = deque()
        chaser_pos = chaser_pos.copy()
        fringe = set()
        fringe.add(chaser_pos)
        q.append((0, chaser_pos))
        while True:
            try:
                cost, cnt_pos = q.popleft()
                if tiles[self.offset(cnt_pos)] == 1:
                    return cost
                for n in self.valid_moves(cnt_pos):
                    if (cnt_pos + Agents.LEARNING_MOVES[n]) in fringe:
                        continue
                    nxt_pos = cnt_pos + Agents.LEARNING_MOVES[n]
                    fringe.add(nxt_pos)
                    q.append((cost + 1, nxt_pos))
            except IndexError:
                break
        return 0

    def near_ghosts(self, cgds):
        "Calculate how many ghosts are in the neighborhood of pacman."
        return sum(cgd <= 2 for cgd in cgds)

    def features(self, state = None, action = None):
        "Return feature names (if no arguments is given) or the features of the given Q-state (@state, @action)"
        if state is None:
            return ["bias", "closest_food_dist", "eats_food", "#_of_ghosts_near"]
        else:
            features = {}
            cgds = [self.Astar_distance(state["pacman_pos"] + action, state["ghost%d_pos" % (i + 1)]) for i in range(len(self.ghosts))]
            features["bias"] = 1.0
            cfd = self.BFS(state["pacman_pos"] + action, state["tiles"])
            features["closest_food_dist"] = cfd / len(self.tiles)
            features["#_of_ghosts_near"] = self.near_ghosts(cgds) / len(self.ghosts)
            if not self.near_ghosts(cgds) and state["tiles"][self.offset(state["pacman_pos"] + action)] == 1:
                features["eats_food"] = 1.0
            return features

    def end_game(self, state = None):
        """
        Return if a game (in @state) is ended.
        @Return: 1 for losing, 2 for winning, 0 for not ended
        """
        state = self.state if state is None else state
        for i in range(len(self.ghosts)):
            if Agents.distance(state["pacman_pos"], state['ghost%d_pos' % (i + 1)]) < 20:
                return 1
        if state["food_num"] == 0:
            return 2
        return 0

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pacmanAgent", help = "specify which agent to be used as the pacman agent (key/value/policy)")
    parser.add_argument("-c", "--challenge", help = "whether to challenge a smarter ghost.", action = "store_true", default = False)
    args = parser.parse_args()
    g = LearningGame(False, args.pacmanAgent, args.challenge)
    g.main()

if __name__ == "__main__":
    main()
