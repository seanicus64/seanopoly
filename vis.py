import textwrap
def show_board(game, board_type):
    game.frame += 1
    t = game.tiles
    fancy_board = """\033c
    {}
    \r┌─────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────┐
    \r│     │{}│{}│?    ?│{}│{}│      │{}│$    $│{}│       │
    \r│JAIL │  CT  │  VT  │      │Orient│Readng│INCOME│Baltic│Commun│Medit │ <---- │
    \r│     │ Ave  │ Ave  │CHANCE│ Ave  │  RR  │ TAX  │  Ave │Chest │ Ave  │   GO  │
    \r+--+  │{}│{}│{}│{}│{}│{}│{}│{}│{}│{} │
    \r│{} │  │ 120  │ 100  │?    ?│ 100  │ 200  │ -200 │  60  │$    $│  60  │  +200 │
    \r+--+{} ├──{}──┴──{}──┴──────┴──{}──┴──{}──┴──────┴──{}──┴──────┴──{}──┴───────┘
    \r│{} │  │
    \r+--+{} ├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬───────┐
    \r│{} │  │{}│{}│{}│{}│{}│{}│$    $│{}│{}│       │
    \r+--+{} │St.Cs'│Electr│States│  VA  │  PA  │SJames│Commun│  TN  │  NY  │ \{}\ \ │
    \r│{} │  │Place │{}Co{}│ Ave  │ Ave  │  RR  │Place │Chest │  Ave │ Ave  │  \ \ \│
    \r+--+{} │{}│{}│{}│{}│{}│{}│{}│{}│{}│       │
    \r│     │  140 │ 150  │  140 │  160 │ 200  │  180 │$    $│  180 │  200 │ \{}\ \ │
    \r└──││─┴──{}──┴──{}──┴──{}──┴──{}──┴──{}──┴──{}──┴──────┴──{}──┴──{}──┤  \ \ \│
    \r   ││                                                                │  FREE │
    \r┌──││─┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┤  PARK │
    \r│     │{}│{}│{}│{}│{}│{}│{}│?    ?│{}│  ING  │
    \r│     │Marvin│Water{}│Ventnr│Atlant│ B&O  │  IL  │  IN  │      │  KY  │ \ \{}\ │
    \r│     │Gardns│{}Works│ Ave  │ Ave  │  RR  │ Ave  │  Ave │CHANCE│ Ave  │  \ \ \│
    \r│  ^  │{}│{}│{}│{}│{}│{}│{}│{}│{}│       │
    \r│  |  │  280 │  150 │  260 │  260 │ 200  │  240 │  220 │?    ?│  220 │ \{}\ \ │
    \r│     ├──{}──┴──{}──┴──{}──┴──{}──┴──{}──┴──{}──┴──{}──┴──────┴──{}──┴───────┘
    \r│ GO  │
    \r│ TO  ├──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐
    \r│JAIL │{}│{}│$    $│{}│{}│?    ?│{}│      │{}│
    \r│     │Pacifc│  NC  │Commun│  PA  │Short │      │Park  │Luxury│Board │
    \r│     │ Ave  │  Ave │Chest │ Ave  │  Line│CHANCE│ Place│ Tax  │ walk │
    \r│     │{}│{}│{}│{}│{}│{}│{}│{}│{}│
    \r│     │  300 │  300 │$    $│  320 │  200 │?    ?│  350 │ -100 │  400 │
    \r└─────┴──{}──┴──{}──┴──────┴──{}──┴──{}──┴──────┴──{}──┴──────┴──{}──┘
    """

    basic_board = """\033c
    {}
    \r+-----+------+------+------+------+------+------+------+------+------+-------+
    \r|     |{}|{}|?    ?|{}|{}|      |{}|$    $|{}|       | 
    \r|JAIL |  CT  |  VT  |      |Orient|Readng|INCOME|Baltic|Commun|Medit | <---- | 
    \r|     | Ave  | Ave  |CHANCE| Ave  |  RR  | TAX  |  Ave |Chest | Ave  |   GO  | 
    \r|==+  |{}|{}|{}|{}|{}|{}|{}|{}|{}|{} | 
    \r|{} |  | 120  | 100  |?    ?| 100  | 200  | -200 |  60  |$    $|  60  |  +200 | 
    \r|==|{} +--{}--+--{}--+------+--{}--+--{}--+------+--{}--+------+--{}--+-------+ 
    \r|{} |  | 
    \r|==|{} +------+------+------+------+------+------+------+------+------+-------+
    \r|{} |  |{}|{}|{}|{}|{}|{}|$    $|{}|{}|       |
    \r|==|{} |St.Cs'|Electr|States|  VA  |  PA  |SJames|Commun|  TN  |  NY  | \{}\ \ | 
    \r|{} |  |Place |{}Co{}| Ave  | Ave  |  RR  |Place |Chest |  Ave | Ave  |  \ \ \| 
    \r|==+{} |{}|{}|{}|{}|{}|{}|{}|{}|{}|       | 
    \r|     |  140 | 150  |  140 |  160 | 200  |  180 |$    $|  180 |  200 | \{}\ \ | 
    \r+--||-+--{}--+--{}--+--{}--+--{}--+--{}--+--{}--+------+--{}--+--{}--+  \ \ \| 
    \r   ||                                                                |  FREE | 
    \r+--||-+------+------+------+------+------+------+------+------+------+  PARK | 
    \r|     |{}|{}|{}|{}|{}|{}|{}|?    ?|{}|  ING  | 
    \r|     |Marvin|Water{}|Ventnr|Atlant| B&O  |  IL  |  IN  |      |  KY  | \ \{}\ | 
    \r|     |Gardns|{}Works| Ave  | Ave  |  RR  | Ave  |  Ave |CHANCE| Ave  |  \ \ \| 
    \r|  ^  |{}|{}|{}|{}|{}|{}|{}|{}|{}|       | 
    \r|  |  |  280 |  150 |  260 |  260 | 200  |  240 |  220 |?    ?|  220 | \{}\ \ | 
    \r|     +--{}--+--{}--+--{}--+--{}--+--{}--+--{}--+--{}--+------+--{}--+-------+ 
    \r| GO  |                                                                          
    \r| TO  +------+------+------+------+------+------+------+------+------+          
    \r|JAIL |{}|{}|$    $|{}|{}|?    ?|{}|      |{}|
    \r|     |Pacifc|  NC  |Commun|  PA  |Short |      |Park  |Luxury|Board |
    \r|     | Ave  |  Ave |Chest | Ave  |  Line|CHANCE| Place| Tax  | walk |
    \r|     |{}|{}|{}|{}|{}|{}|{}|{}|{}|
    \r|     |  300 |  300 |$    $|  320 |  200 |?    ?|  350 | -100 |  400 |          
    \r+-----+--{}--+--{}--+------+--{}--+--{}--+------+--{}--+------+--{}--+         
    \r{} - {}┺\n""" 
#    def format_board(self, board)
    board = basic_board if board_type == "basic" else fancy_board
    #print(board)
    print(board_type)
    text = textwrap.dedent(board.format(
        game.phase,
        t[9].t, t[8].t,         t[6].t, t[5].t,         t[3].t,         t[1].t, 
        t[9].o, t[8].o, t[7].o, t[6].o, t[5].o, t[4].o, t[3].o, t[2].o, t[1].o, t[0].o, 

        game.cells[0], t[10].slots[0], 
        t[9].l, t[8].l, t[6].l, t[5].l, t[3].l, t[1].l,
        game.cells[1], t[10].slots[1], game.cells[2],

        t[11].t, t[12].t, t[13].t, t[14].t, t[15].t, t[16].t,          t[18].t, t[19].t, #"F",
        t[10].slots[2], t[20].slots[0], game.cells[3], "\033[33m* \033[0m", "\033[33m *\033[0m", t[10].slots[3], 
        t[11].o, t[12].o, t[13].o, t[14].o, t[15].o, t[16].o, t[17].o, t[18].o, t[19].o, t[20].slots[1],
        t[11].l, t[12].l, t[13].l, t[14].l, t[15].l, t[16].l, t[18].l, t[19].l,

        t[29].t, t[28].t, t[27].t, t[26].t, t[25].t, t[24].t, t[23].t,          t[21].t, "\033[34;1m~\033[0m", t[20].slots[2], "\033[34;1m~\033[0m",
        t[29].o, t[28].o, t[27].o, t[26].o, t[25].o, t[24].o, t[23].o, t[22].o, t[21].o, t[20].slots[3],
        t[29].l, t[28].l, t[27].l, t[26].l, t[25].l, t[24].l, t[23].l,          t[21].l,         

        t[31].t, t[32].t,          t[34].t, t[35].t,          t[37].t,          t[39].t, 
        t[31].o, t[32].o, t[33].o, t[34].o, t[35].o, t[36].o, t[37].o, t[38].o, t[39].o, 
        t[31].l, t[32].l,          t[34].l, t[35].l,          t[37].l,          t[39].l, 
        game.frame, game.players, #TODO
    ))
    return text
