# Fetchbot: Week Overview

**Day 1**: Set up Ubuntu/ROS2/Gazebo environment, create a simulated apartment with three rooms, configure Nav2 stack with SLAM mapping, and achieve reliable autonomous navigation between any two points in the environment.

**Day 2**: Build a Dockerized CLIP vision service with Flask API, create a ROS2 vision bridge node that processes camera images, implement active object search that rotates the robot while detecting objects, and successfully recognize and locate target objects by name.

**Day 3**: Set up OpenAI GPT API for natural language processing, design prompts that parse commands like "bring me the red cup from the kitchen" into structured JSON task specifications, create a ROS2 service interface for command parsing, and handle ambiguous commands with clarification requests.

**Day 4**: Install py_trees behavior tree library, design a hierarchical behavior tree that sequences command parsing → navigation → object search → approach → grasp → delivery, implement recovery behaviors for common failures, and achieve end-to-end fetch-and-deliver task execution.

**Day 5**: Add comprehensive error handling and parameter tuning, implement temporal filtering for vision false positives, add semantic reasoning about where objects are typically found, optimize inference latency, create a test suite measuring success rates and failure modes, and document performance metrics showing 80%+ reliability.

**Day 6**: Write comprehensive README with architecture diagrams, record video demonstrations of successful tasks and failure recovery, create a technical blog post with code examples and performance data, prepare a 5-8 slide presentation, clean up code with proper docstrings, and push everything to a polished GitHub repository.

**Day 7**: Use buffer time to complete any unfinished core functionality, optionally add one advanced feature (multi-object tasks, human-aware navigation, or dialogue capabilities), polish all documentation, practice explaining the project, and verify all demonstrations work reliably.