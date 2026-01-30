# Notes for creating custom interfaces


If you find the perfect match in an already existing message (ex: from geometry_msgs, sensor_msgs, etc.), then use it instead of reinventing the wheel. Otherwise, create your own ROS2 custom message.


After you’ve created a new package + initialized it, for each new interface you’ll need to:

1. Create a new file under the appropriate directory (msg/, srv/).
2. Write the interface inside the file.
3. Add the file in the CMakeLists.txt of the interfaces packages.
4. Build the interfaces package.