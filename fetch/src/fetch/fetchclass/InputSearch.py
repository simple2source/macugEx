# -*- coding:utf-8 -*-

from lib51search import job51search
import sys,json,traceback,datetime,time,urllib,urlparse
from bs4 import BeautifulSoup
import cgi,common, logging,os,random
import logging.config
import liblogin
import MySQLdb
import id_down_51
reload(sys)
sys.setdefaultencoding('utf8')

class TransportSearch(job51search):
	def __init__(self):
		job51search.__init__(self)
		self.host = r'ehire.51job.com'
		self.login_wait = 300
		self.refer = ''
		self.post_data_first = open('/data/fetch/task/51/post_viewstat.txt', 'r').read()
		with open(common.json_config_path) as f_log:
			f_read = f_log.read()
		logger = logging.getLogger(__name__)
		log_dict = json.loads(f_read)
		log_dict['handlers']['file']['filename'] = os.path.join(common.log_dir, 'input_search.log')
		logging.config.dictConfig(log_dict)

		self.convert_area = {u'北京': '010000', u'上海': '020000', u'广州': '030200', u'深圳': '040000', '7C000000': '7C000000'}
		self.keyword_type = {u'全文': '0', u'职务': '2', u'公司': '3', u'学校': '4', u'证书': '5', u'工作': '1'}
		self.convert_year = {u'在读学生': '7C1%7C1', u'应届毕业生': u'7C2%7C2', u'一年以下': u'7C99%7C3',
								u'1-2年': '7C3%7C3', u'2-3年': '7C4%7C4', u'3-4年': '7C5%7C5', u'5-7年': '7C6%7C6',
								u'8-9年': '7C7%7C7', u'10年以上': '7C8%7C99', '7C99': '7C99'}
		self.convert_degree = {u'初中': '7C1', u'高中': '7C2', u'中技': '7C3', u'中专': '7C4', u'大专以下': '7C4',u'大专': '7C5',
								u'本科': '7C6', u'硕士': '7C7', u'博士': '7C8', '7C99': '7C99'}
		self.industry_dict = {u'计算机软件': '01', u'计算机硬件': '37', u'计算机服务(系统、数据服务、维修)': '38', u'互联网': '32', u'网络游戏': '40',
							u'通信': '31', u'电信运营': '39', u'电子技术': '02', u'仪器仪表': '35', u'会计/审计': '41', u'金融/投资/证券': '03',
							u'银行': '42', u'保险': '43', u'信托/担保/拍卖/典当': '62', u'贸易/进出口': '04', u'批发/零售': '22',
							u'快速消费品': '05', u'服装/纺织/皮革': '06', u'家具/家电/玩具/礼品': '44', u'奢侈品/收藏品/工艺品/珠宝': '60',
							u'办公用品及设备': u'45', '机械/设备/重工': '14', u'汽车及零配件': '33', u'制药/生物工程': '08', u'医疗/护理/卫生': '46',
							u'医疗设备/器械': '47', u'广告': '12', u'公关/市场推广/会展': '48', u'影视/媒体/艺术/文化传播': '49', u'文字媒体/出版': '13',
							u'印刷/包装/造纸': '14', u'房地产': '26', u'建筑/建材/工程': '09', u'家居/室内设计/装潢': '50', u'物业管理/商业中心': '51',
							u'中介服务': '34', u'租赁服务': '63', u'专业服务(咨询、人力资源、财会)': '07', u'外包服务': '59', u'检测，认证': '52',
							u'法律': '18', u'教育/培训/院校': '23', u'学术/科研': '24', u'餐饮业': '11', u'酒店/旅游': '53', u'娱乐/休闲/体育': '17',
							u'美容/保健': '54', u'生活服务': '27', u'交通/运输/物流': '21', u'航天/航空': '55', u'石油/化工/矿产/地质': '19', u'采掘业/冶炼': '16',
							u'电气/电力/水利': '36', u'新能源': '61', u'原材料和加工': '56', u'政府/公共事业': '28', u'非盈利机构': '57', u'环保': '20',
							u'农/林/牧/渔': '29', u'多元化业务集团公司': '58'}

		self.function_dict = {u'电子商务总监': '2535', u'空乘人员': '1823', u'信用卡销售': '2222', u'体系工程师': '3608',
		                      u'钳工': '6210', u'网站营运总监': '2530', u'专业顾问': '1401', u'公关/媒介助理': '4310',
		                      u'首席技术执行官CTO/首席信息官CIO': '2601', u'电脑放码员': '3811', u'育婴师/保育员': '5210',
		                      u'收货员': '5120', u'化妆品研发': '5506', u'总编/副总编': '4501', u'汽车机构工程师': '5401',
		                      u'电话采编': '4516', u'切割技工': '6216', u'呼叫中心客服': '2232', u'培训助理': '5704',
		                      u'茶艺师': '4809', u'自动控制工程师/技术员': '2908', u'家用电器/数码产品研发': '2913',
		                      u'股票/期货操盘手': '3303', u'采购材料、设备质量管理': '3612', u'冲压工程师/技师': '0567',
		                      u'电脑操作员/打字员': '2308', u'品牌/连锁招商管理': '5114', u'生鲜食品加工/处理': '5110',
		                      u'房地产客服': '6006', u'业务分析专员/助理': '3109', u'珠宝销售顾问': '5116', u'资料员': '2130',
		                      u'公司业务客户经理': '2226', u'英语翻译': '2001', u'机电工程师': '0544', u'矿产勘探/地质勘测工程师': '0579',
		                      u'厨师助理/学徒': '4812', u'计量工程师': '2703', u'建筑机电工程师': '2103', u'医疗器械研发': '4124',
		                      u'飞机维修机械师': '0576', u'软件工程师': '0107', u'技术文员/助理': '2710', u'宴会管理': '4912',
		                      u'嵌入式硬件开发(主板机…)': '2919', u'律师/法律顾问': '1101', u'有线传输工程师': '2802',
		                      u'项目管理': '0584', u'客服专员/助理': '3204', u'网站营运经理/主管': '2503', u'渠道/分销专员': '3002',
		                      u'系统分析员': '0123', u'个人业务部门经理/主管': '2223', u'企业文化/员工关系/工会管理': '0629',
		                      u'收银主管': '5103', u'西点师': '4823', u'缝纫工': '3816', u'激光/光电子技术': '2918',
		                      u'物业管理专员/助理': '4703', u'知识产权/专利/商标': '1108', u'机场代表': '4913', u'水工': '3709',
		                      u'烫金工': '6305', u'广告制作执行': '4212', u'资产评估/分析': '2208', u'其他': '1901', u'动画/3D设计': '0924',
		                      u'宾客服务经理': '4915', u'电子软件开发(ARM/MCU...)': '2909', u'售前/售后技术支持主管': '3206',
		                      u'成本管理员': '0409', u'夹具工程师/技师': '0565', u'工厂经理/厂长': '3501', u'手机维修': '2716',
		                      u'房地产内勤': '6007', u'调色员': '6304', u'西班牙语翻译': '2006', u'广告创意/设计经理': '4204',
		                      u'平面设计经理/主管': '0931', u'排版设计': '4505', u'洗车工': '5908', u'财务总监': '0401', u'渠道/分销总监': '0233',
		                      u'平面设计师': '0904', u'展览/展示/店面设计': '0925', u'市场分析/调研人员': '0324', u'生产文员': '3512',
		                      u'心理医生': '1309', u'汽车销售/经纪人': '5903', u'商务经理': '3103', u'监察人员': '4612', u'保险客户服务/续期管理': '3409',
		                      u'施工开料工': '2143', u'采购经理': '3902', u'混凝土工': '2136', u'足疗': '5024', u'中餐厨师': '4807', u'儿科医生': '1325',
		                      u'医药学检验': '1310', u'人事专员': '0604', u'营运主管': '3506', u'物流经理': '0801', u'网站策划': '2506', u'电池/电源开发': '2911',
		                      u'产品规划工程师': '0559', u'意大利语翻译': '2010', u'资金专员': '0450', u'研究生': '1605', u'阿拉伯语翻译': '2009', u'猎头/人才中介': '1408',
		                      u'服装/纺织/皮革工艺师': '3813', u'保镖': '5202', u'外汇交易': '2212', u'手缝工': '3817', u'面料辅料开发': '3802', u'税务经理/税务主管': '0411',
		                      u'售后服务/客户服务': '5902', u'市场/营销/拓展主管': '0303', u'船长/副船长': '1827', u'公司业务部门经理/主管': '2225',
		                      u'网店美工': '6106', u'飞机机长/副机长': '1822', u'配音员': '4408', u'办事处/分公司/分支机构经理': '0709', u'汽车电子工程师': '5403',
		                      u'浆纱工': '3828', u'电子/电器维修工程师/技师': '2920', u'汽车修理工': '5907', u'医院管理人员': '1302', u'网络推广总监': '2532',
		                      u'轨道交通工程师/技术员': '0575', u'送餐员': '4815', u'大堂经理': '4903', u'行程管理/计调': '4920', u'硫化工': '6219', u'大客户销售': '3009',
		                      u'漂染工': '3824', u'日语翻译': '2002', u'电路工程师/技术员(模拟/数字)': '2905', u'产品/品牌主管': '0307', u'培训经理/主管': '0609',
		                      u'职业技术教师': '1211', u'锅炉工程师/技师': '0568', u'医疗器械销售经理/主管': '4125', u'业务跟单经理': '4004',
		                      u'集成电路IC设计/应用工程师': '2901', u'洗衣工': '5213', u'出纳员': '0414', u'助理业务跟单': '4007', u'媒介销售': '4312',
		                      u'会务/会展专员': '4306', u'人事总监': '0601', u'售前/售后技术支持工程师': '3207', u'签证专员': '4921', u'市场/营销/拓展专员': '0304',
		                      u'包装设计': '0927', u'审计经理/主管': '0410', u'验光师': '1326', u'组装工': '3715', u'客房服务员/楼面服务员': '4906', u'总监/部门经理': '0705',
		                      u'给排水/暖通工程': '2104', u'物业设施管理人员': '4705', u'调度员': '0831', u'网络/在线客服': '3213', u'项目经理': '2606', u'物业维修员': '4706',
		                      u'市场通路经理/主管': '0308', u'汽车/摩托车工程师': '0571', u'工长': '2145', u'印染工': '3823', u'工艺工程师': '2923', u'医药销售经理/主管': '4111',
		                      u'汽车钣金': '5913', u'物业管理经理': '4702', u'医疗器械销售代表': '4114', u'音效师': '4407', u'建筑制图/模型/渲染': '2110', u'房地产项目招投标': '4608',
		                      u'结构工程师': '0561', u'公关主管': '4302', u'中医科医生': '1322', u'4S店经理/维修站经理': '5901', u'经销商': '3006', u'体育教师': '1216', u'物流专员/助理': '0814',
		                      u'财务助理/文员': '0422', u'生产总监': '3514', u'需求工程师': '0147', u'空调工': '3708', u'牙科医生': '1319', u'质量管理/测试主管(QA/QC主管)': '3602',
		                      u'理货员': '5121', u'畜牧师': '5804', u'采购助理': '3905', u'物流主管': '0802', u'融资经理/融资主管': '3308', u'公关经理': '4301', u'园艺/园林/景观设计': '2117',
		                      u'高尔夫教练': '6406', u'环境/健康/安全工程师（EHS）': '3610', u'公共卫生/疾病控制': '1323', u'多媒体/游戏开发工程师': '2502', u'兼职': '5301$环保',
		                      u'砌筑工': '2134', u'公务员': '1501', u'塑料工程师': '5505', u'品质经理': '2705', u'可靠度工程师': '3605', u'房产项目配套工程师': '4603',
		                      u'成本经理/成本主管': '0408', u'电信网络工程师': '2807', u'铆工': '6213', u'网站营运专员': '2516', u'美容师': '5019', u'外科医生': '1317',
		                      u'行政主厨/厨师长': '4806', u'临床研究员': '4105', u'仓库管理员': '0809', u'幕墙工程师': '2122', u'游戏界面设计师': '2519', u'产品经理/主管': '2525',
		                      u'运输经理/主管': '0810', u'商务助理': '3105', u'装配工程师/技师': '0581', u'建筑项目助理': '2133', u'固定资产会计': '0448', u'企业秘书/董事会秘书': '0711',
		                      u'网店/淘宝运营': '6102', u'停车管理员': '4709', '切纸机操作工': '6314', u'证券分析师': '3302', '咨询总监': '1402', u'电信交换工程师': '2804',
		                      u'建筑工程师': '2101', u'彩妆培训师': '5013', u'加油站工作员': '5910', u'生产经理/车间主任': '3507', u'炼胶工': '6218', u'房地产中介/置业顾问': '6001', u'护工': '5211', u'清洁工': '5205', u'多媒体设计': '0926', u'美术编辑': '4504', u'合规主管/专员': '1110', u'汽车装饰美容': '5906', u'房地产销售': '6010', u'洗碗工': '4814', u'产品工艺/制程工程师': '0547', u'保险核保': '3407', u'房地产投资分析': '4610', u'服装领班': '3814', u'服装/纺织设计总监': '3812', u'喷塑工': '3722', u'医疗器械维修人员': '4119', u'房地产资产管理': '4611', u'预定部主管': '4916', u'市政工程师': '2132', u'放射科医师': '1327', u'系统集成工程师': '0137', u'特种车司机': '1835', u'建筑工程验收': '2121', u'家教': '1205', u'板房/楦头/底格出格师': '3806', u'收银员': '5119', u'客运司机': '1830', u'细纱工': '3827', u'电力工程师/技术员': '0569', u'美容培训师/导师': '5016', u'奢侈品业务': '5115', u'软件测试': '2707', u'水利/水电工程师': '0577', u'印刷机械机长': '6309', u'配置管理工程师': '2714', u'副总经理/副总裁': '0702', u'纺织工': '3820', u'电子技术研发工程师': '2917', u'网络工程师': '2504', u'市场通路专员': '0335', u'杂工': '4817', '音效设计师': '2523', '物料经理': '0803', '产品总监': '2531', u'玩具设计': '0929', u'钻工': '6211', u'情报信息分析人员': '1407', u'磨工': '6206', u'人事主管': '0603', u'印刷工': '6301', u'面点师': '4822', u'网店/淘宝客服': '6104', u'健身顾问/教练': '6401', u'网店店铺管理员': '6103', u'导演/编导': '4402', u'CNC工程师': '0566', u'水质检测员': '5606', u'物流总监': '0827', u'故障分析工程师': '3606', u'艺术指导/舞台美术设计': '4414', u'手机软件开发工程师': '2811', u'智能大厦/综合布线/安防/弱电': '2126', u'锅炉工': '3726', u'工程/设备主管': '0514', u'Flash设计/开发': '2520', u'项目执行/协调人员': '2608', u'医药技术研发人员': '4104', u'经纪人/星探': '4404', u'法务助理': '1107', u'综合门诊/全科医生': '1328', u'数据库工程师/管理员': '0108', u'打样/制版': '3807', u'餐饮服务员': '4803', u'仪表工': '3720', u'工程监理': '2107', u'烫工': '3818', u'硬件工程师': '2402', u'SPA 技师': '5023', u'物业招商/租赁/租售': '4704', u'团购经理/主管': '0234', u'编辑': '4502', u'按摩': '5007', u'会计经理/会计主管': '0404', u'公路/桥梁/港口/隧道工程': '2118', u'网站编辑': '2507', u'汽车质量管理': '5404', u'房地产店长/经理': '6004', u'岩土工程': '2119', u'管道/暖通': '2144', u'风险管理/控制': '3314', u'吹膜工': '6220', u'活动策划': '4313', u'实习生': '1703', u'酒店前台': '4905', u'娱乐领班': '6509', u'咨询员': '1404', u'财务顾问': '0445', u'健身房服务': '4918', u'专业培训师': '1406', u'首席财务官 CFO': '0444', u'会计': '0405', u'高级软件工程师': '0106', u'系统管理员/网络管理员': '2505', u'机械工程师': '0539', u'内科医生': '1301', u'货运代理': '0829', u'行政经理/主管/办公室主任': '2302', u'卖场经理/店长': '5101', u'培训/课程顾问': '5706', u'房地产销售经理/主管': '6009', u'薪资福利经理/主管': '0607', u'技术支持/维护经理': '2701', u'传菜主管': '4811', u'记者': '4503', u'企业/业务发展经理': '4208', u'网络信息安全工程师': '2509', u'网站维护工程师': '2513', u'版图设计工程师': '2922', u'药品市场推广主管/专员': '4110', u'算法工程师': '0148', u'保安经理': '4710', u'服装/纺织设计': '3801', u'防损员/内保': '5108', u'传菜员': '4825', u'韩语/朝鲜语翻译': '2007', u'工业工程师': '0560', u'广告创意总监': '4205', u'艺术/设计总监': '4403', u'熟食加工': '5111', u'食品/饮料研发': '5507', u'叉车司机': '1836', u'标准化工程师': '2704', u'货运司机': '1831', u'业务跟单': '4006', u'培训策划': '5703', u'木工': '2139', u'质量管理/测试工程师(QA/QC工程师)': '3603', u'美术指导': '4211', u'绿化工': '4713', u'银行柜员': '2216', u'注塑工': '6221', u'技工': '3701', u'外语培训师': '1215', u'硬件测试': '2708', u'二手车评估师': '5904', u'造纸研发': '5509', u'保险业务经理/主管': '3403', u'项目经理/主管': '0833', u'环境影响评价工程师': '5604', u'公关总监': '4315', u'注塑工程师/技师': '0563', u'互联网软件开发工程师': '2501', u'其他语种翻译': '2008', u'维修经理/主管': '0580', u'开发报建': '2127', u'兽医': '1315', u'保险理赔': '3408', u'物业机电工程师': '4708', u'旅游产品销售': '4919', u'校对/录入': '6302', u'会籍顾问': '3011', u'网页设计/制作/美工': '2508', u'DJ': '6503', u'数据通信工程师': '2805', u'媒介主管': '4308', u'射频工程师': '2924', u'市场/营销/拓展经理': '0302', u'农艺师': '5803',u'合伙人': '0704', u'医药学术推广': '4126', u'储备干部': '1702', u'培训生': '1701', u'医药技术研发管理人员': '4103', u'针灸、推拿': '1313', u'进出口/信用证结算': '2210', u'专科医生': '1318', u'视觉设计师': '2522', u'培训产品开发': '5707', u'设备主管': '3516', u'无线通信工程师': '2803', u'保洁': '4712', u'数码直印/菲林输出': '6310', u'电脑维修': '2717', u'养殖部主管': '5801', u'固废工程师': '5607', u'化妆师': '5020', u'供应链经理': '0825', u'人力资源信息系统专员': '0630', u'清洁服务人员': '4908', u'客户关系经理/主管': '3210', u'促销主管/督导': '0311', u'客户代表': '3003', u'生物工程/生物制药': '4101', u'大学/大专应届毕业生': '1602', u'网站架构设计师': '2512', u'打稿机操作员': '6313', u'审计专员/助理': '0419', u'泰语翻译': '2012', u'投资者关系': '0712', u'药品生产/质量管理': '4108', u'钣金工': '6214', u'面料辅料采购': '3803', u'电子商务专员': '2528', u'移动通信工程师': '2806', u'贸易/外贸专员/助理': '4002', u'供应链主管/专员': '0826', u'网络维修': '2715', u'培训专员/助理/培训师': '0610', u'幼教': '1207', u'送水工': '5214', u'店铺推广': '6105', u'原画师': '0933', u'FAE 现场应用工程师': '2912', u'文档工程师': '2713', u'财务分析员': '0407', u'服装/纺织/皮革跟单': '3804', u'寻呼员/话务员': '5203', u'销售助理': '3012', u'综合业务经理/主管': '2227', u'技术总监/经理': '2602', u'美体师': '5017', u'高级建筑工程师/总工': '2123', u'配菜/打荷': '4813', u'质量管理/验货员u(QA/QC)': '3805', u'汽车装配工艺工程师': '5406', u'用户体验（UE/UX）设计师': '2536', u'电力线路工': '3718', u'化工实验室研究员/技术员': '5502', u'娱乐服务员': '6510', u'挡车工': '3825', u'会务/会展经理': '4304', u'系统架构设计师': '0143', u'科研人员': '1001$餐饮服务', u'系统工程师': '0127', u'平面设计总监': '0930', u'保险经纪人/保险代理': '3404', u'投资/基金项目经理': '3305', u'婚礼/庆典策划服务': '6502', u'测试工程师': '2915', u'通信电源工程师': '2808', u'仿真应用工程师': '0145', u'质量检验员/测试员': '3604', u'销售代表': '3001', u'中专/职校生': '1601', u'大学教授': '1208', u'技术研发经理/主管': '0510', u'国内贸易人员': '4003', u'销售主管': '0203', u'软件UI设计师/工程师': '0144', u'生态治理/规划': '5609', u'代驾': '1840', u'麻醉医生': '1308', u'院校教务管理人员': '1202', u'网络管理(Helpdesk)': '2712', u'人事经理': '0602', u'广告创意/设计主管/专员': '4206', u'压痕工': '6316', u'变压器与磁电工程师': '2921', u'VIP专员': '3212', u'项目总监': '3513', u'清算人员': '2211', u'渠道/分销主管': '0220', u'财务分析经理/主管': '0406', u'集装箱业务': '0830', u'个人业务客户经理': '2224', u'化验员': '3510', u'电子工程师/技术员': '2903', u'电工': '3706', u'抹灰工': '2142', u'预结算员': '2124', u'舞蹈老师': '6403', u'商务主管/专员': '3104', u'选址拓展/新店开发': '0338', u'高级硬件工程师': '2401', u'信审核查': '2229', u'配色工': '3822', u'广告客户总监/副总监': '4201', u'机修工': '6203', u'物业机电维修工': '4715', u'电声/音响工程师/技术员': '2906', u'光伏系统工程师': '0583', u'汽车设计工程师': '5402', u'店员/营业员': '5102', u'招聘专员/助理': '0626', u'房地产评估': '6002', u'增值产品开发工程师': '2810', u'数控操机': '6201', u'保险精算师': '3401', u'通信技术工程师': '2801', u'绘画': '0932', u'药品注册': '4107', u'融资专员': '3309', u'区域销售经理': '0226', u'酒店/宾馆经理': '4901', u'投资银行财务分析': '3313', u'家政服务/保姆': '5206', u'建筑设计师': '2131', u'出版/发行': '4507', u'临床协调员': '4106', u'督导/巡店': '5117', u'楼面经理': '4904', u'咨询热线/呼叫中心服务人员': '3208', u'金融/经济研究员': '3304', u'办事处首席代表': '0708', u'金融产品经理': '3312', u'测绘/测量': '2120', u'演员/群众演员': '6507', u'瓦工': '2135', u'放映经理/主管': '4412', u'西点师/面包糕点加工': '5109', u'培训讲师': '5702', u'票务': '4910', u'证券/期货/外汇经纪人': '3301', u'高级物业顾问/物业顾问': '4701', u'司仪': '6501', u'调研员': '1409', u'美容助理': '5002', u'投诉专员': '3211', u'化学分析测试员': '4116', u'金融产品销售': '3315', u'促销经理': '0310', u'动物营养/饲料研发': '5806', u'客户主管/专员': '2214', u'团购业务员': '3008', u'销售经理': '0202', u'招投标管理': '4122', u'文案/策划': '4207', u'风险控制': '2209', u'销售行政助理': '3106', u'信贷管理': '2215', u'供应商开发': '3909', u'咨询经理': '1403', u'搬运工': '0836', u'德语翻译': '2003', u'陈列员': '5104', u'计算机硬件': '2400', u'环保工程师': '5601', u'资金经理/主管': '0449', u'UI设计师/顾问': '2515', u'造型师': '5021', u'建筑安装施工员': '2111', u'汽车喷漆': '5914', u'游戏策划师': '2518', u'纸样师/车板工': '3808', u'医疗器械注册': '4117', u'销售工程师': '3004', u'媒介经理': '4307', u'兼职教师': '1210', u'铣工': '6207', u'物料主管/专员': '0804', u'美容顾问': '5001', u'总工程师/副总工程师': '3502', u'策略发展总监': '0710', u'仪器/仪表/计量分析师': '2914', u'营养师': '1314', u'薪资福利专员/助理': '0608', u'海关事务管理': '0832', u'旋压工': '3719', u'发型助理/学徒': '5005', u'企业策划人员': '4209', u'美容整形师': '1320', u'舞蹈演员': '6505', u'图书管理员/资料管理员': '2307', u'环境/健康/安全经理/主管（EHS）': '3609', u'日式厨师': '4821', u'叉车/铲车工': '3707', u'列车/地铁车长': '1825', u'营业部大堂经理': '2230', u'培训督导': '5701', u'市场企划专员': '0337', u'结构/土木/土建工程师': '2102', u'餐厅领班': '4802', u'模具工程师': '0548', u'维修工程师': '0537', u'影视策划/制作人员': '4401', u'裁剪工': '3815', u'医药销售代表': '4112', u'促销员': '5118', u'发型师': '5004', u'护理主任/护士长': '1324', u'美甲师': '5006', u'裁床': '3809', u'绩效考核专员/助理': '0628', u'售前/售后技术支持经理': '3205', u'首席执行官CEO/总裁/总经理': '0701', u'水处理工程师': '5602', u'公关专员': '4303', u'工业/产品设计': '0919', u'志愿者/社会工作者': '1903', u'预定员': '4917', u'业务分析经理/主管': '3108', u'电气工程师/技术员': '2904', u'室内设计': '2108', u'税务专员/助理': '0412', u'材料工程师': '0582', u'高级业务跟单': '4005', u'网络推广专员': '2534', u'焊接工程师/技师': '0564', u'包装工': '3716', u'刨工': '6209', u'电梯工': '2141', u'电子商务经理/主管': '2527', u'吊车司机': '1838', u'法务主管/专员': '1102', u'小学教师': '1209', u'西餐厨师': '4820', u'市场企划经理/主管': '0336', u'行李员': '4907', u'班车司机': '1833', u'氩弧焊工': '3717', u'客服经理': '3202', u'保险培训师': '3410', u'人事助理': '0605', u'生产主管': '3509', u'工程/设备工程师': '0515', u'仓库经理/主管': '0808', u'船舶工程师': '0572', u'游泳教练': '6404', u'管家部经理/主管': '4914', u'医疗器械市场推广': '4113', u'供应链总监': '0828', u'采购总监': '3901', u'统计员': '0446', u'饲养员': '5805', u'房地产项目/开发/策划主管/专员': '4602', u'保安人员': '4711', u'驻唱/歌手': '6504', u'房地产项目/开发/策划经理': '4601', u'行政总监': '2301', u'镗工': '6212', u'楼宇自动化': '2125', u'综合业务专员': '2228', u'环保检测': '5605', u'客户经理/主管': '0208', u'汽车电工': '5912', u'钢筋工': '2138', u'石油天然气技术人员': '0578', u'测试员': '2709', u'区域销售总监': '0230', u'调墨技师': '6311', u'安全员': '2129', u'模特': '6506', u'律师助理': '1103', u'调酒师/侍酒师/吧台员': '4808', u'药库主任/药剂师': '1304', u'信息技术专员': '2604', u'讲师/助教': '1204', u'针织工': '3821', u'Web前端开发': '2539', u'中学教师': '1201', u'化工技术应用/化工工程师': '5501', u'地勤人员': '1824', u'快递员': '0813', u'家具/家居用品设计': '0928', u'订单处理员': '0834', u'规划与设计': '2109', u'摄影师/摄像师': '4406', u'渠道/分销经理': '0207', u'行政专员/助理': '2303', u'半导体技术': '2907', u'浇注工': '2137', u'保险电销': '3414', u'车工': '6205', u'保险产品开发/项目策划': '3402', u'广告客户主管/专员': '4203', u'驯兽师/助理驯兽师': '1902', u'生产领班/组长': '3515', u'认证工程师': '3607', u'拍卖/担保/典当业务': '3310', u'瘦身顾问': '5003', u'质量管理/测试经理(QA/QC经理)': '3601', u'物业管理主管': '4714', u'焊工': '3703', u'工程造价师/预结算经理': '2105', u'法务经理': '1106', u'废气处理工程师': '5608', u'供应商管理': '3611', u'合规经理': '1109', u'销售总监': '0201', u'列车/地铁司机': '1826', u'产品专员': '2526', u'产品/品牌专员': '0330', u'放映员': '4413', u'中国方言翻译': '2013', u'印刷排版/制版': '6307', u'漆工': '3724', u'招聘经理/主管': '0606', u'高级客户经理/客户经理': '2213', u'电分操作员': '6312', u'飞行器设计与制造': '0573', u'财务主管/总账主管': '0403', u'咖啡师': '4816', u'财务经理': '0402', u'网络/在线销售': '3010', u'合同管理': '2128', u'学徒工': '3727', u'投资银行业务': '3307', u'空调/热能工程师': '0585', u'ERP实施顾问': '0146', u'贸易/外贸经理/主管': '4001', u'会务/会展主管': '4305', u'救生员': '6405', u'后期制作': '4411', u'护士/护理人员': '1305', u'铲车司机': '1837', u'模具工': '6217', u'船员': '1828', u'瑜伽老师': '6402', u'酒店/宾馆销售': '4902', u'音乐/美术教师': '1214', u'建筑工程管理/项目经理': '2106', u'体育运动教练': '6407', u'汽车检验/检测': '5905', u'装订工': '6308', u'品类经理': '5112', u'绩效考核经理/主管': '0627', u'汽车安全性能工程师': '5405', u'市场/营销/拓展总监': '0301', u'汽车项目管理': '5412', u'经理助理/秘书': '2304', u'广告客户经理': '4202', u'技术支持/维护工程师': '2702', u'理财顾问/财务规划师': '3405', u'销售行政经理/主管': '3101', u'空调维修': '5215', u'月嫂': '5209', u'光源与照明工程': '0570', u'后勤': '2306', u'客服主管': '3203', u'实验室负责人/工程师': '0512', u'配色技术员': '5504', u'船务/空运陆运操作': '0815', u'脚本开发工程师': u'2517', u'科研管理人员': '1002', u'客服总监': '3201', u'投资/理财顾问': '3306', u'药品市场推广经理': '4109', u'法语翻译': '2004', u'首席运营官COO': '0707', u'大客户管理': '0235', u'审核员': '3615', u'特效设计师': '2521', u'嵌入式软件开发(Linux/单片机/PLC/DSP…)': '2910', u'涂料研发工程师': '5503', u'发动机/总装工程师': '5414', u'网络推广经理/主管': '2533', u'契约管理': '3413', u'灯光师': '4415', u'葡萄牙语翻译': '2011', u'安防系统工程师': '2925', u'折弯工': '6204', u'铸造/锻造工程师/技师': '0562', u'电镀工': '3721', u'计算机辅助设计工程师': '0141', u'店长/经理': '4801', u'晒版员': '6306', u'语音/视频开发工程师': '2514', u'家电维修': '5216', u'技术研发工程师': '0511', u'抛光工': '6215', u'工程/机械绘图员': '0523', u'ERP技术开发': '0117', u'礼仪/迎宾': '4804', u'复卷工': '6317', u'行长/副行长': '2207', u'单证员': '0812', u'临床数据分析员': '4123', u'业务拓展主管/经理': '0232', u'校长': '1213', u'网店/淘宝店长': '6101', u'数控编程': '6202', u'系统测试': '2706', u'美容店长': '5018', u'出租车司机': '1832', u'促销员/导购': '0312', u'项目主管': '2607', u'整经工': '3826', u'保险内勤': '3411', u'医药招商': '4120', u'前台接待/总机/接待生': '2305', u'安防主管': '5113', u'导购员': '5105', u'工程/设备经理': '0513', u'活动执行': '4314', u'专柜彩妆顾问(BA)': '5014', u'媒介专员': '4309', u'采购员': '3904', u'手机应用开发工程师': '2537', u'生产计划/物料管理(PMC)': '3508', u'市场助理': '0305', u'政府事务管理': '4121', u'采购主管': '3903', u'买手': '3908', u'油漆工': '2140', u'美发店长': '5022', u'安检员': '0835', u'工艺品/珠宝设计鉴定': '0920', u'普工/操作工': '3710', u'信息技术经理/主管': '2603', u'裱胶工': '6315', u'SEO搜索引擎优化': '2524', u'项目工程师': '3504', u'俄语翻译': '2005', u'驾校教练': '1839', u'商务司机': '1810', u'冲压工': '6208', u'理疗师': '1321', u'IC验证工程师': '2902', u'导游/旅行顾问': '4909', u'样衣工': '3819', u'前台迎宾': '6511', u'作家/撰稿人': '4517', u'兼职店员': '5106', u'场长(农/林/牧/渔业)': '5802', u'产品/品牌经理': '0306', u'钟点工': '5212', u'银行客户总监': '2231', u'乘务员': '1801', u'医疗器械生产/质量管理': '4118', u'电话销售': '3005', u'网店模特': '6107', u'预订员': '4824', u'报关与报检': '0811', u'营运经理': '3505', u'销售行政专员/助理': '3102', u'宠物护理/美容': '5010', u'总裁助理/总经理助理': '0703', u'储备经理人': '3406'}

		self.keyword = {}
		self.page_num = '1'
		self.post_dict = {'__EVENTTARGET': '',
						'__EVENTARGUMENT': '',
						'__LASTFOCUS': '',
						'__VIEWSTATE': '',
					'MainMenuNew1%24CurMenuID': 'MainMenuNew1_imgResume%7Csub4',
					'ctrlSerach%24hidTab': '',
					'ctrlSerach%24hidFlag': '',
					'ctrlSerach%24ddlSearchName': '',
					'ctrlSerach%24hidSearchID': '23%2C7%2C5%2C3%2C6%2C4%2C1%2C24%2C2',
					'ctrlSerach%24hidChkedExpectJobArea': '0',
					'ctrlSerach%24KEYWORD': '',
					'ctrlSerach%24KEYWORDTYPE': '0',
					'ctrlSerach%24AREA%24Text': '%E5%B9%BF%E5%B7%9E',
					'ctrlSerach%24AREA%24Value': '',
					'ctrlSerach%24TopDegreeFrom': '5',
					'ctrlSerach%24TopDegreeTo': '5',
					'ctrlSerach%24LASTMODIFYSEL': '5',
					'ctrlSerach%24WorkYearFrom': '5',
					'ctrlSerach%24WorkYearTo': '5',
					'ctrlSerach%24WORKFUN1%24Text': '%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9',
					'ctrlSerach%24WORKFUN1%24Value': '',
					'ctrlSerach%24WORKINDUSTRY1%24Text': '%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9',
					'ctrlSerach%24WORKINDUSTRY1%24Value': '',
					'ctrlSerach%24AgeFrom': '22',
					'ctrlSerach%24AgeTo': '28',
					'ctrlSerach%24EXPECTJOBAREA%24Text': '%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9',
					'ctrlSerach%24EXPECTJOBAREA%24Value': '',
					'ctrlSerach%24txtUserID': '-%E5%A4%9A%E4%B8%AA%E7%AE%80%E5%8E%86ID%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80-',
					'ctrlSerach%24txtSearchName': '',
					'pagerBottom%24txtGO': '3',
					'pagerBottom%24lbtnGO': '+',
					'cbxColumns%240': 'AGE',
					'cbxColumns%241': 'WORKYEAR',
					'cbxColumns%242': 'SEX',
					'cbxColumns%244': 'AREA',
					'cbxColumns%249': 'TOPDEGREE',
					'cbxColumns%2413': 'WORKFUNC',
					'cbxColumns%2414': 'LASTUPDATE',
					'hidSearchHidden': '',
					'hidUserID': '',
					'hidCheckUserIds': '',
					'hidCheckKey': '',
					'hidEvents': '',
					'hidBtnType': '',
					'hidDisplayType': '0',
					'hidJobID': '',
					'hidValue': '',
					'hidWhere': '',
					'hidSearchNameID': '',
					'hidEhireDemo': '',
					'hidNoSearch': '',
					'hidYellowTip' :'0'
					}


	def get_post_viewstat(self):
		try:
			t0 = time.time()
			self.get_cookie_2()
			t1 = time.time() - t0
			logging.info('------load cookie use ---11111---- time %s s' % str(t1))
			url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
			hidWhere = r'hidWhere=00%230%230%230%7C99%7C20150829%7C20160229%7C99%7C99%7C99%7C99%7C99%7C000000%7C000000%7C99%7C99%7C99%7C0000%7C99%7C99%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C000000%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0'
			hidWhere = hidWhere.replace('20160229', time.strftime('%Y%m%d', time.localtime())).replace('20150829', (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d'))
			self.post_data_first = self.post_data_first + hidWhere
			html = None
			if not html:
				html = self.rand_post(url, self.post_data_first)
				if html.find('id="Login_btnLoginCN"') > 0:
					self.get_cookie()
					html = self.rand_post(url, self.post_data_first)
				t2 = time.time() - t0
				logging.info('--request 51job use time is %s s' % str(t2))
				soup = BeautifulSoup(html, 'html.parser')
				post_dynamic = soup.select('#__VIEWSTATE')[0]['value']
				post_dynamic = urllib.quote_plus(post_dynamic)
				hidCheckUserIds = soup.select('#hidCheckUserIds')[0]['value']
				hidCheckUserIds = urllib.quote_plus(hidCheckUserIds)
				hidCheckKey = soup.select('#hidCheckKey')[0]['value']
				hidCheckKey = urllib.quote_plus(hidCheckKey)
				hidValue = soup.select('#hidValue')[0]['value']
				hidValue = urllib.quote_plus(hidValue)
				with open('/data/fetch/task/51/search_viewstat.txt', 'w+') as f1:
					f1.write(post_dynamic)
				with open('/data/fetch/task/51/hidCheckUserIds.txt', 'w+') as f2:
					f2.write(hidCheckUserIds)
				with open('/data/fetch/task/51/hidCheckKey.txt', 'w+') as f3:
					f3.write(hidCheckKey)
				with open('/data/fetch/task/51/hidValue.txt', 'w+') as f4:
					f4.write(hidValue)
			t3 = time.time() - t0
			logging.info('get post viewstat use time is %s s' % str(t3))
				# print self.post_data_first
				# print 'record viewstat +++++++++++++'
		except Exception, e:
			print e, traceback.format_exc()

	# def run_crawl(self, area=None, year=None,
	# 				age=None, degree=None, keyword=None, keywordtype=None,
	# 				industry=None, work_func=None, job_area=None,
	# 				updatetime='180', page_num='1', sid=None):
	# 	try:
	# 		logging.info('second crawl beginning +++++2222++++')
	# 		t0 = time.time()
	# 		get_viewstat = open('/data/fetch/task/51/search_viewstat_1.txt', 'r+').read()
	# 		hidCheckUserIds = open('/data/fetch/task/51/hidCheckUserIds_1.txt', 'r+').read()
	# 		hidCheckKey = open('/data/fetch/task/51/hidCheckKey_1.txt', 'r+').read()
	# 		url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
	# 		hidValue='KEYWORDTYPE%230*LASTMODIFYSEL%235*AGE%2324%7C24*WORKYEAR%238%7C8*AREA%23030200*TOPDEGREE%236%7C6*KEYWORD%23php'
	# 		hidWhere = r'00%230%230%230%7C99%7C{}%7C{}%7Cager%7Cager%7C4%7C4%7C99%7C000000%7C030200%7C99%7C99%7C99%7C0000%7C1%7C1%7C99%7C{industry}%7Cwork_func%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7Cjob_area%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23php&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0'
	#
	# 		if updatetime == '60':
	# 			hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-60)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
	# 		elif updatetime == '30':
	# 			hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-30)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
	# 		elif updatetime == '7':
	# 			hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
	# 		elif updatetime == '180':
	# 			hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-180)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
	#
	# 		if keyword:
	# 			self.post_dict['ctrlSerach%24KEYWORD'] = keyword
	# 			hidValue = hidValue.replace('php', keyword)
	# 			hidWhere = hidWhere.replace('php', keyword)
	# 			self.post_dict['hidValue'] = hidValue
	# 		else:
	# 			self.post_dict['ctrlSerach%24KEYWORD'] = ''
	# 			hidValue = hidValue.replace('php', '')
	# 			hidWhere = hidWhere.replace('php', '')
	#
	# 		if keywordtype:
	# 			self.post_dict['ctrlSerach%24KEYWORDTYPE'] = keywordtype
	# 			hidWhere = hidWhere.replace('00%230', '00%23' + keywordtype)
	#
	# 		if area:
	# 			# area_quote = urllib.quote_plus(area)
	# 			self.post_dict['ctrlSerach%24AREA%24Text'] = area
	# 			self.post_dict['ctrlSerach%24AREA%24Value'] = self.convert_area[area]
	# 			hidValue = hidValue.replace('030200', self.convert_area[area])
	# 			hidWhere = hidWhere.replace('030200', self.convert_area[area])
	# 			self.post_dict['hidValue'] = hidValue
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			area_quote = urllib.quote_plus('选择/修改')
	# 			self.post_dict['ctrlSerach%24AREA%24Text'] = area_quote
	# 			self.post_dict['ctrlSerach%24AREA%24Value'] = ''
	# 			hidValue = hidValue.replace('030200', '000000')
	# 			hidWhere = hidWhere.replace('030200', '000000')
	# 			self.post_dict['hidValue'] = hidValue
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if year:
	# 			self.post_dict['ctrlSerach%24WorkYearFrom'] = self.convert_year[year][-1]
	# 			self.post_dict['ctrlSerach%24WorkYearTo'] = self.convert_year[year][-1]
	# 			hidValue = hidValue.replace('8', self.convert_year[year][-1])
	# 			hidWhere = hidWhere.replace('7C4%7C4', self.convert_year[year])
	# 			self.post_dict['hidValue'] = hidValue
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			self.post_dict['ctrlSerach%24WorkYearFrom'] = '0'
	# 			self.post_dict['ctrlSerach%24WorkYearTo'] = '99'
	# 			hidWhere = hidWhere.replace('7C4%7C4', '7C99%7C99')
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if age:
	# 			# age_list = age.split('-')
	# 			# age_from, age_to = age_list[0], age_list[1]
	# 			# self.post_dict['ctrlSerach%24AgeFrom'] = age_from
	# 			# self.post_dict['ctrlSerach%24AgeTo'] = age_to
	# 			hidValue = hidValue.replace('ager', age)
	# 			hidWhere = hidWhere.replace('ager', age)
	# 			self.post_dict['hidValue'] = hidValue
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			self.post_dict['ctrlSerach%24AgeFrom'] = ''
	# 			self.post_dict['ctrlSerach%24AgeTo'] = ''
	# 			hidWhere = hidWhere.replace('ager', '99')
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if degree:
	# 			self.post_dict['ctrlSerach%24TopDegreeFrom'] = self.convert_degree[degree][-1]
	# 			self.post_dict['ctrlSerach%24TopDegreeTo'] = self.convert_degree[degree][-1]
	# 			hidValue = hidValue.replace('6', self.convert_degree[degree][-1])
	# 			hidWhere = hidWhere.replace('7C1', self.convert_degree[degree])
	# 			self.post_dict['hidValue'] = hidValue
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			self.post_dict['ctrlSerach%24TopDegreeFrom'] = ''
	# 			self.post_dict['ctrlSerach%24TopDegreeTo'] = ''
	# 			hidWhere = hidWhere.replace('7C1', '7C99')
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if industry:
	# 			# industry_quote = urllib.quote_plus(industry)
	# 			self.post_dict['ctrlSerach%24WORKINDUSTRY1%24Text'] = industry
	# 			self.post_dict['ctrlSerach%24WORKINDUSTRY1%24Value'] = industry + '%7C' + self.industry_dict[industry]
	# 			hidWhere = hidWhere.format(industry=self.industry_dict[industry])
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			hidWhere = hidWhere.format(industry='00')
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if work_func:
	# 			# work_func_quote = urllib.quote_plus(work_func)
	# 			self.post_dict['ctrlSerach%24WORKFUN1%24Text'] = work_func
	# 			self.post_dict['ctrlSerach%24WORKFUN1%24Value'] = work_func
	# 			hidWhere = hidWhere.replace('work_func', self.function_dict[work_func])
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			hidWhere = hidWhere.replace('work_func', '0000')
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if job_area:
	# 			# job_area_quote = urllib.quote_plus(job_area)
	# 			self.post_dict['ctrlSerach%24EXPECTJOBAREA%24Text'] = job_area
	# 			self.post_dict['ctrlSerach%24EXPECTJOBAREA%24Value'] = self.convert_area[job_area]
	# 			hidWhere = hidWhere.replace('job_area', self.convert_area[job_area])
	# 			self.post_dict['hidWhere'] = hidWhere
	# 		else:
	# 			hidWhere = hidWhere.replace('job_area', '000000')
	# 			self.post_dict['hidWhere'] = hidWhere
	#
	# 		if page_num:
	# 			self.post_dict['pagerBottom%24txtGO'] = page_num
	#
	#
	# 		self.post_dict['hidCheckUserIds'] = hidCheckUserIds
	# 		self.post_dict['hidCheckKey'] = hidCheckKey
	# 		self.post_dict['__VIEWSTATE'] = get_viewstat
	#
	# 		post_data = ''
	# 		for k, v in self.post_dict.iteritems():
	# 			post_data = post_data + k + '=' + v + '&'
	#
	# 		post_data = post_data.rstrip('&')
	# 		html = None
	# 		if not html:
	# 			html = self.rand_post(url, post_data)
	# 			if html.find('id="Login_btnLoginCN"') > 0:
	# 				self.login2()
	# 			soup = BeautifulSoup(html, 'html.parser')
	# 			resume_count = soup.select('strong')[0].get_text()
	# 			page_count = soup.select('strong')[1].get_text().split('/')[1]
	# 			show_list = soup.select('.inbox_td4')
	#
	# 		html_array = {'resume_list': '', 'page_count': '', 'resume_count': ''}
	# 		resume_list = []
	# 		db = connect_mysql()
	# 		cur = db.cursor()
	# 		for i in range(1, 51):
	# 			try:
	# 				html_dict = {'id': '', 'age': '', 'work_year': '', 'gender': '', 'area': '',
	# 								'degree': '', 'function': '', 'resume_update': '', 'status': ''}
	# 				td_message = '#trBaseInfo_' + str(i)
	# 				td_data = soup.select(td_message)[0]
	# 				if td_data.get_text().find(u'\u7b80\u5386\u4e3a\u6076\u610f\u6295\u9012') > 0:
	# 					continue
	# 				html_dict['id'] = td_data.select('.inbox_td4')[0].find_next()['value']
	# 				sql = """SELECT id,phone FROM `talent` WHERE talent_mark='{}' and talent_source='51job'""".format(html_dict['id'])
	# 				cur.execute(sql)
	# 				zid_phone = cur.fetchall()
	# 				try:
	# 					html_dict['z_id'] = zid_phone[0][0]
	# 					html_dict['phone'] = zid_phone[0][1]
	# 				except:
	# 					html_dict['z_id'] = None
	# 					html_dict['phone'] = None
	# 				html_dict['age'] = td_data.select('.inbox_td4')[2].get_text()
	# 				html_dict['work_year'] = td_data.select('.inbox_td4')[3].get_text()
	# 				html_dict['gender'] = td_data.select('.inbox_td4')[4].get_text()
	# 				html_dict['area'] = td_data.select('.inbox_td4')[5].get_text()
	# 				html_dict['degree'] = td_data.select('.inbox_td4')[6].get_text()
	# 				html_dict['function'] = td_data.select('.inbox_td4')[7].get_text()
	# 				html_dict['resume_update'] = td_data.select('.inbox_td4')[8].get_text()
	# 				html_dict['status'] = td_data.select('.inbox_td4')[9].get_text()
	# 				resume_list.append(html_dict)
	# 			except IndexError:
	# 				print traceback.format_exc(), IndexError
	# 		db.close()
	# 		html_array['resume_list'] = resume_list
	# 		html_array['resume_count'] = resume_count
	# 		html_array['page_count'] = page_count
	# 		with open('/data/fetch/db/search.html', 'w+') as f:
	# 			f.write(html)
	# 		html_array = json.dumps(html_array)
	# 		t1 = time.time() - t0
	# 		logging.info('second crawl use time is %s s' % str(t1))
	# 		print '*********----END----+**********'
	# 		return html_array
	#
	# 	except Exception, e:
	# 		print e, traceback.format_exc()
	# 		logging.debug('second crawl error .....')

	def run_crawl_first(self, area=None, year=None, age=None, degree=None, keyword=None, keywordtype=None,
						industry=None, work_func=None, job_area=None, updatetime='180', page_num='1', sid=None):
		try:
			logging.info('first crawl begin -----000000-------')
			self.get_cookie_2()
			t0 = time.time()
			# self.get_post_viewstat()
			if int(page_num) == 1:
				get_viewstat = open('/data/fetch/task/51/search_viewstat.txt', 'r+').read()
				hidCheckUserIds = open('/data/fetch/task/51/hidCheckUserIds.txt', 'r+').read()
				hidCheckKey = open('/data/fetch/task/51/hidCheckKey.txt', 'r+').read()
			else:
				get_viewstat = open('/data/fetch/task/51/search_viewstat_1.txt', 'r+').read()
				hidCheckUserIds = open('/data/fetch/task/51/hidCheckUserIds_1.txt', 'r+').read()
				hidCheckKey = open('/data/fetch/task/51/hidCheckKey_1.txt', 'r+').read()

			url = r'http://ehire.51job.com/Candidate/SearchResume.aspx'
			hidValue='KEYWORDTYPE%230*LASTMODIFYSEL%235*AGE%2324%7C24*WORKYEAR%238%7C8*AREA%23030200*TOPDEGREE%236%7C6*KEYWORD%23php'
			hidWhere = r'00%230%230%230%7C99%7C{}%7C{}%7Cager_from%7Cager_to%7C4%7C4%7C99%7C000000%7C030200%7C99%7C99%7C99%7C0000%7C1%7C1%7C99%7C{industry}%7Cwork_func%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7Cjob_area%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23php&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0'

			if updatetime == '60':
				hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-60)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
			elif updatetime == '30':
				hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-30)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
			elif updatetime == '7':
				hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')
			elif updatetime == '180':
				hidWhere = hidWhere.format((datetime.datetime.now() + datetime.timedelta(days=-180)).strftime('%Y%m%d'), time.strftime('%Y%m%d', time.localtime()), industry='{industry}')

			if keyword:
				self.post_dict['ctrlSerach%24KEYWORD'] = keyword
				hidValue = hidValue.replace('php', keyword)
				hidWhere = hidWhere.replace('php', keyword)
				self.post_dict['hidValue'] = hidValue
			else:
				self.post_dict['ctrlSerach%24KEYWORD'] = ''
				hidValue = hidValue.replace('php', '')
				hidWhere = hidWhere.replace('php', '')

			if keywordtype:
				self.post_dict['ctrlSerach%24KEYWORDTYPE'] = keywordtype
				hidWhere = hidWhere.replace('00%230', '00%23' + keywordtype)

			if area:
				# area_quote = urllib.quote_plus(area)
				self.post_dict['ctrlSerach%24AREA%24Text'] = area
				self.post_dict['ctrlSerach%24AREA%24Value'] = self.convert_area[area]
				hidValue = hidValue.replace('030200', self.convert_area[area])
				hidWhere = hidWhere.replace('030200', self.convert_area[area])
				self.post_dict['hidValue'] = hidValue
				self.post_dict['hidWhere'] = hidWhere
			else:
				area_quote = urllib.quote_plus('选择/修改')
				self.post_dict['ctrlSerach%24AREA%24Text'] = area_quote
				self.post_dict['ctrlSerach%24AREA%24Value'] = ''
				hidValue = hidValue.replace('030200', '000000')
				hidWhere = hidWhere.replace('030200', '000000')
				self.post_dict['hidValue'] = hidValue
				self.post_dict['hidWhere'] = hidWhere

			if year:
				self.post_dict['ctrlSerach%24WorkYearFrom'] = self.convert_year[year][-1]
				self.post_dict['ctrlSerach%24WorkYearTo'] = self.convert_year[year][-1]
				hidValue = hidValue.replace('8', self.convert_year[year][-1])
				hidWhere = hidWhere.replace('7C4%7C4', self.convert_year[year])
				self.post_dict['hidValue'] = hidValue
				self.post_dict['hidWhere'] = hidWhere
			else:
				self.post_dict['ctrlSerach%24WorkYearFrom'] = '0'
				self.post_dict['ctrlSerach%24WorkYearTo'] = '99'
				hidWhere = hidWhere.replace('7C4%7C4', '7C99%7C99')
				self.post_dict['hidWhere'] = hidWhere

			if age:
				age_list = age.split('-')
				age_from, age_to = age_list[0], age_list[1]
				self.post_dict['ctrlSerach%24AgeFrom'] = age_from
				self.post_dict['ctrlSerach%24AgeTo'] = age_to
				hidValue = hidValue.replace('ager_from', age_from)
				hidWhere = hidWhere.replace('ager_from', age_from).replace('ager_to', age_to)
				self.post_dict['hidValue'] = hidValue
				self.post_dict['hidWhere'] = hidWhere
			else:
				self.post_dict['ctrlSerach%24AgeFrom'] = ''
				self.post_dict['ctrlSerach%24AgeTo'] = ''
				hidWhere = hidWhere.replace('ager_from', '99').replace('ager_to', '99')
				self.post_dict['hidWhere'] = hidWhere

			if degree:
				self.post_dict['ctrlSerach%24TopDegreeFrom'] = self.convert_degree[degree][-1]
				self.post_dict['ctrlSerach%24TopDegreeTo'] = self.convert_degree[degree][-1]
				hidValue = hidValue.replace('6', self.convert_degree[degree][-1])
				hidWhere = hidWhere.replace('7C1', self.convert_degree[degree])
				self.post_dict['hidValue'] = hidValue
				self.post_dict['hidWhere'] = hidWhere
			else:
				self.post_dict['ctrlSerach%24TopDegreeFrom'] = ''
				self.post_dict['ctrlSerach%24TopDegreeTo'] = ''
				hidWhere = hidWhere.replace('7C1', '7C99')
				self.post_dict['hidWhere'] = hidWhere

			if industry:
				self.post_dict['ctrlSerach%24WORKINDUSTRY1%24Text'] = industry
				self.post_dict['ctrlSerach%24WORKINDUSTRY1%24Value'] = industry + '%7C' + self.industry_dict[industry]
				hidWhere = hidWhere.format(industry=self.industry_dict[industry])
				self.post_dict['hidWhere'] = hidWhere
			else:
				hidWhere = hidWhere.format(industry='00')
				self.post_dict['hidWhere'] = hidWhere

			if work_func:
				self.post_dict['ctrlSerach%24WORKFUN1%24Text'] = work_func
				self.post_dict['ctrlSerach%24WORKFUN1%24Value'] = work_func
				hidWhere = hidWhere.replace('work_func', self.function_dict[work_func])
				self.post_dict['hidWhere'] = hidWhere
			else:
				hidWhere = hidWhere.replace('work_func', '0000')
				self.post_dict['hidWhere'] = hidWhere

			if job_area:
				# job_area_quote = urllib.quote_plus(job_area)
				self.post_dict['ctrlSerach%24EXPECTJOBAREA%24Text'] = job_area
				self.post_dict['ctrlSerach%24EXPECTJOBAREA%24Value'] = self.convert_area[job_area]
				hidWhere = hidWhere.replace('job_area', self.convert_area[job_area])
				self.post_dict['hidWhere'] = hidWhere
			else:
				hidWhere = hidWhere.replace('job_area', '000000')
				self.post_dict['hidWhere'] = hidWhere

			if page_num:
				self.post_dict['pagerBottom%24txtGO'] = page_num

			if sid:
				self.post_dict['ctrlSerach%24txtUserID'] = sid
				self.post_dict['ctrlSerach%24btnExactQuery'] = '%E6%9F%A5%E8%AF%A2'
				self.post_dict.pop('pagerBottom%24lbtnGO')            # 通过id搜索简历

			self.post_dict['hidCheckUserIds'] = hidCheckUserIds
			self.post_dict['hidCheckKey'] = hidCheckKey
			self.post_dict['__VIEWSTATE'] = get_viewstat

			# post_data = urllib.urlencode(self.post_dict)
			post_data = ''
			for c, z in self.post_dict.iteritems():
				post_data = post_data + c + '=' + z + '&'

			t1 = time.time() - t0
			logging.info('first crawl get post data and load cookie use time is %s' % str(t1))
			post_data = post_data.rstrip('&')
			html = None
			if not html:
				html = self.rand_post(url, post_data)
				if html.find('id="Login_btnLoginCN"') > 0:
					self.get_cookie_2()
					html = self.rand_post(url, post_data)

				if html.find('没有搜到您想找的简历') > 0:
					logging.warn('not find resume ,condition too much or id error')
					empty_json = json.dumps({'code': '-7', 'message': 'not find resume'})
					return empty_json

				if html.find('账号异常') > 0:
					logging.warn('account error ------')
					return json.dumps({'code': '-12', 'message': 'account error'})

				t2 = time.time() - t0
				logging.info('request 51job to urllib use time %s s' % str(t2))
				with open('/data/fetch/db/trans/search.html', 'w+') as f:
					f.write(html)
				html_latter_part = html.find('<td style="width:100%;" colspan="2" class="inbox_td9">')
				if html_latter_part > 0:
					logging.info('html latter part get  =======')
					html_first_part = html.find('</title>')
					html = html[0:html_first_part] + '</title>' + '<tr>' + html[html_latter_part:-1]
					soup = BeautifulSoup(html, 'html.parser')
				else:
					soup = BeautifulSoup(html, 'html.parser')
				t3 = time.time() - t0
				logging.info('-----soup use time is %s' % str(t3))
				resume_count = soup.select('strong')[0].get_text()
				page_count = soup.select('strong')[1].get_text().split('/')[1]

			html_array = {'resume_list': '', 'page_count': '', 'resume_count': ''}
			resume_list = []
			db = connect_mysql()
			cur = db.cursor()
			for i in range(1, 51):
				try:
					html_dict = {'id': '', 'age': '', 'work_year': '', 'gender': '', 'area': '',
									'degree': '', 'function': '', 'resume_update': '', 'status': ''}
					td_message = '#trBaseInfo_' + str(i)
					try:
						td_data = soup.select(td_message)[0]
					except IndexError:
						break
					if td_data.get_text().find(u'\u7b80\u5386\u4e3a\u6076\u610f\u6295\u9012') > 0:
						continue
					html_dict['id'] = td_data.select('.inbox_td4')[0].find_next()['value']
					# sql = """SELECT id,phone FROM `talent` WHERE talent_mark='{}' and talent_source='51job'""".format(html_dict['id'])
					# cur.execute(sql)
					# zid_phone = cur.fetchall()
					# try:
					# 	html_dict['z_id'] = zid_phone[0][0]
					# 	html_dict['phone'] = zid_phone[0][1]
					# except:
					# 	html_dict['z_id'] = None
					# 	html_dict['phone'] = None
					html_dict['age'] = td_data.select('.inbox_td4')[2].get_text()
					html_dict['work_year'] = td_data.select('.inbox_td4')[3].get_text()
					html_dict['gender'] = td_data.select('.inbox_td4')[4].get_text()
					html_dict['area'] = td_data.select('.inbox_td4')[5].get_text()
					html_dict['degree'] = td_data.select('.inbox_td4')[6].get_text()
					html_dict['function'] = td_data.select('.inbox_td4')[7].get_text()
					html_dict['resume_update'] = td_data.select('.inbox_td4')[8].get_text()
					html_dict['status'] = td_data.select('.inbox_td4')[9].get_text()
					resume_list.append(html_dict)
				except Exception, e:
					print e, traceback.format_exc()
			sql_back = """SELECT id,phone,talent_mark FROM `talent` WHERE talent_mark in ({}) and talent_source='51job'"""
			sql_or = ''
			for resume in resume_list:
				s = "'" + str(resume['id']) + "'" + ','
				sql_or += s
			sql_id_common = sql_back.format(sql_or.rstrip(','))
			cur.execute(sql_id_common)
			zid_phone_back = cur.fetchall()
			db.close()
			if zid_phone_back:
				for zid in zid_phone_back:
					for resume in resume_list:
						if zid[2] == resume['id']:
							logging.info('>>>>>>> zid is %s' % str(zid))
							resume['z_id'] = zid[0]
							resume['phone'] = zid[1]
				else:
					for resume in resume_list:
						if 'z_id' not in resume.keys():
							resume['z_id'] = None
							resume['phone'] = None
			else:
				for resume in resume_list:
					resume['z_id'] = None
					resume['phone'] = None

			html_array['resume_list'] = resume_list
			html_array['resume_count'] = resume_count
			html_array['page_count'] = page_count
			html_array = json.dumps(html_array)
			t3 = time.time() - t0
			logging.info('crawl finish  use time is %s s' % str(t3))
			print '*********----first----+**********'
			return html_array

		except Exception, e:
			print e, traceback.format_exc()
			logging.debug('first crawl error .....')
			with open('/data/fetch/db/trans/error_51.html', 'w+') as f_error:
				f_error.write(html)
			return json.dumps({'code': '-5', 'msg': 'error html'})

	def id_down(self, resume_id):
		try:
			t0 = time.time()
			logging.info('id down start --------')
			run_id = id_down_51.IdDown51(resume_id)
			result = run_id.get_id()
			t1 = time.time() - t0
			logging.info('id down use time is %s' % str(t1))
			return result
		except Exception, e:
			print traceback.format_exc(), e
			logging.error('id down error -------')

	def get_cookie_2(self):
		# 更改这里参数来选择账号
		try:
			flag = False
			# self.account = libaccount.Manage(source='51job', option='down')
			redis_key_list = self.account.uni_user(time_period=self.time_period, num=self.time_num, hour_num=self.hour_num, day_num=self.day_num)
			# print redis_key_list, 8888888888
			if len(redis_key_list) > 0:
				while not flag:
					redis_key = random.choice(redis_key_list)
					redis_key_list.remove(redis_key)
					self.username = redis_key.split('_')[1].encode('utf-8')
					# print(self.username), 99999999999
					logging.info('51 get username is {}'.format(self.username))
					self.ck_str = self.account.redis_ck_get(self.username)
					# print self.ck_str
					self.headers['Cookie'] = self.ck_str
					flag = True
					# if self.login_status_chk():
					# 	print self.username * 100
					# 	logging.info('switching {} username {} success. '.format(self.module_name, self.username))
					# else:
					# 	sql_res = self.account.sql_password(self.username)
					# 	print sql_res
					# 	self.account.redis_ck_ex(self.username)  # 更新该用户名的cookie失效时间
					# 	self.password = sql_res[1]
					# 	self.ctmname = sql_res[0].encode('utf-8')
					# 	print self.password, self.username, self.ctmname
					# 	l_login = liblogin.Login51(cn=self.ctmname, un=self.username, pw=self.password)
					# 	self.ck_str = l_login.main(sleep=5)
					# 	self.headers['Cookie'] = self.ck_str
					# 	flag = True
					# if self.login_status_chk():
					# 	self.account.redis_ck_set(self.username, self.ck_str)
					# 	logging.info('51job user {} auto login success'.format(self.username))
					# 	logging.info('switching {} username {} success. '.format(self.module_name, self.username))
					# 	flag = True
				return flag
			else:
				logging.critical('no account left for {}'.format(self.module_name))
				# 这里需要发邮件警告。
				return False

		except Exception, e:
			logging.critical('error msg is {}'.format(str(e)), exc_info=True)
			return False


def connect_mysql():
	sql_config = {
		'host': "10.4.14.233",
		'user': "tuike",
		'passwd': "sv8VW6VhmxUZjTrU",
		'db': "tuike",
		'charset': "utf8",
	}
	db = MySQLdb.connect(**sql_config)
	return db


if __name__ == '__main__':
	print '+++++++++'
	# form = cgi.FieldStorage()
	# area = form['area'].value
	# year = form['year'].value
	# degree = form['degree'].value
	# keyword = form['keyword'].value
	# page_num = form['page_num'].value
	# appfetch = TransportSearch()
	# result_first = appfetch.run_crawl_first(area='上海',year='3-4年',age='26',degree='本科',keyword='java')
	# result =appfetch.run_crawl(area='上海',year='3-4年',age='26',degree='本科',keyword='java',page_num='3')
