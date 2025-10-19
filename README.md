# MRCA Explorer 🧬

A bare-bones visualizer for exploring Most Recent Common Ancestor (MRCA) relationships in phylogenetic trees, built with pygame + anytree.

## Features

- **Interactive Tree Visualization**: Clean, hierarchical display of evolutionary relationships
- **MRCA Calculation**: Find the most recent common ancestor of any two taxa
- **Visual Highlighting**: Color-coded lineages and MRCA highlighting
- **Keyboard Controls**: Press 1, 2, 3 to cycle through predefined taxon pairs
- **Minimal Design**: Bare-bones pygame interface for fast, focused exploration

## Quick Start

### Method 1: Using the Launcher Script (Recommended)

```bash
# Make the script executable (if not already done)
chmod +x run_mrca.sh

# Run the application
./run_mrca.sh
```

### Method 2: Manual Setup

```bash
# Activate the virtual environment
source chalo/bin/activate

# Run the application
python mrca.py
```

## Prerequisites

- **Python 3.13+**
- **Virtual Environment**: The `chalo` virtual environment with required dependencies

### Installing Dependencies

```bash
# Activate virtual environment
source chalo/bin/activate

# Install required packages
pip install pygame anytree
```

## Usage

1. **Launch the application** using one of the methods above
2. **Use keyboard controls** to cycle through predefined taxon pairs:
   - **1**: Human vs Dog (same clade)
   - **2**: Snake vs Crocodile (same clade)
   - **3**: Human vs Snake (different clades)
3. **View the highlighted tree**:
   - Blue lines: Lineage of first taxon
   - Orange lines: Lineage of second taxon
   - Green node: Most Recent Common Ancestor
4. **Press Q or Esc** to quit

## Example Tree

The default tree includes:

```
Vertebrate
├── Mammal
│   ├── Human
│   └── Dog
└── Reptile
    ├── Snake
    └── Crocodile
```

## Customization

You can modify the tree and taxon pairs by editing `mrca.py`:

```python
# Edit the tree structure
TREE = {
    "YourRoot": ["Child1", "Child2"],
    "Child1": ["Grandchild1", "Grandchild2"],
    # ... add more relationships
}

# Edit predefined taxon pairs
PAIRS = [
    ("TaxonA", "TaxonB"),
    ("TaxonC", "TaxonD"),
    ("TaxonE", "TaxonF"),
]
```

## Troubleshooting

### App won't start

- Ensure virtual environment is activated: `source chalo/bin/activate`
- Check pygame support: `python -c "import pygame"`
- Install dependencies: `pip install pygame anytree`

### Dependencies missing

- Activate venv and install: `pip install pygame anytree`

### Display issues

- Make sure you have a display server running (X11/Wayland on Linux, or normal macOS display)
- Check if pygame can create a window: `python -c "import pygame; pygame.init(); pygame.display.set_mode((100,100))"`

## File Structure

```
DSia/
├── mrca.py              # Main application
├── run_mrca.sh          # Launcher script
├── README.md            # This file
└── chalo/               # Virtual environment
    ├── bin/
    ├── lib/
    └── ...
```

## Technical Details

- **Framework**: pygame + anytree
- **Algorithm**: Tree traversal with ancestor set intersection
- **Layout**: Level-order positioning with automatic spacing
- **Colors**: Blue (#1f77b4), Orange (#ff7f0e), Green (#2ca02c)
- **Controls**: Keyboard-driven (1, 2, 3, Q, Esc)

Enjoy exploring evolutionary relationships! 🦕🐒🐍
