#!/usr/bin/env python

import argparse
import psycopg2
import tornado.ioloop
import tornado.web
import tornado.httpserver
import datetime
import yaml

def pg_connect(settings):
    conn = psycopg2.connect(
    	dbname=settings['PG_DBNAME'],
        user=settings['PG_USER'],
        host=settings['PG_HOST'],
        password=settings['PG_PASS'])
    return (conn)

class BaseHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def initialize(self, settings, *args, **kwargs):
        super(BaseHandler, self).initialize(*args, **kwargs)
        self._settings = settings


class MainHandler(BaseHandler):
    def get(self):
	conn = pg_connect(self._settings)
	cur = conn.cursor()
	cur.execute("INSERT INTO table1 (time) VALUES (%s)", (datetime.datetime.now(),))
	conn.commit()
	cur.execute("SELECT COUNT(id) as views from table1")
	views = cur.fetchone()[0]
	self.write('Congratulations! You\'ve seen this page %d times' % views)
	self.finish()

def make_app(settings):
    return tornado.web.Application([
        (r"/", MainHandler, dict(settings=settings)),
    ])
 
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--conf', help='config file path',
                        default='config.yml')
    args = parser.parse_args()

    with open(args.conf) as f:
    	settings = yaml.load(f)

    app = make_app(settings)
    server = tornado.httpserver.HTTPServer(app)
    server.listen(settings['BIND_PORT'], address=settings['BIND_ADDRESS'])
    server.start(1)
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    main()
