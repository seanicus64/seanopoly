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
        self.game.add_message("Card: {}".format(card[1]))
        stripped_numeral = card[0]%100
        if stripped_numeral < 10:
            tile = self.game.tiles[card[2][0]]
            print("BBBBBBBBBBB", player.tile.name)
            self.game.move_player(player, tile)
        elif stripped_numeral < 20:
            self.game.send_to_jail(player)
        elif stripped_numeral < 30:
            if card[0] == 121:
                pass
        elif stripped_numeral < 40:
            self.game.advance_player(player, card[2][0])
        elif stripped_numeral < 50:
            player.num_cards += 1
            self.game.end_buy_phase()
        elif stripped_numeral < 60:
            pass
            self.game.end_buy_phase()
        else:
            player.money += card[2][0]
            self.game.end_buy_phase()
            
    def grab_card(self, player):
        card = self.deck.pop()
        self.act_on_card(player, card)
class Community(Deck):
        
    deck = [(261, "blank", [0])] * 100 #TODO: debugging
class Chance(Deck):
    deck = [
        (101, "Advance to Go", [0]),
        (102, "Advance to Illinois Ave.", [24]),
        (103, "Advance to St. Charles Place", [11]),
        (104, "Take a trip to Reading Railroad", [5]),
        (105, "Take a walk on the boardwalk", [39]),
#        (111, "Go directly to Jail.  Do not pass Go.  Do not collect $200", []),
#        (121, "Advance token to nearest utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total 10 times the amount thrown.", []),
#        (122, "Advance token to the nearest Railroad and pay owner twice the rental to which he/she is otherwise entitled. If Railroad is unowned, you may buy it from the Bank.", []),
#        (123, "Advance token to the nearest Railroad and pay owner twice the rental to which he/she is otherwise entitled. If Railroad is unowned, you may buy it from the Bank.", []),
        (131, "Go back three spaces.", [-3]),
        (141, "Get out of Jail free.", []),
        (151, "Make general repairs on all your property: For each house pay $25, For each hotel pay $100.", []),
        (152, "You have been elected Chairman of the Board. Pay each player $50.", []),
        (161, "Bank pays you dividend of $50.", [50]),
        (162, "Pay poor tax of $15", [-15]),
        (163, "Your building loan matures. Collect $150.", [150]),
        (164, "You have won a crossword competition.  Collect $100.", [100]),
        ]
    deck = [(161, "blank", [0])] * 100 #TODO: debugging
