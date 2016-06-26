# -*- coding:utf-8 -*-
from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse

class GetHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('0.0.0.0', 8087), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()

# 使用flask做转发 """
# app = Flask(__name__)
#
# @app.route('/', methods=['GET', 'POST'])
# def home():
# 	return '<h1>home</h1>'
#
# @app.route('/query', methods=['GET'])
# def search_form():
# 	return '''<form action="/query" method="get">
# 				<p><input area="area"></p>
# 				<p><input year="year"></p>
# 				<p><input degree="degree"></p>
# 				<p><input keyword="keyword"></p>
# 				<p><input page_num="page_num"></p>
# 				<p><button type="submit">Query</button></p>
# 				</form>'''
#
# @app.route('/query', methods=['GET'])
# def query():
# 	area = request.form['area']
# 	year = request.form['year']
# 	degree = request.form['degree']
# 	keyword = request.form['keyword']
# 	page_num = request.form['page_num']
# 	search_fetch = TransportSearch()
# 	html = search_fetch.run_crawl(area=area,year=year,degree=degree,keyword=keyword,page_num=page_num)
# 	return html
#
# if __name__ == '__main__':
# 	app.run(debug=True,host='0.0.0.0',port=8087)