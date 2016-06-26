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
import pandas as pd

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
  query_key = "work_experience.seged_job_name"
  query_value = key_word.lower()
  es = Elasticsearch("183.131.144.102:8090")
  size = 20
  res = es.search(index='supin_resume',doc_type='doc_v1',from_=0,size=size,explain=True,_source_include=["work_experience.job_name","price"],body=query_dsl)
  return_numbers = res['hits']['total']
  l = len(res['hits']['hits'])
  equal_in = 0
  contain_in = 0
  no_contain = 0
  for i in range(0, l):
    j = res['hits']['hits'][i]['_source']
    if j:
      print j
      quit()
      if len(j.values()):
        if len(j.values()[0]):
            key_word = j.values()[0]
            if len(key_word):
              t1 = 0
              t2 = 0
              if query_value.strip() == "安卓":
                for k in key_word:
                  if (not cmp(query_value.strip(), k.values()[0].lower().strip())) or (not cmp("android", k.values()[0].lower().strip())):
                    t1 = 1
                  elif (query_value.strip() in k.values()[0].lower().strip()) or ("android" in k.values()[0].lower().strip()):
                    t2 = 1
                if t1:
                  equal_in += 1
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
                if t1:
                  equal_in += 1
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
  page = 0
  if return_numbers >= 20:
    mode = return_numbers%size
    if mode != 0:
      page = return_numbers/size + 1
    else:
      page = return_numbers/size
  else:
    page = 1
  result_dict['return_numbers'] = return_numbers
  result_dict['page_numbers'] = page
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


def count_in(key_word, list_job_name):
  for i in list_job_name:
    if key_word == i.lower():
      return 0
    elif key_word in i.lower():
      return 1
  return 2


# 搜索岗位名时，只考虑岗位名
def test_price(key_word="", ip= "115.231.92.103",port="8085"):
  result_dict = {}
  result_dict['key_word'] = key_word.decode("utf8")
  key_word=key_word.lower()
  query_dsl = get_query_job_name(key_word, ip=ip, port=port)
  result_dict['remark'] = "岗位"
  query_key = "work_experience.seged_job_name"
  query_value = key_word.lower()
  es = Elasticsearch("183.131.144.102:8090")
  size = 20
  res = es.search(index='supin_resume',doc_type='doc_v1',from_=0,size=size,explain=True,_source_include=["resume_update_time","price","work_experience.job_name"],body=query_dsl)
  return_numbers = res['hits']['total']
  l = len(res['hits']['hits'])
  resume_list_first = []
  resume_list_first_job = []
  for i in range(0, l):
    j = res['hits']['hits'][i]['_source']
    if j:
      if j.has_key("price"):
        a = j["price"]
      else:
        a = 9999

      if j.has_key("resume_update_time"): 
        b = j["resume_update_time"]
      else:
        b = ""

      if j.has_key("work_experience"): 
        temp_list = []
        for j in j["work_experience"]:
          temp_list.append(j["job_name"])
        c = count_in(key_word, temp_list)
      else:
        c = ""

      resume_list_first.append((a,b))
      resume_list_first_job.append((a,b,c))
  
  # print u"首页" 
  error1 = 0
  error1_list = []
  # 比较一下同一日期，价格是否升序？ 
  # print u"同一日期，价格是否升序"
  df = pd.DataFrame(columns=("price", "date"))
  l = len(resume_list_first)
  for i in range(l):
    df.loc[i] = resume_list_first[i]
  list_date = list(df["date"])
  for i in set(list_date):
    # 检测有没有非数字的
    # print i,
    diff_series = df[df["date"]==i]["price"].diff()
    bool_se = diff_series.values < 0
    if sum(bool_se) > 0:
      # 同一日期时有价格高的排在价格低的前面
      error1 = 1
    else:
      error1 = 0
    error1_list.append(error1)
    # print error1

  # 同一日期和同一价格时，前面的相关度是否较高？
  error2 = 0
  error2_list = []
  # print u"同一日期和同一价格时，前面相关度是否较高"
  df = pd.DataFrame(columns=("price", "date", "job_name"))
  l = len(resume_list_first_job)
  for i in range(l):
    df.loc[i] = resume_list_first_job[i]
  for (k1, k2), group in df.groupby(["price","date"]):
    # print k1,k2,
    diff_series = group["job_name"].diff()
    bool_se = diff_series.values < 0
    if sum(bool_se) > 0:
      error2 = 1
    else:
      error2 = 0
    error2_list.append(error2)
    # print error2

  return_numbers = res['hits']['total']
  page = 0
  if return_numbers >= 20:
    mode = return_numbers%size
    if mode != 0:
      page = return_numbers/size + 1
    else:
      page = return_numbers/size
  else:
    page = 1
  result_dict['return_numbers'] = return_numbers
  result_dict['page_numbers'] = page
  
  from_value = 0
  size_value =20
  resume_list_end = []
  resume_list_end_job = []
  if return_numbers > 40:
    mul = return_numbers/20
    from_value = (mul-1)*20 
    res = es.search(index='supin_resume',doc_type='doc_v1',from_=from_value,size=size_value,explain=True,_source_include=["resume_update_time","price","work_experience.job_name"],body=query_dsl)
    l = len(res['hits']['hits'])
    for i in range(0, l):
      j = res['hits']['hits'][i]['_source']
      if j:
        if j.has_key("price"):
          a = j["price"]
        else:
          a = 9999

        if j.has_key("resume_update_time"): 
          b = j["resume_update_time"]
        else:
          b = ""

        if j.has_key("work_experience"): 
          temp_list = []
          for j in j["work_experience"]:
            temp_list.append(j["job_name"])
          # c = temp_list
          c = count_in(key_word, temp_list)
        else:
          # 如果没有job_name的时候，设置为不在里面
          c = 2

        resume_list_end.append((a,b))
        resume_list_end_job.append((a,b,c))    

  # print u"\n倒数第二页" 
  # print u"同一日期，价格是否升序"
  error3 = 0
  df = pd.DataFrame(columns=("price", "date"))
  l = len(resume_list_first)
  for i in range(l):
    df.loc[i] = resume_list_first[i]
  list_date = list(df["date"])
  error3_list = []
  for i in set(list_date):
    # print i,
    diff_series = df[df["date"]==i]["price"].diff()
    bool_se = diff_series.values < 0
    if sum(bool_se) > 0:
      error3 = 1
    else:
      error3 = 0
    error3_list.append(error3)
    # print error3

  # print u"同一日期和同一价格时，前面相关度是否较高"
  error4 = 0
  df = pd.DataFrame(columns=("price", "date", "job_name"))
  l = len(resume_list_end_job)
  for i in range(l):
    df.loc[i] = resume_list_end_job[i]
  error4_list = []
  for (k1, k2), group in df.groupby(["price","date"]): 
    # print k1,k2,
    diff_series = group["job_name"].diff()
    bool_se = diff_series.values < 0
    if sum(bool_se) > 0:
      error4 = 1
    else:
      error4 = 0
    error4_list.append(error4)
    # print error4
  dict = {}

  if 1 in error1_list:
    error1_list = "异常"
  else: 
    error1_list = "正常"
  if 1 in error2_list:
    error2_list = "异常"
  else: 
    error2_list = "正常"
  if 1 in error3_list:
    error3_list = "异常"
  else: 
    error3_list = "正常"
  if 1 in error4_list:
    error4_list = "异常"
  else: 
    error4_list = "正常"
  dict["error1"] = error1_list
  dict["error2"] = error2_list
  dict["error3"] = error3_list
  dict["error4"] = error4_list
  dict["key_word"] = key_word
  return dict


def create_data(dd):
  data_list = [dd["key_word"],dd["error1"],dd["error2"],dd["error3"],dd["error4"]]
  return data_list  

def create_table():
  attributes = [u"搜索词",u"首页①",u"首页②",u"尾页①",u"尾页②"]
  x = PrettyTable(attributes) 
  x.padding_width = 20 # One space between column edges and contents (default)  
  x.align["搜索词"] = "l" # Left align city names 
  x.align["首页①"] = "l" 
  x.align["首页②"] = "l" 
  x.align["尾页①"] = "l" 
  x.align["尾页②"] = "l" 
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
  msg_head = msg_head + """<h2>价格排序自动化测试报表</h2>"""
  remark = """<td>备注：①同一日期，价格是否升序<br>
%s②同一日期和同一价格时，前面相关度是否较高 </td></br>""" % ("&nbsp;" * 10)
 
  if ip == "115.231.92.103" and port == "8085":
    remark2 = """<td>IP：""" + ip + """&nbsp;&nbsp;&nbsp PORT：""" + port + """&nbsp;&nbsp;&nbsp按简历价格排序""" +"""</td></br>""" 
  elif ip == "115.231.92.103" and port == "8086":
    remark2 = """<td>IP：""" + ip + """&nbsp;&nbsp;&nbsp PORT：""" + port + """&nbsp;&nbsp;&nbsp未按简历价格排序""" +"""</td></br>""" 
  elif ip == "115.231.92.103" and port == "8087":
    remark2 = """<td>IP：""" + ip + """&nbsp;&nbsp;&nbsp PORT：""" + port + """&nbsp;&nbsp;&nbsp同时匹配岗位名和岗位描述(加职能过滤)""" +"""</td></br>""" 
  else:
    remark2 = """<td>IP:""" + ip + """&nbsp;&nbsp;&nbsp PORT:""" + port + """</td></br>""" 
  html_table = msg_head + html_table + remark2 + remark + "</body></html>"
  html_table = html_table.replace('<table>', '<table class="table">').replace('<td>', '<td style="text-align:right">').replace('<th>', "<th class='table'>")
  return html_table

def mark(html_table,length):
  html_table = html_table.replace("right\">异常","right;color:red;\">异常")
  return html_table


def sendMail(keyWordList):
  mail = BaseFetch.BaseFetch()
  table_list = []
  ip = "115.231.92.103"
  for port in ("8085",):
    table = create_table()
    for i in keyWordList:
      dd = test_price(i, ip=ip, port=port)
      data = create_data(dd)
      table.add_row(data)  
    length = len(keyWordList)
    
    attributes = [u"搜索词",u"首页①",u"首页②",u"尾页①",u"尾页②"]
    html_table = create_html_table(table,attributes,ip=ip,port=port)
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
  html_table = table_list[0].replace("不包含</td>","不包含</td></br><tr><td>&nbsp;</td></tr>")
  html_table = mark(html_table,length)
  mail.send_mails(title='报表06: 搜索自动化测试',msg_txt=html_table,msgtype=0)

if __name__ == '__main__':
  #导致异常的原因可能是：1、某个简历没有job_name  2、某个的排序有问题
  keyWordList = ["","C++","PHP","andorid"]
  sendMail(keyWordList)

 