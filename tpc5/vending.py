#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

STOCK_FILE = Path(__file__).with_name("stock.json")

ACCEPTED_COINS = {
    "2e": 200, "1e": 100,
    "50c": 50, "20c": 20, "10c": 10, "5c": 5, "2c": 2, "1c": 1
}
CHANGE_ORDER = [200, 100, 50, 20, 10, 5, 2, 1]  # greedy change

def euro(cents: int) -> str:
    return f"{cents//100}.{cents%100:02d}€"

def load_stock():
    if STOCK_FILE.exists():
        return json.loads(STOCK_FILE.read_text(encoding="utf-8"))
    # tiny fallback if file is missing
    return [
        {"code": "A1", "name": "Water",     "qty": 5, "price": 80},
        {"code": "A2", "name": "Coca-Cola", "qty": 4, "price": 130},
        {"code": "B1", "name": "Snack",     "qty": 6, "price": 95}
    ]

def save_stock(stock):
    STOCK_FILE.write_text(json.dumps(stock, indent=2, ensure_ascii=False), encoding="utf-8")

def list_products(stock):
    print("vm: Product list")
    print("code | name          | quantity | price")
    print("----------------------------------------")
    for p in stock:
        print(f"{p['code']:>3} | {p['name']:<13} | {p['qty']:>8} | {euro(p['price'])}")
    print("----------------------------------------")

def find_product(stock, code):
    code = code.upper()
    for p in stock:
        if p["code"].upper() == code:
            return p
    return None

def parse_coins(args):
    total = 0
    bad = []
    tokens = " ".join(args).replace(" ", "").split(",")
    for t in filter(None, tokens):
        v = ACCEPTED_COINS.get(t.lower())
        if v is None:
            bad.append(t)
        else:
            total += v
    return total, bad

def make_change(cents):
    change = []
    left = cents
    for v in CHANGE_ORDER:
        if left <= 0:
            break
        n = left // v
        if n:
            change.append((v, n))
            left -= n * v
    return change, left

def fmt_change_list(change):
    parts = []
    for v, n in change:
        parts.append(f"{n}x {v//100}e" if v >= 100 else f"{n}x {v}c")
    return ", ".join(parts) if parts else "(no change)"

def main():
    stock = load_stock()
    balance = 0
    print("vm: welcome. Type 'LIST' to see products, 'EXIT' to finish.")
    while True:
        try:
            line = input(">> ").strip()
        except EOFError:
            print()
            line = "EXIT"
        if not line:
            continue
        parts = line.split()
        cmd, args = parts[0].upper(), parts[1:]

        if cmd == "LIST":
            list_products(stock)

        elif cmd == "COIN":
            if not args:
                print("vm: Use 'COIN <list>' e.g., COIN 1e, 50c")
                continue
            inc, bad = parse_coins(args)
            if bad:
                print("vm: coin(s) not accepted: " + ", ".join(bad))
            balance += inc
            print(f"vm: balance = {euro(balance)}")

        elif cmd == "SELECT":
            if not args:
                print("vm: Use 'SELECT <code>'")
                continue
            p = find_product(stock, args[0])
            if not p:
                print("vm: Invalid code. Use LIST to see products.")
                continue
            if p["qty"] <= 0:
                print(f"vm: Out of stock ({p['name']}).")
                continue
            if balance < p["price"]:
                missing = p["price"] - balance
                print(f"vm: Not enough balance for {p['name']} ({euro(p['price'])}). Missing {euro(missing)}.")
                continue
            p["qty"] -= 1
            balance -= p["price"]
            print(f"vm: Please take your product: {p['name']} ({euro(p['price'])}).")
            print(f"vm: balance = {euro(balance)}")

        elif cmd == "RESTOCK":
            if len(args) != 2:
                print("vm: Use 'RESTOCK <code> <qty>'")
                continue
            p = find_product(stock, args[0])
            if not p:
                print("vm: Invalid code.")
                continue
            try:
                qty = int(args[1])
            except ValueError:
                print("vm: invalid quantity.")
                continue
            p["qty"] += qty
            print(f"vm: {p['name']} updated. New quantity = {p['qty']}")

        elif cmd == "EXIT":
            if balance > 0:
                change, rem = make_change(balance)
                print(f"vm: change = {euro(balance)} -> {fmt_change_list(change)}")
                if rem:
                    print(f"vm: warning: couldn't return {euro(rem)}.")
            else:
                print("vm: no change.")
            save_stock(stock)
            print("vm: bye.")
            break

        elif cmd in ("HELP", "?"):
            print("Commands: LIST | COIN <list> | SELECT <code> | RESTOCK <code> <qty> | EXIT")

        else:
            print("vm: unknown command. Type HELP for help.")

if __name__ == "__main__":
    main()
