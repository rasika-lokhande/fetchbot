# behavior_tree_node.py (continued)
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
import py_trees

class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('behavior_tree_node')
        
        self.tree = create_behavior_tree(self)
        self.tree.setup(timeout=15)
        
        # Action server instead of service
        self.action_server = ActionServer(
            self,
            ExecuteTask,
            '/execute_task',
            self.execute_callback
        )
        
        self.timer = self.create_timer(0.1, self.tick_tree)
        self.current_goal_handle = None
        
    def execute_callback(self, goal_handle):
        """Action callback - runs in separate thread"""
        self.current_goal_handle = goal_handle
        
        # Store command on blackboard
        self.tree.blackboard.set(BlackboardKeys.COMMAND, goal_handle.request.command)
        self.tree.root.reset()
        
        # Wait for tree to complete
        while self.tree.root.status == py_trees.common.Status.RUNNING:
            # Check if cancel requested
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return ExecuteTask.Result(success=False, message="Canceled")
                
            time.sleep(0.1)
            
        # Return result
        result = ExecuteTask.Result()
        if self.tree.root.status == py_trees.common.Status.SUCCESS:
            result.success = True
            result.message = "Task completed"
            goal_handle.succeed()
        else:
            result.success = False
            result.message = "Task failed"
            goal_handle.abort()
            
        return result
        
    def tick_tree(self):
        """Tick tree and publish feedback"""
        if self.tree.root.status != py_trees.common.Status.RUNNING:
            return
            
        self.tree.tick()
        
        # Publish feedback if action is active
        if self.current_goal_handle is not None:
            feedback = ExecuteTask.Feedback()
            feedback.current_step = self.get_current_behavior_name()
            feedback.progress = self.estimate_progress()
            self.current_goal_handle.publish_feedback(feedback)

def main(args=None):
    rclpy.init(args=args)
    node = ExecuteTaskNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()