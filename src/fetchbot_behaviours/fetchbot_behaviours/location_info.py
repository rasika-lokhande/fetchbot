

class LocationInfo:

    def __init__(self):
        self.loc_probs = {
            'red cup': {
                'kitchen': 0.6,      # Cups belong in kitchen
                'living_room': 0.2,  # Sometimes left there
                'bedroom': 0.15,     # Morning coffee
                'office': 0.05
            },
            'blue book': {
                'office': 0.5,       # Study/work
                'bedroom': 0.25,     # Reading before bed
                'living_room': 0.15, # Coffee table
                'kitchen': 0.1       # Recipe book?
            },
            'yellow ball': {
                'living_room': 0.5,  # Play area
                'bedroom': 0.25,     # Kids room
                'kitchen': 0.15,     # Rolled under table
                'office': 0.1
            },
            'green bottle': {
                'kitchen': 0.5,      # Water bottle storage
                'office': 0.25,      # Desk hydration
                'bedroom': 0.15,     # Bedside
                'living_room': 0.1
            }
        }

        self.search_locations = {
            'kitchen': [(3.0, 4.5) , (3.0 ,2.0 )],
            'living_room': [(8.0,1.0), (5.0,2.0) , (5.0,5.0), (8.0,5.0)],
            'bedroom': [(-4.0,-2.0) , (-4.0, 0)],
            'office': [(7.5, -1.0) , (8.0,-4.0)]
        }
        pass