import pika, sys, os, time, json
import threading
from main import Bingx, api
from setLogger import get_logger


logger = get_logger(__name__)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='bingx')

    def callback(ch, method, properties, body):
        try:
            print(f" [x] Received {body}")
            data = json.loads(body.decode('utf-8').replace("'",'"'))
            Bingx.position = data['symbol']
            #
            symbol = data['symbol']
            side = data['side']
            positionSide = data['positionSide']
            price = data['price']
            qty = data['qty']
            TP = data['TP']
            SL = data['SL']

            from main import triger_action
            triger_action(symbol=symbol, side=side, positionSide=positionSide, price=price, qty=qty, TP=TP, SL=SL)

        except Exception as e:
            logger.exception(f"{e}")

    channel.basic_consume(queue='bingx', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

threading.Thread(target=main).start()
threading.Thread(target=main).start()



