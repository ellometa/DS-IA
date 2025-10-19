# MRCA Explorer

Visualizer for exploring Most Recent Common Ancestor (MRCA) relationships in phylogenetic trees.

## Files

- `mrca_pygame_anytree.py` - Interactive version with GUI dialogs and pan/zoom
- `mrca.py` - Simple keyboard-controlled version

## Setup

```bash
source chalo/bin/activate
```

## Usage

### Interactive Version (mrca_pygame_anytree.py)

```bash
python mrca_pygame_anytree.py
```

- S: Open dialog to select two animals
- Arrow keys: Pan
- +/-: Zoom
- 0: Reset zoom
- C: Clear selections
- Q/Esc: Quit

### Simple Version (mrca.py)

```bash
python mrca.py
```

- Keys 1, 2, 3: Cycle through taxon pairs
- Q/Esc: Quit

## Tree Structure

```
Vertebrate
├── Mammal
│   ├── Primate (Human, Chimpanzee)
│   └── Carnivore (Dog, Cat)
├── Reptile
│   ├── Lizard (Gecko, Komodo Dragon)
│   └── Crocodilia (Crocodile, Alligator)
└── Bird (Eagle, Penguin)
```
