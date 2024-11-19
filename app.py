from flask import Flask, request, render_template, redirect
import pandas as pd
import os
import random
import requests

url1 = "http://dog-api.kinduff.com/api/facts?number=10"
response1 = requests.get(url1)
url2 = "https://latest.currency-api.pages.dev/v1/currencies/eur.json"
response2 = requests.get(url2)

fieldnames = ['id', 'item', 'account', 'vendor', 'quantity', 'group', 'amount', 'date']
if (not os.path.exists('./budget_tracker.csv')) or (os.path.getsize(('./budget_tracker.csv')) == 0):
    with open('./budget_tracker.csv', 'a', newline='') as file:
        header = pd.DataFrame(columns = fieldnames)
        header.to_csv('./budget_tracker.csv', mode='a', index = False)

def openfile():
    budget = pd.read_csv('./budget_tracker.csv')
    budgetdict = budget.to_dict(orient = 'records')
    return budgetdict

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def show_items():
    return render_template('./index.html', budget = openfile(), fact = random.choice(response1.json()['facts']))

@app.route('/<int:itemid>', methods = ['GET'])
def show_details(itemid):
    y = [x for x in openfile() if x['id'] == itemid]
    return render_template('./details.html', budget = y)
    
@app.route('/create', methods = ['GET', 'POST'])
def show_form():
    if request.method == 'GET':
        return render_template('./form.html')
    else:
        budgetitem = dict()
        b = max([x['id'] for x in openfile()])
        budgetitem['id'] = b + 1
        budgetitem['item'] = request.form['item']
        budgetitem['account'] = request.form['account']
        budgetitem['vendor'] = request.form['vendor']
        budgetitem['quantity'] = request.form['quantity']
        budgetitem['group'] = request.form['group']
        if request.form['group'] == 'e':
            budgetitem['amount'] = -(int(request.form['amount']))
        else:
            budgetitem['amount'] = int(request.form['amount'])
        budgetitem['currency'] = request.form['currency']
        budgetitem['date'] = request.form['date']
        if request.form['group'] == 'e':
            budgetitem['EUR'] = round(-(float(request.form['amount']) / response2.json()['eur'][request.form['currency'].lower()]),2)
        else:
            budgetitem['EUR'] = round((float(request.form['amount']) / response2.json()['eur'][request.form['currency'].lower()]),2)
        itemdf = pd.DataFrame([budgetitem])
        itemdf.to_csv('./budget_tracker.csv', mode='a', index=False, header=False)
        return redirect('/')
        return show_items()

# run the server
if __name__ == '__main__':
    app.run(debug = True)