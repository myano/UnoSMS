"""
uno.py - Uno Bot through Text Messaging

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
from datetime import datetime, timedelta
from googlevoice import Voice,util

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
    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

    Output is a list of dictionaries, one per message.
    """
    msgitems = []										# accum message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :							# for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            msgitems.append(msgitem)					# add msg dictionary to list
    return msgitems


# Log into Google Voice
voice = Voice()
voice.login()


voice.sms()
list_of_messages = []
for msg in extractsms(voice.sms.html):
    list_of_messages.append(msg)

print str(list_of_messages)
