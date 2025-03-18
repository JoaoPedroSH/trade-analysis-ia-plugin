import websockets
import asyncio
import json
import MetaTrader5 as mt5
from cryptography.fernet import Fernet
import os
from pathlib import Path

# Configurações
CONFIG_DIR = Path(os.getenv("APPDATA")) / "TradingApp"
CONFIG_FILE = CONFIG_DIR / "config.enc"
KEY_FILE = CONFIG_DIR / "key.key"

# Carrega configurações criptografadas
def load_config():
    if not CONFIG_FILE.exists():
        return None

    with open(KEY_FILE, "rb") as f:
        key = f.read()
    with open(CONFIG_FILE, "rb") as f:
        encrypted_data = f.read()

    cipher = Fernet(key)
    return json.loads(cipher.decrypt(encrypted_data).decode())

async def connect_to_api():
    config = load_config()
    if not config:
        print("Configure o aplicativo primeiro!")
        return

    user_id = config["user_id"]
    token = config["token"]

    while True:
        try:
            async with websockets.connect(
                f"ws://localhost:8000/ws/{user_id}",
                extra_headers={"Authorization": f"Bearer {token}"}
            ) as websocket:
                print("Conectado à API!")
                await listen_for_orders(websocket)
        except Exception as e:
            print(f"Erro: {e}. Reconectando em 5s...")
            await asyncio.sleep(5)

async def listen_for_orders(websocket):
    try:
        async for message in websocket:
            order = json.loads(message)
            execute_order(order)
    except websockets.exceptions.ConnectionClosed:
        print("Conexão perdida.")

def execute_order(order):
    try:
        if not mt5.initialize():
            print("Falha ao conectar ao MT5")
            return

        symbol = order["symbol"]
        volume = order["volume"]
        action = order["action"]

        if action == "buy":
            trade_type = mt5.ORDER_TYPE_BUY
            price = mt5.symbol_info_tick(symbol).ask
        else:
            trade_type = mt5.ORDER_TYPE_SELL
            price = mt5.symbol_info_tick(symbol).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": trade_type,
            "price": price,
            "deviation": 20,
            "magic": 123456,
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Erro na ordem: {result.comment}")
        else:
            print(f"Ordem executada: {result.order}")

    except Exception as e:
        print(f"Erro ao executar ordem: {e}")
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(connect_to_api())
