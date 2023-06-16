import requests


class BatchDataReceiver:
    def __init__(self):
        pass

    def make_response(self, provider_url, batch_payload):
        response = requests.post(provider_url, json=batch_payload)
        return response.json()

    def build_wallet_token_balance_payload(self, wallet_address, token_contract_address):
        payload = {
            'jsonrpc': '2.0',
            'method': 'eth_call',
            'params': [{
                'to': token_contract_address,
                'data': f"0x70a08231000000000000000000000000{wallet_address[2:]}"
            }, 'latest'],
            'id': 1
        }
        return payload

    def build_wallet_eth_balance_payload(self, wallet_address):
        payload = {
            'jsonrpc': '2.0',
            'method': 'eth_getBalance',
            'params': [wallet_address, 'latest'],
            'id': 1
        }
        return payload

    def fetch_wallet_balance_batch(self, provider_url, wallet_address, token_contract_addresses):
        batch_payload = []
        for token_contract_address in token_contract_addresses:
            batch_payload.append(self.build_wallet_token_balance_payload(wallet_address, token_contract_address))
            batch_payload.append(self.build_wallet_eth_balance_payload(wallet_address))

        batch_response = self.make_response(provider_url, batch_payload)
        return batch_response

    def get_wallet_balance(self, provider_url, wallet_address, token_contract_addresses):
        batch_response = self.fetch_wallet_balance_batch(provider_url, wallet_address, token_contract_addresses)
        balances = {}
        for item in batch_response:
            if 'result' in item and item['result'] is not None:
                balance = int(item['result'], 16)
                balances[item['id']] = balance
        return balances



