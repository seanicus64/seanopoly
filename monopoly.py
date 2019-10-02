#!/usr/local/bin/python3.7
PORT = 8888
#!/usr/bin/env python3.7
import socket
import threading
import random
import sys
import textwrap
import time
class User:
    money = 1500
    def __init__(self, color, char, name, conn=None):
        self.color_code = "\033[3{};1m".format(color)
        self.color = color
        self.char = char
        self.name = name
        self.conn = conn
        self.tile = None
        self.jailed = False
        self.num_cards = 0
        self.rolls = []
    def send(self, message):
        self.conn.send(bytes((message+"\n").encode("utf-8")))
    def rolled_doubles(self):
        """Returns True if last roll was doubles."""
        if self.rolls[-1][0] == self.rolls[-1][1]:
            return True
        return False
    def __str__(self):
        return self.color_code + self.char + "\033[0m"
    def __repr__(self):
        return self.name
class Group:
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
    def __init__(self, name, width=5):
        self.occupants = []
        self.name = name
        self.width=width

    def print_top(self):
        return "     "
#        return " " * self.width

    @property
    def o(self):
        return self.print_occupants()    

    def print_occupants(self):
        string = ""
        occupant_graphic = ""
        for o in self.occupants:
            occupant_graphic += str(o)
        if len(self.occupants) == 0:
#            occupant_graphic = " " * (self.width + 1)
            occupant_graphic = "     "
        elif len(self.occupants) == 1:
            occupant_graphic = "   {}  ".format(*self.occupants)
        elif len(self.occupants) == 2:
            occupant_graphic = " {} {}  ".format(*self.occupants)
        elif len(self.occupants) == 3:
            occupant_graphic = "{} {} {} ".format(*self.occupants)
        elif len(self.occupants) == 4:
            occupant_graphic = " {}{}{}{} ".format(*self.occupants)
#        occupant_graphic += " " * ((self.width+1) - (len(occupant_graphic)))
        occupant_graphic += " "
        return occupant_graphic

    def on_landing(self, player):
        self.game.broadcast("Nothing happened!  Maybe sean didn't put functionality in yet for this tile...")
        self.game.end_buy_phase()
        
class PropertyTile(GeneralTile):
    """Base for all tiles which a player can buy."""
    owner = None
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []

    def buy(self, player):
        print("buy function went through")
        self.owner = player
        player.money -= self.prices["printed"] #TODO: enough money?
        self.game.show_board()
        self.game.broadcast("{} bought the deed for {}".format(player.name, self.name))
        self.game.end_buy_phase()
    def info(self):
        
        string = """{} - Owner: {} ({}), current rent: {}""".format(self.name, self.owner.name, self.owner, self.determine_rent())
        return string
    @property
    def t(self):
        return self.print_top()

    def print_top(self):
        if self.owner:
            return "{}[    ]{}\033[0m".format(self.owner.color_code, self.owner.color_code)
        else:
            return "      "

    def on_landing(self, player):
        amount = 0
        if self.owner:
            if self.owner != player:
                # TODO: differnet rents...
                amount = self.determine_rent()
                player.money -= amount
                player.send("You paid {} in rent".format(amount))
            self.game.end_buy_phase()
        elif not self.owner:
            player.send("No one owns this property.  Would you like to [B]uy it or let it go to [A]uction?")
            self.game.phase = "buy"
            self.game.buying_query = True

class CommunityTile(GeneralTile):
    """Tile for both Community Chest spaces."""
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
class TaxTile(GeneralTile):
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
class RailroadTile(PropertyTile):
    prices = {"printed": 200, "mortgaged": 100}
    def __init__(self, name, label, width=5):
        self.name = name
        self.width = width
        self.label = label
        self.occupants = []
    def on_landing(self, player):
        if not self.owner:
            player.send("No one owns this property.  Would you like to [B]uy it or let it go to [A]uction?")
        elif self.owner:
            if self.owner != player:
                rent = 25 * self.game.check_other_rrs_owned(self)
                self.game.broadcast("{} paid ${} rent to {}".format(player.name, rent, self.owner.name))
            self.game.end_buy_phase()
    def determine_rent(self):
        #TODO
        return 0

class JailTile(GeneralTile):
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.slots = [" "] * 4

    def show_visitor(self, slot):
        pass
class UtilityTile(PropertyTile):
    prices = {"printed": 200, "mortgaged": 100} #TODO: change
    def __init__(self, name, label, width=5):
        self.name = name
        self.width = width
        self.label = label
        self.occupants = []
    def on_landing(self, player):
        if not self.owner:
            player.send("No one owns this property.  Would you like to [b]uy it or let it go to [A]uction?")
        elif self.owner:
            if self.owner != player:
                game.broadcast("{} paid {} to {}".format(player.name, "??", self.owner.name))    
            self.game.end_buy_phase()

    def determine_rent(self):
        #TODO
        return 0
class FreeParkingTile(GeneralTile):
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
        self.slots = [" "] * 4
class ChanceTile(GeneralTile):
    def __init__(self, name, width=5):
        self.name = name
        self.width = width
        self.occupants = []
class GoToJailTile(GeneralTile):
    def on_landing(self, player):
        self.game.send_to_jail(player)
class BuildableTile(PropertyTile):
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

    def determine_rent(self):
        if self.hotel:
            return self.rents["hotel"]
        if not self.num_houses:
            if self.is_monopoly:
                return self.rents[0] * 2
        return self.rents[self.num_houses]
    
    def is_monopoly(self):
        if None in [t.owner for t in self.group.tiles]:
            return False
        num_owners = len(set([t.owner for t in self.group.tiles]))
        if num_owners == 1:
            return True
        return False

    def can_be_improved(self):
        if not self.is_monopoly(): return False
        for tile in self.group.tiles:
            if tile is self: continue
            if self.num_houses > tile.num_houses:
                return False
        return True
    def can_be_dismantled(self):
        if not self.is_monopoly: return False
        for tile in self.group.tiles:
            if tile is self: continue
            if self.num_houses < tile.num_houses:
                return False
            return True
    def sell_house(self):
        if not self.owner: return
        if self.hotel:
            self.hotel = False
            self.owner.money += int(self.prices["building"]//2)
        elif self.num_houses:
            self.num_houses -= 1
            self.owner.money += int(self.prices["building"]//2)


    def improve(self):
        if not self.owner: return
        if self.hotel: return
        if self.num_houses < 4:
            self.num_houses += 1
            self.owner.money -= self.prices["building"]
        elif self.num_houses == 4:
            self.hotel = True
    def print_top(self):
        string = ""
        if self.owner:
            string += self.owner.color_code + "["
        if self.hotel:
            building_graphic = " HH "
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
    def __init__(self, tiles):
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

        tile_iterator = iter(self.tiles[1:])
        for next_tile in tile_iterator:
            current_tile.next_tile = next_tile
            current_tile.game = self
            current_tile = next_tile
        next_tile.next_tile = self.tiles[0] 
        next_tile.game = self

        self.cells = [" ", " ", " ", " "]

    def broadcast(self, message):
        """Sends a message to every player."""
        for p in self.players:
            p.conn.send(bytes((message + "\n").encode("utf-8")))

    def show_board(self):
        """Shows the current state of the game to everyone."""
        self.broadcast(str(self))

    def add_player(self, player):
        """Adds a new player to the game before it starts."""
        if not self.started:
            self.players.append(player)
            if len(self.players) == 1:
                self.creator = player
        self.broadcast("{}({}) joined the game!".format(player.name, player))

    def begin(self):
        """Initializes the beginning of the game."""
        random.shuffle(self.players)
        self.started = True
        self.current_player = self.players[0]
        self.tiles[0].occupants = self.players.copy()
        self.show_board()
        self.broadcast("The game has begun!")
        order = ", ".join(["{} ({})".format(p.name, p) for p in self.players])
        self.broadcast("The order of play is {}".format(order))
        self.current_player.send("It is your turn! [R]oll the dice by typing 'R'.")

        #amount_to_move = self.roll_dice()
        #self.advance_player(self.current_player, amount_to_move)

    def player_rolls(self):
        amount = self.roll_dice()
        if len(self.current_player.rolls) >= 3:
            is_double = True
            for roll in self.current_player.rolls[-3:]:
                if not roll[0] == roll[1]:
                    is_double = False
            if is_double:
                self.send_to_jail(self.current_player)
        self.phase = "buy"
        self.buying_query = True
        self.advance_player(self.current_player, amount)
        self.broadcast_after_roll(self.current_player.rolls[-1][0], self.current_player.rolls[-1][1])
        if hasattr(self.current_player.tile, "on_landing"):
            self.current_player.tile.on_landing(self.current_player)
    def broadcast_after_roll(self, roll1, roll2):
        """Sends messages to everyone after the board changes after a roll."""
        self.broadcast(str(self))
        message = "{} rolled a {}-{} and landed on {}.".format(self.current_player.name, roll1, roll2, self.current_player.tile.name)
        if self.current_player.tile.name == "Jail":
            message += "  They're just visiting, though!"
        self.broadcast(message)
    def roll_dice(self):
        """Determines how far to move the player."""
        die1 = random.randrange(1, 7)
        die2 = random.randrange(1, 7)
        self.current_player.rolls.append((die1, die2))
        return die1 + die2

    def next_turn(self):
        """Starts the turn for the next player, moves them and prompts them."""
        which_player = self.players.index(self.current_player)
        which_player += 1
        which_player = which_player % len(self.players)
        self.current_player = self.players[which_player]
        self.phase = "buy"
        self.phase = "roll"
        if self.current_player.jailed:
            self.current_player.send("You are in jail.  To leave you can pay $50 [B]ail, attempt to [R]oll a double, or play a Get Out of Jail Free [C]ard.")
            return
        self.current_player.send("It is your turn!  [R] the dice by typing 'R'.")

    def advance_player(self, player, amount):
        """Moves a player to a new tile."""
        self.broadcast("{} rolled {}".format(player.name, amount))
        which_tile = None
        for t in self.tiles:
            if player in t.occupants:
                which_tile = t
                break
        print(type(which_tile))
        if not which_tile and player.jailed:
            which_tile = self.tiles[10]
        else:
            which_tile.occupants.remove(player)
        current_tile = which_tile
        if current_tile.name in ["Jail", "Free Parking"]:
            current_tile.slots = [" " if s == player else s for s in current_tile.slots]
        for i in range(amount):
            current_tile = current_tile.next_tile
        current_tile.occupants.append(player)
        if current_tile.name in ["Jail", "Free Parking"]:
            while True:
                which_slot = random.randrange(4)
                if current_tile.slots[which_slot] != " ":
                    continue
                current_tile.slots[which_slot] = player
                break
        player.tile = current_tile

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
        self.broadcast(str(self))
        self.broadcast("Auction over!")
        self.broadcast("{} bought {} for {}".format(self.highest_bid[0], tile.name, self.highest_bid[1]))
        self.end_buy_phase()

    def end_buy_phase(self):
        """After a PropertyTile is bought, ask the player if they want to buy/sell houses, etc"""
        self.phase = "accounts"
        if self.current_player.rolls[-1][0] == self.current_player.rolls[-1][1] and not self.current_player.jailed:
            self.current_player.send("Do you want to handle your [a]ccounts or [r]oll again?")
        else:
            self.current_player.send("Do you want to handle your [a]ccounts or [p]ass to the next person's turn?")

    # Jail stuff
    def send_to_jail(self, player):
        player.tile.occupants.remove(player)
        player.tile = None
        while True:
            which_cell = random.randrange(4)
            if self.cells[which_cell] == " ":
                break
        self.cells[which_cell] = player
        player.jailed = True
        self.end_buy_phase()
    def pay_bail(self):
        """Current player pays the bail, advances."""
        player = self.current_player
        if player.money >= 50:
            player.money -= 50
        else: return
        amount = self.roll_dice()
        self.leave_jail(player, amount)

    def use_card(self):
        """Current player uses their Get Out of Jail Free Card, advances."""
        player = self.current_player
        if player.num_cards >= 0:
            player.num_cards -= 1
            amount = self.roll_dice()
            self.leave_jail(player, amount)
            return

    def roll_to_leave_jail(self):
        """Current player attempts to roll doubles to get out of jail, may advance."""
        player = self.current_player
        amount = self.roll_dice()
        if player.rolled_doubles():
            self.leave_jail(player, amount)

    def leave_jail(self, player, amount):
        """Current player leaves jail, advances."""
        if player.jailed:
            player.jailed = False
        else: return
        for cell in self.cells:
            if cell == player:
                self.cells[self.cells.index(cell)] = " "
        
        player.tile = self.tiles[10]
        self.tiles[10].occupants.append(player)
        self.advance_player(player, amount)

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
        amount = int(amount)
        if self.highest_bid[1] < amount < player.money:
            self.highest_bid = (player, amount)
            if not self.auction_timer.is_alive():
                self.auction_timer.start()
            self.seconds_left = 21

        
    def __str__(self):
        t = self.tiles
        board = """\
        +-----+------+------+------+------+------+------+------+------+------+-------+
        |     |{}|{}|  ?   |{}|{}|      |{}|      |{}|       | 
        |JAIL |  CT  |  VT  |      |Orient|Readng|INCOME|Baltic|Commun|Medit | <---- | 
        |     | Ave  | Ave  |CHANCE| Ave  |  RR  | TAX  |  Ave |Chest | Ave  |   GO  | 
        |==+  |{}|{}|{}|{}|{}|{}|{}|{}|{}|{}| 
        |{} |  | 120  | 100  |  ?   | 100  | 200  | -200 |  60  |      |  60  |  +200 | 
        |==|{} +------+------+------+------+------+------+------+------+------+-------+ 
        |{} |  |                                                                      
        |==|{} +------+------+------+------+------+------+------+------+------+-------+
        |{} |  |{}|{}|{}|{}|{}|{}|      |{}|{}|       |
        |==|{} |St.Cs'|Electr|States|  VA  |  PA  |SJames|Commun|  TN  |  NY  | \{}\ \ | 
        |{} |  |Place |  Co  | Ave  | Ave  |  RR  |Place |Chest |  Ave | Ave  |  \ \ \| 
        |==+{} |{}|{}|{}|{}|{}|{}|{}|{}|{}|       | 
        |     |  140 | 150  |  140 |  160 | 200  |  180 |      |  180 |  200 | \{}\ \ | 
        +--||-+------+------+------+------+------+------+------+------+------+  \ \ \| 
           ||                                                                |  FREE | 
        +--||-+------+------+------+------+------+------+------+------+------+  PARK | 
        |     |{}|{}|{}|{}|{}|{}|{}|  ?   |{}|  ING  | 
        |     |Marvin|Water |Ventnr|Atlant| B&O  |  IL  |  IN  |      |  KY  | \ \{}\ | 
        |     |Gardns| Works| Ave  | Ave  |  RR  | Ave  |  Ave |CHANCE| Ave  |  \ \ \| 
        |  ^  |{}|{}|{}|{}|{}|{}|{}|{}|{}|       | 
        |  |  |  280 |  150 |  260 |  260 | 200  |  240 |  220 |  ?   |  220 | \{}\ \ | 
        |     +------+------+------+------+------+------+------+------+------+-------+ 
        | GO  |                                                                          
        | TO  +------+------+------+------+------+------+------+------+------+          
        |JAIL |{}|{}|      |{}|{}|  ?   |{}|      |{}|
        |     |Pacifc|  NC  |Commun|  PA  |Short |      |Park  |Luxury|Board |
        |     | Ave  |  Ave |Chest | Ave  |  Line|CHANCE| Place| Tax  | walk |
        |     |{}|{}|{}|{}|{}|{}|{}|{}|{}|
        |     |  300 |  300 |      |  320 |  200 |  ?   |  350 | -100 |  400 |          
        +---------------------------------------------------------------------         """ 
        return textwrap.dedent(board.format(
            t[9].t, t[8].t,         t[6].t, t[5].t,         t[3].t,         t[1].t, 
            t[9].o, t[8].o, t[7].o, t[6].o, t[5].o, t[4].o, t[3].o, t[2].o, t[1].o, t[0].o, 

            self.cells[0], t[10].slots[0], self.cells[1], t[10].slots[1], self.cells[2],

            t[11].t, t[12].t, t[13].t, t[14].t, t[15].t, t[16].t,          t[18].t, t[19].t, #"F",
            t[10].slots[2], t[20].slots[0], self.cells[3], t[10].slots[3], 
            t[11].o, t[12].o, t[13].o, t[14].o, t[15].o, t[16].o, t[17].o, t[18].o, t[19].o, t[20].slots[1],

            t[29].t, t[28].t, t[27].t, t[26].t, t[25].t, t[24].t, t[23].t,          t[21].t, t[20].slots[2],
            t[29].o, t[28].o, t[27].o, t[26].o, t[25].o, t[24].o, t[23].o, t[22].o, t[21].o, t[20].slots[3],

            t[31].t, t[32].t,          t[34].t, t[35].t,          t[37].t,          t[39].t, 
            t[31].o, t[32].o, t[33].o, t[34].o, t[35].o, t[36].o, t[37].o, t[38].o, t[39].o, 

        ))
sean = User(3, "&", "sean")
fred = User(4, "@", "fred")
abby = User(2, "%", "abby")
becky = User(5, "#", "becky")

first = Group(2, 1)
second = Group(6, 2)
third = Group(3, 3)
fourth = Group(4, 4)
fifth = Group(7, 5)
sixth = Group(1, 6)
seventh = Group(5, 7)
eighth = Group(0, 8)
cells = []
parking_spots = []
just_visiting = []
go_spots = []


tiles = [
    GeneralTile(
        name = "Go",
        width = 7),
    BuildableTile(
        group = first,
        name = "Meditterranean Avenue",
        label = "1a",
        rents = {0: 2, 1: 10, 2: 30, 3: 90, 4: 160, "hotel": 250},
        prices = {"printed": 60, "mortaged": 30, "building": 50}),
    CommunityTile(
        name = "Community Chest"),
    BuildableTile(
        group = first,
        name = "Baltic Avenue",
        label = "1b",
        rents = {0: 4, 1: 20, 2: 60, 3: 180, 4: 320, "hotel": 450},
        prices = {"printed": 60, "mortgaged": 30, "building": 50}),
    TaxTile(
        name = "Income Tax"),
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
        name = "Luxury Tax"),
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
        data = conn.recv(1024).decode("utf-8").strip().lower()
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
        game.add_player(you)
        game.broadcast("{} joined the game!".format(you))
        break
    return you

def main_loop(conn, you, game):
    jail_methods = {"b": game.pay_bail, "c": game.use_card, "r": game.roll_to_leave_jail,
                    "bail": game.pay_bail, "card": game.use_card, "roll": game.roll_to_leave_jail}
    while True:
        try:
            data = conn.recv(1024).decode("utf-8").strip().lower()
        except:
            continue
        split = data.split()
        split = [w.lower() for w in split]

        if not game.started:
            if you == game.creator and data == "s":
                game.begin()
            continue

        if game.in_auction:
            if data.isdigit():
                game.handle_bid(you, int(data))
            continue
        # five phases:
        # roll - roll to move, in jail, take getting-out-of-jail move
        # buyint - Either buy a property, or put it up for auction
        # accounts - build houses/hotels, selll, mortgage, trade
        # auction - any player can make a bid for an auction
        # acknowledgement - informs player of something happening before doing it
        if you == game.current_player:
            if game.phase == "roll":
                if you.jailed:
                    if data in jail_methods.keys():
                        jail_methods[data]()
                elif data in ["r", "rolls"]:
                    game.player_rolls()
                elif debug and data.isdigit():
                    game.advance_player(you, int(data))
            elif game.phase == "buy":
                if data in ["buy", "b"]:
                    try:
                        you.tile.buy(you)        
                        game.building_query = False
                        game.phase = "accounts"
                    except Exception as e:
                        print(e)
                elif data in ["auction", "a"]:
                    game.broadcast("{} is going up for auction! Any player can type any amount.".format(you.tile.name))
                    game.in_auction = True
                    game.highest_bid = (None, 0)
                    game.auction_timer = threading.Thread(target = game.handle_auction, args=(you.tile,))
            elif game.phase == "accounts":
                #TODO: trade, mortgage
                if len(split) == 2 and split[0] in ["improve", "house", "hotel", "i", "h"]:
                    for tile in game.tiles:
                        if type(tile) is BuildableTile and tile.label == split[1] and tile.owner == you:
                            if tile.can_be_improved():
                                tile.improve()
                if data in ["sell", "s"]:
                    for p in split[1:]:
                        which_property = None
                        for t in game.tiles:
                            if not hasattr(t, "label"): continue
                            if t.label == p:
                                which_property = t
                        if not which_property: continue
                        try:
                            which_property.sell_house()
                        except: continue
                if data in ["pass", "p"]:
                    game.next_turn()
        if data == "map":
            you.send(str(game))
        if len(split) == 2 and split[0].lower() == "info":
            label = split[1].lower()
            for tile in game.tiles:
                if hasattr(tile, "label") and tile.label == label:
                    you.send(tile.info())
                    break
        if data == "change":
            game.next_turn()
        if data == "me":
    
            game.show_player_info(you)
                        
                    
        #if game.phase == "roll":
        #if game.phase == "accounts" and you == game.current_player:
        #    if data == "p":
        #        game.next_turn()
    conn.close()
def handle_connection(conn, game_list):
    print("connection started")
    conn.send(bytes("hello!".encode("utf-8")))
    game = game_menu(conn, game_list)
    if debug:
        colors = [1, 2, 3]
        names = ["abby", "becky", "charlie"]
        chars = ["@", "#", "&"]
        you = User(colors[len(game.players)], chars[len(game.players)], names[len(game.players)], conn)
    else: 
        you = user_settings(conn, game)
    game.add_player(you)
    if you == game.creator: 
        you.send("Type 'S' to begin the game after everyone has joined.")
    main_loop(conn, you, game)

debug = True
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
        print("Connected with {}: {}".format(addr[0], str(addr[1])))
        thread = threading.Thread(target=handle_connection, args=(conn, game_list))
        thread.start()

    s.close()

