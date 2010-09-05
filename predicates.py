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

#####################################################
# Predicates
#####################################################

class _BinaryPredicate:
    def __init__(self, predicate1, predicate2):
        self.predicate1 = predicate1
        self.predicate2 = predicate2

    def __str__(self):
        return "(%s %s %s)" % (str(self.predicate1), self.symbol,
                               str(self.predicate2))

class Is:
    def __init__(self, varname, value):
        self.varname = varname
        self.value = value

    def fulfills(self, state):
        #print "", str(self)
        #print " fulfilled by", str(state)
        return state[self.varname] == self.value

    def __str__(self):
        return "(%s == %s)" % (str(self.varname), str(self.value))

class Not:
    def __init__(self, predicate):
        self.predicate = predicate

    def fulfills(self, state):
        return not self.predicate.fulfills(state)

    def __str__(self):
        return "!" + str(self.predicate)
            
class And(_BinaryPredicate):
    symbol = "&"
    def fulfills(self, state):
        if self.predicate1.fulfills(state):
            return self.predicate2.fulfills(state)

class Or(_BinaryPredicate):
    symbol = "|"
    def fulfills(self, state):
        if self.predicate1.fulfills(state):
            return True
        else:
            return self.predicate2.fulfills(state)

class Implies(_BinaryPredicate):
    symbol = "->"
    def fulfills(self, state):
        if self.predicate2.fulfills(state):
            return True
        else:
            return not self.predicate1.fulfills(state)

class Equivalent(_BinaryPredicate):
    symbol = "<->"
    def fulfills(self, state, context):
        if self.predicate2.fulfills(state):
            return self.predicate1.fulfills(state)
        else:
            return not self.predicate1.fulfills(state)
