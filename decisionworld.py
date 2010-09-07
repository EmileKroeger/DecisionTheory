#####################################################
# Decision theory proto
#
# Copyright (c) 2010 Emile Kroeger
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#####################################################

class Agent:
    def __init__(self, role, strategy):
        self.role = role
        self.strategy = strategy

    def get_choice(self, world):
        if self.role.sees_world:
            return self.strategy(self.role, world.game, dict(world.state))
        else:
            return self.strategy(self.role, world.game)

def print_role_result(role, state):
    print "%s = %s -> %s = %s" % (role.choicevar, str(state[role.choicevar]),
                                  role.utility, str(state[role.utility]))

def print_role_expected_result(role, states_and_probas):
    choice_probas = {}
    expected_utility = 0.0
    utilities = set()
    for state, proba in states_and_probas:
        choice = state[role.choicevar]
        choice_probas[choice] = choice_probas.get(choice, 0.0) + proba
        expected_utility += state[role.utility] * proba
        utilities.add(state[role.utility])
    if len(choice_probas) > 1:
        print "Choices (%s):" % str(role.choicevar),
        for choice in choice_probas:
            percentage = 100.0 * choice_probas[choice]
            if int(percentage) == percentage:
                print "%s (%i%%)" % (str(choice), int(percentage)),
            else:
                print "%s (%.1f%%)" % (str(choice), 100.0 * percentage),
        print
    else:
        choice = choice_probas.keys()[0] # There should be at least 1!
        print "Choice (%s): %s" % (str(role.choicevar), choice)
    if len(utilities) > 1:
        print "Expected utility (%s): %.2f" % (str(role.utility),
                                               expected_utility)
    else:
        print "Utility (%s):" % str(role.utility), str(utilities.pop())

def iter_role_states(role, state):
    state = dict(state)
    if role.choicevar in state:
        yield state
    else:
        for choice in role.choices:
            state[role.choicevar] = choice
            yield dict(state)

class GameRules:
    def __init__(self, function, *roles):
        self.roles = roles
        self.function = function
        # Now would be the right place to do some pre-analysis.
        # On possible outcomes, etc.

    def run(self, *strategies):
        game = Game(self, strategies)
        # This is where I may want to make several forks.
        world = game.run()
        for role in self.roles:
            print_role_result(role, world.state)

    def _iter_outcomes_rec(self, base_state, roles):
        if roles:
            for choice_state in iter_role_states(roles[0], base_state):
                for final_state in self._iter_outcomes_rec(choice_state,
                                                           roles[1:]):
                    yield final_state
        else:
            result = dict(base_state)
            self.function(result)
            yield result

    def iter_possible_outcomes(self, base_state):
        return self._iter_outcomes_rec(base_state, self.roles)

    def get_possible_values(self, var):
        values = set()
        for state in self.iter_possible_outcomes():
            values.add(state[var])
        return values

class ProbaGameRules(GameRules):
    def run(self, *strategies):
        game = Game(self, strategies)
        probagame = ProbabilisticGame(game)
        worlds_and_probas = [(w.state, p) for w, p in probagame.iter_worlds()]
        for role in self.roles:
            print_role_expected_result(role, worlds_and_probas)

class Game:
    def __init__(self, rules, strategies, possible_states=None):
        self.rules = rules
        self.strategies = strategies
        self.function = rules.function
        self.agents = {}
        for i, role in enumerate(rules.roles):
            self.agents[role.choicevar] = Agent(role, strategies[i])
        if possible_states is None:
            possible_states = list(self.rules.iter_possible_outcomes({}))
        self._possible_states = possible_states

    def get_agent_choice(self, var, world):
        return self.agents[var].get_choice(world)

    def is_certain(self, predicate):
        allowed_states = filter(predicate.fulfills, self._possible_states)
        if len(allowed_states) >= len(self._possible_states):
            assert len(allowed_states) == len(self._possible_states)
            return True
        elif len(allowed_states) == 0:
            return False
        else:
            # We need recursion! But under strict control.
            sub_game = Game(self.rules, self.strategies,
                            possible_states=allowed_states)
            world = sub_game.run()
            return world.state in allowed_states

    def random(self):
        assert False, "This game doesn't allow random strategies!"

    def run(self):
        world = World(self)
        self.function(world)        
        return world

class ProbabilisticGame:
    def __init__(self, game):
        self.game = game
        self.done = False
        self.index = 0
        self.needed = []
        self.playback = []
        self.current = []
        self.current_proba = 1.0

    def get_agent_choice(self, var, world):
        choice = self.game.get_agent_choice(var, world)
        if isinstance(choice, dict):
            choice_probas = [(c, choice[c]) for c in choice]
            return self._random(choice_probas)
        else:
            return choice

    def reset(self):
        self.current = []
        self.index = 0
        self.current_proba = 1.0
        if len(self.needed) > 0:
            self.playback = self.needed.pop()
            self.done = False
        else:
            self.done = True

    def is_certain(self):
        return self.game.is_certain

    def _random(self, choice_probas):
        if self.index < len(self.playback):
            choice, proba = self.playback[self.index]
        else:
            choice, proba = choice_probas.pop()
            for pair in choice_probas:
                self.needed.append(list(self.current) + [pair])
        self.index += 1
        self.current.append((choice, proba))
        self.current_proba *= proba
        return choice

    def iter_worlds(self):
        while not self.done:
            world = World(self)
            self.game.function(world)
            yield world, self.current_proba
            self.reset()

class World:
    def __init__(self, game, state={}):
        self.game = game
        self.state = dict(state)

    def get(self, var):
        if var not in self.state:
            self.state[var] = self.game.get_agent_choice(var, self)
        return self.state[var]

    def __setitem__(self, var, val):
        self.state[var] = val

    def __str__(self):
        return str(self.state)


