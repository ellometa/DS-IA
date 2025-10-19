# This program shows a family tree and finds the common ancestor of two animals
# Press S to pick two animals, then it shows their common ancestor
# Press ESC to quit, C to clear, 0 to reset zoom

import pygame
import pygame_gui
from anytree import Node

# This is our family tree data
family_tree = {
    "Vertebrate": ["Mammal", "Reptile", "Bird"],
    "Mammal": ["Primate", "Carnivore"],
    "Reptile": ["Lizard", "Crocodilia"],
    "Bird": ["Eagle", "Penguin"],
    "Primate": ["Human", "Chimpanzee"],
    "Carnivore": ["Dog", "Cat"],
    "Lizard": ["Gecko", "Komodo Dragon"],
    "Crocodilia": ["Crocodile", "Alligator"],
}
root_name = "Vertebrate"

# Screen settings
screen_width = 1280
screen_height = 800
top_space = 80

# Colors (red, green, blue values)
white = (255, 255, 255)
black = (0, 0, 0)
blue = (31, 119, 180)
orange = (255, 127, 14)
green = (44, 160, 44)
light_green = (198, 234, 185)
gray = (40, 40, 40)
light_gray = (245, 245, 245)

# Drawing settings
node_size = 14
space_x = 160
space_y = 120
move_amount = 40
zoom_in = 1.1
zoom_out = 0.9
min_zoom = 0.3
max_zoom = 3.0


# Make a list of who is the parent of each animal
def make_parent_list(tree, root):
    parent_list = {}
    parent_list[root] = None  # The root has no parent
    
    # We need to check all animals in the tree
    animals_to_check = [root]
    
    while len(animals_to_check) > 0:
        current_animal = animals_to_check.pop(0)
        
        # Get all children of this animal
        if current_animal in tree:
            children = tree[current_animal]
            for child in children:
                parent_list[child] = current_animal
                animals_to_check.append(child)
    
    return parent_list

# Get the path from an animal back to the root
def get_path_to_root(animal_name, parent_list):
    path = []
    current = animal_name
    
    # Keep going up the family tree until we reach the root
    while current is not None:
        path.append(current)
        current = parent_list.get(current)
    
    # Reverse the path so it goes from root to animal
    path.reverse()
    return path

# Find the most recent common ancestor of two animals
def find_common_ancestor(animal_a, animal_b, parent_list):
    if not animal_a or not animal_b:
        return None
    
    # Get the path from animal A to root
    path_a = get_path_to_root(animal_a, parent_list)
    
    # Start from animal B and go up the tree
    current = animal_b
    while current is not None:
        # If this ancestor is also in animal A's path, it's the common ancestor
        if current in path_a:
            return current
        current = parent_list.get(current)
    
    return None


# Figure out where to draw each animal on the screen
def calculate_positions(tree, root, x_space, y_space):
    positions = {}
    levels = {}  # Animals at each level of the tree
    
    # Start with the root at level 0
    animals_to_check = [(root, 0)]
    
    while len(animals_to_check) > 0:
        animal, level = animals_to_check.pop(0)
        
        # Add this animal to its level
        if level not in levels:
            levels[level] = []
        levels[level].append(animal)
        
        # Add children to the next level
        if animal in tree:
            for child in tree[animal]:
                animals_to_check.append((child, level + 1))
    
    # Now position each animal
    for level, animals in levels.items():
        num_animals = len(animals)
        
        for i, animal in enumerate(animals):
            # Center the animals horizontally
            offset = i - (num_animals - 1) / 2.0
            x = offset * x_space
            y = level * y_space
            positions[animal] = (x, y)
    
    return positions

# Convert tree coordinates to screen coordinates
def tree_to_screen(x, y, zoom, pan_x, pan_y, center_x, top_space):
    screen_x = center_x + zoom * x + pan_x
    screen_y = top_space + zoom * y + pan_y
    return screen_x, screen_y

# Convert all animal positions to screen positions
def all_positions_to_screen(positions, zoom, pan_x, pan_y, center_x, top_space):
    screen_positions = {}
    for animal, (x, y) in positions.items():
        screen_positions[animal] = tree_to_screen(x, y, zoom, pan_x, pan_y, center_x, top_space)
    return screen_positions


# Make a dialog box for picking two animals
def make_dialog_box(ui_manager, window_width, window_height):
    # Make the dialog box in the center of the screen
    dialog_x = window_width // 2 - 200
    dialog_y = window_height // 2 - 150
    dialog_width = 400
    dialog_height = 300
    
    dialog_box = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    
    # Create the dialog window
    dialog = pygame_gui.windows.UIConfirmationDialog(
        rect=dialog_box,
        manager=ui_manager,
        window_title="Pick Two Animals",
        action_long_desc="Type the names of two animals to find their common ancestor:",
        action_short_name="OK"
    )
    
    # Make text boxes for typing animal names
    text_box_a = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(50, 100, 300, 30),
        manager=ui_manager,
        container=dialog,
        placeholder_text="First Animal"
    )
    
    text_box_b = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect(50, 150, 300, 30),
        manager=ui_manager,
        container=dialog,
        placeholder_text="Second Animal"
    )
    
    return dialog, text_box_a, text_box_b

# Get all the animal names from our tree
def get_all_animal_names(tree, root):
    all_animals = [root]  # Start with the root
    animals_to_check = [root]
    
    while len(animals_to_check) > 0:
        current = animals_to_check.pop(0)
        if current in tree:
            for child in tree[current]:
                all_animals.append(child)
                animals_to_check.append(child)
    
    return all_animals


# Draw a legend to show what the colors mean
def draw_legend(screen, normal_font, title_font):
    # Legend box settings
    box_padding = 12
    circle_size = 8
    line_spacing = 24
    
    # What each color means
    legend_items = [
        ("Animal A's family", blue, white),
        ("Animal B's family", orange, white),
        ("Common ancestor", green, light_green),
        ("Regular tree", black, white),
    ]
    
    # Calculate how big the legend box should be
    title_width = title_font.size("Legend")[0]
    max_text_width = title_width
    for label, _, _ in legend_items:
        text_width = normal_font.size(label)[0]
        if text_width > max_text_width:
            max_text_width = text_width
    
    box_width = max_text_width + 2 * box_padding + circle_size * 2
    box_height = box_padding * 2 + line_spacing * (len(legend_items) + 1)
    
    # Draw the legend box
    legend_rect = pygame.Rect(0, 0, box_width, box_height)
    legend_rect.topright = (screen_width - 20, 20)
    
    pygame.draw.rect(screen, light_gray, legend_rect, border_radius=10)
    pygame.draw.rect(screen, black, legend_rect, width=1, border_radius=10)
    
    # Draw the title
    title_text = title_font.render("Legend", True, gray)
    screen.blit(title_text, (legend_rect.left + box_padding, legend_rect.top + box_padding))
    
    # Draw each legend item
    y_position = legend_rect.top + box_padding + line_spacing
    for label, circle_color, fill_color in legend_items:
        # Draw the colored circle
        circle_x = legend_rect.left + box_padding + circle_size
        circle_y = y_position + circle_size // 2
        pygame.draw.circle(screen, fill_color, (circle_x, circle_y), circle_size)
        pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_size, width=2)
        
        # Draw the text
        text_surface = normal_font.render(label, True, gray)
        screen.blit(text_surface, (circle_x + circle_size + 8, y_position))
        
        y_position += line_spacing


# Draw everything on the screen
def draw_everything(screen, tree, screen_positions, selections, parent_map, fonts):
    # Clear the screen with white
    screen.fill(white)
    normal_font, title_font = fonts

    animal_a, animal_b = selections
    
    # Find the common ancestor
    common_ancestor = find_common_ancestor(animal_a, animal_b, parent_map)
    
    # Get the family paths for both animals
    path_a = get_path_to_root(animal_a, parent_map) if animal_a else []
    path_b = get_path_to_root(animal_b, parent_map) if animal_b else []
    
    # Make sets of animals in each family path
    family_a = set(path_a)
    family_b = set(path_b)

    # Draw all the tree lines first
    for parent, children in tree.items():
        parent_x, parent_y = screen_positions[parent]
        for child in children:
            child_x, child_y = screen_positions[child]
            pygame.draw.line(screen, black, (parent_x, parent_y), (child_x, child_y), width=2)

    # Draw special colored lines for the selected animals' families
    for i in range(len(path_a) - 1):
        parent = path_a[i]
        child = path_a[i + 1]
        if parent in screen_positions and child in screen_positions:
            parent_x, parent_y = screen_positions[parent]
            child_x, child_y = screen_positions[child]
            pygame.draw.line(screen, blue, (parent_x, parent_y), (child_x, child_y), width=4)
    
    for i in range(len(path_b) - 1):
        parent = path_b[i]
        child = path_b[i + 1]
        if parent in screen_positions and child in screen_positions:
            parent_x, parent_y = screen_positions[parent]
            child_x, child_y = screen_positions[child]
            pygame.draw.line(screen, orange, (parent_x, parent_y), (child_x, child_y), width=4)

    # Draw all the animal circles
    for animal, (x, y) in screen_positions.items():
        if animal == common_ancestor:
            # Draw the common ancestor with special colors
            pygame.draw.circle(screen, light_green, (int(x), int(y)), node_size)
            pygame.draw.circle(screen, green, (int(x), int(y)), node_size, width=4)
        else:
            # Choose color based on which family this animal belongs to
            if animal in family_a and animal in family_b:
                # Animal is in both families - mix the colors
                mixed_color = (143, 123, 97)  # Mixed blue and orange
                pygame.draw.circle(screen, mixed_color, (int(x), int(y)), node_size)
            elif animal in family_b:
                # Animal is in family B
                pygame.draw.circle(screen, orange, (int(x), int(y)), node_size)
            elif animal in family_a:
                # Animal is in family A
                pygame.draw.circle(screen, blue, (int(x), int(y)), node_size)
            else:
                # Regular animal
                pygame.draw.circle(screen, white, (int(x), int(y)), node_size)
            
            # Draw the outline
            pygame.draw.circle(screen, black, (int(x), int(y)), node_size, width=2)

    # Draw animal names above each circle
    for animal, (x, y) in screen_positions.items():
        name_text = normal_font.render(animal, True, black)
        text_rect = name_text.get_rect(center=(int(x), int(y) - node_size - 12))
        screen.blit(name_text, text_rect)

    # Draw the status text at the top
    if animal_a:
        display_a = animal_a
    else:
        display_a = "—"
    
    if animal_b:
        display_b = animal_b
    else:
        display_b = "—"
    
    if common_ancestor:
        ancestor_text = common_ancestor
    else:
        ancestor_text = "—"
    
    status_text = f"Animal A = {display_a}, Animal B = {display_b}   |   Common Ancestor = {ancestor_text}"
    status_surface = title_font.render(status_text, True, black)
    screen.blit(status_surface, (20, 20))

    # Draw the legend
    draw_legend(screen, normal_font, title_font)


# Make sure a value stays within a range
def keep_in_range(value, min_val, max_val):
    if value < min_val:
        return min_val
    elif value > max_val:
        return max_val
    else:
        return value

# This is the main function that runs the program
def main():
    # Start pygame
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Animal Family Tree")
    clock = pygame.time.Clock()
    
    # Set up fonts
    normal_font = pygame.font.SysFont(None, 22)
    title_font = pygame.font.SysFont(None, 28, bold=True)
    
    # Set up the user interface manager
    ui_manager = pygame_gui.UIManager((screen_width, screen_height))

    # Set up our data
    parent_list = make_parent_list(family_tree, root_name)
    animal_positions = calculate_positions(family_tree, root_name, space_x, space_y)
    all_animals = get_all_animal_names(family_tree, root_name)

    # Set up camera/view settings
    zoom_level = 1.0
    camera_x = 0.0
    camera_y = 0.0
    selected_animals = [None, None]  # Animal A and Animal B
    center_x = screen_width // 2

    # Set up dialog variables
    running = True
    dialog_box = None
    text_box_a = None
    text_box_b = None

    # Main game loop
    while running:
        # Calculate how much time has passed
        time_delta = clock.tick(60) / 1000.0
        
        # Convert tree positions to screen positions
        screen_positions = all_positions_to_screen(
            animal_positions, zoom_level, camera_x, camera_y, center_x, top_space
        )

        # Handle events (keyboard, mouse, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Quit the program
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                # Reset zoom and camera position
                elif event.key in (pygame.K_0, pygame.K_KP0):
                    zoom_level = 1.0
                    camera_x = 0.0
                    camera_y = 0.0
                # Zoom out
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    zoom_level = keep_in_range(zoom_level * zoom_out, min_zoom, max_zoom)
                # Zoom in
                elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    zoom_level = keep_in_range(zoom_level * zoom_in, min_zoom, max_zoom)
                # Move camera left
                elif event.key == pygame.K_LEFT:
                    camera_x -= move_amount
                # Move camera right
                elif event.key == pygame.K_RIGHT:
                    camera_x += move_amount
                # Move camera up
                elif event.key == pygame.K_UP:
                    camera_y -= move_amount
                # Move camera down
                elif event.key == pygame.K_DOWN:
                    camera_y += move_amount
                # Clear selections
                elif event.key == pygame.K_c:
                    selected_animals = [None, None]
                # Recalculate positions
                elif event.key == pygame.K_r:
                    animal_positions = calculate_positions(family_tree, root_name, space_x, space_y)
                # Open selection dialog
                elif event.key == pygame.K_s:
                    if dialog_box is None:
                        dialog_box, text_box_a, text_box_b = make_dialog_box(
                            ui_manager, screen_width, screen_height
                        )
            
            # Handle UI events
            ui_manager.process_events(event)
            
            # Handle when user clicks OK in dialog
            if (event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED and 
                event.ui_object_id == '#confirmation_dialog'):
                
                if text_box_a and text_box_b:
                    animal_a_name = text_box_a.get_text().strip()
                    animal_b_name = text_box_b.get_text().strip()
                    
                    # Check if the animal names are valid
                    if animal_a_name in all_animals and animal_b_name in all_animals:
                        selected_animals = [animal_a_name, animal_b_name]
                    elif animal_a_name not in all_animals and animal_b_name not in all_animals:
                        print(f"Neither '{animal_a_name}' nor '{animal_b_name}' are valid animal names")
                    elif animal_a_name not in all_animals:
                        print(f"'{animal_a_name}' is not a valid animal name")
                    else:
                        print(f"'{animal_b_name}' is not a valid animal name")
                
                # Close the dialog
                dialog_box = None
                text_box_a = None
                text_box_b = None
            
            # Handle when user closes the dialog window
            elif (event.type == pygame_gui.UI_WINDOW_CLOSE and 
                  dialog_box and 
                  event.ui_element == dialog_box):
                dialog_box = None
                text_box_a = None
                text_box_b = None

        # Update the UI
        ui_manager.update(time_delta)
        
        # Draw everything
        draw_everything(
            screen,
            family_tree,
            screen_positions,
            selected_animals,
            parent_list,
            (normal_font, title_font),
        )
        
        # Draw the UI elements
        ui_manager.draw_ui(screen)
        
        # Update the display
        pygame.display.flip()

    # Quit pygame when done
    pygame.quit()


if __name__ == "__main__":
    main()
