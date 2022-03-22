import requests
import csv
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

url = "https://books.toscrape.com/catalogue/mesaerion-the-best-science-fiction-stories-1800-1849_983/index.html"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')


for index_books in range(1):
    # Get the product_page_url
    product_page_url.append(url)
    print(f"product_page_url: {product_page_url}")

    # Get the title
    title.append((soup.find("h1")).string)
    print(f"title: {title}")

    # Get all the description tab
    description_tab = soup.find_all("tr")
    for element in description_tab:

        # Get the universal_product_code
        if (element.find("th")).string=="UPC":
            universal_product_code.append((element.find("td")).string)
            print(f"universal_product_code: {universal_product_code}")
        # Get the price_including_tax
        elif (element.find("th")).string=="Price (incl. tax)":
            price_including_tax.append(float(((element.find("td")).string).replace("£","")))
            print(f"price_including_tax: {price_including_tax}")
        # Get the price_excluding_tax
        elif (element.find("th")).string=="Price (excl. tax)":
            price_excluding_tax.append(float(((element.find("td")).string).replace("£","")))
            print(f"price_excluding_tax: {price_excluding_tax}")
        # Get the number_available    
        elif (element.find("th")).string=="Availability":
            number_available.append(int(((element.find("td")).string).replace("In stock (","").replace(" available)","")))
            print(f"number_available: {number_available}")

    # Get the image_url
    image_struct = soup.find_all("div",class_="item active")
    for image_tag in image_struct:
        image_url.append(((image_tag.find("img")))['src'].replace("../../","http://books.toscrape.com/"))
        print(f"image_url: {image_url}")

    # Get the product_description
    product_description_struct = soup.find_all("p")
    for product_description_tag in product_description_struct:
        if product_description_tag.get('class') == None:
            product_description.append(product_description_tag.string)
            print(f"product_description: {product_description}")

    # Get the category
    category_struct = (soup.find("ul",class_="breadcrumb")).find_all("li")
    category.append((category_struct[2].find("a")).string)
    print(f"category: {category}")

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
        print(soup.find(class_="star-rating Three"))
    elif review_rating_struct.find(class_="star-rating Four") != None:
        review_rating.append(4)
    else:
        review_rating.append(5)
    print(f"review_rating: {review_rating}")

# print(f"{image_url[0]} , {product_page_url[0]}\n")
# with open('couleurs_preferees.csv') as fichier_csv:
#    reader = csv.reader(fichier_csv, delimiter=',')
#    for ligne in reader:
#       print(ligne)