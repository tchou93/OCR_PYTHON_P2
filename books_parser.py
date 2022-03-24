from bs4 import BeautifulSoup
import requests
import csv
import urllib.request
import os
import shutil

# Function extract_book
# Description: Parse the page book_url which represent the url of one book and store the required informations (product_page_url, universal_ product_code (upc), 
# title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url) into a dictionary (book_info).
def extract_book(book_url, book_info):
    page = requests.get(book_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get the product_page_url
    book_info["product_page_url"]=book_url

    # Get the title
    title_book=(soup.find("h1")).string
    book_info["title"]=title_book

    # Get all the description in tab on the website
    description_tab = soup.find_all("tr")

    for element in description_tab:
        # Get the universal_product_code
        if (element.find("th")).string=="UPC":
            book_info["universal_product_code"]=(element.find("td")).string
        # Get the price_including_tax
        elif (element.find("th")).string=="Price (incl. tax)":
            book_info["price_including_tax"]=float(((element.find("td")).string).replace("£",""))
        # Get the price_excluding_tax
        elif (element.find("th")).string=="Price (excl. tax)":
            book_info["price_excluding_tax"]=float(((element.find("td")).string).replace("£",""))
        # Get the number_available    
        elif (element.find("th")).string=="Availability":
            book_info["number_available"]=int(((element.find("td")).string).replace("In stock (","").replace(" available)",""))

    # Get the image_url
    image_struct = soup.find_all("div",class_="item active")
    for image_tag in image_struct:
        book_info["image_url"]=((image_tag.find("img")))['src'].replace("../../","http://books.toscrape.com/")

    # Get the product_description
    product_description_struct = soup.find_all("p")
    flag_description = 0
    for product_description_tag in product_description_struct:
        if product_description_tag.get('class') == None:
            book_info["product_description"]=product_description_tag.string
            flag_description = 1
    if(flag_description != 1):
        book_info["product_description"]="empty"

    # Get the category
    category_struct = (soup.find("ul",class_="breadcrumb")).find_all("li")
    book_info["category"]=(category_struct[2].find("a")).string

    # Get the review_rating
    review_rating_struct = soup.find(class_="col-sm-6 product_main")  
    if review_rating_struct.find(class_="star-rating Zero") != None:
        book_info["review_rating"]=0
    elif review_rating_struct.find(class_="star-rating One") != None:
        book_info["review_rating"]=1
    elif review_rating_struct.find(class_="star-rating Two") != None:
        book_info["review_rating"]=2
    elif review_rating_struct.find(class_="star-rating Three") != None:
        book_info["review_rating"]=3
    elif review_rating_struct.find(class_="star-rating Four") != None:
        book_info["review_rating"]=4
    else:
        book_info["review_rating"]=5

# Function extract_books_category
# Description: Extract informations of all the books on a category from category_url into a list (books_category_info).
def extract_books_category(category_url,books_category_info):
    flag_next = 1
    books_url = []
    print(f"Extraction de la catégorie ayant pour lien {category_url} en cours...")
    while flag_next != 0:
        page = requests.get(category_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        if (soup.find(class_="next")) != None:
            category_url = (category_url[0:category_url.rfind("/")+1])+ ((soup.find(class_="next")).find("a"))["href"]   
        else:
            flag_next = 0

        for links_books in soup.find_all(class_="image_container"):
            books_url.append(((links_books.find("a"))["href"]).replace("../../..","https://books.toscrape.com/catalogue"))
    for book_url in books_url:
        book_info = {}
        extract_book(book_url, book_info)
        books_category_info.append(book_info)

# Function extract_books_categories
# Description: Extract informations of all the books on all the categories from https://books.toscrape.com/index.html into a list (books_category_info).
def extract_books_categories(books_categories_info):
    categories_url = []
    extract_url_categories("https://books.toscrape.com/index.html",categories_url)
    
    for category_url in categories_url:
        books_category_info = []
        extract_books_category(category_url,books_category_info)
        books_categories_info.append(books_category_info)

# Function book_to_csv
# Description: Create a file tree with a csv file and image from the informations of a book (book_info).
def book_to_csv(book_info):
    header = ["product_page_url", "universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]
    book_name= book_info["title"]
    category_name= book_info["category"]
    extract_path ="./extract/"
    category_path = extract_path + category_name + "/"
    images_path= category_path + "images/"

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        os.makedirs(category_path)
        os.makedirs(images_path)
    elif not os.path.exists(category_path):
        os.makedirs(category_path)
        os.makedirs(images_path)
    else:
        shutil.rmtree(category_path)
        os.makedirs(category_path)
        os.makedirs(images_path)

    csv_file_path= category_path + "book_parse.csv"
    with open(csv_file_path,'w',encoding='utf-8-sig', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(header)
        writer.writerow([book_info["product_page_url"], book_info["universal_product_code"], book_name, book_info["price_including_tax"], book_info["price_excluding_tax"], book_info["number_available"], book_info["product_description"], book_info["category"], book_info["review_rating"], book_info["image_url"]])
 
    urllib.request.urlretrieve(book_info["image_url"], images_path + book_info["universal_product_code"]+".jpg")
    print(f"Voir la conversion du livre \"{book_name}\" en fichier csv au niveau du chemin {csv_file_path}.")
    print(f"Voir l'image du livre \"{book_name}\" au niveau du chemin {images_path}.")

# Function books_category_to_csv
# Description: Create a file tree with some csv files and images from the informations of all the books on a category (books_category_info).
def books_category_to_csv(books_category_info):
    header = ["product_page_url", "universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]
    category_name = (books_category_info[0])["category"]
    extract_path ="./extract/"
    category_path = extract_path + category_name + "/"
    images_path= category_path + "images/"

    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
        os.makedirs(category_path)
        os.makedirs(images_path)
    elif not os.path.exists(category_path):
        os.makedirs(category_path)
        os.makedirs(images_path)
    else:
        shutil.rmtree(category_path)
        os.makedirs(category_path)
        os.makedirs(images_path)
        
    csv_file_path= category_path +(books_category_info[0])["category"]+".csv"
    with open(csv_file_path,'w',encoding='utf-8-sig', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(header)
        
        for i in range(len(books_category_info)):     
            writer.writerow([(books_category_info[i])["product_page_url"], (books_category_info[i])["universal_product_code"], (books_category_info[i])["title"], (books_category_info[i])["price_including_tax"], (books_category_info[i])["price_excluding_tax"], (books_category_info[i])["number_available"], (books_category_info[i])["product_description"], (books_category_info[i])["category"], (books_category_info[i])["review_rating"], (books_category_info[i])["image_url"]])
            urllib.request.urlretrieve((books_category_info[i])["image_url"], images_path + (books_category_info[i])["universal_product_code"]+".jpg")

    print(f"Voir la conversion de la catégorie {category_name} en fichier csv au niveau du chemin {csv_file_path}.")
    print(f"Voir les images de la catégorie {category_name} au niveau du chemin {images_path}.")

# Function extract_books_categories_to_csv
# Description: Create a files tree with some csv files and images from the informations of all the books on all the categories (books_categories_info).
def books_categories_to_csv(books_categories_info):
    for books_category_info in books_categories_info:
        books_category_to_csv(books_category_info)

# Function extract_url_categories
# Description: Extract all the categories url from the main_url to a list(categories_url).
def extract_url_categories(main_url,categories_url):
    page = requests.get(main_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    categories_struct = soup.find("ul",class_="nav")
    for categories_tag in categories_struct.find_all("a"):
        categories_url.append("https://books.toscrape.com/"+categories_tag["href"])
    del categories_url[0]

############################################################################
# Program main                                                             #
# Give some options to a user to extract datas from a book, category       #
# or categories of the website Books to Scrape                             #
# All the datas will be store on ./
############################################################################
while 1:
    print("-----------------------------------------------------------------")
    print("Bienvenue dans le script d'extraction du site \"Books to Scrape\"")
    print("1: Extraire une catégorie.")
    print("2: Extraire toutes les catégories.")
    print("3: Extraction d'un livre")
    print("4: Quittez.")
    print("------------------------------------------------------------------")
    choix = input("Veuillez choisir le mode d'extraction: ")
    choix = int(choix)
    if choix==4:
        break
    elif choix<1 or choix>4:
        print("Le choix ne correspond à aucune extraction, recommencez! ")
    elif choix==1:
        print("--------------------------")
        print("Extraction d'une catégorie")
        print("--------------------------")
        category_url = input("Veuillez indiquer l'url exacte de la catégorie à extraire: ")
        books_category_info = []
        extract_books_category(category_url,books_category_info)
        books_category_to_csv(books_category_info)
    elif choix==2:
        print("-----------------------------------")
        print("Extraction de toutes les catégories")
        print("-----------------------------------")
        books_categories_info = []
        extract_books_categories(books_categories_info)
        books_categories_to_csv(books_categories_info)
    elif choix==3:
        print("---------------------")
        print("Extraction d'un livre")
        print("---------------------")   
        book_url = input("Veuillez indiquer l'url exacte du livre à extraire: ")
        book_info = {}
        extract_book(book_url, book_info)
        book_to_csv(book_info)
