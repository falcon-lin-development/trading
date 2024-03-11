import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print("Received data:", data)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

# Example WebSocket URL (this is a hypothetical example; use the appropriate URL for your data provider)
socket_url = "wss://example.com/marketdata"

ws = websocket.WebSocketApp(socket_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.on_open = on_open
ws.run_forever()
