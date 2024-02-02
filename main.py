import json, time, requests
from models import Signal
import concurrent.futures
from database import SessionLocal
from BingXApi_v2 import BingXApi
import random, schedule
import threading
from datetime import datetime
from database import SessionLocal


from setLogger import get_logger
logger = get_logger(__name__)


with open('config.json') as f:
    config = json.load(f)

api = BingXApi(APIKEY=config['api_key'], SECRETKEY=config['api_secret'], demo=False)


class BingX:
	bot: str = 'Stop' # 'Run'
	leverage: int 
	symbols: list = []
      

Bingx = BingX()


# def schedule_kline():
# 	second_ = time.gmtime().tm_sec
# 	min_ = time.gmtime().tm_min
# 	hour_ = time.gmtime().tm_hour


# def schedule_job():
# 	schedule.every(1).minutes.at(":02").do(schedule_kline)
# 	while True:
# 		if Bingx.bot == "Stop":
# 			schedule.clear()
# 			break
# 		schedule.run_pending()
# 		# print(time.ctime(time.time()))
# 		time.sleep(1)





def placeOrder(symbol, side, tradeType, positionSide, price, qty, leverage):
	res = api.setLeverage(symbol=symbol, side=positionSide, leverage=leverage)
	logger.info(f"set leverage---{symbol}--- {res}")

	# if side == "BUY":
	# 	TP = price * (1 + TP/100)
	# 	SL = price * (1 - SL/100)
	# else:
	# 	TP = price * (1 - TP/100)
	# 	SL = price * (1 + SL/100)
	# print(symbol, side, margin, Bingx.TP_percent, Bingx.SL_percent)
	# logger.info(f"{symbol}---{side}---{price}---{qty}")

	# take_profit = "{\"type\": \"TAKE_PROFIT_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (qty, TP, TP)
	# stop_loss = "{\"type\": \"STOP_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (qty, SL, SL)
	res = api.placeOrder(symbol=symbol, side=f"{side}", positionSide=f"{positionSide}", tradeType=tradeType, 
				quantity=qty, 
				# quoteOrderQty=margin,
				#takeProfit=take_profit,
				#stopLoss=stop_loss
				)
	logger.info(f"{res}")
	#
	from models import Signal
	signal = Signal()
	signal.symbol = symbol
	signal.side = side
	signal.price = price
	# signal.time = datetime.fromtimestamp(time_/1000)
	signal.time = datetime.now().strftime('%y-%m-%d %H:%M:%S')
	db = SessionLocal()
	db.add(signal)
	db.commit()
	db.close()
	logger.info(f"load to sqlite. {symbol}---{side}---{datetime.now().strftime('%y-%m-%d %H:%M:%S')}")


def place_order(symbol, side, price, qty, leverage, TP, SL):
	if side == "BUY":
		TP = price * (1 + TP/100)
		SL = price * (1 - SL/100)
		side = "SELL"
		positionSide = "LONG"
	else:
		TP = price * (1 - TP/100)
		SL = price * (1 + SL/100)
		side = "BUY"
		positionSide = "LONG"

	res = api.placeOrder(symbol=symbol, side=side,positionSide=positionSide, 
					  stopPrice=SL, price=price, quantity=qty, tradeType='STOP')
	logger.info(f"res")

	res = api.placeOrder(symbol=symbol, side=side,positionSide=positionSide, 
					  stopPrice=TP, price=price, quantity=qty, tradeType='TAKE_PROFIT')
	logger.info(f"res")
	
	# limit order
	res = api.placeOrder(symbol=symbol, side=side,positionSide=positionSide, 
					  stopPrice=SL, price=price, quantity=qty, tradeType='LIMIT')
	logger.info(f"res")