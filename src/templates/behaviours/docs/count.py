import py_trees

class PrintMessage(py_trees.behaviour.Behaviour):
    def __init__(self, name, message):
        super(PrintMessage, self).__init__(name)
        self.message = message
        
    def update(self):
        # This gets called when the behavior executes
        print(f"{self.name}: {self.message}")
        # Return SUCCESS to indicate we're done
        return py_trees.common.Status.SUCCESS

# Create the behavior
behavior = PrintMessage(name="Greeter", message="Hello!")

# Set it up (required before ticking)
behavior.setup_with_descendants()

# Execute it once - ROS node will call it in a timer
behavior.tick_once()

# Check the status
print(f"Final status: {behavior.status}")