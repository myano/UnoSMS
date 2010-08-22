"""
UnoText - UnoBot through Text Messaging
Copyright (C) 2010  Michael S. Yanovich

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.
"""

# imports
import random
import BeautifulSoup
import sys
import time
from datetime import datetime, timedelta
from googlevoice import Voice,util

SCOREFILE = "/home/yano/phenny_osu/unoscores.txt"

STRINGS = {
    'ALREADY_STARTED' : 'Game already started by %s! Type join to join!',
    'GAME_STARTED' : 'IRC-UNO started by %s - Type join to join!',
    'GAME_STOPPED' : 'Game stopped.',
    'CANT_STOP' : '%s is the game owner, you can\'t stop it!',
    'DEALING_IN' : 'Dealing %s into the game as player #%s!',
    'JOINED' : 'Dealing %s into the game as player #%s!',
    'ENOUGH' : 'There are enough players, type .deal to start!',
    'NOT_STARTED' : 'Game not started, type .uno to start!',
    'NOT_ENOUGH' : 'Not enough players to deal yet.',    
    'NEEDS_TO_DEAL' : '%s needs to deal.',
    'ALREADY_DEALT' : 'Already dealt.',
    'ON_TURN' : 'It\'s %s\'s turn.',
    'DONT_HAVE' : 'You don\'t have that card, %s',
    'DOESNT_PLAY' : 'That card does not play, %s',
    'UNO' : 'UNO! %s has ONE card left!',
    'WIN' : 'We have a winner! %s!!!! This game took %s',
    'DRAWN_ALREADY' : 'You\'ve already drawn, either .pass or .play!',
    'DRAWS' : '%s draws a card',
    'DRAWN_CARD' : 'Drawn card: %s',
    'DRAW_FIRST' : '%s, you need to draw first!',
    'PASSED' : '%s passed!',
    'NO_SCORES' : 'No scores yet',
    'SCORE_ROW' : '#%s %s (%s points %s games, %s won, %s wasted)',
    'TOP_CARD' : '%s\'s turn. Top Card: %s',
    'YOUR_CARDS' : 'Your cards: %s',
    'NEXT_START' : 'Next: ',
    'NEXT_PLAYER' : '%s (%s cards)',
    'D2' : '%s draws two and is skipped!',
    'CARDS' : 'Cards: %s',
    'WD4' : '%s draws four and is skipped!',
    'SKIPPED' : '%s is skipped!',
    'REVERSED' : 'Order reversed!',
    'GAINS' : '%s gains %s points!',
}

# List of needed functions
def extractsms(htmlsms) :
    """
    extractsms  --  extract SMS messages from BeautifulSoup tree of 
    Google Voice SMS HTML.

    Output is a list of dictionaries, one per message.
    """
    msgitems = [] # accum message items here
    # Extract all conversations by searching for a DIV with an ID at top
    # level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)   # parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True}, \
        recursive=False)
    for conversation in conversations :
        # For each conversation, extract each row, which is one SMS 
        # message.
        rows = conversation.findAll(attrs={"class" : \
            "gc-message-sms-row"})
        for row in rows: # for all rows
            # For each row, which is one message, extract all the fields
            # tag this message with conversation ID
            msgitem = {"id" : conversation["id"]} 
            spans = row.findAll("span",attrs={"class" : True}, \
                recursive=False)
            # for all spans in row
            for span in spans:
                cl = span["class"].replace('gc-message-sms-', '')
                # put text in dict
                msgitem[cl] = (" ".join(span.findAll( \
                    text=True))).strip()
            # add msg dictionary to list
            msgitems.append(msgitem)     
    return msgitems



# ======================================================================
"""
Copyright 2010 Tamas Marki. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY TAMAS MARKI ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL TAMAS MARKI OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


[18:03] <Lako> .play w 3
[18:03] <unobot> TopMobil's turn. Top Card: [*]
[18:03] [Notice] -unobot- Your cards: [4][9][4][8][D2][D2]
[18:03] [Notice] -unobot- Next: hatcher (5 cards) - Lako (2 cards)
[18:03] <TopMobil> :O
[18:03] <Lako> :O
"""
class UnoBot:
    def __init__ (self):
        self.colored_card_nums = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'R', 'S', 'D2' ]
        self.special_scores = { 'R' : 20, 'S' : 20, 'D2' : 20, 'W' : 50, 'WD4' : 50}
        self.colors = 'RGBY'
        self.special_cards = [ 'W', 'WD4' ]
        self.players = { }
        self.playerOrder = [ ]
        self.game_on = False
        self.currentPlayer = 0
        self.topCard = None
        self.way = 1
        self.drawn = False
        self.scoreFile = SCOREFILE
        self.deck = [ ]
    
    def start(self, owner):
        if self.game_on:
            #phenny.msg (CHANNEL, STRINGS['ALREADY_STARTED'] % self.game_on)
            #message = STRINGS['ALREADY_STARTED'] % self.game_on
            voice.send_sms(owner, STRINGS['ALREADY_STARTED'] % self.game_on)
        else:
            self.game_on = owner
            self.deck = [ ]
            #phenny.msg (CHANNEL, STRINGS['GAME_STARTED'] % owner)
            voice.send_sms(owner, STRINGS['GAME_STARTED'] % owner)
            self.players = { }
            self.players[owner] = [ ]
            self.playerOrder = [ owner ]
    
    def stop (self, person):
        if person == self.game_on:
            #phenny.msg (CHANNEL, STRINGS['GAME_STOPPED'])
            voice.send_sms(self.playerOrder, STRINGS['GAME_STOPPED'])
            self.game_on = False
        elif self.game_on:
            #phenny.msg (CHANNEL, STRINGS['CANT_STOP'] % self.game_on)
            voice.send_sms(self.playerOrder, STRINGS['CANT_STOP'] % self.game_on)
            
    def join (self, current_player):
        if self.game_on:
            if current_player not in self.players:
                self.players[current_player] = [ ]
                self.playerOrder.append (current_player)
                if self.deck:
                    for i in xrange (0, 7):
                        self.players[current_player].append (self.getCard ())
                    #phenny.msg (CHANNEL, STRINGS['DEALING_IN'] % (current_player, self.playerOrder.index (current_player) + 1))
                    voice.send_sms(self.playerOrder, STRINGS['DEALING_IN'] % (current_player, self.playerOrder.index (current_player) + 1))
                else:
                    #phenny.msg (CHANNEL, STRINGS['JOINED'] % (current_player, self.playerOrder.index (current_player) + 1))
                    voice.send_sms(self.playerOrder, STRINGS['JOINED'] % (current_player, self.playerOrder.index (current_player) + 1))
                    if len (self.players) > 1:
                        #phenny.msg (CHANNEL, STRINGS['ENOUGH'])
                        voice.send_sms(self.playerOrder, STRINGS['ENOUGH'])
        else:
            #phenny.msg (CHANNEL, STRINGS['NOT_STARTED'])
            voice.send_sms(self.playerOrder, STRINGS['NOT_STARTED'])
    
    def deal (self):
        if not self.game_on:
            #phenny.msg (CHANNEL, STRINGS['NOT_STARTED'])
            voice.send_sms(self.playerOrder, STRINGS['NOT_STARTED'])
            return
        if len (self.players) < 2:
            #phenny.msg (CHANNEL, STRINGS['NOT_ENOUGH'])
            voice.send_sms(self.playerOrder, STRINGS['NOT_ENOUGH'])
            return
        if input.nick != self.game_on:
            #phenny.msg (CHANNEL, STRINGS['NEEDS_TO_DEAL'] % self.game_on)
            voice.send_sms(self.playerOrder, STRINGS['NEEDS_TO_DEAL'] % self.game_on)
            return
        if len (self.deck):
            #phenny.msg (CHANNEL, STRINGS['ALREADY_DEALT'])
            voice.send_sms(self.playerOrder, STRINGS['ALREADY_DEALT'])
            return
        self.startTime = datetime.now ()
        self.deck = self.createnewdeck ()
        for i in xrange (0, 7):
            for p in self.players:
                self.players[p].append (self.getCard ())
        self.topCard = self.getCard ()
        while self.topCard in ['W', 'WD4']: self.topCard = self.getCard ()
        self.currentPlayer = 1
        self.cardPlayed (self.topCard)
        self.showOnTurn ()
    
    def play (self, player):
        if not self.game_on or not self.deck:
            return
        if player != self.playerOrder[self.currentPlayer]:
            #phenny.msg (CHANNEL, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            return
        tok = [z.strip () for z in str (input).upper ().split (' ')]
        if len (tok) != 3:
            return
        searchcard = ''
        if tok[1] in self.special_cards:
            searchcard = tok[1]
        else:
            searchcard = (tok[1] + tok[2])
        if searchcard not in self.players[self.playerOrder[self.currentPlayer]]:
            #phenny.msg (CHANNEL, STRINGS['DONT_HAVE'] % self.playerOrder[self.currentPlayer])
            return
        playcard = (tok[1] + tok[2])
        if not self.cardPlayable (playcard):
            #phenny.msg (CHANNEL, STRINGS['DOESNT_PLAY'] % self.playerOrder[self.currentPlayer])
            return
        
        self.drawn = False
        self.players[self.playerOrder[self.currentPlayer]].remove (searchcard)
        
        pl = self.currentPlayer
        
        self.incPlayer ()
        self.cardPlayed (playcard)

        if len (self.players[self.playerOrder[pl]]) == 1:
            #phenny.msg (CHANNEL, STRINGS['UNO'] % self.playerOrder[pl])
            voice.send_sms(self.playerOrder, STRINGS['UNO'] % self.playerOrder[pl])
        elif len (self.players[self.playerOrder[pl]]) == 0:
            #phenny.msg (CHANNEL, STRINGS['WIN'] % (self.playerOrder[pl], (datetime.now () - self.startTime)))
            voice.send_sms(self.playerOrder, STRINGS['WIN'] % (self.playerOrder[pl], (datetime.now () - self.startTime)))
            self.gameEnded (self.playerOrder[pl])
            return
            
        self.showOnTurn ()

    def draw (self, player):
        if not self.game_on or not self.deck:
            return
        if player != self.playerOrder[self.currentPlayer]:
            #phenny.msg (CHANNEL, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            voice.send_sms(self.playerOrder, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            return
        if self.drawn:
            #phenny.msg (CHANNEL, STRINGS['DRAWN_ALREADY'])
            voice.send_sms(self.playerOrder, STRINGS['DRAWN_ALREADY'])
            return
        self.drawn = True
        #phenny.msg (CHANNEL, STRINGS['DRAWS'] % self.playerOrder[self.currentPlayer])
        voice.send_sms(self.playerOrder, STRINGS['DRAWS'] % self.playerOrder[self.currentPlayer])
        c = self.getCard ()
        self.players[self.playerOrder[self.currentPlayer]].append (c)
        #phenny.notice (input.nick, STRINGS['DRAWN_CARD'] % self.renderCards ([c]))
        voice.send_sms(player, STRINGS['DRAWN_CARD'] % self.renderCards ([c]))

    # this is not a typo, avoiding collision with Python's pass keyword
    def passs (self, player):
        if not self.game_on or not self.deck:
            return
        if player != self.playerOrder[self.currentPlayer]:
            #phenny.msg (CHANNEL, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            voice.send_sms(self.playerOrder, STRINGS['ON_TURN'] % self.playerOrder[self.currentPlayer])
            return
        if not self.drawn:
            #phenny.msg (CHANNEL, STRINGS['DRAW_FIRST'] % self.playerOrder[self.currentPlayer])
            voice.send_sms(self.playerOrder, STRINGS['DRAW_FIRST'] % self.playerOrder[self.currentPlayer])
            return
        self.drawn = False
        #phenny.msg (CHANNEL, STRINGS['PASSED'] % self.playerOrder[self.currentPlayer])
        voice.send_sms(self.playerOrder, STRINGS['PASSED'] % self.playerOrder[self.currentPlayer])
        self.incPlayer ()
        self.showOnTurn ()
    
    def top10 (self):
        from copy import copy
        prescores = [ ]
        try:
            f = open (self.scoreFile, 'r')
            for l in f:
                t = l.replace ('\n', '').split (' ')
                if len (t) < 4: continue
                prescores.append (copy (t))
                if len (t) == 4: t.append (0)
            f.close ()
        except: pass
        prescores = sorted (prescores, lambda x, y: cmp ((y[1] != '0') and (float (y[3]) / int (y[1])) or 0, (x[1] != '0') and (float (x[3]) / int (x[1])) or 0))
        if not prescores:
            #phenny.say(STRINGS['NO_SCORES'])
            pass
        i = 1
        for z in prescores[:10]:
            #phenny.say(STRINGS['SCORE_ROW'] % (i, z[0], z[3], z[1], z[2], timedelta (seconds = int (z[4]))))
            pass
            i += 1

    
    def createnewdeck (self):
        ret = [ ]
        for a in self.colored_card_nums:
            for b in self.colors:
                ret.append (b + a)
        for a in self.special_cards: 
            ret.append (a)
            ret.append (a)
        ret *= 3
        random.shuffle (ret)

        return ret
    
    def getCard(self):
        ret = self.deck[0]
        self.deck.pop (0)
        if not self.deck:
            self.deck = self.createnewdeck ()        
        return ret
    
    def showOnTurn (self):
        #phenny.msg (CHANNEL, STRINGS['TOP_CARD'] % (self.playerOrder[self.currentPlayer], self.renderCards ([self.topCard])))
        voice.send_sms(self.playerOrder, STRINGS['TOP_CARD'] % (self.playerOrder[self.currentPlayer], self.renderCards ([self.topCard])))
        #phenny.notice (self.playerOrder[self.currentPlayer], STRINGS['YOUR_CARDS'] % self.renderCards (self.players[self.playerOrder[self.currentPlayer]]))
        voice.send_sms(self.playerOrder[self.currentPlayer], STRINGS['YOUR_CARDS'] % self.renderCards (self.players[self.playerOrder[self.currentPlayer]]))
        msg = STRINGS['NEXT_START']
        tmp = self.currentPlayer + self.way
        if tmp == len (self.players):
            tmp = 0
        if tmp < 0:
            tmp = len (self.players) - 1
        arr = [ ]
        while tmp != self.currentPlayer:
            arr.append (STRINGS['NEXT_PLAYER'] % (self.playerOrder[tmp], len (self.players[self.playerOrder[tmp]])))
            tmp = tmp + self.way
            if tmp == len (self.players):
                tmp = 0
            if tmp < 0:
                tmp = len (self.players) - 1
        msg += ' - '.join (arr)
        #phenny.notice (self.playerOrder[self.currentPlayer], msg)
        voice.send_sms(self.playerOrder[self.currentPlayer], msg)
    
    def showCards (self, user):
        if not self.game_on or not self.deck:
            return
        #phenny.notice (user, STRINGS['YOUR_CARDS'] % self.renderCards (self.players[user]))
        voice.send_sms(user, STRINGS['YOUR_CARDS'] % self.renderCards (self.players[user]))
    def renderCards (self, cards):
        ret = [ ]
        for c in sorted (cards):
            if c in ['W', 'WD4']:
                ret.append ('\x0300,01[' + c + ']')
                continue
            if c[0] == 'W':
                c = c[-1] + '*'
            t = '\x0300,01\x03'
            if c[0] == 'B':
                t += '11,01['
            if c[0] == 'Y':
                t += '08,01['
            if c[0] == 'G':
                t += '09,01['
            if c[0] == 'R':
                t += '04,01['
            t += c[1:] + ']\x0300,01'
            ret.append (t)
        return ''.join (ret)
    
    def cardPlayable (self, card):
        if card[0] == 'W' and card[-1] in self.colors:
            return True
        if self.topCard[0] == 'W':
            return card[0] == self.topCard[-1]
        return (card[0] == self.topCard[0]) or (card[1] == self.topCard[1])
    
    def cardPlayed (self, card):
        if card[1:] == 'D2':
            #phenny.msg (CHANNEL, STRINGS['D2'] % self.playerOrder[self.currentPlayer])
            voice.send_sms(self.playerOrder, STRINGS['D2'] % self.playerOrder[self.currentPlayer])
            z = [self.getCard (), self.getCard ()]
            #phenny.notice(self.playerOrder[self.currentPlayer], STRINGS['CARDS'] % self.renderCards (z))
            voice.send_sms(self.playerOrder[self.currentPlayer], STRINGS['CARDS'] % self.renderCards (z))
            self.players[self.playerOrder[self.currentPlayer]].extend (z)
            self.incPlayer ()
        elif card[:2] == 'WD':
            #phenny.msg (CHANNEL, STRINGS['WD4'] % self.playerOrder[self.currentPlayer])
            voice.send_sms(self.playerOrder, STRINGS['WD4'] % self.playerOrder[self.currentPlayer])
            z = [self.getCard (), self.getCard (), self.getCard (), self.getCard ()]
            #phenny.notice(self.playerOrder[self.currentPlayer], STRINGS['CARDS'] % self.renderCards (z))
            voice.send_sms(self.playerOrder[self.currentPlayer], STRINGS['CARDS'] % self.renderCards (z))
            self.players[self.playerOrder[self.currentPlayer]].extend (z)
            self.incPlayer ()
        elif card[1] == 'S':
            #phenny.msg (CHANNEL, STRINGS['SKIPPED'] % self.playerOrder[self.currentPlayer])
            voice.send_sms(self.playerOrder, STRINGS['SKIPPED'] % self.playerOrder[self.currentPlayer])
            self.incPlayer ()
        elif card[1] == 'R' and card[0] != 'W':
            #phenny.msg (CHANNEL, STRINGS['REVERSED'])
            voice.send_sms(self.playerOrder, STRINGS['REVERSED'])
            if len(self.players) > 2:
                self.way = -self.way
                self.incPlayer ()
                self.incPlayer ()
            else:
                self.incPlayer ()
        self.topCard = card
    
    def gameEnded (self, winner):
        try:
            score = 0
            for p in self.players:
                for c in self.players[p]:
                    if c[0] == 'W':
                        score += self.special_scores[c]
                    elif c[1] in [ 'S', 'R', 'D' ]:
                        score += self.special_scores[c[1:]]
                    else:
                        score += int (c[1])
            #phenny.msg (CHANNEL, STRINGS['GAINS'] % (winner, score))
            voice.send_sms(self.playerOrder, STRINGS['GAINS'] % (winner, score))
            self.saveScores (self.players.keys (), winner, score, (datetime.now () - self.startTime).seconds)
        except Exception, e:
            print 'Score error: %s' % e
        self.players = { }
        self.playerOrder = [ ]
        self.game_on = False
        self.currentPlayer = 0
        self.topCard = None
        self.way = 1
        
    
    def incPlayer (self):
        self.currentPlayer = self.currentPlayer + self.way
        if self.currentPlayer == len (self.players):
            self.currentPlayer = 0
        if self.currentPlayer < 0:
            self.currentPlayer = len (self.players) - 1
    
    def saveScores (self, players, winner, score, time):
        from copy import copy
        prescores = { }
        try:
            f = open (self.scoreFile, 'r')
            for l in f:
                t = l.replace ('\n', '').split (' ')
                if len (t) < 4: continue
                if len (t) == 4: t.append (0)
                prescores[t[0]] = [t[0], int (t[1]), int (t[2]), int (t[3]), int (t[4])]
            f.close ()
        except: pass
        for p in players:
            if p not in prescores:
                prescores[p] = [ p, 0, 0, 0, 0 ]
            prescores[p][1] += 1
            prescores[p][4] += time
        prescores[winner][2] += 1
        prescores[winner][3] += score
        try:
            f = open (self.scoreFile, 'w')
            for p in prescores:
                f.write (' '.join ([str (s) for s in prescores[p]]) + '\n')
            f.close ()
        except Exception, e:
            print 'Failed to write score file %s' % e

unobot = UnoBot ()

# ======================================================================
'''
def uno(phenny, input):
    unobot.start (phenny, input.nick)
uno.commands = ['uno']

def unostop(phenny, input):
    unobot.stop (phenny, input)
unostop.commands = ['unostop']

def join(phenny, input):
    unobot.join (phenny, input)
join.rule = '^join$'

def deal(phenny, input):
    unobot.deal (phenny, input)
deal.commands = ['deal']

def play(phenny, input):
    unobot.play (phenny, input)
play.commands = ['play', 'p']

def draw(phenny, input):
    unobot.draw (phenny, input)
draw.commands = ['draw', 'd']

def passs(phenny, input):
    unobot.passs (phenny, input)
passs.commands = ['pass', 'pa']

def unotop10 (phenny, input):
    unobot.top10 (phenny)
unotop10.commands = ['unotop10']

def show_user_cards (phenny, input):
    unobot.showCards (phenny, input.nick)
show_user_cards.commands = ['cards']
'''
# ======================================================================

# Log into Google Voice
voice = Voice()
voice.login()

# Keep searching all messages for a '.uno'

k=True
while k==True:
    voice.sms()
    # Search text messages for '.uno' and just '.uno'
    for each in extractsms(voice.sms.html):
        # act accordingly.
        input = each["from"]
        if input != "Me:":
            a = input[1:-1]
            if each["text"] == '.uno' and voice.sms().messages[0].isRead == False:
                print "Starting the game!"
                unobot.start (a)
                break
            elif each["text"] == 'join':
                print "Joining  " + str(a) + " to the game!"
                unobot.join(a)
                break
            elif each["text"] == 'deal':
                print "Dealing the game."
                unobot.deal()
                break
            elif each["text"] == 'unostop':
                print "Stopping the game!"
                unobot.stop(a)
                k=False
                break
            elif each["text"].beginswith("play"):
                print "Making a play!"
                unobot.play(a)
                break
            elif each["text"] == 'draw':
                print "Drawing!"
                unobot.draw(a)
                break
            elif each["text"] == "pass":
                print "Pass!"
                unobot.passs(a)
                break
    # Sleep for 15 seconds to prevent abuse.
    time.sleep(5)


'''
voice.sms()
list_of_messages = []
for msg in extractsms(voice.sms.html):
    list_of_messages.append(msg)
# Search text messages for '.uno' and just '.uno'
for each in list_of_messages:
    if each["text"] == '.uno' and each["from"] != "Me:":
        print each
'''

# Logout when all done!
voice.logout()
