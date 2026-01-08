from flask import Flask

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200

@app.route('/graphql', methods=['POST'])
def graphql():
    return {'message': 'GraphQL endpoint - coming soon'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)