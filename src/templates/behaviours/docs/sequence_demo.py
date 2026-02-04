import rclpy
from rclpy.node import Node
import py_trees
from py_trees.composites import Sequence

class CheckBattery(py_trees.behaviour.Behaviour):
    """Simulates checking if battery is low"""
    def __init__(self, name, battery_level):
        super(CheckBattery, self).__init__(name)
        self.battery_level = battery_level
        
    def update(self):
        print(f"{self.name}: Checking battery level... it's at {self.battery_level}%")
        
        if self.battery_level < 20:
            print(f"{self.name}: Battery is LOW! Returning SUCCESS (yes, it's low)")
            return py_trees.common.Status.SUCCESS
        else:
            print(f"{self.name}: Battery is fine. Returning FAILURE (no, it's not low)")
            return py_trees.common.Status.FAILURE


class GoToCharger(py_trees.behaviour.Behaviour):
    """Simulates navigating to charging station"""
    def __init__(self, name):
        super(GoToCharger, self).__init__(name)
        self.ticks_needed = 3
        self.current_tick = 0
        
    def initialise(self):
        print(f"{self.name}: Starting navigation to charger")
        self.current_tick = 0
        
    def update(self):
        self.current_tick += 1
        print(f"{self.name}: Navigating... ({self.current_tick}/{self.ticks_needed})")
        
        if self.current_tick < self.ticks_needed:
            return py_trees.common.Status.RUNNING
        else:
            print(f"{self.name}: Arrived at charger!")
            return py_trees.common.Status.SUCCESS
            
    def terminate(self, new_status):
        if new_status == py_trees.common.Status.SUCCESS:
            print(f"{self.name}: Navigation complete")


class Charge(py_trees.behaviour.Behaviour):
    """Simulates charging"""
    def __init__(self, name):
        super(Charge, self).__init__(name)
        
    def update(self):
        print(f"{self.name}: Charging battery... Done!")
        return py_trees.common.Status.SUCCESS


class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('sequence_demo_node')
        
        # Create a Sequence composite
        # This says: "Check battery AND navigate to charger AND charge"
        self.root = Sequence(name="Battery Management", memory=False)
        
        # Add children to the sequence in the order they should execute
        self.root.add_children([
            CheckBattery(name="Check Battery", battery_level=15),
            GoToCharger(name="Navigate to Charger"),
            Charge(name="Charge Battery")
        ])
        
        # Set up the tree
        self.root.setup_with_descendants()
        
        # Create timer to tick the tree every 0.5 seconds
        self.timer = self.create_timer(0.5, self.tick_tree)
        
        self.tick_count = 0
        self.get_logger().info("Sequence demo started - Battery is at 15%")
        
    def tick_tree(self):
        self.tick_count += 1
        self.get_logger().info(f"\n{'='*50}")
        self.get_logger().info(f"TICK {self.tick_count}")
        self.get_logger().info(f"{'='*50}")
        
        self.root.tick_once()
        
        self.get_logger().info(f"Sequence status: {self.root.status}")
        
        # Stop after the sequence completes
        if self.root.status != py_trees.common.Status.RUNNING:
            self.get_logger().info(f"\nSequence finished with status: {self.root.status}")
            self.get_logger().info("Stopping ticks...")
            self.timer.cancel()


def main(args=None):
    rclpy.init(args=args)
    node = BehaviorTreeNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()