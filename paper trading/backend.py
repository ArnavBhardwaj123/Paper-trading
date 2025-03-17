from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import random

ALPACA_API_KEY = "PKWLDCKC8D50WZMIT2WL"
ALPACA_SECRET_KEY = "lMw97HeS9EmeLOOOsjE1eC1eb2TAXYa"
BASE_URL = "https://paper-api.alpaca.markets/v2"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

portfolio = {}

@app.get("/stock/{symbol}")
def get_stock_price(symbol: str):
    url = f"https://data.alpaca.markets/v2/stocks/quotes/latest?symbols={symbol}"
    headers = {"APCA-API-KEY-ID": ALPACA_API_KEY, "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if symbol in data:
            return {"symbol": symbol, "price": data[symbol]["ap"]}
    return {"error": "Invalid symbol"}

@app.post("/trade/")
def execute_trade(symbol: str, side: str, qty: int, stop_loss: float = None):
    market_price = get_stock_price(symbol).get("price", 0)
    
    if market_price == 0:
        return {"error": "Invalid stock symbol"}

    slippage = random.uniform(-0.2, 0.2)
    executed_price = round(market_price + slippage, 2)
    filled_qty = random.randint(qty // 2, qty)

    trade = {"symbol": symbol, "side": side, "qty": filled_qty, "price": executed_price, "stop_loss": stop_loss}
    if symbol not in portfolio:
        portfolio[symbol] = []
    portfolio[symbol].append(trade)

    return {"status": "Executed", "trade": trade}

@app.get("/pnl/{symbol}")
def calculate_pnl(symbol: str):
    if symbol not in portfolio:
        return {"error": "No trades found"}
    
    market_price = get_stock_price(symbol).get("price", 0)
    pnl = 0;
    
    for trade in portfolio[symbol]:
        if trade["side"] == "BUY":
            pnl += (market_price - trade["price"]) * trade["qty"]
        else:
            pnl += (trade["price"] - market_price) * trade["qty"]

    return {"symbol": symbol, "PnL": round(pnl, 2)}