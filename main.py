from bs4 import BeautifulSoup
import requests
import smtplib
import lxml
import pandas

# email vars
EMAIL = ''
PASSWORD = ''


def get_price(url):
    # http://myhttpheader.com/
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; '
                                                        'rv:86.0) Gecko/20100101 Firefox/86.0',
                                          'Accept-Language': 'en-US,en;q=0.5'})
    soup = BeautifulSoup(response.text, 'lxml')

    check_id = soup.find(id='priceblock_ourprice')

    if check_id is None:
        price = soup.find('span', class_='a-size-medium a-color-price offer-price a-text-normal').get_text()
    else:
        price = soup.find(id='priceblock_ourprice').get_text()

    price_without_currency = price.split('£')[1]
    price_as_float = float(price_without_currency)
    return price_as_float


# File vars
file_path = 'product_data.csv'
data = pandas.read_csv(file_path)
products_dict = data.to_dict(orient="records")

change_of_price = False
email_message = ''

# check all products
for product in products_dict:
    new_price = get_price(product['url'])
    if new_price < product['price']:
        product['price'] = new_price
        email_message += f"{product['name']}: \n Current Price:{product['price']}\n Lowest Price: {product['lowest_price']} \n"
        if new_price < product['lowest_price']:
            product['lowest_price'] = new_price

# send email
if email_message != '':
    with smtplib.SMTP('smtp.gmail.com') as connection:
        # Secure connection
        connection.starttls()
        # Login
        connection.login(user=EMAIL, password=PASSWORD)
        # Send mail
        connection.sendmail(
            from_addr=EMAIL,
            to_addrs='harryez@yahoo.com',
            msg=f'Subject: Low Price Detected \n\n {email_message}')

print(email_message)

# store new data
new_products_df = pandas.DataFrame(products_dict)
new_products_df.to_csv('product_data.csv', index=False, header=True)