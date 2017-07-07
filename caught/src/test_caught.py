""" Simple interface to test caught_robber.py """
__author__ = "LT"
__copyright__ = "Copyright 2017, Cohrint"
__license__ = "GPL"
__version__ = "1.1"
__maintainer__ = "LT"
__email__ = "luba6098@colorado.edu"
__status__ = "Development"

import rospy
from caught.msg import Caught
import pymsgbox

class Test_Caught(object):

	def __init__(self, num_robbers):
		rospy.init_node('test_caught')
		rospy.Subscriber('/caught', Caught, self.robber_callback)
		self.pub = rospy.Publisher('/caught_confirm', Caught, queue_size=10)
		self.num_robbers = num_robbers
		print("Test Caught Ready!")
		rospy.spin()

	def robber_callback(self, msg):
		res = pymsgbox.confirm("Did I catch "+ msg.robber +" ?" , title="Robber Caught?", buttons=["Yes", "No"])
		if res == "Yes":
			print("Marking " + msg.robber + " as caught!")
			msg_res = Caught()
			msg_res.robber = msg.robber
			msg_res.confirm = True
			self.pub.publish(msg)
			self.num_robbers -= 1
			if self.num_robbers == 0:
				rospy.signal_shutdown("All Robbers Caught!")


if __name__ == '__main__':
    a = Test_Caught(1)