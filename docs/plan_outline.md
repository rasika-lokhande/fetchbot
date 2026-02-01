# Fetchbot: All Days Objectives

## Day 1: Navigation Foundation

**Environment Setup (2-3 hours)**
- Install ROS2 Humble, Gazebo, Nav2, TurtleBot3 packages
- Set up `~/fetchbot/ros2_ws/src` directory structure
- Install Docker, create Git repository

**Simulation Running (1 hour)**
- Launch TurtleBot3 House world
- Verify robot, LIDAR, camera active
- Test teleoperation works

**Mapping (1-2 hours)**
- Run SLAM Toolbox
- Drive through all rooms, build complete map
- Save map to `~/fetchbot/maps/turtlebot_house.yaml`

**Navigation (2-3 hours)**
- Launch Nav2 with saved map
- Set initial pose in RViz
- Send navigation goals to different rooms
- Verify 90%+ success rate

**Success Criteria**
- Click any goal in RViz, robot navigates there successfully
- Handles doorways and furniture without collisions

---

## Day 2: Vision-Language Integration

**Vision Service (2-3 hours)**
- Create Flask app with CLIP model, `/detect` endpoint
- Write Dockerfile, build `fetchbot-vision:latest`
- Test via curl

**ROS2 Vision Bridge (2 hours)**
- Create `fetchbot_perception` package
- Write `vision_bridge.py`: camera → Docker API → publish detections
- Verify `/detected_objects` topic

**Object Placement (1 hour)**
- Add 4 colored objects to TurtleBot House
- Place on tables/shelves

**Active Search (2-3 hours)**
- Create `object_search.py` with action interface
- Rotate robot while checking vision
- Return success when object found

**Success Criteria**
- Robot finds all 4 test objects when requested
- Tuned confidence thresholds, minimal false positives

---

## Day 3: Natural Language Understanding

**LLM Setup (30 min)**
- Get OpenAI API key
- Test basic API call

**Schema Design (30 min)**
- Define JSON structure: `{target_object, source_location, destination_location}`
- List valid rooms

**Prompt Engineering (2 hours)**
- Write system prompt with examples
- Test varied commands, refine prompts
- Handle ambiguous commands

**ROS2 Service (2 hours)**
- Create `fetchbot_language` package
- Write `command_parser.py` service
- Validate parsed locations

**Testing (2 hours)**
- Build CLI test interface
- Test 20+ command variations
- Document accuracy

**Success Criteria**
- 90%+ parsing accuracy
- Ambiguous commands trigger clarification
- All command types parse correctly

---

## Day 4: Behavior Orchestration

**Behavior Tree Setup (1 hour)**
- Install py_trees
- Design tree structure on paper
- Map task sequence: parse → navigate → search → approach → grasp → deliver

**Individual Behaviors (3-4 hours)**
- Command parsing behavior (calls language service)
- Navigation behaviors (calls Nav2)
- Object search behavior (calls vision action)
- Approach behavior (navigate near detected object)
- Simulated grasp/release behaviors

**Recovery Behaviors (2 hours)**
- Navigation retry with alternate approach
- Multi-room search if object not found
- Timeout handling

**Integration (2-3 hours)**
- Implement blackboard data sharing
- Add logging/telemetry
- Create launch file for complete system

**Success Criteria**
- End-to-end task: command → parse → navigate → find → deliver
- At least 3 successful runs with different objects/rooms
- Recovery behaviors trigger and succeed

---

## Day 5: Robustness & Performance

**Error Handling (2 hours)**
- Add try-except blocks throughout
- Handle service/API failures gracefully
- Implement retry logic with backoff

**Parameter Tuning (1-2 hours)**
- Create ROS2 parameter file
- Expose key settings (thresholds, timeouts, speeds)
- Test parameter variations

**Temporal Filtering (1 hour)**
- Require detections persist across 5-10 frames
- Implement voting scheme (70% agreement)

**Semantic Reasoning (2 hours)**
- Create object→room associations
- Prioritize likely locations when searching
- Fall back to exhaustive search

**Testing & Metrics (2-3 hours)**
- Build test suite (10+ scenarios)
- Measure success rate, completion time, latency
- Document failure modes and frequencies

**Success Criteria**
- 80%+ task success rate
- Documented performance metrics
- Common failures identified with frequencies

---

## Day 6: Documentation & Demo

**README (2 hours)**
- High-level overview
- Architecture diagram
- Design decisions explained
- Installation instructions

**Video Demos (2-3 hours)**
- Record 3+ successful runs (different objects/rooms)
- Record 1 failure recovery example
- Create 2-min highlights reel
- Add text overlays explaining what's happening

**Technical Report (2 hours)**
- Write blog post/report narrative
- Include code snippets, performance graphs
- Explain challenges and solutions

**Presentation (1 hour)**
- Create 6-8 slides
- Practice 10-min delivery

**Code Cleanup (1-2 hours)**
- Add docstrings
- Remove debug code
- Consistent formatting
- Organize files logically

**GitHub (30 min)**
- Push to public repository
- Verify README renders well
- Add relevant tags

**Success Criteria**
- Complete professional documentation package
- Polished video demonstrations
- Clean, well-organized codebase

---

## Day 7: Buffer & Polish

**If Behind Schedule**
- Complete unfinished core functionality
- Debug failing components
- Get basic end-to-end working

**If On Schedule - Choose ONE Extension**
- **Multi-object tasks**: Queue multiple fetches, optimize route
- **Human-aware navigation**: Add simulated humans, larger safety margins
- **Dialogue capabilities**: Answer status questions ("where are you?")
- **Learning from corrections**: Remember where objects found

**Polish (remainder of time)**
- Run test suite, fix intermittent failures
- Improve error messages
- Add detailed logging
- Review all documentation for accuracy
- Practice explaining project

**Final Verification**
- Checklist: can demonstrate every capability
- All videos render correctly
- GitHub repository complete
- Presentation ready

**Success Criteria**
- All core functionality works reliably
- Professional documentation complete
- Ready to demonstrate in interviews