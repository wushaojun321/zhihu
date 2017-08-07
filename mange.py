#encoding:utf8
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = create_app()

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    # with app.test_request_context():
    #     print app.config['SQLALCHEMY_DATABASE_URI']
    manager.run()
    # app.run(debug=True)