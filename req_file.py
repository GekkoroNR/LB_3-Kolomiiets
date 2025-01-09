import requests
method = input('Введіть обраний метод великими літерами: ')
head = {'Content-type': 'application/json'}
if method != 'GET' and method != 'DELETE':
    changes = {
        'item_name': input('Введіть назву: '),
        'price': int(input('Введіть ціну: '))
    }
if method != 'POST':
    item = input('Введіть назву або номер товару: ')

match method:
    case 'GET':
        response = requests.get(f'http://127.0.0.1:8000/item/{item}', headers = head)
        print(response.text)
    case 'POST':
        response = requests.post('http://127.0.0.1:8000/items',json = changes,
                                 headers= head, auth=('Admin', 'Password'))
        print(response.text)
    case 'PUT':
        response = requests.put(f'http://127.0.0.1:8000/item/{item}', json=changes,
                                 headers=head, auth=('Admin', 'Password'))
        print(response.text)
    case 'DELETE':
        response = requests.delete(f'http://127.0.0.1:8000/item/{item}',
                        headers=head, json={}, auth=('Admin', 'Password'))
        print(response.text)

