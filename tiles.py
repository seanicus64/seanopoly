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
                graphic = "\033[{};7m{}\033[0m".format(o.color, str(o))
            else:
                graphic = str(o)
            occupant_graphics.append(graphic)
        for f in self.footprints:
            occupant_graphics.append("\033[3{};1m*\033[0m".format(f.color))
        if len(occupant_graphics) == 0:
            occupant_graphic = "     "
        elif len(occupant_graphics) == 1:
            occupant_graphic = "   {}  ".format(*occupant_graphics)
        elif len(occupant_graphics) == 2:
            occupant_graphic = " {} {}  ".format(*occupant_graphics)
        elif len(occupant_graphics) == 3:
            occupant_graphic = "{} {} {} ".format(*occupant_graphics)
        elif len(occupant_graphics) == 4:
            occupant_graphic = " {}{}{}{} ".format(*occupant_graphics)
        occupant_graphic += " " * ((self.width+1) - (len(occupant_graphic)))

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
            pass
        elif player.obtainable_wealth >= self.prices["printed"]:
            self.game.messages.append("You must sell property before you can afford this")
        else:
            self.game.messages.append("You cannot afford this even if you sold everything. Maybe just let it go to [a]uction")

    def buy(self, player):
        """Player buys the property."""
        if self.owner:
            player.send("This property is not for sale!")
            return
        try:
            assert player.money >= self.prices["printed"]
        except: 
            return False
        self.owner = player
        player.money -= self.prices["printed"]
        self.game.add_message("{} bought the deed for {}".format(player.name, self.name))
        self.game.end_buy_phase()
        self.game.SHOW_BOARD()
        return True

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
        player = self.game.current_player
        player.money += amount
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
                print("hhhhhhhhhhhhhh")
                self.game.pay_amount(player, self.owner, amount)
                print("jjjjjjjjjjjjjjj")
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
                rent = self.determine_rent()
                self.game.add_message("{} paid ${} rent to {}".format(player.name, rent, self.owner.name))
            self.game.end_buy_phase()

    def determine_rent(self):
        """Returns how much rent a landing player owes to the owner."""
        rent = 25

        for i in range(self.game.check_other_rrs_owned(self) - 1):
            rent *= 2
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
        print("utility on_landing")
        if not self.owner:
            print("there is no owner")
            self.game.prompt = "No one owns this property. Would you like to [b]uy it or let it go to [a]uction?"
        elif self.owner:
            print("there is an owner")
            if self.owner != player:
                print("owner is not hte player")
                rent = self.determine_rent()
                self.game.add_message("{} paid ${} to {}".format(player.name, rent, self.owner.name))    
            print("ending the buy phase")
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

        if actual_amount == -1:
            return False
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
        string += "\033[0m" + self.group.color_code + building_graphic
        if self.owner:
            string += self.owner.color_code + "]"
        string += "\033[0m"
        return string
