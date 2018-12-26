from Agents import * # extend Agents module and let Game treat this as Agents

class IntelligentAgent(PacmanAgent):
    """
    Abstract pacman agent class moving with AI algorithm.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.possible_moves = LEARNING_MOVES # move one entire grid at one time, which makes MDP states easier to define.

    def if_keyboard(self):
        "Return if this is a keyboard agent."
        return False

class MDPAgent(IntelligentAgent):
    """
    Abstract pacman agent class used to solve MDP.
    """
    def __init__(self, game, gamma, *args):
        super().__init__(*args)
        self.game = game
        self.gamma = gamma # discount factor
        self.initialize()
        try:
            self.load()
        except FileNotFoundError:
            self.plan()
    
    def hash_state(self, state):
        "A helper function for hashing the game state."
        "It's helpful if you use dictionary to store state values."
        state = state.copy()
        state["foods"] = str(state["foods"])
        return frozenset(state.items())

    # --------------------------------------
    # DO NOT CHANGE THE CODE ABOVE THIS LINE
    
    def possible_nextstate(self, state):
        "Yield possible next states (s') and the probability T(s, a, s') from a Q-state Q(s, a)(@state)."
        """
        for a in possible ghost actions from state
            compute s' and T(s, a, s') by self.probability
            yield T(s, a, s'), s'
        """
        "YOUR CODE HERE"
        vms = self.valid_moves(state["ghost1_pos"], self.game.valid)
        for a in vms:
            ns = self.game.nextstate("sim_ghost", self.possible_moves[a], state)
            prob = self.probability(state, a, len(vms))
            yield prob, ns

    def probability(self, Qstate, ghost_action, number_of_valid_ghost_actions):
        "Return the probability for one nextstate (s') given @Qstate and @ghost_action."
        "@number_of_valid_ghost_actions can be used to evaluate the probability."
        """
        0.8 of the time, the ghost goes its [best_chase]. (see Agents.py for more details)
        0.2 of the time, randomly picks actions from the rest valid actions.
        NOTE: If there's only one valid action, ghost takes it with 1 probability.
        """
        "YOUR CODE HERE"
        if number_of_valid_ghost_actions == 1:
            return 1
        best_action = self.best_chase(Qstate["ghost1_pos"], Qstate["pacman_pos"], self.game.valid)
        if best_action == ghost_action:
            return 0.8
        else:
            return 0.2/(number_of_valid_ghost_actions - 1)

    def best_of_state(self, state):
        "Return the best action of the given @state."
        "One of ['stop', 'up', 'down', 'left', 'right']"
        "If there are more than one actions with max Q-value, randomly pick one. (use choice(actions))"
        "YOUR CODE HERE"
        action = self.V[self.hash_state(state)]["action"]
        return action

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given @state."
        """
        To get the corresponding vector of a action (string), use self.possible_moves[action].
        @valid is a function used to check if a position is valid.
        """
        "YOUR CODE HERE"
        action = self.best_of_state(state)
        action_in_vector = self.possible_moves[action]
        return action_in_vector

class ValueIterationAgent(MDPAgent):
    """
    Pacman agent class that constructs a policy of a given world with value iteration before the game starts.
    """
    def load(self):
        "Load model file into this object."
        "It would be convenient if you save the policy into a file so that you don't need to plan again the next time you start a game."
        with open(self.modelfilename, "r") as f:
            self.V = eval(f.read())
            "YOUR CODE HERE (OPTIONAL)"

    def save(self):
        "Save the policy into a model file."
        "It would be convenient if you save the policy into a file so that you don't need to plan again the next time you start a game."
        with open(self.modelfilename, "w") as f:
            f.write(str(self.V))
            "YOUR CODE HERE (OPTIONAL)"

    def initialize(self):
        "Initialize this agent."
        self.modelfilename = "Q1.txt" # replace this if you implement the save & load methods
        "PLACE ANY INITIALIZATION CODE THAT YOU NEED HERE"
        "And you probably wanna initialize the data structure storing state values and policy here."
        self.V = {self.hash_state(s): {"value": 0, "action": "stop"} for s in self.game.allstates()}
        
    def iteration(self):
        "Update the state values (probably also policy) with one step look ahead."
        """
        new_V(s) <- Max(a)[Sigma(s')[T(s, a, s') x (R(s, a, s') + gamma x old_V(s'))]]
        new_P(s) <- ArgMax(a)[Sigma(s')[T(s, a, s') x (R(s, a, s') + gamma x old_V(s'))]]
        get all possible states by self.game.allstates()
        NOTE: A state or a Q-state might be an end state under our assumption for this game.
            You can check that by self.game.end_game(state), and in those cases, there will be no s'.
        """
        "@Return: total difference of the state values for convergence checking."
        old_V = deepcopy(self.V)
        delta = 0
        for s in self.game.allstates():
            if self.game.end_game(s) == 1:
                delta = delta + abs(-200 - old_V[self.hash_state(s)]["value"])
                self.V[self.hash_state(s)]["value"] = -200
                continue
            elif self.game.end_game(s) == 2:
                delta = delta + abs(100 - old_V[self.hash_state(s)]["value"])
                self.V[self.hash_state(s)]["value"] = 100
                continue
            V = 0
            n = 0
            action = "stop"
            for a in self.valid_moves(s["pacman_pos"], self.game.valid):
                V_new = 0
                Qstate = self.game.nextstate("sim_pac", self.possible_moves[a], s)
                if self.game.end_game(Qstate) == 0:
                    for prob, s_new in self.possible_nextstate(Qstate):
                        R = s_new["score"] - s["score"]
                        V_new = V_new + prob*(R + self.gamma*old_V[self.hash_state(s_new)]["value"])
                elif self.game.end_game(Qstate) == 1:
                    R = -200
                    V_new = V_new + 1*(R + self.gamma*old_V[self.hash_state(Qstate)]["value"])
                elif self.game.end_game(Qstate) == 2:
                    R = 100
                    V_new = V_new + 1*(R + self.gamma*old_V[self.hash_state(Qstate)]["value"])
                if n == 0:
                    V = V_new
                    action = a
                    n = n + 1
                elif V_new >= V:
                    V = V_new
                    action = a
            delta = delta + abs(V - old_V[self.hash_state(s)]["value"])
            self.V[self.hash_state(s)]["value"] = V
            self.V[self.hash_state(s)]["action"] = action
        return delta

    def plan(self):
        "Construct the policy from the information given by self.game."
        """
        Run one iteration
        See if it converges
        If so, stop; else, run another iteration
        """
        "YOUR CODE HERE"
        i = 1
        delta = self.iteration()
        print(i," ",delta)
        while delta > 0.01 and i < 100:
            i = i + 1
            delta = self.iteration()
            print(i," ",delta)
        self.save() # save the resulted policy into a file (optional)

class PolicyIterationAgent(MDPAgent):
    """
    Pacman agent class that constructs a policy of a given world with policy iteration before the game starts.
    """
    def load(self):
        "Load model file into this object."
        "It would be convenient if you save the policy into a file so that you don't need to plan again the next time you start a game."
        with open(self.modelfilename, "r") as f:
            self.V = eval(f.read())
            "YOUR CODE HERE (OPTIONAL)"

    def save(self):
        "Save the policy into a model file."
        "It would be convenient if you save the policy into a file so that you don't need to plan again the next time you start a game."
        with open(self.modelfilename, "w") as f:
            f.write(str(self.V))
            "YOUR CODE HERE (OPTIONAL)"


    def initialize(self):
        "Initialize this agent."
        self.modelfilename = "Q2.txt" # replace this if you implement the save & load methods
        "PLACE ANY INITIALIZATION CODE THAT YOU NEED HERE"
        "And you probably wanna initialize the data structure storing state values and policy here."
        self.V = {self.hash_state(s): {"value": 0, "action": "up"} for s in self.game.allstates()}

    def policyevaluation(self):
        "Evaluate the state value due to the current policy."
        """
        new_V(s) <- Sigma(s')[T(s, a_pi, s') x (R(s, a_pi, s') + gamma x old_V(s'))]
        get all possible states by self.game.allstates()
        NOTE: A state or a Q-state might be an end state under our assumption for this game.
            You can check that by self.game.end_game(state), and in those cases, there will be no s'.
        """
        "YOUR CODE HERE"
        old_V = deepcopy(self.V)
        for s in self.game.allstates():
            if self.game.end_game(s) == 1:
                self.V[self.hash_state(s)]["value"] = -200
                continue
            elif self.game.end_game(s) == 2:
                self.V[self.hash_state(s)]["value"] = 100
                continue
            a = old_V[self.hash_state(s)]["action"]
            check = 0
            for valid_a in self.valid_moves(s["pacman_pos"], self.game.valid):
                if valid_a == a:
                    check = 1
                    break
            if check == 0:
                pa = self.valid_moves(s["pacman_pos"], self.game.valid)
                a = pa[0]
            Qstate = self.game.nextstate("sim_pac", self.possible_moves[a], s)
            V_new = 0
            if self.game.end_game(Qstate) == 1:
                R = -200
                V_new = V_new + 1*(R + self.gamma*old_V[self.hash_state(Qstate)]["value"])
            elif self.game.end_game(Qstate) == 2:
                R = 100
                V_new = V_new + 1*(R + self.gamma*old_V[self.hash_state(Qstate)]["value"])
            else:
                for prob, s_new in self.possible_nextstate(Qstate):
                    R = s_new["score"] - s["score"]
                    V_new = V_new + prob*(R + self.gamma*old_V[self.hash_state(s_new)]["value"])
            self.V[self.hash_state(s)]["value"] = V_new
            
    def policyextraction(self):
        "Extract the policy from the updated state values by self.policyextraction."
        """
        new_P(s) <- ArgMax(a)[Sigma(s')[T(s, a, s') x (R(s, a, s') + gamma x V(s'))]]
        get all possible states by self.game.allstates()
        NOTE: A state or a Q-state might be an end state under our assumption for this game.
            You can check that by self.game.end_game(state), and in those cases, there will be no s'.
        """
        "@Return: whether the policy's different from the last one for convergence checking."
        "YOUR CODE HERE"
        old_action = deepcopy(self.V)
        temp = 0
        for s in self.game.allstates():
            if self.game.end_game(s) == 1:
                temp = temp + 1
                continue
            elif self.game.end_game(s) == 2:
                temp = temp + 1
                continue
            n = 0
            V = 0
            action = "stop"
            for a in self.valid_moves(s["pacman_pos"], self.game.valid):
                V_new = 0
                Qstate = self.game.nextstate("sim_pac", self.possible_moves[a], s)
                if self.game.end_game(Qstate) == 1:
                    R = -200
                    V_new = V_new + 1*(R + self.gamma*old_action[self.hash_state(Qstate)]["value"])
                elif self.game.end_game(Qstate) == 2:
                    R = 100
                    V_new = V_new + 1*(R + self.gamma*old_action[self.hash_state(Qstate)]["value"])
                else:
                    for prob, s_new in self.possible_nextstate(Qstate):
                        R = s_new["score"] - s["score"]
                        V_new = V_new + prob*(R + self.gamma*old_action[self.hash_state(s_new)]["value"])
                if n == 0:
                    V = V_new
                    action = a
                    n = n + 1
                elif V_new >= V:
                    V = V_new
                    action = a
            self.V[self.hash_state(s)]["action"] = action
            if action == old_action[self.hash_state(s)]["action"]:
                temp = temp + 1
            else:
                change = False
        print(temp)
        if temp == 9216:
            print(temp)
            change = True
        return change

    def iteration(self):
        "Update the policy with one step look ahead."
        "You don't need to modify the code here in most cases, but you are allowed to."
        self.policyevaluation()
        return self.policyextraction()

    def plan(self):
        "Construct the policy from the information given by self.game."
        """
        Run one iteration
        See if it converges
        If so, stop; else, run another iteration
        """
        "YOUR CODE HERE"
        i = 1
        change = self.iteration()
        print(i," ",change)
        while change == False and i < 100:
            i = i + 1
            change = self.iteration()
            print(i," ",change)
        self.save() # save the resulted policy into a file (optional)

class LearningAgent(IntelligentAgent):
    """
    Abstract pacman agent class for reinforcement learning.
    """
    def __init__(self, num_episodes, alpha, epsilon, game, gamma, *args):
        super().__init__(*args)
        self.num_episodes = num_episodes
        self.alpha = alpha # learning rate
        self.epsilon = epsilon # exploration rate
        self.game = game
        self.gamma = gamma # discount factor
        self.initialize()
        try:
            self.load()
        except FileNotFoundError:
            self.learn()

    # --------------------------------------
    # DO NOT CHANGE THE CODE ABOVE THIS LINE
    
    def best_of_state(self, state):
        "Return the best action of the given @state."
        "One of ['stop', 'up', 'down', 'left', 'right']"
        "If there are more than one actions with max Q-value, randomly pick one. (use choice(actions))"
        "YOUR CODE HERE"
        return action

    def will_move(self, valid, state):
        "Return the action (move vector) this agent will take in the given @state."
        """
        To get the corresponding vector of a action (string), use self.possible_moves[action]
        @valid is a function used to check if a position is valid.
        """
        "YOUR CODE HERE"
        return action_in_vector

class ApproximateQLearningAgent(LearningAgent):
    def load(self):
        "Load model file into this object."
        "It would be convenient if you save the policy into a file so that you don't need to plan again the next time you start a game."
        raise FileNotFoundError # !!remove this if you implement this method!!
        with open(self.modelfilename, "rb") as f:
            "YOUR CODE HERE (OPTIONAL)"
            pass # !!remove this if you implement this method!!

    def save(self):
        "Save the policy into a model file."
        "It would be convenient if you save the policy into a file so that you don't need to plan again the next time you start a game."
        with open(self.modelfilename, "wb") as f:
            "YOUR CODE HERE (OPTIONAL)"
            pass # !!remove this if you implement this method!!

    def initialize(self):
        "Initialize this agent."
        self.modelfilename = "ANY NAME YOU WANT" # replace this if you implement the save & load methods
        "PLACE ANY INITIALIZATION CODE THAT YOU NEED HERE"
        "And you probably wanna initialize the data structure storing weights here."
        "You can use self.game.features() to get all the feature names."

    def get_Qvalue(self, state, action):
        "Evaluate the value of a Qstate Q(@state, @action)."
        """
        Use self.game.features(state, action) to get the features. (stored in a dictionary)
        Inner product of weights and features is the desired Qvalue.
        """
        "YOUR CODE HERE"
        return Qvalue

    def get_value(self, state):
        "Evaluate the value of a @state."
        """
        Max(a)[Q(s, a)]
        """
        "YOUR CODE HERE"
        return value

    def updateWeights(self, diff, features):
        "Update the weights with given @diff and @features"
        """
        new_W <- old_W + gamma x diff x features (NOTE: new_W, old_W, and features are vectors)
        """
        "YOUR CODE HERE"
        pass # !!remove this if you implement this method!!

    def learn(self):
        "Learn the weights by actually playing the game."
        """
        Use self.game.initialize() to initialize the game state.
        Use uniform(0, 1) to randomly generate a number in (0, 1], and choice(actions) to randomly pick an action.
        Run self.num_episode times:
            While a game is not ended:
                Take action
                    (With epsilon probability, the pacman randomly takes a valid action.
                     With (1-epsilon) probability, it takes the best action given by self.best_of_state.)
                Get the reward and resulted state
                Compute diff in order to update the weights
            Initialize the game state
        """
        "YOUR CODE HERE"
        self.save() # save the resulted weights into a file (optional)
