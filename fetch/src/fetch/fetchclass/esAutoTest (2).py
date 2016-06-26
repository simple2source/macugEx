# -*- coding: UTF-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import json
from elasticsearch import Elasticsearch
import chardet
from prettytable import PrettyTable  
import urllib
import urllib2
import BaseFetch  
import common 
import re

def get_query_job_name(info,ip,port):
  info = urllib.quote(info.encode('utf8'))
  url = "http://115.231.92.103:" + port + "/translator?q=" + info + "&last=7"
  req = urllib2.Request(url)
  res_data = urllib2.urlopen(req)
  return  res_data.read()

# 搜索岗位名时，只考虑岗位名
def test_job_name(key_word="", ip= "115.231.92.103",port="8085"):
  result_dict = {}
  result_dict['key_word'] = key_word.decode("utf8")
  key_word=key_word.lower()
  query_dsl = get_query_job_name(key_word, ip=ip, port=port)
  result_dict['remark'] = "岗位"
  # print u"搜索词:",key_word.decode("utf8")
  query_key = "work_experience.seged_job_name"
  query_value = key_word.lower()
  es = Elasticsearch("183.131.144.102:8090")
  size = 20
  res = es.search(index='supin_resume',doc_type='doc_v1',from_=0,size=size,explain=True,_source_include=["work_experience.job_name"],body=query_dsl)
  return_numbers = res['hits']['total']
  l = len(res['hits']['hits'])
  equal_in = 0
  contain_in = 0
  no_contain = 0
  for i in range(0, l):
    j = res['hits']['hits'][i]['_source']
    if j:
      if len(j.values()):
        if len(j.values()[0]):
            key_word = j.values()[0]
            if len(key_word):
              # 一份简历
              t1 = 0
              t2 = 0
              if query_value.strip() == "安卓":
                for k in key_word:
                  if (not cmp(query_value.strip(), k.values()[0].lower().strip())) or (not cmp("android", k.values()[0].lower().strip())):
                    t1 = 1
                  elif (query_value.strip() in k.values()[0].lower().strip()) or ("android" in k.values()[0].lower().strip()):
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1
              elif query_value.strip() == "android":
                for k in key_word:
                  if (not cmp(query_value.strip(), k.values()[0].lower().strip())) or (not cmp("安卓", k.values()[0].lower().strip())):
                    t1 = 1
                  elif (query_value.strip() in k.values()[0].lower().strip()) or ("安卓" in k.values()[0].lower().strip()):
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1   
              else:
                for k in key_word:
                  if not cmp(query_value.strip(),k.values()[0].lower().strip()):
                    t1 = 1
                  elif query_value.strip() in k.values()[0].lower().strip():
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1 
  count_number = {}
  sum_number = equal_in + contain_in + no_contain
  count_number['0'] = (equal_in,equal_in/float(sum_number))
  count_number['1'] = (contain_in,contain_in/float(sum_number))
  count_number['2'] = (no_contain,no_contain/float(sum_number))
  page = 0
  if return_numbers >= 20:
    mode = return_numbers%size
    if mode != 0:
      page = return_numbers/size + 1
    else:
      page = return_numbers/size
  else:
    page = 1
  # print u'搜索返回总数:',return_numbers
  result_dict['return_numbers'] = return_numbers
  # print u'搜索返回页数:',page
  result_dict['page_numbers'] = page
  # print u"注：岗位名取值: 取值0-等于搜索词,1-包含搜索词,2-不包含搜索词"
  # print u"搜索岗位时，岗位名的首页情况:"
  # print u"(岗位名):百分比"
  first = {}
  for key,value in count_number.items():
    # print key,':','%.2f%%' % (value[1]*100)
    condition = str(value[1]*100)
    first[str(key)] = condition+"%"
  result_dict['first_page'] = first
  from_value = 0
  size_value =20
  if return_numbers > 40:
    mul = return_numbers/20
    from_value = (mul-1)*20 
    res = es.search(index='supin_resume',doc_type='doc_v1',from_=from_value,size=size_value,explain=True,_source_include=["work_experience.job_name"],body=query_dsl)
    l = len(res['hits']['hits'])
    equal_in = 0
    contain_in = 0
    no_contain = 0
    for i in range(0, l):
      j = res['hits']['hits'][i]['_source']
      if j:
        if len(j.values()):
          if len(j.values()[0]):
              key_word = j.values()[0]
              if len(key_word):
                # 一份简历
                t1 = 0
                t2 = 0
              if query_value.strip() == "安卓":
                for k in key_word:
                  if (not cmp(query_value.strip(), k.values()[0].lower().strip())) or (not cmp("android", k.values()[0].lower().strip())):
                    t1 = 1
                  elif (query_value.strip() in k.values()[0].lower().strip()) or ("android" in k.values()[0].lower().strip()):
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1

              elif query_value.strip() == "android":
                for k in key_word:
                  if (not cmp(query_value.strip(), k.values()[0].lower().strip())) or (not cmp("安卓", k.values()[0].lower().strip())):
                    t1 = 1
                  elif (query_value.strip() in k.values()[0].lower().strip()) or ("安卓" in k.values()[0].lower().strip()):
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1              

              else:
                for k in key_word:
                  if not cmp(query_value.strip(),k.values()[0].lower().strip()):
                    t1 = 1
                  elif query_value.strip() in k.values()[0].lower().strip():
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1

    count_number = {}
    sum_number = equal_in + contain_in + no_contain
    count_number['0'] = (equal_in,equal_in/float(sum_number))
    count_number['1'] = (contain_in,contain_in/float(sum_number))
    count_number['2'] = (no_contain,no_contain/float(sum_number))
    # print u"搜索岗位时，岗位名的倒数第二页情况:"
    # print u"(岗位名):百分比"
    end = {}
    for key,value in count_number.items():
      # print key,':','%.2f%%' % (value[1]*100)
      condition = str(value[1]*100)
      end[str(key)] = condition+"%"
    result_dict['end_page'] = end
  else:
    end = {}
    end['0'] = ""
    end['1'] = ""
    end['2'] = ""
    # print u'搜索结果不足两页' 
    result_dict['end_page'] = end
  return result_dict


#搜索公司名
def test_company_name(key_word=""):
  result_dict = {}
  result_dict['remark'] = "公司"
  # print u"搜索词:",key_word.decode("utf8")
  result_dict['key_word'] = key_word.decode("utf8")
  query_key = "work_experience.seged_company_name"
  query_value = key_word
  es = Elasticsearch("183.131.144.102:8090")
  size = 20
  res = es.search(index='supin_resume',doc_type='doc_v1',explain=True,_source_include=["work_experience.company_name"],body={ 
          "query": {
            "bool":{
              "must":[
                {"match":
                  {
                    query_key:{"query":query_value.lower(),"operator":"and","type":"phrase"}
                  }
                }
              ]
            }
           },"from":0,"size":size
         }
      )
  return_numbers = res['hits']['total']
  result_dict['return_numbers'] = return_numbers
  l = len(res['hits']['hits'])
  equal_in = 0
  contain_in = 0
  no_contain = 0
  for i in range(0, l):
    j = res['hits']['hits'][i]['_source']
    if j:
      if len(j.values()):
        if len(j.values()[0]):
            key_word = j.values()[0]
            if len(key_word):
              # 一份简历
              t1 = 0
              t2 = 0
              for k in key_word:
                if not cmp(query_value.strip(),k.values()[0].lower().strip()):
                  t1 = 1
                elif query_value.strip() in k.values()[0].lower().strip():
                  t2 = 1
              # t1为1，相等
              if t1:
                equal_in += 1
              # t2为1，包含
              elif t2:
                contain_in += 1
              else:
                no_contain += 1
  count_number = {}
  sum_number = equal_in + contain_in + no_contain
  if not sum_number:
    return 0
  count_number['0'] = (equal_in,equal_in/float(sum_number))
  count_number['1'] = (contain_in,contain_in/float(sum_number))
  count_number['2'] = (no_contain,no_contain/float(sum_number))
  page = 0
  if return_numbers >= 20:
    mode = return_numbers%size
    if mode != 0:
      page = return_numbers/size + 1
    else:
      page = return_numbers/size
  else:
    page = 1
  # print u'搜索返回总数:',return_numbers
  # print u'搜索返回页数:',page
  result_dict['page_numbers'] = page
  # print u"注：公司名取值: 取值0-等于搜索词,1-包含搜索词,2-不包含搜索词"
  # print u"搜索岗位时，岗位名的首页情况:"
  # print u"(公司名):百分比"
  first = {}
  for key,value in count_number.items():
    # print key,':','%.2f%%' % (value[1]*100)
    condition = str(value[1]*100)
    first[str(key)] = condition+"%"
  result_dict['first_page'] = first

  from_value = 0
  size_value =20
  if return_numbers > 40:
    mul = return_numbers/20
    from_value = (mul-1)*20 
    res = es.search(index='supin_resume',doc_type='doc_v1',explain=True,_source_include=["work_experience.company_name"],body={ 
            "query": {
              "bool":{
                "must":[
                  {"match":
                    {
                      query_key:{"query":query_value,"operator":"and","type":"phrase"}
                    }
                  }
                ]
              }
             },"from":from_value,"size":size_value
           }
        )
    l = len(res['hits']['hits'])
    equal_in = 0
    contain_in = 0
    no_contain = 0
    for i in range(0, l):
      j = res['hits']['hits'][i]['_source']
      if j:
        if len(j.values()):
          if len(j.values()[0]):
              key_word = j.values()[0]
              if len(key_word):
                # 一份简历
                t1 = 0
                t2 = 0
                for k in key_word:
                  if not cmp(query_value.strip(),k.values()[0].lower().strip()):
                    t1 = 1
                  elif query_value.strip() in k.values()[0].lower().strip():
                    t2 = 1
                # t1为1，相等
                if t1:
                  equal_in += 1
                # t2为1，包含
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1
    count_number = {}
    sum_number = equal_in + contain_in + no_contain
    count_number['0'] = (equal_in,equal_in/float(sum_number))
    count_number['1'] = (contain_in,contain_in/float(sum_number))
    count_number['2'] = (no_contain,no_contain/float(sum_number))
    # print u"搜索岗位时，岗位名的倒数第二页情况:"
    # print u"(公司名):百分比"
    end = {}
    for key,value in count_number.items():
      # print key,':','%.2f%%' % (value[1]*100)
      condition = str(value[1]*100)
      end[str(key)] = condition+"%"
    result_dict['end_page'] = end
  else:
    end = {}
    end['0'] = ""
    end['1'] = ""
    end['2'] = "" 
    # print u'搜索结果不足两页' 
    result_dict['end_page'] = end
  return result_dict


# 同时搜索地点和岗位名时，只考虑岗位名
def test_job_name_city(job_name="", city_value=""):
  result_dict = {}
  result_dict['remark'] = "岗位+城市"
  # print u"搜索词:",job_name.decode("utf8"),city_value.decode("utf8")
  result_dict['key_word'] = job_name.decode("utf8") + ' ' + city_value.decode("utf8")
  query_key = "work_experience.seged_job_name"
  query_value = job_name
  es = Elasticsearch("183.131.144.102:8090")
  size = 20
  res = es.search(index='supin_resume',doc_type='doc_v1',explain=True,_source_include=["work_experience.job_name",'expected_city'],
       body={
            "query": {
               "bool":{
                 "must":[
                   {"match":{"work_experience.seged_job_name":{"query":query_value.lower(),"operator":"and","type":"phrase"}}},   
                   {"match":{"seged_expected_city":{"query":city_value.lower(),"operator":"and","type":"phrase"}}}
                  ]
                }
              },"from":0,"size":size
             }
          )
  return_numbers = res['hits']['total']
  result_dict['return_numbers'] = return_numbers
  l = len(res['hits']['hits'])
  equal_in = 0
  contain_in = 0
  no_contain = 0
  for i in range(0, l):
    j = res['hits']['hits'][i]['_source']
    if j:
      t1, t2 = 0, 0
      for k in j['work_experience']:
        if not cmp(query_value.strip(),k['job_name'].lower().strip()):
          t1 = 1
        elif query_value.strip() in k['job_name'].lower().strip():
          t2 = 1
      if t1:
        equal_in += 1
      elif t2:
        contain_in += 1
      else:
        no_contain += 1
  count_number = {}
  sum_job = equal_in + contain_in + no_contain
  count_number['0'] = (equal_in,equal_in/float(sum_job))
  count_number['1'] = (contain_in,contain_in/float(sum_job))
  count_number['2'] = (no_contain,no_contain/float(sum_job))
  page = 0
  if return_numbers >= 20:
    mode = return_numbers%size
    if mode != 0:
      page = return_numbers/size + 1
    else:
      page = return_numbers/size
  else:
    page = 1
  # print u'搜索返回总数:',return_numbers
  # print u'搜索返回页数:',page
  result_dict['page_numbers'] = page
  
  # print u"注：岗位名取值: 取值0-等于搜索词,1-包含搜索词,2-不包含搜索词"
  # print u"搜索地点和岗位时，岗位名首页情况:"
  # print u"(岗位名):百分比"
  first = {}
  for key,value in count_number.items():
    # print key,':','%.2f%%' % (value[1]*100) 
    condition = str(value[1]*100)
    first[str(key)] = condition+"%"
  result_dict['first_page'] = first
  from_value = 0
  size_value =20
  if return_numbers > 40:
    mul = return_numbers/20
    from_value = (mul-1)*20 
    res = es.search(index='supin_resume',doc_type='doc_v1',explain=True,_source_include=["work_experience.job_name"],body={ 
            "query": {
              "bool":{
                "must":[
                  {"match":
                    {
                      query_key:{"query":query_value,"operator":"and","type":"phrase"}
                    }
                  }
                ]
              }
             },"from":from_value,"size":size_value
           }
        )
    l = len(res['hits']['hits'])
    equal_in = 0
    contain_in = 0
    no_contain = 0
    for i in range(0, l):
      j = res['hits']['hits'][i]['_source']
      if j:
        print j
        if len(j.values()):
          if len(j.values()[0]):
              key_word = j.values()[0]
              if len(key_word):
                t1 = 0
                t2 = 0
                for k in key_word:
                  if not cmp(query_value.strip(),k.values()[0].lower().strip()):
                    t1 = 1
                  elif query_value.strip() in k.values()[0].lower().strip():
                    t2 = 1
                if t1:
                  equal_in += 1
                elif t2:
                  contain_in += 1
                else:
                  no_contain += 1
    count_number = {}
    sum_number = equal_in + contain_in + no_contain
    count_number['0'] = (equal_in,equal_in/float(sum_number))
    count_number['1'] = (contain_in,contain_in/float(sum_number))
    count_number['2'] = (no_contain,no_contain/float(sum_number))
    # print u"搜索地点和岗位时，岗位名的倒数第二页情况:"
    # print u"(岗位名):百分比"
    end = {}
    for key,value in count_number.items():
      # print key,':','%.2f%%' % (value[1]*100)
      condition = str(value[1]*100)
      end[str(key)] = condition+"%"
    result_dict['end_page'] = end
  else:
    end = {}
    end['0'] = ""
    end['1'] = ""
    end['2'] = "" 
    # print u'搜索结果不足两页' 
    result_dict['end_page'] = end
  return result_dict

def create_data(dd):
  data_list = [dd["key_word"],dd["return_numbers"],dd["page_numbers"],dd["first_page"]['0'],dd["first_page"]['1'],dd["first_page"]['2'],\
  dd["end_page"]['0'],dd["end_page"]['1'],dd["end_page"]['2'],dd["remark"]]
  return data_list  

def create_table():
  attributes = [u"搜索词",u"总数",u"页数",u"首:0",u"首:1",u"首:2",u"尾:0",u"尾:1",u"尾:2","备注"]
  x = PrettyTable(attributes) 
  x.padding_width = 20 # One space between column edges and contents (default)  
  x.align["key word"] = "l" # Left align city names 
  x.align["total"] = "l" 
  x.align["page"] = "l" 
  x.align["F:0"] = "l" 
  x.align["F:1"] = "l" 
  x.align["F:2"] = "l" 
  x.align["E:0"] = "l" 
  x.align["E:1"] = "l" 
  x.align["E:2"] = "l" 
  x.align["E:2"] = "l" 
  x.align["remark"] = "l" 
  return x  

def create_html_table(table,attributes,ip,port):
  html_table = table.get_html_string(fields=attributes)
  msg_style = """<style type="text/css">
.body{
  font-family: Monaco, Menlo, Consolas, "Courier New", "Lucida Sans Unicode", "Lucida Sans", "Lucida Console",  monospace;
  font-size: 14px;
  line-height: 20px;
}

.table{ border-collapse:collapse; border:solid 1px gray; padding:6px}
.table td{border:solid 1px gray; padding:6px}

.color-ok {color: green;}
.color-warning {color: coral;}
.color-error {color: red;}

.bg-ok {background-color: lavender;}
.bg-warning {background-color: yellow;}
.bg-error {background-color: deeppink;}
</style>"""
  msg_head = """<html><head><meta charset="utf-8"></head>""" + msg_style + "<body>"
  msg_head = msg_head + """<h2>搜索结果自动化测试报表</h2>"""
  remark = """<td>备注：0:相等，1:包含，2:不包含</td>"""

  if ip == "115.231.92.103" and port == "8085":
    remark2 = """<td>ip:""" + ip + """&nbsp;&nbsp;&nbsp port:""" + port + """&nbsp;&nbsp;&nbsp只匹配岗位名(修改了c/c++ c#等词的搜索)""" +"""</td></br>""" 
  elif ip == "115.231.92.103" and port == "8086":
    remark2 = """<td>ip:""" + ip + """&nbsp;&nbsp;&nbsp port:""" + port + """&nbsp;&nbsp;&nbsp只匹配岗位名""" +"""</td></br>""" 
  elif ip == "115.231.92.103" and port == "8087":
    remark2 = """<td>ip:""" + ip + """&nbsp;&nbsp;&nbsp port:""" + port + """&nbsp;&nbsp;&nbsp同时匹配岗位名和岗位描述(加职能过滤)""" +"""</td></br>""" 
  else:
    remark2 = """<td>ip:""" + ip + """&nbsp;&nbsp;&nbsp port:""" + port + """</td></br>""" 
  html_table = msg_head + html_table + remark2 + remark + "</body></html>"
  html_table = html_table.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
  return html_table

def mark(html_table,length):
  html_list = html_table.split("\n")
  for i in range(0,length):
    pat = re.compile("\>.*?%\<")
    percent_e = re.findall(pat,html_list[39+12*i])
    if len(percent_e):
      percent = percent_e[0].replace(">","").replace("%<","")
      if float(percent) != 0.0:
        find_str = "right"
        replace_str = "right;color:red;"
        html_list[39+12*i] = html_list[39+12*i].replace(find_str, replace_str)

    percent_f = re.findall(pat,html_list[36+12*i])
    if len(percent_f):
      percent = percent_f[0].replace(">","").replace("%<","")
      if float(percent) != 0.0:
        find_str = "right"
        replace_str = "right;color:red;"
        html_list[36+12*i] = html_list[36+12*i].replace(find_str, replace_str)
  html_table = "\n".join(html_list)
  return html_table


def sendMail(keyWordList):
  mail = BaseFetch.BaseFetch()
  table_list = []
  ip = "115.231.92.103"
  for port in ("8085","8086","8087"):
    table = create_table()
    for i in keyWordList:
      dd = test_job_name(i, ip=ip, port=port)
      data = create_data(dd)
      table.add_row(data)  
    length = len(keyWordList)
    
    attributes = [u"搜索词",u"总数",u"页数",u"首:0",u"首:1",u"首:2",u"尾:0",u"尾:1",u"尾:2","备注"]
    html_table = create_html_table(table,attributes,ip=ip,port=port)
    html_table = mark(html_table,length)
    table_list.append(html_table)

   
  pat_start = re.compile("<body>.*</h2>")
  pat_end = re.compile("</table>.*</td>")
  sub_table_list = []
  for i in table_list[1:]:
    start =  re.findall(pat_start,i)  #先找到开头
    end = re.findall(pat_end,i)
    if len(start) and len(end):
      start_index = i.find(start[0])
      end_index = i.find(end[0])
      sub_table_list.append(i[start_index:end_index+len(end[0])])
  end = re.findall(pat_end,table_list[0])
  for i in range(0,len(sub_table_list)):
    sub_table_list[i] = sub_table_list[i].replace("<h2>搜索结果自动化测试报表</h2>","")

  if len(end):
    table_list[0] = table_list[0].replace(end[0], end[0] + "\n".join(sub_table_list))
  # print table_list[0].replace("不包含</td>","不包含</td></br><tr><td>&nbsp;</td></tr>")
  html_table = table_list[0].replace("不包含</td>","不包含</td></br><tr><td>&nbsp;</td></tr>")
  mail.send_mails(title='报表04: 搜索自动化测试',msg_txt=html_table,msgtype=0)

if __name__ == '__main__':
  keyWordList = ["PHP","C++","前端","安卓","android","iOS","Java","设计"]
  sendMail(keyWordList)

  
 