from turtle import *
from freegames import floor, vector
import Agents

SCORE_FONT = ('Times', 8, "bold")
W_L_FONT = ('Times', 48, "normal")

class Game():
    """
    Base Game class for game rules and flows. (Only allow keyboard agent for pacman)
    """
    def __init__(self, auto, *args, **kwargs):
        self.initialize()
        self.init_agents(*args, **kwargs)
        if not auto:
            self.path = Turtle(visible=False)
            self.writer = Turtle(visible=False)

    def init_agents(self):
        "Initialize agents, the speed setting here is more suitable for human playing than other games."
        self.pacman = Agents.KeyboardAgent(self.state['pacman_pos'])
        self.ghosts = []
        for i in range(4):
            self.ghosts.append(Agents.UXGhostAgent(self, i, self.state['ghost%d_pos' % (i + 1)]))

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
        self.state = {'score': 0, 'pacman_pos': vector(-40, -80),
                            'ghost1_pos': vector(-180, 160),
                            'ghost2_pos': vector(-180, -160),
                            'ghost3_pos': vector(100, 160),
                            'ghost4_pos': vector(100, -160),
                            'food_num': self.tiles.count(1)}
        self.corners = [
            vector(-180, 160),
            vector(-180, -160),
            vector(100, 160),
            vector(100, -160)
        ]

    def reposition_agents(self):
        "Reset the position of the agents."
        self.pacman.position = self.state['pacman_pos'].copy()
        for i in range(len(self.ghosts)):
            self.ghosts[i].position = self.state['ghost%d_pos' % (i + 1)].copy()

    def restart(self):
        "Reset game state and settings for another game."
        self.initialize()
        self.path.home()
        self.path.clear()
        self.writer.home()
        self.writer.clear()
        self.reposition_agents()
        hideturtle()
        tracer(False)
        self.writer.goto(160, 160)
        self.writer.color('white')
        self.writer.write(self.state['score'], font = SCORE_FONT)
        self.world()
        self.move()

    def square(self, x, y):
        "Draw square using path at (@x, @y)."
        self.path.up()
        self.path.goto(x, y)
        self.path.down()
        self.path.begin_fill()

        for count in range(4):
            self.path.forward(20)
            self.path.left(90)

        self.path.end_fill()

    def offset(self, point):
        "Return offset of @point in tiles."
        x = (floor(point.x, 20) + 200) / 20
        y = (180 - floor(point.y, 20)) / 20
        index = int(x + y * 20)
        return index

    def cord(self, index):
        "Return coordinate of @index in tiles"
        x = (index % 20) * 20 - 200
        y = 180 - (index // 20) * 20
        return x, y

    def valid(self, point):
        "Return True if @point is valid in tiles."
        index = self.offset(point)

        if self.tiles[index] == 0:
            return False

        index = self.offset(point + 19)

        if self.tiles[index] == 0:
            return False

        return point.x % 20 == 0 or point.y % 20 == 0

    def world(self):
        "Draw world using path."
        bgcolor('black')
        self.path.color('blue')
        for index in range(len(self.tiles)):
            tile = self.tiles[index]
            if tile > 0:
                x, y = self.cord(index)
                self.square(x, y)
                if tile == 1:
                    self.path.up()
                    self.path.goto(x + 10, y + 10)
                    self.path.dot(5, 'white')

    def food_eaten_update(self, index):
        "Update game state due to a eaten food on @index."
        self.tiles[index] = 2
        self.state['score'] += 1
        self.state['food_num'] -= 1

    def move(self):
        "Move pacman and all ghosts."
        self.writer.undo()
        self.writer.write(self.state['score'], font = SCORE_FONT)

        clear()

        self.pacman.move(self.valid, self.state)
        self.state['pacman_pos'] = self.pacman.position.copy()

        index = self.offset(self.pacman.position)

        if self.tiles[index] == 1:
            self.food_eaten_update(index)
            self.square(*(self.cord(index)))

        up()
        goto(self.pacman.position.x + 10, self.pacman.position.y + 10)
        dot(20, 'yellow')

        end = self.end_game()
        if end == 1:
            self.state["score"] -= 200
            self.lose()
            return
        elif end == 2:
            self.state["score"] += 100
            self.win()
            return

        for i, g in enumerate(self.ghosts):
            g.move(self.valid, self.state)
            self.state['ghost%d_pos' % (i + 1)] = g.position.copy()
            point = g.position
            up()
            goto(point.x + 10, point.y + 10)
            dot(20, 'red')

        update()

        end = self.end_game()
        if end == 1:
            self.state["score"] -= 200
            self.lose()
            return
        elif end == 2:
            self.state["score"] += 100
            self.win()
            return

        ontimer(self.move, 100)
        for g in self.ghosts:
            if hasattr(g, "change_mode"):
                g.change_mode()

    def nextstate(self, agent, param1, param2):
        "Return the updated state for the given @agent and action(@param1, @param2)."
        if agent == "none": # deprecated
            return self.state
        else:
            raise KeyError("invalid agent")

    def end_game(self):
        """
        Return if a game is ended.
        @Return: 1 for losing, 2 for winning, 0 for not ended
        """
        for g in self.ghosts:
            if abs(self.pacman.position - g.position) < 20:
                return 1
        if self.state['food_num'] == 0:
            return 2
        return 0

    def lose(self):
        "Output message for losing a game."
        self.writer.undo()
        self.writer.write(self.state['score'], font = SCORE_FONT)
        self.writer.up()
        self.writer.home()
        self.writer.goto(0, -40)
        self.writer.color('red')
        self.writer.write('You Lose!!', align = 'center', font = W_L_FONT)
        if not self.pacman.if_keyboard():
            ontimer(self.restart, 2000)

    def win(self):
        "Output message for winning a game."
        self.writer.undo()
        self.writer.write(self.state['score'], font = SCORE_FONT)
        self.writer.up()
        self.writer.home()
        self.writer.goto(0, -40)
        self.writer.color('yellow')
        self.writer.write('You Win!!', align = 'center', font = W_L_FONT)
        if not self.pacman.if_keyboard():
            ontimer(self.restart, 2000)

    def main(self):
        "Main flow of the game."
        setup(420, 420, 370, 0)
        hideturtle()
        tracer(False)
        self.writer.goto(160, 160)
        self.writer.color('white')
        self.writer.write(self.state['score'], font = SCORE_FONT)
        listen()
        if self.pacman.if_keyboard():
            onkey(lambda: self.pacman.change_aim(self.valid, 'right'), 'Right')
            onkey(lambda: self.pacman.change_aim(self.valid, 'left'), 'Left')
            onkey(lambda: self.pacman.change_aim(self.valid, 'up'), 'Up')
            onkey(lambda: self.pacman.change_aim(self.valid, 'down'), 'Down')
        self.world()
        self.move()
        done()

def main():
    g = Game(False)
    g.main()

if __name__ == "__main__":
    main()
