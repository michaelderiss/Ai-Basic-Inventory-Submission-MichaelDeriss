from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)
print(client.get('/health').json())
print(client.get('/api/products').status_code)
print(client.post('/api/products', json={'name': 'Coffee Cups', 'quantity': 30, 'price': 2.5, 'location': 'North'}).json())
print(client.patch('/api/inventory/prod-1001', json={'delta': -5, 'reason': 'morning rush'}).status_code)
print(client.get('/api/inventory/alerts', params={'threshold': 10}).status_code)
