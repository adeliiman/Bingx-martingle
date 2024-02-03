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

api = BingXApi(APIKEY=config['api_key'], SECRETKEY=config['api_secret'], demo=True)


class BingX:
	bot: str = 'Stop' # 'Run'
	leverage: int 
	TP_percent: float
	SL_percent: float
	trade_value: int
	symbols: list = []
      

Bingx = BingX()




def placeOrders(symbol, side, tradeType, positionSide, price, qty, leverage):
	res = api.setLeverage(symbol=symbol, side=positionSide, leverage=leverage)
	logger.info(f"set leverage---{symbol}--- {res}")

	if positionSide == "LONG":
		TP = price * (1 + Bingx.TP_percent/100)
		SL = price * (1 - Bingx.SL_percent/100)
	else:
		TP = price * (1 - Bingx.TP_percent/100)
		SL = price * (1 + Bingx.SL_percent/100)

	take_profit = "{\"type\": \"TAKE_PROFIT_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (qty, TP, TP)
	stop_loss = "{\"type\": \"STOP_MARKET\", \"quantity\": %s,\"stopPrice\": %s,\"price\": %s,\"workingType\":\"MARK_PRICE\"}"% (qty, SL, SL)
	res = api.placeOrder(symbol=symbol, side=f"{side}", positionSide=f"{positionSide}", tradeType=tradeType, 
				quantity=qty, 
				# quoteOrderQty=margin,
				takeProfit=take_profit,
				stopLoss=stop_loss
				)
	logger.info(f"{res}")
	# trigger limit orders
	res = api.placeOrder(symbol=symbol, side=side, positionSide=positionSide, price=TP, stopPrice=TP, quantity=qty, 
                     tradeType='TRIGGER_LIMIT')
	logger.info(f"{res}")
	# 
	side = "SELL" if side == "BUY" else "BUY"
	positionSide = "SHORT" if positionSide == "LONG" else "LONG"
	res = api.placeOrder(symbol=symbol, side=side, positionSide=positionSide, price=SL, stopPrice=SL, quantity=2*qty, 
                     tradeType='TRIGGER_LIMIT')
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


def place_tp_sl_limit(symbol, side, positionSide, price, qty):
	if positionSide == "LONG":
		TP = price * (1 + Bingx.TP_percent/100)
		SL = price * (1 - Bingx.SL_percent/100)
		side = "SELL"
	else:
		TP = price * (1 - Bingx.TP_percent/100)
		SL = price * (1 + Bingx.SL_percent/100)
		side = "BUY"

	res = api.placeOrder(symbol=symbol, side=side, positionSide=positionSide, 
					  stopPrice=SL, price=SL, quantity=qty, tradeType='STOP')
	logger.info(f"{res}")

	res = api.placeOrder(symbol=symbol, side=side, positionSide=positionSide, 
					  stopPrice=TP, price=TP, quantity=qty, tradeType='TAKE_PROFIT')
	logger.info(f"{res}")
	
	# trigger limit orders
	side = "SELL" if positionSide == "SHORT" else "BUY"
	res = api.placeOrder(symbol=symbol, side=side, positionSide=positionSide, price=TP, stopPrice=TP, quantity=qty, 
                     tradeType='TRIGGER_LIMIT')
	logger.info(f"{res}")
	# 
	positionSide = "SHORT" if positionSide == "LONG" else "LONG"
	side = "SELL" if positionSide == "SHORT" else "BUY"
	res = api.placeOrder(symbol=symbol, side=side, positionSide=positionSide, price=SL, stopPrice=SL, quantity=2*qty, 
                     tradeType='TRIGGER_LIMIT')
	logger.info(f"{res}")


def triger_action(symbol, side, positionSide, price, qty):
	res = api.closeOrders(symbol=symbol)
	logger.info(f"{res}")
	place_tp_sl_limit(symbol, side, positionSide, price, qty)
	