from Game import Game
from freegames import floor, vector
import IntelligentAgents as Agents
from copy import deepcopy

class ValueIterGame(Game):
    """
    Specialized Game class for MDP value iteration and policy iteration.
    """
    def init_agents(self, pacmanAgent = "key", evil = False):
        "Initialize agents with respect to the given type (@pacmanAgent)."
        if pacmanAgent == "key":
            self.pacman = Agents.KeyboardAgent(self.state['pacman_pos'])
            self.pacman.change_speed(2)
        elif pacmanAgent == "value":
            self.pacman = Agents.ValueIterationAgent(self, 0.5, self.state['pacman_pos'])
        elif pacmanAgent == "policy":
            self.pacman = Agents.PolicyIterationAgent(self, 0.5, self.state['pacman_pos'])
        else:
            print("invalid agent name, use default agent instead (keyboard)")
            self.pacman = Agents.KeyboardAgent(self.state['pacman_pos'])
            self.pacman.change_speed(2)
        if evil:
            self.ghosts = [Agents.AstarGhostAgent(0, self.state['ghost1_pos'])]
            self.ghosts[0].change_speed(4)
        else:
            self.ghosts = [Agents.VIRandomGhostAgent(0, self.state['ghost1_pos'])]
    
    def initialize(self):
        "Initialize game state."
        self.tiles = [
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 2, 2, 2, 2, 2, 2, 2, 0,
            0, 2, 0, 0, 1, 0, 0, 2, 0,
            0, 2, 1, 0, 0, 0, 1, 2, 0,
            0, 2, 0, 0, 1, 0, 0, 2, 0,
            0, 2, 2, 2, 2, 2, 2, 2, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0,
        ]
        self.foods = [vector(0, 0), vector(0, 40), vector(-40, 20), vector(40, 20)]
        self.state = {'score': 0, 'pacman_pos': vector(0, -20),
                            'ghost1_pos': vector(0, 60),
                            'food_num': self.tiles.count(1),
                            'foods': self.foods}

    def offset(self, point):
        "Return offset of point in tiles."
        x = (floor(point.x, 20) + 80) / 20
        y = (80 - floor(point.y, 20)) / 20
        index = int(x + y * 9)
        return index

    def cord(self, index):
        "Return coordinate of index in tiles"
        x = (index % 9) * 20 - 80
        y = 80 - (index // 9) * 20
        return x, y

    def nextstate(self, agent, param1, param2):
        "Return the updated state for the given @agent and action(@param1, @param2)."
        if agent == "sim_pac": # move the pacman due to given action (@param1) from the given state (@param2)
            state = deepcopy(param2)
            aim = param1
            state["pacman_pos"] = state["pacman_pos"] + aim
            index = self.offset(state	["pacman_pos"])

            tiles = self.tiles.copy()
            for ef in (f for f in self.foods if f not in state["foods"]):
                tiles[self.offset(ef)] = 2

            if tiles[index] == 1:
                state['score'] += 1
                state['food_num'] -= 1
                state['foods'].remove(vector(*self.cord(index)))

            end = self.end_game(state)
            if end == 2:
                state['score'] += 100
            if end == 1:
                state['score'] -= 200
            return state

        if agent == "sim_ghost": # move the ghost due to given action (@param1) from the given Qstate (@param2)
            state = deepcopy(param2)
            aim = param1
            state["ghost1_pos"] = state["ghost1_pos"] + aim
            index = self.offset(state["ghost1_pos"])
            
            end = self.end_game(state)
            if end == 1:
                state['score'] -= 200
            return state

        return super().nextstate(agent, param1, param2)

    def food_eaten_update(self, index):
        "Update game state due to a eaten food on @index."
        super().food_eaten_update(index)
        self.state['foods'].remove(vector(*self.cord(index)))

    def end_game(self, state = None):
        """
        Return if a game (in @state) is ended.
        @Return: 1 for losing, 2 for winning, 0 for not ended
        """
        state = self.state if state is None else state
        if abs(state["pacman_pos"] - state["ghost1_pos"]) < 20:
            return 1
        if state["food_num"] == 0:
            return 2
        return 0

    def allstates(self):
        "Return all possible states in this game setting."
        posb_poses = [idx for idx in range(len(self.tiles)) if self.tiles[idx] > 0]
        for pc_idx in posb_poses:
            for gh_idx in posb_poses:
                for fd in range(16):
                    foods = []
                    for i in range(4):
                        if (fd >> i) % 2 == 1:
                            foods.append(self.foods[i])
                    food_num = len(foods)
                    score = 4 - food_num
                    if pc_idx == gh_idx:
                        score -= 200
                    elif food_num == 0:
                        score += 100
                    yield {"score": score, "pacman_pos": vector(*self.cord(pc_idx)), "ghost1_pos": vector(*self.cord(gh_idx)), "foods": foods, "food_num": len(foods)}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pacmanAgent", help = "specify which agent to be used as the pacman agent (key/value/policy)")
    parser.add_argument("-e", "--evil", help = "whether to fight the evil.", action = "store_true", default = False)
    args = parser.parse_args()
    g = ValueIterGame(False, args.pacmanAgent, args.evil)
    g.main()

if __name__ == "__main__":
    main()
