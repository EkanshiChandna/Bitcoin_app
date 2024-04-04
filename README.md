# MSD_bitcoin_app
Homework for MSD interview

# Bitcoin Price Microservice

A microservice that provides Bitcoin (BTC) price information in EUR and CZK. It also takes into account the calculated daily and monthly averages based on the data stored in the database. The data is updated every 5 minutes and maintains a 12-month retention policy for the stored data.

# Features Implemented #

- Real-time retrieval of Bitcoin price in EUR and CZK.
- Daily and monthly average price calculations based on local data storage.
- Data storage with a minimum cadence of 1 request every 5 minutes.
- Data retention limited to 12 months to optimize storage and performance.
- JSON formatted output including price information, currency, client request time, and server data time.
- Containerization of the microservice for ease of deployment and scalability.

# Prerequisites #

- Docker for running the containerized microservice.
- Basic knowledge of how to use Docker and run Docker commands.

# Getting Started #

To get the microservice up and running on your local machine, follow these steps:

1. Clone the repository:
   bash git clone https://github.com/EkanshiChandna/MSD_bitcoin_app.git

2. Navigate to the project directory:
   cd bitcoin-price-microservice

3. Building a docker image
   docker build -t bitcoin_app .

4. Run the docker image
   docker run -p bitcoin-price-microservice

# Further Steps (to be done) #
1. Introducing API keys or OAuth for secure access to the microservice.
2. While containerization has been achieved, a comprehensive Kubernetes deployment using Helm charts is yet to be achieved.

 
