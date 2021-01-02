import random
import chance
import vis
from tiles import Group, GeneralTile, PropertyTile, TaxTile, RailroadTile
from tiles import UtilityTile, FreeParkingTile, CommunityTile, ChanceTile
from tiles import GoToJailTile, BuildableTile, JailTile


class User:
    _money = 1500
    trying_to_quit = False
    connected = True
    #_money = 10
#    _money = 150000000000
    def __init__(self, color, char, name, ascii_mode, conn=None):
        self.color = color
        self.char = char
        self.name = name
        self.ascii_mode = ascii_mode
        self.conn = conn
        self.color_code = "\033[3{};1m".format(color)
        self.tile = None
        self.jailed = False
        self.num_cards = 0  # get out of jail free cards
        self.num_cards = 1  # TODO: debugging
        self.rolls = []
        self.obtainable_wealth = 0  # amount of money player will have if they sell everything
                                    # distinct from worth in that mortgaged props only give you half
        # very unlikely that a sequence will reappear but...
#        while True:
#            self.code = ""
#            for i in range(10):
#                self.code += random.choice(letters)
#            if self.code not in [p.code for p in all_players]:
#                break
        self.make_code()            
        self.in_debt = False
        self.indebted_to = None
        self.bankrupt = False

    def make_code(self):
        letters = "abcdefghjkmnpqrstuvwxyz"
        self.code = ""
        for i in range(10):
            self.code += random.choice(letters)
        
    @property
    def money(self):
        return self._money
    @money.setter
    def money(self, amount):
        # first thing is to resolve any debt
        if self.in_debt and self.indebted_to and amount > 0:
            owed = abs(self._money)
            self._money += amount
            self.indebted_to.money += min(owed, amount)
            print("{} got {}".format(self.indebted_to, min(owed, amount)))
        print(self._money, amount, "<--amount of money being given to you") 
        self._money = amount
        self.in_debt = False
        if self._money < 0:
            self.in_debt = True
            

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
        
        
class Board():
    """The object that represents the game as a whole."""
    turn = 0
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
        self.chat_messages = []

        tile_iterator = iter(self.tiles[1:])
        for next_tile in tile_iterator:
            current_tile.next_tile = next_tile
            current_tile.game = self
            current_tile = next_tile
        next_tile.next_tile = self.tiles[0] 
        next_tile.game = self

        self.cells = [" ", " ", " ", " "] # representing players in jail

    def advance_to_nearest_tiletype(self, tiletype, player):
        tt_dict = {"utility": UtilityTile, "railroad": RailroadTile}
        tiletype = tt_dict[tiletype]
        current = player.tile
        while True:
            # "Advance to nearest" is understood by the community to always mean /forward/.
            current = current.next_tile
            # per the rules, if you pass GO whether through a roll OR CARD, collect 200.
            #if current == self.tiles[0]:
            #    player.money += 200 #TODO: maybe use pay_amount function
            if isinstance(current, tiletype):
                break

        self.move_player(player, current, override=True)
        return current

    def pay_amount(self, player, recipient, amount):
        """Player pays another player or the bank."""
        print("PAYING AMOUNT: " + str(amount))
        # When penultimate player runs out of money, game is over.
        print(000000000)
        if amount > player.worth:
            print(111111, player.worth)
            self.declare_bankrupcy(player, recipient, amount)
            if self.phase == "GAMEOVER":
                return
        # Player ran out of hard cash, must sell properties before turn can continue
        elif amount > player.money:
            print(222222222, player.worth)
            print("{} paying {}".format(player.name, amount))
            if recipient != "bank":
                recipient.money += player.money
            #player.debt = amount - player.money
            #self.phase = "debt"
            #print("player still owes {}".format(player.debt))
            player.money -= amount
            self.messages.append("{} paid {} but still owes {}.".format(player, amount + player.money, -1 * player.money))
            player.indebted_to = recipient
            return

        
        else:
            player.money -= amount
            if recipient != "bank":
                recipient.money += amount
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
#        string = ""
#        string += str(self)
        for e, p in enumerate(self.players, 1):
            string = ""
            if p.ascii_mode:
                string += vis.show_board(self, "basic")
            else:
                string += vis.show_board(self, "fancy")

            if p == self.current_player: string += ">"
            else: string += " "
            string += "{}: {} ({}): ${}\n".format(e, p.name, p, p.money)
            string += "Current player: {} ({}), has ${} (${} including property) -- {}\n".format(self.current_player.name, self.current_player, self.current_player.money, self.current_player.worth, self.current_player.obtainable_wealth)
            for m in self.messages:
                string += m + "\n"
#        for p in self.players:
#            if p == self.current_player: continue
            if p == self.current_player:
                string += self.prompt
                self.promot = ""
                self.messages = []
            
            p.send(string)
            #except:
            #    pass

#        string += self.prompt
#        self.prompt = ""
#        self.messages = []
#        self.current_player.send(string)

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

        #TODO: debugging----------------
        self.tiles[15].owner = self.players[1]

        self.tiles[5].owner = self.players[1]
        self.tiles[25].owner = self.players[1]
        self.tiles[35].owner = self.players[1]
        #self.tiles[-1].owner = self.players[0]
        #self.tiles[-3].owner = self.players[0]
        #self.tiles[-1].num_houses = 2
        #self.tiles[-3].num_houses = 2
        #self.tiles[-11].owner = self.players[1]
        #self.tiles[-13].owner = self.players[1]
        #self.tiles[-14].owner = self.players[1]
        #self.tiles[-11].num_houses = 4
        #self.tiles[-13].num_houses = 4
        #self.tiles[-14].num_houses = 4
        #self.tiles[12].owner = self.players[1]

        #-------------------------------

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
        if self.turn == 0:
            amount = 7 # TODO: debugging for chance
        if self.turn == 1:
            amount = 39
        self.turn += 1
        if len(self.current_player.rolls) >= 3:
            is_double = True
            for roll in self.current_player.rolls[-3:]:
                if not roll[0] == roll[1]:
                    is_double = False
            if is_double:
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

    def roll_dice(self, override=False):
        """Determines how far to move the player."""
        die1 = random.randrange(1, 7)
        die2 = random.randrange(1, 7)
        # usually rolling dice is to move player, but for cards it can do other things
        if not override:
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
            self.prompt = "It is your turn! Enter 'R' to roll the dice."
        self.SHOW_BOARD()
    
    def move_player(self, player, tile, override=False):
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
            player.money += 200 #TODO: this is passing go, maybe a specific function for that?
        if override:
            return
        if hasattr(whither, "on_landing"):
            whither.on_landing(player)
        
        if whence.name in ["Jail", "Free Parking"]:
            whence.slots = [" " if s == player else s for s in whence.slots]
        if whither.name in ["Jail", "Free Parking"]:
            self.put_in_random_slot(player, whither)
            
    def get_next_tile(self, player, amount, single=False):
        """Returns the tile a player is moving to."""
        current_tile = player.tile
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
                    current_tile.footprints.add(player)
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
        self.seconds_left = 11

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
        #TODO: this raised an error once, saying current_player can't be NoneType, after player was sent to jail after chance card during first turn
        if self.current_player.in_debt:
            self.prompt = "You must resolve your debt before you can continue."
        elif self.current_player.rolls[-1][0] == self.current_player.rolls[-1][1] and not self.current_player.jailed:
#            self.prompt = "Do you want to handle your [a]ccounts or [r]oll again?"
            #TODO: implement rolling again!
            self.prompt = "Do you want to handle your [a]ccounts or [p]ass to the next person's turn?"
        else:
            self.prompt = "Do you want to handle your [a]ccounts or [p]ass to the next person's turn?"

    def send_to_jail(self, player):
        """Moves a player to jail."""
        if hasattr(player.tile, "occupants"):
            player.tile.occupants.remove(player)
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
        string = ""
        string += "Cash on hand: ${}; Total worth: ${}\n".format(player.money, player.worth)
        jail_string = "Jail-free cards: {}\n".format(player.num_cards)
        string += jail_string
#        player.send("{} ({}) - ${}".format(player.name, player, player.money))
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
        string += owned_string
        player.send(string)

    def check_other_rrs_owned(self, tile):
        """Check how many other railroads the player owns."""
        owner = tile.owner
        owned = filter(lambda t: t.owner == owner, (self.tiles[5], self.tiles[15], self.tiles[25], self.tiles[35]))
        return(len(list(owned)))
            
    def handle_bid(self, player, amount):
        """Handles a bid for an auction."""
        amount = int(amount)
        if self.highest_bid[1] < amount <= player.money:
            self.highest_bid = (player, amount)
            if not self.auction_timer.is_alive():
                self.auction_timer.start()
            self.seconds_left = 11

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
            p.owner = player
        for p in offered_stuff["properties"]:
            p.owner = offeree

        self.current_trade = None

    def help(self, player):
        example_tile = """
        1: +------+      
        2: |[====]|   color = which group, color of brackets = owner, # = house
        3: |  KY  |   Property name
        4: | Ave  |   Property name [cont]
        5: | # @  |   Players on property
        6: |  220 |   Cost of property without buildings
        7: +--5a--+   property id
        """
        player.send(example_tile)

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
            return None

        offer = [player, offeree, offered_stuff, for_stuff]
        offered_string = ""
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
    def add_chat(self, user, message):
       log = "{} ({}): {}".format(user.name, user, message)
       self.broadcast(log)
       self.chat_messages.append(log)
            
        
    def __str__(self):
        return  vis.show_board(self, "basic")


