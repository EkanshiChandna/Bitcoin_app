from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
from sqlalchemy import func
import pytz
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bitcoin_prices.db'
db = SQLAlchemy(app)


class BitcoinPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    price_eur = db.Column(db.Float)
    price_czk = db.Column(db.Float)


def fetch_and_store_bitcoin_prices():
    url_to_fetch_btc_prices = "https://api.coingecko.com/api/v3/simple/price"
    params = {'ids': 'bitcoin', 'vs_currencies': 'eur,czk'}
    response = requests.get(url_to_fetch_btc_prices, params=params)
    data = response.json()['bitcoin']
    price_record = BitcoinPrice(
        price_eur=data['eur'],
        price_czk=data['czk'],
        timestamp=datetime.utcnow()
    )

    db.session.add(price_record)
    db.session.commit()
    return {
        'price_eur': data['eur'],
        'price_czk': data['czk'],
        'server_timestamp': datetime.utcnow().replace(tzinfo=pytz.utc).isoformat()
    }


def delete_old_records():
    records_older_than_twelve_months = datetime.utcnow() - timedelta(days=365)
    BitcoinPrice.query.filter(BitcoinPrice.timestamp < records_older_than_twelve_months).delete()
    db.session.commit()


@app.route('/btc-price', methods=['GET'])
def btc_price():
    try:
        latest_price_record = fetch_and_store_bitcoin_prices()

        # Client request's time in ISO format, assuming UTC
        client_request_time = datetime.now(pytz.utc).isoformat()

        response = {
            'BTC_EUR': latest_price_record['price_eur'],
            'BTC_CZK': latest_price_record['price_czk'],
            'currency': '1 BTC',
            'client_request_time': client_request_time,
            'server_data_time': latest_price_record['server_timestamp'],
        }

        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/btc/current', methods=['GET'])
def current_price():
    latest_price = BitcoinPrice.query.order_by(BitcoinPrice.timestamp.desc()).first()
    if latest_price:
        return jsonify({
            'timestamp': latest_price.timestamp.isoformat(),
            'BTC_EUR': latest_price.price_eur,
            'BTC_CZK': latest_price.price_czk
        })
    else:
        return jsonify({'error': 'No price data available'}), 404


@app.route('/btc/averages/daily', methods=['GET'])
def daily_averages():

    # to calculate the daily average of the bitcoin prices #
    averages = db.session.query(
        func.date(BitcoinPrice.timestamp).label('day'),
        func.avg(BitcoinPrice.price_eur).label('avg_price_eur'),
        func.avg(BitcoinPrice.price_czk).label('avg_price_czk')
    ).group_by(func.date(BitcoinPrice.timestamp)).all()

    result = [{'day': day.isoformat(), 'avg_price_eur': avg_price_eur, 'avg_price_czk': avg_price_czk} for day, avg_price_eur, avg_price_czk in averages]
    return jsonify(result)


@app.route('/btc/averages/monthly', methods=['GET'])
def monthly_averages():
    # to calculate the monthly avg of prices by grouping the months #
    averages = db.session.query(
        func.strftime('%Y-%m', BitcoinPrice.timestamp).label('month'),
        func.avg(BitcoinPrice.price_eur).label('avg_price_eur'),
        func.avg(BitcoinPrice.price_czk).label('avg_price_czk')
    ).group_by(func.strftime('%Y-%m', BitcoinPrice.timestamp)).all()

    result = [{'month': month, 'avg_price_eur': avg_price_eur, 'avg_price_czk': avg_price_czk} for month, avg_price_eur, avg_price_czk in averages]
    return jsonify(result)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
    scheduler = BackgroundScheduler()
    scheduler.add_job(fetch_and_store_bitcoin_prices, 'interval', minutes=5)
    scheduler.add_job(delete_old_records, 'cron', day_of_week='mon-sun', hour=2)
    scheduler.start()
    app.run(debug=True)
