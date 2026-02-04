# behavior_base_class.py
import py_trees
import rclpy
from rclpy.node import Node

class RobotBehavior(py_trees.behaviour.Behaviour):
    """Base class for all robot behaviors"""
    
    def __init__(self, name, node):
        super().__init__(name)
        self.node = node  # ROS2 node for calling services/actions
        self.blackboard = self.attach_blackboard_client()
        
    def setup(self, **kwargs):
        """One-time setup (create service clients, etc)"""
        pass
        
    def initialise(self):
        """Called when behavior starts executing"""
        pass
        
    def update(self):
        """Called every tick while behavior is running"""
        # Return: SUCCESS, FAILURE, or RUNNING
        return py_trees.common.Status.SUCCESS
        
    def terminate(self, new_status):
        """Called when behavior finishes (success or failure)"""
        pass