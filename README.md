# Project Title

Digital Wallet as name is suggests is a medium for admin/retailer(devices)/customer to interact and transfer money via their cards.
A user can signup as Admin/customer/Retailer


## Description


- Admin can transfer money to customer
- Admin can view all the customers and retailers
- Admin can deactivate any customer or retailer

- Customer can view their balance/transactions history
- Customer can transfer money to another customer
- Customer can transfer money to any device

- Retailer can add device
- Retailer can Generate Apikey for his device
- Retailer can deactivate his device

## Getting Started


### Installing
git clone https://github.com/Mansi-Chauhan27/Digital-Wallet.git

Inside requirements folder:
pip install -r base.txt

Set Up .env File inside config folder with keys:
SECRET_KEY=
SENDGRID_KEY=
SENDER_EMAIL=

Create logs folder at the root level

### Executing program

Inside digitalwallet folder:

1. python manage.py runserver
2. python manage.py migrate
3. (if error in previos step)python manage.py migrate --run-syncdb
4. python manage.py migrate
<!-- TO LOAD Data -->
5. python manage.py loaddata fixtures/sample_data.json   

