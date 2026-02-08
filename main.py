from Set_DNP_To_False_True import *
from PriceDatasheetUpdater import updatePriceOrDatasheet
from time import sleep



def add_upt_options():
    while True:
        print('\033c')

        print("--PyCad-Automated-Scripts--\n\n\nChoose an option:\n\n\n[1] Add or update prices.\n\n[2] Add or update datasheet links.\n\n[3] Go back.\n\n> ", end = "")

        choosed_option = input("")

        print('\033c')

        if choosed_option == "1":
            updatePriceOrDatasheet("price")

        elif choosed_option == "2":
            updatePriceOrDatasheet("datasheet")

        elif choosed_option == "3":
            break

        else:
            print("\n\nThe chosen option is not valid. Please, retry.\n")
            sleep(2)
            print('\033c')
            continue



def dnp_options():
    while True:
        print('\033c')

        print("--PyCad-Automated-Scripts--\n\n\nChoose an option:\n\n\n[1] Set or remove DNP for all the schematics in the selected directory.\n\n[2] Set or remove DNP for all the selected schematics.\n\n[3] Set or remove DNP for all the schematics, except for the ones selected.\n\n[4] Set or remove DNP for a selected part of a schematic.\n\n[5] Go back.\n\n> ", end = "")

        choosed_option = input("")

        print('\033c')

        if choosed_option == "1":
            set_all_dnp_to_false_true()
        
        elif choosed_option == "2":
            set_selected_dnp_to_false_true()

        elif choosed_option == "3":
            set_all_dnp_to_false_true_except_selected()

        elif choosed_option == "4":
            set_part_selected_dnp_false_true()

        elif choosed_option == "5":
            break

        else:
            print("\n\nThe chosen option is not valid. Please, retry.\n")
            sleep(2)
            print('\033c')
            continue



def main_menu():
    while True:
        print('\033c')

        print("--PyCad-Automated-Scripts--\n\n\nChoose an Option:\n\n\n[1] Set or Remove DNP.\n\n[2] Add or update prices and datasheet links.\n\n[3] Quit\n\n> ", end = "")

        choosed_option = input("")

        if choosed_option == "1":
            dnp_options()

        elif choosed_option == "2":
            add_upt_options()

        elif choosed_option == "3":
            print('\033c')
            exit()

        else:
            print("\n\nThe chosen option is not valid. Please, retry.\n")
            sleep(2)
            continue



main_menu()
