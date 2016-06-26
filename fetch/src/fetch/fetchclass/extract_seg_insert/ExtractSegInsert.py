# -*- coding: UTF-8 -*-
import re
from bs4 import BeautifulSoup
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time
import json
from elasticsearch import Elasticsearch
import tarfile
import urllib
import urllib2
import cjolextract_new
from  zhilian_parse import zhilian_parse
import chardet
import logging
from simhash import Simhash
from redispipe_for_resume_classify import ResumeClassifyPipe
import shutil

#检查切词后的字典是否有job_status_convert
def check_dict(dict):
  if dict.has_key("job_status_convert"):
    return 1
  else:
    return 0
  
#检查存入搜索库后是否有job_status_convert
def check_es(resume_id):
  es = Elasticsearch("183.131.144.102:8090")
  if resume_id:
    res = es.search(index='supin_resume',doc_type='doc_v1',explain=True,_source_include=["job_status_convert","source","domicile"],body={ 
          "query": {
             "bool":{
               "must":[
                {"match":
                  {
                    "id":{"query": resume_id,"operator":"and","type":"phrase"}
                  }
                }
              ]
            }
          }
        }
      )
  resume = res['hits']['hits'][0]["_source"]
  if resume.has_key("job_status_convert"):
    return resume
  else:
    return 0



# 传入切词后的字典，增加价格字段
def add_price(seged_dict):
  #判断来源
  if seged_dict:
    if seged_dict["source"] == "51job":
      seged_dict["price"] = 5.5
    elif seged_dict["source"] == "cjol":
      seged_dict["price"] = 2.8
    elif seged_dict["source"] == "zhilian":
      if "北京" in seged_dict["domicile"]:
        seged_dict["price"] = 9.5
      elif ("广州" in seged_dict["domicile"]) or ("深圳" in seged_dict["domicile"]):
        # print seged_dict["domicile"]
        seged_dict["price"] = 3
      else:
        pass
    else:
      pass
  return seged_dict

def loadhtml(filename): 
  content = open(filename).read().decode("utf8")
  return content

def lower_dict(resume_dict):
  seged_resume = resume_dict
  seged_resume['seg_major'] = seged_resume['seg_major'].lower()
  for key,value in seged_resume.items():
    if 'seged_' in key:
      seged_resume[key] = seged_resume[key].lower()
    if type(seged_resume[key]) == list:
      if len(seged_resume[key]) != 0:
        length = len(seged_resume[key])
        for i in range(0,length):  
          dict_item = seged_resume[key][i]
          for k,v in dict_item.items():
            if 'seged_' in k:
              dict_item[k] = v.lower()
  return seged_resume
  

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False

#中文数字替换为阿拉伯数字
def myReplace(number_cn):
  dict ={u'零':0,u'一':1,u'二':2,u'三':3,u'四':4,u'五':5,u'六':6,u'七':7,u'八':8,u'九':9,u'十':10}
  if dict.has_key(number_cn):
    working_seniority = dict[number_cn]
  else:
    return int(number_cn)
  return working_seniority
#temp_dict为一个字典，传入最小工作年和最大毕业年
def pre_work_start_time(temp_dict, working_seniority):
  #if temp_dict['max_edu_year'] == "" and temp_dict['min_work_year'] == "":
  #  return 0,0
  if len(working_seniority) == 0:
    #如果有工作经验
    if temp_dict.has_key('min_work_year'):
      dict = {}
      dict['start_work_time'] = int(temp_dict['min_work_year'])
      return '8.1',dict['start_work_time']
    elif temp_dict.has_key('max_edu_year'):
      dict = {}
      dict['start_work_time'] = int(temp_dict['max_edu_year'])
      return '8.2',dict['start_work_time']
    else:
      return '0',0
  dict = {}
  working_seniority = working_seniority.replace(u"工作经验","")
  #当前年份
  y = time.strftime('%Y',time.localtime(time.time()))
  #n年/n-m年
  if working_seniority[-1] == "年": 
    #n年
    if '-' not in working_seniority:
      dict['start_work_time'] = int(y) - int(working_seniority.strip("年"))
      dict['compute_method'] = '1.1'   
    #n-m年
    else:
      #取出n，m
      number_list = working_seniority.strip("年").split("-")
      if temp_dict.has_key('min_work_year'):
        #根据工作经验中最小年份推算
        d = int(y) - int(temp_dict['min_work_year'])
        #判断是否在[n,m]中
        if d >= number_list[0] and d <= number_list[1]:
          dict['start_work_time'] = int(temp_dict['min_work_year'])
          dict['compute_method'] = '2.1'
        elif temp_dict.has_key('max_edu_year'):
          d = int(y) - int(temp_dict['max_edu_year'])
          if d >= number_list[0] and d <= number_list[1]:
            dict['start_work_time'] = int(temp_dict['max_edu_year'])
            dict['compute_method'] = '2.2'
          else:
            dict['start_work_time'] = int(y) - int(number_list[1])
            dict['compute_method'] = '2.3' 
        else:
          dict['start_work_time'] = int(y) - int(number_list[1])
          dict['compute_method'] = '2.3'
      else:  #没有工作经验
        if temp_dict.has_key('max_edu_year'):
          d = int(y) - int(temp_dict['max_edu_year'])
          if d >= number_list[0] and d <= number_list[1]: 
            dict['start_work_time'] = int(temp_dict['max_edu_year'])
            dict['compute_method'] = '2.2'
          else:
            dict['start_work_time'] = int(y) - int(number_list[1])
            dict['compute_method'] = '2.3' 
        else:
          dict['start_work_time'] = int(y) - int(number_list[1])
          dict['compute_method'] = '2.3' 
  #在读生
  elif "在读" in working_seniority :
    dict['start_work_time'] = int(y) + 1
    dict['compute_method'] = '3.1'

  #应届毕业生
  elif "毕业生" in working_seniority :
    dict['start_work_time'] = int(y)
    dict['compute_method'] = '4.1'
  #十年以上
  elif "以上" in working_seniority:
    if working_seniority[0:2] == "10":
      n = working_seniority[0:2]
    else:
      n = working_seniority[0]
    n = myReplace(n)
    if temp_dict.has_key('min_work_year'):
      #假设取出了n
      d = int(y) - int(temp_dict['min_work_year'])
      if d >= n:
        dict['start_work_time'] = int(temp_dict['min_work_year'])
        dict['compute_method'] = '5.1'
      elif temp_dict.has_key('max_edu_year'):
        d = int(y) - int(temp_dict['max_edu_year'])
        if d > n: 
          dict['start_work_time'] = int(temp_dict['max_edu_year'])
          dict['compute_method'] = '5.2'
        else:
          dict['start_work_time'] = int(y) - n
          dict['compute_method'] = '5.3'
      else:
        dict['start_work_time'] = int(y) - n
        dict['compute_method'] = '5.3'
    elif temp_dict.has_key('max_edu_year'): 
      d = int(y) - int(temp_dict['max_edu_year'])
      if d >= n: 
        dict['start_work_time'] = int(temp_dict['max_edu_year'])
        dict['compute_method'] = '5.2'
      else:
        dict['start_work_time'] = int(y) - n
        dict['compute_method'] = '5.3'
    else:
      dict['start_work_time'] = int(y) - n
      dict['compute_method'] = '5.3'
  else:
    pass
  if working_seniority == "Graduating Student":
    dict['start_work_time'] = int(y)
    dict['compute_method'] = '4.1'
  return dict['compute_method'],dict['start_work_time']

# 抽取函数，html_file为html文件名,content为抽取压缩文件时使用的参数,output_dir为输出目录，默认不输出
def extract_51(html_file="", content="", output_dir=""):
  content = content.decode("utf8")
  f_output = open('insert_recode.log','a')
  result_file = open('insert_result.log','a')
  if html_file != "":
    if not os.path.exists(html_file):
      print >>f_output,"no such file",html_file
      return 0
    print >>f_output,'extract file:',html_file
  resume = {}
  if content == "":
    html = loadhtml(html_file)
  else:
    html = content
  # 取出简历ID
  index_id = html.find(u"简历ID：")
  index_mark = html.find('<', index_id)
  id = html[index_id:index_mark].replace("简历ID：","").replace("\r","").replace("\n","")
  resume['id'] = id
  print >>result_file,id,
  soup = BeautifulSoup(html, 'html.parser')
  time_str = '\d{4}/\d{1,2}\-\-\d{4}/\d{1,2}|\d{4}/\d{1,2}\-\-..'
  ## 更新时间
  temp = soup.select("#lblResumeUpdateTime")
  if len(temp) != 0:
    resume['resume_update_time'] = temp[0].get_text().strip(u"更新时间：")
  else:
    resume['resume_update_time'] = "1000-01-01"
    print >>f_output,'no resume_update_time',  

  select_item = soup.select("#divResume")
  if len(select_item) == 0:
    resume = {}
    print >>f_output,u"extract error",
    return 0
  item = select_item[0]
  first_table = item.select("table")[0].select("table")[0].get_text()

  # 户口          匹配"户　口："
  index_hukou = first_table.find(u'户　口：')
  if index_hukou != -1:
    index_2 = first_table.find("：",index_hukou)
    index_3 = first_table.find("\n",index_2)
    resume['household'] = first_table[index_2+1:index_3]
  else:
    resume['household'] = ""

  # 居住地         匹配"居住地："，"户 口："不一定有
  index_juzhudi = first_table.find(u'居住地：')
  if index_juzhudi != -1:
    if index_hukou != -1:
      resume['domicile'] = first_table[index_juzhudi+4:index_hukou]
      # print "domicile",resume['domicile']
    else:
      index = first_table.find("\n",index_juzhudi)
      resume['domicile'] = first_table[index_juzhudi+4:index]
      # print "domicile",resume['domicile']
  else:
    resume['domicile'] = ""

  ## 
  temp = soup.select("span.blue b")
  temp_list = []
  if len(temp) > 0 and temp != None and len(temp[0])>0 :
    for j in temp[0].get_text().split("|"):
      temp_list.append(j.strip())

  #已购买简历,姓名,联系方式
  for b_span in soup.select('b'):
    if soup.title.get_text().strip() == b_span.get_text():
      resume['name'] = soup.title.get_text().strip()

  if html.find('电　话：') > 0:
    tel_start = html.find('电　话：')
    tel_end = html.find('（手机）')
    resume['telephone'] = html[tel_start:tel_end][-11:-1]

  if html.find('E-mail：') > 0:
    resume['email'] = soup.select('a.blue')[-1].get_text()


  #工作年限           匹配：年、以上、应届生、在读、yaer、student
  for element in (u'年工作', u'以上', u'应届', u'在读', u'yaer', u'student',"no"):
    for working_seniority in temp_list:
      if element in working_seniority:
        resume['working_seniority'] = working_seniority
        break
    if resume.has_key('working_seniority'):
        break
  if element == "no":
    resume['working_seniority'] = ""

  # 性别              匹配"男"或"女"
  for sex in (u'男',u'女',"no"):
    if sex in temp_list:
      resume['sex'] = sex 
      break
  if sex == "no":
    resume['sex'] = ""

  pat_high = re.compile('&nbsp;.*?cm')
  high_list = re.findall(pat_high, html)
  if len(high_list):
    high = high_list[0].replace("&nbsp;","").replace("cm","")
    if len(high) > 5:
      return 0
    resume['high'] = int(high)
  else:
    resume['high'] = ""

  # 出生日期         匹配：月或日
  for element in (u'月','no'):
    for birthday in temp_list:  
      if element in birthday:
        if u'岁' in birthday:
          ii = birthday.find(u'岁')
          resume['age'] =  birthday[:ii]
        else:
          resume['age'] = 0
        index1 = birthday.find("（")
        index2 = birthday.find("）")
        resume['birthday'] = birthday[index1+1:index2]
        break
    if resume.has_key('birthday'):
      break
  if element == 'no':
    resume['birthday'] = ""

  #婚姻状况           匹配类型：未婚、已婚、保密
  for marital_status in ('未婚', '已婚', '保密',"no"):
    if marital_status in temp_list:
      resume['marital_status'] = marital_status
      break
  if marital_status == "no":
    resume['marital_status'] = ""

  # 政治面貌      匹配类型：中共党员、团员、民主党派、无党派人士、群众、其他
  for pl_type in ('中共党员', '团员', '民主党派', '无党派人士', '群众', '其他',"no"):
    if pl_type in temp_list:
      resume['political_status'] = pl_type
      break
  if pl_type == 'no':
    resume['political_status'] = ""
  
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  ## 求职意向
  # $("#divInfo table")  简历信息的表
  item_list =(u'目前薪资：', u'自我评价', u'求职意向', u'工作经验',  u'教育经历')
  resumeInfo = soup.select("#divInfo table")
  job_intension_dict = {u'工作性质：':'job_type', u'希望行业：':'expected_industry', u'目标地点：':'expected_city',\
  u'期望薪资：':'expected_salary', u'求职状态：':'job_status', u'目标职能：':'target_functions', \
  u'到岗时间：':'Entry_time',u'关键词：':'key_words'}
  
  for i in resumeInfo:
    info_text = i.get_text()
    # 0 提取目前薪资
    if item_list[0] in info_text:
      index_base_salary1 = info_text.find(u'基本工资：')    #找到'万元/年'
      el = len(u'万元/年')
      if index_base_salary1 != -1:
        index_base_salary2 = info_text.find(u'万元/年', index_base_salary1)
        sl = len(u'基本工资：')
        resume['base_salary'] = info_text[index_base_salary1 + sl:index_base_salary2 + el]
      index_bonus1 = info_text.find(u'奖金/佣金：')
      if index_bonus1 != -1:
        index_bonus2 = info_text.find(u'万元/年', index_bonus1)
        sl = len(u'奖金/佣金：')
        resume['bonus'] = info_text[index_bonus1 + sl:index_bonus2 + el]

      index_allowance1 = info_text.find(u'补贴/津贴：')
      if index_allowance1 != -1:
        index_allowance2 = info_text.find(u'万元/年',index_allowance1)
        sl = len(u'补贴/津贴：')
        resume['allowance'] = info_text[index_allowance1 + sl:index_allowance2 + el]
      
      index_list = [index_base_salary1, index_bonus1, index_allowance1]
      if index_list.count(-1)>0 and index_list.count(-1)<3:
        index_list.remove(-1)
        current_salary_end = min(index_list)
        resume['current_salary'] = info_text[:current_salary_end].strip(item_list[0])
      elif index_list.count(-1) == 0:
        current_salary_end = min(index_list)
        resume['current_salary'] = info_text[:current_salary_end].strip(item_list[0])
      else:
        resume['current_salary'] = info_text.strip(item_list[0])
            
    # 1 提取自我评价 
    if item_list[1] in info_text:
      resume['self_evaluation'] = info_text.strip(item_list[1])
    
    # 2 提取求职意向内容
    if item_list[2] in info_text :
      e_s = 0
      job_intension = (info_text.replace(" ","").replace("\t","").replace("\r","").split("\n"))
      if item_list[2] in job_intension:
        job_intension.remove(item_list[2])
      for i in job_intension:
        if u'面议' in i:
          e_s = 1
      for i in (u'月薪',u'年薪',u'日薪'):
        if i in job_intension:
          index_i = job_intension.index(i)
          job_intension[index_i] =  job_intension[index_i] + job_intension[index_i+1]
          del job_intension[index_i+1]
      l = len(job_intension) 
      for key,value in job_intension_dict.items():
        j = 0
        while j < l:
          if job_intension[j] == key:
            resume[value] = job_intension[j+1]
          j += 2
      
      if e_s == 1:
        resume['expected_salary'] = u'面议'
    if item_list[3] in info_text:
      index = info_text.find(item_list[3])

    if item_list[4] in info_text:
      index = info_text.find(item_list[4])
      four_after = info_text[index+4:index+8]
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  # print u"===================================工作经验"
  work_experience = []
  work_time_list = []
  company_list = []
  working_hours = []
  index_experience = html.find(u'>工作经验<')
  if index_experience != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_ex_to_next = html.find(mark_string, index_experience)
    #匹配到下一个表的出现前，不等于-1是正常，否则是异常
    if index_ex_to_next != -1:
      #取出工作时间列表
      experience_content =  html[index_experience:index_ex_to_next]
      experience_content = experience_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = u'''返回顶部'''
      experience_content =  html[index_experience:index_ex_to_next]
      experience_content = experience_content.replace(" ","").replace("\r","").replace("\n","")
    if experience_content != None: 
      pat_time = re.compile(time_str) 
      work_time_list = re.findall(pat_time, experience_content)
      for i in work_time_list:
        if '-' in i[-2:]:
          work_time_list.remove(i)
      #取出公司名列表
      time_index = []  #保存每个时间的位置，备用
      company_name_list = []
      for worktime in work_time_list:
        index_time = experience_content.find(worktime)
        time_index.append(index_time)
        mark = "<"
        idnex_mark = experience_content.find(mark, index_time)
        company_name_list.append(experience_content[index_time+len(worktime)+1:idnex_mark])
      company_list = company_name_list 

      #取出工作时长列表
      working_hours = []
      pat = re.compile(u'\[.*?\]')
      long_working_hours =re.findall(pat, experience_content)
      for i in long_working_hours:
        if u'月' in i or u'年' in i:
          working_hours.append(i)

      #取出高级人才信息
      senior_talent = {}
      # 汇报对象：
      index_1 = experience_content.find(u'汇报对象：')
      if index_1 != -1:
        index_2 = experience_content.find('''<tdclass="text">''', index_1)
        index_3 = experience_content.find('''</td>''', index_2)
        l = len('''<tdclass="text">''')
        report_objects = experience_content[index_2 + l:index_3]
        senior_talent['report_objects'] = report_objects
      else:
        report_objects = ""
        senior_talent['report_objects'] = report_objects
      #print report_objects

      # 下属人数：
      index_1 = experience_content.find(u'下属人数：')
      if index_1 != -1:
        index_2 = experience_content.find('''<tdclass="text">''', index_1)
        index_3 = experience_content.find('''</td>''', index_2)
        l = len('''<tdclass="text">''')
        subordinate_number = experience_content[index_2 + l:index_3]
        senior_talent['subordinate_number'] = subordinate_number
      else:
        subordinate_number = ""
        senior_talent['subordinate_number'] = subordinate_number
      #print subordinate_number

      #证明人：
      index_1 = experience_content.find(u'证明人：')
      if index_1 != -1:
        index_2 = experience_content.find('''<tdclass="text">''', index_1)
        index_3 = experience_content.find('''</td>''', index_2)
        l = len('''<tdclass="text">''')
        voucher = experience_content[index_2 + l:index_3]
        senior_talent['voucher'] = voucher
      else:
        voucher = ""
        senior_talent['voucher'] = voucher
      #print voucher

      # 离职原因：
      index_1 = experience_content.find(u'离职原因：')
      if index_1 != -1:
        index_2 = experience_content.find('''class="text">''', index_1)
        index_3 = experience_content.find('''</td>''', index_2)
        l = len('''class="text">''')
        reasons_leaving = experience_content[index_2 + l:index_3]
        senior_talent['reasons_leaving'] = reasons_leaving
      else:
        reasons_leaving = ""
        senior_talent['reasons_leaving'] = reasons_leaving

      # 工作业绩：
      index_1 = experience_content.find(u'工作业绩：')
      if index_1 != -1:
        index_2 = experience_content.find('''<tdclass="text">''', index_1)
        index_3 = experience_content.find('''</td>''', index_2)
        l = len('''<tdclass="text">''')
        work_performance  = experience_content[index_2 + l:index_3]
        senior_talent['work_performance'] = work_performance
      else:
        work_performance  = ""
        senior_talent['work_performance'] = work_performance



      #工作经验保存为列表，一段工作经验为一个大字典，字典内嵌套字典
      l = len(time_index)   
      for i in range(0,l):
        exprience_dict = {}
        exprience_dict['senior_talent'] = senior_talent
        if i < l-1:
          industry_info  = experience_content[time_index[i]:time_index[i+1]]
        else:
          industry_info = experience_content[time_index[i]:]
        index_in = industry_info.find(u'所属行业：')
        #所属行业: class="text"> 往后到 </td> 之前的内容
        index1 = industry_info.find('''class="text">''')
        index2 = industry_info.find('''</td>''', index1)
        exprience_dict['industry_belongs'] = industry_info[index1+13:index2]
        #print exprience_dict['industry_belongs']
        #部门:     <tdclass="text_left"><b> 往后到第一个 </b>之前的内容
        index1 = industry_info.find('''<tdclass="text_left"><b>''')
        index2 = industry_info.find('''</b>''', index1)
        exprience_dict['department'] = industry_info[index1+24:index2]   
        #print  exprience_dict['department']  
        #职位名称: <tdclass="text"><b> 往后到第一个 </b>之前的内容
        index1 = industry_info.find('''<tdclass="text"><b>''')
        index2 = industry_info.find('''</b>''', index1)
        exprience_dict['job_name'] = industry_info[index1+19:index2] 
        #print  exprience_dict['job_name']          
        #工作描述: <tdcolspan="2"class="text_left">
        index1 = industry_info.find('''<tdcolspan="2"class="text_left">''')
        index2 = industry_info.find('''</td>''', index1)
        exprience_dict['job_describe'] = industry_info[index1+32:index2].strip(u'工作描述：')
        #print exprience_dict['job_describe']
        work_experience.append(exprience_dict)
  else:
    print >>f_output,u'no work_experience',

  #从公司名中提取公司规模
  company_size = []
  for i in company_list:
    if (u'人)') in i or (u'人以上)') in i:
      pat = re.compile('\(.*\)')
      size = re.findall(pat,i)[0].strip(u'()')
      company_size.append(size)
      i.replace(size, "")
    else:
      company_size.append('')
  numbers_ex = len(working_hours)

  if len(working_hours) > len(work_time_list):
    numbers_ex = len(work_time_list)

  for i in range(0,numbers_ex):
    work_experience[i]['work_time'] = work_time_list[i]
    work_experience[i]['company_name'] = company_list[i].replace('('+company_size[i]+')',"")
    work_experience[i]['working_hours'] = working_hours[i].strip('[]')
    work_experience[i]['company_size'] = company_size[i]

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #print u"===================================教育经历"
  education = []
  ## 教育经历
  index_edu = html.find(u'>教育经历</td>')
  # 教育经历的结束标识
  # 如果找
  if index_edu != -1:
    mark_string = u'''<td align="left" valign="middle" class="cvtitle">'''
    index_edu_to_next = html.find(mark_string, index_edu)
    #匹配到下一个表的出现前，不等于-1是正常，否则是异常
    if index_edu_to_next != -1:
      #取出教育时间列表
      edu_content =  html[index_edu:index_edu_to_next]
      edu_content = edu_content.replace(" ","").replace("\r", "").replace("\n", "")
    else:
      mark_string = u'''返回顶部'''
      index_edu_to_next = html.find(mark_string, index_edu)
      edu_content =  html[index_edu:index_edu_to_next]
      edu_content = edu_content.replace(" ","").replace("\r", "").replace("\n", "")
    pat_time = re.compile(time_str)
    time_list = re.findall(pat_time, edu_content)
    graduate_list = []
    #取出毕业时间
    for i in time_list:
      pat = re.compile(u'\d{4}|至今')
      year_list = re.findall(pat, i)
      for j in range(0,len(year_list)):
        if year_list[j] == u'至今':
          year_list[j] = time.strftime('%Y',time.localtime(time.time()))
        graduate_list.append(int(year_list[j]))
    if len(graduate_list) == 0:
      return 0
    resume['graduate_time'] = max(graduate_list)
    #取出学校、专业、学历
    # class="text"> 与 </td>之间的内容
    pat_school = re.compile('class\=\"text\"\>.*?\</td\>')
    school_major_degree = re.findall(pat_school, edu_content)
    length = len(school_major_degree)
    j = 0
    education = []
    while j < length-1:
      edu_dict = {}

      # i可以表示第i段教育经历
      edu_dict['school'] = school_major_degree[j].replace("</td>","").replace('''class="text">''',"")
      edu_dict['major'] = school_major_degree[j+1].replace("</td>","").replace('''class="text">''',"")
      if j+2 >= len(school_major_degree):
        print "education parse erorr"
        return 0
      edu_dict['degree'] = school_major_degree[j+2].replace("</td>","").replace('''class="text">''',"")
      j += 3
      edu_dict['education_time'] = time_list[j/3-1]
      education.append(edu_dict)
    
    #专业描述
    #class="text_left">  </td>  会将时间一起取出
    pat = re.compile('class\=\"text_left\"\>.*?\</td\>')
    major_describe = re.findall(pat, edu_content)

    major_describe_list = []
    for i in time_list:
      index1 = edu_content.find(i)
      major_describe = re.findall(pat,edu_content[index1:])
      if len(major_describe) == 0:
        major_describe = [""]
      else:
        #处理专业描述里面是专业时间的情况
        s = major_describe[0].replace("</td>","").replace('''class="text_left">''',"")
        istime = re.findall(time_str,s)
        if  len(istime):
          s = s.replace(istime[0],"")
          if len(s) == 0:
            major_describe = [""]      
      major_describe_list.append(major_describe[0].replace("</td>","").replace('''class="text_left">''',""))
    
    l1 = len(education)
    l2 = len(major_describe_list)
    if l1 == l2:
      for i in range(0, l1):
        education[i]['major_describe'] = major_describe_list[i]
  else:
    print  >>f_output,u"no education",
  if not resume.has_key("graduate_time"):
    resume["graduate_time"] = 0
  

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  project = []
  index_project = html.find(u'>项目经验<')
  if index_project != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_project_to_next = html.find(mark_string, index_project)
    #匹配到下一个表的出现前，不等于-1是正常，否则是异常
    if index_project_to_next != -1:
      #取出项目时间列表
      project_content =  html[index_project:index_project_to_next]
      project_content = project_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = u'''返回顶部'''
      index_project_to_next = html.find(mark_string, index_project)
      project_content =  html[index_project:index_project_to_next]
      project_content = project_content.replace(" ","").replace("\r","").replace("\n","")
    if project_content:
      #print project_content
      pat_time = re.compile(time_str)  
      time_list = re.findall(pat_time, project_content)
      index_time_list = []
      for i in time_list:
        index_time_list.append(project_content.find(i))
      l = len(index_time_list)
      for k in range(0,l):
        project_dict = {}
        project_dict['project_time'] = time_list[k]
        if i < l-1:
          temp_content = project_content[index_time_list[k]:index_time_list[k+1]]
        else:
          temp_content = project_content[index_time_list[k]:]
        index_pro_name = temp_content.find(u'</td>')
        if index_pro_name != -1:
          project_dict['project_name'] = temp_content[len(time_list[k])+1:index_pro_name]
          #print project_dict['project_name']
        else:
          project_dict['project_name'] = ""
        index_pro_describe = temp_content.find(u'项目描述：')
        if index_pro_describe != -1:
          index_mark1 = temp_content.find(u'''class="text">''', index_pro_describe)
          index_mark2 = temp_content.find(u'</td>', index_mark1)
          project_dict['project_describe'] = temp_content[index_mark1+len('''class="text">'''):index_mark2]
        else:
          project_dict['project_describe'] = ""
        index_task_describe = temp_content.find(u'责任描述：')
        if index_task_describe != -1:
          index_mark1 = temp_content.find(u'''<tdclass="text">''', index_task_describe)
          index_mark2 = temp_content.find(u'</td>', index_mark1)
          project_dict['task_describe'] = temp_content[index_mark1+len('''<tdclass="text">'''):index_mark2]    
        else:
          project_dict['task_describe'] = ""
        index_dev_tools = temp_content.find(u'开发工具：')
        if index_dev_tools != -1:
          mark_string = '''<tdclass="text">'''
          index_mark1 = temp_content.find(mark_string, index_dev_tools)
          index_mark2 = temp_content.find(u'</td>', index_mark1)
          project_dict['project_dev_tools'] = temp_content[index_mark1+len(mark_string):index_mark2]  
        else:
          project_dict['project_dev_tools'] = ""  

        index_soft_env = temp_content.find(u'软件环境：')
        if index_soft_env != -1:
          mark_string = '''<tdclass="text">'''
          index_mark1 = temp_content.find(mark_string, index_soft_env)
          index_mark2 = temp_content.find(u'</td>', index_mark1)
          project_dict['project_soft_env'] = temp_content[index_mark1+len(mark_string):index_mark2]   
        else:
          project_dict['project_soft_env'] = "" 

        index_hard_env = temp_content.find(u'硬件环境：')
        if index_hard_env != -1:
          mark_string = '''<tdclass="text">'''
          index_mark1 = temp_content.find(mark_string, index_hard_env)
          index_mark2 = temp_content.find(u'</td>', index_mark1)
          project_dict['project_hard_env'] = temp_content[index_mark1+len(mark_string):index_mark2] 
        else:
          project_dict['project_hard_env'] = ""
        project.append(project_dict)

  else:
    print >>f_output,u"no project",

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  prize = []
  index_prize = html.find(u'>所获奖项<')
  if index_prize != -1:
    
    mark_string = '''<td align="left" valign="middle" class="cvtitle">''' 
    index_prize_to_next = html.find(mark_string, index_prize )
    #匹配到下一个表的出现前，不等于-1是正常，否则是异常
    if index_prize_to_next != -1:
      prize_content =  html[index_prize:index_prize_to_next]
      prize_content = prize_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部''' 
      index_prize_to_next = html.find(mark_string, index_prize )
      prize_content =  html[index_prize:index_prize_to_next]
      prize_content = prize_content.replace(" ","").replace("\r","").replace("\n","")
    if prize_content:

      #先取出奖项时间列表  2004/7
      pat_time = re.compile('\d{4}/\d{1}')
      time_list = re.findall(pat_time, prize_content)  
      index_time_list = []
      for i in time_list:
        index_time_list.append(prize_content.find(i))

      l = len(index_time_list)
      for k in range(0,l):
        prize_dict = {}
        if k < l-1:
          temp_content = prize_content[index_time_list[k]:index_time_list[k+1]]
        else:
          temp_content = prize_content[index_time_list[k]:]

        prize_dict['prize_time'] = time_list[k]

        index1 = temp_content.find('''class="text">''')
        index2 = temp_content.find('</td>', index1)
        len_mark = len('''class="text">''')
        prize_dict['prize_name'] = temp_content[index1 + len_mark:index2]

        index3 = temp_content.find('''class="text">''', index1+len_mark)
        if index3 != -1: 
          index4 = temp_content.find('</td>', index3)
          prize_dict['prize_rank'] = temp_content[index3 + len_mark:index4]
        else:
          prize_dict['prize_rank'] = ""
        prize.append(prize_dict)
  else:
    print >>f_output,u"no prize",
  
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #print "===================================学生实践经验"
  experince_prectice = []
  index_prectice = html.find(u'>学生实践经验<')
  if index_prectice != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_prectice_to_next = html.find(mark_string, index_prectice )

    if index_prectice_to_next != -1:
      prectice_content =  html[index_prectice:index_prectice_to_next]
      prectice_content = prectice_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部'''
      index_prectice_to_next = html.find(mark_string, index_prectice )
      prectice_content =  html[index_prectice:index_prectice_to_next]
      prectice_content = prectice_content.replace(" ","").replace("\r","").replace("\n","")
    if prectice_content:

      #先取出实践时间列表
      pat_time = re.compile(time_str)
      time_list = re.findall(pat_time, prectice_content)  
      index_time_list = []
      j = 0
      for i in time_list:
        if j == 0:
          index_time_list.append(prectice_content.find(i))
        else:
          index_time_list.append(prectice_content.find(i,index_time_list[-1] + 1))
        j += 1
      # 每次取一段实践经验
      l = len(index_time_list)
      for k in range(0,l):
        prectice_dict = {}
        if k < l-1:
          temp_content = prectice_content[index_time_list[k]:index_time_list[k+1]]
        else:
          temp_content = prectice_content[index_time_list[k]:]
        # 实践名称   <tdclass="text"> 与 下一个</td>之间
        pat = re.compile(u'''\<tdclass\=\"text"\>.*?\</td\>''')
        prectice_name = re.findall(pat,temp_content)
        if len(prectice_name) > 0:
          prectice_name = prectice_name[0]
          prectice_dict['prectice_name'] = prectice_name.replace('''<tdclass="text">''',"").replace("</td>","")
          # 实践描述   class="text_left"> 与 下一个</td>之间
          pat = re.compile(u'''class\=\"text_left\"\>.*?\</td\>''')
          prectice_describe = re.findall(pat,temp_content)
          if len(prectice_describe):
            prectice_dict['prectice_describe'] = prectice_describe[0].replace('''class="text_left">''',"").replace("</td>","")
          else:
            prectice_dict['prectice_describe'] = ""
          prectice_dict['prectice_time']  = time_list[k]      
          experince_prectice.append(prectice_dict)
    else:
      print u"没有找到结束标记" 
  else:
    print >>f_output,u"no prectice",

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  it_skill = []
  index_it_skill = html.find(u'>IT    技能<')
  if index_it_skill != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_it_skill_to_next = html.find(mark_string, index_it_skill )
    # 匹配到下一个表的出现前，不等于-1是正常，否则是异常
    if index_it_skill_to_next != -1:
      # 取出技能   <tdclass="text_left"> 与下一个 </td> 之间是技能名称
      it_skill_content =  html[index_it_skill:index_it_skill_to_next]
      it_skill_content = it_skill_content
    else:
      mark_string = u'''返回顶部'''
      index_it_skill_to_next = html.find(mark_string, index_it_skill )
      it_skill_content =  html[index_it_skill:index_it_skill_to_next]
      it_skill_content = it_skill_content 

    pat = re.compile(u'''\<td class\=\"text_left\"\>.*?\</td\>''')
    skill_name = re.findall(pat,it_skill_content)
    index_name_list = []
    l = len(skill_name)
    for i in range(0, l):
      skill_name[i] = skill_name[i].replace('''<td class="text_left">''', "").replace("</td>","")
      if i == 0:
        index_name_list.append(it_skill_content.find(skill_name[i]))
      else:
        index_name_list.append(it_skill_content.find(skill_name[i], index_name_list[-1] + len(skill_name[i-1])))

    for k in range(0,l):
      skill_dict = {}
      skill_dict['skill_name'] = skill_name[k]
      if k < l-1:
        temp_content = it_skill_content[index_name_list[k]:index_name_list[k+1]]
      else:
        temp_content = it_skill_content[index_name_list[k]:]
      # 掌握程度 精通、熟练、一般、了解
      for i in ('精通', '熟练', '一般', '了解'):
        if i in temp_content:
          skill_dict['skill_level'] = i
      # 使用时间,以月为单位
      pat = re.compile(u'\d{1}月|\d{2}月')
      use_time = re.findall(pat,temp_content)[0]
      skill_dict['skill_user_time'] = use_time
      it_skill.append(skill_dict)
  else:
    print >>f_output,u"no it_skill",

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  #print "===================================培训经历"
  train = []
  index_train = html.find(u'>培训经历<')

  if index_train != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_train_to_next = html.find(mark_string, index_train )
    #匹配到下一个表的出现前，不等于-1是正常，否则是异常
    if index_train_to_next != -1:
      #循环匹配
      train_content =  html[index_train:index_train_to_next]
      train_content = train_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
      index_train_to_next = html.find(mark_string, index_train )
      train_content =  html[index_train:index_train_to_next]
      train_content = train_content.replace(" ","").replace("\r","").replace("\n","")
    #取出培训时间  必有
    pat_time = re.compile(time_str)  
    time_list = re.findall(pat_time, train_content)
    index_time_list = []
    j = 0
    for i in time_list:
      train_dict = {}
      if j-1 >= 0: 
        index_time_list.append(train_content.find(i, index_time_list[-1]+1))
      else:
        index_time_list.append(train_content.find(i))
      j += 1

    # 每次取一段项目
    l = len(index_time_list)
    for k in range(0,l):
      train_dict = {}
      if k < l-1:
        temp_content = train_content[index_time_list[k]:index_time_list[k+1]]
      else:
        temp_content = train_content[index_time_list[k]:]
      train_dict['training_time'] = time_list[k]
      #培训机构 必有    class="text">-------</td>  第一个一定是
      #培训课程 必有    class="text">-------</td>  第二个一定是
      #获得证书         class="text">-------</td>   没有时中间没有内容
      pat = re.compile('''class\=\"text\"\>.*?\</td\>''')
      temp_list = re.findall(pat,temp_content)
      if len(temp_list) > 0:
        train_dict['training_agency'] = temp_list[0].replace('''class="text">''',"").replace('''</td>''',"")
        train_dict['training_course'] = temp_list[1].replace('''class="text">''',"").replace('''</td>''',"")
        train_dict['training_certificate'] = temp_list[2].replace('''class="text">''',"").replace('''</td>''',"")
        

        #详细描述         class="text_left">--</td>
        pat = re.compile('''class\=\"text\_left\"\>.*?\</td\>''')
        temp_list = re.findall(pat,temp_content)
        if len(temp_list) != 0:
          train_dict['training_describe'] = temp_list[0].replace('''class="text_left">''',"").replace('''</td>''',"")
          train.append(train_dict)
        else:
          train_dict['training_describe'] = ""
        train.append(train_dict)
  else:
    print >>f_output,u'no train',
                
  ## # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
  school_job = []
  index_school_job = html.find(u'>校内职务<')
  if index_school_job != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_school_job_to_next = html.find(mark_string, index_school_job )
    if index_school_job_to_next != -1:
      school_job_content =  html[index_school_job:index_school_job_to_next]
      school_job_content = school_job_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部'''
      index_school_job_to_next = html.find(mark_string, index_school_job )
      school_job_content =  html[index_school_job:index_school_job_to_next]
      school_job_content = school_job_content.replace(" ","").replace("\r","").replace("\n","")
    if school_job_content != None:
      pat_time = re.compile(time_str)
      time_list = re.findall(pat_time, school_job_content) 
      index_time_list = []     
      j = 0
      for i in time_list:
        if j == 0:
          index_time_list.append(school_job_content.find(i))
        else:
          index_time_list.append(school_job_content.find(i,index_time_list[-1] + 1))
        j += 1
      l = len(index_time_list)
      school_job = []
      for k in range(0,l):
        school_job_dict = {}
        if k < l-1:
          temp_content = school_job_content[index_time_list[k]:index_time_list[k+1]]
        else:
          temp_content = school_job_content[index_time_list[k]:]
        
        school_job_dict['school_job_time']  = time_list[k]
        # 职务名称   <tdclass="text"> 与 下一个</td>之间
        pat = re.compile(u'''\<tdclass\=\"text"\>.*?\</td\>''')
        school_job_name = re.findall(pat,temp_content)
        if len(school_job_name) == 0:
          print "school_job error"
          return 0
        else:
          school_job_name = school_job_name[0]
        school_job_dict['school_job_name'] = school_job_name.replace('''<tdclass="text">''',"").replace("</td>","")
        # 职务描述   class="text_left"> 与 下一个</td>之间
        pat = re.compile(u'''class\=\"text_left\"\>.*?\</td\>''')

        school_job_describe = re.findall(pat,temp_content)
        if len(school_job_describe):
          school_job_describe = school_job_describe[0]
          school_job_dict['school_job_describe'] = school_job_describe.replace('''class="text_left">''',"").replace("</td>","")
        else:
          school_job_dict['school_job_describe'] = ""
        school_job.append(school_job_dict)
  else:
    print >>f_output,u"no shcool_job",

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
  #print "===================================证书"
  certificate = []
  pat_temp = re.compile(u'证.*?书') 
  certificate_content = re.findall(pat_temp, html)
  if len(certificate_content):
    index_certificate = html.find(certificate_content[0])
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_certificate_to_next = html.find(mark_string, index_certificate )
    if index_certificate_to_next != -1:
      certificate_content =  html[index_certificate:index_certificate_to_next]
      certificate_content = certificate_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部'''
      index_certificate_to_next = html.find(mark_string, index_certificate)
      certificate_content =  html[index_certificate:index_certificate_to_next]
      certificate_content = certificate_content.replace(" ","").replace("\r","").replace("\n","")

    pat = re.compile('\d{4}/\d{1,2}')
    time_list = re.findall(pat,certificate_content)
    index_time_list = []
    for i in time_list:
      index_time_list.append(certificate_content.find(i))
    # 每次取一段实践经验
    l = len(index_time_list)
    for k in range(0,l):
      certificate_dict = {}
      if k < l-1:
        temp_content = certificate_content[index_time_list[k]:index_time_list[k+1]]
      else:
        temp_content = certificate_content[index_time_list[k]:]
      # 证书名称   class="text"> 与 下一个</td>之间
      pat = re.compile(u'''class\=\"text"\>.*?\</td\>''')
      certificate_name = re.findall(pat,temp_content)
      #print certificate_name
      certificate_dict['certificate_time'] = time_list[k]
      l_certificate = len(certificate_name)
      if l_certificate == 1:
        certificate_name = certificate_name[0].replace('''class="text">''',"").replace("</td>","")
        certificate_grade = ""
      elif l_certificate == 2:
        t = certificate_name
        certificate_name = t[0].replace('''class="text">''',"").replace("</td>","")
        certificate_grade = t[1].replace('''class="text">''',"").replace("</td>","")
      else:
        certificate_name = ""
        certificate_grade = ""
      certificate_dict['certificate_name'] = certificate_name
      certificate_dict['certificate_grade'] = certificate_grade
      certificate.append(certificate_dict)

  else:
    print >>f_output,u'no certificate',    

  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
  language_skills = []
  index_language_skills = html.find(u'>语言能力<')
  if index_language_skills != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_language_skills_to_next = html.find(mark_string, index_language_skills )
    if index_language_skills_to_next != -1:
      language_skills_content =  html[index_language_skills:index_language_skills_to_next]
      language_skills_content = language_skills_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部'''
      index_language_skills_to_next = html.find(mark_string, index_language_skills )
      language_skills_content =  html[index_language_skills:index_language_skills_to_next]
      language_skills_content = language_skills_content.replace(" ","").replace("\r","").replace("\n","")
    #class="text_left">语言类别(掌握程度)</td>
    pat = re.compile('''class\=\"text_left\"\>.*?\</td\>''')
    language_list = re.findall(pat, language_skills_content)
    #语言类比列表中可能有英语等级，匹配出来
    index_language_list = []
    for i in language_list:
      index_language_list.append(language_skills_content.find(i))



    # 每次取一段实践经验
    l = len(index_language_list)
    for k in range(0,l):
      language_skills_dict = {}
      if k < l-1:
        temp_content = language_skills_content[index_language_list[k]:index_language_list[k+1]]
      else:
        temp_content = language_skills_content[index_language_list[k]:]
      #语言掌握程度，在类别名的括号中选取
      language = language_list[k].replace('''class="text_left">''',"").replace("</td>","")
      if language in (u'英语等级：',u'日语等级：', u'TOEFL：', u'GRE：', u'GMAT：', u'TOEIC：'):
        #直接取class="text">专业八级</td>中的内容
        pat = re.compile('''class\=\"text\"\>.*?\</td\>''')
        language_level = re.findall(pat,temp_content)
        if len(language_level):
          if language == u'英语等级：':
            language_skills_dict['english_rank'] = language_level[0].replace('''class="text">''',"").replace("</td>","")
          elif language == u'日语等级：':
            language_skills_dict['japanese_rank'] = language_level[0].replace('''class="text">''',"").replace("</td>","")
          else:
            language_name = language.strip(u'：')
            language_skills_dict['japanese_rank'] = language_level[0].replace('''class="text">''',"").replace("</td>","")
      else:
        pat_level = re.compile(u"\（.*?\）")
        level = re.findall(pat_level, language)
        if len(level):
          language = language.replace(level[0],"")
          level = level[0].strip(u"（）")
        else:
          level = ""
        language_skills_dict['language'] = language
        language_skills_dict['level'] = level

        #听说能力
        pat = re.compile(u"听说\（.*?\）")
        temp_list = re.findall(pat, temp_content)
        if len(temp_list):
          listening_speaking = temp_list[0]
          pat_level = re.compile(u"\（.*?\）")
          level = re.findall(pat_level, listening_speaking)
          if len(level):
            listening_speaking =  listening_speaking.replace(level[0],"")
            level = level[0].strip(u"（）")
          else:
            level = ""
          language_skills_dict['listening_speaking'] = level

        #读写能力
        pat = re.compile(u"读写\（.*?\）")
        temp_list = re.findall(pat, temp_content)
        if len(temp_list):
          reading_writing = temp_list[0]
          pat_level = re.compile(u"\（.*?\）")
          level = re.findall(pat_level, reading_writing)
          if len(level):
            reading_writing = reading_writing.replace(level[0], "") 
            level = level[0].strip(u"（）")
          language_skills_dict['reading_writing'] = level
      language_skills.append(language_skills_dict)
  else:
    print >>f_output,u"no language_skill",
  
  keyword = []
  index_other_info = html.find(u'>自我评价<')
  if index_other_info != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_other_info_to_next = html.find(mark_string, index_other_info )
    if index_other_info_to_next != -1:
      other_info_content =  html[index_other_info:index_other_info_to_next]
      other_info_content = other_info_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部'''
      index_other_info_to_next = html.find(mark_string, index_other_info )
      other_info_content =  html[index_other_info:index_other_info_to_next]
      other_info_content = other_info_content.replace(" ","").replace("\r","").replace("\n","")
    pat = re.compile('''keydiv\"\>.*?\</div''')
    keyword_list = re.findall(pat, other_info_content)
    for i in range(0,len(keyword_list)):
      keyword_list[i] = keyword_list[i].replace("keydiv\">","").replace("</div","")
    keyword = keyword_list
  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
  other_info= []
  index_other_info = html.find(u'>其他信息<')
  if index_other_info != -1:
    mark_string = '''<td align="left" valign="middle" class="cvtitle">'''
    index_other_info_to_next = html.find(mark_string, index_other_info )
    if index_other_info_to_next != -1:
      other_info_content =  html[index_other_info:index_other_info_to_next]
      other_info_content = other_info_content.replace(" ","").replace("\r","").replace("\n","")
    else:
      mark_string = '''返回顶部'''
      index_other_info_to_next = html.find(mark_string, index_other_info )
      other_info_content =  html[index_other_info:index_other_info_to_next]
      other_info_content = other_info_content.replace(" ","").replace("\r","").replace("\n","")
    pat = re.compile('''valign\=\"top\"\>.*?\</td\>''')
    topic_list = re.findall(pat, other_info_content)
    index_topic_list = []
    for i in topic_list:
      index_topic_list.append(other_info_content.find(i))
    # 每次取一段实践经验
    l = len(index_topic_list)
    for k in range(0,l):
      other_info_dict = {}
      other_info_dict['topic'] = topic_list[k].replace('''valign="top">''',"").replace("</td>","").replace("：","")
      if k < l-1:
        temp_content = other_info_content[index_topic_list[k]:index_topic_list[k+1]]
      else:
        temp_content = other_info_content[index_topic_list[k]:] 
      #class="text">内容</td>
      pat = re.compile('''class\=\"text\"\>.*?\</td\>''')
      other_content = re.findall(pat, temp_content)
      if len(other_content):
        other_info_dict['content'] = other_content[0].replace('''class="text">''',"").replace("</td>","")
      other_info.append(other_info_dict)

  else:
    print  >>f_output,u"no other_info"
  l = len(work_experience)
  min_work_year = []
  for i in range(0,l):
     if not work_experience[i].has_key('work_time'):
       return 0
     for j in re.findall('\d{4}',work_experience[i]['work_time']):
        min_work_year.append(int(j))
  temp_dict = {}
  if len(min_work_year) != 0:
    temp_dict['min_work_year'] = min(min_work_year)
  if len(education) > 0:
    temp_dict['max_edu_year'] = resume['graduate_time']
  else:
    if len(work_experience) == 0:
      temp_dict={}
  resume['compute_method'],resume['start_work_time'] = pre_work_start_time(temp_dict, resume['working_seniority'])
  if not resume.has_key('current_salary'):
    resume['current_salary'] = ""
  if not resume.has_key('base_salary'):
    resume['base_salary'] = ""
  if not resume.has_key('bonus'):
    resume['bonus'] = ""
  if not resume.has_key('allowance'):
    resume['allowance'] = ""
  if not resume.has_key('evaluation'):
    resume['evaluation'] = ""
  for key, value in job_intension_dict.items():
    if not resume.has_key(value):
      resume[value] = ""
  resume['current_salary'] = resume['current_salary'].replace("\t","").replace("\r","").replace("\n","")
  resume['expected_salary'] = resume['expected_salary'].replace("\t","").replace("\r","").replace("\n","")
  resume['work_experience'] = work_experience
  resume['education'] = education 
  resume['project'] =  project
  resume['prize'] = prize
  resume['experince_prectice'] = experince_prectice
  resume['it_skill'] = it_skill 
  resume['train'] = train
  resume['school_job'] = school_job
  resume['certificate'] = certificate
  resume['language_skills'] = language_skills
  resume['other_info'] = other_info
  resume['resume_tag'] = " ".join(keyword)
  if len(resume['education']):
    resume['degree'] = resume['education'][0]['degree']
    resume['school'] = resume['education'][0]['major']
    resume['major'] = resume['education'][0]['school']
  f_output.close()
  if output_dir == "":
    return resume
  else:
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
    path,fileName = os.path.split(html_file)
    resume_id = os.path.splitext(fileName)[0]
    json_name = resume_id + '.json'
    dir1 = resume_id[0:3]
    output = os.path.join(output_dir, dir1)
    if not os.path.exists(output):
      os.mkdir(output)
    dir2 = resume_id[3:6]
    output = os.path.join(output, dir2)
    if not os.path.exists(output):
      os.mkdir(output)
    output_json = os.path.join(output,json_name)
    json.dump(resume, open(output_json, 'w'))

def seg(info):
  info = urllib.quote(info.encode('utf8'))
  url = "http://10.4.29.242:8087/segmenter?text=" + info
  # url = "http://183.131.144.102:8087/segmenter?text=" + info
  reload(urllib2)
  req = urllib2.Request(url)
  res_data = urllib2.urlopen(req)
  info = eval(res_data.read())
  return info['segmented_text']

def trans_sex(sex):
  if type(sex) != int:
    if sex == '男':
      return 1
    elif sex == '女':
      return 0
  else:
    return sex


def new_seg(resume):
  # if not resume.has_key('start_work_time'):
  #   temp_dict = {}
  #   temp_dict['min_work_year'] = resume['min_work_year']
  #   temp_dict['max_edu_year'] = resume['graduate_time']
  #   pre_work_start_time(temp_dict,resume['work_seniority'])
  seged_resume = {}
  if not resume.has_key('work_seniority'):
    resume['work_seniority'] = ""
  if not resume.has_key('start_work_time'):
    resume['start_work_time'] = 0 
  seged_resume['start_work_time'] = int(resume['start_work_time'])
  
  if not resume.has_key('age'):
    resume['age'] = 0
  if u'岁' in resume['age']:
    seged_resume['age'] = int(resume['age'].replace(u'岁',""))
  else:
    seged_resume['age'] = int(resume['age'])

  if not resume.has_key('resume_tag'):
    resume['resume_tag'] = ""
  if len(resume['resume_tag']):
    seged_resume['resume_tag'] = resume['resume_tag']
    seged_resume['seged_resume_tag'] = seg(resume['resume_tag'])
  else:
    seged_resume['resume_tag'] = resume['resume_tag']
    seged_resume['seged_resume_tag'] = ""
  
  if not resume.has_key('birthday'):
    if resume['age'] != 0:
      resume['birthday'] = int(time.strftime('%Y',time.localtime(time.time()))) - int(seged_resume['age'])
      seged_resume['birthday'] = int(resume['birthday'])
    else:
      seged_resume['birthday'] = 0
  else:
    seged_resume['birthday'] = int(resume['birthday'][:4])
  '''1'''
  if not resume.has_key('id'):
    resume['id'] = ""
  seged_resume['id'] = resume['id']
  '''2'''
  if not resume.has_key('sex'):
    resume['sex'] = ""
  seged_resume['sex'] = trans_sex(resume['sex'])
  '''3'''
  if not resume.has_key('expected_city'):
    resume['expected_city'] = ""
  if len(resume['expected_city']):
    seged_resume['expected_city'] = resume['expected_city']
    seged_resume['seged_expected_city'] = seg(resume['expected_city'])
  else:
    seged_resume['expected_city'] = resume['expected_city']
    seged_resume['seged_expected_city'] = ""
  '''4'''
  if not resume.has_key('expected_industry'):
    resume['expected_industry'] = ""
  if len(resume['expected_industry']):
    seged_resume['expected_industry'] = resume['expected_industry']
    seged_resume['seged_expected_industry'] = seg(resume['expected_industry'])
  else:
    seged_resume['expected_industry'] = resume['expected_industry']
    seged_resume['seged_expected_industry'] = ""
  '''5'''
  if not resume.has_key('marital_status'):
    resume['marital_status'] = ""
  if len(resume['marital_status']):
    seged_resume['marital_status'] = resume['marital_status']
  else:
    seged_resume['marital_status'] = ""
  '''6'''
  if not resume.has_key('degree'):
    resume['degree'] = ""
  if len(resume['degree']):
    seged_resume['degree'] = resume['degree']
  else:
    seged_resume['degree'] = ""

  

  '''7'''
  if not resume.has_key('school'):
    resume['school'] = ""
  if len(resume['school']):
    seged_resume['school'] = resume['school']
    seged_resume['seged_school'] = seg(resume['school'])
  else:
    seged_resume['school'] = resume['school']
    seged_resume['seged_school'] = ""

  '''8'''
  if not resume.has_key('start_work_time'):
    resume['start_work_time'] = 0
  seged_resume['start_work_time'] = resume['start_work_time']
  
  
  '''9'''
  if not resume.has_key('resume_update_time'):
    resume['resume_update_time'] = ""
  if len(resume['resume_update_time']):
    seged_resume['resume_update_time'] = resume['resume_update_time']
  else:
    seged_resume['resume_update_time'] = ""
  '''10'''
  if not resume.has_key('graduate_time'):
    resume['graduate_time'] = 0
  if type(resume['graduate_time']) != int:
    if u'至今' in resume['graduate_time']:
      resume['graduate_time'] = int(time.strftime('%Y',time.localtime(time.time())))
  if type(resume['graduate_time']) != int:
    resume['graduate_time'] = resume['graduate_time'][:4]
  seged_resume['graduate_time'] = resume['graduate_time']

  '''11'''
  if not resume.has_key('Entry_time'):
    resume['Entry_time'] = ""
  if len(resume['Entry_time']) > 0:
    seged_resume['Entry_time'] = resume['Entry_time']
    seged_resume['seged_Entry_time'] = seg(resume['Entry_time'])
  else:
    seged_resume['Entry_time'] = resume['Entry_time']
    seged_resume['seged_Entry_time'] = ""
  '''12'''
  if not resume.has_key('expected_salary'):
    resume['expected_salary'] = ""
  if len(resume['expected_salary']) > 0:
    seged_resume['expected_salary'] = resume['expected_salary']
    seged_resume['seged_expected_salary'] = seg(resume['expected_salary'])
  else:
    seged_resume['expected_salary'] = resume['expected_salary']
    seged_resume['seged_expected_salary'] = ""
  '''13'''
  if not resume.has_key('target_functions'):
    resume['target_functions'] = ""
  if len(resume['target_functions']) > 0:
    seged_resume['target_functions'] = resume['target_functions']
    seged_resume['seged_target_functions'] = seg(resume['target_functions'])
  else:
    seged_resume['target_functions'] = resume['target_functions']
    seged_resume['seged_target_functions'] = ""
  '''14'''
  if not resume.has_key('major'):
    resume['major'] = ""
  if len(resume['major']) > 0:
    seged_resume['major'] = resume['major']
    seged_resume['seg_major'] = seg(resume['major'])
  else:
    seged_resume['major'] = resume['major']
    seged_resume['seg_major'] = ""
  '''15'''
  if not resume.has_key('household'):
    resume['household'] = ""
  if len(resume['household']) > 0:
    seged_resume['household'] = resume['household']
    seged_resume['seged_household'] = seg(resume['household'])
  else:
    seged_resume['household'] = resume['household']
    seged_resume['seged_household'] = ""
  '''16'''
  if not resume.has_key('domicile'):
    resume['domicile'] = ""
  if len(resume['domicile']) > 0:
    seged_resume['domicile'] = resume['domicile']
    seged_resume['seged_domicile'] = seg(resume['domicile'])
  else:
    seged_resume['domicile'] = resume['domicile']
    seged_resume['seged_domicile'] = ""
  '''17'''
  if not resume.has_key('job_type'):
    resume['job_type'] = ""
  seged_resume['job_type'] = resume['job_type']
  '''18'''
  if not resume.has_key('job_status'):
    resume['job_status'] = ""
  if len(resume['job_status']) > 0:
    seged_resume['job_status'] = resume['job_status'].strip()
    seged_resume['seged_job_status'] = seg(resume['job_status']).strip()
  else:
    seged_resume['job_status'] = resume['job_status']
    seged_resume['seged_job_status'] = ""
  
  if resume['job_status'] in ("半年内无换工作的计划","一年内无换工作的计划","我暂时不想找工作"):
    seged_resume['job_status_convert'] = 13
  elif resume['job_status'] == "目前正在找工作":
    seged_resume['job_status_convert'] = 12
  elif resume['job_status'] == "观望有好的机会再考虑":
    seged_resume['job_status_convert'] = 14
  elif resume['job_status'] == "我目前处于离职状态，可立即上岗":
    seged_resume['job_status_convert'] = 22
  elif resume['job_status'] == "我目前在职，正考虑换个新环境（如有合适的工作机会，到岗时间一个月左右）":
    seged_resume['job_status_convert'] = 32
  elif resume['job_status'] == "我对现在的工作还算满意，如有更好的工作机会，我也可以考虑。（到岗时间另议）":
    seged_resume['job_status_convert'] = 34
  elif resume['job_status'] == "目前暂无跳槽打算":
    seged_resume['job_status_convert'] = 33
  elif resume['job_status'] == "应届毕业生":
    seged_resume['job_status_convert'] = 41
  else:
    seged_resume['job_status_convert'] = 00
  

  '''19'''
  if not resume.has_key('self_evaluation'):
    resume['self_evaluation'] = ""
  if len(resume['self_evaluation']) > 0:
    seged_resume['self_evaluation'] = replace_html(resume['self_evaluation'])
    seged_resume['seged_self_evaluation'] = seg(resume['self_evaluation'])
  else:
    seged_resume['self_evaluation'] = resume['self_evaluation']
    seged_resume['seged_self_evaluation'] = ""
  '''20'''
  if not resume.has_key("work_experience"):
    resume["work_experience"] = []
  length = len(resume["work_experience"])
  if length > 0:
    seged_resume["work_experience"] = []
    for i in range(0,length):
      temp = {}
      work_dict = resume["work_experience"][i]
      if not work_dict.has_key("company_name"):
        work_dict["company_name"] = ""
      if len(work_dict["company_name"]) > 0:
        temp["company_name"] = replace_html(work_dict["company_name"])
        temp["seged_company_name"] = seg(replace_html(work_dict["company_name"]))
      else:
        temp["company_name"] = work_dict["company_name"]
        temp["seged_company_name"] = ""

      if not work_dict.has_key("job_name"):
        work_dict["job_name"] = ""
      if len(work_dict["job_name"]) > 0:
        temp["job_name"] = replace_html(work_dict["job_name"])
        temp["seged_job_name"] = seg(replace_html(work_dict["job_name"]))
      else:
        temp["job_name"] = work_dict["job_name"]
        temp["seged_job_name"] = ""

      if not work_dict.has_key("job_describe"):
        work_dict["job_describe"] = ""
      if len(work_dict["job_describe"]):
        work_dict["job_describe"] = replace_html(work_dict["job_describe"])
        temp["job_describe"] = work_dict["job_describe"]
        temp["seged_job_describe"] = seg(replace_html(work_dict["job_describe"]))

      if not work_dict.has_key("working_hours"):
        work_dict["working_hours"] = ""
      if len(work_dict["working_hours"]):
        temp["working_hours"] = work_dict["working_hours"]
      else:
        temp["working_hours"] = ""

      if not work_dict.has_key("work_time"):
        work_dict["work_time"] = ""
      if len(work_dict["work_time"]):
        temp["work_time"] = work_dict["work_time"]
      else:
        temp["work_time"] = ""

      if not work_dict.has_key("work_salary"):
        work_dict["work_salary"] = ""
      if len(work_dict["work_salary"]):
        temp["work_salary"] = work_dict["work_salary"]
      else:
        temp["work_salary"] = ""

      if not work_dict.has_key('company_size'): 
        work_dict['company_size'] = ""
      if len(work_dict['company_size']):
        temp['company_size'] = work_dict['company_size']

      if not work_dict.has_key('industry_belongs'): 
        work_dict['industry_belongs'] = ""
      if len(work_dict['industry_belongs']):
        temp['industry_belongs'] = replace_html(work_dict['industry_belongs'])
        temp['seged_industry_belongs'] = seg(replace_html(work_dict['industry_belongs']))
      else:
        temp['industry_belongs'] = work_dict['industry_belongs']
        temp['seged_industry_belongs'] = ""
      seged_resume["work_experience"].append(temp)
  ''' '''
  if not resume.has_key("education"):
    resume["education"] = [] 
  length = len(resume["education"])
  seged_resume["education"] = []
  if length > 0:
    for i in range(0,length):
      temp = {}
      education_dict = resume["education"][i]
      if not education_dict.has_key('education_time'): 
        education_dict['education_time'] = ""
      if len(education_dict['education_time']):
        temp['education_time'] = education_dict['education_time']

      if not education_dict.has_key('school'): 
        education_dict['school'] = ""
      if len(education_dict['school']):
        temp['school'] = education_dict['school']

      if not education_dict.has_key('degree'): 
        education_dict['degree'] = ""
      if len(education_dict['degree']):
        temp['degree'] = education_dict['degree']

      if not education_dict.has_key('major'):
        education_dict['major'] = ""
      if len(education_dict["major"]):
        temp['major'] = education_dict["major"].strip(";")
        education_dict["seged_major"] = seg(education_dict["major"].strip(";"))
      else:
        temp['major'] = education_dict['major']
        temp['seged_major'] = ""

      if not education_dict.has_key('major_describe'): 
        education_dict['major_describe'] = ""
      if len(education_dict['major_describe']):
        temp['major_describe'] = replace_html(education_dict['major_describe'])
        temp['seged_major_describe'] = seg(replace_html(education_dict['major_describe']))
      else:
        temp['major_describe'] = education_dict['major_describe']
        temp['seged_major_describe'] = ""
      seged_resume["education"].append(temp)

  if not resume.has_key("project"):
    resume["project"] = [] 
  length = len(resume["project"])
  seged_resume["project"] = []
  if length > 0:
    for i in range(0,length):
      temp = {}
      project_dict = resume["project"][i]
      if not project_dict.has_key('project_time'): 
        project_dict['project_time'] = ""
      if len(project_dict['project_time']):
        temp['project_time'] = project_dict['project_time']

      if not project_dict.has_key('project_name'): 
        project_dict['project_name'] = ""
      if len(project_dict['project_name']):
        temp['project_name'] = project_dict['project_name']
        temp['seged_project_name'] = seg(project_dict['project_name'])
      else:
        temp['project_name'] = project_dict['project_name']
        temp['seged_project_name'] = ""

      if not project_dict.has_key('project_describe'): 
        project_dict['project_describe'] = ""
      if len(project_dict['project_describe']):
        temp['project_describe'] = replace_html(project_dict['project_describe'])
        temp['seged_project_describe'] = seg(replace_html(project_dict['project_describe']))
      else:
        temp['project_describe'] = project_dict['project_describe']
        temp['seged_project_describe'] = ""

      if not project_dict.has_key('duty_describe'): 
        project_dict['duty_describe'] = ""
      if len(project_dict['duty_describe']):
        temp['duty_describe'] = replace_html(project_dict['duty_describe'])
        temp['seged_duty_describe'] = seg(replace_html(project_dict['duty_describe']))
      else:
        temp['duty_describe'] = project_dict['duty_describe']
        temp['seged_duty_describe'] = ""
      seged_resume["project"].append(temp)

  if not resume.has_key("language_skills"):
    resume["language_skills"] = [] 
  length = len(resume["language_skills"])
  seged_resume["language_skills"] = []
  if length > 0:
    for i in range(0,length):
      temp = {}
      language_dict = resume["language_skills"][i]
      if not language_dict.has_key('language'): 
        language_dict['language'] = ""
      if len(language_dict['language']):
        temp['language'] = language_dict['language']

      if not language_dict.has_key('listening_speaking'): 
        language_dict['listening_speaking'] = ""
      if len(language_dict['listening_speaking']):
        temp['listening_speaking'] = language_dict['listening_speaking']

      if not language_dict.has_key('reading_writing'): 
        language_dict['reading_writing'] = ""
      if len(language_dict['reading_writing']):
        temp['reading_writing'] = language_dict['reading_writing']
      seged_resume["language_skills"].append(temp)

  if not resume.has_key("train"):
    resume["train"] = [] 
  length = len(resume["train"])
  seged_resume["train"] = []
  if length > 0:
    for i in range(0,length):
      temp = {}
      train_dict = resume["train"][i]

      if not train_dict.has_key('training_time'): 
        train_dict['training_time'] = ""
      if len(train_dict['training_time']):
        temp['training_time'] = train_dict['training_time']

      if not train_dict.has_key('training_agency'): 
        train_dict['training_agency'] = ""
      if len(train_dict['training_agency']):
        temp['training_agency'] = train_dict['training_agency']
        temp['seged_training_agency'] = seg(train_dict['training_agency'])
      else:
        temp['training_agency'] = train_dict['training_agency']
        temp['seged_training_agency'] = ""

      if not train_dict.has_key('training_course'): 
        train_dict['training_course'] = ""
      if len(train_dict['training_course']):
        temp['training_course'] = train_dict['training_course']
        temp['seg_training_course'] = seg(train_dict['training_course'])
      else:
        temp['training_course'] = train_dict['training_course']
        temp['seg_training_course'] = ""

      if not train_dict.has_key('training_certificate'): 
        train_dict['training_certificate'] = ""
      if len(train_dict['training_certificate']):
        temp['training_certificate'] = train_dict['training_certificate']

      if not train_dict.has_key('training_describe'): 
        train_dict['training_describe'] = ""
      if len(train_dict['training_describe']):
        temp['training_describe'] = train_dict['training_describe']
      seged_resume["train"].append(temp)

  if not resume.has_key("certificate"):
    resume["certificate"] = [] 
  length = len(resume["certificate"])
  seged_resume["certificate"] = []
  if length > 0:
    for i in range(0,length):
      temp = {}
      certificate_dict = resume["certificate"][i]
      if not certificate_dict.has_key('certificate_name'): 
        certificate_dict['certificate_name'] = ""
      if len(certificate_dict['certificate_name']):
        temp['certificate_name'] = certificate_dict['certificate_name']
      if not certificate_dict.has_key('certificate_time'): 
        certificate_dict['certificate_time'] = ""
      if len(certificate_dict['certificate_time']):
        temp['certificate_time'] = certificate_dict['certificate_time']
  if not resume.has_key('has_contact_info'):
    resume['has_contact_info'] = 0
  seged_resume['seg_major'] = seged_resume['seg_major'].decode('unicode-escape').encode('utf8')
  for key,value in seged_resume.items():
    if 'seged_' in key:
      seged_resume[key] = seged_resume[key].decode('unicode-escape')
      seged_resume[key] = seged_resume[key].encode('utf8')
    if type(seged_resume[key]) == list:
      if len(seged_resume[key]) != 0:
        length = len(seged_resume[key])
        for i in range(0,length):  
          dict_item = seged_resume[key][i]
          for k,v in dict_item.items():
            if 'seged_' in k:
              dict_item[k] = v.decode('unicode-escape').encode('utf8')
  seged_resume = lower_dict(seged_resume)
  return seged_resume

def insert_old(resume_dict, source):
  if not resume_dict.has_key('education') and not resume_dict.has_key('work_experience'):
    logging.info('exsearch return 0 %s' % resume_dict['id'])
    return 0
  else:
    if len(resume_dict['education']) == 0 and len(resume_dict['work_experience']) == 0:
      logging.info('exsearch return 0 %s' % resume_dict['id'])
      return 0
  resume_source = source
  resume_doc = resume_dict
  es = Elasticsearch("10.4.29.242:8090")
  resume_doc['id'] = resume_doc['id'].strip()
  resume_id = resume_doc['id']
  res = es.search(index='supin_resume_v1',doc_type='doc_v1',
    body={
      "query": {
        "bool": {
          "must": [
            { "match": { "id": resume_id }},
            { "match": { "source": resume_source }}
          ]
        }
      }
    }
  )
  hits_number = res['hits']['total']
  print hits_number
  pp = urllib.urlopen('http://183.131.144.102:8090/supin_resume/doc_v1/_search?q=id:'+resume_id+'&pretty=true')
  print json.load(pp)['hits']['total']
  if hits_number == 0:
    resume_doc['source'] = resume_source
    res = es.index(index="supin_resume_v1", doc_type="doc_v1", body=resume_doc)
    time.sleep(0.3)
    result = es.search(index='supin_resume_v1',doc_type='doc_v1',
            body={
              "query": {
                "bool": {
                  "must": [
                    { "match": { "id": resume_doc['id'] }},
                      { "match": { "source": resume_source }}
                  ]
                }
              }
            }
          )
    if result['hits']['total'] == 1:
      logging.info('exsearch return 1 %s' % resume_dict['id'])
      return 1
    else:
      logging.info('exsearch return 9 %s' % resume_dict['id'])
      return 9
  elif hits_number >= 1:
    es_id = res['hits']['hits'][0]['_id']
    update_result = es.update(index='supin_resume_v1',doc_type='doc_v1',id=es_id,
        body={
          "doc":resume_doc
        }
      )
    if update_result['_shards']['successful']==1 and  update_result['_version']>1: 
      logging.info('exsearch return -1 %s' % resume_dict['id'])
      return -1
    else:
      logging.info('exsearch return -4 %s' % resume_dict['id'])
      return -4
  else:
    logging.info('exsearch return -5 %s' % resume_dict['id'])
    return -5

def is_resume_exists(resume_dict):
  '''判断简历是否已经存在'''
  query_dsl = {
    'from' : 0,
    'query' : {
      'filtered' : {
        'query': {
          'bool': {
            'must': [],
            'must_not': []
          }
        }
      }
    }
  }

  must_not_query_dsl = query_dsl['query']['filtered']['query']['bool'][
    'must_not']
  if 'source' in resume_dict:
    must_not_query_dsl.append(
      {'match': {
        'source': resume_dict['source']
      }}
    )
  id = ''
  if 'id' in resume_dict:
    id = resume_dict['id']
    must_not_query_dsl.append(
      {'match': {
        'id': id
      }}
    )
  word_query_dsl = query_dsl['query']['filtered']['query']['bool']['must']
  # 工作经历_公司名，工作经历_职位名
  if 'work_experience' in resume_dict:
    work_experience_list = resume_dict['work_experience']
    for experience_item in work_experience_list:
      # job_name = experience_item['job_name']
      # if len(job_name) > 0:
      #   word_query_dsl.append({
      #     'match' : {
      #       'work_experience.job_name' : {
      #         'query' : job_name,
      #         'type' : 'phrase'
      #       }
      #     }
      #   })
      company_name = experience_item['company_name']
      if len(company_name) > 0:
        word_query_dsl.append({
          'match' : {
            'work_experience.company_name' : {
              'query' : company_name,
              # 'type' : 'phrase'
            }
          }
        })
  # 专业
  if 'major' in resume_dict and len(resume_dict['major']) > 0:
    word_query_dsl.append({
      'match' : {
        'major' : {
          'query' : resume_dict['major'],
          # 'type' : 'phrase'
        }
      }
    })
  # 学校
  if 'school' in resume_dict and len(resume_dict['school']) > 0:
    word_query_dsl.append({
      'match' : {
        'school' : {
          'query' : resume_dict['school'],
          # 'type' : 'phrase'
        }
      }
    })
  # 毕业时间
  if 'graduate_time' in resume_dict and resume_dict['graduate_time']:
    word_query_dsl.append({
      'match' : {
        'graduate_time' : {
          'query' : resume_dict['graduate_time'],
          'type' : 'phrase'
        }
      }
    })
  # 年龄
  if 'age' in resume_dict and resume_dict['age']:
    word_query_dsl.append({
      'match': {
        'age': {
          'query': resume_dict['age'],
        }
      }
    })
  # 简历更新年份
  if 'resume_update_time' in resume_dict and resume_dict['resume_update_time']:
    resume_update_year = resume_dict['resume_update_time'].split('-')[0]
    start_time = resume_update_year + '-01-01'
    end_time = resume_update_year + '-12-31'
    query_dsl['query']['filtered']['filter'] = {
      'range': {
        'resume_update_time': {
          "gte" : start_time,
          "lte" : end_time
        }
      }
    }

  # 搜索条件为空，返回True
  if len(word_query_dsl) == 0:
    logging.info('query_dsl is empty. return True. %s' % id)
    return True
  es = Elasticsearch("10.4.29.242:8090")
  # es = Elasticsearch("127.0.0.1:9200")
  res = es.search(index='supin_resume_v1', doc_type='doc_v1', body=query_dsl)
  # 根据搜索条件能从库中找到简历，通过比较简历更新时间、年龄、工作经历
  # 的simhash距离、教育经历的simhash距离判断是否是同一份简历

  # 对resume_dict中的工作经历、教育经历进行转码，用于计算simhash值
  work_experience_list = []
  if 'work_experience' in resume_dict:
    for experience_item in resume_dict['work_experience']:
      new_experience_dict = {}
      for k, v in experience_item.items():
        if isinstance(v, str):
          new_experience_dict[k.decode('utf8')] = v.decode('utf8')
        else:
          new_experience_dict[k.decode('utf8')] = v
      work_experience_list.append(new_experience_dict)
  edu_experience_list = []
  if 'education' in resume_dict:
    for edu_item in resume_dict['education']:
      new_edu_dict = {}
      for k, v in edu_item.items():
        if isinstance(v, str):
          new_edu_dict[k.decode('utf8')] = v.decode('utf8')
        else:
          new_edu_dict[k.decode('utf8')] = v
      edu_experience_list.append(new_edu_dict)

  if len(work_experience_list) == 0:
    logging.info('experience is empty. return False. %s' % id)
    return False

  # 循环判断从库中搜索到的结果
  count = 0
  for item in res['hits']['hits']:
    count += 1
    if count > 5:
      break
    resume = item['_source']
    db_id = resume['id']

    # 计算工作经历和教育经历的simhash距离
    work_experience = ''
    if 'work_experience' in resume:
      work_experience = str(resume['work_experience'])
    work_distance = Simhash(str(work_experience_list)).distance(\
      Simhash(work_experience))
    edu_experience = ''
    if 'education' in resume:
      edu_experience = str(resume['education'])
    edu_distance = Simhash(str(edu_experience_list)).distance(\
      Simhash(edu_experience))
    # 两个距离同时小于指定值即判断为同一份简历
    if work_distance < 7 and edu_distance < 9:
      logging.info('return True. %s,%s. distance:%s,%s' % (\
        id, db_id, work_distance, edu_distance))
      return True
    else:
      logging.info('distance too big. %s,%s. distance:%s,%s' % (id, db_id,\
        work_distance, edu_distance))
  logging.info('return False. %s' % id)
  return False

def insert(resume_dict, source, operation):
  resume_dict.setdefault('education', [])
  resume_dict.setdefault('work_experinece', [])
  if len(resume_dict["work_experience"]) == 0:
    logging.info('exsearch return 0 %s' % resume_dict['id'])
    return 0
  length_checker = False
  for work_experience in resume_dict["work_experience"]:
    if len(work_experience["job_describe"]) > 10:
      length_checker = True
      break
  if length_checker == False:
    logging.info('exsearch return 0 %s' % resume_dict['id'])
    return 0
  resume_source = source
  resume_dict = resume_dict
  es = Elasticsearch("10.4.29.242:8090")
  # es = Elasticsearch("127.0.0.1:9200")
  resume_dict['id'] = resume_dict['id'].strip()
  resume_id = resume_dict['id']
  if operation == 1:
    # 先判断简历是否已经存在
    resume_exists = is_resume_exists(resume_dict)
    # print resume_exists
    if not resume_exists:
      resume_dict['source'] = resume_source
      res = es.index(index="supin_resume_v1", doc_type="doc_v1", body=resume_dict)
      if res.has_key("_id"):
        logging.info('exsearch return 1 %s' % resume_dict['id'])
        return 1
      else:
        logging.info('exsearch return 0 %s' % resume_dict['id'])
        return 0
  elif operation == -1:
    res = es.search(index='supin_resume_v1',doc_type='doc_v1',
      body={
        "query": {
          "bool": {
            "must": [
              { "match": { "id": resume_id }},
              { "match": { "source": resume_source }}
            ]
          }
        }
      }
    )
    if res['hits']['total'] >= 1:
      es_id = res['hits']['hits'][0]['_id']
    else:
      logging.info('exsearch return -4 %s' % resume_dict['id'])
      return -4
    #取出内容
    check_dict = res["hits"]["hits"][0]["_source"]
    # 判断是否存在is_delete键
    if check_dict.has_key("is_delete"):
      if check_dict["is_delete"] == 1:
        resume_dict["is_delete"] = 1

    update_result = es.update(index='supin_resume_v1',doc_type='doc_v1',id=es_id,
        body={
          "doc":resume_dict
        }
      )
    if update_result['_shards']['successful']==1 and  update_result['_version']>1: 
      logging.info('exsearch return -1 %s' % resume_dict['id'])
      return -1
    else:
      logging.info('exsearch return 0 %s' % resume_dict['id'])
      return 0
  else:
    logging.info('exsearch return -5 %s' % resume_dict['id'])
    return -5


''' 一次性完成三个操作，不产生中间文件 '''
''' source = 51job / cjol / zhilian'''
''' operation=1:入库 operation=-1:更新'''
''' 正常入库:1 正常更新:-1 已在库中搜索失败:-4 没有工作经验和教育经历:0 解析有问题:-2 来源有问题:-3 操作有问题:-5'''
def fetch_do123(html_file, source, operation):
  start = time.time()
  result_file = open('insert_result.log','a')
  if source == "51job":
    resume_dict = extract_51(content=html_file)
  elif source == "cjol":
    resume_dict = json.loads(cjolextract_new.json_output(html_file)[0])
  elif source == "zhilian":
    app = zhilian_parse()
    resume_dict = app.run_parse(html_file)
  else:
    return 0,-3
  if resume_dict != 0:
    seged_dict = new_seg(resume_dict)
    seged_dict["source"] = source
    # print "after_seg",check_dict(seged_dict)
    seged_dict = add_price(seged_dict)
    result = insert(resume_dict=seged_dict, source=source, operation=operation)
    # print "after_es",check_es(seged_dict["id"])

    # 若插入或更新成功，则向简历分类队列发送一条消息
    print 'insert result:', result
    if result == 1 or result == -1:
      rcp = ResumeClassifyPipe()
      rcp.producer(seged_dict['id'])

    return_info = {}
    y = time.strftime('%Y',time.localtime(time.time()))
    return_info['id'] = seged_dict['id']
    return_info['sex'] = seged_dict['sex']
    return_info['age'] = int(y) - seged_dict['birthday']
    return_info['work_year'] = int(y) - seged_dict['start_work_time']
    return_info['domicile'] = seged_dict['domicile']
    return_info['degree'] = seged_dict['degree']
    return_info['resume_update_time'] = seged_dict['resume_update_time']
    return  return_info, result, seged_dict
  else:
    return 0,-2

''' 按照目录批量进行处理123，不保存中间文件 '''
def dir_do123(input_dir, source):
  list_dirs = os.walk(input_dir)
  for root, dirs, files in list_dirs:
    for f in files: 
      html_file = os.path.join(root, f)
      fetch_do123(html_file, source)

''' 目录抽取、切词操作。中间文件不保存。设置输出目录，否则默认在输入目录子目录下新建一个子目录output作为输出 '''
def dir_do12(input_dir, source, output_dir = ""):
  if not os.path.exists(input_dir):
    print u"没有此输入目录"
  if output_dir == "":
    path_str_list = input_dir.split("\\")
    output_dir = ""
    if len(path_str_list[-1]) == 0:
      for i in path_str_list[:-2]:
        print output_dir
        output_dir = os.path.join(output_dir, i)
    else:
      for i in path_str_list[:-1]:
        output_dir = os.path.join(output_dir, i)
        print output_dir
    output_dir = os.path.join(output_dir,'output')
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
  # 取出单个文件
  list_dirs = os.walk(input_dir)
  for root, dirs, files in list_dirs:
    for f in files: 
      html_file = os.path.join(root, f)
      if source == "51job":
        resume_dict = extract_51(html_file)
      elif source == "cjol":
        resume_dict = extract_cjol(html_file)
      elif source == "zhilian":
        resume_dict = extract_zhilian(html_file)
      else:
        return 0
      if resume_dict == 0:
        continue
      else:
        seged_dict = new_seg(resume_dict=resume_dict)
        resume_id = os.path.splitext(f)[0]
        json_name = resume_id + '.json'
        output_json = os.path.join(output_dir,json_name)
        json.dump(seged_dict, open(output_json, 'w'))

''' 目录切词、入库操作。中间文件不保存。 '''
def dir_do23(input_dir, source):
  if not os.path.exists(input_dir):
    print u"没有此输入目录"
    return None
  list_dirs = os.walk(input_dir)
  for root, dirs, files in list_dirs:
    for f in files: 
      json_file = os.path.join(root, f)
      with open(json_file, 'r') as f:
        resume = json.load(f) 
      resume_dict = new_seg(resume)
      insert_test(resume_dict=resume_dict, source=source)

''' 目录抽取操作。当不指定目录输出时，自动在输入目录的子目录创建输出目录进行输出'''
def dir_do1(input_dir, source, output_dir = ""):
  if output_dir == "":
    path_str_list = input_dir.split("\\")
    if len(path_str_list[-1]) == 0:
      for i in path_str_list[:-2]:
        output_dir = os.path.join(output_dir, i)
    else:
      for i in path_str_list[:-1]:
        output_dir = os.path.join(output_dir, i)
    output_dir = os.path.join(output_dir,'output')
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
  list_dirs = os.walk(input_dir)
  for root, dirs, files in list_dirs:
    for f in files:
      if os.path.splitext(f)[1] == ".html":
        fileName = os.path.join(root, f)
        if source == "51job":
          resume_dict = extract_51(html_file)
        elif source == "cjol":
          resume_dict = extract_cjol(html_file)
        elif source == "zhilian":
          resume_dict = extract_zhilian(html_file)
        else:
          return 0
        resume_id = os.path.splitext(f)[0]
        dir1 = resume_id[0:3]
        output = os.path.join(output_dir, dir1)
        if not os.path.exists(output):
          os.mkdir(output)
        dir2 = resume_id[3:6]
        output = os.path.join(output, dir2)
        if not os.path.exists(output):
          os.mkdir(output)
        json_name = resume_id + '.json'
        output_json = os.path.join(output,json_name)
        json.dump(resume_dict, open(output_json, 'w'))

''' 目录切词操作。当不指定目录输出时，自动在输入目录的同级目录创建输出目录进行输出'''
def dir_do2(input_dir,output_dir = ""):
  if output_dir == "":
    output_dir = os.path.join(input_dir,'output')
    if not os.path.exists(output_dir):
      os.mkdir(output_dir)
  list_dirs = os.walk(input_dir)
  for root, dirs, files in list_dirs:
    for f in files:
      if os.path.splitext(f)[1] == ".json":
        fileName = os.path.join(root, f)
        print fileName
        with open(fileName, 'r') as f:
          resume = json.load(f) 
        resume_dict = new_seg(resume)
        resume_id = resume_dict['id'].replace("\n","")
        json_name = resume_id + '.json'
        output_json = os.path.join(output_dir,json_name)
        json.dump(resume_dict, open(output_json, 'w'))

''' 目录入库操作。'''
def dir_do3(input_dir):
  list_dirs = os.walk(input_dir)
  for root, dirs, files in list_dirs:
    for f in files:
      if os.path.splitext(f)[1] == ".json":
        print f,"strat to insert!"
        fileName = os.path.join(root, f)
        with open(json_file, 'r') as f:
          resume = json.load(f)   
        insert(resume)

''' 直接对一个压缩文件中的html文件进行抽取，tarfile压缩文件，output输出目录 '''
def extract_tar(tar_file, output_dir):
  tar = tarfile.open(tar_file, 'r:gz')  
  for tar_info in tar: 
    path_file = tar_info.name
    file = tar.extractfile(tar_info)
    if file != None:
      content = file.read()      
      extract(html_file=path_file,content=content,output_dir=output_dir)

def replace_html(value):
    html_dict = {"&nbsp;":"\t","&amp;":"&","&gt;":">","&lt;":"<","&quot;":"\"","&qpos;":"'","\r":"","<br>":"\n",\
'''<font color="red">''':"","</font>":"","< br>":"","< br >":"","&#x20;":" "}
    for k,v in html_dict.items():
        value = value.replace(k,v)
    return value
