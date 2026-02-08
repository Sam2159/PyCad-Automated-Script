# PyCad-Automated-Script
A Python script that can automatically modify KiCad schematic properties. 

# Dependencies
Before running the script, make sure KiCad and the required Python modules are installed:
```
pip3 install kicad-skip filedialpy pathlib tk PyMuPDF requests bs4 tqdm
```
If you are on linux, you also need to run:
```
sudo apt-get install python3-tk
```

# How To Run
To run the Python script use:
```
python3 main.py
```

# Development Progress:
- [x] Add a script for automatically update DNP status
- [x] Add a script for automatically update components price
- [-] Add a script for automatically update components datasheet

>[!NOTE]
>To avoid problems when updating prices or datasheet links in a schematic, make sure that the MPN property exists for each component and that it contains the correct part number.
(The script will still try to find the part numbers in other properties, but it's not guaranteed to work every time)

>[!NOTE]
>If you have any problems with the script or think it could be improved, issues and PR are welcome.
