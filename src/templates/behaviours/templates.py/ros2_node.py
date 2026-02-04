# behavior_tree_node.py (continued)
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('behavior_tree_node')
        
        # Create the behavior tree
        self.tree = create_behavior_tree(self)
        self.tree.setup(timeout=15)
        
        # Service to execute task
        self.execute_srv = self.create_service(
            ExecuteTask, 
            '/execute_task', 
            self.execute_task_callback
        )
        
        # Timer to tick tree
        self.timer = self.create_timer(0.1, self.tick_tree)  # 10 Hz
        self.executing = False
        
        self.get_logger().info("Behavior tree node ready")
        
    def execute_task_callback(self, request, response):
        """Service handler to start task execution"""
        if self.executing:
            response.success = False
            response.message = "Already executing a task"
            return response
            
        # Store command on blackboard
        self.tree.blackboard.set(BlackboardKeys.COMMAND, request.command)
        
        # Reset and start tree execution
        self.tree.root.reset()
        self.executing = True
        
        response.success = True
        response.message = "Task started"
        return response
        
    def tick_tree(self):
        """Called at 10 Hz to advance tree execution"""
        if not self.executing:
            return
            
        # Tick the tree once
        self.tree.tick()
        
        # Check if tree finished
        if self.tree.root.status != py_trees.common.Status.RUNNING:
            if self.tree.root.status == py_trees.common.Status.SUCCESS:
                self.get_logger().info("✓ Task completed successfully!")
            else:
                self.get_logger().error("✗ Task failed")
            self.executing = False

def main(args=None):
    rclpy.init(args=args)
    node = BehaviorTreeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()