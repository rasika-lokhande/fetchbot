import rclpy
from rclpy.node import Node
import py_trees
from py_trees.composites import Sequence

class InstantBehavior(py_trees.behaviour.Behaviour):
    """A behavior that completes immediately"""
    def __init__(self, name):
        super(InstantBehavior, self).__init__(name)
        
    def update(self):
        print(f"  {self.name}: Executing and completing immediately")
        return py_trees.common.Status.SUCCESS


class SlowBehavior(py_trees.behaviour.Behaviour):
    """A behavior that takes multiple ticks to complete"""
    def __init__(self, name, ticks_needed):
        super(SlowBehavior, self).__init__(name)
        self.ticks_needed = ticks_needed
        self.current_tick = 0
        
    def initialise(self):
        # Called once when this behavior first starts
        self.current_tick = 0
        print(f"  {self.name}: STARTING (will need {self.ticks_needed} ticks)")
        
    def update(self):
        # Called on every tick while this behavior is active
        self.current_tick += 1
        print(f"  {self.name}: Working... (tick {self.current_tick}/{self.ticks_needed})")
        
        if self.current_tick < self.ticks_needed:
            print(f"  {self.name}: Still working, returning RUNNING")
            return py_trees.common.Status.RUNNING
        else:
            print(f"  {self.name}: FINISHED, returning SUCCESS")
            return py_trees.common.Status.SUCCESS


class BehaviorTreeNode(Node):
    def __init__(self):
        super().__init__('sequence_multi_tick_demo')
        
        # Create a Sequence with a mix of instant and slow behaviors
        self.root = Sequence(name="Mission", memory=False)
        
        self.root.add_children([
            InstantBehavior(name="Step 1 (instant)"),
            SlowBehavior(name="Step 2 (needs 3 ticks)", ticks_needed=3),
            InstantBehavior(name="Step 3 (instant)"),
            SlowBehavior(name="Step 4 (needs 2 ticks)", ticks_needed=2),
            InstantBehavior(name="Step 5 (instant)")
        ])
        
        self.root.setup_with_descendants()
        
        # Timer fires every 1 second
        self.timer = self.create_timer(1.0, self.tick_tree)
        
        self.tick_count = 0
        self.get_logger().info("Starting multi-tick Sequence demo")
        self.get_logger().info("Watch which behaviors execute on each tick!\n")
        
    def tick_tree(self):
        self.tick_count += 1
        
        print(f"\n{'='*70}")
        print(f"TICK {self.tick_count} - Timer fired at {self.get_clock().now().nanoseconds / 1e9:.2f}s")
        print(f"{'='*70}")
        
        # Tick the tree once
        self.root.tick_once()
        
        print(f"\nSequence status after this tick: {self.root.status}")
        print(f"{'='*70}\n")
        
        # Stop once the sequence completes
        if self.root.status != py_trees.common.Status.RUNNING:
            self.get_logger().info(f"Sequence completed with status: {self.root.status}")
            self.get_logger().info("Stopping timer...")
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