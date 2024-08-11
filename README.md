
# S2L

A GUI interface that can segment images with additional info.


## Acknowledgements

 - [CHATGPT: Assisted in those boring and long tasks.](https://chatgpt.com)


## Roadmap

- More features

- Optimizations (REALLY IMPORTANT)
- Linux and Mac support 


## Building into a  single executable

I used SFX and pyinstaller. You can package it in anyway possible

## Prerequisites

- Pyinstaller or Nuitka (I used Pyinstaller)

- A reliable SFX creator (I used WinRAR for the ease of use)

## Actual Build Process

- Compile the loader.py file using pyinstaller
```bash
pyinstaller --onefile loader.py
```

- Package the executable that you generated with the AutomationFolder. Make sure that the executeable runs AFTER extracting it. The loader.exe file will run the main.py script inside the  AutomationFolder
    
## Installation

Either build or download the precompiled executable ( Windows ONLY )

