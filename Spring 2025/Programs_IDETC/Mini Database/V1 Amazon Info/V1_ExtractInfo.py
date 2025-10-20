import os
from random import randint

from numpy.random import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pickle
import pandas as pd


def save_cookies(driver, cookies_file):
    with open(cookies_file, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)


def load_cookies(driver, cookies_file):
    if os.path.exists(cookies_file):
        with open(cookies_file, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)


def amazon_login_and_save_cookies(driver, email, password, cookies_file):
    driver.get("https://www.amazon.com/-/zh/ap/signin")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email"))).send_keys(email)
    driver.find_element(By.ID, "continue").click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password"))).send_keys(password)
    driver.find_element(By.ID, "signInSubmit").click()

    # 等待主页加载
    # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "nav-link-accountList")))

    # 保存Cookies
    save_cookies(driver, cookies_file)


def get_reviews_selenium_with_cookies(URL, cookies_file, star_rating, product_url, max_reviews=10000):
    reviews = []
    chrome_driver_path = "chromedriver.exe"  # 替换为你的 ChromeDriver 路径
    driver = webdriver.Chrome(executable_path=chrome_driver_path)

    try:
        driver.get("https://www.amazon.com")
        time.sleep(30)
        load_cookies(driver, cookies_file)
        driver.get(URL)

        product_link = driver.find_element(By.CSS_SELECTOR, 'a[data-hook="product-link"]')
        product_link.click()
        product_title = driver.find_element(By.ID, 'productTitle').text
        whole_price = driver.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
        fraction_price = driver.find_element(By.CSS_SELECTOR, 'span.a-price-fraction').text
        full_price = whole_price + '.' + fraction_price
        combined_text = ''
        try:
            ul_element = driver.find_element(By.CSS_SELECTOR, 'ul.a-unordered-list.a-vertical.a-spacing-mini')
            span_elements = ul_element.find_elements(By.TAG_NAME, 'span')
            span_texts = [span.text for span in span_elements]
            combined_text = ' '.join(span_texts)
        except Exception as e:
            print('no description')

        div_element = driver.find_element(By.ID, 'averageCustomerReviews_feature_div')
        a_element = div_element.find_element(By.CSS_SELECTOR, 'a.a-popover-trigger.a-declarative')
        a_text = a_element.text
        aa_text = a_text + 'out of 5 stars'

        number_of_reviews = driver.find_element(By.ID, 'acrCustomerReviewText').text
        combined_text1 = ''
        try:
            climate_pledge_friendly_element = driver.find_element(By.ID, 'climatePledgeFriendly')
            a_section_elements = climate_pledge_friendly_element.find_elements(By.CSS_SELECTOR, '.a-section.a-spacing-base')
            combined_text1 = ' '.join([element.text for element in a_section_elements])
        except Exception as e:
            print('no sustainability_features')
        driver.back()
        # 根据星级选择不同的CSS选择器
        star_filter = f'filterByStar={star_rating}_star'
        star_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'a[href*="{star_filter}"]'))
        )
        star_link.click()
        page = 1

        while len(reviews) < max_reviews:
            # 等待评论加载完成
            time.sleep(randint(0, 5))
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="reviews-content"]'))
            # )

            # 解析评论
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_divs = soup.find_all('ul', class_='a-unordered-list a-nostyle a-vertical')[0]
            review_divs_list = review_divs.find_all('li', {'data-hook': 'review'})

            for div in review_divs_list:
                review = {}
                review['url'] = URL
                start = URL.split('product-reviews/')[1]  # 获取 'B0007VJMM4/ref=cm_cr_dp_d_show_all_btm...'
                asin = start.split('/')[0]
                review['product_id'] = asin
                review['name'] = product_title
                review['product_page_url'] = product_url
                review['price'] = full_price
                review['description'] = combined_text
                review['sustainability_features'] = combined_text1
                review['rating_x'] = aa_text
                review['number_of_reviews'] = number_of_reviews
                review['rating_y'] = f'{star_rating}_star'
                # if 'rating' in review and review['rating'] != '无评分':
                #     review['rating'] = f"{review['rating'].split()[0]} out of 5 stars"
                review['author'] = div.find('span', {'class': 'a-profile-name'}).text.strip() if div.find('span', {
                    'class': 'a-profile-name'}) else '无作者'
                review['date'] = div.find('span', {'data-hook': 'review-date'}).text.strip() if div.find('span', {
                    'data-hook': 'review-date'}) else '无日期'
                review['content'] = div.find('span', {'data-hook': 'review-body'}).text.strip() if div.find('span', {
                    'data-hook': 'review-body'}) else '无内容'
                reviews.append(review)

                if len(reviews) >= max_reviews:
                    break

            print(f"{URL} 第 {page} 页评论爬取成功。")

            if len(review_divs) == 0 or len(reviews) >= max_reviews:
                break  # 如果当前页面没有评论或者已经获取到足够的评论，停止爬取

            page += 1  # 下一页

            # 点击“下一页”按钮
            try:
                time.sleep(randint(0, 10))
                next_button = driver.find_element(By.CSS_SELECTOR, 'li.a-last > a')
                next_button.click()
            except Exception as e:
                print(f"未找到下一页按钮，爬取结束: {e}")
                break

            time.sleep(3)  # 等待加载新页面

        print(f"{URL} 爬取了 {len(reviews)} 条评论。")

    except Exception as e:
        print(f"爬取 {URL} 出错: {e}")

    driver.quit()
    return reviews[:max_reviews]


def get_reviews_url(product_url):
    product_id = product_url.split('/dp/')[1].split('/')[0]
    return f"https://www.amazon.com/product-reviews/{product_id}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews&language=en_US"


def get_txt_files_from_directory(directory):
    txt_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))
    return txt_files


# 主函数逻辑
def main():
    # 读取product links文件夹下所有子文件夹中的txt文件
    directory = r'C:\Users\LENOVOT\Desktop\data-analysis\666\Product Links2\Product Links\new'
    txt_files = get_txt_files_from_directory(directory)

    # 亚马逊登录信息
    email = "zng@ucsd.edu"
    password = "zng^dN08:amazon"
    cookies_file = "amazon_cookies.pkl"

    # 检查是否已有Cookies文件
    if not os.path.exists(cookies_file):
        chrome_driver_path = "chromedriver.exe"
        driver = webdriver.Chrome(executable_path=chrome_driver_path)
        amazon_login_and_save_cookies(driver, email, password, cookies_file)
        driver.quit()

    # 遍历每个txt文件中的URL
    for txt_file in txt_files:
        all_reviews = []
        with open(txt_file, 'r') as file:
            urls = file.readlines()

        for url in urls:
            if url == '\n':
                continue
            url = url.strip()  # 去除首尾空格和换行符
            review_url_template = get_reviews_url(url)

            # 获取一星到五星评论
            for star in ['one', 'two', 'three', 'four', 'five']:
                print(f"正在获取 {star} 星评论: {url}")
                reviews = get_reviews_selenium_with_cookies(review_url_template, cookies_file, star, url)
                all_reviews.extend(reviews)

        # 获取txt文件的文件名并去掉扩展名
        base_name = os.path.splitext(os.path.basename(txt_file))[0]

        # 将评论信息写入对应的xlsx文件
        df = pd.DataFrame(all_reviews)
        output_file = f"{base_name}.xlsx"
        df.to_excel(output_file, index=False)
        print(f"评论信息已写入 {output_file} 文件。")


if __name__ == "__main__":
    main()
