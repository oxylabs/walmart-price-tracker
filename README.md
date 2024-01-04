# How to Build Walmart Price Tracker With Python
Follow this guide to learn how to track prices and availability of your desired Walmart products, and how to set up email alerts with the latest product and price change data.

See the [full blog post](https://oxylabs.io/blog/walmart-price-tracker) for comprehensive explanations about each step.

## 1. Install libraries
```bash
pip install requests
```
Next, you’ll have to create an Oxylabs account to get the necessary credentials for the Walmart Scraper API. Register on the [Oxylabs dashboard](https://dashboard.oxylabs.io/) and claim a **1-week free trial**.

## 2. Import libraries

```python
import json
import smtplib
from email.message import EmailMessage
from pprint import pprint
import requests
```

## 3. Inspect elements to prepare XPaths

### Title

```xml
//div[@role='group']//span[@data-automation-id='product-title']
```

### Price
```xml
//div[@role='group']//div[@data-automation-id='product-price']//span[@class='w_iUH7'][1]
```

### Product link
```xml
//div[@role='group']//a/@href
```


## 4. Fetch Walmart category data
### Set API credentials
```python
username, password = "USERNAME", "PASSWORD"
```
Replace `PASSWORD` and `USERNAME` with your API credentials. 


### Prepare parsing instructions
```python
parsing_instructions = {
   "titles": {
       "_fns": [
           {
               "_fn": "xpath",
               "_args": [
                   "//div[@role='group']//span[@data-automation-id='product-title']/text()"
               ],
           }
       ]
   },
   "links": {
       "_fns": [
           {
               "_fn": "xpath",
               "_args": ["//div[@role='group']//a/@href"],
           }
       ]
   },
   "prices": {
       "_fns": [
           {
               "_fn": "xpath",
               "_args": [
                   "//div[@role='group']//div[@data-automation-id='product-price']//span[@class='w_iUH7'][1]/text()"
               ],
           },
           {"_fn": "amount_from_string"},
       ]
   },
}
```
Visit our [documentation](https://developers.oxylabs.io/scraper-apis/custom-parser/list-of-functions) to learn more about the available functions and how to use them.

### Prepare payload
```python
url = "https://www.walmart.com/cp/electronics/3944"


payload = {
   "source": "universal_ecommerce",
   "url": url,
   "parse": True,
   "parsing_instructions": parsing_instructions,
}
```

### Send a POST request
```python
response = requests.post(
   "https://realtime.oxylabs.io/v1/queries", auth=(username, password), json=payload
)
print(response.status_code)
pprint(response.json())
```

## 5. Track Walmart’s price history
### Load history data
```python
history = {}


try:
   with open("walmart_data.json", "r") as f:
       history = json.load(f)
except Exception as _:
   pass
```

### Track Walmart price changes and new products
```python
content = response.json()["results"][0]["content"]
price_changed = []
new_products = []
for title, price, link in zip(content["titles"], content["prices"], content["links"]):
   product = {"title": title, "price": price, "link": link}
   if link not in history:
       new_products.append(product)
   elif history[link]["price"] != price:
       product["old_price"] = history[link]["price"]
       price_changed.append(product)
   history[link] = product
```

### Save history data
```python
with open("walmart_data.json", "w") as f:
   f.write(json.dumps(history))
```

## 6. Create a price alert
### Configuration
```python
# config
SMTP_SERVER, SMTP_PORT = "SERVER_ADDRESS", "SERVER_PORT"
email, email_password, destination_email = "from@email", "from_email_pass", "to@email"
```

As you can guess, you’ll have to replace these configs with appropriate data. For example, if you are using a Gmail account for sending email, you’ll have to set the `SERVER_ADDRESS` as `smtp.gmail.com` and `SERVER_PORT` must be set to `587`. `from@email` and `from_email_pass` should be set as per your sender email. Last but not least, `to@email` will be replaced with the receiver of the email notification. 

To generate an app password for Gmail, you can do the following: 

- Go to your [Google account](https://myaccount.google.com/)
- Select Security
- Select 2-Step Verification under "Signing in to Google"
- Select App passwords at the bottom of the page
- Enter a name to help you remember where you'll use the app password
- Select Generate
- Copy and save the generated password

For more details, check out [Google's support documentation](https://support.google.com/mail/answer/185833?hl=en).

### Compose email
```python
body = f"""Price Changed:
{json.dumps(price_changed, indent=2)}
New products:
{json.dumps(new_products, indent=2)}
"""
msg = EmailMessage()
msg.set_content(body)
msg["subject"] = "Walmart Price Tracking alert"
msg["to"] = destination_email
msg["from"] = email
```

### Send email
```python
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(email, email_password)
server.send_message(msg)
server.quit()
```

## 7. Full source code
```python
import json
import smtplib
from email.message import EmailMessage
from pprint import pprint
import requests


username, password = "USERNAME", "PASSWORD"

history = {}


try:
   with open("walmart_data.json", "r") as f:
       history = json.load(f)
except Exception as _:
   pass

url = "https://www.walmart.com/cp/electronics/3944"

parsing_instructions = {
   "titles": {
       "_fns": [
           {
               "_fn": "xpath",
               "_args": [
                   "//div[@role='group']//span[@data-automation-id='product-title']/text()"
               ],
           }
       ]
   },
   "links": {
       "_fns": [
           {
               "_fn": "xpath",
               "_args": ["//div[@role='group']//a/@href"],
           }
       ]
   },
   "prices": {
       "_fns": [
           {
               "_fn": "xpath",
               "_args": [
                   "//div[@role='group']//div[@data-automation-id='product-price']//span[@class='w_iUH7'][1]/text()"
               ],
           },
           {"_fn": "amount_from_string"},
       ]
   },
}

payload = {
   "source": "universal_ecommerce",
   "url": url,
   "parse": True,
   "parsing_instructions": parsing_instructions,
}

response = requests.post(
   "https://realtime.oxylabs.io/v1/queries", auth=(username, password), json=payload
)

print(response.status_code)
pprint(response.json())
content = response.json()["results"][0]["content"]
price_changed = []
new_products = []
for title, price, link in zip(content["titles"], content["prices"], content["links"]):
   product = {"title": title, "price": price, "link": link}
   if link not in history:
       new_products.append(product)
   elif history[link]["price"] != price:
       product["old_price"] = history[link]["price"]
       price_changed.append(product)
   history[link] = product
   print(product)
with open("walmart_data.json", "w") as f:
   f.write(json.dumps(history))
# Send email alert
SMTP_SERVER, SMTP_PORT = "SERVER_ADDRESS", "SERVER_PORT"
email, email_password, destination_email = "from@email", "from_email_pass", "to@email"
body = f"""Price Changed:
{json.dumps(price_changed, indent=2)}
New products:
{json.dumps(new_products, indent=2)}
"""
msg = EmailMessage()
msg.set_content(body)
msg["subject"] = "Walmart Price Tracking alert"
msg["to"] = destination_email
msg["from"] = email
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(email, email_password)
server.send_message(msg)
server.quit()
```

