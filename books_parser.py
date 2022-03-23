import requests
import csv
import urllib.request
from bs4 import BeautifulSoup

""" 
Elements we need to stock during the parsing
- product_page_url
- universal_product_code (upc)
- title
- price_including_tax
- price_excluding_tax
- number_available
- product_description
- category
- review_rating
- image_url
"""
def extract_book(book_url, book_info):
    page = requests.get(book_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get the product_page_url
    book_info["product_page_url"]=book_url

    # Get the title
    book_info["title"]=(soup.find("h1")).string

    # Get all the description tab
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


def extract_books_category(category_url,books_info):
    flag_next = 1
    books_url = []
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
        books_info.append(book_info)

def extract_url_categories(main_url,categories_url):
    page = requests.get(main_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    categories_struct = soup.find("ul",class_="nav")
    for categories_tag in categories_struct.find_all("a"):
        categories_url.append("https://books.toscrape.com/"+categories_tag["href"])
    del categories_url[0]

def extract_books_to_csv(path_csv, books_info):
    en_tete = ["product_page_url", "universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]

    with open(path_csv+(books_info[0])["category"]+".csv",'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(en_tete)

        for i in range(len(books_info)):     
            writer.writerow([(books_info[i])["product_page_url"], (books_info[i])["universal_product_code"], (books_info[i])["title"], (books_info[i])["price_including_tax"], (books_info[i])["price_excluding_tax"], (books_info[i])["number_available"], (books_info[i])["product_description"], (books_info[i])["category"], (books_info[i])["review_rating"], (books_info[i])["image_url"]])

categories_url = []
books_category_info = []
books_categories_info = []
extract_url_categories("https://books.toscrape.com/index.html",categories_url)

for category_url in categories_url:
    books_category_info = []
    extract_books_category(category_url,books_category_info)
    books_categories_info.append(books_category_info)
    print(f"Traitement de la catégorie: {books_category_info[0]}")
    print("Extraction en cours...")
    extract_books_to_csv("D:/Tan/Formation/Python/Projet/P2/Livres_extraction/", books_category_info)
    print("Extraction Terminé...")

# urllib.request.urlretrieve(image_url[index],((title[index])[0:10]+".jpg"))