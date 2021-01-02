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
import vis
from helper_classes import User, Board
from tiles import Group, GeneralTile, PropertyTile, TaxTile, RailroadTile, JailTile 
from tiles import UtilityTile, FreeParkingTile, CommunityTile, ChanceTile
from tiles import GoToJailTile, BuildableTile
random.seed(0)
import random


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
    """Lets you select which current game to play."""
    def quit():
        """Quits out of the game menu."""
        conn.close()
        game = None
        return game
    # gets set only if rejoining existing game with a code
    player = None
    trying_to_quit = False
    while True:
        if trying_to_quit:
            conn.send(bytes("You sure you want to quit? \033[31mqy\033[m to confirm. ".encode("utf-8")))
            trying_to_quit = False
        else: conn.send(bytes("\033cSelect an existing game to play, or create a [n]ew game?\n\rq to quit.\n\r".encode("utf-8")))
        for e, i in enumerate(game_list):
            active = False
            if i.started:
                active = True
            string = "{}#{} - {} player(s) {}  Turn:{}\033[0m\n\r".format("\033[33m" if active else "\033[32m", e, len(i.players), "playing" if active else "waiting", i.turn)
            string = bytes(string.encode("utf-8"))
            conn.send(string)
        try:
            data = conn.recv(1024).decode("utf-8").strip().lower()
        except: 
            continue
        if len(data) == 10:
            game = None
            possible_code = data.lower().strip()
            for p in all_players:
                print(p.code, possible_code)
                if p.code == possible_code and not p.connected:
                    # if quit during lobby, there won't be an associated game #TODO: associate a game
                    try:
                        game = p.game
                        p.connected = True
                        print("YOUR GAME IS {}".format(game))
                        player = p
                        break
                    except:
                        continue
            if game:
                break
        if data == "n":
            print("New game lobby started.")
            player = user_settings(conn)
            game = Board(tiles)
            game_list.append(game)
            #TODO: announce new game lobby (probably should wait after player chooses name 
            break
        if data == "qy":
            return quit(), None
        if data == "q":
            trying_to_quit = True
        if data.isdigit():
            which_game = int(data)
            if 0 <= which_game < len(game_list):
                game = game_list[which_game]
                break
    return game, player

def user_settings(conn, game=None):
    """User sets settings, such as display name and color."""
    # TODO possibly: spectators?
    while True:
        conn.send(bytes("\033cType in your (one word) name, desired character(@ # % or &), and color (\033[31;1m1\033[32m2\033[33m3\033[34m4\033[35m5\033[36m6\033[37m7\033[0m) without using anyone else's\r\n".encode("utf-8")))
        conn.send(bytes("If you don't see a straight line here, type '\033[33mascii\033[0m' or '\033[33ma\033[0m' at the end to use ascii-only mode: \033[35;1m─────\033[0m\r\n".encode("utf-8")))
        conn.send(bytes("For example, to play as Fred using  an at-sign and the color yellow, in ascii-only mode, type '\033[33mfred @ 3 ascii\033[0m'\n\r".encode("utf-8")))
        conn.send(bytes("Type \033[31mq\033[0m to quit.\r\n".encode("utf-8")))
        if game:
            for player in game.players:
                conn.send(bytes("{} - {}\n".format(player.name, player).encode("utf-8")))
        else:
            conn.send(bytes("No one is playing yet!".encode("utf-8")))
        raw = conn.recv(1024)
        try:
           data = raw.decode("utf-8").strip().lower().split()
        except: 
            continue
        if raw.decode("utf-8").lower().strip() in ["q", "quit"]:
            conn.close()
            return None
        if not 3 <= len(data) < 5: 
            continue
        if len(data[1]) != 1 and not data[1] in "@#%&": 
            #TODO: was ble to use the number 5 as a symbol?
            continue
        if not data[2].isdigit():
            continue
        if (data[2].isdigit() and not (1 <= int(data[2]) <= 7)): 
            continue
        ascii_mode = False
        if len(data) == 4:
            if data[3] not in ("a", "ascii"): continue
            ascii_mode = True
        name, char, color = data[:3]
        color = int(color)
        if game:
            if name in [p.name for p in game.players]: 
                continue
            if char in [p.char for p in game.players]: 
                continue
            if color in [p.color for p in game.players]:    
                continue
            you = create_user(color, char, name, ascii_mode, conn)
            game.broadcast("{} joined the game!".format(you))
        else:
            you = create_user(color, char, name, ascii_mode, conn)
        break
    return you
  
def create_user(color, char, name, ascii_mode, conn):
    """Creates a User, ensuring that the .code isn't already being used."""
    user = User(color, char, name, ascii_mode, conn)
    while True:
        all_codes = [p.code for p in all_players]
        if user.code in all_codes:
            user.make_code
            continue
        else:
            break
    return user	

def main_loop(conn, you, game):
    """Handles the main loop of a game."""
    jail_methods = {"b": game.pay_bail, "c": game.use_card, "r": game.roll_to_leave_jail,
                    "bail": game.pay_bail, "card": game.use_card, "roll": game.roll_to_leave_jail}
    while True:
        try:
            raw = conn.recv(1024).decode("utf-8").strip()
            data = raw.lower()
        except:
            #print("failed") #TODO: this is a way to check disconnection
            continue

        if game.phase == "GAMEOVER":
            game.show_board()
            continue

        split = data.split()
        if len(split) == 0: continue
        split = [w.lower() for w in split]
        if len(data) > 1 and data.startswith("/"):
            game.add_chat(you, raw[1:])
        if data in ["c", "code"]:
            you.send("\033[33m{}\033[0m".format(you.code))
        if you.trying_to_quit:
            if data == "y":
                you.connected = False
                you.send("\033[33m{}\033[0m".format(you.code))
                you.trying_to_quit = False
                you.conn.close()
            else:
                you.send("Okay, I guess not.")
                you.trying_to_quit = False

        if data in ["q", "quit"]:
            you.trying_to_quit = True
            you.send("Are you sure you want to quit?  Type '\033[31my\033[0m' to confirm.")
        if data == "qy":
            you.send("\033[33m{}\033[0m".format(you.code))
            you.connected = False
            you.conn.close()
        if not game.started:
            if you == game.creator and data == "s" and len(game.players) > 1:
                game.begin()
                #TODO: error one time, not enough players but this still went through
            continue
        if data in ["q", "quit"]:
            pass
        if data in ["h", "help"]:
            you.send("hello world")
            game.help(you)

        if data == "chat":
            string = "\033c"
            for c in game.chat_messages:
                string += c + "\r\n"
            string = string.strip()
            you.send(string)
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

        if data == "me":
            game.show_player_info(you)
        if data == "board":
            if you.ascii_mode:
                you.send(vis.show_board(game, "basic"))
            else:
                you.send(vis.show_board(game, "fancy"))
        if you == game.current_player:
            if you.in_debt:
                if len(split) == 2 and split[0] in ["s", "sell"]:
                    game.sell_tile(you, split[1])
                elif split[0] in ["t", "trade"]:
                    trade = game.parse_trade(you, split)
                    if trade:
                        game.current_trade = trade
                        continue
                else:
                    you.send("You must resolve your debt.")
                    continue
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
                        you.send("This isn't for sale!")
                        continue

                #TODO: does this block belong here?
                if len(split) == 2 and split[0] in ["sell", "s"]:
                    game.sell_tile(you, split[1])
                        
                elif data in ["auction", "a"]:
                    if isinstance(you.tile, PropertyTile) and not you.tile.owner and not you.tile.owner == you:
                        game.broadcast("{} is going up for auction!  Any player can type any amount.".format(you.tile.name))
                        game.in_auction = True
                        game.highest_bid = (None, 0)
                        game.auction_timer = threading.Thread(target = game.handle_auction, args=(you.tile,))
                    else:
                        print("????????????")
                        you.send("This isn't for sale!")
                        continue
                    
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
                    if trade:
                        game.current_trade = trade
                        continue

    conn.close()

def handle_connection(conn, game_list):
    """Handles a connection to the server."""
    code = bytearray()
    for i in [0xff, 0xfe, 0x03, 0xff, 0xfb, 0x22, 0xff, 0xfe, 0x01]:
        code.append(i)
    conn.send(code)
    # First, get the game
    game, player = game_menu(conn, game_list)

    # if you chose a new game, then you go through user_settings and a game is created
    # in game_menu because a game lobby cant exist without a creator
    #, so this return shouldn't run unless player quit.
    if not game: return

    print(game.started, game.players, player)
    # So there's an existing game lobby you are joining.
    if not game.started:# and game.players:
        # joining pending game lobby
        if not player:
            # you'll have to pick a name
            player = user_settings(conn, game)
            # then you clearly don't wnat to play...
            if not player:
                return False
    else:
        player.conn = conn
        if player.ascii_mode:
            player.send(vis.show_board(game, "basic"))
        else:
            player.send(vis.show_board(game, "fancy"))
        player.send("You have rejoined the game")
        
    you = player
    game.add_player(you) #TODO: is this duplicating players?
    all_players.append(you)
    print("Player {} ({}) joined game.".format(you.name, you))
    you.send("\033cYour reconnect code is \033[32m{}\033[0m.  Write that down somewhere!  If you disconnect, you can rejoin your game with it instantly.".format(you.code))
    if you == game.creator and not game.started: 
        you.send("Type '\033[33mS\033[0m' to begin the game after everyone has joined.")
    main_loop(conn, you, game)

debug = False
def check_connection(conn):
    """Thread to make sure that a connection isn't lost."""
    associated_with_player = False
    associated_game = False
    while True:
        # Finds what game a player is associated with
        if not associated_with_player:
            for p in all_players:
                if p.conn == conn:
                    associated_with_player = p
                    for g in game_list:
                        if p in g.players:
                            associated_game = g

        # Checks if the player is no longer connected
        x = conn.fileno()
        if x < 0 and associated_with_player:
            associated_game.broadcast("{} left the game.".format(associated_with_player.name))
            if not associated_game.started:
                associated_game.players.remove(associated_with_player)
                if len(associated_game.players) == 1:
                    #TODO: tell the guy he's the new owner
                    associated_game.creator = associated_game.players[0]
                    associated_game.creator.send("You're the new owner of this game.  If another player joins, type S to begin.")
                elif len(associated_game.players) == 0:
                    game_list.remove(associated_game)

            break
        time.sleep(1)
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
    all_players = []
    print("Game server started!")
    while True:
        conn, addr = s.accept()
        conns.append(conn)
        thread = threading.Thread(target=handle_connection, args=(conn, game_list))
        check_conn_thread = threading.Thread(target=check_connection, args=(conn,))
        thread.start()
        check_conn_thread.start()
    s.close()

