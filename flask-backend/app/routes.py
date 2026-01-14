from flask import Blueprint, jsonify, request
from flask.views import MethodView
from app.schema import schema

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Flask backend is running'}), 200


class GraphQLView(MethodView):
    def get(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GraphQL Playground</title>
            <style>
                body {
                    height: 100vh;
                    margin: 0;
                    width: 100%;
                    overflow: hidden;
                }
                #graphiql {
                    height: 100vh;
                }
            </style>
            <script crossorigin src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
            <script crossorigin src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/graphiql@2.4.7/graphiql.min.css" />
        </head>
        <body>
            <div id="graphiql">Loading...</div>
            <script src="https://unpkg.com/graphiql@2.4.7/graphiql.min.js" type="application/javascript"></script>
            <script>
                const fetcher = GraphiQL.createFetcher({
                    url: '/api/graphql',
                });
                
                ReactDOM.render(
                    React.createElement(GraphiQL, { fetcher: fetcher }),
                    document.getElementById('graphiql'),
                );
            </script>
        </body>
        </html>
        """, 200
    
    def post(self):
        data = request.get_json()
        query = data.get('query')
        variables = data.get('variables')
        
        result = schema.execute(query, variables=variables)
        
        response = {}
        if result.data:
            response['data'] = result.data
        if result.errors:
            response['errors'] = [str(error) for error in result.errors]
        
        return jsonify(response), 200


api_bp.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql'))