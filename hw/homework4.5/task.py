# --------------
# USER INSTRUCTIONS
#
# Write a function called stochastic_value that
# takes no input and RETURNS two grids. The
# first grid, value, should contain the computed
# value of each cell as shown in the video. The
# second grid, policy, should contain the optimum
# policy for each cell.
#
# Stay tuned for a homework help video! This should
# be available by Thursday and will be visible
# in the course content tab.
#
# Good luck! Keep learning!
#
# --------------
# GRADING NOTES
#
# We will be calling your stochastic_value function
# with several different grids and different values
# of success_prob, collision_cost, and cost_step.
# In order to be marked correct, your function must
# RETURN (it does not have to print) two grids,
# value and policy.
#
# When grading your value grid, we will compare the
# value of each cell with the true value according
# to this model. If your answer for each cell
# is sufficiently close to the correct answer
# (within 0.001), you will be marked as correct.
#
# NOTE: Please do not modify the values of grid,
# success_prob, collision_cost, or cost_step inside
# your function. Doing so could result in your
# submission being inappropriately marked as incorrect.

# -------------
# GLOBAL VARIABLES
#
# You may modify these variables for testing
# purposes, but you should only modify them here.
# Do NOT modify them inside your stochastic_value
# function.

grid = [[0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0]]

goal = [0, len(grid[0]) - 1]  # Goal is in top right corner


delta = [[-1, 0],  # go up
         [0, -1],  # go left
         [1, 0],  # go down
         [0, 1]]  # go right

delta_name = ['^', '<', 'v', '>']  # Use these when creating your policy grid.

success_prob = 0.5
failure_prob = (1.0 - success_prob) / 2.0  # Probability(stepping left) = prob(stepping right) = failure_prob
collision_cost = 100
cost_step = 1


############## INSERT/MODIFY YOUR CODE BELOW ##################
#
# You may modify the code below if you want, but remember that
# your function must...
#
# 1) ...be called stochastic_value().
# 2) ...NOT take any arguments.
# 3) ...return two grids: FIRST value and THEN policy.

def stochastic_value():
    value = [[1000.0 for row in range(len(grid[0]))] for col in range(
        len(grid))]
    policy = [[' ' for row in range(len(grid[0]))] for col in range(len(grid))]

    new_value = update_value(value)
    while new_value != value:
        value = new_value
        new_value = update_value(value)

    return new_value, policy


def update_value(value):
    new_value = []
    for x, row in enumerate(value):
        new_row = []
        for y, v in enumerate(row):
            action_values = [0 for i in range(len(delta))]
            if [x, y] == goal:
                new_row.append(0)
                continue
            for i, attempted_move in enumerate(delta):
                for d, prob in get_stocastic_move(attempted_move):
                    x2, y2 = x + d[0], y + d[1]
                    if x2 in range(len(value)) and y2 in range(len(value[0])):
                        n_v = value[x2][y2]
                    else:
                        n_v = collision_cost
                    action_values[i] += prob * n_v + 1
            new_row.append(min(action_values))
        new_value.append(new_row)
    return new_value


def get_stocastic_move(move):
    move_map = {
        0: [1, 3],
        1: [0, 2],
        2: [1, 3],
        3: [0, 2]
    }
    yield move, success_prob
    for i in move_map[delta.index(move)]:
        yield delta[i], failure_prob
