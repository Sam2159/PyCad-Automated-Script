from time import sleep
import skip
from glob import glob
import filedialpy
import subprocess
from pathlib import Path
import tkinter
from tkinter import Tk, messagebox
import fitz
import os
from platform import system



def show_pdf(pdf_location=""):

    global selected, select_done

    select_done = False

    selected = False

    doc = fitz.open(pdf_location)
    page = doc.load_page(0)


    zoom = 1280 / page.rect.width

    width = int(page.rect.width * zoom)
    height = int(page.rect.height * zoom)

    window = Tk()
    window.title("Schematic Part Selector")
    window.geometry(f"{width}x{height + 50}")
    window.focus_force()

    instruction = tkinter.Label(master = window, text = 'Select the part of the schematic that you want to modify', font = 'Arial 13')
    instruction.pack()


    mat = fitz.Matrix(zoom, zoom)
    pixmap = page.get_pixmap(matrix = mat)
    img = pixmap.tobytes()
    
    load_img = tkinter.PhotoImage(data = img)

    canvas = tkinter.Canvas(window, width = width, height = height)
    canvas.create_image(0, -8, anchor = tkinter.NW, image = load_img)
    canvas.pack()

    def SelectStart(event): #get pointer x, y
        global old_x, old_y
        old_x = event.x
        old_y = event.y
        canvas.delete("selbox")
        

    def SelectBox(event): #create selectbox
        global selected
        selected = True
        canvas.create_rectangle(old_x, old_y, event.x, event.y, tags="selbox", stipple="gray25", fill = "blue") #TO DO: fix stipple in mac os.
        canvas.delete("selbox")
        canvas.create_rectangle(old_x, old_y, event.x, event.y, tags="selbox", stipple="gray25", fill = "blue")


    def SelectRelease(event): #get pointer last x, y
        global new_x, new_y, selected, select_done
        new_x = event.x
        new_y = event.y
        sleep(0.2)
        if selected:
            user_response = messagebox.showinfo(message = "Do you want to confirm the selection made?", icon = "question", type="yesno")
            if user_response == "yes":
                select_done = True
                global x1, y1, x2, y2

                #the x and y value of the tkinter canvas and the schematic file text don't match, this solve it.
                conversion_value = 0.071969143687814 / 0.0254

                x1 = (old_x / zoom) / conversion_value
                y1 = (old_y / zoom) / conversion_value

                x2 = (new_x / zoom) / conversion_value
                y2 = (new_y / zoom) / conversion_value

                window.destroy()
                window.quit()

            elif user_response == "no":
                select_done = False
                selected = False
                canvas.delete("selbox")

    canvas.bind("<ButtonPress-1>", SelectStart)
    canvas.bind("<B1-Motion>", SelectBox)
    canvas.bind("<ButtonRelease-1>", SelectRelease)


    window.mainloop()





# This function take the settings saved before in the Old_Set.sav file and update the schematic with them

def restore_old_settings():
    with open(f"{Path(__file__).parent}/Old_Set.sav", "r+") as save_txt:
        no_dir = True

        old_settings = (save_txt.read()).split("\n")
        for schem_file_dir in finded_schem:
            schem = skip.Schematic(schem_file_dir)
            if schem_file_dir in old_settings:
                no_dir = False
                for component in schem.symbol:
                    symbol_value = component.property.Reference.value

                    try:
                        filedir_index = old_settings.index(schem_file_dir)

                        end_file_symbols = old_settings.index("T_END_", filedir_index)

                        index_component = old_settings.index(symbol_value, filedir_index, end_file_symbols)

                        component.dnp.value = bool( int(old_settings[ index_component + 1 ]) )
                        old_settings.remove(old_settings[index_component])
                        old_settings.remove(old_settings[index_component + 1])
                    except ValueError:
                        pass

                schem.write(schem_file_dir)


        if no_dir == True:
            print("\nTheres not saved settings for this directory.\n")
            sleep(1)
            return 0
        else:
            print("\nDone.\n")
            sleep(1)






# This function set or disable DNP for each symbol in the schematics contained in the choosed directory

def set_all_dnp_to_false_true():

    global finded_schem, dir_path
    
    dir_path = filedialpy.openDir(title = "Choose a Directory")

    if not dir_path:
        print("No directory have been selected. Please, retry.")
        sleep(1)
        return 0

    finded_schem = glob(f"{dir_path}/*.kicad_sch")

    if finded_schem:
        while True:
            global true_or_false
            true_or_false = (input("\nPlease, specify if DNP must be set to False [F], True [T] or restored to old settings [R] (if they exist). If you want to go back, insert [C]: ")).lower()
            if true_or_false == "t":
                choosen_option = True
                break
            elif true_or_false == "f":
                choosen_option = False
                break
            elif true_or_false == "r":
                restore_old_settings()
                return 0
            elif true_or_false == "c":
                print("\nAborted.\n")
                sleep(1)
                return 0
            else:
                print("\nThe choosen option doesn't exist, retry.\n")


        with open(f"{Path(__file__).parent}/Old_Set.sav", "w") as save_txt:
            save_txt.truncate()

            for schem_file_dir in finded_schem:
                save_txt.write(f"{schem_file_dir}\n") 
                print(schem_file_dir)
                schem = skip.Schematic(schem_file_dir)
                for component in schem.symbol:
                    save_txt.write(f"\n{ component.property.Reference.value }\n{ int(component.dnp.value) }\n\n")
                    component.dnp.value = choosen_option
                
                save_txt.write(f"\nT_END_\n\n\n") 

                schem.write(schem_file_dir)

        print("\nDone.\n")
        sleep(1)

    else:
        print("\nThe selected folder doesn't contain '.kicad_sch' files.\n")






# This function set or disable DNP for each symbol contained in the selected schematics

def set_selected_dnp_to_false_true():

    schems_path = filedialpy.openFiles(filter = "*.kicad_sch", title = "Choose One or More Files")

    if schems_path and schems_path != [""]:
        while True:
            global true_or_false
            true_or_false = (input("\nPlease, specify if DNP must be set to False [F] or True [T]. If you want to go back, insert [C]: ")).lower()
            if true_or_false == "t":
                choosen_option = True
                break
            elif true_or_false == "f":
                choosen_option = False
                break
            elif true_or_false == "c":
                print("\nAborted.\n")
                sleep(1)
                return 0
            else:
                print("\nThe choosen option doesn't exist, retry.\n")
            
        for schem_file in schems_path:
            print(schem_file)
            schem = skip.Schematic(schem_file)
            for component in schem.symbol:
                component.dnp.value = choosen_option

            schem.write(schem_file)

        print("\nDone.\n")
        sleep(1)

    else:
        print("\nNo files have been selected. Please, retry.\n")
        sleep(1)
        return 0


#the original function "openFiles" of filedialpy wasn't permitting the user to select just one file on Windows, so a modified version is needed.

def windows_file_selector(filter=None,title=None):
    kwargs={}

    kwargs["Title"] = title

    kwargs["Filter"]= filter+"\0"+filter+"\0"

    kwargs["Flags"]=filedialpy.win32con.OFN_ALLOWMULTISELECT  | filedialpy.win32con.OFN_EXPLORER
        
    hwnd = filedialpy.win32gui.GetForegroundWindow()
    try:
        res=filedialpy.win32gui.GetOpenFileNameW(hwndOwner=hwnd,**kwargs)[0]
    except:
        return 0

    res = res.split('\x00')
    dirname=res[0]
    if len(res) > 1:
        res = [os.path.join(dirname,x) for x in res[1:]]
    elif len(res) == 1:
        pass
    else: 
        res=[]
    
    return res



# This function set or disable DNP for each symbol in the schematics contained in a directory except for the selected ones

def set_all_dnp_to_false_true_except_selected():

    global finded_schem

    check_sys_name = system()
    
    if check_sys_name == "Windows":
        files_path = windows_file_selector(filter = "*.kicad_sch", title = "Choose One or More Files")

    else:
        files_path = filedialpy.openFiles(filter = "*.kicad_sch", title = "Choose One or More Files")

    if files_path and files_path != [""]:

        directory_of_files = Path(files_path[0]).parent

        finded_schem = glob(f"{directory_of_files}/*.kicad_sch")

        for dir_choose in files_path:
            if dir_choose in finded_schem:
                finded_schem.remove(dir_choose)

        while True:
            global true_or_false
            true_or_false = (input(f"\nPlease, specify if DNP must be set to False [F] or True [T]. If you want to go back, insert [C]: ")).lower()
            if true_or_false == "t":
                choosen_option = True
                break
            elif true_or_false == "f":
                choosen_option = False
                break
            elif true_or_false == "c":
                print("\nAborted.\n")
                sleep(1)
                return 0
            else:
                print("\nThe choosen option doesn't exist, retry.\n")

        for schem_file in finded_schem:
            print(schem_file)
            schem = skip.Schematic(schem_file)
            for component in schem.symbol:
                component.dnp.value = choosen_option

            schem.write(schem_file)

        print("\nDone.\n")
        sleep(1)

    else:
        print("\nNo files have been selected. Please, retry.\n")
        sleep(2)
        return 0
    

def kicad_path_not_found():
    global kicad_path, kicad_cli_path
    choosen_option = input('\nThe kicad installation folder has not been found. Select the "KiCad" folder manually [S] or, if you want to go back, insert [C]: ').lower()
    if choosen_option == "s":
        kicad_path = Path(filedialpy.openDir(title = "Select The KiCad Installation Folder"))

        if kicad_path == Path("."):
            print('\033c')
            print("\nNothing has been selected, retry.\n")
            sleep(2)
            return 0
        
        kicad_cli_path_finder = sorted(Path(kicad_path).rglob("kicad-cli.exe"))

        kicad_cli_path = kicad_cli_path_finder[0]
        
        with open(f"{Path(__file__).parent}/Kicad_custom_path.sav", "w") as save_txt:
                save_txt.truncate()
                save_txt.write(str(kicad_cli_path))


    elif choosen_option == "c":
        print("\nAborted.\n")
        sleep(1)
        return 0
    
    else:
        print("\nThe choosen option doesn't exist, retry.\n")

    

#This function set or disable DNP for each symbol in the choosen part of the selected schematic

def set_part_selected_dnp_false_true():
    global kicad_path, kicad_cli_path

    if system().lower() == "windows": 
        with open(f"{Path(__file__).parent}/Kicad_custom_path.sav") as save_txt:
            save_path = save_txt.read()

            if Path("C:/Program Files/KiCad/").is_dir():
                kicad_path = "C:/Program Files/KiCad"

                kicad_cli_path_finder = sorted(Path(kicad_path).glob("*/bin/kicad-cli.exe"))

                kicad_cli_path = kicad_cli_path_finder[0] #TO DO: handle IndexError if something is wrong in the KiCad folder

            elif Path(f"{Path.home()}/AppData/Local/Programs/Kicad/").is_dir():
                kicad_path = f"{Path.home()}/AppData/Local/Programs/Kicad/"

                kicad_cli_path_finder = sorted(Path(kicad_path).glob("*/bin/kicad-cli.exe"))

                kicad_cli_path = kicad_cli_path_finder[0] #TO DO: Same thing

            elif Path(save_path).is_file():
                print("\nUsing Saved Kicad Path.\n")
                kicad_cli_path = save_path

            else:
                not_found_path = kicad_path_not_found()
                if not_found_path == 0:
                    return 0

    
    elif system().lower() == "darwin":
        kicad_cli_path = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"

        if not Path(kicad_cli_path).is_file():
            not_found_path = kicad_path_not_found()
            if not_found_path == 0:
                return 0
    
    elif "linux" in system().lower():
        kicad_cli_path = "/usr/bin/kicad-cli"

        if not Path(kicad_cli_path).is_file():
            not_found_path = kicad_path_not_found()
            if not_found_path == 0:
                return 0


    file_path = Path(filedialpy.openFile(filter = "*.kicad_sch", title = "Choose One File"))
    
    if file_path != Path("."):

        schem = skip.Schematic(file_path)

        py_path = Path(__file__).parent

        output_export = str(subprocess.run(f'"{kicad_cli_path}" sch export pdf --output "{py_path}/schem_export_img.pdf" "{str(file_path)}"', shell = True))

        if "returncode=0" in output_export:
            pass
        
        else:
            sleep(1.5)
            return "Failed"

        exported_img_path = f"{py_path}/schem_export_img.pdf"

        show_pdf(exported_img_path)

        if select_done:

            while True:
                global true_or_false

                print('\033c')
                true_or_false = (input(f"Please, specify if DNP must be set to False [F] or True [T]. If you want to go back, insert [C]: ")).lower()
                
                if true_or_false == "t":
                    choosen_option = True
                    break
                elif true_or_false == "f":
                    choosen_option = False
                    break
                elif true_or_false == "c":
                    print("\nAborted.\n")
                    sleep(1)
                    return 0
                else:
                    print("\nThe choosen option doesn't exist, retry.\n")

        else:
            print('\033c')
            print("\nNothing has been selected, retry.\n")
            sleep(2)
            return 0
        

        for component in schem.symbol.within_rectangle(x1, y1, x2, y2):
            component.dnp.value = choosen_option

        schem.write(file_path)

        print("\nDone.\n")
        sleep(1)

    else:
        print("\nNo files have been selected. Please, retry.\n")
        sleep(1)
        return 0