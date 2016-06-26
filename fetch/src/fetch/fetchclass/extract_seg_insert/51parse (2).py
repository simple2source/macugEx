# -*- coding: UTF-8 -*-
import sys
reload(sys)
import json
sys.setdefaultencoding('utf8')
from ExtractSegInsert import *


if __name__ == "__main__":
  #curl -XGET 'http://183.131.144.102:8090/p_resume/51doc/_count?pretty' 

  # 测extract函数
  # extract("e:\\html\\307000488.html",output_dir='e:\\log2')   #设置保存目录

  # 测试insert函数
  # insert_test(json_file="e:\\log2\\212\\340\\21234090.json")
  
  # 测试dir_do1函数  测试完毕
  # dir_do1("e:\\html", output_dir="e:\\log2")
  
  # 测试dir_do2函数
  dir_do2(input_dir="e:\\log2\\")

  # 测试dir_do2函数
  # dir_do3(input_dir="e:\\log2\\205")

  # 测试dir_do23函数
  # dir_do23(input_dir="e:\\log2\\205")

  # 测试dir_do12函数
  # dir_do12("e:\\html\\659\\340\\")

  # 测试fetch_do123函数 
  # fetch_do123("e:\\html\\20500035.html")  


  # 测试dir_do123函数
  # dir_do123("e:\\html\\")