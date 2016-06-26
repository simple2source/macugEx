# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json
import re
import sys
import datetime
import os

expect_job = u'\u6c42\u804c\u610f\u5411'
skill = u'\u6280\u80fd\u4e13\u957f'
attach = u'\u9644\u4ef6\u7b80\u5386'
edu = u'\u6559\u80b2\u80cc\u666f'
work = u'\u5de5\u4f5c\u7ecf\u5386'
baseinfo = u'\n\u3010 \u57fa\u672c\u4fe1\u606f\u3011\n   '
work_describe_detail = u'\u5de5\u4f5c\u7ecf\u5386\u8be6\u7ec6\u4ecb\u7ecd'
lang = u'\u8bed\u8a00\u80fd\u529b\u4e0e\u6280\u5de7'
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

def br2n(soup):
    """替换soup格式里面的 <br> 的标签, 然后又转为 beautifulsoup 对象"""
    s = re.sub('<br\s*?>', '\n', unicode(soup))
    s2 = BeautifulSoup(s, 'html.parser')
    return s2

def analytics_m(fname, tp=0):
    html = resume_fname(fname, tp)
    soup = BeautifulSoup(html, "html.parser")
    common_box = soup.find_all('table', {'width': '100%', 'border': '0', 'cellpadding': '0', 'class': 'common_box'})
    base_info = {}
    expected = {}
    work_experience_list = []
    education_list = []
    attachment_list = []
    skill_describe_list = []
    work_describe_detail_dict = {}
    other_language = []
    second_language_dict = {}
    resume_id = soup.find('td',{'class':'resume_info_up'}).contents[1]
    up_date = soup.find('td',{'class':'resume_info_down'}).contents[1]
    up_date = up_date.split()[0]
    base_info['resume_update_time'] = up_date
    base_info['id'] = resume_id
    print resume_id, up_date

    #独立找出 个人信息
    person_con = soup.find('td',{'class':'jobseekerbaseinfo_con'})
    # print person_con

    jobb = person_con.find_all('td', {'class': 'field_fontsize'})
    base_info['expected_salary'] = jobb[0].get_text().split(u'\uff1a')[1]
    # print base_info['expected_salary']
    salary_str = jobb[1].get_text()
    working_seniority = re.search('\d+.\d+', salary_str)
    if working_seniority:
        working_seniority = float(working_seniority.group())
        working_seniority = int(round(working_seniority))
    else:
        working_seniority = 0
    # print working_seniority
    base_info['working_seniority'] = working_seniority

    base_con = person_con.find_all('td', {'class': ['field_right', 'field_right_long']})
    base_til = person_con.find_all('td', {'class': ['field_left']})
    base_key_list = ['degree', 'sex', 'current_industry', 'school', 'age', 'current_work',  'major',
                     'high', 'english_skill_total', 'marital_status',  'computer_skill']
    # for base_i in base_con:
    #     # print base_i.get_text()
    #     base_info[base_key_list[base_con.index(base_i)]] = string_format(base_i.get_text())

    for base_t in base_til:
        if base_t.get_text() == u'学历：':
            base_info['degree'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'性别：':
            base_info['sex'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'目前行业：':
            base_info['current_industry'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'毕业院校：':
            base_info['school'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'年龄：':
            base_info['age'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'目前岗位：':
            base_info['current_work'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'专业：':
            base_info['major'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'身高：':
            base_info['high'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'外语：':
            base_info['english_skill_total'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'婚否：':
            base_info['marital_status'] = string_format(base_t.find_next().get_text())
        if base_t.get_text() == u'计算机：':
            base_info['computer_skill'] = string_format(base_t.find_next().get_text())

    try:
        en_list =  base_info['english_skill_total'].split()
        base_info.pop('english_skill_total', None)

        base_info['english_rank'] = ''
        base_info['english_skill'] = ''
        for i in en_list:
            if i.find(u'级') > 0:
                base_info['english_rank'] = i
                en_list.pop(en_list.index(i))
        if len(en_list) > 1:
            base_info['english_skill'] = en_list[1]
    except:
        base_info['english_rank'] = ''
        base_info['english_skill'] = ''

    # print base_info['english_skill'], base_info['english_rank'], 888888888888

    for common_box_content in common_box[:-1]:
        title = common_box_content.find('td',{'class':'common_tit'}).get_text()
        common_con = common_box_content.find('td',{'class': 'common_con'})
        # print title
        if title == expect_job:
            expect_info = common_con.find_all('td', {'class': ['common_right_l', 'common_right_r', 'common_right']})
            info_key_list = ['expected_industry', 'Entry_time', 'target_functions',
                             'house_required', 'expected_city']
            #print expect_info
            for expect_i in expect_info:
                #print expect_i.get_text()
                expected[info_key_list[expect_info.index(expect_i)]] = string_format(expect_i.get_text())
            #print expected
            for key in expected:
                base_info[key] = expected[key]

        if title == work:
            work_total = common_con.find_all('table', {'width': '100%', 'border': '0', 'cellspacing': '0'})

            for work_t in work_total:
                work_experience_dict = {}
                not_avail = work_t.find('td', {'class':  'gap_between_tit'})
                if not not_avail:
                    work_info = work_t.find('td', {'class': 'work_experience'}).find_all('span')
                    info_key_list = [ 'company_name', 'job_name', 'work_time', 'work_salary']
                    if work_info:
                        if len(work_info) == 4:
                            for i in work_info:
                                #print work_info.index(i)
                                work_experience_dict[info_key_list[work_info.index(i)]] = string_format(i.get_text())
                            try:
                                work_describe = work_t.find('td', {'class': 'work_experience_describe'})
                                work_describe = br2n(work_describe).get_text()
                            except:
                                work_describe = ''
                            work_experience_dict['job_describe'] = work_describe
                            work_times = work_experience_dict['work_time']
                            work_experience_dict['work_time'] = work_times[:work_times.find(u'（')]
                            work_experience_dict['working_hours'] = work_times[(work_times.find(u'（')+1):work_times.find(u'）')]
                            work_experience_list.append(work_experience_dict)
            #print work_experience_list
            #print 'work'

        if title == work_describe_detail:
            if common_con.get_text():
                work_describe_detail_dict['work_describe_detal'] = string_format(common_con.get_text())
            else:
                work_describe_detail_dict['work_describe_detal'] = ''

        if title == edu:
            #print common_con
            edu_total = common_con.find_all('table', {'width': '100%', 'border': '0', 'cellspacing': '0'})
            for edu_t in edu_total:
                edu_dict = {}
                not_avail = edu_t.find('td', {'class':  'gap_between_tit'})
                if not not_avail:
                    #print edu_t.find('td', {'class': 'work_experience'})
                    edu_info = edu_t.find('td', {'class': 'work_experience'}).find_all('span')
                    info_key_list = [ 'school', 'degree', 'education_time', 'major']
                    for i in edu_info:
                        edu_dict[info_key_list[edu_info.index(i)]] = string_format(i.get_text())
                    td_num = edu_t.find_all('td')
                    if len(td_num) ==3:
                        edu_dict['major'] = td_num[1].get_text()
                    try:
                        edu_describe = edu_t.find('td', {'class': 'work_experience_describe'})
                        edu_describe = br2n(edu_describe).get_text()
                    except:
                        edu_describe = ''
                    edu_dict['edu_describe'] = edu_describe
                    education_list.append(edu_dict)
            #print education_list

        if title == skill:
            #print common_con
            skill_total = common_con.find('table', {'width': '100%', 'border': '0', 'cellspacing': '0'})
            try:
                skill_describe_info = br2n(skill_total).get_text()
                skill_describe_info = string_format(skill_describe_info)
            except:
                skill_describe_info = ''
            base_info['self_evaluation'] = skill_describe_info
            # skill_dict = {'skill_describe': skill_describe_info}
            # skill_describe_list.append(skill_dict)
            #print skill_describe_list

        if title == lang:
            #print 'laskjdfla'
            language_con = common_con.find('table', {'width': '100%', 'border': '0', 'cellspacing': '0'})

            try:
                second_language = language_con.get_text()
            except:
                second_language = ''
            second_language_dict['second_language'] = string_format(second_language)
            #other_language.append(second_language_dict)
            #print other_language

        if title == attach:
            #print 222
            attachment_list.append({'have_attachment':'yes'})
            #print attachment_list

    return base_info, work_experience_list, second_language_dict,  education_list, attachment_list


def json_output(fname, tp=0):
    [base_info, work_experience_list, second_language_dict,  education_list, attachment_list] = analytics_m(fname, tp)
    base_info['work_experience'] = work_experience_list
    base_info['education'] = education_list
    #base_info['skill_describe'] = skill_describe_list
    #base_info['addition'] = addition_list
    base_info['attachment'] = attachment_list
    base_info['graduate_time'] = 0
    try:
        education_time =  education_list[0]['education_time']
        base_info['graduate_time'] = education_time[(education_time.find('--')+2):][:4]
    except:
        pass
    #跟 原 json 兼容
    language_skills = []
    english_skill = base_info.pop('english_skill')
    english_rank = base_info.pop('english_rank')
    lan_dict1 = {"listening_speaking":english_skill, "reading_writing": english_skill, "language": u"\u82f1\u8bed", 'level':''}
    lan_dict2 = {'english_rank': english_rank}
    language_skills.append(lan_dict1)
    language_skills.append(lan_dict2)
    language_skills.append(second_language_dict)
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
    #print json_format
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
