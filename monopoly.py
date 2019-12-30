#!/usr/local/bin/python3.7
#!/usr/bin/env python3.7
PORT = 8888
import socket
import threading
import random
import sys
import textwrap
import time
import chance
class User:
    money = 1500
    money = 150000000000
    def __init__(self, color, char, name, conn=None):
        self.color = color
        self.char = char
        self.name = name
        self.conn = conn
        self.color_code = "\033[3{};1m".format(color)
        self.tile = None
        self.jailed = False
        self.num_cards = 0  # get out of jail free cards
        self.num_cards = 1  # TODO: debugging
        self.rolls = []
        self.obtainable_wealth = 0  # amount of money play will have if they sell everything
                                    # distinct from worth in that mortgaged props only give you half
        self.bankrupt = False

    @property 
    def worth(self):
        """Returns total amount that a player is worth, with full unmortgaged property values."""
        total = 0
        obtainable_wealth = 0
        for t in self.game.tiles:
            if hasattr(t, "owner") and t.owner == self:
                if t.mortgaged:
                    total += t.prices["mortgaged"]
                else:
                    total += t.prices["printed"]
                    if type(t) is BuildableTile:
                        obtainable_wealth += t.prices["mortgaged"]
                        # A hotel is worth the same as a house
                        num_houses = 5 if t.hotel else t.num_houses
                        for h in range(num_houses):
                            total += t.prices["building"]
                            obtainable_wealth += t.prices["building"]
        obtainable_wealth += self.money
        self.obtainable_wealth = obtainable_wealth
        total += self.money
        return total

    def send(self, message):
        """Sends a specific user a message,"""
        self.conn.send(bytes((message+"\n").encode("utf-8")))

    def rolled_doubles(self):
        """Returns True if last roll was doubles."""
        # Useful for determining if user goes to or leaves jail.
        if self.rolls[-1][0] == self.rolls[-1][1]:
            return True
        return False

    def __str__(self):
        return self.color_code + self.char + "\033[0m"
    def __repr__(self):
        return self.name

class Group:
    """A group of properties, for example, the red properties."""
    def __init__(self, color, group_id):
        self.tiles = []
        self.color = color
        self.id = group_id
        if color == 0:
            self.color_code = "\033[36;1m"
        elif color == 7:
            self.color_code = "\033[37;1m"
        else:
            self.color_code = "\033[3{};21m".format(color)

class GeneralTile:
    """Base class for the entire types of tiles."""
    width = 5
    next_tile = None
#    footprints = set()
    def __init__(self, name, width=5):
        self.occupants = []
        self.name = name
        self.width=width
        self.footprints = set()

    def print_top(self):
        """Prints out a blank top row of a tile for basic tiles."""
        return "     "

    @property
    def o(self):
        """Returns a string of occupants of the tile."""
        # This property exists to make the __str__ method a bit more readable.
        return self.print_occupants()    

    def print_occupants(self):
        """Returns a string of occupants of the tile."""
        string = ""
        occupant_graphics = []
        for o in self.occupants:
            if o == self.game.current_player:
                print("is current_player")
                graphic = "\033[{};7m{}\033[0m".format(o.color, str(o))
                print(graphic)
            else:
                graphic = str(o)
            occupant_graphics.append(graphic)
#            occupant_graphic += graphic
        
#        if occupant_graphic:
#            print(occupant_graphic)
        print(self.footprints)
        for f in self.footprints:
            occupant_graphics.append("\033[3{}m-\033[0m".format(f.color))
        #random.shuffle(occupant_graphics)
        print(occupant_graphics)

        # Centering graphic for aesthetic reasons.
#        if len(self.occupants) == 0:
#            occupant_graphic = "     "
#        elif len(self.occupants) == 1:
##            occupant_graphic = "   {}  ".format(*self.occupants)
#            occupant_graphic = "   {}  ".format(*occupant_graphics)
#        elif len(self.occupants) == 2:
##            occupant_graphic = " {} {}  ".format(*self.occupants)
#            occupant_graphic = " {} {}  ".format(*occupant_graphics)
#        elif len(self.occupants) == 3:
#            occupant_graphic = "{} {} {} ".format(*self.occupants)
#        elif len(self.occupants) == 4:
#            occupant_graphic = " {}{}{}{} ".format(*self.occupants)
        if len(occupant_graphics) == 0:
            occupant_graphic = "     "
        elif len(occupant_graphics) == 1:
#            occupant_graphic = "   {}  ".format(*self.occupants)
            occupant_graphic = "   {}  ".format(*occupant_graphics)
        elif len(occupant_graphics) == 2:
#            occupant_graphic = " {} {}  ".format(*self.occupants)
            occupant_graphic = " {} {}  ".format(*occupant_graphics)
        elif len(occupant_graphics) == 3:
            occupant_graphic = "{} {} {} ".format(*occupant_graphics)
        elif len(occupant_graphics) == 4:
            occupant_graphic = " {}{}{}{} ".format(*occupant_graphics)
        occupant_graphic += " " * ((self.width+1) - (len(occupant_graphic)))

        if occupant_graphic.strip():
            print("!!", occupant_graphic)
        return occupant_graphic

    def on_landing(self, player):
        """Handles what happens when player lands on tile."""
        # This function shouldn't ever run.
        self.game.add_message("Nothing happened!  Maybe sean didn't put functionality in yet for this tile...")
        self.game.end_buy_phase()
        
class PropertyTile(GeneralTile):
    """Base for all tiles which a player can buy."""
    owner = None
    mortgaged = False
    num_houses = 0
    hotel = False
    # following is tricky. When a player is bankrupt due to debt to another player, 
    # the other player is supposed to pay the 10% interest on that mortgage
    # then they may have to pay that interest AGAIN later on 
    # This is a subtle but big TODO
    mortgage_interest_paid = False
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.footprints = set()

    def check_which_prompt(self, player):
        """Queues an appropriate message for when a player lands on an unbought tile."""
        if player.money >= self.prices["printed"]:
            self.game.messages.append("can buy easily")
        elif player.obtainable_wealth >= self.prices["printed"]:
            self.game.messages.append("You must sell property before you can afford this")
        else:
            self.game.messages.append("You cannot afford this even if you sold everything. Maybe just let it go to [a]uction")

    def buy(self, player):
        """Player buys the property."""
        self.owner = player
        try:
            assert player.money >= self.prices["printed"]
        except: 
            return False
        player.money -= self.prices["printed"]
        self.game.add_message("{} bought the deed for {}".format(player.name, self.name))
        self.game.end_buy_phase()
        self.game.SHOW_BOARD()

    def can_be_dismantled(self):
        """Returns if a player can sell building of property, or mortgage it."""
        # Always true for base class. Descendent classes will define otherwise based off, i.e.,
        # how built up other properties in group are.
        return True

    def info(self):
        """Returns a string showing information about a tile."""
        string = """{} - Owner: {} ({}), current rent: {}""".format(self.name, self.owner.name, self.owner, self.determine_rent())
        return string

    def sell_house(self):
        """Player unimproves the property."""
        if not self.owner: return

        if isinstance(self, UtilityTile):
            self.mortgaged = True
            amount = 75
        elif isinstance(self, RailroadTile):
            self.mortgaged = True
            amount = 100
        elif self.hotel:
            self.hotel = False
            amount = int(self.prices["building"]//2)
        elif self.num_houses:
            self.num_houses -= 1
            amount = int(self.prices["building"]//2)
        else:   # by default, mortgaging the property.
            self.mortgaged = True
            amount = int(self.prices["mortgaged"])

        # If player is currently trying to resolve debt before 
        # they can continue normal play.
        if self.game.phase == "debt":
            player = self.game.current_player
            if hasattr(player.tile, "owner"):
                player.tile.owner.money += amount
            if amount >= player.debt:
                self.game.phase = "accounts"
            player.debt = max(0, player.debt - amount)
        return

    @property
    def t(self):
        """Returns the top graphic of a tile."""
        # Put in to make __str__ function of game object easier to read.
        return self.print_top()

    @property
    def l(self):
        """Returns the label of a property."""
        if self.game.show_labels:
            if self.owner:
                return "{}{}\033[0m".format(self.owner.color_code, self.label)
            return self.label
        else:
            return "--"

    def print_top(self):
        """Returns the top graphic of a tile."""
        if self.owner and not self.mortgaged:
            return "{}[    ]{}\033[0m".format(self.owner.color_code, self.owner.color_code)
        elif self.owner:
            return "{}[\\\\\\\\]{}\033[0m".format(self.owner.color_code, self.owner.color_code)
        else:
            return "      "

    def on_landing(self, player):
        """What happens when player lands on this tile."""
        amount = 0
        if self.owner:
            if self.owner != player:
                amount = self.determine_rent()
                self.game.pay_amount(player, self.owner, amount)
            self.game.end_buy_phase()

        elif not self.owner:
            self.check_which_prompt(player)
            self.game.prompt = "No one owns this property.  Would you like to [B]uy it or let it go to [A]uction?"
            self.game.phase = "buy"
            self.game.buying_query = True

class TaxTile(GeneralTile):
    """A tile that taxes the player."""
    def __init__(self, name, width=5, tax=0):
        self.name = name
        self.width = width
        self.occupants = []
        self.tax = tax
        self.footprints = set()
    def on_landing(self, player):
        """What happens when player lands on this tile."""
        self.game.pay_amount(player, "bank", self.tax)
        self.game.end_buy_phase()        

class RailroadTile(PropertyTile):
    """A railroad tile."""
    prices = {"printed": 200, "mortgaged": 100}
    mortgaged = False
    def __init__(self, name, label, width=5):
        self.name = name
        self.width = width
        self.label = label
        self.occupants = []
        self.footprints = set()

    def on_landing(self, player):
        """What happens when a player lands on this tile."""
        if not self.owner:
            self.game.prompt = "No one owns this property.  Would you like to [b]uy it or let it go to [a]uction?"
        elif self.owner:
            if self.owner != player:
#                rent = 25 * self.game.check_other_rrs_owned(self)
                rent = self.determine_rent()
                self.game.add_message("{} paid ${} rent to {}".format(player.name, rent, self.owner.name))
            self.game.end_buy_phase()

    def determine_rent(self):
        """Returns how much rent a landing player owes to the owner."""
        rent = 25 * self.game.check_other_rrs_owned(self)
        return rent

class JailTile(GeneralTile):
    """The Jail tile."""
    # Is essentially a free tile.  Jail functionality itself isn't handled here.
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = [] # These are the cellmates.
        self.slots = [" "] * 4  # And these are the visitors
        self.footprints = set()

class UtilityTile(PropertyTile):
    """The Electric Company and Water Works tiles."""
    prices = {"printed": 200, "mortgaged": 100} #TODO: change
    mortgaged = False
    def __init__(self, name, label, width=5):
        self.name = name
        self.width = width
        self.label = label
        self.occupants = []
        self.footprints = set()

    def on_landing(self, player):
        """What happens when a player lands here."""
        if not self.owner:
            self.game.prompt = "No one owns this property. Would you like to [b]uy it or let it go to [a]uction?"
        elif self.owner:
            if self.owner != player:
                rent = self.determine_rent()
                self.game.add_message("{} paid ${} to {}".format(player.name, rent, self.owner.name))    
            self.game.end_buy_phase()

    def determine_rent(self):
        """Returns how much a player pays in rent if they land here."""
        last_roll = sum(self.game.current_player.rolls[-1])
        multiplier = 4
        for tile in self.game.tiles:
            if tile == self:
                continue
            elif isinstance(tile, UtilityTile):
                if tile.owner == self.owner:
                    multiplier = 10
                break
        return last_roll * multiplier

class FreeParkingTile(GeneralTile):
    """The Free Parking tile."""
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.slots = [" "] * 4
        self.footprints = set()

class CommunityTile(GeneralTile):
    """Tile for both Community Chest spaces."""
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.footprints = set()

    def on_landing(self, player):
        """What happens when a player lands on this tile."""
        card = self.game.community_deck.grab_card(player)

class ChanceTile(GeneralTile):
    """Tile for both Chance spaces."""
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.footprints = set()

    def on_landing(self, player):
        """What happens when a player lands on this tile."""
        card = self.game.chance_deck.grab_card(player)

class GoToJailTile(GeneralTile):
    """The tile that sends you to Jail."""
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.footprints = set()
    def on_landing(self, player):
        """What happens when a player lands here."""
        
#        #TODO: This block is for debugging
#        new_tile = self.game.get_next_tile(self.game.current_player, 1, single=True) #TODO: debugging
#        self.game.move_player(self.game.current_player, new_tile)
#        return

        self.game.send_to_jail(player)

class BuildableTile(PropertyTile):
    """A tile you can build houses on."""
    mortgaged = False
    def __init__(self, group, name, label, rents, prices, width = 5):
        self.width = width
        self.occupants = []
        self.owner = None
        self.label = label
        self.group = group
        self.name = name
        self.rents = rents
        self.prices = prices
        group.tiles.append(self)
        self.num_houses = 0
        self.num_hotels = 0
        self.hotel = False
        self.footprints = set()

    def determine_rent(self):
        "Returns how much rent is owed."""
        if self.hotel:
            return self.rents["hotel"]
        if not self.num_houses:
            if self.is_monopoly:
                return self.rents[0] * 2
        return self.rents[self.num_houses]
    
    def is_monopoly(self):
        """Returns if one player owns all the properties in the group."""
        if None in [t.owner for t in self.group.tiles]:
            return False
        num_owners = len(set([t.owner for t in self.group.tiles]))
        if num_owners == 1:
            return True
        return False

    def can_be_improved(self):
        """Returns if it's allowed for the owner to build a house or hotel on this property."""
        if not self.is_monopoly(): return False
        for tile in self.group.tiles:
            if tile is self: continue
            if not self.mortgaged and tile.mortgaged:
                return False
            if self.num_houses > tile.num_houses:
                return False
        return True
    def can_be_dismantled(self):
        """Determines if owner is allowed to remove a house, or mortgage, this property."""
        if not self.is_monopoly: return False
        # hotel functionally counts as 5 houses
        if self.hotel:
            actual_amount = 5
        elif self.mortgaged:
            actual_amount = -1
        else:
            actual_amount = self.num_houses
        for tile in self.group.tiles:
            temp_actual_amount = 5 if tile.hotel else tile.num_houses
            temp_actual_amount = -1 if tile.mortgaged else temp_actual_amount
            if tile is self: continue
            if actual_amount < temp_actual_amount:
                return False
        return True

    def improve(self):
        """Builds a house or hotel on this property."""
        if not self.owner: return
        if self.hotel: return
        if self.mortgaged:
            self.owner.money -= int(self.prices["mortgaged"] + self.prices["mortgaged"]*.1)
            self.mortgaged = False
            self.game.messages.append("{} paid off the mortgage on {}".format(self.game.current_player.name, self.name))
        elif self.num_houses < 4:
            self.num_houses += 1
            self.owner.money -= self.prices["building"]
            self.game.messages.append("{} erected a house on {}".format(self.game.current_player.name, self.name))
        elif self.num_houses == 4:
            self.hotel = True
            self.game.messages.append("{} erected a hotel on {}".format(self.game.current_player.name, self.name))

    def print_top(self):
        """Prints the top part of the tile."""
        if self.owner and self.mortgaged:
            return "{}[XXXX]\033[0m".format(self.owner.color_code, self.owner.color_code)
        string = ""
        if self.owner:
            string += self.owner.color_code + "["
        if self.hotel:
            building_graphic = "*HH*"
        elif self.num_houses:
            building_graphic = "h" * self.num_houses
        else:
            building_graphic = "=" * 6 if not self.owner else "=" * 4
        building_graphic = "{:^4}".format(building_graphic)
        string += self.group.color_code + building_graphic
        if self.owner:
            string += self.owner.color_code + "]"
        string += "\033[0m"
        return string

class Board():
    """The object that represents the game as a whole."""
    def __init__(self, tiles):
        self.current_player = None
        self.tiles = tiles
        self.players = []
        self.started = False
        self.buying_query = False
        self.in_auction = False
        self.phase = "buy" #TODO: buying?
        self.phase = "roll"
        self.seconds_left = 0
        self.owner = None
        current_tile = self.tiles[0]
        current_tile.occupants = self.players.copy()
        self.highest_bid = (None, 0)
        self.messages = []
        self.prompt = ""
        self.frame = 0
        self.chance_deck = chance.Chance(self)
        self.chance_deck.shuffle()
        self.community_deck = chance.Community(self)
        self.community_deck.shuffle()
        self.current_trade = None
        self.show_labels = True

        tile_iterator = iter(self.tiles[1:])
        for next_tile in tile_iterator:
            current_tile.next_tile = next_tile
            current_tile.game = self
            current_tile = next_tile
        next_tile.next_tile = self.tiles[0] 
        next_tile.game = self

        self.cells = [" ", " ", " ", " "] # representing players in jail

    def pay_amount(self, player, recipient, amount):
        """Player pays another player or the bank."""
        # When penultimate player runs out of money, game is over.
        if amount > player.worth:
            self.declare_bankrupcy(player, recipient, amount)
            if self.phase == "GAMEOVER":
                return
        # Player ran out of hard cash, must sell properties before turn can continue
        elif amount > player.money:
            if recipient != "bank":
                recipient.money += player.money
            player.debt = amount - player.money
            self.phase = "debt"
            self.messages.append("{} paid {} but still owes {}.".format(player, player.money, player.debt))
            player.money = 0
            return

        else:
            player.money -= amount
            self.messages.append("{} paid {} to {}".format(player, amount, recipient))
            player.send("You paid {} in rent".format(amount))

    def declare_bankrupcy(self, player, creditor, amount):
        """Player loses the game."""
        properties = []
        num_houses = 0
        num_hotels = 0
        mortgage_interest_owed = 0
        for tile in self.tiles:
            if hasattr(tile, "owner") and tile.owner == player:
                if hasattr(tile, "num_houses"):
                    num_houses += tile.num_houses
                    if tile.hotel:
                        num_hotels += 1
                    tile.num_houses = 0
                    tile.num_hotels = 0
                if tile.mortgaged:
                    mortgage_interest_owed += int(tile.prices["mortgage"]/10)
                tile.mortgaged = True
                if creditor != "bank":
                    tile.owner = creditor
        if creditor != "bank":
            creditor.money += player.worth - mortgage_interest_owed
        player.money = 0
        player.bankrupt = True
        self.next_turn(after_bankrupcy=player)

    def broadcast(self, message):
        """Sends a message to every player."""
        for p in self.players:
            try:
                p.conn.send(bytes((message + "\n").encode("utf-8")))
            except: #Player doesn't exist, or isn't connected anymore
                pass

    def show_board(self):
        """Shows the current state of the game to everyone."""
        self.broadcast(str(self))

    def add_message(self, message):
        """ Adds a message to the queue which gets displayed with the board."""
        self.messages.append(message)
    def add_player(self, player):
        """Adds a new player to the game before it starts."""
        if not self.started:
            self.players.append(player)
            if len(self.players) == 1:
                self.creator = player
        self.broadcast("{}({}) joined the game!".format(player.name, player))
    
    def SHOW_BOARD(self):
        string = ""
        string += str(self)
        for e, p in enumerate(self.players, 1):
            if p == self.current_player: string += ">"
            else: string += " "
            string += "{}: {} ({}): ${}\n".format(e, p.name, p, p.money)
        string += "Current player: {} ({}), has ${} (${} including property) -- {}\n".format(self.current_player.name, self.current_player, self.current_player.money, self.current_player.worth, self.current_player.obtainable_wealth)
        for m in self.messages:
            string += m + "\n"
        for p in self.players:
            if p == self.current_player: continue
            try:
                p.send(string)
            except:
                pass

        string += self.prompt
        self.prompt = ""
        self.messages = []
        self.current_player.send(string)

    def begin(self):
        """Initializes the beginning of the game."""

        # TODO: debugging stuff
#        you = self.players[0]
#        self.players.append(User(2, "!", "test1", conn=you.conn))
#        self.players.append(User(3, "#", "test3", conn=you.conn))

        random.shuffle(self.players)
        for player in self.players:
            player.tile = self.tiles[0]
            player.game = self

        self.started = True
        self.current_player = self.players[0]
        self.tiles[0].occupants = self.players.copy()

        self.add_message("The game has begun!")
        order = ", ".join(["{} ({})".format(p.name, p) for p in self.players])
        self.add_message("The order of play is {}".format(order))
        self.SHOW_BOARD()
        self.current_player.send("It is your turn! [R]oll the dice by typing 'R'.")

    def player_rolls(self):
        """Handles what happens during or after a player rolls the dice at beginning of their turn."""
        amount = self.roll_dice()
        if len(self.current_player.rolls) >= 3:
            is_double = True
            for roll in self.current_player.rolls[-3:]:
                if not roll[0] == roll[1]:
                    is_double = False
            if is_double:
                print(self.current_player.rolls)
                self.send_to_jail(self.current_player)
                return
        self.phase = "buy"
        self.buying_query = True
        new_tile = self.get_next_tile(self.current_player, amount) #TODO: debugging
        
        roll1, roll2 = self.current_player.rolls[-1][0], self.current_player.rolls[-1][1]
        try:
            message = "{} rolled a {}-{} and landed on {}.".format(self.current_player.name, roll1, roll2, new_tile.name)
        except: 
            message = "{} rolled a {}-{}".format(self.current_player.name, roll1, roll2)

        if not self.current_player.jailed and hasattr(new_tile, "name") and new_tile.name == "Jail":
            message += "  They're just visiting though!"
        self.add_message(message)
        self.move_player(self.current_player, new_tile)
        self.SHOW_BOARD()

    def roll_dice(self):
        """Determines how far to move the player."""
        die1 = random.randrange(1, 7)
        die2 = random.randrange(1, 7)
        self.current_player.rolls.append((die1, die2))
        return die1 + die2

    def game_over(self):
        """Handling the game ending."""
        self.broadcast("Game over!")
        self.phase = "GAMEOVER"

    def next_turn(self, after_bankrupcy=None):
        """Starts the turn for the next player, moves them and prompts them."""
        for t in self.tiles:
            t.footprints.clear()
        which_player = self.players.index(self.current_player)
        if after_bankrupcy:
            self.players.remove(after_bankrupcy)
            if len(self.players) == 1:
                self.game_over()
                return
        
        else:
            #TODO: player that's out isn't necessarily the current player.  Make it so the number increments if and only if 
            # the removed player doesn't mess with the next index
            which_player += 1
        which_player = which_player % len(self.players)
        self.current_player = self.players[which_player]
        self.phase = "roll"
        if self.current_player.jailed:
            self.prompt = "It's your turn, but you are in jail. To leave you can pay $50 [b]ail, attempt to [r]oll a double, or play a Get Out of Jail Free [C]ard"
        else:
            self.prompt = "It is your turn! Enter 'R' to roll the dice. ZZZZZZZZZZ"
        self.SHOW_BOARD()
    
    def move_player(self, player, tile):
        """Moves the player to a specific tile."""
        # If you didn't know the difference between whither and whence, now you know.
        whence = player.tile
        whither = tile
        whence.occupants.remove(player)
        if hasattr(whither, "occupants"):
            whither.occupants.append(player)
        player.tile = whither

        # Player passed Go
        if self.tiles.index(whither) <= self.tiles.index(whence):
            player.money += 200
        if hasattr(whither, "on_landing"):
            whither.on_landing(player)

        if whence.name in ["Jail", "Free Parking"]:
            whence.slots = [" " if s == player else s for s in whence.slots]
        if whither.name in ["Jail", "Free Parking"]:
            self.put_in_random_slot(player, whither)
            
    def get_next_tile(self, player, amount, single=False):
        """Returns the tile a player is moving to."""
        current_tile = player.tile
        print("starting tile is: ", player.tile)
        #TODO: debugging
        previous = [current_tile]
        if single:
            return current_tile.next_tile
            self.move_player(player, player.tile.next_tile)
            return
        if amount < 0:
            amount = 40 + amount
        for i in range(amount):
            try:
                current_tile = current_tile.next_tile #TODO: occasionally doesn't work, figure out why
                if i < amount - 1:
                    print(current_tile)
                    current_tile.footprints.add(player)
                print("{} add {}".format(current_tile.name, player))
            except Exception as err:
                print(previous)
                raise err
            previous.append(current_tile)
            
        return current_tile

    def put_in_random_slot(self, player, tile):
        """Puts a player's icon into a slot for Jail or Free Parking."""
        slots = list(range(4))
        random.shuffle(slots)
        for s in slots:
            if tile.slots[s] != " ":
                continue
            else:
                tile.slots[s] = player
                break
        
    def handle_auction(self, tile):
        """If current player doesn't purchase PropertyTile, hold an auction to determine who buys it."""
        amount = 0
        player = None
        self.current_auction_price = 0
        self.seconds_left = 21

        while self.seconds_left > 0:
            if (self.seconds_left % 5 == 0) or self.seconds_left <= 5:
                self.broadcast("${}\t{} seconds left...".format(self.highest_bid[1], self.seconds_left))
            time.sleep(1)
            self.seconds_left -= 1

        self.in_auction = False
        tile.owner = self.highest_bid[0]
        self.add_message("Auction over!")
        self.add_message("{} bought {} for {}".format(self.highest_bid[0], tile.name, self.highest_bid[1]))
        tile.owner.money -= self.highest_bid[1]
        
        self.end_buy_phase()
        self.SHOW_BOARD()

    def end_buy_phase(self):
        """After a PropertyTile is bought, ask the player if they want to buy/sell houses, etc"""
        # Because this function runs after landing on a tax tile.
        if self.phase == "GAMEOVER":
            return
        self.phase = "accounts"
        if self.current_player.rolls[-1][0] == self.current_player.rolls[-1][1] and not self.current_player.jailed:
            self.prompt = "Do you want to handle your [a]ccounts or [r]oll again?"
        else:
            self.prompt = "Do you want to handle your [a]ccounts or [p]ass to the next person's turn?"

    def send_to_jail(self, player):
        """Moves a player to jail."""
        if hasattr(player.tile, "occupants"):
            player.tile.occupants.remove(player)
        print("sent to jail???")
        player.tile = None
        while True:
            which_cell = random.randrange(4)
            if self.cells[which_cell] == " ":
                break
        self.cells[which_cell] = player
        player.jailed = True
        self.prompt = "Type 'p' to pass to the next player."
        self.end_buy_phase()

    def pay_bail(self):
        """Current player pays the bail, advances."""
        player = self.current_player
        if player.money >= 50:
            player.money -= 50
        else: return
        self.prompt = "Type 'r' to roll the dice."
        self.leave_jail(player)

    def use_card(self):
        """Current player uses their Get Out of Jail Free Card, advances."""
        player = self.current_player
        if player.num_cards >= 0:
            player.num_cards -= 1
            self.promt = "Type 'r' to roll the dice."
            self.leave_jail(player)
            return

    def sell_tile(self, player, label):
        """Player sells a tile."""
        for tile in self.tiles:
            if isinstance(tile, PropertyTile) and tile.label == label and tile.owner == self.current_player:
                if tile.can_be_dismantled():
                    tile.sell_house()
                    self.SHOW_BOARD()
                break

    def roll_to_leave_jail(self):
        """Current player attempts to roll doubles to get out of jail, may advance."""
        player = self.current_player
        amount = self.roll_dice()
        if player.rolled_doubles():
            self.leave_jail(player)
            tile = self.get_next_tile(player, amount)
            self.move_player(player, tile)
            if hasattr(player.tile, "on_landing"):
                player.tile.on_landing(player)

    def leave_jail(self, player):
        """Current player leaves jail, advances."""
        if player.jailed:
            player.jailed = False
        else: return
        for cell in self.cells:
            if cell == player:
                # Removes graphic from Jail cell.
                self.cells[self.cells.index(cell)] = " "
        
        player.tile = self.tiles[10]
        self.tiles[10].occupants.append(player)
        self.put_in_random_slot(player, self.tiles[10])
        self.SHOW_BOARD()

    def show_player_info(self, player):
        """Show the players data about themselves in response to 'me' query."""
        player.send("{} ({}) - ${}".format(player.name, player, player.money))
        grouped_a = list(filter(lambda t: hasattr(t, "group"), self.tiles))
        grouped = sorted(grouped_a, key=lambda t: t.group.id)
        owned_by_player = list(filter(lambda t: t.owner == player, grouped))
        utilities_owned_by_player = list(filter(lambda t: t.owner == player, [self.tiles[12], self.tiles[28]]))
        railroads_owned_by_player = list(filter(lambda t: t.owner == player, [self.tiles[5], self.tiles[15], self.tiles[25], self.tiles[35]]))
        owned_by_player.extend(utilities_owned_by_player + railroads_owned_by_player)
        
        # Show all properties owned by player in an organized manner.
        owned_string = ""
        for tile in owned_by_player:
            if hasattr(tile, "group"):
                owned_string += "{}: {}{}\033[0m, ".format(tile.label, tile.group.color_code, tile.name)
            else:
                owned_string += "{}: {}, ".format(tile.label, tile.name)
        owned_string.strip(", ")
        player.send(owned_string)

    def check_other_rrs_owned(self, tile):
        """Check how many other railroads the player owns."""
        owner = tile.owner
        owned = filter(lambda t: t.owner == owner, (self.tiles[5], self.tiles[15], self.tiles[25], self.tiles[35]))
        return(len(list(owned)))
            
    def handle_bid(self, player, amount):
        """Handles a bid for an auction."""
        amount = int(amount)
        if self.highest_bid[1] < amount < player.money:
            self.highest_bid = (player, amount)
            if not self.auction_timer.is_alive():
                self.auction_timer.start()
            self.seconds_left = 21

    def accept_trade(self):
        """Transfer property and money in a trade."""
        trade = self.current_trade
        player, offeree, offered_stuff, for_stuff = trade
        money_delta = for_stuff["money"] - offered_stuff["money"]
        player.money += money_delta
        offeree.money -= money_delta
        player.num_cards -= offered_stuff["cards"]
        offeree.num_cards += offered_stuff["cards"] #TODO: fix cards
        
        for p in for_stuff["properties"]:
            print(p.owner)
            p.owner = player
            print(p.owner)
        for p in offered_stuff["properties"]:
            p.owner = offeree

        self.current_trade = None


    def parse_trade(self, player, line):
        line = [w.lower() for w in line]
        # Smallest size trade command example: trade fred c3 for c4"
        if len(line) < 5:
            return None
        if "for" not in line[3:-1]:
            return None
            
        recipient = line[1]
        valid_player = None

        # When the trader puts in the player index number
        if recipient.isdigit() and 0 < int(recipient) <= (len(self.players)+1):
            valid_player = self.players[int(recipient)-1]
        else:
            for p in self.players:
            
                if recipient in [p.name.lower(), p.char]:
                    valid_player = p

        if not (valid_player and (valid_player != player and not valid_player.bankrupt)):
            valid_player = False
        if not valid_player: 
            return None

        offeree = valid_player
        offeree_tiles = []
        offerer_tiles = []

        offered_stuff = {"money": 0, "cards": 0, "properties": set()}
        for_stuff = {"money": 0, "cards": 0, "properties": set()}
        target_dict = offered_stuff
        target_tilelist = offerer_tiles
        target_player = player

        for tile in self.tiles:
            if not hasattr(tile, "owner"):
                continue
            # Not allowed to trade properties that are built up
            #TODO: none in the group can have houses
            if tile.owner == player:
                if isinstance(tile, BuildableTile) and (tile.num_houses > 0 or tile.hotel):
                    continue
                offerer_tiles.append(tile)
            elif tile.owner == offeree:
                if isinstance(tile, BuildableTile) and (tile.num_houses > 0 or tile.hotel):
                    continue
                offeree_tiles.append(tile)


        for word in line[2:]:
            word = word.lower().strip(",.$")
            if word.lower() == "for":
                target_dict = for_stuff
                target_tilelist = offeree_tiles
                target_player = offeree
                continue

            if word.isdigit():
                amount = int(word)
                if amount <= target_player.money:
                    target_dict["money"] += amount
                else:
                    print("{} doesn't have that much money".format(target_player.name))
            elif word in ["card", "c", "jail", "j"]:
                if target_player.num_cards > 0:
                    target_dict["cards"] += 1
                else:
                    print("{} does't have a get out of jail free card".format(target_player.name))
            else:
                for tile in target_tilelist:
                    if tile.label == word:
                        target_dict["properties"].add(tile)
                    else:
                        print("{} doesn't own that".format(target_player.name))

        lowest_money = min(offered_stuff["money"], for_stuff["money"])
        offered_stuff["money"] -= lowest_money
        for_stuff["money"] -= lowest_money


        # Ensure something is being moved both sides of the transaction
        if not (any(offered_stuff.values()) and any(for_stuff.values())):
            print("d")
            return None

        offer = [player, offeree, offered_stuff, for_stuff]
        offered_string: ""
        offered_property_string = ", ".join(["{}[{}]".format(p.name, p.label) for p in offered_stuff["properties"]])
        for_property_string = ", ".join(["{}[{}]".format(p.name, p.label) for p in for_stuff["properties"]])
        offered_money_string, for_money_string, offered_card_string, for_card_string = "", "", "", ""
        if offered_stuff["money"]:
            offered_money_string += "${}".format(offered_stuff["money"])
        if for_stuff["money"]:
            for_money_string += "${}".format(for_stuff["money"])
        if offered_stuff["cards"]:
            offered_card_string += "a Get Out of Jail Free card"
        if for_stuff["cards"]:
            for_card_string += "a Get Out of Jail Free card"
        offered_string = ", ".join(list(filter(None, [offered_property_string, offered_money_string, offered_card_string])))
        for_string = ", ".join(list(filter(None, [for_property_string, for_money_string, for_card_string])))

        message = "Trade: {} offered {} to {} in exchange for {}".format(player.name, offered_string, offeree.name, for_string)
        print(message)
        self.broadcast(message)
        self.messages.append(message)
        return offer

            
        
    def __str__(self):
        self.frame += 1
        t = self.tiles
        board = """
        \033c{}
        +-----+------+------+------+------+------+------+------+------+------+-------+
        |     |{}|{}|  ?   |{}|{}|      |{}|  $   |{}|       | 
        |JAIL |  CT  |  VT  |      |Orient|Readng|INCOME|Baltic|Commun|Medit | <---- | 
        |     | Ave  | Ave  |CHANCE| Ave  |  RR  | TAX  |  Ave |Chest | Ave  |   GO  | 
        |==+  |{}|{}|{}|{}|{}|{}|{}|{}|{}|{} | 
        |{} |  | 120  | 100  |  ?   | 100  | 200  | -200 |  60  |  $   |  60  |  +200 | 
        |==|{} +--{}--+--{}--+------+--{}--+--{}--+------+--{}--+------+--{}--+-------+ 
        |{} |  | 
        |==|{} +------+------+------+------+------+------+------+------+------+-------+
        |{} |  |{}|{}|{}|{}|{}|{}|  $   |{}|{}|       |
        |==|{} |St.Cs'|Electr|States|  VA  |  PA  |SJames|Commun|  TN  |  NY  | \{}\ \ | 
        |{} |  |Place |{}Co{}| Ave  | Ave  |  RR  |Place |Chest |  Ave | Ave  |  \ \ \| 
        |==+{} |{}|{}|{}|{}|{}|{}|{}|{}|{}|       | 
        |     |  140 | 150  |  140 |  160 | 200  |  180 |  $   |  180 |  200 | \{}\ \ | 
        +--||-+--{}--+--{}--+--{}--+--{}--+--{}--+--{}--+------+--{}--+--{}--+  \ \ \| 
           ||                                                                |  FREE | 
        +--||-+------+------+------+------+------+------+------+------+------+  PARK | 
        |     |{}|{}|{}|{}|{}|{}|{}|  ?   |{}|  ING  | 
        |     |Marvin|Water{}|Ventnr|Atlant| B&O  |  IL  |  IN  |      |  KY  | \ \{}\ | 
        |     |Gardns|{}Works| Ave  | Ave  |  RR  | Ave  |  Ave |CHANCE| Ave  |  \ \ \| 
        |  ^  |{}|{}|{}|{}|{}|{}|{}|{}|{}|       | 
        |  |  |  280 |  150 |  260 |  260 | 200  |  240 |  220 |  ?   |  220 | \{}\ \ | 
        |     +--{}--+--{}--+--{}--+--{}--+--{}--+--{}--+--{}--+------+--{}--+-------+ 
        | GO  |                                                                          
        | TO  +------+------+------+------+------+------+------+------+------+          
        |JAIL |{}|{}|   $  |{}|{}|  ?   |{}|      |{}|
        |     |Pacifc|  NC  |Commun|  PA  |Short |      |Park  |Luxury|Board |
        |     | Ave  |  Ave |Chest | Ave  |  Line|CHANCE| Place| Tax  | walk |
        |     |{}|{}|{}|{}|{}|{}|{}|{}|{}|
        |     |  300 |  300 |  $   |  320 |  200 |  ?   |  350 | -100 |  400 |          
        +-----+--{}--+--{}--+------+--{}--+--{}--+------+--{}--+------+--{}--+         
        {} - {}\n""" 
        text = textwrap.dedent(board.format(
            self.phase,
            t[9].t, t[8].t,         t[6].t, t[5].t,         t[3].t,         t[1].t, 
            t[9].o, t[8].o, t[7].o, t[6].o, t[5].o, t[4].o, t[3].o, t[2].o, t[1].o, t[0].o, 

            self.cells[0], t[10].slots[0], 
            t[9].l, t[8].l, t[6].l, t[5].l, t[3].l, t[1].l,
            self.cells[1], t[10].slots[1], self.cells[2],

            t[11].t, t[12].t, t[13].t, t[14].t, t[15].t, t[16].t,          t[18].t, t[19].t, #"F",
            t[10].slots[2], t[20].slots[0], self.cells[3], "\033[33m* \033[0m", "\033[33m *\033[0m", t[10].slots[3], 
            t[11].o, t[12].o, t[13].o, t[14].o, t[15].o, t[16].o, t[17].o, t[18].o, t[19].o, t[20].slots[1],
            t[11].l, t[12].l, t[13].l, t[14].l, t[15].l, t[16].l, t[18].l, t[19].l,

            t[29].t, t[28].t, t[27].t, t[26].t, t[25].t, t[24].t, t[23].t,          t[21].t, "\033[34;1m~\033[0m", t[20].slots[2], "\033[34;1m~\033[0m",
            t[29].o, t[28].o, t[27].o, t[26].o, t[25].o, t[24].o, t[23].o, t[22].o, t[21].o, t[20].slots[3],
            t[29].l, t[28].l, t[27].l, t[26].l, t[25].l, t[24].l, t[23].l,          t[21].l,         

            t[31].t, t[32].t,          t[34].t, t[35].t,          t[37].t,          t[39].t, 
            t[31].o, t[32].o, t[33].o, t[34].o, t[35].o, t[36].o, t[37].o, t[38].o, t[39].o, 
            t[31].l, t[32].l,          t[34].l, t[35].l,          t[37].l,          t[39].l, 
            self.frame, self.players, #TODO
        ))
        return text

first = Group(2, 1)
second = Group(6, 2)
third = Group(3, 3)
fourth = Group(4, 4)
fifth = Group(7, 5)
sixth = Group(1, 6)
seventh = Group(5, 7)
eighth = Group(0, 8)

tiles = [
    GeneralTile(
        name = "Go",),
    BuildableTile(
        group = first,
        name = "Meditterranean Avenue",
        label = "1a",
        rents = {0: 2, 1: 10, 2: 30, 3: 90, 4: 160, "hotel": 250},
        prices = {"printed": 60, "mortgaged": 30, "building": 50}),
    CommunityTile(
        name = "Community Chest"),
    BuildableTile(
        group = first,
        name = "Baltic Avenue",
        label = "1b",
        rents = {0: 4, 1: 20, 2: 60, 3: 180, 4: 320, "hotel": 450},
        prices = {"printed": 60, "mortgaged": 30, "building": 50}),
    TaxTile(
        name = "Income Tax",
        tax = 200),
    RailroadTile(
        name = "Reading Railroad",
        label = "r1"),
    BuildableTile(
        group = second,
        name = "Oriental Avenue",
        label = "2a",
        rents = {0: 6, 1: 30, 2: 90, 3: 270, 4: 400, "hotel": 550},
        prices = {"printed": 100, "mortgaged": 50, "building": 50}),
    ChanceTile(
        name = "Chance"),
    BuildableTile(
        group = second,
        name = "Vermont Avenue",
        label = "2b",
        rents = {0: 6, 1: 30, 2: 90, 3: 270, 4: 400, "hotel": 550},
        prices = {"printed": 100, "mortgaged": 50, "building": 50}),
    BuildableTile(
        group = second,
        name = "Connecticut Avenue",
        label = "2c",
        rents = {0: 8, 1: 40, 2: 100, 3: 300, 4: 450, "hotel": 600},
        prices = {"printed": 120, "mortgaged": 60, "building": 50}),
    JailTile(
        name = "Jail"),
    BuildableTile(
        group = third,
        name = "St. Charles Place",
        label = "3a",
        rents = {0: 10, 1: 50, 2: 150, 3: 450, 4: 625, "hotel": 750},
        prices = {"printed": 140, "mortgaged": 70, "building": 100}),
    UtilityTile(
        name = "Electric Company",
        label = "u1"),
    BuildableTile(
        group = third,
        name = "States Avenue",
        label = "3b",
        rents = {0: 10, 1: 50, 2: 150, 3: 450, 4: 625, "hotel": 750},
        prices = {"printed": 140, "mortgaged": 70, "building": 100}),
    BuildableTile(
        group = third,
        name = "Virginia Avenue",
        label = "3c",
        rents = {0: 12, 1: 60, 2: 180, 3: 500, 4: 700, "hotel": 900},
        prices = {"printed": 160, "mortgaged": 80, "building": 100}),
    RailroadTile(
        name = "Pennsylvania Railroad",
        label = "r2"),
    BuildableTile(
        group = fourth,
        name = "St. James Place",
        label = "4a",
        rents = {0: 14, 1: 70, 2: 200, 3: 550, 4: 750, "hotel": 950},
        prices = {"printed": 180, "mortgaged": 90, "building": 100}),
    CommunityTile(
        name = "Community Chest"),
    BuildableTile(
        group = fourth, 
        name = "Tennessee Avenue",
        label = "4b",
        rents = {0: 14, 1: 70, 2: 200, 3: 550, 4: 750, "hotel": 950},
        prices = {"printed": 180, "mortgaged": 90, "building": 100}),
    BuildableTile(
        group = fourth, 
        name = "New York Avenue",
        label = "4c",
        rents = {0: 16, 1: 80, 2: 220, 3: 600, 4: 800, "hotel": 1000},
        prices = {"printed": 200, "mortgaged": 100, "building": 100}),
    FreeParkingTile(
        name = "Free Parking"),
    BuildableTile(
        group = fifth,
        name = "Kentucky Avenue", 
        label = "5a",
        rents = {0: 18, 1: 90, 2: 250, 3: 700, 4: 875, "hotel": 1050},
        prices = {"printed": 220, "mortgaged": 110, "building": 150}),
    ChanceTile(
        name = "Chance"),
    BuildableTile(
        group = fifth,
        name = "Indiana Avenue",
        label = "5b",
        rents = {0: 18, 1: 90, 2: 250, 3: 700, 4: 875, "hotel": 1050},
        prices = {"printed": 220, "mortgaged": 110, "building": 150}),
    BuildableTile(
        group = fifth,
        name = "Illinois Avenue",
        label = "5c",
        rents = {0: 20, 1: 100, 2: 300, 3: 750, 4: 915, "hotel": 1100},
        prices = {"printed": 240, "mortgaged": 120, "building": 150}),
    RailroadTile(
        name = "B & O Railroad",
        label = "r3"),
    BuildableTile(
        group = sixth,
        name = "Atlantic Avenue",
        label = "6a",
        rents = {0: 22, 1: 110, 2: 330, 3: 800, 4: 975, "hotel": 1150},
        prices = {"printed": 260, "mortgaged": 130, "building": 150}),
    BuildableTile(
        group = sixth,
        name = "Ventnor Avenue",
        label = "6b",
        rents = {0: 22, 1: 110, 2: 330, 3: 800, 4: 975, "hotel": 1150},
        prices = {"printed": 260, "mortgaged": 130, "building": 150}),
    UtilityTile(
        name = "Water Works",
        label = "u2"),
    BuildableTile(
        group = sixth,
        name = "Marvin Gardens", 
        label = "6c",
        rents = {0: 24, 1: 120, 2: 360, 3: 850, 4: 1025, "hotel": 1200},
        prices = {"printed": 280, "mortgaged": 140, "building": 150}),
    GoToJailTile(
        name = "Go To Jail"),
    BuildableTile(
        group = seventh,
        name = "Pacific Avenue",
        label = "7a",
        rents = {0: 26, 1: 130, 2: 390, 3: 900, 4: 1100, "hotel": 1275},
        prices = {"printed": 300, "mortgaged": 150, "building": 200}),
    BuildableTile(
        group = seventh,
        name = "North Carolina Avenue",
        label = "7b",
        rents = {0: 26, 1: 130, 2: 390, 3: 900, 4: 1100, "hotel": 1275},
        prices = {"printed": 300, "mortgaged": 150, "building": 200}),
    CommunityTile(
        name = "Community Chest"),
    BuildableTile(
        group = seventh,
        name = "Pennsylvania Avenue",
        label = "7c",
        rents = {0: 28, 1: 150, 2: 450, 3: 1000, 4: 1200, "hotel": 1400},
        prices = {"printed": 320, "mortgaged": 160, "building": 200}),
    RailroadTile(
        name = "Short Line",
        label = "r4"),
    ChanceTile(
        name = "Chance"),
    BuildableTile(
        group = eighth,
        name = "Park Place",
        label = "8a",
        rents = {0: 35, 1: 175, 2: 500, 3: 1100, 4: 1300, "hotel": 1500},
        prices = {"printed": 350, "mortgaged": 175, "building": 200}),
    TaxTile(
        name = "Luxury Tax",
        tax = 75),
    BuildableTile(
        group = eighth,
        name = "Boardwalk",
        label = "8b",
        rents = {0: 50, 1: 200, 2: 600, 3: 1400, 4: 1700, "hotel": 2000},
        prices = {"printed": 400, "mortgaged": 200, "building": 200}),
    ]

def game_menu(conn, game_list):
    """'Lets you select which current game to play."""
    while True:
        conn.send(bytes("Select an existing game to play, or create a [n]ew game?\n".encode("utf-8")))
        for e, i in enumerate(game_list):
            conn.send(bytes("{} - {}\n".format(e, " ".join([p.name for p in i.players])).encode("utf-8")))
        try:
            data = conn.recv(1024).decode("utf-8").strip().lower()
        except: 
            continue
        if data == "n":
            game = Board(tiles)
            game_list.append(game)
            break
        if data == "q":
            conn.close()
            sys.exit(0)
        if data.isdigit():
            which_game = int(data)
            if 0 <= which_game < len(game_list):
                game = game_list[which_game]
                break
    return game

def user_settings(conn, game):
    """User sets settings, such as display name and color."""
    # TODO possibly: spectators?
    while True:
        conn.send(bytes("Type in your name, desired character(@ # % or &), and color (\033[31;1m1\033[32;1m2\033[33;1m3\033[0m) without using anyone else's\n".encode("utf-8")))
        for player in game.players:
            conn.send(bytes("{} - {}\n".format(player.name, player).encode("utf-8")))
        data = conn.recv(1024).decode("utf-8").strip().lower().split()
        if len(data) != 3: 
            continue
        if len(data[1]) != 1 and not data[1] in "@#%&": 
            continue
        if not data[2].isdigit():
            continue
        if (data[2].isdigit() and not (1 <= int(data[2]) <= 3)): 
            continue
        name, char, color = data
        color = int(color)
        if name in [p.name for p in game.players]: 
            continue
        if char in [p.char for p in game.players]: 
            continue
        if color in [p.color for p in game.players]:    
            continue
        you = User(color, char, name, conn)
#        game.add_player(you)
        game.broadcast("{} joined the game!".format(you))
        break
    return you

def main_loop(conn, you, game):
    """Handles the main loop of a game."""
    jail_methods = {"b": game.pay_bail, "c": game.use_card, "r": game.roll_to_leave_jail,
                    "bail": game.pay_bail, "card": game.use_card, "roll": game.roll_to_leave_jail}
    while True:
        if game.current_player:
            you = game.current_player
        try:
            raw = conn.recv(1024)
            print(type(raw))
            raw = raw.decode("utf-8")
            print(type(raw))
            raw = conn.recv(1024).decode("utf-8").strip()
            print(raw)
            data = raw.lower()
        except:
            continue

        if game.phase == "GAMEOVER":
            game.show_board()
            continue

        split = data.split()
        if len(split) == 0: continue
        split = [w.lower() for w in split]
        if len(data) > 1 and data.startswith("/"):
            game.broadcast("{} ({}): {}".format(you.name, you, raw[1:]))
        if not game.started:
            if you == game.creator and data == "s":
                game.begin()
            continue

        if game.current_trade:
            #TODO: debug
            game.accept_trade()
            continue
            offeree = game.current_trade[1]
            if data in ["a", "accept", "y", "yes"]:
                game.accept_trade()
            if data in ["d", "decline", "n", "no"]:
                game.decline_trade()
        if game.in_auction:
            if data.isdigit():
                game.handle_bid(you, int(data))
            continue

        if you == game.current_player:
            if game.phase == "roll":
                if you.jailed:
                    if data in jail_methods.keys():
                        jail_methods[data]()
                elif data in ["r", "roll", ""]:
                    game.player_rolls()
            elif game.phase == "buy":
                if data in ["buy", "b"]:
                    if isinstance(you.tile, PropertyTile) and you.tile.buy(you):
                        game.phase = "accounts"
                    else:
                        continue

                #TODO: does this block belong here?
                if len(split) == 2 and split[0] in ["sell", "s"]:
                    game.sell_tile(you, split[1])
                        
                elif data in ["auction", "a"]:
                    game.broadcast("{} is going up for auction!  Any player can type any amount.".format(you.tile.name))
                    game.in_auction = True
                    game.highest_bid = (None, 0)
                    game.auction_timer = threading.Thread(target = game.handle_auction, args=(you.tile,))
            elif game.phase == "debt":
                if len(split) == 2 and split[0] in ["s", "sell"]:
                    game.sell_tile(you, split[1])
                    
            elif game.phase == "accounts":
                if data in ["p", "pass"]:
                    game.next_turn()

                if data in ["a", "accounts"]:
                    you.send("[h] or [i] to improve lot to house or hotel.  [s] to sell a house/hotel. [m] to mortage a lot.")
                    game.show_player_info(you)
                elif len(split) == 2 and split[0] in ["h", "house", "hotel", "i", "improve", "b", "buy"]:
                    for tile in game.tiles:
                        if type(tile) is BuildableTile and tile.label == split[1] and tile.owner == you:
                            if tile.can_be_improved():
                                tile.improve()
                                game.SHOW_BOARD()

                            break
                elif len(split) == 2 and split[0] in ["s", "sell"]:
                    game.sell_tile(you, split[1])
                elif split[0] in ["t", "trade"]:
                    trade = game.parse_trade(you, split)
                    print(trade)
                    if trade:
                        game.current_trade = trade
                        continue

    conn.close()

def handle_connection(conn, game_list):
    """Handles a connection to the server."""
    game = game_menu(conn, game_list)
    if debug:
        colors = [1, 2, 3]
        names = ["abby", "becky", "charlie"]
        names = ["Player1", "Player2", "Player3"]
        chars = ["@", "#", "&"]
        you = User(colors[len(game.players)], chars[len(game.players)], names[len(game.players)], conn)
    else: 
        you = user_settings(conn, game)
    game.add_player(you)
    if you == game.creator: 
        you.send("Type 'S' to begin the game after everyone has joined.")
    main_loop(conn, you, game)

debug = False
if __name__ == "__main__":
    HOST = ""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print("Bind failed.  Error Code: {}; Message: {}".format(str(msg[0], msg[1])))
        sys.exit(4)
    s.listen(10)
    game_list = []
    conns = []
    while True:
        conn, addr = s.accept()
        conns.append(conn)
        thread = threading.Thread(target=handle_connection, args=(conn, game_list))
        thread.start()
    s.close()

