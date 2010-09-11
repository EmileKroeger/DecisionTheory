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

from decisionworld import ProbaGameRules
from predicates import *

###################################
# Coin guessing
###################################

P1COIN = "P1COIN"
P2COIN = "P2COIN"
HEADS = "HEADS"
TAILS = "TAILS"

class CoinGuesser1:
    utility = P1UTIL
    choicevar = P1COIN
    choices = [HEADS, TAILS]
    sees_world = False
    
class CoinGuesser2:
    utility = P2UTIL
    choicevar = P2COIN
    choices = [HEADS, TAILS]
    sees_world = False

def coin_guessing(world):
    coin1 = world.get(P1COIN)
    coin2 = world.get(P2COIN)
    world[P1UTIL] = int(coin1 == coin2)
    world[P2UTIL] = 1 - int(coin1 == coin2)

def randomguesser(role, game):
    return {HEADS: 0.5, TAILS: 0.5}
    #return game.random([(HEADS, 0.5), (TAILS, 0.5)])

coin_guessing_rules = ProbaGameRules(coin_guessing, CoinGuesser1, CoinGuesser2)


###################################
# Absent-minded driver
###################################

DRIVERUTIL = "DRIVERUTIL"
DRIVERCHOICE1 = "DRIVERCHOICE1"
DRIVERCHOICE2 = "DRIVERCHOICE2"
STRAIGHT = "STRAIGHT"
TURN = "TURN"

class AbsentMindedDriver:
    utility = DRIVERUTIL
    choicevars = DRIVERCHOICE1, DRIVERCHOICE2
    choices = [TURN, STRAIGHT]
    sees_world = False

def absent_minded_driver(world):
    if (world.get(DRIVERCHOICE1) == TURN):
        world[DRIVERUTIL] = 0
    else:
        if (world.get(DRIVERCHOICE2) == TURN):
            world[DRIVERUTIL] = 4
        else:
            world[DRIVERUTIL] = 1
        
absent_minded_driver_rules = ProbaGameRules(absent_minded_driver,
                                            AbsentMindedDriver)



###################################
# Conterfactual mugging
###################################

PREDICT_PLAYER_GIVES = "PREDICT_PLAYER_GIVES"

PLAYER_GIVES = "PLAYER_GIVES"
PLAYER_UTIL = "PLAYER_UTIL"

COIN_FLIPPED_HEADS = "COIN_FLIPPED_HEADS"

class MuggingOmegaRole:
    choicevar = PREDICT_PLAYER_GIVES
    choices = [True, False]
    sees_world = True

class MuggingPlayerRole:
    utility = PLAYER_UTIL
    choicevar = PLAYER_GIVES
    choices = [True, False]
    sees_world = True

class CoinRole:
    choicevar = COIN_FLIPPED_HEADS
    choices = [True, False]
    sees_world = False

def counterfactual_mugging(world):
    predicts_player_gives = world.get(PREDICT_PLAYER_GIVES)
    transparent_box = 1000
    if world.get(COIN_FLIPPED_HEADS):
        if predicts_player_gives:
            world[PLAYER_UTIL] = 1000000
        else:
            world[PLAYER_UTIL] = 0
        world[OMEGA_WAS_RIGHT] = 1
    else:
        if world.get(PLAYER_GIVES):
            world[PLAYER_UTIL] = -100
        else:
            world[PLAYER_UTIL] = 0


def mugging_omega(role, game):
    if game.is_certain(Implies(Is(COIN_FLIPPED_HEADS, FALSE),
                               Is(PLAYER_CHOICE, GIVE))):
        return GIVE
    else:
        return DONTGIVE
                       
mugging_rules = ProbaGameRules(counterfactual_mugging, MuggingOmegaRole,
                               CoinRole, MuggingPlayerRole)


###################################
# Trivial coin watching
###################################

    
if __name__ == "__main__":
    #coin_guessing_rules.run(make_mono_strategy(HEADS), make_mono_strategy(HEADS))
    #coin_guessing_rules.run(randomguesser, make_mono_strategy(HEADS))
    #coin_guessing_rules.run(randomguesser, blind_optimizer)
    #print
    #coin_guessing_rules.run(make_mono_strategy(HEADS), blind_optimizer)
    #print
    #coin_guessing_rules.run(blind_optimizer, blind_optimizer)
    absent_minded_driver_rules.run(blind_optimizer)
    #absent_minded_driver_rules.run(make_mono_strategy({TURN:0.33, STRAIGHT:0.67}))
    #pass

