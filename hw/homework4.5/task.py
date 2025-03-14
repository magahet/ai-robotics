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
    value = [[1000.0 for row in range(len(grid[0]))] for col in range(len(grid))]
    policy = [[' ' for row in range(len(grid[0]))] for col in range(len(grid))]

    past_value = None
    while not past_value or value != past_value:
        past_value = [r[:] for r in value]
        for x, row in enumerate(grid):
            for y, v in enumerate(row):
                if [x, y] == goal:
                    value[x][y] = 0
                    policy[x][y] = '*'
                    continue
                elif grid[x][y] == 1:
                    value[x][y] = 1000
                    continue
                for a, v in enumerate(delta):
                    v = cost_step
                    for i in range(-1, 2):
                        action = (a + i) % len(delta)
                        x2, y2 = x + delta[action][0], y + delta[action][1]
                        prob = success_prob if i == 0 else failure_prob
                        if x2 in range(len(grid)) and y2 in range(len(grid[0])) and grid[x2][y2] == 0:
                            v += prob * value[x2][y2]
                        else:
                            v += prob * collision_cost
                    if v < value[x][y]:
                        value[x][y] = v
                        policy[x][y] = delta_name[a]
    for r in value:
        print r
    for r in policy:
        print r
    return value, policy


#value, policy = stochastic_value()
