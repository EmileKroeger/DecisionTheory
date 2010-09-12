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
# Strategies
####################################

def make_mono_strategy(choice):
    def choose(role, *args):
        return choice
    return choose

def blind_optimizer(role, game, *args):
    utilities_and_choices = []
    for state in game.rules.extrapolate_possible_outcomes({}):
        #print "Possible state:", state
        utility = state[role.utility]
        choices = [state[choicevar] for choicevar in role.choicevars]
        if len(choices) == 1:
            utilities_and_choices.append((utility, choices[0]))
        else:
            s = set(map(str, choices)) # hack, check they're all the same.
            if len(s) == 1:
                utilities_and_choices.append((utility, choices[0]))
    return sorted(utilities_and_choices, reverse=True)[0][1]

####################################
# Ultimatum
####################################

GIVER_REWARD = "GIVER_REWARD"
ACCEPTER_REWARD = "ACCEPTER_REWARD"
OFFER = "OFFER"
ACCEPTS = "ACCEPTS"

class GiverRole:
    utility = GIVER_REWARD
    choicevar = OFFER
    choices = [(5, 5), (8, 2)]
    sees_world = True

class AccepterRole:
    utility = ACCEPTER_REWARD
    choicevar = ACCEPTS
    choices = [True, False]
    sees_world = True

def ultimatum(world):
    offer = world.get(OFFER)
    if world.get(ACCEPTS):
        world[GIVER_REWARD], world[ACCEPTER_REWARD] = offer
    else:
        world[GIVER_REWARD], world[ACCEPTER_REWARD] = (0, 0)

ultimatum_rules = GameRules(ultimatum, GiverRole, AccepterRole)

####################################
# Prisoner's Dilemma
####################################

COOPERATE = "COOPERATE"
DEFECT = "DEFECT"

class Prisoner1:
    utility = P1UTIL
    choicevar = P1CHOICE
    choices = [COOPERATE, DEFECT]
    sees_world = False

class Prisoner2:
    utility = P2UTIL
    choicevar = P2CHOICE
    choices = [COOPERATE, DEFECT]
    sees_world = False

pd_payoffs = {(COOPERATE, COOPERATE): (3, 3),
              (COOPERATE, DEFECT):    (0, 5),
              (DEFECT,    COOPERATE): (5, 0),
              (DEFECT,    DEFECT):    (1, 1)}

def prisoners_dilemma(world):
    choices = world.get(P1CHOICE), world.get(P2CHOICE)
    world[P1UTIL], world[P2UTIL] = pd_payoffs[choices]

pd_rules = GameRules(prisoners_dilemma, Prisoner1, Prisoner2)

# Agents

pd_asshole = make_mono_strategy(DEFECT)
pd_sucker = make_mono_strategy(COOPERATE)

def nice_prisoner(role, game):
    if game.is_certain(Implies(Is(role.choicevar, COOPERATE),
                               Is(role.utility, 3))):
        return COOPERATE
    else:
        return DEFECT

def smart_prisoner(role, game):
    if game.is_certain(Implies(Is(role.choicevar, DEFECT),
                               Is(role.utility, 5))):
        return DEFECT
    elif game.is_certain(Implies(Is(role.choicevar, COOPERATE),
                                 Is(role.utility, 3))):
        return COOPERATE
    else:
        return DEFECT

###################################
# Newcomb's problem
###################################

OMEGA_PREDICATION = "OMEGA_PREDICATION"

PLAYER_CHOICE = "PLAYER_CHOICE"
ONEBOX = "ONEBOX"
TWOBOX = "TWOBOX"
PLAYER_UTIL = "PLAYER_UTIL"

class OmegaRole:
    choicevar = OMEGA_PREDICATION
    choices = [ONEBOX, TWOBOX]
    sees_world = False

class NewcombsPlayerRole:
    utility = PLAYER_UTIL
    choicevar = PLAYER_CHOICE
    choices = [ONEBOX, TWOBOX]
    sees_world = False

def newcombs_problem(world):
    prediction = world.get(OMEGA_PREDICATION)
    transparent_box = 1000
    if prediction == TWOBOX:
        opaque_box = 0
    else:
        opaque_box = 1000000
    player_choice = world.get(PLAYER_CHOICE)
    if player_choice == TWOBOX:
        world[PLAYER_UTIL] = opaque_box + transparent_box
    else:
        world[PLAYER_UTIL] = opaque_box

def newcombs_omega(role, game):
    if game.is_certain(Is(PLAYER_CHOICE, ONEBOX)):
        return ONEBOX
    else:
        return TWOBOX
                       
newcombs_rules = GameRules(newcombs_problem, OmegaRole, NewcombsPlayerRole)


###################################
# Blackmail
###################################

BLACKMAIL_CHOICES = [9, 6, 5, 4, 1]
#BLACKMAIL_CHOICES = [9, 5, 1]

class Splitter1Role:
    utility = P1UTIL
    choicevar = P1CHOICE
    choices = BLACKMAIL_CHOICES
    sees_world = False

class Splitter2Role:
    utility = P2UTIL
    choicevar = P2CHOICE
    choices = BLACKMAIL_CHOICES
    sees_world = False

def blackmail(world):
    p1val = world.get(P1CHOICE)
    p2val = world.get(P2CHOICE)
    if p1val + p2val <= 10:
        world[P1UTIL] = p1val
        world[P2UTIL] = p2val
    else:
        world[P1UTIL] = 0
        world[P2UTIL] = 0

blackmail_rules = GameRules(blackmail, Splitter1Role, Splitter2Role)

def smart_blackmailer(role, game):
    for share in BLACKMAIL_CHOICES:
        if game.is_certain(Implies(Is(role.choicevar, share),
                                   Is(role.utility, share))):
            return share
    return 9
                           
def verbose_blackmailer(role, game):
    if role.utility == P1UTIL:
        name = "P1: "
    else:
        name = "P2: "
    game.comment(name + "What will I play?")
    for share in BLACKMAIL_CHOICES:
        game.comment(name + "Could I get " + str(share) + "?")
        if game.is_certain(Implies(Is(role.choicevar, share),
                                   Is(role.utility, share)),
                           verbose=True):
            game.comment(name + "I can get " + str(share))
            return share
        else:
            game.comment(name + "I can't get " + str(share))
    game.comment(name + "Final fallback!")
    return 9
                           
if __name__ == "__main__":
    #ultimatum_rules.run(blind_optimizer, blind_optimizer)
    #pd_rules.run(pd_asshole, blind_optimizer)
    #pd_rules.run(nice_prisoner, pd_sucker)
    #newcombs_rules.run(newcombs_omega, make_mono_strategy(ONEBOX))
    #blackmail_rules.run(smart_blackmailer, smart_blackmailer)
    #blackmail_rules.run(verbose_blackmailer, smart_blackmailer)
    blackmail_rules.run(verbose_blackmailer, verbose_blackmailer)
