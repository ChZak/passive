import argparse
import requests
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def check_name_format(names_found, first_name, last_name):
    # Vérifier prénom puis nom
    if first_name.lower() == names_found[0].lower() and last_name.lower() == names_found[1].lower():
        return first_name, last_name
    # Vérifier nom puis prénom
    elif last_name.lower() == names_found[0].lower() and first_name.lower() == names_found[1].lower():
        return first_name, last_name
    return None, None
    

def generate_file():
    base_name = "result"
    extension =".txt"
    counter = 1
    filename = f"{base_name}{extension}"

    while os.path.exists(filename):
        filename = f"{base_name}{counter}{extension}"
        counter += 1

    return filename

def search_ip(ip_adress):
    url = f'http://ip-api.com/json/{ip_adress}'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'success':
        return {
            'ISP': data.get('isp', 'Not Available'),
            'Country': data.get('country', 'Not Available'),
            'RegionName': data.get('regionName', 'Not Available'),
            'City': data.get('city', 'Not Available'),
            'Zip': data.get('zip', 'Not Available'),
            'Lat': data.get('lat', 'Not Available'),
            'Lon': data.get('lon', 'Not Available'),
        }
    else:
        return 'No data found for this IP'
    
def search_fullname(fullname):
    # Diviser fullname en first_name et last_name
    try:
        first_name, last_name = fullname.split()
    except:
        print("Erreur : Le nom complet doit comprendre un prénom et nom")
        return
    

    # Créer session Firefox
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    driver.maximize_window()

    driver.get('https://www.pagesjaunes.fr/pagesblanches')

    #Localiser et remplir le champ de recherche
    search_field = driver.find_element(By.ID, 'quoiqui')
    search_field.clear()
    search_field.send_keys(fullname)
    search_field.submit()

    # Gérer la popup si elle existe
    try:
        dismiss_button = driver.find_element(By.ID, 'didomi-notice-agree-button')
        dismiss_button.click()
    except:
        pass

    # Récupérer les noms trouvés
    ul_element = driver.find_element(By.CLASS_NAME, 'bi-list')
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

    for li in li_elements:
        full_name_element = li.find_element(By.CLASS_NAME, 'bi-denomination')
        text_full_name = full_name_element.text

        # Diviser le nom trouvé en mots et comparer
        names_found = text_full_name.split()
        if len(names_found) >= 2:
            first_name_found, last_name_found = check_name_format(names_found, first_name, last_name)
            if first_name_found and last_name_found:
                # Trouver et cliquer sur le bouton pour afficher le numéro
                button = li.find_element(By.TAG_NAME, 'button')
                button.click()

                # Attendre l'affichage du numéro
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'number-contact'))
                )
                number_div = li.find_element(By.CLASS_NAME, 'number-contact')

                # Extraire le numéro
                pattern_number = r"(\d{2} \d{2} \d{2} \d{2} \d{2})"
                result_num = re.search(pattern_number, number_div.text)
                number_final = result_num.group(0) if result_num else 'Not Found'

                # Extraire et formater l'adresse
                the_address = li.find_element(By.CLASS_NAME, 'bi-address')
                address_text = the_address.text
                match = re.search(r'\b\d{5}\b', address_text)
                if match:
                    address_parse = address_text[:match.start()] + '\n' + address_text[match.start():]
                address_parse = address_parse.replace('Voir le plan', '')

                result_fullname_str = (
                    f"First Name : {first_name_found}\n"
                    f"Last Name : {last_name_found}\n"
                    f"Address : {address_parse}\n"
                    f"Phone Number : {number_final}\n"
                )

                print(result_fullname_str)
                
                filename = generate_file()
                with open(filename, 'w') as file:
                    file.write(result_fullname_str)
                    print(f"Results saved to {filename}")
                break
    driver.quit()            



def main():
    logo = """
╔═╗╔═╗╔═╗╔═╗╦╦  ╦╔═╗
╠═╝╠═╣╚═╗╚═╗║╚╗╔╝║╣ 
╩  ╩ ╩╚═╝╚═╝╩ ╚╝ ╚═╝

By ZakCH
V 1.0.0
    """

    print(logo)
    parser = argparse.ArgumentParser(description='Passive information gathering tool')
    parser.add_argument('-ip', help='Search with IP Address')
    parser.add_argument('-fn', help='Search with Full Name')

    args = parser.parse_args()

    if args.fullname:
        search_fullname(args.fullname)
    if args.ipaddress:
        result = search_ip(args.ipaddress)
        result_str = (
            f"ISP : {result['ISP']}\n"
            f"Country : {result['Country']}\n"
            f"Region Name : {result['RegionName']}\n"
            f"City : {result['City']}\n"
            f"Zip Code : {result['Zip']}\n"
            f"City Lat/Lon: ({result['Lat']}) / ({result['Lon']})\n"
        )

        print(result_str)

        filename = generate_file()
        with open(filename, 'w') as file:
            file.write(result_str)
            print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()
