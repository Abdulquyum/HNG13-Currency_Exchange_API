### Country Currency & Exchange API
#### A nRESTful API that fetches country data from an external API, stores it in a database, and provides CRUD operations.
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