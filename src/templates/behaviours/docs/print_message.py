import py_trees

class PrintMessage(py_trees.behaviour.Behaviour):
    def __init__(self, name, message):
        # Every behavior must call the parent constructor with a name
        super(PrintMessage, self).__init__(name)
        self.message = message
        
    def update(self):
        # The update() method is the heart of any behavior
        # It gets called repeatedly and must return a status
        print(f"{self.name}: {self.message}")
        
        # We're done after printing once, so return SUCCESS
        return py_trees.common.Status.SUCCESS

# Create an instance of our behavior
my_behavior = PrintMessage(name="Greeter", message="Hello from py_trees!")

# Before we can use a behavior, we must set it up
my_behavior.setup()

# Now let's tick it (execute one update cycle)
status = my_behavior.update()

print(f"Behavior returned: {status}")