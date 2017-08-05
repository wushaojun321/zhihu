#encoding:utf8
from app import create_app

app = create_app()

if __name__ == '__main__':
    # with app.test_request_context():
    #     print app.config['SQLALCHEMY_DATABASE_URI']
    app.run(host='0.0.0.0', debug=True, port=80)