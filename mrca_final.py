import pygame as pgame
import pygame_gui as pgui
from anytree import Node
import anytree
from typing import TypeAlias

def build_tree():
    """Build the family tree using anytree Node objects."""
    # Create all nodes
    vertebrate = Node("Vertebrate")
    mammal = Node("Mammal", parent=vertebrate)
    reptile = Node("Reptile", parent=vertebrate)
    bird = Node("Bird", parent=vertebrate)
    
    primate = Node("Primate", parent=mammal)
    carnivore = Node("Carnivore", parent=mammal)
    
    lizard = Node("Lizard", parent=reptile)
    crocodilia = Node("Crocodilia", parent=reptile)
    
    eagle = Node("Eagle", parent=bird)
    penguin = Node("Penguin", parent=bird)
    
    human = Node("Human", parent=primate)
    chimpanzee = Node("Chimpanzee", parent=primate)
    
    dog = Node("Dog", parent=carnivore)
    cat = Node("Cat", parent=carnivore)
    
    gecko = Node("Gecko", parent=lizard)
    komodo_dragon = Node("Komodo Dragon", parent=lizard)
    
    crocodile = Node("Crocodile", parent=crocodilia)
    alligator = Node("Alligator", parent=crocodilia)
    
    return vertebrate

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


def nodesearch_root_key(root_n, name):
    for node in root_n.descendants:
        if node.name == name:
            return node
    if root_n.name == name:
        return root_n
    return None

def get_path_to_root(root_n, animal_name):
    nim = nodesearch_root_key(root_n, animal_name)
    if nim is None:
        return []
    return [ancestor.name for ancestor in nim.path]

def _lca_align_depth(n1, n2):
    """Bring both nodes to the same depth, then climb together until they meet."""
    d1, d2 = n1.depth, n2.depth

    # Raise deeper node
    while d1 > d2:
        n1 = n1.parent
        d1 -= 1
    while d2 > d1:
        n2 = n2.parent
        d2 -= 1

    # Climb together
    while n1 is not n2:
        n1 = n1.parent
        n2 = n2.parent
        if n1 is None or n2 is None:
            return None
    return n1

def find_common_ancestor(root_n, animal_a, animal_b):
    if not animal_a or not animal_b:
        return None
    
    nim_a = nodesearch_root_key(root_n, animal_a)
    nim_b = nodesearch_root_key(root_n, animal_b)
    if nim_a is None or nim_b is None:
        return None

    ca = _lca_align_depth(nim_a, nim_b)
    
    if ca:
        return ca.name
    else: 
        return None




def calculate_positions(root_n, x_space, y_space):
    """Calculate positions for all nodes in the tree."""
    positions = {}
    lvls = {}
    
    for node in anytree.LevelOrderIter(root_n):
        lvl = node.depth
        if lvl not in lvls:
            lvls[lvl] = []
        lvls[lvl].append(node.name)
    
    for lvl, animals in lvls.items():
        num_animals = len(animals)
        
        for i, animal in enumerate(animals):
            offset = i - (num_animals - 1) / 2.0
            x = offset * x_space
            y = lvl * y_space
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


def make_dialog_box(ui_man, wnd_width, wnd_height):
    dia_x = wnd_width // 2 - 199
    dia_y = wnd_height // 2 - 149
    dia_wid = 400
    dia_hght = 300

    dialog_box = pgame.Rect(dia_x, dia_y, dia_wid, dia_hght)

    dialog = pgui.windows.UIConfirmationDialog(
        rect=dialog_box,
        manager=ui_man,  # <-- was 'man', must be 'manager'
        window_title="Pick Two Animals",
        action_long_desc="Type the names of two animals to find their common ancestor:",
        action_short_name="OK"
    )

    text_box_a = pgui.elements.UITextEntryLine(
        relative_rect=pgame.Rect(50, 100, 300, 30),  # <-- was 'rel_rect', must be 'relative_rect'
        manager=ui_man,                               # <-- was 'man', must be 'manager'
        container=dialog,
        placeholder_text="First Animal"
    )

    text_box_b = pgui.elements.UITextEntryLine(
        relative_rect=pgame.Rect(50, 150, 300, 30),  # <-- was 'rel_rect', must be 'relative_rect'
        manager=ui_man,                               # <-- was 'man', must be 'manager'
        container=dialog,
        placeholder_text="Second Animal"
    )

    return dialog, text_box_a, text_box_b


def get_all_animal_names(root_n):
    return [node.name for node in anytree.LevelOrderIter(root_n)]


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
    max_wid = title_wid
    for label, _, _ in legend_items:
        text_wid = normal_font.size(label)[0]

        if text_wid > max_wid:
            max_wid = text_wid
    
    box_width = max_wid + 2 * box_padding + circle_size * 2
    box_height = box_padding * 2 + line_spacing * (len(legend_items) + 1)
    
    legend_rect = pgame.Rect(0, 0, box_width, box_height)
    legend_rect.topright = (screen_width - 20, 20)
    
    pgame.draw.rect(screen, light_gray, legend_rect, border_radius=10)
    pgame.draw.rect(screen, black, legend_rect, width=1, border_radius=10)
    
    legend_title_surface = title_font.render("Legend", True, gray)
    title_x = legend_rect.x + box_padding
    title_y = legend_rect.y + box_padding
    screen.blit(legend_title_surface, (title_x, title_y))
    
    y_position = legend_rect.top + box_padding + line_spacing
    for label, circle_color, fill_color in legend_items:
        circ_x = legend_rect.left + box_padding + circle_size
        circ_y = y_position + circle_size // 2
        pgame.draw.circle(screen, fill_color, (circ_x, circ_y), circle_size)
        pgame.draw.circle(screen, circle_color, (circ_x, circ_y), circle_size, width=2)
        
        text_surface = normal_font.render(label, True, gray)
        screen.blit(text_surface, (circ_x + circle_size + 8, y_position))
        
        y_position += line_spacing


def draw_everything(screen, root_n, screen_positions, selections, fonts):
    screen.fill(white)
    normal_font, title_font = fonts

    animal_a, animal_b = selections
    
    common_ancestor = find_common_ancestor(root_n, animal_a, animal_b)
    
    trail_a = get_path_to_root(root_n, animal_a) if animal_a else []
    trail_b = get_path_to_root(root_n, animal_b) if animal_b else []
    
    family_a = set(trail_a)
    family_b = set(trail_b)

    # Draw tree edges
    for node in anytree.LevelOrderIter(root_n):
        par_name = node.name
        if par_name in screen_positions:
            for child in node.children:
                chld_name = child.name
                if chld_name in screen_positions:
                    par_x, par_y = screen_positions[par_name]
                    chld_x, chld_y = screen_positions[chld_name]
                    pgame.draw.line(screen, black, (par_x, par_y), (chld_x, chld_y), width=2)

    for idx in range(len(trail_a) - 1):
        ancestor = trail_a[idx]
        descendant = trail_a[idx + 1]
        if ancestor in screen_positions and descendant in screen_positions:
            sbegin_x, sbegin_y = screen_positions[ancestor]
            send_x, send_y = screen_positions[descendant]
            pgame.draw.line(screen, blue, (sbegin_x, sbegin_y), (send_x, send_y), width=4)
    

    for i in range(len(trail_b) - 1):
        parent = trail_b[i]
        child = trail_b[i + 1]
        if parent in screen_positions and child in screen_positions:
            par_x, par_y = screen_positions[parent]
            chld_x, chld_y = screen_positions[child]
            pgame.draw.line(screen, orange, (par_x, par_y), (chld_x, chld_y), width=4)

    for animal, (x, y) in screen_positions.items():
        nsop = (int(x), int(y))
        if animal == common_ancestor:
            pgame.draw.circle(screen, light_green, nsop, node_size)
            pgame.draw.circle(screen, green, nsop, node_size, width=4)
        else:
            if animal in family_a and animal in family_b:
                pgame.draw.circle(screen, (143, 123, 97), nsop, node_size)
            elif animal in family_b:
                pgame.draw.circle(screen, orange, nsop, node_size)
            elif animal in family_a:
                pgame.draw.circle(screen, blue, nsop, node_size)
            else:
                pgame.draw.circle(screen, white, nsop, node_size)
            pgame.draw.circle(screen, black, nsop, node_size, width=2)

    for animal, pos in screen_positions.items():
        x, y = pos
        label_surface = normal_font.render(animal, True, black)
        label_rect = label_surface.get_rect(center=(int(x), int(y) - node_size - 12))
        screen.blit(label_surface, label_rect)

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
    stat_srf = title_font.render(status_text, True, black)
    screen.blit(stat_srf, (20, 20))

    draw_legend(screen, normal_font, title_font)


def keep_in_range(val, mn_val, mx_val):
    if val < mn_val:
        return mn_val
    elif val > mx_val:
        return mx_val
    else:
        return val

def main():
    pgame.init()
    screen = pgame.display.set_mode((screen_width, screen_height))
    pgame.display.set_caption("Animal Family Tree")
    clk = pgame.time.Clock()
    
    normal_font = pgame.font.SysFont(None, 22)
    title_font = pgame.font.SysFont(None, 28, bold=True)
    
    ui_man = pgui.UIManager((screen_width, screen_height))

    root_n = build_tree()
    animal_positions = calculate_positions(root_n, space_x, space_y)
    all_taxa = get_all_animal_names(root_n)

    zoom_lvl = 1.0
    cam_x = 0.0
    camera_y = 0.0
    selected_animals = [None, None]
    center_x = screen_width // 2

    looping = True
    dialog_box = None
    text_box_a = None
    text_box_b = None

    while looping:
        time_delta = clk.tick(60) / 1000.0
        
        screen_positions = all_positions_to_screen(
            animal_positions, zoom_lvl, cam_x, camera_y, center_x, top_space
        )

        for event in pgame.event.get():
            evnt = getattr(event, "key", None)

            if event.type == pgame.QUIT:
                looping = False
            elif event.type == pgame.KEYDOWN:
                if evnt in (pgame.K_ESCAPE, pgame.K_q):
                    looping = False
                elif evnt in (pgame.K_0, pgame.K_KP0):
                    zoom_lvl = 1.0
                    cam_x = 0.0
                    camera_y = 0.0
                elif evnt in (pgame.K_MINUS, pgame.K_KP_MINUS):
                    zoom_lvl = keep_in_range(zoom_lvl * zoom_out, min_zoom, max_zoom)
                elif evnt in (pgame.K_EQUALS, pgame.K_PLUS, pgame.K_KP_PLUS):
                    zoom_lvl = keep_in_range(zoom_lvl * zoom_in, min_zoom, max_zoom)
                elif evnt == pgame.K_LEFT:
                    cam_x -= move_amount
                elif evnt == pgame.K_RIGHT:
                    cam_x += move_amount
                elif evnt == pgame.K_UP:
                    camera_y -= move_amount
                elif evnt == pgame.K_DOWN:
                    camera_y += move_amount
                elif evnt == pgame.K_c:
                    selected_animals = [None, None]
                elif evnt == pgame.K_r:
                    animal_positions = calculate_positions(root_n, space_x, space_y)
                elif evnt == pgame.K_s:
                    if dialog_box is None:
                        dialog_box, text_box_a, text_box_b = make_dialog_box(
                            ui_man, screen_width, screen_height
                        )
            
            ui_man.process_events(event)
            
            if (event.type == pgui.UI_CONFIRMATION_DIALOG_CONFIRMED and 
                event.ui_object_id == '#confirmation_dialog'):
                
                if text_box_a and text_box_b:
                    taxa_a_name = text_box_a.get_text().strip()
                    taxa_b_name = text_box_b.get_text().strip()
                    
                    if taxa_a_name in all_taxa and taxa_b_name in all_taxa:
                        selected_animals = [taxa_a_name, taxa_b_name]
                    elif taxa_a_name not in all_taxa and taxa_b_name not in all_taxa:
                        print(f"Neither '{taxa_a_name}' nor '{taxa_b_name}' are valid animal names")
                    elif taxa_a_name not in all_taxa:
                        print(f"'{taxa_a_name}' is not a valid animal name")
                    else:
                        print(f"'{taxa_b_name}' is not a valid animal name")
                
                dialog_box = None
                text_box_a = None
                text_box_b = None
            
            elif (event.type == pgui.UI_WINDOW_CLOSE and 
                  dialog_box and 
                  event.ui_element == dialog_box):
                dialog_box = None
                text_box_a = None
                text_box_b = None

        ui_man.update(time_delta)
        
        draw_everything(
            screen,
            root_n,
            screen_positions,
            selected_animals,
            (normal_font, title_font),
        )
        
        ui_man.draw_ui(screen)
        
        pgame.display.flip()

    pgame.quit()


if __name__ == "__main__":
    main()
