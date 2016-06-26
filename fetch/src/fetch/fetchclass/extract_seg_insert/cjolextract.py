# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json
import re
import sys
import datetime

skill =u'\n                                    \u3010\u6280\u80fd\u4e13\u957f\u3011\n                                '
attach = u'\n                                \u3010\u9644\u4ef6\u7b80\u5386\u3011\n                            '
edu = u'\n                                    \u3010\u6559\u80b2\u80cc\u666f\u3011\n                                '
work = u'\n                                    \u3010\u5de5\u4f5c\u7ecf\u9a8c\u3011\n                                '
baseinfo = u'\n                                                \u3010 \u57fa\u672c\u4fe1\u606f\u3011\n                                            '
work_describe_key = u' '
# 技能专长、附件简历、教育经历、工作经验、基本信息、工作经历详细介绍(这个用户自行添加）

def resume_fname(fname, tp=0):
    # 传入参数为0， fname 为字符串，参数为1， fname为文件
    if tp == 0:
        html = fname
    elif tp == 1:
        with open(fname) as f:
            html = f.read()
    return html

def string_format(string):
    #format_string = re.sub('[\s+]', ' ', string)
    format_string = ' '.join(string.split())
    p = re.compile(u'\u81f3')
    format_string = p.sub('--', format_string)
    format_string = format_string.replace('CM', '')
    return format_string

def analytics_main(fname, tp=0):
    # 分析简历主要部分
    html = resume_fname(fname, tp)
    soup = BeautifulSoup(html, "html5lib")
    # 标题
    data = soup.find_all('td',{'class':'lanmu'})
    # 具体信息
    data2 = soup.find_all('table', {'width':"100%", 'border':"0", 'cellpadding':"2", 'cellspacing':"0", 'bgcolor':"#C9DDF1"})


    # 挑出相同的信息组
    l = []
    for data_info in data:
        #print data_info.get_text()
        for data2_info in data2:
            if  data2_info.find_previous('td',{'class':'lanmu'}) == data_info:
                l.append(data.index(data_info))

    base_info = {}
    work_experience_list = []
    education_list = []
    attachment_list = []
    skill_describe_list = []

    # 简历更新时间
    resume_date = soup.find_all('td', {'valign':'middle'})
    llinfo =  resume_date[1].get_text()
    llist = llinfo.split()
    up_date = llist[2][-10:]
    print up_date

    # 简历ID
    resume_id = re.search('J\d+', html).group()
    print resume_id

    base_info['resume_update_time'] = up_date
    base_info['id'] = resume_id

    # 分类
    for data2_info in data2:
        # find data name
        data2_index = data2.index(data2_info)
        l_num = l[data2_index]
        # data name
        data_type = data[l_num].get_text()
        # 分类

        if data_type == baseinfo:

            if data2.index(data2_info) == 0:
                info_key_list = ['name', 'sex', 'age', 'birthday', 'marital_status', 'high', 'domicile', 'household',
                                 'working_seniority', 'english_skill', 'english_rank', 'computer_skill', 'other_lang',
                                 'other_lang_rank', 'degree', 'major']
            if data2.index(data2_info) == 1:
                info_key_list = ['current_work', 'current_salary',
                                 'current_industry', 'expected_salary', 'expected_city', 'house_required', 'expected_industry',
                                 'Entry_time', 'target_functions']
            info_value_list = data2_info.find_all('td',{'class':'fieldContent'})

            for info_value in info_value_list:
                value_info = info_value.contents[0].strip()
                value_info = string_format(value_info)
                key_index = info_value_list.index(info_value)
                base_info[info_key_list[key_index]] = value_info

        if data_type == work:
            work_experience_dict = {}
            info_key_list = ['work_time', 'job_name', 'company_name', 'Chinese_salary', 'work_salary']
            info_value_list = data2_info.find_all('td',{'class':'fieldName'})
            #print info_value_list
            for info_value in info_value_list:
                value_info = info_value.get_text().strip()
                value_info = string_format(value_info)
                key_index = info_value_list.index(info_value)
                work_experience_dict[info_key_list[key_index]] = value_info
            job_describe = data2_info.find_all('td',{'class':'fieldContent'})[0].get_text().strip()
            job_describe = string_format(job_describe)
            work_experience_dict['job_describe'] = job_describe
            work_experience_list.append(work_experience_dict)

        if data_type == edu:
            school_dict = {}
            info_key_list = ['education_time', 'degree', 'major', 'school']
            info_value_list = data2_info.find_all('td',{'class':'fieldName'})
            #print info_value_list
            for info_value in info_value_list:
                value_info = info_value.get_text().strip()
                value_info = string_format(value_info)
                key_index = info_value_list.index(info_value)
                school_dict[info_key_list[key_index]] = value_info
            job_describe = data2_info.find_all('td',{'class':'fieldContent'})[0].get_text().strip()
            job_describe = string_format(job_describe)
            school_dict['major_describe'] = job_describe
            education_list.append(school_dict)

        if data_type == attach:
            attachment_list.append({'have_attachment':'yes'})

        if data_type == skill:
            try:
                skill_describe_info = data2_info.find_all('td',{'class':'fieldContent'})[0].get_text().strip()
            except:
                skill_describe_info = ''
            base_info['self_evaluation'] = skill_describe_info
            # skill_dict = {'skill_describe': skill_describe_info}
            # skill_describe_list.append(skill_dict)

    # 找出用户自行添加信息
    lset = set(l)
    lset2 = set(range(len(data)))
    diff_set = lset ^ lset2
    # print lset, lset2
    # print list(diff_set), len(diff_set)
    addition_list = []
    if len(diff_set) > 0:
        for i in list(diff_set):
            addition_key = data[i].get_text().strip()
            addition_info = data[i].find_next().get_text().strip()
            addition_list.append({('addition' + str(i)): (addition_key + addition_info)})
    #print [base_info, work_experience_list, skill_describe_list, education_list, addition_list]
    return [base_info, work_experience_list, skill_describe_list, education_list, addition_list, attachment_list]

def json_output(fname, tp=0):
    [base_info, work_experience_list, skill_describe_list, education_list, addition_list, attachment_list] = analytics_main(fname, tp)
    base_info['work_experience'] = work_experience_list
    base_info['education'] = education_list
    base_info['skill_describe'] = skill_describe_list
    base_info['addition'] = addition_list
    base_info['attachment'] = attachment_list

    #跟 原 json 兼容
    working_seniority = base_info['working_seniority']
    working_seniority = float(working_seniority.replace(u'年', ''))
    working_seniority = int(round(working_seniority))
    base_info['working_seniority'] = working_seniority

    base_info['graduate_time'] = 0
    if education_list[0]['education_time']:
        education_time =  education_list[0]['education_time']
        base_info['graduate_time'] = education_time[(education_time.find('--')+2):][:4]
    language_skills = []
    english_skill = base_info.pop('english_skill')
    english_rank = base_info.pop('english_rank')
    lan_dict1 = {"listening_speaking":english_skill, "reading_writing": english_skill, "language": u"\u82f1\u8bed", 'level':''}
    lan_dict2 = {'english_rank': english_rank}
    language_skills.append(lan_dict1)
    language_skills.append(lan_dict2)
    base_info["language_skills"] = language_skills
    try:
        max_work_year = base_info['work_experience'][-1]['work_time'][:4]
    except:
        max_work_year = ''
    start_working_time = datetime.date.today().year - base_info['working_seniority']
    base_info['start_work_time'] = start_working_time
    base_info['min_work_year'] = max_work_year

    json_format =  json.dumps(base_info)
    #print json_format
    # 返回 json 格式文件，跟id
    return json_format, base_info['id']

def json_file(fname, tp=0):
    # 写入到文件中
    json_format, resume_id = json_output(fname, tp)
    json_fname = str(resume_id) + '.json'
    with open(json_fname, 'w+') as f:
        f.write(json_format)


if __name__ == "__main__":
    fname = sys.argv[1]
    json_output(fname, tp=1)[0]
    json_file(fname, tp=1)
