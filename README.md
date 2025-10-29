### Country Currency & Exchange API
#### A RESTful API that fetches country data from an external API, stores it in a database, and provides CRUD operations.
#### Functionalities
- Fetch country data from: https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
- For each country, extract the currency code (e.g. NGN, USD, GBP).
- Then fetch the exchange rate from: https://open.er-api.com/v6/latest/USD
- Match each country's currency with its rate (e.g. NGN → 1600).
- Compute a field estimated_gdp = population × random(1000–2000) ÷ exchange_rate.
- Store or update everything in MySQL as cached data.
#### Endpoints
- POST /countries/refresh → Fetch all countries and exchange rates, then cache them in the database
- GET /countries → Get all countries from the DB (support filters and sorting) - ?region=Africa | ?currency=NGN | ?sort=gdp_desc
- GET /countries/:name → Get one country by name
- DELETE /countries/:name → Delete a country record
- GET /status → Show total countries and last refresh timestamp
- GET /countries/image → serve summary image

### SETUP
- git clone https://github.com/Abdulquyum/HNG13-Currency_Exchange_API.git #clone repo
- python3 -m venv hng_venv #create a virtual environ
- source hng_venv/Script/activate #gitbash #activate virtual environ
- pip3 install -r requirements.txt #install required dependencies
- cd country_currency_exchange #go into project folder
- chmod app.py
- ./app

#### open another terminal to test endpoints
### Testing endpoints locally
#### 1. Refresh countries data
curl -X POST http://localhost:3000/countries/refresh

#### 2. Get all countries
curl http://localhost:3000/countries

#### 3. Get countries with filters
curl "http://localhost:3000/countries?region=Europe"
curl "http://localhost:3000/countries?currency=EUR"
curl "http://localhost:3000/countries?sort=gdp_desc"

#### 4. Get specific country
curl http://localhost:3000/countries/France

#### 5. Get status
curl http://localhost:3000/status

#### 6. Get summary image
curl http://localhost:3000/countries/image -o summary.png

#### 7. Delete a country (example)
curl -X DELETE http://localhost:3000/countries/TestCountry

- ctrl+c #quite running server
- deactivate #exit virtual environ

### DEPLOYMENT
- sudo apt update -y
- git clone https://github.com/Abdulquyum/HNG13-Currency_Exchange_API.git #clone repo
- sudo apt install python3
- sudo apt install python3-pip
- pip3 install -r requirements.txt #install required dependencies
- sudo apt install mysql-server -y
- sudo mysql_secure_installation
- sudo mysql
- sudo apt install python3-pip python3-venv nginx git -y
#### In the MySQL prompt, create a database and user:
CREATE DATABASE your_database_name;
CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
EXIT;

- pip install mysqlclient
