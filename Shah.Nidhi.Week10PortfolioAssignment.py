#Week 10 Portfolio Assignment
#8/15/2023
#Author: Nidhi Shah

"""
This portfolio assignment is a comprehensive code that will read data from local files and insert into db. In addition,
the code will utilize plotly to visualize the stock data in chart format. 

"""
import locale
import datetime
from datetime import date, datetime
import csv
import sqlite3
from sqlite3 import Error
import json
from collections import defaultdict
import plotly.graph_objects as go
import unittest

#Create stock class 
class Stock:
    def __init__(self, investorId, symbol, shares, purchasePrice, currentValue, purchaseDate):
        self.investorId = investorId
        self.symbol = symbol
        self.shares = shares
        self.purchasePrice = purchasePrice
        self.currentValue = currentValue
        self.purchaseDate = purchaseDate
       
    def calculateEaringsOrLossPerShare(value, price, shares):
        earningsOrLossPerShare = (value - price) * shares
        return earningsOrLossPerShare

    def calculatePercentage(value, price, date):
        increaseOrDecreasePercentage = (((value - price) / price) / ((today - date).days / 365)) * 100
        return increaseOrDecreasePercentage

#Create bond class
class Bond(Stock):
    def __init__(self, investorId, symbol, shares, purchasePrice, currentValue, purchaseDate, coupon, yeild):
        super().__init__(investorId, symbol, shares, purchasePrice, currentValue, purchaseDate)

        self.coupon = coupon
        self.yeild = yeild

#Create investor class
class Investor:
    def __init__(self, firstName, lastName, address, phoneNumber):
        self.firstName = firstName
        self.lastName = lastName
        self.address = address
        self.phoneNumber = phoneNumber
        self.stocks = []
        self.bonds = []

    def add_stock(self, symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id):
        stock = Stock(symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id)
        self.stocks.append(stock)

    def add_bond(self, symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id, coupon, yield_bond):
        bond = Bond(symbol, number_shares, purchase_price, current_cost, purchase_date, purchase_id, coupon, yield_bond)
        self.bonds.append(bond)

#create CSV file class 
class CSVDataFile:
    def __init__(self, fileName):
        self.fileName = fileName
        self.stockList = []
        self.bondList = []

    def readCSVFile(self):
        with open(self.fileName, 'r') as f:
            reader = csv.reader(f)
            next(reader)

            for row in reader:
                symbol = row[0]
                shares = float(row[1])
                price = float(row[2])
                value = float(row[3])
                date = str(row[4])
                self.stockList.append([symbol, shares, price, value, date])
   
    def getStockList(self):
        return self.stockList
    
    def readCSVBondFile(self): 
        with open(self.fileName, 'r') as f: 
            reader = csv.reader(f)
            next(reader)

            for row in reader: 
                symbol = row[0]
                shares = float(row[1])
                price = float(row[2])
                value = float(row[3])
                date = str(row[4])
                coupon = float(row[5])
                bondYield = float(row[6])
                self.bondList.append([symbol, shares, price, value, date, coupon, bondYield])

    def getBondList(self):
        return self.bondList

#create investor instance 
investor = Investor("Bob", "Smith", "3456 disney street", "454-099-0494")

#read stock file 
try:
    csvFile = CSVDataFile('Lesson6_Data_Stocks.csv')
    csvFile.readCSVFile()
except FileNotFoundError:
    print("File name does not exists in directory. Please try again with correct file name")

csvStockList = csvFile.getStockList()

#read bond file 
try:
    csvBondFile = CSVDataFile('Lesson6_Data_Bonds.csv')
    csvBondFile.readCSVBondFile()
except FileNotFoundError:
    print("File name does not exists in directory. Please try again with correct file name") 
csvBondList = csvBondFile.getBondList()

today = datetime.now()

#format earnings/loss into currency
locale.setlocale(locale.LC_ALL, '')
def format_currency(value):
    return locale.currency(value, grouping=True)

#DB set up 
connection_obj = sqlite3.connect('stocks.db', timeout=30)
cursor_obj = connection_obj.cursor()

cursor_obj.execute("DROP TABLE IF EXISTS STOCK")
sql_create_stocks_table = """ CREATE TABLE IF NOT EXISTS stock (
                                        stockId integer PRIMARY KEY AUTOINCREMENT, 
                                        stockSymbol text,
                                        shares integer, 
                                        earnings integer, 
                                        yearlyEarnings integer

                                        );"""
cursor_obj.execute("DROP TABLE IF EXISTS bond")
sql_create_bond_table = """ CREATE TABLE IF NOT EXISTS bond (
                                        bondId integer PRIMARY KEY AUTOINCREMENT,
                                        stockSymbol text,
                                        shares integer, 
                                        earnings integer,
                                        yearlyEarnings integer, 
                                        coupon integer,
                                        yield integer
                                        );"""

cursor_obj.execute("DROP TABLE IF EXISTS investor")
sql_create_investor_table = """ CREATE TABLE IF NOT EXISTS investor (
                                        investorId integer PRIMARY KEY AUTOINCREMENT,
                                        firstName text, 
                                        lastName text, 
                                        address text,
                                        phoneNumber text
                                        );"""

#Create new stock table 
cursor_obj.execute("DROP TABLE IF EXISTS newStock")
sql_create_newStock_table = """ CREATE TABLE IF NOT EXISTS newStock (
                                        stockId integer PRIMARY KEY AUTOINCREMENT,
                                        symbol text, 
                                        date text, 
                                        open integer,
                                        high integer, 
                                        low integer, 
                                        close interger,
                                        volume integer
                                        );"""

try:
    cursor_obj.execute(sql_create_stocks_table)
    cursor_obj.execute(sql_create_bond_table)
    cursor_obj.execute(sql_create_investor_table)
    cursor_obj.execute(sql_create_newStock_table)
except Error as e: 
    print("SQLite error occured while creating new tables", e.add_note)

#format earnings/loss into currency
locale.setlocale(locale.LC_ALL, '')
def format_currency(value):
    return locale.currency(value, grouping=True)

#Insert stock list 
for data in csvStockList:
    earnings_loss_per_share = Stock.calculateEaringsOrLossPerShare(data[3], data[2], data[1])
    percentage = Stock.calculatePercentage(data[3], data[2], datetime.strptime(data[4], '%m/%d/%Y'))
    cursor_obj.execute("INSERT INTO stock (stockSymbol, shares, earnings, yearlyEarnings) VALUES ( ?, ?, ?, ?)",
                        (data[0], data[1],format_currency(earnings_loss_per_share), format_currency(percentage)))

#Insert bond list 
for data in csvBondList: 
    earnings_loss_per_share = Stock.calculateEaringsOrLossPerShare(data[3], data[2], data[1])
    percentage = Stock.calculatePercentage(data[3], data[2], datetime.strptime(data[4], '%m/%d/%Y'))
    cursor_obj.execute("INSERT INTO bond (stockSymbol, shares, earnings, yearlyEarnings, coupon, yield) VALUES (?, ?, ?, ?, ?, ?)",
                        (data[0], data[1], format_currency(earnings_loss_per_share), format_currency(percentage), data[5], data[6]))

#Insert Investor 
cursor_obj.execute("INSERT INTO investor (firstName, lastName, address, phoneNumber) VALUES (?, ?, ?, ?)", 
                   (investor.firstName, investor.lastName, investor.address, investor.phoneNumber))

#Store stock symbols into a list from db
myStockSymbolCursor = connection_obj.cursor()
myStockSymbolCursor.execute("SELECT stockSymbol FROM STOCK")
stockSymbolQuery = myStockSymbolCursor.fetchall()
dbSymbolList = [res[0] for res in stockSymbolQuery]

#Store number of shares into a list from db
mySharesCursor = connection_obj.cursor()
mySharesCursor.execute("SELECT shares FROM STOCK")
sharesQuery = mySharesCursor.fetchall()
dbSharesList = [res[0] for res in sharesQuery]

#create dictionary for the shares from previous assignment 
sharesFromPreviousAssignment = {}
for symbol in dbSymbolList: 
    for share in dbSharesList:
        sharesFromPreviousAssignment[symbol] = share

#Create dict for dates and stocks. Using DefaultDict to mitigate datetime mismatch
dates = defaultdict(int)
stock_values = defaultdict(lambda: defaultdict(int))

#create function to read JSON file
def loadJSONData(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

#read from JSON file 
file = 'AllStocks.json'
data_set = loadJSONData(file)

#access JSON data 
jsonStockList = []
for entry in data_set['data']:
    symbol = entry['Symbol']
    date_str = entry['Date']
    open_price = entry['Open']
    high_price = entry['High']
    low_price = entry['Low']
    close_price = entry['Close']
    volume = entry['Volume']
    jsonStockList.append([symbol, date_str, open_price, high_price, low_price, close_price, volume])

    date = datetime.strptime(date_str, '%d-%b-%y').date()
    if symbol not in stock_values: 
        stock_values[symbol] = {}
    stock_values[symbol][date] = (sharesFromPreviousAssignment[symbol] * close_price)
    if date not in dates: 
        dates[date] = 0
    
    dates[date] += stock_values[symbol][date]

#Insert new stock table with json data
for data in jsonStockList: 
    cursor_obj.execute("INSERT INTO newStock (symbol, date, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (data[0], data[1], data[2], data[3], data[4], data[5], data[6]))

#Prepare dates and value lists for plotting
sortedDates = sorted(dates.items())
dates_list = [date for date, _ in sortedDates]
values_list = [value for _, value in sortedDates]

#Create a plotly figure 
figure = go.Figure()

#Plot the data using plotly
for symbol in stock_values: 
    stock_value_list = [stock_values[symbol].get(date, 0) for date in dates_list]
    figure.add_trace(go.Scatter(x=dates_list, y=stock_value_list, mode='lines', name=symbol))

figure.update_layout(
    title="Stock Portfolio for " + investor.firstName + ' ' + investor.lastName,
    title_x=0.5,
    xaxis_title="Date",
    yaxis_title="Value",
    xaxis=dict(type='date'),
    xaxis_tickformat='%Y-%m-%d',
    legend=dict(x=0, y=1)
)

figure.show()

try:
    connection_obj.commit()
except Error as e:
    print("SQLite error occured while inserting into tables", e.add_note)
connection_obj.close()

#Unit tests
class testStock(unittest.TestCase):
    def test_symbol(self):
        stock = Stock(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2))
        self.assertEqual(stock.symbol, 'GOOG')

    def test_shares(self):
        stock = Stock(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2))
        self.assertEqual(stock.shares, 125)

    def test_price(self):
        stock = Stock(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2))
        self.assertEqual(stock.purchasePrice, 34.56)

    def test_value(self):
        stock = Stock(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2))
        self.assertEqual(stock.currentValue, 50.00)

    def test_date(self):
        stock = Stock(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2))
        self.assertEqual(stock.purchaseDate, datetime(2018, 3, 2))

class testBond(unittest.TestCase):
    def test_coupon(self):
        bond = Bond(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2), 44, 55)
        self.assertEqual(bond.coupon, 44)

    def test_yeild(self):
        bond = Bond(1, 'GOOG', 125, 34.56, 50.00, datetime(2018, 3, 2), 44, 55)
        self.assertEqual(bond.yeild, 55)

class testInvestor(unittest.TestCase):
    def test_first(self):
        investor = Investor('Bob', 'Smith', '1234 lala land', '444-000-9808')
        self.assertEqual(investor.firstName, 'Bob')

    def test_last(self):
        investor = Investor('Bob', 'Smith', '1234 lala land', '444-000-9808')
        self.assertEqual(investor.lastName, 'Smith')

    def test_address(self):
        investor = Investor('Bob', 'Smith', '1234 lala land', '444-000-9808')
        self.assertEqual(investor.address, '1234 lala land')

    def test_phone(self):
        investor = Investor('Bob', 'Smith', '1234 lala land', '444-000-9808')
        self.assertEqual(investor.phoneNumber, '444-000-9808')

def main():
    unittest.main()

if __name__ == '__main__':
    unittest.main()