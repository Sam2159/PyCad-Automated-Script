import skip
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from filedialpy import openFile
from pathlib import Path






def priceFinder(partNumber):
    searchResult = requests.get(f"https://www.findchips.com/search/{partNumber}?currency=USD").content

    soup = BeautifulSoup(searchResult, features="html.parser")

    if soup.find("h2", attrs={"class" : "title no-results-results-title"}) != None:
        return None, None

    DigiKeyElement = soup.find("tr", attrs={"data-distributor_name" : "DigiKey"})

    if DigiKeyElement == None:
        return None, None


    priceList_String = DigiKeyElement["data-price"]

    if(priceList_String == "[]"):
        return 0, 0

    priceList_Iterable = re.findall("(([0-9]+)([.]*)([0-9]*))", priceList_String)

    quantity = priceList_Iterable[-2][0]

    price = priceList_Iterable[-1][0]

    print(f"Price: ${price}\n")

    return quantity, price




def datasheetFinder(partNumber):
    mainSite = "https://www.datasheets.com"

    searchResult = requests.get(f"{mainSite}/search?p={partNumber}").content

    soup = BeautifulSoup(searchResult, features="html.parser")

    try:
        componentPageUrl = soup.find("a", text=partNumber)["href"]

    except TypeError:
        return None

    componentPage = requests.get(f"{mainSite}{componentPageUrl}").content

    soup = BeautifulSoup(componentPage, features="html.parser")

    try:
        datasheetUrl = soup.find("a", attrs={"data-testid" : "datasheet-link"})["href"]

    except TypeError:
        return None

    print(f"Datasheet: {datasheetUrl}\n")
    
    return datasheetUrl






def updatePriceOrDatasheet(target):
    schemPath = Path(openFile(filter = "*.kicad_sch", title = "Choose One File"))

    if schemPath == ".":
        print('\033c')
        print("\nNothing has been selected, retry.\n")
        sleep(2)
        return


    schem = skip.Schematic(schemPath)

    invalidComponents = []

    notFound = []

    outOfStock = []

    onlyBigQuantityAvailable = []


    print('\033c')


    # This for loop try to find the part number of each component.

    for component in schem.symbol:
        compType = component.Value.value

        compReference = component.property.Reference.value

        compDatasheet = component.property.Datasheet.value


        if re.findall("VCC|GND|test-pad", compType) == [] and compReference != "Module1":
            try:
                partNumber = component.property.MPN.value

            except:
                try:
                    partNumber = component.property.MP.value

                except:
                    # Fallback

                    if not "https://" in compDatasheet and compDatasheet != "":
                        partNumber = compDatasheet

                    elif compType != "~" and len(compType) > 4:
                        partNumIndex = re.search("([A-Z]{0}([a-z]|[0-9])-(_{0})([A-Z]|[0-9]|-)*)$|(([A-Z]|[0-9]|[a-z])_([A-Z]|[0-9]|-)*)$", compType)

                        if partNumIndex == None:
                            partNumIndex = re.search(".", compType).start()

                        else:
                            partNumIndex = partNumIndex.start() + 2

                        partNumber = compType[partNumIndex:]

                    else:
                        if(len(compReference) > 4):
                            partNumber = compReference

                        else:
                            notFound.append(compReference)
                            continue



            if partNumber.islower():
                notFound.append(compReference)
                continue

            print(f'Found component: "{compReference}" Component part number: "{partNumber}"\n')

            if target == "price":
                quantity, price = priceFinder(partNumber)


                if quantity == None:
                    notFound.append(compReference)
                    continue

                elif int(quantity) < 1:
                    outOfStock.append(compReference)
                    continue

                elif int(quantity) > 1:
                    onlyBigQuantityAvailable.append(compReference)
                    continue


                # Create the "Price" property and save the price in it

                priceProp = component.property.Description.clone()
                priceProp.name = "Price"
                priceProp.value = f"${price}"

            elif target == "datasheet":
                datasheetUrl = datasheetFinder(partNumber)

                if datasheetUrl == None:
                    notFound.append(compReference)
                    print("Datasheet: None\n")
                    continue

                component.property.Datasheet.value = datasheetUrl



    schem.write(schemPath)

    print("\nDone\n")

    sleep(1)


    print('\033c')
    print(f'''{schemPath}:
            Invalid part number or not found: {notFound}
            Out of Stock: {outOfStock}
            Only big quantity available: {onlyBigQuantityAvailable}\n''')

    input("\n\nPress any key to continue...")

