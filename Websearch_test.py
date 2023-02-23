from time import sleep
from bs4 import BeautifulSoup
import requests
import pandas as pd
from flask import Flask, render_template, url_for, redirect, request

# python -m pip install pandas


app = Flask(__name__)

HEADERS = ({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'})


def get_soup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def getnextpage(soup):
    # this will return the next page URL
    pages = soup.find('div', {'class': 'a-form-actions a-spacing-top-extra-large'}).find('ul',
                                                                                         {'class': 'a-pagination'})
    if not pages.find('li', {'class': 'a-disabled a-last'}):
        url = 'https://www.amazon.in' + pages.find('li', {'class': 'a-last'}).find('a')['href']
        return url
    else:
        return ""


def get_soup_with_header(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


reviewlist = []


def get_reviews(soup):
    reviews = soup.find_all('div', {'data-hook': 'review'})
    try:
        for item in reviews:
            # review = {
            # 'title': item.find('a', {'data-hook': 'review-title'}).text.strip(),
            # 'rating':  float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()),
            # 'body': item.find('span', {'data-hook': 'review-body'}).text.strip(),
            # }
            review = []
            try:
                review = {
                    'body': item.find('span', {'data-hook': 'review-body'}).text.strip()
                }
                reviewlist.append(review)
            except:
                pass

    except:
        pass


@app.route('/main_func/<products>')
def main_func(products):
    product = products
    url = "https://www.amazon.in/s?k=" + product
    soup = get_soup_with_header(url)
    findlink = soup.find('div', {
        'class': 's-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16'})

    x = findlink.a
    nextPage = x.get("href")
    str = 'http://www.amazon.in' + nextPage
    # str = 'https://www.amazon.in/ORENAME-Umbrella-Polyester-Portable-Protection/dp/B095MVHBR7/ref
    # =pd_rhf_d_se_s_pd_sbs_rvi_sccl_1_2/257-6498795-2606201?pd_rd_w=NTMuZ&content-id=amzn1.sym.0d5f32d5-d8bf-40fc
    # -9298-1b7e0b0b5c8d&pf_rd_p=0d5f32d5-d8bf-40fc-9298-1b7e0b0b5c8d&pf_rd_r=YZ7X0PW2A8E3TV1KF2CE&pd_rd_wg=ay89e
    # &pd_rd_r=d824157a-90e4-4bbd-855c-1c59fb90465a&pd_rd_i=B095MXPSDQ&psc=1'
    next_soup = get_soup_with_header(str)
    links = next_soup.find('div', {'id': 'reviews-medley-footer'})
    final_link = "http://www.amazon.in" + links.a.get("href")
    # final_link = "http://www.amazon.in/Fitbit-Inspire-Fitness-Tracker-Included/product-reviews/B08DFGPTSK/ref
    # =cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"

    for x in range(1, 100):
        print(final_link)
        soup = get_soup_with_header(final_link)
        print(f'Getting page: {x}')
        get_reviews(soup)
        print(len(reviewlist))
        sleep(3)
        if not soup.find('li', {'class': 'a-disabled a-last'}):
            final_link = getnextpage(soup)
            if final_link == "":
                break
            pass
        else:
            break

    df = pd.DataFrame(reviewlist)
    df.to_csv('reviews.csv', index=False)
    return render_template("product.html", msg="success")


@app.route('/', methods=["POST", "GET"])
def call_to_scrapper():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == 'POST':
        products = request.form
        return redirect(url_for('main_func', products=products))


if __name__ == '__main__':
    app.run(debug=True)
