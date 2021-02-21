from GameElements import Game, PokerSets, Player, Cards, create_card


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

    # load a game with public info
    current_player = game_info["next_player"]
    if current_player == 0 or current_player > game_info["number_of_players"]:
        # all player pass, dealer's turn
        return -1.0
    n_players = game_info["number_of_players"]
    n_sets = game_info["number_of_sets"]
    avail_cards = [4 * n_sets] * 10
    avail_cards[9] = 4 * 4 * n_sets
    i = 1
    player_cards = []
    while i <= n_players:
        pkey = "players_%d" % i
        for s in game_info[pkey]["cards"]:
            # card: str like "diamond A"
            card = create_card(s)
            avail_cards[card.get_value() - 1] -= 1
            if i == current_player:
                player_cards.append(card)
        i += 1
    assert game_info[pkey]["ended"] == False
    player = Player(current_player, player_cards, game_info[pkey]["ended"])
    for s in game_info["dealer"]["cards"]:
        card = create_card(s)
        if not card.hidden:
            avail_cards[card.get_value() - 1] -= 1
    
    


if __name__ == "__main__":
    g = Game()
    g.first_serve()
    winning_odd(g.get_public_status())

        
