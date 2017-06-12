from __future__ import division


# DISCRETIZED MAP TRANSLATOR

from gaussianMixtures import Gaussian, GM

import random                   # testing getNextPose
import matplotlib.pyplot as plt # testing getNextPose
import sys
import numpy as np

__author__ = "LT"
__copyright__ = "Copyright 2017, Cohrint"
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "LT"
__email__ = "luba6098@colorado.edu"
__status__ = "Development"


class MAPTranslator(object):


    def __init__(self):
        self.delta = 0.1
        pass





    """
    Takes a belief and returns the goal
    pose (MAP coordinate list [x.y] in [m, m])
    (orientation is calculated in
    the Policy Translator Service)

    -Calls the findMAP function to find the [x,y] MAP
    coordinate.

    Parameters
    ----------
    belief : belief object

    Returns
    -----------
    goal_pose : [x, y] in [m,m]

    """

    # belief is a 2D grid because of the discretization
    def getNextPose(self, belief):



        #grid from plot 2D function
        max_coord = self._find_array2D_max(belief)
        goal_pose = self._grid_coord_to_world_coord(max_coord)

        # TODO call belief update method here
        # belief is a GM instance, find MAP coords [x,y]
        return [belief, belief.findMAPN()]

    """ Locates the max coord of the 2D array"""
    def _find_array2D_max(self, array2D):
        max_num = 0
        max_coord = [0,0]
        size = array2D.shape # tuple of numpy array size

        for i in range(size[0]):
            for j in range(size[1]):
                if (array2D[i,j] > max_num):
                    max_coord = [i,j]
                    max_num = array2D[i,j]  # set new max num
        return max_coord

    """ Inputs the max grid coord and returns the
        world map coord equivalent"""
    def _grid_coord_to_world_coord(self, coord, world_min_x_y=[0,0]):
        d = self.delta
        world_coord = [0,0]
        world_coord[0] = world_min_x_y[0] + d * coord[0] # world x coord
        world_coord[1] = world_min_x_y[1] + d * coord[1] # world y coord
        return world_coord

    def beliefUpdate(self, belief, action, observation):
        pass


    def getQuestions(self, belief):
        pass

""" Creates a belief, call getNextPose to find the MAP
    verifies the coord returned is the actual MAP
        -Features: will plot the given MAP using plt.contourf """
def testGetNextPose(rndm=None):
    print "Testing MAP Translator!"
    MAP = MAPTranslator()


    if (rndm):
        random.seed()
        means = [[rdm(), rdm()], [rdm(),rdm()], [rdm(), rdm()],[rdm(), rdm()]]
        variances = [[1,0], [0,1]]
        weights = [1.5, 2, rdm(), rdm()]
        pos = [1,1]

    else:
        means = [[2,3],[5,5],[3,1],[3,4]]               # Also the MAP location
        variances = [[1,0], [0,1]]
        weights = [1.5, 2, 1.5, 0.7]
        pos = [1,1]

    # create the belief
    b = GM()
    b.addG(Gaussian(means[0], variances, weights[0]))
    b.addG(Gaussian(means[1], variances, weights[1]))
    b.addG(Gaussian(means[2], variances, weights[2]))
    b.addG(Gaussian(means[3], variances, weights[3]))
    b.normalizeWeights()

    # [b_updated, goal_pose] = MAP.getNextPose(b, None, None)
    # print "Means: " + str(means)
    # print "MAP Goal Pose: " + str(goal_pose)


    # plot using matplotlib contourf
    [x, y, c] = b.plot2D(low=[0,0], high=[10,10], vis=False, res = 100)
    max_pt = MAP._find_array2D_max(c)
    min_x_y = [5.2, 8.752]
    MAP.delta = 0.1
    print(max_pt)
    print(MAP._grid_coord_to_world_coord(max_pt, min_x_y))

    plt.contourf(x, y, c, cmap='viridis')
    # plt.pause(0.1)
    # raw_input('Show MAP?')
    # plt.scatter(goal_pose[0], goal_pose[1])
    plt.show()



def rdm():
    return random.randint(0, 5)

if __name__ == '__main__':
    testGetNextPose(1)
