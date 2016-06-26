# encoding: utf-8

"""处理传入的json， 选择合适的cookie跟发布脚本"""

import libzlpublish
import lib51publish
import libcjolpublish
import selectuser
import sys, json, random, datetime
import logging
reload(sys)
sys.setdefaultencoding('utf8')

source_json = {
    'source': '51job',
    'job_detail': {
        'job_name': 'lal34ala2222', # 职位名称
        'job_type': '硬件测试',  # 职位类别  这个的话51 的选择太多，先不做判断
        'work_type': '全职',  # 工作性质 全职，兼职
        'city': '广州',  # 发布城市
        'district': '海珠区',  # 区
        'work_address': '高大上', # 上班地址
        'job_num': '15',  # 招聘人数
        'salary': '19320',  # 月薪，输入数字， 判断选择范围
        'work_year': '3',  # 工作年限，输入数字，判断选择范围
        # 可选
        'degree': '博士',  # 学历
        'major': '计算机科学与技术',  # 专业  智联不需要
        # 'publish_day': '2015-12-31',  # 发布日志，只有cjol有
        # 'department': '',  所属公司部门，意义不大
        # 'sex': '男',  # 性别  51job 没有 只有 cjol 有,  智联把区分性别当做歧视
        'welfare': '五险一金 222 111 高温补贴',  # 福利 以空白做分隔符
        'keyword': '高薪 养廉',  # 职位关键词，方便搜索
        'email': 'a@a.com',  # 接受系统自动转发的简历
        'job_describe': '大家好，大家好，大家好。',  # 这是职位描述，用户自行添加
        }
    }

json_str = json.dumps(source_json)

class Cjol(object):
    def __init__(self, j_dict):
        self.j_dict = j_dict
        self.j_type_list = [{'N': '高级硬件工程师', 'I': '010101'}, {'N': '硬件工程师', 'I': '010102'}, {'N': '其他计算机硬件类', 'I': '010199'}, {'N': '系统架构设计师', 'I': '010201'}, {'N': '系统分析师/分析员', 'I': '010202'}, {'N': '高级软件工程师/高级程序员/资深程序员', 'I': '010203'}, {'N': '软件工程师/程序员', 'I': '010204'}, {'N': '数据库管理员（DBA）/数据库开发工程师', 'I': '010205'}, {'N': '算法工程师', 'I': '010206'}, {'N': '计算机辅助设计工程师', 'I': '010207'}, {'N': 'ERP技术开发', 'I': '010208'}, {'N': '其他计算机软件类', 'I': '010299'}, {'N': '测试经理/主管', 'I': '010301'}, {'N': '系统测试', 'I': '010302'}, {'N': '硬件测试', 'I': '010303'}, {'N': '软件测试', 'I': '010304'}, {'N': '手机测试', 'I': '010305'}, {'N': '自动化测试', 'I': '010306'}, {'N': '测试开发', 'I': '010307'}, {'N': '游戏测试', 'I': '010308'}, {'N': '其它测试类', 'I': '010399'}, {'N': '互联网软件开发工程师', 'I': '010401'}, {'N': 'Web前端开发工程师', 'I': '010402'}, {'N': '脚本开发工程师', 'I': '010403'}, {'N': '网站架构设计师', 'I': '010404'}, {'N': '网站维护工程师', 'I': '010405'}, {'N': '网站策划/管理', 'I': '010406'}, {'N': '网站编辑/论坛维护/内容监管', 'I': '010407'}, {'N': '网页设计/制作/美工', 'I': '010408'}, {'N': '网店美工', 'I': '010409'}, {'N': '电子商务总监', 'I': '010410'}, {'N': '电子商务经理/主管', 'I': '010411'}, {'N': '电子商务专员', 'I': '010412'}, {'N': '网店店长', 'I': '010413'}, {'N': '游戏制作人', 'I': '010414'}, {'N': '游戏策划师', 'I': '010415'}, {'N': '多媒体/游戏开发工程师', 'I': '010416'}, {'N': 'Flash设计/开发', 'I': '010417'}, {'N': '其他互联网/电子商务/游戏类', 'I': '010499'}, {'N': '产品总监', 'I': '010501'}, {'N': '产品部经理/主管', 'I': '010502'}, {'N': '产品经理', 'I': '010503'}, {'N': '需求分析师', 'I': '010504'}, {'N': '产品专员/助理', 'I': '010505'}, {'N': '产品实习生', 'I': '010506'}, {'N': '首席运营官COO', 'I': '010507'}, {'N': '运营总监', 'I': '010508'}, {'N': '运营经理/主管', 'I': '010509'}, {'N': '运营专员', 'I': '010510'}, {'N': '新媒体运营专员', 'I': '010511'}, {'N': '产品运营专员', 'I': '010512'}, {'N': '数据运营专员', 'I': '010513'}, {'N': '微信运营专员', 'I': '010514'}, {'N': 'SEO搜索引擎优化/SEM搜索引擎营销', 'I': '010515'}, {'N': '网络推广总监', 'I': '010516'}, {'N': '网络推广经理/主管', 'I': '010517'}, {'N': '网络推广专员', 'I': '010518'}, {'N': '微信推广专员', 'I': '010519'}, {'N': '其他产品/运营类', 'I': '010599'}, {'N': '首席技术官CTO/首席信息官CIO', 'I': '010601'}, {'N': 'IT技术/研发总监', 'I': '010602'}, {'N': 'IT技术/研发经理/主管', 'I': '010603'}, {'N': '信息技术经理/主管', 'I': '010604'}, {'N': '信息技术专员/助理', 'I': '010605'}, {'N': '系统集成工程师', 'I': '010606'}, {'N': 'MRP/ERP实施顾问', 'I': '010607'}, {'N': 'IT项目总监', 'I': '010608'}, {'N': 'IT项目经理/主管', 'I': '010609'}, {'N': 'IT项目执行/项目组长/协调人员', 'I': '010610'}, {'N': '网络工程师', 'I': '010611'}, {'N': '系统管理员/网络管理员', 'I': '010612'}, {'N': '网络与信息安全工程师', 'I': '010613'}, {'N': '配置管理工程师', 'I': '010614'}, {'N': '技术支持经理/主管', 'I': '010615'}, {'N': '技术服务/技术支持/HelpDesk', 'I': '010616'}, {'N': '技术文档写作', 'I': '010617'}, {'N': '技术文员/助理', 'I': '010618'}, {'N': '其他IT管理/系统集成/运维类', 'I': '010699'}]
        self.location_list = [{'N': '深圳', 'C': [{'N': '南山区', 'I': '200801'}, {'N': '罗湖区', 'I': '200802'}, {'N': '福田区', 'I': '200803'}, {'N': '宝安区', 'I': '200804'}, {'N': '龙岗区', 'I': '200805'}, {'N': '盐田区', 'I': '200806'}, {'N': '光明新区', 'I': '200807'}, {'N': '坪山新区', 'I': '200808'}, {'N': '大鹏新区', 'I': '200809'}, {'N': '龙华新区', 'I': '200810'}], 'I': '2008'}, {'N': '广州', 'C': [{'N': '越秀区', 'I': '201001'}, {'N': '东山区', 'I': '201002'}, {'N': '荔湾区', 'I': '201003'}, {'N': '海珠区', 'I': '201004'}, {'N': '天河区', 'I': '201005'}, {'N': '白云区', 'I': '201006'}, {'N': '黄埔区', 'I': '201007'}, {'N': '芳村区', 'I': '201008'}, {'N': '花都区', 'I': '201009'}, {'N': '番禺区', 'I': '201010'}, {'N': '从化', 'I': '201011'}, {'N': '增城', 'I': '201012'}, {'N': '南沙区', 'I': '201013'}, {'N': '萝岗区', 'I': '201014'}], 'I': '2010'}, {'N': '东莞', 'C': [{'N': '莞城区', 'I': '201101'}, {'N': '南城区', 'I': '201102'}, {'N': '东城区', 'I': '201103'}, {'N': '万江区', 'I': '201104'}, {'N': '石碣镇', 'I': '201105'}, {'N': '石龙镇', 'I': '201106'}, {'N': '常平镇', 'I': '201107'}, {'N': '麻涌镇', 'I': '201108'}, {'N': '樟木头镇', 'I': '201109'}, {'N': '虎门镇', 'I': '201110'}, {'N': '厚街镇', 'I': '201111'}, {'N': '长安镇', 'I': '201112'}], 'I': '2011'}, {'N': '珠海', 'C': [{'N': '香洲区', 'I': '201301'}, {'N': '斗门区', 'I': '201302'}, {'N': '金湾区', 'I': '201303'}], 'I': '2013'}, {'N': '惠州', 'C': [{'N': '博罗', 'I': '201501'}, {'N': '惠城区', 'I': '201502'}, {'N': '惠东县', 'I': '201503'}, {'N': '惠阳区', 'I': '201504'}, {'N': '龙门县', 'I': '201505'}], 'I': '2015'}, {'N': '佛山', 'C': [{'N': '禅城区', 'I': '201910'}, {'N': '顺德区', 'I': '201920'}, {'N': '南海区', 'I': '201930'}, {'N': '三水区', 'I': '201940'}, {'N': '高明区', 'I': '201950'}], 'I': '2019'}, {'N': '中山', 'C': [{'N': '石岐区街道', 'I': '201201'}, {'N': '东区街道', 'I': '201202'}, {'N': '小榄镇', 'I': '201203'}], 'I': '2012'}, {'N': '上海', 'C': [{'N': '黄浦区', 'I': '300101'}, {'N': '卢湾区', 'I': '300102'}, {'N': '徐汇区', 'I': '300103'}, {'N': '长宁区', 'I': '300104'}, {'N': '静安区', 'I': '300105'}, {'N': '普陀区', 'I': '300106'}, {'N': '闸北区', 'I': '300107'}, {'N': '虹口区', 'I': '300108'}, {'N': '杨浦区', 'I': '300109'}, {'N': '宝山区', 'I': '300110'}, {'N': '闵行区', 'I': '300111'}, {'N': '嘉定区', 'I': '300112'}, {'N': '浦东新区', 'I': '300113'}, {'N': '松江区', 'I': '300114'}, {'N': '金山区', 'I': '300115'}, {'N': '青浦区', 'I': '300116'}, {'N': '南汇区', 'I': '300117'}, {'N': '奉贤区', 'I': '300118'}, {'N': '崇明县', 'I': '300119'}], 'I': '30'}, {'N': '北京', 'C': [{'N': '东城区', 'I': '310101'}, {'N': '西城区', 'I': '310102'}, {'N': '崇文区', 'I': '310103'}, {'N': '宣武区', 'I': '310104'}, {'N': '朝阳区', 'I': '310105'}, {'N': '海淀区', 'I': '310106'}, {'N': '丰台区', 'I': '310107'}, {'N': '石景山区', 'I': '310108'}, {'N': '门头沟区', 'I': '310109'}, {'N': '房山区', 'I': '310110'}, {'N': '通州区', 'I': '310111'}, {'N': '顺义区', 'I': '310112'}, {'N': '昌平区', 'I': '310113'}, {'N': '大兴区', 'I': '310114'}, {'N': '怀柔区', 'I': '310115'}, {'N': '平谷区', 'I': '310116'}, {'N': '密云县', 'I': '310117'}, {'N': '延庆县', 'I': '310118'}], 'I': '31'}]
        self.level_list = [{"value":"10","text":"初中"},{"value":"20","text":"高中"},{"value":"30","text":"中技"},{"value":"40","text":"中专"},{"value":"50","text":"大专"},{"value":"60","text":"本科"},{"value":"70","text":"硕士"},{"value":"80","text":"博士"}]
        self.job_salary = [2000, 3500, 5000, 6500, 8000, 10000, 15000, 20000, 30000, 50000, 50000]
        self.major = [{"I":"050501","N":"计算机科学与技术"},{"I":"050502","N":"软件工程"},{"I":"050503","N":"网络工程"},{"I":"050504","N":"信息安全"},{"I":"050505","N":"物联网工程"},{"I":"050506","N":"数字媒体技术"},{"I":"050507","N":"智能科学与技术"},{"I":"050508","N":"空间信息与数字技术"},{"I":"050509","N":"电子与计算机工程"}]
        self.job_welfare = {'101': '五险一金', '116': '年终奖金', '103': '补充医疗保险', '104': '企业年金', '121': '岗位晋升', '110': '提供食宿', '113': '加班补助', '118': '年终分红', '125': '股票期权', '108': '高温补贴', '128': '定期体检', '102': '补充商业保险', '127': '员工旅游', '107': '通讯补贴', '105': '住房补贴 ', '123': '免费班车', '120': '专业培训', '126': '带薪年假', '106': '交通补贴', '114': '全勤奖', '109': '餐饮补贴', '117': '年底双薪 ', '119': '弹性工作', '115': '绩效奖金', '122': '节日福利', '111': '提供住宿', '124': '出国机会', '112': '提供工作餐'}
        self.payload = {
                'StatusID':'0',  #
                'JobName':'adffasdfasf',  # 自行输入的职位名字
                'JobCategory_FullTime':'1',  # 全职
                'JobCategory_Parttime':'0',  # 兼职
                'JobCategory_Graduate': '0',  # 应届毕业生
                'JobCategory_Trainee': '0',  # 实习
                'JobFunctions': '0102',  #
                'DepartmentId': '1',  #
                'JobLocation_CODE': '200804',  #
                'Requirement': '<p>asdfasdfasdfasdfasdfasdfasdfasdfsadfasdfasdf</p>',  # 自行输入的职位描述，支持HTML
                'Specialty_CODE': '',  #
                'EducationRequirement_CODE': '50',
                'MinYearsOfExperience': '5',  #
                'MinAge': '',  # 要求最低年龄 18
                'MaxAge': '',  # 要求最高年龄 26
                'ForeignLanguage_CODE': "",  # 0表示没有选择语言
                'PostTime': '',  # 发布日期
                'DisableTime': '',  # 发布失效日期
                'KeyWord': '',  #
                'ApplyThroughEmail': '',  # 转发简历邮箱
                'ApplyThroughURL': '',  #
                'GenderRequirement_CODE': '2',
                'JobWorkLocation': '深圳市南山区田夏国际B座',   # 上班地址
                'MinProvidedSalary': '20000',  # 最小工资，貌似可以用户自行输入
                'MaxProvidedSalary': '30000',  # 最大工资，貌似可以用户自行输入
                'JobLabel_CODE': '126,118,110,103',  # 职位标签， 福利
                'JobCustomLabel_CODE': '',  #
                'IsFilter': '0',
                  }


    def j_payload(self):
        """生成cjol的payload"""
        json_dict = self.j_dict['job_detail']
        self.payload['JobName'] = json_dict['job_name']
        j_work_type = json_dict['work_type']
        if j_work_type == u'全职':
            self.payload['JobCategory_FullTime'] = '1'
        elif j_work_type == u'兼职':
            self.payload['JobCategory_FullTime'] = '0'
            self.payload['JobCategory_Parttime'] = '1'

        j_job_type = json_dict['job_type']
        for j in self.j_type_list:
            if j_job_type == j['N']:
                self.payload['JobFunctions'] = j['I']

        j_city = json_dict['city']
        j_district = json_dict['district']
        for i in self.location_list:
            if j_city == i['N']:
                self.payload['JobLocation_CODE'] = i['I']
                for ii in i['C']:
                    if j_district == ii['N']:
                        self.payload['JobLocation_CODE'] = ii['I']
        self.payload['Requirement'] = json_dict['job_describe']
        j_level = json_dict['degree']
        self.payload['EducationRequirement_CODE'] = '60'
        for i in self.level_list:
            if j_level == i['text']:
                self.payload['EducationRequirement_CODE'] = i['value']
        self.payload['MinYearsOfExperience'] = json_dict['work_year']  # cjol 的直接是几年以上，不是范围
        self.payload['PostTime'] = datetime.datetime.now().date().isoformat()
        self.payload['DisableTime'] = (datetime.datetime.now().date() + datetime.timedelta(days=31)).isoformat()
        self.payload['KeyWord'] = json_dict['keyword']
        self.payload['ApplyThroughEmail'] = json_dict['email']
        self.payload['GenderRequirement_CODE'] = '2'  # 不限性别2， 男1， 女0
        self.payload['JobWorkLocation'] = json_dict['work_address']
        j_major = json_dict['major']
        for i in self.major:
            if j_major == i['N']:
                self.payload['Specialty_CODE'] = i['I']

        j_salary = int(json_dict['salary'])
        if j_salary < 2000:
            self.payload['MinProvidedSalary'] = '0'
            self.payload['MaxProvidedSalary'] = '2000'
        elif j_salary >= 50000:
            self.payload['MinProvidedSalary'] = '50000'
            self.payload['MaxProvidedSalary'] = '0'
        else:
            for i in self.job_salary:
                if i <= j_salary < self.job_salary[self.job_salary.index(i)+1]:
                    self.payload['MinProvidedSalary'] = str(i)
                    self.payload['MaxProvidedSalary'] = str(self.job_salary[self.job_salary.index(i)+1])
        j_welfare = json_dict['welfare'].split(' ')
        welfare_list = []
        for i in j_welfare:
            for ii in self.job_welfare:
                if i == self.job_welfare[ii]:
                    welfare_list.append(ii)
        self.payload['JobLabel_CODE'] = ','.join(welfare_list)

        # 发布payload
        self.payload['StatusID'] = '0'  # 改为5是发布
        return self.payload

class Zhilian(object):
    def __init__(self, j_dict):
        self.j_dict = j_dict
        self.job_type_str = '044|高级软件工程师|160000@045|软件工程师|160000@079|软件研发工程师|160000@665|需求工程师|160000@667|系统架构设计师|160000@668|系统分析员|160000@047|数据库开发工程师|160000@048|ERP技术/开发应用|160000@053|互联网软件工程师|160000@679|手机软件开发工程师|160000@687|嵌入式软件开发|160000@863|移动互联网开发|160000@864|WEB前端开发|160000@317|语音/视频/图形开发|160000@669|用户界面（UI）设计|160000@861|用户体验（UE/UX）设计|160000@054|网页设计/制作/美工|160000@057|游戏设计/开发|160000@671|游戏策划|160000@672|游戏界面设计|160000@666|系统集成工程师|160000@060|其他|160000@686|电子技术研发工程师|160100@078|电子/电器工程师|160100@528|电器研发工程师|160100@091|电子/电器工艺/制程工程师|160100@089|电路工程师/技术员|160100@406|模拟电路设计/应用工程师|160100@408|版图设计工程师|160100@404|集成电路IC设计/应用工程师|160100@405|IC验证工程师|160100@082|电子元器件工程师|160100@684|射频工程师|160100@318|无线电工程师|160100@411|激光/光电子技术|160100@559|光源/照明工程师|160100@681|变压器与磁电工程师|160100@083|电池/电源开发|160100@085|家用电器/数码产品研发|160100@560|空调工程/设计|160100@402|音频/视频工程师/技术员|160100@808|安防系统工程师|160100@401|电子/电器设备工程师|160100@403|电子/电器维修/保养|160100@409|电子/电器项目管理|160100@865|电气工程师|160100@467|电气设计|160100@683|电气线路设计|160100@682|线路结构设计|160100@081|半导体技术|160100@086|仪器/仪表/计量工程师|160100@033|自动化工程师|160100@084|现场应用工程师（FAE）|160100@410|测试/可靠性工程师|160100@094|其他|160100@316|互联网产品经理/主管|160200@675|互联网产品专员/助理|160200@676|电子商务经理/主管|160200@677|电子商务专员/助理|160200@052|网络运营管理|160200@670|网络运营专员/助理|160200@056|网站编辑|160200@552|SEO/SEM|160200@556|其他|160200@314|高级硬件工程师|160300@043|硬件工程师|160300@407|嵌入式硬件开发|160300@557|其他|160300@693|IT质量管理经理/主管|160400@049|IT质量管理工程师|160400@694|系统测试|160400@695|软件测试|160400@696|硬件测试|160400@868|配置管理工程师|160400@692|信息技术标准化工程师|160400@561|其他|160400@305|公务员/事业单位人员|200100@362|科研管理人员|200100@255|科研人员|200100@306|其他|200100@398|CTO/CIO|200300@928|IT技术/研发总监|200300@313|IT技术/研发经理/主管|200300@688|IT项目总监|200300@042|IT项目经理/主管|200300@689|IT项目执行/协调人员|200300@841|其他|200300@040|信息技术经理/主管|200500@041|信息技术专员|200500@058|IT技术支持/维护经理|200500@315|IT技术支持/维护工程师|200500@046|系统工程师|200500@051|系统管理员|200500@055|网络工程师|200500@388|网络管理员|200500@059|网络与信息安全工程师|200500@389|数据库管理员|200500@678|计算机硬件维护工程师|200500@551|ERP实施顾问|200500@690|IT技术文员/助理|200500@699|IT文档工程师|200500@698|Helpdesk|200500@840|其他|200500@@120|人力资源总监|5002000@121|人力资源经理|5002000@618|人力资源主管|5002000@122|人力资源专员/助理|5002000@125|培训经理/主管|5002000@126|培训专员/助理|5002000@123|招聘经理/主管|5002000@124|招聘专员/助理|5002000@127|薪酬福利经理/主管|5002000@780|薪酬福利专员/助理|5002000@619|绩效考核经理/主管|5002000@778|绩效考核专员/助理|5002000@620|员工关系/企业文化/工会|5002000@858|企业培训师/讲师|5002000@779|人事信息系统(HRIS)管理|5002000@128|猎头顾问/助理|5002000@130|其他|5002000'
        self.job_type_list = self.job_type_str.split('@')
        self.address_dict = {"763":{"2045":"越秀区","2046":"海珠区","2047":"荔湾区","2048":"天河区","2049":"白云区","2050":"黄埔区","2052":"番禺区","2051":"花都区","2053":"萝岗区","2054":"南沙区","2475":"增城","2474":"从化"},
                        "765":{"2037":"福田区","2038":"罗湖区","2039":"南山区","2040":"盐田区","2041":"宝安区","2042":"龙岗区","2043":"坪山新区","2044":"光明新区","2361":"龙华新区","2362":"大鹏新区"},
                        "538":{"2019":"黄浦区","2021":"徐汇区","2022":"长宁区","2023":"静安区","2024":"普陀区","2025":"闸北区","2026":"虹口区","2027":"杨浦区","2028":"闵行区","2029":"宝山区","2030":"嘉定区","2031":"浦东新区","2032":"金山区","2033":"松江区","2034":"青浦区","2035":"奉贤区","2036":"崇明县"},
                        "530":{"2001":"东城区","2002":"西城区","2003":"崇文区","2004":"宣武区","2005":"海淀区","2006":"朝阳区","2007":"丰台区","2008":"石景山区","2009":"通州区","2010":"顺义区","2011":"房山区","2012":"大兴区","2013":"昌平区","2014":"怀柔区","2015":"平谷区","2016":"门头沟区","2017":"密云县","2018":"延庆县"}}
        self.welfareTabJson = [{"Id":"10000","Name":"五险一金"},{"Id":"10001","Name":"年底双薪"},{"Id":"10002","Name":"绩效奖金"},{"Id":"10003","Name":"年终分红"},{"Id":"10004","Name":"股票期权"},{"Id":"10005","Name":"加班补助"},{"Id":"10006","Name":"全勤奖"},{"Id":"10007","Name":"包吃"},{"Id":"10008","Name":"包住"},{"Id":"10009","Name":"交通补助"},{"Id":"10010","Name":"餐补"},{"Id":"10011","Name":"房补"},{"Id":"10012","Name":"通讯补贴"},{"Id":"10013","Name":"采暖补贴"},{"Id":"10014","Name":"带薪年假"},{"Id":"10015","Name":"弹性工作"},{"Id":"10016","Name":"补充医疗保险"},{"Id":"10017","Name":"定期体检"},{"Id":"10018","Name":"免费班车"},{"Id":"10019","Name":"员工旅游"},{"Id":"10020","Name":"高温补贴"},{"Id":"10021","Name":"节日福利"}]
        self.payload = {
                'LoginPointId':'112721565',  # 需要从网页中解析
                'PriorityRule':'1',
                'PublicPoints':'0',  # 扣除的发布点数
                'HavePermissionToPubPosition':'False',
                'TemplateId': '',
                'EmploymentType': '2',  # 全职2，兼职1, 实习4
                'JobTitle': 'java',  # 输入的职位名称
                'JobTypeMain': '', # '160000',  # 选择。。。 职位类别
                'SubJobTypeMain': '', # '044',  # 还是选择
                'JobTypeMinor': '',  # 添加的第二种职业分类
                'SubJobTypeMinor': '',
                'Quantity': '1',  # 招聘人数
                'EducationLevel': '4', # 学历 不限-1
                'WorkYears': '1099',  # 工作年限 不限-1
                'MonthlyPay': "1500120000",  # 月薪 又是选择
                'DontDisplayMonthlyPay': 'False',  # 选项可以隐藏月薪
                'JobDescription': '<p>岗位职责：</p><p>有钱，有钱，还是有钱</p><p>任职要求：</p><p>有钱就行了</p><p><br/></p>',  # 用户输入的职位描述
                'welfaretab': '',  # 这是福利
                'CanPubPositionQty': '0',
                'PositionPubPlace': '763@2048',  # 北京530
                'ContractCityList': '',
                'PositionPubPlaceInitCityId': '',   #
                'WorkAddress': '天河区天河公园',  # 工作地址，貌似可以用户自行输入
                'WorkAddressCoordinate': '0,0',
                # 'CompanyAddress': '南宁市新华街4号',
                'DateEnd': '2016-03-11',
                'ApplicationMethod': '',  # '2'表示有邮箱，1表示无
                'EmailList': '',  # 'a@a.com,b@b.com', 分隔符 ,
                'ApplicationMethodOptionsList': '1,2',  #
                'ESUrl': '',  #
                'IsCorpUser': 'False',
                'IsShowRootCompanyIntro': 'True',  #
                'IsShowSubCompanyIntro': 'False',  # 语言程度 数字
                'DepartmentId': '112721565',  # 从网页中解析？
                'FilterId': '-1',  #
                'JobNo': '',  #
                'SeqNumber': '',  #
                'btnAddClick': 'preview',  # 应该这里判断是否发布/保存/预览
                'editorValue': '<p>岗位职责：</p><p>有钱，有钱，还是有钱</p><p>任职要求：</p><p>有钱就行了</p><p><br/></p>',
                  }

    def j_payload(self):
        """生成51job的payload"""
        json_dict = self.j_dict['job_detail']
        # json_dict = json_str['job_detail']
        self.payload['JobTitle'] = json_dict['job_name']
        # payload['hidAjaxJobName1'] = json_dict['job_type']  # 这个选项实在太多，先不做判断

        self.payload['JobDescription'] = json_dict['job_describe']
        welfare_list = json_dict['welfare'].split(' ')
        w_list = []
        for w in welfare_list:
            for welfare in self.welfareTabJson:
                if w == welfare['Name']:
                    w_list.append(welfare['Id'])
        self.payload['welfaretab'] = ','.join(w_list)

        self.payload['editorValue'] = json_dict['job_describe']
        self.payload['WorkAddress'] = json_dict['work_address']
        self.payload['EmailList'] = json_dict['email']
        if len(json_dict['email']) > 0:
            self.payload['ApplicationMethod'] = '2'
        else:
            self.payload['ApplicationMethod'] = '1'

        j_job_type = json_dict['job_type']
        for j in self.job_type_list:
            if j_job_type in j:
                self.payload['JobTypeMain'] = j.split('|')[2]
                self.payload['SubJobTypeMain'] = j.split('|')[0]

        if not self.payload['JobTypeMain'] and self.payload['SubJobTypeMain']:
            print 'job_type is needed'
            exit()
        j_work_type = json_dict['work_type']
        if j_work_type == u'兼职':
            self.payload['EmploymentType'] = '1'
        elif j_work_type == u'全职':
            self.payload['EmploymentType'] = '2'
        else:
            self.payload['EmploymentType'] = '4'

        j_work_address = json_dict['city']
        if j_work_address == u'广州':
            self.payload['PositionPubPlace'] = '763'
        elif j_work_address == u'深圳':
            self.payload['PositionPubPlace'] = '765'
        elif j_work_address == u'上海':
            self.payload['PositionPubPlace'] = '538'
        elif j_work_address == u'北京':
            self.payload['PositionPubPlace'] = '530'

        d_dict = self.address_dict[self.payload['PositionPubPlace']]
        for k in d_dict:
            if d_dict[k] == json_dict['district']:
                self.payload['PositionPubPlace'] = self.payload['PositionPubPlace'] + '@' + k

        self.payload['Quantity'] = json_dict['job_num']

        # 月薪为范围
        j_salasy = int(json_dict['salary'])
        if j_salasy < 1000:
            self.payload['MonthlyPay'] = '0000001000'
        elif 1000 <= j_salasy < 2000:
            self.payload['MonthlyPay'] = '0100002000'
        elif 2000 <= j_salasy < 4000:
            self.payload['MonthlyPay'] = '0200104000'
        elif 4000 <= j_salasy < 6000:
            self.payload['MonthlyPay'] = '0400106000'
        elif 6000 <= j_salasy < 8000:
            self.payload['MonthlyPay'] = '0600108000'
        elif 8000 <= j_salasy < 10000:
            self.payload['MonthlyPay'] = '0800110000'
        elif 10000 <= j_salasy < 15000:
            self.payload['MonthlyPay'] = '1000115000'
        elif 15000 <= j_salasy < 20000:
            self.payload['MonthlyPay'] = '1500120000'
        elif 20000 <= j_salasy < 25000:
            self.payload['MonthlyPay'] = '2000130000'
        elif 30000 <= j_salasy < 50000:
            self.payload['ProvideSalary'] = '3000150000'
        elif 50000 <= j_salasy:
            self.payload['ProvideSalary'] = '5000199999'

        j_work_year = json_dict['work_year']
        if j_work_year == '':
            self.payload['WorkYears'] = '-1'
        elif int(j_work_year) == 0:
            self.payload['WorkYears'] = '0'
        elif int(j_work_year) < 1:
            self.payload['WorkYears'] = '1'
        elif 1 <= int(j_work_year) < 3:
            self.payload['WorkYears'] = '103'
        elif 3 <= int(j_work_year) < 5:
            self.payload['WorkYears'] = '305'
        elif 5 <= int(j_work_year) < 10:
            self.payload['WorkYears'] = '510'
        elif 10 <= int(j_work_year):
            self.payload['WorkYears'] = '1099'
        else:
            self.payload['WorkYears'] = '-1'

        j_degree = json_dict['degree']
        if j_degree == u'本科':
            self.payload['EducationLevel'] = '4'
        elif j_degree == u'硕士' or j_degree == u'研究生':
            self.payload['EducationLevel'] = '3'
        elif j_degree == u'大专':
            self.payload['EducationLevel'] = '5'
        elif j_degree == u'博士':
            self.payload['EducationLevel'] = '1'
        elif j_degree == u'中专':
            self.payload['EducationLevel'] = '12'
        elif j_degree == u'中技':
            self.payload['EducationLevel'] = '13'
        elif j_degree == u'高中':
            self.payload['EducationLevel'] = '7'
        elif j_degree == u'初中及以下':
            self.payload['EducationLevel'] = '7'
        else:
            self.payload['EducationLevel'] = ''

        return self.payload


class Job51(object):
    # 传入字典，生成payload
    def __init__(self, j_dict):
        self.j_dict = j_dict
        self.payload = {
                '__EVENTTARGET':'',
                '__EVENTARGUMENT':'',
                '__LASTFOCUS':'',
                '__VIEWSTATE':'',
                'strMarkValue': 'New',
                'tblFlag': '',
                'jobId': '',
                'MainMenuNew1$CurMenuID': 'MainMenuNew1_imgJob|sub2',
                'hidMdJobName': '0',
                'CJOBNAME': 'Java 高级开发',  # 职位名称
                'hidJobCode': '',
                'POSCODE': '',  # 职位编号
                'EJOBNAME': '',
                'JOBNUM': '0',  # 招聘人数
                'JobAreaAllValue': "'040000','00000",
                # 'AllJobArea': "'010000','020000','030000','030200','030300','030400','030500','030600','030700','030800','031400','031500','031700','031800','031900','032000','032100','032200','032300','032400','032600','032700','032800','032900','040000','050000','060000','070000','070200','070300','070400','070500','070600','070700','070800','070900','071000','071100','071200','071300','071400','071600','071800','071900','072000','072100','072300','072500','080000','080200','080300','080400','080500','080600','080700','080800','080900','081000','081100','081200','081400','081600','090000','090200','090300','090400','090500','090600','090700','090800','090900','091000','091100','091200','091300','091400','091500','091600','091700','091800','091900','092000','092100','092200','092300','100000','100200','100300','100400','100500','100600','100700','100800','100900','101000','101100','101200','101300','101400','101500','101600','101700','101800','101900','102000','102100','110000','110200','110300','110400','110500','110600','110700','110800','110900','111000','120000','120200','120300','120400','120500','120600','120700','120800','120900','121000','121100','121200','121300','121400','121500','121600','121700','121800','130000','130200','130300','130400','130500','130600','130700','130800','130900','131000','131100','131200','140000','140200','140300','140400','140500','140600','140700','140800','140900','141000','141100','141200','141300','141400','141500','150000','150200','150300','150400','150500','150600','150700','150800','150900','151000','151100','151200','151400','151500','151600','151700','151800','160000','160200','160300','160400','160500','160600','160700','160800','160900','161000','161100','161200','161300','170000','170200','170300','170400','170500','170600','170700','170800','170900','171000','171100','171200','171300','171400','171500','171600','171700','171800','171900','172000','180000','180200','180300','180400','180500','180600','180700','180800','180900','181000','181100','181200','181300','181400','181500','181600','181700','181800','190000','190200','190300','190400','190500','190600','190700','190800','190900','191000','191100','191200','191300','191400','191500','200000','200200','200300','200400','200500','200600','200700','200800','200900','201000','201100','201200','210000','210200','210300','210400','210500','210600','210700','210800','210900','211000','211100','211200','220000','220200','220300','220400','220500','220600','220700','220800','220900','221000','221100','221200','221300','221400','230000','230200','230300','230400','230500','230600','230700','230800','230900','231000','231100','231200','231300','231400','231500','240000','240200','240300','240400','240500','240600','240700','240800','240900','241000','241100','250000','250200','250300','250400','250500','250600','251000','251100','251200','251300','251400','251500','251600','251700','251800','251900','252000','260000','260200','260300','260400','260500','260600','260700','260800','260900','261000','270000','270200','270300','270400','270500','270600','270700','270800','270900','271000','271100','271200','271300','271400','271500','280000','280200','280300','280400','280700','280800','280900','281000','281100','281200','281300','281400','281500','290000','290200','290300','290400','290500','290600','300000','300200','300300','300400','300500','300600','300700','300800','310000','310200','310300','310400','310500','310600','310700','310800','310900','311000','311100','311200','311300','311400','311500','311600','311700','311800','311900','320000','320200','320300','320400','320500','320600','320700','320800','320900','330000','340000','350000','360000'",
                'RestrictedJobArea': '040000',
                'JobAreaSelectValue': '',
                'DEGREEFROM': '6',  # 最低学历 数字 1初中及以下，2，高中，3，中技，4，中专，5，大专，6，本科，7，硕士，8，博士
                'txtSelectedJobAreas': '',
                'hidJobAreasLimit': '',
                'hidWorkareaId': '',  # todo 测试发布时要不要添加 需要选择 广州天河区
                'hidAddress': '天河区',   # 用户输入地址
                'hidWorkarea': '030204',
                'hidLon': '',
                'hidLat': '',
                'hidLandMarkId': '',
                'txtWorkAddress': '',  #用户输入内容加上前缀
                'AGEFROM': '',  # 要求最低年龄
                'AGETO': '',  # 要求最高年龄
                'FuncType1Text': '',  # 职能类别 1 文字 （需要选择）
                'FuncType1Value': '',  # 高级软件工程师 0106
                'FL1': '',  # 语言选择栏1  01 英语
                'TxtOtherLanguage1': '',  # 语言程度 数字
                'FuncType2Text': '',  # 职能类别 2 文字 （需要选择）
                'FuncType2Value': '',  #
                'FL2': '',  # 语言选择栏2
                'TxtOtherLanguage2': '',  # 语言程度2
                'hidFunRecommend1': '',
                'hidFunRecommend2': '',
                'hidFunRecommend3': '',
                'hidFunRecommendSelected': '',
                'WORKYEAR': '',  # 工作年限 （需要选择） 数字，代表范围
                'Major1Text': '',  # 专业名字 （需要选择）
                'Major1Value': '',  # （需要选择） 计算机科学与技术 3701
                'Term': '',  # 全职兼职 （需要选择） 0 全职
                'Major2Text': '',  # 专业要求2 （需要选择）
                'Major2Value': '',  # （需要选择）
                'hidIsSalaryDefault': '',
                'hidIsCustomSalary': '0',
                'DdrSalaryType': '1',
                'YEARSALARY': '',
                'ProvideSalary': '',
                'TxtSalaryFrom': '',  # 月薪范围（低值）
                'TxtSalaryTo': '',  # 月薪范围 （高值）
                'TxtCustomSalary': '',
                'hidAllSalaryCities': '', # 北京,长春,成都,重庆,长沙,东莞,大连,福州,广东省,广州,哈尔滨,合肥,杭州,济南,江西省,昆明,宁波,南京,青岛,上海,苏州,沈阳,深圳,天津,武汉,无锡,西安,厦门,郑州
                'hidAjaxIndustry': '互联网',
                'hidAjaxJobType1': '信息技术',
                'hidAjaxJobType2': '',
                'hidAjaxJobName1': '软件工程师',
                'hidAjaxJobName2': '',
                # 'hidAjaxCompanyType': '外商独资（欧美企业）',
                'hidLinkButtonID': '1',
                'hidJobtype_erji': '软件工程师',
                'hidJobtype_erji2': '',
                'TxtJobKeywords': 'java 高薪',
                'hidIndex': '0',
                'viewTimes': '0',
                'CJOBINFO': '少年', # 职位描述
                'hidCCopyContent': '',
                'EJOBINFO': '',
                'hidMode': '0',
                'hidJobDescAss1': '',
                'hidJobDescAss2': '',
                'hidJobDescAss3': '',
                'hidJobDescAssContent': '',
                'cbxEmail': 'on',
                'radEmail1': '2',
                'JOBEMAIL': '2@qq.com',
                'HidCompanyEmail': '',
                'HidDivEmail': '',
                'hidEmails': '',
                'hasFilter': '',
                'RefID1': '',
                'RefID2': '',
                'HidFLTID': '',
                'HidNewFLTID': '',
                'JOBORDER': '输入0-999中任一数字',
                'jobOrderInputTip': '0',
                'hidDivOrder': '',
                'hidJobOrderCoid': '3725975',
                'viewTimes2': '10',
                'hidUrlParameters': '',
                'WCBigAreaCode1$2': 'rdbGroup2_1',
                'WCBigAreaCode2$2': 'rdbGroup2_1',
                'TextKeyWords': '',
                'HidSHowSaleDiv': '0',
                'HidSaleSelect': '',
                'TextKeyWords2': '',
                'HidSHowSaleDiv2': '0',
                'HidSale2Select': '',
                'TpmName': '',
                'hidCOID': '',
                'hidDIVID': '',
                'hidMark': 'Job',
                'hidTop': '1155',
                'hidLeft': '513',
                'ViewCOID': '3725975',
                'ViewDIVID': '',
                'ViewJobArea': '',
                'ViewCJobName': '',
                'ViewEJobName': '',
                'ViewIssuehDate': '',
                'ViewPOSCODE': '',
                'ViewNewJobName': '',
                'hidWelfare': '99 2222222',  # 福利
                'ddlCompanyType': '',
                #'checkErr': '1^200-22:200|2^235:363|3^306:175|4^263:283|5^-22:0|6^0:0|7^328:644|8^328:773|9^359:899|10^393:899|11^1094:299|12^684:98|13^-22:0|14^200-22:200|15^200-22:200|16^-22:0|17^200-22:200|',
                'matchjobFun': '3',
                'matchjobInd': '3',
                'matchmajor': '3',
                'matchedu': '3',
                'matchworkyear': '3',
                'matchage': '3',
                'matchsalary': '3',
                'matchlang': '3',
                'matchlocal': '3',
                'workaddressId': '',
                'workaddressCityCode': '',
                'ddlCity': '',
                'ddlDistrict': '',
                'hidExistWorkArea': '030204',
                'rdoWorkaddress': '1202089',
                  }


    def j_payload(self):
        """生成51job的payload， 传入json_dumps 过的字符串"""
        # json_dict = json.loads(json_str)['job_detail']
        json_dict = self.j_dict['job_detail']
        self.payload['CJOBNAME'] = json_dict['job_name']
        # payload['hidAjaxJobName1'] = json_dict['job_type']  # 这个选项实在太多，先不做判断

        j_work_type = json_dict['work_type']
        if j_work_type == u'兼职':
            self.payload['Term'] = '1'
        else:
            self.payload['Term'] = '0'

        self.payload[''] = json_dict['city']  # 发布城市，扣发布岗位数量

        j_work_address = json_dict['city']
        if j_work_address == u'广州':
            self.payload['hidWorkarea'] = '030200'
            self.payload['txtWorkAddress'] = u'广州' + json_dict['work_address']
            self.payload['hidAddress'] = u'广州' + json_dict['work_address']
        elif j_work_address == u'深圳':
            self.payload['hidWorkarea'] = '040000'
            self.payload['txtWorkAddress'] = u'深圳' + json_dict['work_address']
            self.payload['hidAddress'] = u'深圳' + json_dict['work_address']
        elif j_work_address == u'上海':
            self.payload['hidWorkarea'] = '020000'
            self.payload['txtWorkAddress'] = u'上海' + json_dict['work_address']
            self.payload['hidAddress'] = u'上海' + json_dict['work_address']
        elif j_work_address == u'北京':
            self.payload['hidWorkarea'] = '010000'
            self.payload['txtWorkAddress'] = u'北京' + json_dict['work_address']
            self.payload['hidAddress'] = u'北京' + json_dict['work_address']


        self.payload['JOBNUM'] = json_dict['job_num']

        # 月薪为范围
        j_salasy = int(json_dict['salary'])
        if j_salasy < 1500:
            self.payload['ProvideSalary'] = '01'
        elif 1500 <= j_salasy <= 1999:
            self.payload['ProvideSalary'] = '02'
        elif 2000 <= j_salasy <= 2999:
            self.payload['ProvideSalary'] = '03'
        elif 3000 <= j_salasy <= 4499:
            self.payload['ProvideSalary'] = '04'
        elif 4500 <= j_salasy <= 5999:
            self.payload['ProvideSalary'] = '05'
        elif 6000 <= j_salasy <= 7999:
            self.payload['ProvideSalary'] = '06'
        elif 8000 <= j_salasy <= 9999:
            self.payload['ProvideSalary'] = '07'
        elif 10000 <= j_salasy <= 14999:
            self.payload['ProvideSalary'] = '08'
        elif 15000 <= j_salasy <= 19999:
            self.payload['ProvideSalary'] = '09'
        elif 20000 <= j_salasy <= 24999:
            self.payload['ProvideSalary'] = '10'
        elif 25000 <= j_salasy <= 29999:
            self.payload['ProvideSalary'] = '11'
        elif 30000 <= j_salasy <= 39999:
            self.payload['ProvideSalary'] = '12'
        elif 40000 <= j_salasy <= 49999:
            self.payload['ProvideSalary'] = '13'
        elif 50000 <= j_salasy <= 69999:
            self.payload['ProvideSalary'] = '14'
        elif 70000 <= j_salasy <= 99999:
            self.payload['ProvideSalary'] = '15'
        elif 100000 <= j_salasy:
            self.payload['ProvideSalary'] = '16'


        j_work_year = json_dict['work_year']
        if j_work_year == '':
            self.payload['WORKYEAR'] = ''
        elif j_work_year == '0':
            self.payload['WORKYEAR'] = '2'
        elif j_work_year == '1':
            self.payload['WORKYEAR'] = '3'
        elif j_work_year == '2':
            self.payload['WORKYEAR'] = '4'
        elif 3 <= int(j_work_year) <= 4:
            self.payload['WORKYEAR'] = '5'
        elif 5 <= int(j_work_year) <= 7:
            self.payload['WORKYEAR'] = '6'
        elif 8 <= int(j_work_year) <= 9:
            self.payload['WORKYEAR'] = '7'
        elif 10 <= int(j_work_year):
            self.payload['WORKYEAR'] = '8'


        j_degree = json_dict['degree']
        if j_degree == u'本科':
            self.payload['DEGREEFROM'] = '6'
        elif j_degree == u'硕士' or j_degree == u'研究生':
            self.payload['DEGREEFROM'] = '7'
        elif j_degree == u'大专':
            self.payload['DEGREEFROM'] = '5'
        elif j_degree == u'博士':
            self.payload['DEGREEFROM'] = '8'
        elif j_degree == u'中专':
            self.payload['DEGREEFROM'] = '4'
        elif j_degree == u'中技':
            self.payload['DEGREEFROM'] = '3'
        elif j_degree == u'高中':
            self.payload['DEGREEFROM'] = '2'
        elif j_degree == u'初中及以下':
            self.payload['DEGREEFROM'] = '1'
        else:
            self.payload['DEGREEFROM'] = ''

        j_major = json_dict['major']
        self.payload['Major1Text'] = j_major
        if j_major == u'计算机科学与技术':
            self.payload['Major1Value'] = '3701'
        elif j_major == u'计算机科学':
            self.payload['Major1Value'] = '3702'
        elif j_major == u'计算机工程':
            self.payload['Major1Value'] = '3703'
        elif j_major == u'计算机网络':
            self.payload['Major1Value'] = '3704'
        elif j_major == u'计算机应用':
            self.payload['Major1Value'] = '3705'
        elif j_major == u'软件工程':
            self.payload['Major1Value'] = '3706'
        elif j_major == u'计算机信息管理':
            self.payload['Major1Value'] = '3707'
        else:
            self.payload['Major1Value'] = ''
        # payload[''] = json_dict['sex']
        self.payload['hidWelfare'] = json_dict['welfare']
        self.payload['TxtJobKeywords'] = json_dict['keyword']
        self.payload['JOBEMAIL'] = json_dict['email']

        ########### 发布 payload
        # self.payload['ScriptManager1'] = 'ScriptManager1|lbtnFuncTypeSure2'
        # self.payload['__EVENTTARGET'] = 'lbtnFuncTypeSure2'
        # self.payload['JobAreaSelectValue'] = payload['hidWorkarea']
        # self.payload['txtSelectedJobAreas'] = j_work_address
        # self.payload['__ASYNCPOST'] = 'true'

        return self.payload


class mainfetch(object):
    def __init__(self, position='', json_file=''):
        self.position = position
        # 直接传入json的字符串
        self.json_dict = json.loads(json_file)
        # with open(json_file) as f:   #注释掉打开文件的
        #     self.json_dict = json.load(f)
        if len(sys.argv) >= 5:
            if sys.argv[4] == "debug":
                self.debug = True
            else:
                self.debug = False
        else:
            self.debug = False

        # 选取合适的 cookie 文件
        if position == 'gz':
            ppp = '广州'
        elif position == 'sz':
            ppp = '深圳'
        elif position == 'bj':
            ppp = '北京'
        elif position == 'hz':
            ppp = '杭州'
        elif position == 'sh':
            ppp = '上海'
        else:
            ppp = '%'
        self.detail = self.json_dict['job_detail']
        self.source = self.json_dict['source']
        fpath_choice = selectuser.Selcet_user(self.source, location=ppp, option='pub')
        fpath_list = fpath_choice.select_cookie()
        if len(fpath_list) > 0:
            cookie_fpath = random.choice(fpath_list)
            print '选择的cookie文件为 {}'.format(cookie_fpath)
        else:
            logging.error('no avail login cookie file for cjol')
            print '没有已经登陆的 {} cookie文件'.format(self.source)
            quit()
        # cookie_fpath = '/home/vagrant/share/fetch/src/fetch/cookie/zl.txt'
        self.cookie_fpath = cookie_fpath

    def run_work(self):
        if self.source == 'zhilian':
            p = Zhilian(self.json_dict)
            payload = p.j_payload()
            # print payload
            a = libzlpublish.zhilianpub(self.cookie_fpath, payload)
            a.run_work()
        elif self.source == '51job':
            p = Job51(self.json_dict)
            payload = p.j_payload()
            a = lib51publish.job51pub(self.cookie_fpath, payload)
            a.run_work()
        elif self.source == 'cjol':
            p = Cjol(self.json_dict)
            payload = p.j_payload()
            a = libcjolpublish.Cjolpub(self.cookie_fpath, payload)
            a.run_work()


if __name__ == '__main__':
    # c = mainfetch('gz', 'pp.json')
    c = Cjol(source_json)
    p = c.j_payload()
    print p