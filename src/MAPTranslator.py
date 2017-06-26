from __future__ import division


# DISCRETIZED MAP TRANSLATOR

from gaussianMixtures import Gaussian, GM

import random                   # testing getNextPose
import matplotlib.pyplot as plt # testing getNextPose
import sys
import numpy as np
import os;
import copy;
from map_maker import Map
from matplotlib import patches
import matplotlib.tri as tri;
import math
import matplotlib
from voi import Questioner

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
        # f = self.findFile('likelihoods.npy','./');
        f = os.path.dirname(__file__) + "/likelihoods.npy"
        self.likelihoods = np.load(f)
        # self.likelihoods = np.load("likelihoods.npy")
        self.bounds = [-9.6, -3.6, 4, 3.6]
        self.questioner = Questioner(human_sensor=None,target_order=["roy","pris"],target_weights=[11., 10.],bounds=self.bounds,delta=0.1,
                        repeat_annoyance=0.5, repeat_time_penalty=60)

    def findFile(self,name,path):
        for root,dirs,files in os.walk(path):
            if name in files:
                return os.path.join(root,name);


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
    def getNextPose(self,belief,obs,copPoses=None):

        #grid from plot 2D function
        # obs = self.Obs_Queue.flush()
        belief = self.beliefUpdate(belief,obs,copPoses)
        max_coord = self._find_array2D_max(belief)
        print("MAX COORD: {}".format(max_coord))
        goal_pose = self._grid_coord_to_world_coord(max_coord,world_min_x_y=[self.bounds[0],self.bounds[1]])
        self.questioner.get_questions(belief)

        # TODO call belief update method here
        # belief is a GM instance, find MAP coords [x,y]
        return [belief, goal_pose]

    """ Locates the max coord of the 2D array
        and returns its index"""
    def _find_array2D_max(self, array2D):
        max_num = 0
        max_index = [0,0]
        size = array2D.shape # tuple of numpy array size

        for i in range(size[0]):
            for j in range(size[1]):
                if (array2D[i,j] > max_num):
                    max_index = [i,j]
                    max_num = array2D[i,j]  # set new max num
        return max_index

    """ Inputs the max grid coord and returns the
        world map coord equivalent"""
    def _grid_coord_to_world_coord(self, coord, world_min_x_y=[0,0]):
        d = self.delta
        world_coord = [0,0]
        world_coord[0] = world_min_x_y[0] + d * coord[0] # world x coord
        world_coord[1] = world_min_x_y[1] + d * coord[1] # world y coord
        return world_coord

    def unFlatten(self,arr,shapes):
        newArr = np.zeros((shapes[0],shapes[1]));
        for i in range(0,shapes[0]):
            for j in range(0,shapes[1]):
                newArr[i][j] = arr[i*shapes[1]+j];
        return newArr;

    def normalize(self,arr):
           suma = sum(arr);
           for i in range(0,len(arr)):
               arr[i] = arr[i]/suma;
           return arr;


    def beliefUpdate(self, belief, responses = None,copPoses = None):

        flatBelief = belief.flatten();
        post = flatBelief;
        if(responses is not None):
            for res in responses:
                if(res[1] == True):
                    like = self.likelihoods[res[0]][1];
                else:
                    like = 1-self.likelihoods[res[0]][1];
                #print(self.likelihoods[res[0]][0],res[1])
                posterior = np.multiply(post,like);
                post = self.normalize(posterior);


        if(copPoses is not None):
            for pose in copPoses:
                bearing = 0;
                l = 1;
                triPath = matplotlib.path.Path([[pose[0],pose[1]],[pose[0]+l*math.cos(2*-0.261799+math.radians(pose[2]+(bearing)+90)),pose[1]+l*math.sin(2*-0.261799+math.radians(pose[2]+(bearing)+90))],[pose[0]+l*math.cos(2*0.261799+math.radians(pose[2]+(bearing)+90)),pose[1]+l*math.sin(2*0.261799+math.radians(pose[2]+(bearing)+90))]]);

                l = .6;
                triPath2 = matplotlib.path.Path([[pose[0],pose[1]],[pose[0]+l*math.cos(2*-0.261799+math.radians(pose[2]+(bearing)+90)),pose[1]+l*math.sin(2*-0.261799+math.radians(pose[2]+(bearing)+90))],[pose[0]+l*math.cos(2*0.261799+math.radians(pose[2]+(bearing)+90)),pose[1]+l*math.sin(2*0.261799+math.radians(pose[2]+(bearing)+90))]]);



                viewLike = np.ones(belief.shape);
                for i in range(0,belief.shape[0]):
                    for j in range(0,belief.shape[1]):
                        x = i*self.delta + self.bounds[0];
                        y = j*self.delta + self.bounds[1];

                        if(triPath.contains_point([x,y])):
                            viewLike[i][j] = .4;

                        if(triPath2.contains_point([x,y])):
                            viewLike[i][j] = .1;

                viewLike = viewLike.flatten();
                posterior = np.multiply(post,viewLike);
                post = self.normalize(posterior);
                #levels = [i/250 + 1 for i in range(0,250)]

                #tpl = plt.tricontourf(triang,[2,1,1],cmap="inferno",alpha=0.5,levels=levels);

        post = self.unFlatten(post,belief.shape);
        if copPoses is not None:
            pose = copPoses[len(copPoses)-1]
            print("MAP COP POSE TO PLOT: {}".format(pose))
            self.makeBeliefMap(post,pose)



        return post;


    def makeBeliefMap(self, belief,copPose = [0,0,0]):
        print("MAKING NEW BELIEF MAP!")
        figure = plt.figure()
        x_space,y_space = np.mgrid[self.bounds[0]:self.bounds[2]:self.delta,self.bounds[1]:self.bounds[3]:self.delta];
        plt.contourf(x_space,y_space,belief,cmap="viridis");
        m = Map('map2.yaml');
        for obj in m.objects:
            cent = m.objects[obj].centroid;
            x = m.objects[obj].x_len;
            y = m.objects[obj].y_len;
            theta = m.objects[obj].orient;
            col = m.objects[obj].color
            # print(obj);
            # print(col);
            # print(theta);
            # print("");
            if(m.objects[obj].shape == 'oval'):
                tmp = patches.Ellipse((cent[0] - x/2,cent[1]-y/2),width = x, height=y,angle=theta,fc=col,ec='black');
            else:
                tmp = patches.Rectangle((cent[0]- x/2,cent[1]-y/2),width = x, height=y,angle=theta,fc=col,ec='black');
            plt.gca().add_patch(tmp);

        bearing = 0;
        l = 1;
        triang=tri.Triangulation([copPose[0],copPose[0]+l*math.cos(2*-0.261799+math.radians(copPose[2]+(bearing)+90)),copPose[0]+l*math.cos(2*0.261799+math.radians(copPose[2]+(bearing)+90))],[copPose[1],copPose[1]+l*math.sin(2*-0.261799+math.radians(copPose[2]+(bearing)+90)),copPose[1]+l*math.sin(2*0.261799+math.radians(copPose[2]+(bearing)+90))])

        levels = [i/250 + 1 for i in range(0,250)]

        tpl = plt.tricontourf(triang,[2,1,1],cmap="inferno",alpha=0.5,levels=levels);

        cop = patches.Circle((copPose[0],copPose[1]),radius=0.2,fc = 'white',ec='black');
        plt.gca().add_patch(cop);

        plt.axis('scaled');
        plt.axis('off')
        plt.savefig(os.path.abspath(os.path.dirname(__file__) + '/../tmp/tmpBelief.png'));
        # plt.show();

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
        print("Determined Test")
        means = [[2,3],[2,4],[3,1],[3,4]]               # Also the MAP location
        variances = [[1,0], [0,1]]
        weights = [1.5, 2, 1.5, 0.7]
        pos = [1,1]

    # create the belief
    b = GM()
    b.addG(Gaussian(means[0], variances, weights[0]))
    b.addG(Gaussian(means[1], variances, weights[1]))
    b.addG(Gaussian(means[2], variances, weights[2]))
    b.addG(Gaussian(means[3], variances, weights[3]))
    b.normalizeWeights()            # all GaussianMixtures must be normalized

    min_x_y = [-6,-6]
    max_x_y = [8,8]
    d = 0.1
    grid = b.discretize2D(low=min_x_y, high=max_x_y, delta=d)

    max_pt = MAP._find_array2D_max(grid)

    # TODO why do these need to be reversed?
    # switch x and y
    x = max_pt[1]
    y = max_pt[0]
    max_pt = [x,y]

    MAP.delta = d
    print("In Luke's Discretized coords, the MAX is: "+ str(max_pt))
    print("In World Coords from "+ str(min_x_y) + " to " + str(max_x_y) + " with delta: "+str(MAP.delta)+ ". The MAP would be: " + str(MAP._grid_coord_to_world_coord(max_pt, min_x_y)))

    plt.contourf(grid, cmap='viridis')
    plt.pause(0.1)
    raw_input("Show MAP?")
    plt.scatter(max_pt[0], max_pt[1])
    plt.show()

def testBeliefUpdate():
    print "Testing Belief Update!"
    MAP = MAPTranslator();
    belief = GM();
    belief.addG(Gaussian([0,0],[[8,0],[0,8]],0.5));
    belief.addG(Gaussian([-8,-1],[[4,0],[0,4]],0.5));
    db = belief.discretize2D(low=[MAP.bounds[0],MAP.bounds[1]],high=[MAP.bounds[2],MAP.bounds[3]],delta=MAP.delta);

    responses = [[50,True],[3,True],[15,False]];
    copPoses = [];
    for i in range(0,20):
        copPoses.append([-i/10,.45,90]);
    MAP.makeBeliefMap(db,copPose = copPoses[0]);

    post = MAP.beliefUpdate(db,responses,copPoses);
    MAP.makeBeliefMap(post,copPose = copPoses[-1]);

    # print(sum(sum(post)));
    # print(db.shape);


    # like = MAP.unFlatten(MAP.likelihoods[questionNum][1],db.shape);
    #like = MAP.likelihoods[questionNum][1];
    # print(like.shape);
    # print(post.shape);

    x_space,y_space = np.mgrid[MAP.bounds[0]:MAP.bounds[2]:MAP.delta,MAP.bounds[1]:MAP.bounds[3]:MAP.delta];

    fig,axarr = plt.subplots(2);
    axarr[0].contourf(x_space,y_space ,db);
    axarr[0].set_title('Prior');
    # axarr[1].contourf(x_space,y_space ,like);
    # axarr[1].set_title('Likelihood');
    axarr[1].contourf(x_space,y_space ,post);
    axarr[1].set_title('Posterior');
    #plt.suptitle('Belief Update for question:' + str(MAP.likelihoods[questionNum][0]));
    plt.show();

def testMakeMap():
    print "Testing Map creation!"
    MAP = MAPTranslator();
    belief = GM();
    belief.addG(Gaussian([0,0],[[8,0],[0,8]],0.5));
    belief.addG(Gaussian([-8,-1],[[4,0],[0,4]],0.5));
    db = belief.discretize2D(low=[MAP.bounds[0],MAP.bounds[1]],high=[MAP.bounds[2],MAP.bounds[3]],delta=MAP.delta);

    copPose = [-2,-1,45]
    MAP.makeBeliefMap(db,copPose);


def rdm():
    return random.randint(0, 5)

if __name__ == '__main__':
    #testGetNextPose();
    #testBeliefUpdate();
    testMakeMap();
