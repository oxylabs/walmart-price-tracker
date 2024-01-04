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
