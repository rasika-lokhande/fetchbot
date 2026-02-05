

loc_probs = {
    'red_cup': {
        'kitchen': 0.6,      # Cups belong in kitchen
        'living_room': 0.2,  # Sometimes left there
        'bedroom': 0.15,     # Morning coffee
        'office': 0.05
    },
    'blue_book': {
        'office': 0.5,       # Study/work
        'bedroom': 0.25,     # Reading before bed
        'living_room': 0.15, # Coffee table
        'kitchen': 0.1       # Recipe book?
    },
    'yellow_ball': {
        'living_room': 0.5,  # Play area
        'bedroom': 0.25,     # Kids room
        'kitchen': 0.15,     # Rolled under table
        'office': 0.1
    },
    'green_bottle': {
        'kitchen': 0.5,      # Water bottle storage
        'office': 0.25,      # Desk hydration
        'bedroom': 0.15,     # Bedside
        'living_room': 0.1
    }
}


# Dictionary to store coordinates of object to spawn. Replace later with a distribution
spawn_locations = {
     'kitchen': [(3.0,3.0)],
        'living_room': [(7.0,2.0)],
        'bedroom': [(-4.0, -1.0)],
        'office': [(7.0,-2.0)]

}

# Dictionary for locations to navigate to to start search
search_locations = {
     'kitchen': [(3.0, 4.5) , (3.0 ,2.0 )],
        'living_room': [(8.0,1.0), (5.0,2.0) , (5.0,5.0), (8.0,5.0)],
        'bedroom': [(-4.0,-2.0) , (-4.0, 0)],
        'office': [(7.5, -1.0) , (8.0,-4.0)]

}





# 1. Kitchen
#     Center: (3,3)
#     (3,4.5) , (3,2)

# 2. Living room (7,2)
#     (8,1), (5,2) , (5,5), (8,5)
# 3. Office (7,-2)
#     (7.5, -1) , (8,-4)



# 4. Bedroom (-4 , -1)
#     (-4,-2) , (-4, 0)
# 5. 
# 6.


