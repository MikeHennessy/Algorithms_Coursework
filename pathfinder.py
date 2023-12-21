'''
CMSI 2130 - Homework 1
Author: Mike Hennessy

Modify only this file as part of your submission, as it will contain all of the logic
necessary for implementing the A* pathfinder that solves the target practice problem.
'''
import queue
from maze_problem import MazeProblem
from dataclasses import *
from typing import *

@dataclass
class SearchTreeNode:
    """
    SearchTreeNodes contain the following attributes to be used in generation of
    the Search tree:

    Attributes:
        player_loc (tuple[int, int]):
            The player's location in this node.
        action (str):
            The action taken to reach this node from its parent (or empty if the root).
        parent (Optional[SearchTreeNode]):
            The parent node from which this node was generated (or None if the root).
    """
    player_loc: tuple[int, int]
    action: str
    parent: Optional["SearchTreeNode"]
    """
    Implemented two new attrbiutes:
        shot_target (list[tuple[int, int]]):
            A list of all of the targets shot by the node thus far.
        past_cost (int):
            The total cost of the transitions that the node has taken.
        priority (int):
            The priority of the node calculated by the heuristic and added to the priority queue.
    """
    shot_targets: list[tuple[int, int]]
    past_cost: int
    priority: int

    def __lt__(self, other: "SearchTreeNode") -> bool:
            return self.priority < other.priority


def find_solution_path(node: Union["SearchTreeNode", Any]) -> list[str]:
    """
    Helper method that unravels path taken from initial state to goal state.

    Parameters:
        node (SearchTreeNode):
            Current node along the path from initial state to goal state.

    Returns
        list[str]:
            A solution to the problem: a sequence of actions leading from the
            initial state to the goal (a maze with all targets destroyed).
    """

    solution_path: list[str] = []
    
    while node.parent is not None:
        solution_path.insert(0, node.action)
        node = node.parent

    return solution_path


def heuristic(node: SearchTreeNode, targets_left: list[tuple[int, int]], problem: "MazeProblem") -> int:
    """
    Helper method that implements a heuristic to get the priority of each node by adding the
    past cost parameter to a calculated future cost using a manipulation of Manhatten Distance.

    Parameters:
        node (SearchTreeNode):
            Current node along the path.
        targets_left (list[tuple[int, int]]):
            List of the targets that are yet to be shot.

    Returns
        int:
            The priority of the node based on the heuristic method.
    """
    future_cost: int = 0
    
    for target in targets_left:
        future_cost_x: int = 0
        future_cost_y: int = 0
        
        if node.player_loc[0] < target[0]:
            for num in range(node.player_loc[0], target[0]):
                future_cost_x += problem.get_transition_cost("R", (num, node.player_loc[1]))
        else:
            for num in range(target[0], node.player_loc[0]):
                future_cost_x += problem.get_transition_cost("L", (num, node.player_loc[1]))

        if node.player_loc[1] < target[1]:
            for num in range(node.player_loc[1], target[1]):
                future_cost_y += problem.get_transition_cost("U", (node.player_loc[0], num))
        else:
            for num in range(target[1], node.player_loc[1]):
                future_cost_y += problem.get_transition_cost("D", (node.player_loc[0], num))

        if future_cost_x <= future_cost_y:
            future_cost += future_cost_x
        else:
            future_cost += future_cost_y

    priority: int = node.past_cost + future_cost
    return priority


def get_targets_left(node: SearchTreeNode, problem: "MazeProblem") -> list[tuple[int, int]]:
    targets_left: list[tuple[int, int]] = [item for item in problem.get_initial_targets() if item not in node.shot_targets]
    return targets_left


def pathfind(problem: "MazeProblem") -> Optional[list[str]]:
    """
    The main workhorse method of the package that performs A* graph search to find the optimal
    sequence of actions that takes the agent from its initial state and shoots all targets in
    the given MazeProblem's maze, or determines that the problem is unsolvable.

    Parameters:
        problem (MazeProblem):
            The MazeProblem object constructed on the maze that is to be solved or determined
            unsolvable by this method.

    Returns:
        Optional[list[str]]:
            A solution to the problem: a sequence of actions leading from the 
            initial state to the goal (a maze with all targets destroyed). If no such solution is
            possible, returns None.
    """

    frontier: queue.PriorityQueue[SearchTreeNode] = queue.PriorityQueue()
    initial_priority: int = 1
    initial_state: "SearchTreeNode" = SearchTreeNode(problem.get_initial_loc(), "", None, [], 0, initial_priority)
    frontier.put(initial_state)

    # list of tuple[location, shot_targets]
    graveyard: Set[tuple[tuple[int, int], list[tuple[int, int]]]] = set()

    while not frontier.empty():
        parent_node: "SearchTreeNode" = frontier.get()
        graveyard.add((parent_node.player_loc, parent_node.shot_targets))
        targets_left: list[tuple[int, int]] = get_targets_left(parent_node, problem)
        children: dict = problem.get_transitions(parent_node.player_loc, set(targets_left))

        for child in children.items():
            temp_priority: int = 0
            new_node: "SearchTreeNode" = SearchTreeNode(child[1]["next_loc"], child[0], parent_node, list(parent_node.shot_targets), parent_node.past_cost, temp_priority)
            new_node.past_cost += child[1]["cost"]
            new_node.shot_targets.extend(child[1]["targets_hit"])
            targets_left = get_targets_left(new_node, problem)
            new_node.priority = heuristic(new_node, targets_left, problem)

            if set(new_node.shot_targets) == problem.get_initial_targets():
                return find_solution_path(new_node)

            if (new_node.player_loc, new_node.shot_targets) not in graveyard:
                frontier.put(new_node)

    return None
