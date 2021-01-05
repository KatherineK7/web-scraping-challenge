# %%
# Import dependencies

import pandas as pd
import pymongo
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
# %%
# Configure ChromeDriver
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path)

# %%
# # Insert into Mongo DB

def scrape_all():

    # Populate variables from the functions
    news_title, news_p = mars_news()
    featured_img_url = featured_image()
    mars_facts_html = mars_facts()
    

    # Assemble the document to insert into the database
    nasa_document = {
        'news_title': news_title,
        'news_paragraph': news_p,
        'featured_img_url': featured_img_url,
        'mars_facts_html': mars_facts_html,
    }

    # consider closing browser here
    browser.quit()

    return nasa_document

# %%
# # NASA Mars News

def mars_news():
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')

    article_container = news_soup.find('ul', class_='item_list')

    headline_date = article_container.find('div', class_='list_date').text
    news_title = article_container.find('div', class_='content_title').find('a').text
    news_p = article_container.find('div', class_='article_teaser_body').text

    return news_title, news_p
# %%
# # JPL Mars Space Images - Featured Image

def featured_image():
    base_url = 'https://www.jpl.nasa.gov'

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Method 1: parsing through the style attribute in the article tag
    try:
        img_elem = img_soup.find('article', class_='carousel_item')['style']
        img_rel_url = img_elem.replace("background-image: url('", '')
        img_rel_url = img_rel_url.replace("');", '')
        #print(img_rel_url)
    except Exception as e:
        print(e)

    # Method 2: clicking the FULL TEXT button and pulling the image
    try:
        full_image_elem = browser.find_by_id('full_image')[0]
        full_image_elem.click()

        html = browser.html
        img_soup = BeautifulSoup(html, 'html.parser')

        img_rel_url = img_soup.find('img', class_='fancybox-image')['src']
        #print(img_rel_url)
    except Exception as e:
        print(e)

    featured_image_url  = f'{base_url}{img_rel_url}'
    print(featured_image_url)
    
    return featured_image_url


# %%
# # Mars Facts

def mars_facts():
    url = 'https://space-facts.com/mars/'
    browser.visit(url)

    mars_facts_df = pd.read_html(url)
    mars_facts_df = mars_facts_df[0]
    mars_facts_df.columns = ['Description', 'Mars']
    mars_facts_df

    mars_facts_html = mars_facts_df.to_html(classes='table table-striped', index=False, border=0)
    
    return mars_facts_html
# %%
# # Mars Hemispheres

def mars_hemispheres():

    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    html = browser.html
    hem_soup = BeautifulSoup(html, 'html.parser')
    
    #Finding hemisphere names and saving them to a list
    
    titles = []
    results = hem_soup.find_all('div', class_="collapsible results")
    hemispheres = results[0].find_all('h3')

    for title in hemispheres:
        titles.append(title.text)
        
    #Finding links to click and creating a list to iterate through
    
        thumbnail_results = results[0].find_all('a')
    
        thumbnail_links = []
    
    for thumbnail in thumbnail_results:
    
        if (thumbnail.img):
        
            thumbnail_url = 'https://astrogeology.usgs.gov/' + thumbnail['href']
        
        
        thumbnail_links.append(thumbnail_url)

        thumbnail_links

    full_imgs = []

    for url in thumbnail_links:
    
   
        browser.visit(url)

        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
    
   
        results = soup.find_all('img', class_='wide-image')
        relative_img_path = results[0]['src']
    
    
        img_link = 'https://astrogeology.usgs.gov/' + relative_img_path
    
    
        full_imgs.append(img_link)

        full_imgs

# Zip together the list of hemisphere names and hemisphere image links
    mars_hemi_zip = zip(titles, full_imgs)

    hemisphere_image_urls = []

# Iterate through the zipped object
    for title, img in mars_hemi_zip:
    
        mars_hemisphere_dict = {}
    
   
        mars_hemisphere_dict['title'] = title
    

        mars_hemisphere_dict['img_url'] = img
       
   
        hemisphere_image_urls.append(mars_hemisphere_dict)

    return hemisphere_image_urls


# %%
# Run Script

if __name__ == '__main__':
    scrape_all()