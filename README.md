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

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10

### Installing
Inside requirements folder:
pip install -r base.txt

### Executing program

Inside digitalwallet folder:

To load initial data:
python manage.py loaddata fixtures/sample_data.json
To Run Server:
python manage.py tunserver

