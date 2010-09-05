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

from decisionworld import GameRules
from predicates import *

####################################
# General constants
####################################

P1CHOICE = "P1CHOICE"
P2CHOICE = "P2CHOICE"
P1UTIL = "P1UTIL"
P2UTIL = "P2UTIL"


####################################
# Ultimatum
####################################

GIVER_REWARD = "GIVER_REWARD"
ACCEPTER_REWARD = "ACCEPTER_REWARD"
OFFER = "OFFER"
ACCEPTS = "ACCEPTS"

class GiverRole:
    utility = GIVER_REWARD
    choice = (OFFER, [(5, 5), (8, 2)])
    sees_world = True

class AccepterRole:
    utility = ACCEPTER_REWARD
    choice = (ACCEPTS, [True, False])
    sees_world = True

def ultimatum(world):
    offer = world[OFFER]
    if world[ACCEPTS]:
        world[GIVER_REWARD], world[ACCEPTER_REWARD] = offer
    else:
        world[GIVER_REWARD], world[ACCEPTER_REWARD] = (0, 0)

ultimatum_rules = GameRules(ultimatum, GiverRole, AccepterRole)

####################################
# Strategies
####################################

def make_mono_strategy(choice):
    def choose(role, *args):
        return choice
    return choose

def first_strategy(role, *args):
    return role.choice[1][0]

def last_strategy(role, *args):
    return role.choice[1][-1]

def blind_optimizer(role, game, *args):
    var, alternatives = role.choice
    utilities_and_choices = []
    for state in game.rules.iter_possible_outcomes({}):
        choice = state[var]
        utility = state[role.utility]
        utilities_and_choices.append((utility, choice))
    return sorted(utilities_and_choices, reverse=True)[0][1]

####################################
# Prisoner's Dilemma
####################################

COOPERATE = "COOPERATE"
DEFECT = "DEFECT"

class Prisoner1:
    utility = P1UTIL
    choice = (P1CHOICE, [COOPERATE, DEFECT])
    sees_world = False

class Prisoner2:
    utility = P2UTIL
    choice = (P2CHOICE, [COOPERATE, DEFECT])
    sees_world = False

pd_payoffs = {(COOPERATE, COOPERATE): (3, 3),
              (COOPERATE, DEFECT):    (0, 5),
              (DEFECT,    COOPERATE): (5, 0),
              (DEFECT,    DEFECT):    (1, 1)}

def prisoners_dilemma(world):
    choices = world[P1CHOICE], world[P2CHOICE]
    world[P1UTIL], world[P2UTIL] = pd_payoffs[choices]

pd_rules = GameRules(prisoners_dilemma, Prisoner1, Prisoner2)

# Agents

pd_asshole = make_mono_strategy(DEFECT)
pd_sucker = make_mono_strategy(COOPERATE)

def nice_prisoner(role, game):
    if game.is_certain(Implies(Is(role.choice[0], COOPERATE),
                               Is(role.utility, 3))):
        return COOPERATE
    else:
        return DEFECT

def smart_prisoner(role, game):
    if game.is_certain(Implies(Is(role.choice[0], DEFECT),
                               Is(role.utility, 5))):
        return DEFECT
    elif game.is_certain(Implies(Is(role.choice[0], COOPERATE),
                                 Is(role.utility, 3))):
        return COOPERATE
    else:
        return DEFECT

###################################
#newcomb's problem
###################################


OMEGA_WAS_RIGHT = "OMEGA_WAS_RIGHT"
OMEGA_PREDICATION = "BOX_CONTENTS"

PLAYER_CHOICE = "PLAYER_CHOICE"
ONEBOX = "ONEBOX"
TWOBOX = "TWOBOX"
PLAYER_UTIL = "PLAYER_UTIL"

class OmegaRole:
    utility = OMEGA_WAS_RIGHT
    choice = OMEGA_PREDICATION, (ONEBOX, TWOBOX)
    sees_world = False

class NewcombsPlayerRole:
    utility = PLAYER_UTIL
    choice = PLAYER_CHOICE, (ONEBOX, TWOBOX)
    sees_world = False

def newcombs_problem(world):
    prediction = world[OMEGA_PREDICATION]
    transparent_box = 1000
    if prediction == TWOBOX:
        opaque_box = 0
    else:
        opaque_box = 1000000
    player_choice = world[PLAYER_CHOICE]
    if player_choice == TWOBOX:
        world[PLAYER_UTIL] = opaque_box + transparent_box
    else:
        world[PLAYER_UTIL] = opaque_box
    world[OMEGA_WAS_RIGHT] = (prediction == player_choice)

def omega(role, game):
    if game.is_certain(Is(PLAYER_CHOICE, ONEBOX)):
        return ONEBOX
    elif game.is_certain(Is(PLAYER_CHOICE, TWOBOX)):
        return TWOBOX
    else:
        # stuck? Player deliberately opaque?
        return TWOBOX
                       
newcombs_rules = GameRules(newcombs_problem, OmegaRole, NewcombsPlayerRole)

###################################
# coin guessing
###################################

P1COIN = "P1COIN"
P2COIN = "P2COIN"
HEADS = "HEADS"
TAILS = "TAILS"

class CoinGuesser1:
    utility = P1UTIL
    choice = (P1COIN, [HEADS, TAILS])
    sees_world = False
    
class CoinGuesser2:
    utility = P2UTIL
    choice = (P2COIN, [HEADS, TAILS])
    sees_world = False

def coin_guessing(world):
    coin1 = world[P1COIN]
    coin2 = world[P2COIN]
    world[P1UTIL] = int(coin1 == coin2)
    world[P2UTIL] = 1 - world[P1UTIL]

coin_guessing_rules = GameRules(coin_guessing, CoinGuesser1, CoinGuesser2)

if __name__ == "__main__":
    #ultimatum_rules.run(first_strategy, first_strategy)
    #ultimatum_rules.run(blind_optimizer, blind_optimizer)
    #pd_rules.run(pd_asshole, blind_optimizer)
    #pd_rules.run(nice_prisoner, pd_sucker)
    #newcombs_rules.run(omega, make_mono_strategy(ONEBOX))
    coin_guessing_rules.run(make_mono_strategy(HEADS), make_mono_strategy(HEADS))



