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
books_url = []
product_page_url = []
universal_product_code= []
title = []
price_including_tax = []
price_excluding_tax = []
number_available = []
product_description = []
category = []
review_rating = []
image_url = []

books_url_page = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
flag_next = 1

while flag_next != 0:
    page = requests.get(books_url_page)
    soup = BeautifulSoup(page.content, 'html.parser')
    if (soup.find(class_="next")) != None:
        books_url_page = (books_url_page[0:books_url_page.rfind("/")+1])+ ((soup.find(class_="next")).find("a"))["href"]   
    else:
        flag_next = 0
    for links_books in soup.find_all(class_="image_container"):
        books_url.append(((links_books.find("a"))["href"]).replace("../../..","https://books.toscrape.com/catalogue"))

for book_url in books_url:
    page = requests.get(book_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get the product_page_url
    product_page_url.append(book_url)

    # Get the title
    title.append((soup.find("h1")).string)

    # Get all the description tab
    description_tab = soup.find_all("tr")
    for element in description_tab:
        # Get the universal_product_code
        if (element.find("th")).string=="UPC":
            universal_product_code.append((element.find("td")).string)
        # Get the price_including_tax
        elif (element.find("th")).string=="Price (incl. tax)":
            price_including_tax.append(float(((element.find("td")).string).replace("£","")))
        # Get the price_excluding_tax
        elif (element.find("th")).string=="Price (excl. tax)":
            price_excluding_tax.append(float(((element.find("td")).string).replace("£","")))
        # Get the number_available    
        elif (element.find("th")).string=="Availability":
            number_available.append(int(((element.find("td")).string).replace("In stock (","").replace(" available)","")))

    # Get the image_url
    image_struct = soup.find_all("div",class_="item active")
    for image_tag in image_struct:
        image_url.append(((image_tag.find("img")))['src'].replace("../../","http://books.toscrape.com/"))

    # Get the product_description
    product_description_struct = soup.find_all("p")
    for product_description_tag in product_description_struct:
        if product_description_tag.get('class') == None:
            product_description.append(product_description_tag.string)

    # Get the category
    category_struct = (soup.find("ul",class_="breadcrumb")).find_all("li")
    category.append((category_struct[2].find("a")).string)

    # Get the review_rating
    review_rating_struct = soup.find(class_="col-sm-6 product_main")  
    if review_rating_struct.find(class_="star-rating Zero") != None:
        review_rating.append(0)
    elif review_rating_struct.find(class_="star-rating One") != None:
        review_rating.append(1)
    elif review_rating_struct.find(class_="star-rating Two") != None:
        review_rating.append(2)
    elif review_rating_struct.find(class_="star-rating Three") != None:
        review_rating.append(3)
    elif review_rating_struct.find(class_="star-rating Four") != None:
        review_rating.append(4)
    else:
        review_rating.append(5)

# print(f"product_page_url: {product_page_url}")
# print(f"universal_product_code: {universal_product_code}")
# print(f"title: {title}")
# print(f"price_including_tax: {price_including_tax}")
# print(f"price_excluding_tax: {price_excluding_tax}")
# print(f"number_available: {number_available}")
# print(f"product_description: {product_description}")
# print(f"category: {category}")
# print(f"review_rating: {review_rating}")
# print(f"image_url: {image_url}")

en_tete = ["product_page_url", "universal_product_code","title","price_including_tax","price_excluding_tax","number_available","product_description","category","review_rating","image_url"]

with open('data.csv', 'w', newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=';')
    writer.writerow(en_tete)

    # for index in range(len(product_page_url)):     
    #     writer.writerow([product_page_url[index],universal_product_code[index],title[index],price_including_tax[index],price_excluding_tax[index],number_available[index],product_description[index],category[index],review_rating[index],image_url[index]])
    #     urllib.request.urlretrieve(image_url[index],((title[index])[0:10]+".jpg"))
        