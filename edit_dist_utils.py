'''
Variety of functions related to computing the edit distance between
strings and, importantly, which WILL be used by the DistleGame to
provide feedback to the DistlePlayer during a game of Distle.

[!] Feel free to use any of these methods as needed in your DistlePlayer.

[!] Feel free to ADD any methods you see fit for use by your DistlePlayer,
e.g., some form of entropy computation.
'''

def get_edit_dist_table(row_str: str, col_str: str) -> list[list[int]]:
    '''
    Returns the completed Edit Distance memoization structure: a 2D list
    of ints representing the number of string manupulations required to
    minimally turn each subproblem's string into the other.

    Parameters:
        row_str (str):
            The string located along the table's rows
        col_str (col):
            The string located along the table's columns

    Returns:
        list[list[int]]:
            Completed memoization table for the computation of the
            edit_distance(row_str, col_str)
    '''

    table: list[list[int]] = [[]]
    replacement: float
    transposition: float
    insertion: float
    deletion: float

    for col_num in range(len(col_str) + 1):
        table[0].append(col_num)
    for row_num in range(1, len(row_str) + 1):
        table.append([])
        table[row_num].append(row_num)

    for row_index in range(1, len(row_str) + 1):
        for col_index in range(1, len(col_str) + 1):
            if col_str[col_index - 1] == row_str[row_index - 1]:
                table[row_index].append(table[row_index - 1][col_index - 1])
            else:
                replacement = float(table[row_index - 1][col_index - 1] + 1)
                deletion = float(table[row_index - 1][col_index] + 1)
                insertion = float(table[row_index][col_index - 1] + 1)

                if row_index >= 2 and col_index >= 2 and col_str[col_index - 1] == row_str[row_index - 2] and col_str[col_index - 2] == row_str[row_index - 1]:
                    transposition = float(table[row_index - 2][col_index - 2] + 1)
                else:
                    transposition = float('inf')

                table[row_index].append(int(min(replacement, transposition, insertion, deletion)))

    return table


def edit_distance(s0: str, s1: str) -> int:
    '''
    Returns the edit distance between two given strings, defined as an
    int that counts the number of primitive string manipulations (i.e.,
    Insertions, Deletions, Replacements, and Transpositions) minimally
    required to turn one string into the other.
    
    [!] Given as part of the skeleton, no need to modify
    
    Parameters:
        s0, s1 (str):
            The strings to compute the edit distance between
    
    Returns:
        int:
            The minimal number of string manipulations
    '''
    if s0 == s1: return 0
    return get_edit_dist_table(s0, s1)[len(s0)][len(s1)]

def get_transformation_list(s0: str, s1: str) -> list[str]:
    '''
    Returns one possible sequence of transformations that turns String s0
    into s1. The list is in top-down order (i.e., starting from the largest
    subproblem in the memoization structure) and consists of Strings representing
    the String manipulations of:
        1. "R" = Replacement
        2. "T" = Transposition
        3. "I" = Insertion
        4. "D" = Deletion
    In case of multiple minimal edit distance sequences, returns a list with
    ties in manipulations broken by the order listed above (i.e., replacements
    preferred over transpositions, which in turn are preferred over insertions, etc.)
    
    [!] Given as part of the skeleton, no need to modify
    
    Example:
        s0 = "hack"
        s1 = "fkc"
        get_transformation_list(s0, s1) => ["T", "R", "D"]
        get_transformation_list(s1, s0) => ["T", "R", "I"]
    
    Parameters:
        s0, s1 (str):
            Start and destination strings for the transformation
    
    Returns:
        list[str]:
            The sequence of top-down manipulations required to turn s0 into s1
    '''
    
    return get_transformation_list_with_table(s0, s1, get_edit_dist_table(s0, s1))

def get_transformation_list_with_table(s0: str, s1: str, table: list[list[int]]) -> list[str]:
    '''
    See get_transformation_list documentation.

    This method does exactly the same thing as get_transformation_list, except that
    the memoization table is input as a parameter. This version of the method can be
    used to save computational efficiency if the memoization table was pre-computed
    and is being used by multiple methods.

    [!] MUST use the already-solved memoization table and must NOT recompute it.
    [!] MUST be implemented recursively (i.e., in top-down fashion)
    '''
    
    transformations: list[str] = []
    return recursion(s0, s1, table, transformations)


def recursion(s0: str, s1: str, table: list[list[int]], transformations: list[str]) -> list[str]:
    '''
    The helper method that helps get_transformation_list_with_table()
    recursively carry out top-down dynamic programming.
    
    Parameters:
        s0, s1 (str):
            Start and destination strings for the transformation.
        table (list[list[int]]):
            Pre-computed memoization table of the two string parameters.
        transformations (list[str]):
            The current, but not completed, sequence of top-down manipulations required to turn s0 into s1,
            continuously edited everytime the recursive method is called.
    
    Returns:
        list[str]:
            The sequence of top-down manipulations required to turn s0 into s1
    '''

    if (len(s0) == 0 and len(s1) == 0) or table[len(s0)][len(s1)] == 0:
        return transformations

    if len(s0) > 0 and len(s1) > 0 and s0[-1] == s1[-1]:
        s0 = s0[:-1]
        s1 = s1[:-1]
    elif len(s0) >= 1 and len(s1) >= 1 and (table[len(s0)][len(s1)] == (table[len(s0) - 1][len(s1) - 1] + 1)):
        transformations.append("R")
        s0 = s0[:-1]
        s1 = s1[:-1]
    elif len(s0) >= 2 and len(s1) >= 2 and (s0[-1] == s1[-2] and s0[-2] == s1[-1]):
        transformations.append("T")
        s0 = s0[:-2]
        s1 = s1[:-2]
    elif len(s1) >= 1 and table[len(s0)][len(s1)] == (table[len(s0)][len(s1) - 1] + 1):
        transformations.append("I")
        s1 = s1[:-1]
    elif len(s0) >= 1 and table[len(s0)][len(s1)] == (table[len(s0) - 1][len(s1)] + 1):
        transformations.append("D")
        s0 = s0[:-1]

    return recursion(s0, s1, table, transformations)

