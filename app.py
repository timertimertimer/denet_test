from flask import Flask, request, jsonify
from client import Client
from consts import TOKEN_ADDRESS

app = Flask(__name__)
client = Client()


@app.route('/')
def hello():
    return "Hello, World!"


@app.route('/get_balance')
async def get_balance():
    return jsonify({'balance': (await client.get_balance(request.args.get('address'))).ether})


@app.route('/get_balance_batch', methods=['POST'])
async def get_balance_batch():
    addresses = request.json.get('addresses')
    if not addresses:
        return jsonify({"error": "No addresses provided"}), 400

    return jsonify(
        {'balances': {balance.owner_address: balance.ether for balance in await client.get_balance_batch(addresses)}})


@app.route('/get_top_holders')
async def get_top_holders():
    top_holders = await client.get_top_holders(int(request.args.get('n')))
    return jsonify({'top_holders': {holder.owner_address: holder.ether for holder in top_holders}})


@app.route('/get_top_holders_with_transaction_date')
async def get_top_holders_with_transaction_date():
    holders_with_date = await client.get_top_holders_with_transaction_date(int(request.args.get('n')))
    return jsonify({
        'top_holders': {
            owner_address: {'balance': balance, 'last_transaction_date': date}
            for owner_address, balance, date in holders_with_date}
    })


@app.route('/get_token_info')
async def get_token_info():
    token = await client.get_token_info(request.args.get('address', TOKEN_ADDRESS))
    return jsonify(
        {
            'address': token.address, 'symbol': token.symbol, 'name': token.name,
            'totalSupply': token.total_supply, 'decimals': token.decimals
        }
    )
