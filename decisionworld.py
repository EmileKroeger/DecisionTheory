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
    chosen = ["%s = %s" % (var, str(state[var])) for var in role.choicevars]
    print ", ".join(chosen),
    if hasattr(role, "utility"):
        print "-> %s = %s" % (role.utility, str(state[role.utility]))
    else:
        print

def print_role_expected_result(role, states_and_probas):
    for choicevar in role.choicevars:
        choice_probas = {}
        for state, proba in states_and_probas:
            if choicevar in state:
                choice = state[choicevar]
                choice_probas[choice] = choice_probas.get(choice, 0.0) + proba
        if len(choice_probas) > 1:
            print "Choices (%s):" % str(choicevar),
            for choice in choice_probas:
                percentage = 100.0 * choice_probas[choice]
                if int(percentage) == percentage:
                    print "%s (%i%%)" % (str(choice), int(percentage)),
                else:
                    print "%s (%.1f%%)" % (str(choice), percentage),
            print
        elif choice_probas:
            choices = choice_probas.keys()
            print "Choice (%s): %s" % (str(choicevar), choices[0])
        else:
            print "Choice (%s): Never encountered" % str(choicevar)
    if hasattr(role, "utility"):
        expected_utility = 0.0
        utilities = set()
        for state, proba in states_and_probas:
            expected_utility += state[role.utility] * proba
            utilities.add(state[role.utility])
        if len(utilities) > 1:
            print "Expected utility (%s): %.2f" % (str(role.utility),
                                                   expected_utility)
        else:
            print "Utility (%s):" % str(role.utility), str(utilities.pop())

def _iter_choice_states(choices, state, choicevars):
    if choicevars:
        choicevar = choicevars[0]
        for substate in _iter_choice_states(choices, state, choicevars[1:]):
            if choicevar in substate:
                yield substate
            else:
                for choice in choices:
                    substate[choicevar] = choice
                    yield dict(substate)
    else:
        yield state

def iter_role_states(role, state):
    state = dict(state)
    return _iter_choice_states(role.choices, dict(state), role.choicevars)

class GameRules:
    def __init__(self, function, *roles):
        for role in roles:
            if not hasattr(role, "choicevars"):
                role.choicevars = [role.choicevar]
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
            yield base_state

    def iter_possible_outcomes(self, base_state):
        for choice_state in self._iter_outcomes_rec(base_state, self.roles):
            result = dict(choice_state)
            self.function(result)
            yield result

    def extrapolate_possible_outcomes(self, base_state):
        return self.iter_possible_outcomes(base_state)

    def get_possible_values(self, var):
        values = set()
        for state in self.iter_possible_outcomes():
            values.add(state[var])
        return values

def _iter_mixed_choices_dicts(choices, remaining_parts, total_parts):
    if remaining_parts == 0:
        yield {}
    else:
        first = choices[0]
        if len(choices) <= 1:
            yield {first: float(remaining_parts) / total_parts}
        else:
            for first_parts in range(remaining_parts + 1):
                parts = remaining_parts - first_parts
                for sub_choice in _iter_mixed_choices_dicts(choices[1:], parts,
                                                            total_parts):
                    if first_parts > 0:
                        sub_choice[first] = float(first_parts) / total_parts
                    yield sub_choice
                
def _iter_mixed_choices(choices, parts):
    for dic in _iter_mixed_choices_dicts(choices, parts, parts):
        if len(dic) == 1:
            yield dic.keys()[0]
        else:
            yield dic

GRANULARITY = 8 # 8 is reasonable

class ProbaGameRules(GameRules):
    def __init__(self, function, *roles):
        new_roles = []
        for role in roles:
            class new_role(role):
                choices = list(_iter_mixed_choices(role.choices, GRANULARITY))
            new_role.__name__ = role.__name__
            new_roles.append(new_role)
        GameRules.__init__(self, function, *new_roles)


    def extrapolate_possible_outcomes(self, base_state):
        for choice_state in self._iter_outcomes_rec(base_state, self.roles):
            strategies = []
            is_possible = True
            for role in self.roles:
                choices = [choice_state[var] for var in role.choicevars]
                # Whether it is possible to take different choices
                # depending of the context or not depends of what info we see
                # for now, let's not handle that, asssume the user is blind
                if len(choices) >= 2:
                    assert len(choices) == 2
                    if choices[0] != choices[1]:
                        is_possible =  False
                def choose(role, *args):
                    return  choices[0]
                strategies.append(choose)
            if is_possible:
                states_and_probas = self._get_states_and_probas(strategies)
                result = dict(choice_state)
                for state, proba in states_and_probas:
                    for role in self.roles:
                        if hasattr(role, "utility"):
                            result.setdefault(role.utility, 0.0)
                            result[role.utility] += state[role.utility] * proba
                yield result

    def _get_states_and_probas(self, strategies):
        game = Game(self, strategies)
        probagame = ProbabilisticGame(game)
        return [(w.state, p) for w, p in probagame.iter_worlds()]
        
    def run(self, *strategies):
        states_and_probas = self._get_states_and_probas(strategies)
        for role in self.roles:
            print_role_expected_result(role, states_and_probas)

MAX_DEPTH = 1

class Game:
    def __init__(self, rules, strategies, possible_states=None, depth=0):
        self.rules = rules
        self.strategies = strategies
        self.function = rules.function
        self.agents = {}
        for i, role in enumerate(rules.roles):
            agent = Agent(role, strategies[i])
            for choicevar in role.choicevars:
                self.agents[choicevar] = agent
        if possible_states is None:
            possible_states = list(self.rules.iter_possible_outcomes({}))
        self._possible_states = possible_states
        self.depth = depth

    def get_agent_choice(self, var, world):
        return self.agents[var].get_choice(world)

    def is_certain(self, predicate, verbose=False):
        allowed_states = filter(predicate.fulfills, self._possible_states)
        if len(allowed_states) >= len(self._possible_states):
            assert len(allowed_states) == len(self._possible_states)
            if verbose:
                self.comment(str(predicate) + " already true of " +\
                             str(len(allowed_states)) + " states.")
                #for state in allowed_states:
                #    self.comment(" " + str(state))
            return True
        elif len(allowed_states) == 0:
            if verbose:
                self.comment(str(predicate) + " never true.")
            return False
        else:
            if verbose:
                self.comment(str(predicate) + " uncertain - simulating.")
            # We need recursion! But under strict control.
            sub_game = Game(self.rules, self.strategies,
                            possible_states=allowed_states, depth=self.depth+1)
            world = sub_game.run()
            if verbose:
                self.comment(str(predicate) + " == " +\
                             str(world.state in allowed_states))
            return world.state in allowed_states

    def random(self):
        assert False, "This game doesn't allow random strategies!"

    def run(self):
        world = World(self)
        self.function(world)        
        return world

    def comment(self, line):
        if self.depth <= MAX_DEPTH:
            print " "*self.depth + str(line)

class ProbabilisticGame:
    def __init__(self, game):
        self.game = game
        self.rules = game.rules
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

    def __delitem__(self, var):
        del self.state[var]

    def __setitem__(self, var, val):
        self.state[var] = val

    def __str__(self):
        return str(self.state)

if __name__ == "__main__":
    for c in _iter_mixed_choices(["Foo", "Bar", "Foobar"], 4):
        print c
