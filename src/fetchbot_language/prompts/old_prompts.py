LOCATIONS = ["living room", "bedroom", "kitchen", "entrance"]
OBJECTS = ["yellow ball", "red cup", "blue book", "green bottle"]


SYSTEM_PROMPT = f"""Extract fetch command information from user input.

Fields:
- target_object: the item to fetch (use only from {OBJECTS})
- source_location: where to find it (use: {LOCATIONS} or "unknown")
- destination_location: where to bring it (use room names or "user" if bringing to the person)

If location not mentioned, use "unknown" for source and "user" for destination."""