import random
class Deck:
    def __init__(self, game):
        self.game = game
    def shuffle(self):
        random.shuffle(self.deck)
    def change_money(self, player, amount):
        player.money += amount
    def act_on_card(self, player, card):
        self.game.add_message("{} picked a card from the top of the deck.".format(player.name))
        color_dict = {"Good": "\033[32m", "Neutral": "\033[0m", "Conditional": "\033[33m", "Bad": "\033[31m"}
        colored_card = "{}{}\033[0m".format(color_dict[card[3]], card[1])
        self.game.add_message("Card: {}".format(colored_card))
        stripped_numeral = card[0]%100
        
        # Move to specific tile
        if stripped_numeral < 10:
            tile = self.game.tiles[card[2][0]]
            self.game.move_player(player, tile)
        # go to jail
        elif stripped_numeral < 20:
            self.game.send_to_jail(player)
        # move, multiplicative rent
        elif stripped_numeral < 30:
            if card[0] in (121, 122):
                new_tile = self.game.advance_to_nearest_tiletype("utility", player)    
                if new_tile.owner and new_tile.owner != player:
                    amount = self.game.roll_dice(override=True) * 10
                    self.game.pay_amount(player, new_tile.owner, amount)
                    self.game.end_buy_phase()
            if card[0] == 123:
                new_tile = self.game.advance_to_nearest_tiletype("railroad", player)
                if new_tile.owner and new_tile.owner != player:
                    rent = new_tile.determine_rent() * 2
                    self.game.pay_amount(player, new_tile.owner, rent)
                    self.game.end_buy_phase()
                
#        (123, "Advance token to the nearest Railroad and pay owner twice the rental to which he/she is otherwise entitled. If Railroad is unowned, you may buy it from the Bank.", []),
                

                
        # relative move
        elif stripped_numeral < 40:
            self.game.advance_player(player, card[2][0])
        # jail free card
        elif stripped_numeral < 50:
            player.num_cards += 1
            self.game.end_buy_phase()

        # misc
        elif stripped_numeral < 60:
            if card[0] == 151:
                owed = 0
                for tile in self.game.tiles:
                    if hasattr(tile, "num_houses"):
                        if tile.hotel:
                            owed += 100
                        elif tile.num_houses:
                            owed += 50 * tile.num_houses

                self.game.pay_amount(player, "bank", -1 * owed) 
            elif card[0] == 152:
                for p in self.game.players:
                    p.money += 50
                    player.money -= 50
                player.money = max(0, player.money)
            self.game.end_buy_phase()
        
        # lose or gain funds
        else:
            self.game.pay_amount(player, "bank", -1 * card[2][0]) 
            self.game.end_buy_phase()
            
    def grab_card(self, player):
        card = self.deck.pop()
        print(card)
        print("acting on card")
        self.act_on_card(player, card)
class Community(Deck):
        
    deck = [(261, "blank", [0])] * 100 #TODO: debugging
class Chance(Deck):
    deck = [
        (101, "Advance to Go", [0], "Good"),
        (102, "Advance to Illinois Ave.", [24], "Neutral"),
        (103, "Advance to St. Charles Place", [11], "Neutral"),
        (104, "Take a trip to Reading Railroad", [5], "Neutral"),
        (105, "Take a walk on the boardwalk", [39], "Neutral"),
        (111, "Go directly to Jail.  Do not pass Go.  Do not collect $200", [], "Bad"),
        (121, "Advance token to nearest utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total 10 times the amount thrown.", [], "Conditional"),
        (122, "Advance token to the nearest Railroad and pay owner twice the rental to which he/she is otherwise entitled. If Railroad is unowned, you may buy it from the Bank.", [], "Conditional"),
        (123, "Advance token to the nearest Railroad and pay owner twice the rental to which he/she is otherwise entitled. If Railroad is unowned, you may buy it from the Bank.", [], "Conditional"),
        (131, "Go back three spaces.", [-3], "Bad"),
        (141, "Get out of Jail free.", [], "Good"),
        (151, "Make general repairs on all your property: For each house pay $25, For each hotel pay $100.", [], "Bad"),
        (152, "You have been elected Chairman of the Board. Pay each player $50.", [], "Bad"),
        (161, "Bank pays you dividend of $50.", [50], "Good"),
        (162, "Pay poor tax of $15", [-15], "Bad"),
        (163, "Your building loan matures. Collect $150.", [150], "Good"),
        (164, "You have won a crossword competition.  Collect $100.", [100], "Good"),
        ]
#    deck = [(162, "blank", [15])] * 100 #TODO: debugging
#    deck = [(111, "blank", [])] * 100 #TODO: debugging
