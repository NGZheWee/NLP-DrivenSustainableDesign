from DrissionPage import ChromiumPage
import pandas as pd
import re
from parsel import Selector
import os
import random

def random_delay(page, scroll_times=random.randint(0, 2), delay=random.uniform(0, 2)):
    for _ in range(scroll_times):
        page.actions.scroll(0, random.randint(60, 1000))
        page.wait(delay)

def extract_product_details(page, product_url):
    page.get(product_url)
    page.wait(random.uniform(1,3))  # Random delay to avoid detection
    sel = Selector(text=page.html)
    random_delay(page)  # Random action chain to avoid detection

    # Extract price information
    price_whole = sel.css('span.a-price-whole::text').get()
    price_fraction = sel.css('span.a-price-fraction::text').get()
    if price_whole and price_fraction:
        price = f"{price_whole.strip()}.{price_fraction.strip()}"
    else:
        price = None

    # Extract product description with line breaks
    description_items = sel.css('ul.a-unordered-list.a-vertical.a-spacing-mini li span.a-list-item::text').getall()
    description = '\n'.join([item.strip() for item in description_items])  # Join with line breaks

    # Extract sustainability features
    sustainability_sections = sel.css('div.a-section.a-spacing-base')
    sustainability_features = []
    for section in sustainability_sections:
        title = section.css('span.a-size-base-plus.a-text-bold::text').get()
        if title:
            feature_text = section.css('p.a-size-base::text').get()
            certifications = section.css('div.climatePledgeFriendlyAttributePillText a::text').getall()
            certification_text = ' '.join(certifications).strip()
            feature_detail = f"{title.strip()}\n{feature_text.strip() if feature_text else ''}\nAs certified by\n{certification_text}"
            sustainability_features.append(feature_detail)
    sustainability_features_text = '\n\n'.join(sustainability_features)

    product_details = {
        'name': sel.css('#productTitle::text').get().strip(),
        'price': price,
        # Removed 'product_dimensions' key as per your request
        'description': description,
        'sustainability_features': sustainability_features_text,
        'rating': sel.css('span.a-icon-alt::text').get(),
        'number_of_reviews': sel.css('#acrCustomerReviewText::text').get(),
        'product_page_url': product_url
    }

    return product_details

def process_urls(file_path):    # Extract URLs from TXT file
    with open(file_path, 'r') as file:
        product_urls = file.readlines()

    all_products = []

    page = ChromiumPage()

    for url in product_urls:
        product_url = url.strip()
        if product_url:
            details = extract_product_details(page, product_url)
            all_products.append(details)

    page.quit()

    return all_products

def save_products_to_csv(products, output_path):    # Save products to CSV
    df = pd.DataFrame(products)
    df.to_csv(output_path, index=False)

def process_all_files(folder_path):    # Process all TXT files in a folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.txt'):
            txt_file_path = os.path.join(folder_path, file_name)
            csv_output_path = os.path.join(folder_path, file_name.replace('.txt', '.csv'))

            all_products = process_urls(txt_file_path)
            save_products_to_csv(all_products, csv_output_path)

# Process all TXT files in the folder and save the results
folder_path = r'D:\OneDrive\UC Berkeley\Sustainable Design Insights\Programs\Amazon Product Scrapers'  # Folder containing TXT files
process_all_files(folder_path)
