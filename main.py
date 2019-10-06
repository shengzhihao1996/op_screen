from flask import Flask
from flask import make_response
from ops_screen.PortMetrics import PortMetrics
from ops_screen.MongoRsMetrics import MongoRsMetrics
from ops_screen.MysqlMsMetrics import MysqlMsMetrics
from ops_screen.RedisMsMetrics import RedisMsMetrics


app = Flask(__name__)
@app.route('/PortMetrics')
def PortWeb():
    a = make_response(PortMetrics())
    a.headers['Content-Type'] = 'text/plain'
    return a, 200

@app.route('/RedisMsMetrics')
def RedisWeb():
    a = make_response(RedisMsMetrics())
    a.headers['Content-Type'] = 'text/plain'
    return a, 200

@app.route('/MysqlMsMetrics')
def MysqlWeb():
    a = make_response(MysqlMsMetrics())
    a.headers['Content-Type'] = 'text/plain'
    return a, 200

@app.route('/MongoRsMetrics')
def MongoWeb():
    a = make_response(MongoRsMetrics())
    a.headers['Content-Type'] = 'text/plain'
    return a, 200

if __name__ == '__main__':
    app.run(port=80)