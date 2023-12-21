'''
Calendar Satisfaction Problem (CSP) Solver
Designed to make scheduling those meetings a breeze! Suite of tools
for efficiently scheduling some n meetings in a given datetime range
that abides by some number of constraints.

In this module:
- A solver that uses the backtracking exact solver approach
- Tools for pruning domains using node and arc consistency
'''
from datetime import *
from date_constraints import *
from dataclasses import *
from copy import *
import random


# CSP Backtracking Solver
# ---------------------------------------------------------------------------
def solve(n_meetings: int, date_range: set[datetime], constraints: set[DateConstraint]) -> Optional[list[datetime]]:
    '''
    When possible, returns a solution to the given CSP based on the need to
    schedule n meetings within the given date range and abiding by the given
    set of DateConstraints.
      - Implemented using the Backtracking exact solution method
      - May return None when the CSP is unsatisfiable
    
    Parameters:
        n_meetings (int):
            The number of meetings that must be scheduled, indexed from 0 to n-1
        date_range (set[datetime]):
            The range of datetimes in which the n meetings must be scheduled; by default,
            these are each separated a day apart, but there's nothing to stop these from
            being meetings scheduled down to the second
            [!] WARNING: AVOID ALIASING -- Remember that each variable must have its
            own domain but what's provided is a single reference to a set of datetimes
        constraints (set[DateConstraint]):
            A set of DateConstraints specifying how the meetings must be scheduled.
            See DateConstraint documentation for different types of DateConstraints
            that might be found, and useful methods for implementing this solver.
    
    Returns:
        Optional[list[datetime]]:
            If a solution to the CSP exists:
                Returns a list of datetimes, one for each of the n_meetings, where the
                datetime at each index corresponds to the meeting of that same index
            If no solution is possible:
                Returns None
    '''
    assignment: list[datetime] = []
    solution: Optional[list[datetime]] = []
    domains: list[set[datetime]] = [date_range.copy() for num in range(n_meetings)]
    node_consistency(domains, constraints)
    arc_consistency(domains, constraints)
    solution = recursive_backtracker(assignment, domains, date_range, constraints)
    return solution


def recursive_backtracker(assignment: list[datetime], domains: list[set[datetime]], date_range: set[datetime], constraints: set[DateConstraint]) -> Optional[list[datetime]]:
    '''
    Recursively implements the backtracking method until there is a complete assignment list or the constraints are impossible.
    
    Parameters:
        assignment (list[datetime]):
            The current list of assigned datetimes.
        domains (list[set[datetime]]):
            The domain of possible datetimes at each variable / index.
        date_range (set[datetime]):
            The range of datetimes in which the n meetings must be scheduled.
        constraints (set[DateConstraint]):
            A set of DateConstraints specifying how the meetings must be scheduled.
    
    Returns:
        Optional[list[datetime]]:
            If a solution to the CSP exists:
                Returns a list of datetimes, one for each of the n_meetings, where the
                datetime at each index corresponds to the meeting of that same index
            If no solution is possible:
                Returns None
    '''
    if is_complete(assignment, domains, constraints):
        return assignment

    variable: int = len(assignment)
    result: Optional[list[datetime]]
    
    for date in domains[variable]:
        consistent: bool = True
        assignment.append(date)
        for constraint in constraints:
            if not constraint.is_satisfied_by_assignment(assignment):
                consistent = False
                break
        if consistent:
            result = recursive_backtracker(assignment, domains, date_range, constraints)
            if result is not None:
                return assignment
        assignment.pop()
    
    return None


def is_complete(assignment: list[datetime], domains: list[set[datetime]], constraints: set[DateConstraint]) -> bool:
    '''
    Returns whether the assignment is solved by checking whether it has the correct number of variables and follows the constraints.
    
    Parameters:
        assignment (list[datetime]):
            The current list of assigned datetimes.
        domains (list[set[datetime]]):
            The domain of possible datetimes at each variable / index.
        constraints (set[DateConstraint]):
            A set of DateConstraints specifying how the meetings must be scheduled.
    
    Returns:
        bool:
            If the assignment list is the correct number of variables and follows the constraints:
                Returns True
            If the assignment list is the incorrect number of variables or does not follow constraint(s):
                Returns False
    '''
    completed: bool = True
    
    if len(assignment) == len(domains):
        for constraint in constraints:
            if not constraint.is_satisfied_by_assignment(assignment):
                completed = False
    else:
        completed = False
    
    return completed
    

# CSP Filtering: Node Consistency
# ---------------------------------------------------------------------------
def node_consistency(domains: list[set[datetime]], constraints: set[DateConstraint]) -> None:
    '''
    Enforces node consistency for all variables' domains given in the set of domains.
    Meetings' domains' index in each of the provided constraints correspond to their index
    in the list of domains.
    
    [!] Note: Only applies to Unary DateConstraints, i.e., those whose arity() method
    returns 1
    
    Parameters:
        domains (list[set[datetime]]):
            A list of domains where each domain is a set of possible date times to assign
            to each meeting. Each domain in the given list is indexed such that its index
            corresponds to the indexes of meetings mentioned in the given constraints.
        constraints (set[DateConstraint]):
            A set of DateConstraints specifying how the meetings must be scheduled.
            See DateConstraint documentation for different types of DateConstraints
            that might be found, and useful methods for implementing this solver.
            [!] Hint: see a DateConstraint's is_satisfied_by_values
    
    Side Effects:
        Although no values are returned, the values in any pruned domains are changed
        directly within the provided domains parameter
    '''
    unary_constraints: set[DateConstraint] = set()
    for constraint in constraints:
        if constraint.arity() == 1:
            unary_constraints.add(constraint)

    domain_copy: list[datetime]
    index: int = 0
    
    for domain in domains:
        domain_copy = list(domain)
        for date in domain_copy:
            for unary_constraint in unary_constraints:
                if unary_constraint.L_VAL == index and not unary_constraint.is_satisfied_by_values(date):
                    domain.remove(date)
                    break
        index += 1
    
    return


# CSP Filtering: Arc Consistency
# ---------------------------------------------------------------------------
class Arc:
    '''
    Helper Arc class to be used to organize domains for pruning during the AC-3
    algorithm, organized as (TAIL -> HEAD) Arcs that correspond to a given
    CONSTRAINT.
    
    [!] Although you do not need to, you *may* modify this class however you see
    fit to accomplish the arc_consistency method
    
    Attributes:
        CONSTRAINT (DateConstraint):
            The DateConstraint represented by this arc
        TAIL (int):
            The index of the meeting variable at this arc's tail.
        HEAD (int):
            The index of the meeting variable at this arc's head.
    
    [!] IMPORTANT: By definition, the TAIL = CONSTRAINT.L_VAL and
        HEAD = CONSTRAINT.R_VAL
    '''
    
    def __init__(self, constraint: DateConstraint):
        '''
        Constructs a new Arc from the given DateConstraint, setting this Arc's
        TAIL to the constraint's L_VAL and its HEAD to the constraint's R_VAL
        
        Parameters:
            constraint (DateConstraint):
                The constraint represented by this Arc
        '''
        self.CONSTRAINT: DateConstraint = constraint
        self.TAIL: int = constraint.L_VAL
        if isinstance(constraint.R_VAL, int):
            self.HEAD: int = constraint.R_VAL
        else:
            raise ValueError("[X] Cannot create Arc from Unary Constraint")
    
    def __eq__(self, other: Any) -> bool:
        if other is None: return False
        if not isinstance(other, Arc): return False
        return self.CONSTRAINT == other.CONSTRAINT and self.TAIL == other.TAIL and self.HEAD == other.HEAD
    
    def __hash__(self) -> int:
        return hash((self.CONSTRAINT, self.TAIL, self.HEAD))
    
    def __str__(self) -> str:
        return "Arc[" + str(self.CONSTRAINT) + ", (" + str(self.TAIL) + " -> " + str(self.HEAD) + ")]"
    
    def __repr__(self) -> str:
        return self.__str__()

def arc_consistency(domains: list[set[datetime]], constraints: set[DateConstraint]) -> None:
    '''
    Enforces arc consistency for all variables' domains given in the set of domains.
    Meetings' domains' index in each of the provided constraints correspond to their index
    in the list of domains.
    
    [!] Note: Only applies to Binary DateConstraints, i.e., those whose arity() method
    returns 2
    
    Parameters:
        domains (list[set[datetime]]):
            A list of domains where each domain is a set of possible date times to assign
            to each meeting. Each domain in the given list is indexed such that its index
            corresponds to the indexes of meetings mentioned in the given constraints.
        constraints (set[DateConstraint]):
            A set of DateConstraints specifying how the meetings must be scheduled.
            See DateConstraint documentation for different types of DateConstraints
            that might be found, and useful methods for implementing this solver.
            [!] Hint: see a DateConstraint's is_satisfied_by_values
    
    Side Effects:
        Although no values are returned, the values in any pruned domains are changed
        directly within the provided domains parameter
    '''
    arcs: set[Arc] = set()
    for constraint in constraints:
        if constraint.arity() == 2:
            arcs.add(Arc(constraint))
            arcs.add(Arc(constraint.get_reverse()))

    original_arcs: set[Arc] = arcs.copy()
    arc: "Arc"
    while len(arcs) > 0:
        arc = arcs.pop()
        if remove_inconsistent_values(domains, arc):
            for original_arc in original_arcs:
                if original_arc.HEAD == arc.TAIL:
                    arcs.add(original_arc)
    
    return


def remove_inconsistent_values(domains: list[set[datetime]], arc: "Arc") -> bool:
    '''
    Checks for inconsistencies in the arc and removes the dates that are inconsistent
    from the tail domain. An arc is consistent if for all values in the tail domain
    there is at least one value in the head domain that satisfies the arc's constraint.
    
    Parameters:
        domains (list[set[datetime]]):
            A list of domains where each domain is a set of possible date times to assign
            to each meeting. Each domain in the given list is indexed such that its index
            corresponds to the indexes of meetings mentioned in the given constraints.
        arc (Arc):
            A singular arc that is to be checked for consistency using its head and tail.
    '''
    removed: bool = False
    consistent: bool
    tail_domains: set[datetime] = domains[arc.TAIL].copy()
    
    for tail_date in tail_domains:
        consistent = False
        for head_date in domains[arc.HEAD]:
            if arc.CONSTRAINT.is_satisfied_by_values(tail_date, head_date):
                consistent = True
                break
        if not consistent:
            domains[arc.TAIL].remove(tail_date)
            removed = True
    
    return removed

