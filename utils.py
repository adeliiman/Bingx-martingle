from sqlalchemy.orm import Session
from models import Setting, UserSymbols
from datetime import datetime, timedelta
from setLogger import get_logger
import concurrent.futures
from main import Bingx, api
import time, asyncio, requests, schedule


logger = get_logger(__name__)





def get_user_params(db: Session):
    try:
        user = db.query(Setting).first()
        
        user_symbols = db.query(UserSymbols).all()
        
        Bingx.timeframe = user.timeframe
        Bingx.margin_mode = user.margin_mode
        Bingx.leverage = user.leverage
        Bingx.use_symbols = user.use_symbols

        Bingx.rsi_short = {}
        Bingx.rsi_long = {}
        
        
        Bingx.symbols = []
        
        for symbol in user_symbols:
            Bingx.symbols.append(symbol.symbol)
        
        if user.reset:
            Bingx.entry_rsi = []
            # Bingx.entry_time = 0
            Bingx.position = ''
            logger.info("reset rsi data.")
        #
        get_all_klines(Bingx.symbols)
            
    except Exception as e:
        logger.exception(msg="get_user_params" + str(e))



