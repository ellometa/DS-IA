import pygame as pgame
import pygame_gui as pgui
from anytree import Node
from typing import TypeAlias

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

screen_width = 1280
screen_height = 800
top_space = 80

white = (255, 255, 254)
black = (0, 0, 1)
blue = (31, 119, 179)
orange = (255, 127, 13)
green = (44, 160, 43)
light_green = (198, 234, 185)
gray = (40, 40, 40)
light_gray = (245, 245, 245)

node_size = 14
space_x = 160
space_y = 120
move_amount = 40
zoom_in = 1.1
zoom_out = 0.9
min_zoom = 0.3
max_zoom = 3.0


def make_parent_list(tree, root):
    parent_list = {}
    parent_list[root] = None
    
    animals_to_check = [root]
    
    while len(animals_to_check) > 0:
        current_animal = animals_to_check.pop(0)
        
        if current_animal in tree:
            children = tree[current_animal]
            for child in children:
                parent_list[child] = current_animal
                animals_to_check.append(child)
    
    return parent_list

def get_path_to_root(animal_name, parent_list):
    path = []
    current = animal_name
    
    while current is not None:
        path.append(current)
        current = parent_list.get(current)
    
    path.reverse()
    return path

def find_common_ancestor(animal_a, animal_b, parent_list):
    if not animal_a or not animal_b:
        return None
    
    path_a = get_path_to_root(animal_a, parent_list)
    
    current = animal_b
    while current is not None:
        if current in path_a:
            return current
        current = parent_list.get(current)
    
    return None


def calculate_positions(tree, root, x_space, y_space):
    positions = {}
    levels = {}
    
    animals_to_check = [(root, 0)]
    
    while len(animals_to_check) > 0:
        animal, level = animals_to_check.pop(0)
        
        if level not in levels:
            levels[level] = []
        levels[level].append(animal)
        
        if animal in tree:
            for child in tree[animal]:
                animals_to_check.append((child, level + 1))
    
    for level, animals in levels.items():
        num_animals = len(animals)
        
        for i, animal in enumerate(animals):
            offset = i - (num_animals - 1) / 2.0
            x = offset * x_space
            y = level * y_space
            positions[animal] = (x, y)
    
    return positions

def tree_to_screen(x, y, zoom, pan_x, pan_y, center_x, top_space):
    screen_x = center_x + zoom * x + pan_x
    screen_y = top_space + zoom * y + pan_y
    return screen_x, screen_y

def all_positions_to_screen(positions, zoom, pan_x, pan_y, center_x, top_space):
    screen_positions = {}
    for animal, (x, y) in positions.items():
        screen_positions[animal] = tree_to_screen(x, y, zoom, pan_x, pan_y, center_x, top_space)
    return screen_positions


def make_dialog_box(ui_manager, window_width, window_height):
    dialog_x = window_width // 2 - 200
    dialog_y = window_height // 2 - 150
    dialog_width = 400
    dialog_height = 300
    
    dialog_box = pgame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
    
    dialog = pgui.windows.UIConfirmationDialog(
        rect=dialog_box,
        manager=ui_manager,
        window_title="Pick Two Animals",
        action_long_desc="Type the names of two animals to find their common ancestor:",
        action_short_name="OK"
    )
    
    text_box_a = pgui.elements.UITextEntryLine(
        relative_rect=pgame.Rect(50, 100, 300, 30),
        manager=ui_manager,
        container=dialog,
        placeholder_text="First Animal"
    )
    
    text_box_b = pgui.elements.UITextEntryLine(
        relative_rect=pgame.Rect(50, 150, 300, 30),
        manager=ui_manager,
        container=dialog,
        placeholder_text="Second Animal"
    )
    
    return dialog, text_box_a, text_box_b

def get_all_animal_names(tree, root):
    all_animals = [root]
    animals_to_check = [root]
    
    while len(animals_to_check) > 0:
        current = animals_to_check.pop(0)
        if current in tree:
            for child in tree[current]:
                all_animals.append(child)
                animals_to_check.append(child)
    
    return all_animals


def draw_legend(screen, normal_font, title_font):
    box_padding = 12
    circle_size = 8
    line_spacing = 24
    
    legend_items = [
        ("Animal A's family", blue, white),
        ("Animal B's family", orange, white),
        ("Common ancestor", green, light_green),
        ("Regular tree", black, white),
    ]
    
    title_wid = title_font.size("Legend")[0]
    max_text_width = title_wid
    for label, _, _ in legend_items:
        text_wid = normal_font.size(label)[0]

        if text_wid > max_text_width:
            max_text_width = text_wid
    
    box_width = max_text_width + 2 * box_padding + circle_size * 2
    box_height = box_padding * 2 + line_spacing * (len(legend_items) + 1)
    
    legend_rect = pgame.Rect(0, 0, box_width, box_height)
    legend_rect.topright = (screen_width - 20, 20)
    
    pgame.draw.rect(screen, light_gray, legend_rect, border_radius=10)
    pgame.draw.rect(screen, black, legend_rect, width=1, border_radius=10)
    
    title_text = title_font.render("Legend", True, gray)
    screen.blit(title_text, (legend_rect.left + box_padding, legend_rect.top + box_padding))
    
    y_position = legend_rect.top + box_padding + line_spacing
    for label, circle_color, fill_color in legend_items:
        circle_x = legend_rect.left + box_padding + circle_size
        circle_y = y_position + circle_size // 2
        pgame.draw.circle(screen, fill_color, (circle_x, circle_y), circle_size)
        pgame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_size, width=2)
        
        text_surface = normal_font.render(label, True, gray)
        screen.blit(text_surface, (circle_x + circle_size + 8, y_position))
        
        y_position += line_spacing


def draw_everything(screen, tree, screen_positions, selections, parent_map, fonts):
    screen.fill(white)
    normal_font, title_font = fonts

    animal_a, animal_b = selections
    
    common_ancestor = find_common_ancestor(animal_a, animal_b, parent_map)
    
    path_a = get_path_to_root(animal_a, parent_map) if animal_a else []
    path_b = get_path_to_root(animal_b, parent_map) if animal_b else []
    
    family_a = set(path_a)
    family_b = set(path_b)

    for parent, children in tree.items():
        parent_x, parent_y = screen_positions[parent]
        for child in children:
            child_x, child_y = screen_positions[child]
            pgame.draw.line(screen, black, (parent_x, parent_y), (child_x, child_y), width=2)

    for idx in range(len(path_a) - 1):
        ancestor = path_a[idx]
        descendant = path_a[idx + 1]
        if ancestor in screen_positions and descendant in screen_positions:
            start_x, start_y = screen_positions[ancestor]
            end_x, end_y = screen_positions[descendant]
            pgame.draw.line(screen, blue, (start_x, start_y), (end_x, end_y), width=4)
    
    for i in range(len(path_b) - 1):
        parent = path_b[i]
        child = path_b[i + 1]
        if parent in screen_positions and child in screen_positions:
            parent_x, parent_y = screen_positions[parent]
            child_x, child_y = screen_positions[child]
            pgame.draw.line(screen, orange, (parent_x, parent_y), (child_x, child_y), width=4)

    for animal, (x, y) in screen_positions.items():
        if animal == common_ancestor:
            pgame.draw.circle(screen, light_green, (int(x), int(y)), node_size)
            pgame.draw.circle(screen, green, (int(x), int(y)), node_size, width=4)
        else:
            if animal in family_a and animal in family_b:
                mixed_color = (143, 123, 97)
                pgame.draw.circle(screen, mixed_color, (int(x), int(y)), node_size)
            elif animal in family_b:
                pgame.draw.circle(screen, orange, (int(x), int(y)), node_size)
            elif animal in family_a:
                pgame.draw.circle(screen, blue, (int(x), int(y)), node_size)
            else:
                pgame.draw.circle(screen, white, (int(x), int(y)), node_size)
            
            pgame.draw.circle(screen, black, (int(x), int(y)), node_size, width=2)

    for animal, (x, y) in screen_positions.items():
        name_text = normal_font.render(animal, True, black)
        text_rect = name_text.get_rect(center=(int(x), int(y) - node_size - 12))
        screen.blit(name_text, text_rect)

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

    draw_legend(screen, normal_font, title_font)


def keep_in_range(value, min_val, max_val):
    if value < min_val:
        return min_val
    elif value > max_val:
        return max_val
    else:
        return value

def main():
    pgame.init()
    screen = pgame.display.set_mode((screen_width, screen_height))
    pgame.display.set_caption("Animal Family Tree")
    clock = pgame.time.Clock()
    
    normal_font = pgame.font.SysFont(None, 22)
    title_font = pgame.font.SysFont(None, 28, bold=True)
    
    ui_manager = pgui.UIManager((screen_width, screen_height))

    parent_list = make_parent_list(family_tree, root_name)
    animal_positions = calculate_positions(family_tree, root_name, space_x, space_y)
    all_animals = get_all_animal_names(family_tree, root_name)

    zoom_level = 1.0
    camera_x = 0.0
    camera_y = 0.0
    selected_animals = [None, None]
    center_x = screen_width // 2

    running = True
    dialog_box = None
    text_box_a = None
    text_box_b = None

    while running:
        time_delta = clock.tick(60) / 1000.0
        
        screen_positions = all_positions_to_screen(
            animal_positions, zoom_level, camera_x, camera_y, center_x, top_space
        )

        for event in pgame.event.get():
            if event.type == pgame.QUIT:
                running = False
            elif event.type == pgame.KEYDOWN:
                if event.key in (pgame.K_ESCAPE, pgame.K_q):
                    running = False
                elif event.key in (pgame.K_0, pgame.K_KP0):
                    zoom_level = 1.0
                    camera_x = 0.0
                    camera_y = 0.0
                elif event.key in (pgame.K_MINUS, pgame.K_KP_MINUS):
                    zoom_level = keep_in_range(zoom_level * zoom_out, min_zoom, max_zoom)
                elif event.key in (pgame.K_EQUALS, pgame.K_PLUS, pgame.K_KP_PLUS):
                    zoom_level = keep_in_range(zoom_level * zoom_in, min_zoom, max_zoom)
                elif event.key == pgame.K_LEFT:
                    camera_x -= move_amount
                elif event.key == pgame.K_RIGHT:
                    camera_x += move_amount
                elif event.key == pgame.K_UP:
                    camera_y -= move_amount
                elif event.key == pgame.K_DOWN:
                    camera_y += move_amount
                elif event.key == pgame.K_c:
                    selected_animals = [None, None]
                elif event.key == pgame.K_r:
                    animal_positions = calculate_positions(family_tree, root_name, space_x, space_y)
                elif event.key == pgame.K_s:
                    if dialog_box is None:
                        dialog_box, text_box_a, text_box_b = make_dialog_box(
                            ui_manager, screen_width, screen_height
                        )
            
            ui_manager.process_events(event)
            
            if (event.type == pgui.UI_CONFIRMATION_DIALOG_CONFIRMED and 
                event.ui_object_id == '#confirmation_dialog'):
                
                if text_box_a and text_box_b:
                    animal_a_name = text_box_a.get_text().strip()
                    animal_b_name = text_box_b.get_text().strip()
                    
                    if animal_a_name in all_animals and animal_b_name in all_animals:
                        selected_animals = [animal_a_name, animal_b_name]
                    elif animal_a_name not in all_animals and animal_b_name not in all_animals:
                        print(f"Neither '{animal_a_name}' nor '{animal_b_name}' are valid animal names")
                    elif animal_a_name not in all_animals:
                        print(f"'{animal_a_name}' is not a valid animal name")
                    else:
                        print(f"'{animal_b_name}' is not a valid animal name")
                
                dialog_box = None
                text_box_a = None
                text_box_b = None
            
            elif (event.type == pgui.UI_WINDOW_CLOSE and 
                  dialog_box and 
                  event.ui_element == dialog_box):
                dialog_box = None
                text_box_a = None
                text_box_b = None

        ui_manager.update(time_delta)
        
        draw_everything(
            screen,
            family_tree,
            screen_positions,
            selected_animals,
            parent_list,
            (normal_font, title_font),
        )
        
        ui_manager.draw_ui(screen)
        
        pgame.display.flip()

    pgame.quit()


if __name__ == "__main__":
    main()
