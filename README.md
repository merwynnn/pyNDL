
# PyNDL : A versatile and modular visual programming language for Python applications

PyNDL is a dynamic node-based visual programming language created using Pygame.



## Screenshots

![App Screenshot](pyNDL/Screenshots/Screenshot1.png)
![App Screenshot](pyNDL/Screenshots/Screenshot2.png)
![App Screenshot](pyNDL/Screenshots/Screenshot3.png)


## Installation

Install pyNDL using pip

```python
  pip install python-NDL
```
    
## Usage/Examples

```python
from pyNDL import pyNDL
import pygame

pygame.init()
win = pygame.display.set_mode((0, 0))

pyndl = pyNDL("Default", win, (0, 0), win.get_size())

while True:

  pyndl.frame(pygame.event.get(), pygame.mouse.get_pos())
  pygame.display.update()
```

