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
        world = World(game)
        world.run()
        for role in self.roles:
            print_role_result(role, world.state)

    def run_proba(self, *strategies):
        game = ProbabilisticGame(self, strategies)
        # This is where I may want to make several forks.
        for world, proba in game.iter_worlds():
            print "Proba:", proba
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
            world = World(sub_game)
            world.run()
            return world.state in allowed_states

    def random(self, choice_probas):
        # 1) ask for a fork
        pass

class ProbabilisticGame(Game):
    def __init__(self, rules, strategies):
        self.rules = rules
        self.strategies = strategies
        self.function = rules.function
        self.agents = {}
        for i, role in enumerate(rules.roles):
            self.agents[role.choicevar] = Agent(role, strategies[i])
        self.done = False
        self.index = 0
        self.needed = []
        self.playback = []
        self.current = []
        self.current_proba = 1.0

    def reset(self):
        self.current = []
        self.index = 0
        self.current_proba = 1.0
        if len(self.needed) > 0:
            self.playback = self.needed.pop()
            self.done = False
        else:
            self.done = True

    def random(self, choice_probas):
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
            self.function(world)
            yield world, self.current_proba
            self.reset()


class World:
    def __init__(self, game, state={}):
        self.game = game
        self.state = dict(state)

    def get(self, var):
        if var not in self.state:
            agent = self.game.agents[var]
            self.state[var] = agent.get_choice(self)
        return self.state[var]

    def __setitem__(self, var, val):
        self.state[var] = val

    def run(self):
        self.game.function(self)

    def __str__(self):
        return str(self.state)


