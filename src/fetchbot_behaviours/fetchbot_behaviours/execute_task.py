
import rclpy
from rclpy.node import Node
import py_trees
from fetchbot_behaviours.behaviour_tree import create_behavior_tree
import py_trees.display as display
from rclpy.executors import MultiThreadedExecutor

class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('behavior_tree_node')
        
        # Create the behavior tree
        self.tree = create_behavior_tree(self)
        self.tree.setup(timeout=15)

        self.blackboard = py_trees.blackboard.Client(name="Client")
        self.blackboard.register_key("user_command", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key("is_search_plan_generated", access=py_trees.common.Access.WRITE)
        

        # Timer to tick tree
        self.timer = self.create_timer(0.1, self.tick_tree)  # 10 Hz
        self.tick_count = 0
        self.executing = False
        self.get_logger().info("Behavior tree node ready")

    def execute_task(self, user_command:str):   
        # Reset and start tree execution
        self.tree.root.stop(py_trees.common.Status.INVALID) 
        self.tick_count = 0  # Reset on new task
        self.executing = True
        self.get_logger().info("Starting task execution...")
        self.blackboard.set("user_command", user_command)
        self.blackboard.set("is_search_plan_generated", False)
        
        
    def tick_tree(self):
        """Called at 10 Hz to advance tree execution"""
        if not self.executing: 
            return
            
        # Tick the tree once
        self.tree.tick()

        self.tick_count += 1  # Increment counter
        self.get_logger().info(f"Tick #{self.tick_count}") #Debug
       
        # Show tree with status
        print(display.unicode_tree(self.tree.root, show_status=True))
        # Show blackboard activity
        print(display.unicode_blackboard())
    

        
        # Check if tree finished
        if self.tree.root.status != py_trees.common.Status.RUNNING:
            self.executing = False
            if self.tree.root.status == py_trees.common.Status.SUCCESS:
                self.get_logger().info("✓ Task completed successfully!")
                self.tick_count = 0

            else:
                self.get_logger().error("✗ Task failed")
            self.tree.root.stop(py_trees.common.Status.INVALID)
            self.tick_count = 0
           
        else:
            self.get_logger().info("RUNNING")

def main(args=None):
    rclpy.init(args=args)
    node = BehaviorTreeNode()
  
    node.execute_task("Bring blue book from kitchen")

    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()