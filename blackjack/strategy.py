from GameElements import Game, PokerSets, Player, Cards


def dealer_rule(dealer):
    """ dealer should take one more or not
        input: player 
        output: boolean
    """
    p = dealer.get_points(hide_dealer_card=False)
    return p < 17


def winning_odd(game_info):
    """ calculate winning prob of the current player """
    # input: game_info is the public info on the desk
    # output: a float between [0.0, 1.0]
    current_player = game_info["next_player"]
    if current_player == 0 or current_player > game_info["number_of_players"]:
        # all player pass, dealer's turn
        return -1.0
    all_cards = {}
    pass
