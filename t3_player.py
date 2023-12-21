"""
Artificial Intelligence responsible for playing the game of T3!
Implements the alpha-beta-pruning mini-max search algorithm
"""
from dataclasses import *
from typing import *
from t3_state import *


def alphabeta(state: "T3State", alpha: float, beta: float, odd_turn: bool, parent: "T3Node") -> tuple[float, int, "T3Action"]:
    """
    Recrusive method that completes the alpha-beta pruning with the given criteria,
    returning the best terminal action with the utility score.

    Parameters:
        state (T3State):
            The state of the map with the given node.
        alpha (float):
            The alpha value with the given node.
        beta (float):
            The beta value with the given node.
        odd_turn (bool):
            A boolean that tells if it is an odd or even turn, telling if it is a min or max node.
        player (T3Player):
            The player node, which includes the node's action, utility score, and depth.

    Returns:
        tuple[float, int, "T3Action"]:
            The utility score that the node leads to, the depth of the node, and the action taken to get there.
    """
    
    if odd_turn and state.is_win():
        return 0, parent.depth, parent.action
    elif not odd_turn and state.is_win():
        return 1, parent.depth, parent.action
    elif state.is_tie():
        return 0.5, parent.depth, parent.action

    child: "T3Node" = T3Node(parent.action, float("-inf"), parent.depth + 1)

    if odd_turn:
        parent.utility_score = float("-inf")
        for transition in state.get_transitions():
            child.action = transition[0]
            temp_child = alphabeta(transition[1], alpha, beta, False, child)
            child.utility_score = temp_child[0]
            child.depth = temp_child[1]
            if check_best_option((child.utility_score, child.depth, child.action), (parent.utility_score, parent.depth, parent.action)):
                parent.action = transition[0]
                parent.depth = child.depth
            parent.utility_score = max(parent.utility_score, child.utility_score)
            alpha = max(alpha, parent.utility_score)
            if beta <= alpha:
                break
        return parent.utility_score, parent.depth, parent.action

    else:
        parent.utility_score = float("inf")
        for transition in state.get_transitions():
            child.action = transition[0]
            temp_child = alphabeta(transition[1], alpha, beta, True, child)
            child.utility_score = temp_child[0]
            child.depth = temp_child[1]
            if check_best_option((child.utility_score, child.depth, child.action), (parent.utility_score, parent.depth, parent.action)):
                parent.action = transition[0]
                parent.depth = child.depth
            parent.utility_score = min(parent.utility_score, child.utility_score)
            beta = min(beta, parent.utility_score)
            if beta <= alpha:
                break
        return parent.utility_score, parent.depth, parent.action


def check_best_option(option1: tuple[float, int, "T3Action"], option2: tuple[float, int, "T3Action"]) -> bool:
    """
    Compares two options for a tiebreaker and returns the option that's best in terms of the tie-breaker criteria.
    Specifically, it first checks the utility score, then the depth of the terminal node, and then the earliest move.

    Parameters:
        option1 (tuple[float, int, "T3Action"]):
            The first tiebreaker option, which is a tuple that includes a float which is the utility score,
            an int which is the depth of the node,
            and an action which can be used to find the column, row, and move of the action.
        option2 (tuple[float, int, "T3Action"]):
            The second tiebreaker option, which is a tuple that includes a float which is the utility score,
            an int which is the depth of the node,
            and an action which can be used to find the column, row, and move of the action.

    Returns:
        bool:
            Whether option1 is the better option than option2, checking the utility score, depth, and action of the node.
    """

    optionA: tuple[float, int, int, int, int] = (-option1[0], option1[1], option1[2].col(), option1[2].row(), option1[2].move())
    optionB: tuple[float, int, int, int, int] = (-option2[0], option2[1], option2[2].col(), option2[2].row(), option2[2].move())

    return optionA < optionB


def choose(state: "T3State") -> Optional["T3Action"]:
    """
    Main workhorse of the T3Player that makes the optimal decision from the max node
    state given by the parameter to play the game of Tic-Tac-Total.

    [!] Remember the tie-breaking criteria! Moves should be selected in order of:
    1. Best utility
    2. Smallest depth of terminal
    3. Earliest move (i.e., lowest col, then row, then move number)

    You can view tiebreaking as something of an if-ladder: i.e., only continue to
    evaluate the depth if two candidates have the same utility, only continue to
    evaluate the earliest move if two candidates have the same utility and depth.

    Parameters:
        state (T3State):
            The board state from which the agent is making a choice. The board
            state will be either the odds or evens player's turn, and the agent
            should use the T3State methods to simplify its logic to work in
            either case.

    Returns:
        Optional[T3Action]:
            If the given state is a terminal (i.e., a win or tie), returns None.
            Otherwise, returns the best T3Action the current player could take
            from the given state by the criteria stated above.
    """

    if state.is_win() or state.is_tie():
        return None

    is_odd: bool = True
    alpha: float = float("-inf")
    beta: float = float("inf")
    action: "T3Action" = T3Action(0, 0, 0)
    start_node: "T3Node" = T3Node(action, 0.0, 0)

    choice = alphabeta(state, alpha, beta, is_odd, start_node)
    return choice[2]


class T3Node:
    """
    Helper class representation of a node, which will contain the action, utility score, and depth of the node.
    Make T3Node objects to compare to see which object is the best.
    """

    def __init__(self, action: "T3Action", utility_score: float, depth: int):
        """
        Constructs a new T3Node from the provided action, utility score, and depth.
        
        Parameters:
            action (T3Action):
                The action being taken on the node.
            utility_score (float):
                The minimax score, or utility score, at the node.
            depth (int):
                The depth of the node, specifically a count of iterations through the depth first search.
        """
        self.action: "T3Action" = action
        self.utility_score: float = utility_score
        self.depth: int = depth

