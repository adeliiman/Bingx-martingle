from sqlalchemy.orm import Session
from models import Setting, UserSymbols
from datetime import datetime, timedelta
from setLogger import get_logger
import concurrent.futures
from main import Bingx, api
import time, asyncio, requests, schedule


logger = get_logger(__name__)


def init_orders():
    def init_order(items):
        symbol = items[0]
        position_side = items[1]
        price = api.getLatestPrice(symbol=symbol)
        price = float(price['data']['price'])

        side = "SELL" if position_side == "SHORT" else "BUY"
        qty = (Bingx.trade_value * Bingx.leverage) / price
        
        from main import placeOrders
        
        placeOrders(symbol=symbol, side=side, tradeType="MARKET", positionSide=position_side, 
                    price=price, qty=qty, leverage=Bingx.leverage)

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        items = [(sym[0], sym[1]) for sym in Bingx.symbols]
        executor.map(init_order, items)
    logger.info("init all orders done.")


def get_user_params(db: Session):
    try:
        user = db.query(Setting).first()
        user_symbols = db.query(UserSymbols).all()

        Bingx.leverage = user.leverage
        Bingx.TP_percent = user.TP_percent
        Bingx.SL_percent = user.SL_percent
        Bingx.trade_value = user.trade_value
        
        Bingx.symbols = []
        for symbol in user_symbols:
            Bingx.symbols.append((symbol.symbol, symbol.position_side))

            
    except Exception as e:
        logger.exception(msg="get_user_params" + str(e))



