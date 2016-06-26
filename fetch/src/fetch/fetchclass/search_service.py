# -*- coding:utf-8 -*-
from BaseHTTPServer import BaseHTTPRequestHandler
import urlparse,urllib
from InputSearch import *
from id_down_51 import *
from id_down_zhilian import *
from id_down_cjol import *
import json,os,common,time
import logging.config, logging
from lib51search import *
from Inputzhilian import *
from libzhilian import *
from libcjolsearch import *
from Inputcjol import *



class GetHandler(BaseHTTPRequestHandler, job51search):
    
    def do_GET(self):
        parsed_path = urlparse.urlparse(self.path)
        # message_parts = [
        #         'CLIENT VALUES:',
        #         'client_address=%s (%s)' % (self.client_address,
        #                                     self.address_string()),
        #         'command=%s' % self.command,
        #         'path=%s' % self.path,
        #         'real path=%s' % parsed_path.path,
        #         'query=%s' % parsed_path.query,
        #         'request_version=%s' % self.request_version,
        #         '',
        #         'SERVER VALUES:',
        #         'server_version=%s' % self.server_version,
        #         'sys_version=%s' % self.sys_version,
        #         'protocol_version=%s' % self.protocol_version,
        #         '',
        #         'HEADERS RECEIVED:',
        #         ]
        # for name, value in sorted(self.headers.items()):
        #     message_parts.append('%s=%s' % (name, value.rstrip()))
        # message_parts.append('')
        # message = '\r\n'.join(message_parts)
        with open(common.json_config_path) as f_log:
            f_read = f_log.read()
        logger = logging.getLogger(__name__)
        log_dict = json.loads(f_read)
        log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'input_search.log')
        logging.config.dictConfig(log_dict)

        t1 = time.time()
        parameter = urlparse.parse_qs(parsed_path.query)


        if parameter['source'][0] == '51job':
            if 'area' in parameter.keys():
                area = parameter['area'][0]
            else:
                area = None

            if 'year' in parameter.keys():
                year = parameter['year'][0]
            else:
                year = None

            if 'age' in parameter.keys():
                age = parameter['age'][0]
            else:
                age = None

            if 'degree' in parameter.keys():
                degree = parameter['degree'][0]
            else:
                degree = None

            if 'keyword' in parameter.keys():
                keyword = parameter['keyword'][0]
            else:
                keyword = None

            if 'keywordtype' in parameter.keys():
                keywordtype = parameter['keywordtype'][0]
            else:
                keywordtype = None



            if 'page' in parameter.keys():
                page_num = parameter['page'][0]
            else:
                page_num = '1'

            if 'industry' in parameter.keys():
                industry = parameter['industry'][0]
            else:
                industry = None

            if 'work_func' in parameter.keys():
                work_func = parameter['work_func'][0]
            else:
                work_func = None

            if 'job_area' in parameter.keys():
                job_area = parameter['job_area'][0]
            else:
                job_area = None

            if 'updatetime' in parameter.keys():
                updatetime = parameter['updatetime'][0]
            else:
                updatetime = '180'


            run = TransportSearch()
            if 'id' in parameter.keys():
                flag = run.id_down(parameter['id'][0])
                if flag == 1:
                    message = {'code': flag, 'msg': 'insert success'}
                elif flag == -1:
                    message = {'code': flag, 'msg': 'update success'}
                elif flag == 0:
                    message = {'code': flag, 'msg': 'not insert'}
                elif flag == -2:
                    message = {'code': flag, 'msg': 'parse error'}
                elif flag == -3:
                    message = {'code': flag, 'msg': 'source error'}
                elif flag == -5:
                    message = {'code': flag, 'msg': 'operate error'}
                elif flag == 8:
                    message = {'code': flag, 'msg': 'resume secret'}
                elif flag == 9:
                    message = {'code': flag, 'msg': 'resume remove'}
                elif flag == 10:
                    message = {'code': flag, 'msg': 'more busy action'}
                elif flag == -10:
                    message = {'code': flag, 'msg': 'already update'}
                message = json.dumps(message)
            else:
                if page_num == '1':
                    message = run.run_crawl_first(area, year, age, degree, keyword, keywordtype, industry, work_func, job_area, updatetime, page_num)
                else:
                    run.run_crawl_first(area, year, age, degree, keyword,keywordtype, industry, work_func, job_area, updatetime, page_num)
                    message = run.run_crawl(area, year, age, degree, keyword, keywordtype,industry, work_func, job_area, updatetime, page_num)



        elif parameter['source'][0] == 'zhilian':
            if 'area' in parameter.keys():
                area = parameter['area'][0]
            else:
                area = None

            if 'year' in parameter.keys():
                year = parameter['year'][0]
            else:
                year = None

            if 'age' in parameter.keys():
                age = parameter['age'][0]
            else:
                age = None

            if 'degree' in parameter.keys():
                degree = parameter['degree'][0]
            else:
                degree = None

            if 'keyword' in parameter.keys():
                keyword = parameter['keyword'][0]
            else:
                keyword = None

            if 'page' in parameter.keys():
                page_num = parameter['page'][0]
            else:
                page_num = '1'

            if 'industry' in parameter.keys():
                industry = parameter['industry'][0]
            else:
                industry = None

            if 'work_func' in parameter.keys():
                work_func = parameter['work_func'][0]
            else:
                work_func = None

            if 'job_area' in parameter.keys():
                job_area = parameter['job_area'][0]
            else:
                job_area = None

            if 'updatetime' in parameter.keys():
                updatetime = parameter['updatetime'][0]
            else:
                updatetime = '6,9'


            if 'id' in parameter.keys():
                run_id = IdDownzhilian(parameter['id'][0])
                flag = run_id.get_id()
                if flag == 1:
                    message = {'code': flag, 'msg': 'insert success'}
                elif flag == -1:
                    message = {'code': flag, 'msg': 'update success'}
                elif flag == 0:
                    message = {'code': flag, 'msg': 'not insert'}
                elif flag == -2:
                    message = {'code': flag, 'msg': 'parse error'}
                elif flag == -3:
                    message = {'code': flag, 'msg': 'source error'}
                elif flag == -5:
                    message = {'code': flag, 'msg': 'operate error'}
                elif flag == 8:
                    message = {'code': flag, 'msg': 'resume secret'}
                elif flag == 9:
                    message = {'code': flag, 'msg': 'resume remove'}
                elif flag == 10:
                    message = {'code': flag, 'msg': 'more busy action'}
                elif flag == -10:
                    message = {'code': flag, 'msg': 'already update'}
                message = json.dumps(message)
            else:
                run = TransportZhlian()
                run.crawl_zhilian_test()
                message = run.crawl_zhilian(area, year, age, degree, keyword, industry, work_func, job_area, updatetime, page_num)



        elif parameter['source'][0] == 'cjol':
            if 'area' in parameter.keys():
                area = parameter['area'][0]
            else:
                area = None

            if 'year' in parameter.keys():
                year = parameter['year'][0]
            else:
                year = None

            if 'age' in parameter.keys():
                age = parameter['age'][0]
            else:
                age = None

            if 'degree' in parameter.keys():
                degree = parameter['degree'][0]
            else:
                degree = None

            if 'keyword' in parameter.keys():
                keyword = parameter['keyword'][0]
            else:
                keyword = None

            if 'page' in parameter.keys():
                page_num = parameter['page'][0]
            else:
                page_num = '1'

            if 'industry' in parameter.keys():
                industry = parameter['industry'][0]
            else:
                industry = None

            if 'work_func' in parameter.keys():
                work_func = parameter['work_func'][0]
            else:
                work_func = None

            if 'job_area' in parameter.keys():
                job_area = parameter['job_area'][0]
            else:
                job_area = None

            if 'updatetime' in parameter.keys():
                updatetime = parameter['updatetime'][0]
            else:
                updatetime = None

            if 'id' in parameter.keys():
                run_id = IdDowncjol(parameter['id'][0])
                flag = run_id.get_id()
                if flag == 1:
                    message = {'code': flag, 'msg': 'insert success'}
                elif flag == -1:
                    message = {'code': flag, 'msg': 'update success'}
                elif flag == 0:
                    message = {'code': flag, 'msg': 'not insert'}
                elif flag == -2:
                    message = {'code': flag, 'msg': 'parse error'}
                elif flag == -3:
                    message = {'code': flag, 'msg': 'source error'}
                elif flag == -5:
                    message = {'code': flag, 'msg': 'operate error'}
                elif flag == 8:
                    message = {'code': flag, 'msg': 'resume secret'}
                elif flag == 9:
                    message = {'code': flag, 'msg': 'resume remove'}
                elif flag == 10:
                    message = {'code': flag, 'msg': 'more busy action'}
                elif flag == -10:
                    message = {'code': flag, 'msg': 'already update'}
                message = json.dumps(message)
            else:
                run = TransportCjol()
                message = run.crawl_cjol(area, year, age, degree, keyword, industry, work_func, job_area, updatetime, page_num)




        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        t2 = time.time() - t1
        print '-------->', message
        logging.info('--+++--return crawl search page use time: %s s--+++--' % str(t2))
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