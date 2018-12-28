import argparse
from LearningGame import LearningGame as LG
from ValueIterGame import ValueIterGame as VIG
from freegames import vector as v
from copy import deepcopy
import traceback

def q1():
    g = VIG(True, "value")
    point = 0
    try:
        for i in range(10):
            while g.end_game() == 0:
                qs = g.nextstate("sim_pac", g.pacman.will_move(g.valid, g.state), g.state)
                g.pacman.position = qs["pacman_pos"]
                g.state = qs
                ns = g.nextstate("sim_ghost", g.ghosts[0].will_move(g.valid, g.state), g.state)
                g.ghosts[0].position = ns["ghost1_pos"]
                g.state = ns
            if g.end_game() == 2:
                point += 1
            print("Game %d score: %d" % (i + 1, g.state["score"]))
            g.initialize()
            g.reposition_agents()
    except:
        traceback.print_exc()
    score = v(point, 10)
    print_score(score, "question 1")
    print("")
    return score

def q2():
    g = VIG(True, "policy")
    point = 0
    try:
        for i in range(10):
            while g.end_game() == 0:
                qs = g.nextstate("sim_pac", g.pacman.will_move(g.valid, g.state), g.state)
                g.pacman.position = qs["pacman_pos"]
                g.state = qs
                ns = g.nextstate("sim_ghost", g.ghosts[0].will_move(g.valid, g.state), g.state)
                g.ghosts[0].position = ns["ghost1_pos"]
                g.state = ns
            if g.end_game() == 2:
                point += 1
            print("Game %d score: %d" % (i + 1, g.state["score"]))
            g.initialize()
            g.reposition_agents()
    except:
        traceback.print_exc()
    score = v(point, 10)
    print_score(score, "question 2")
    print("")
    return score

def q3():
    g = LG(True, "rein")
    point = 0
    try:
        for i in range(10):
            while g.end_game() == 0:
                qs = g.nextstate("sim_pac", g.pacman.will_move(g.valid, g.state))
                g.pacman.position = qs["pacman_pos"]
                ns = g.nextstate("sim_ghost_best_Q")
                g.ghosts[0].position = ns["ghost1_pos"]
            if g.end_game() == 2:
                point += 1
            print("Game %d score: %f" % (i + 1, g.state["score"]))
            g.initialize()
            g.reposition_agents()
    except:
        traceback.print_exc()
    score = v(point, 10)
    print_score(score, "question 3")
    print("")
    return score
    
def print_score(score, question):
    p, t =  score
    print("For %s:" % question)
    print("Your score is %d/%d." % (p, t))

def main():
    score = 0
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--question", help = "Which question to evaluate the score.")
    args = parser.parse_args()
    q = args.question
    if q is None:
        score += q1()
        score += q2()
        score += q3()
    elif q == "q1":
        score += q1()
    elif q == "q2":
        score += q2()
    elif q == "q3":
        score += q3()
    else:
        raise ValueError("No such question.")
    print_score(score, "all the questions")

if __name__ == "__main__":
    main()
