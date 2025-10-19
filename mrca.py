# mrca_pygame_anytree.py
# Bare-bones MRCA visualizer with pygame (+ anytree for in-memory nodes)
# Keys:
#   1 -> (Human, Dog)
#   2 -> (Snake, Crocodile)
#   3 -> (Human, Snake)
#   Q / Esc -> Quit

import sys
import pygame
from collections import deque, defaultdict
from anytree import Node

# ------------------ DATA (edit freely) ------------------
TREE = {
    "Vertebrate": ["Mammal", "Reptile", "Bird"],
    "Mammal": ["Primate", "Carnivore"],
    "Reptile": ["Lizard", "Crocodile"],
    "Bird": ["Eagle", "Penguin"],
    "Primate": ["Human", "Chimpanzee"],
    "Carnivore": ["Dog", "Cat"],
    "Lizard": ["Gecko", "Komodo Dragon"],
    "Crocodile": ["Saltwater Crocodile", "Alligator"]
}
ROOT = "Vertebrate"


PAIRS = [
    ("Human", "Dog"),               
    ("Snake", "Crocodile"),         
    ("Human", "Snake"),             
    ("Cat", "Dog"),                 
    ("Human", "Chimpanzee"),        
    ("Gecko", "Komodo Dragon"),     
    ("Eagle", "Penguin"),           
    ("Human", "Penguin"),           
    ("Dog", "Crocodile"),           
    ("Cat", "Komodo Dragon")        
]


# ------------------ AUTHORITATIVE PARENT MAP (from TREE) ------------------
ALL_NODES = set(TREE.keys()) | {c for kids in TREE.values() for c in kids}

PARENT = {ROOT: None}
def _dfs_parent(v: str):
    for c in TREE.get(v, []):
        PARENT[c] = v
        _dfs_parent(c)
_dfs_parent(ROOT)

def lineage(name: str):
    """Return list from node up to ROOT (inclusive)."""
    path = []
    cur = name if name in ALL_NODES else None
    while cur is not None:
        path.append(cur)
        cur = PARENT.get(cur)
    return path

def mrca(a: str, b: str):
    """Most recent common ancestor via ancestor set + climb."""
    A = set(lineage(a))
    cur = b if b in ALL_NODES else None
    while cur is not None:
        if cur in A: return cur
        cur = PARENT.get(cur)
    return None

# ------------------ ANYTREE BUILD (optional, not used for layout) ------------------
nodes = {}
def get_node(name):
    n = nodes.get(name)
    if n is None:
        n = Node(name)
        nodes[name] = n
    return n

for p, kids in TREE.items():
    pnode = get_node(p)
    for c in kids:
        Node(c, parent=pnode)
root_node = nodes[ROOT]

# ------------------ LAYOUT: BFS LEVELS FROM TREE (centers each row) ------------------
def compute_positions_from_tree(root: str, x_spacing=200, y_spacing=130):
    """
    Return {node: (x,y)} with rows centered around x=0.
    Uses BFS levels from the TREE dict, so ALL_NODES get positions.
    """
    level = {root: 0}
    by_level = defaultdict(list)
    by_level[0].append(root)
    q = deque([root])
    while q:
        v = q.popleft()
        for c in TREE.get(v, []):
            if c not in level:
                level[c] = level[v] + 1
                by_level[level[c]].append(c)
                q.append(c)

    # (Safety) if any nodes weren’t reachable, drop them on row 0
    for n in ALL_NODES:
        if n not in level:
            level[n] = 0
            by_level[0].append(n)

    pos = {}
    for d in sorted(by_level.keys()):
        row = by_level[d]
        total_w = (len(row) - 1) * x_spacing
        start_x = -total_w / 2
        for i, n in enumerate(row):
            x = start_x + i * x_spacing
            y = d * y_spacing
            pos[n] = (x, y)
    return pos

POS = compute_positions_from_tree(ROOT)  # <-- positions for every node

# ------------------ PYGAME SETUP ------------------
pygame.init()
W, H = 1920, 1080
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("MRCA (pygame + anytree)")
FONT = pygame.font.SysFont(None, 22)
BIG  = pygame.font.SysFont(None, 28, bold=True)

WHITE = (255,255,255)
BLACK = (30,30,30)
BLUE  = (31,119,180)   # lineage A
ORNG  = (255,127,14)   # lineage B
GREEN = (44,160,44)    # MRCA

RADIUS = 14
TOP_MARGIN = 70

def to_screen(x, y):
    """Logical (x,y) with root centered at x=0 -> screen coords."""
    cx = W // 2
    return int(cx + x), int(TOP_MARGIN + y)

# ------------------ DRAW ------------------
def draw_tree(pair_idx: int):
    screen.fill(WHITE)

    a, b = PAIRS[pair_idx % len(PAIRS)]
    A_path = set(lineage(a))
    B_path = set(lineage(b))
    M = mrca(a, b)

    # Title
    title = BIG.render(f"MRCA({a}, {b}) = {M}", True, BLACK)
    screen.blit(title, (20, 18))

    # Legend
    legend = [
        (BLUE,  "A-lineage"),
        (ORNG,  "B-lineage"),
        (GREEN, "MRCA"),
        (BLACK, "Tree"),
    ]
    lx, ly = W - 190, 20
    for color, label in legend:
        pygame.draw.circle(screen, color, (lx, ly+8), 6)
        lab = FONT.render(label, True, BLACK)
        screen.blit(lab, (lx+14, ly))
        ly += 22

    # Edges: iterate the TREE dict (guarantees leaves are drawn)
    for p, kids in TREE.items():
        xp, yp = to_screen(*POS[p])
        for c in kids:
            xc, yc = to_screen(*POS[c])
            col, width = BLACK, 2
            if c in A_path and p in A_path:
                col, width = BLUE, 3
            if c in B_path and p in B_path:
                col, width = ORNG, 3
            pygame.draw.line(screen, col, (xp, yp), (xc, yc), width)

    # Nodes
    for name, (x, y) in POS.items():
        sx, sy = to_screen(x, y)
        outline = BLACK
        fill = WHITE
        width = 2
        if name in A_path:
            outline, width = BLUE, 3
        if name in B_path:
            outline, width = ORNG, 3
        if name == M:
            outline, fill, width = GREEN, (210, 245, 210), 4

        pygame.draw.circle(screen, outline, (sx, sy), RADIUS+1)
        pygame.draw.circle(screen, fill, (sx, sy), RADIUS)
        label = FONT.render(name, True, BLACK)
        screen.blit(label, (sx - label.get_width()//2, sy - RADIUS - 20))

    pygame.display.flip()

# ------------------ MAIN LOOP ------------------
def main():
    pair_idx = 0
    clock = pygame.time.Clock()
    draw_tree(pair_idx)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit(); sys.exit(0)
                if e.key == pygame.K_1: pair_idx = 0; draw_tree(pair_idx)
                if e.key == pygame.K_2: pair_idx = 1; draw_tree(pair_idx)
                if e.key == pygame.K_3: pair_idx = 2; draw_tree(pair_idx)

        clock.tick(60)

if __name__ == "__main__":
    main()
