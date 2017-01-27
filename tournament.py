#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        con = psycopg2.connect("dbname=tournament")
        cur = con.cursor()
        return con, cur
    except:
        print "Error connecting to db"


def deleteMatches():
    """Remove all the match records from the database."""
    con, cur = connect()

    try:
        # reset the matches and wins to zero in players
        cur.execute("truncate matches cascade;")
    except:
        print "Error deleting matches"

    con.commit()
    cur.close()


def deletePlayers():
    """Remove all the player records from the database."""
    con, cur = connect()
    try:
        # delete all player rows from the players table
        cur.execute("truncate players cascade;")
    except:
        print "Error deleting from db."
    con.commit()
    cur.close()


def countPlayers():
    """Returns the number of players currently registered."""
    con, cur = connect()

    try:
        cur.execute("select count(*) from players")
        # returns results as a list tuple
        r = cur.fetchall()
        # access the list/tuple value using indexes
        print r
        print r[0][0]
        return r[0][0]

    except:
        print "Error counting players."

    cur.close()


def registerPlayer(theName):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    # initialize vars for inserting zeros for wins and matches

    con, cur = connect()

    try:
        cmd = "insert into players (name) values(%s);"
        cur.execute(cmd, (theName,))
        con.commit()
    except:
        print "Error registering players."

    cur.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    con, cur = connect()
    '''get all the players from the players table and convert the data from\
     a list of tuples to a list of lists.
    '''
    cur.execute("select * from players;")
    allPlayers = cur.fetchall()
    playerList = []
    # Now copy all the players to a new list
    allPlayers2 = []
    for x in allPlayers:
        temp = []
        temp.append(x[0])
        temp.append(x[1])
        allPlayers2.append(temp)

    '''Now, get the wins and matches from the data base and copy everything\
     to yet another new list.'''
    allPlayers3 = []
    for x in allPlayers2:
        # get the value in the db for the first players wins
        q = "select count(winner) from matches where winner = %s;"
        '''[x[0]] is the first index value of "x" player ... the extra [] \
        is needed for a strange Pythonic reason.
        '''
        cur.execute(q, [x[0]])
        wins = cur.fetchall()
        # convert list tuple to integer
        wins = int(wins[0][0])
        x.append(wins)
        # Now do the same thing for matches
        q2 = "select count(loser) from matches where loser = %s;"
        cur.execute(q2, [x[0]])
        loses = cur.fetchall()
        matches = wins + int(loses[0][0])
        x.append(matches)
        allPlayers3.append(x)

    # convert the nested list of lists to a list of tuples using a list comp:
    allPlayers3 = [tuple(x) for x in allPlayers3]
    return allPlayers3

    cur.close()


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    # first update the winner
    con, cur = connect()
    cur.execute(
        "insert into matches (winner, loser) values (%s,%s);", (winner, loser))
    con.commit()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    con, cur = connect()
    # find how many is the max number of wins for all players
    cur.execute(
        "SELECT players.id, players.name, count(matches.winner) as wins FROM players left join matches on players.id = matches.winner group by players.id order by wins desc;")
    standings = cur.fetchall()

    pairings = []
    # set the range for the loop
    num = int(len(standings))/2
    # create pairings..loop over the 'ordered' standings and pair them up
    for x in range(0, num):
        player1 = standings.pop(0)
        player1 = player1[0:2]
        player2 = standings.pop(0)
        player2 = player2[0:2]
        # combine tuples
        match = player1 + player2
        # add tuple(match) to the list
        pairings.append(match)

    return pairings
