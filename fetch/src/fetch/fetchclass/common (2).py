#-*- coding:UTF-8 -*-

import urllib2,urllib,cookielib
import logging,os,shutil
import smtplib,ConfigParser
from email.mime.text import MIMEText


root_path=os.path.dirname(os.path.abspath(__file__))
root_path=os.path.dirname(root_path) #根目录
database_path = os.path.join(root_path,'database','fetch.db') #数据库文件路径
db_root = os.path.join(root_path,'db')#简历文件存储路径
conf_dir=os.path.join(root_path,'conf')#配置文件存放目录
cookie_root = os.path.join(root_path,'cookie')#cookie根目录，下有各个数据源的次级目录
task_root = os.path.join(root_path,'task')#任务根目录，下有各个数据源的次级目录
error_root = os.path.join(root_path,'error')#出错信息根目录，下有各个数据源的次级目录
log_dir = os.path.join(root_path,'log')#日志文件目录
buy_database_path = os.path.join(root_path, 'database', 'buy.db')
stat_db_path = os.path.join(root_path, 'database', 'autologin.db')
database_root = os.path.join(root_path, 'database')

basic_confpath=os.path.join(conf_dir,'basic.conf')
json_config_path = os.path.join(conf_dir, 'logging.json')

basic_dirs=[db_root,conf_dir,cookie_root,task_root,error_root]
for item in basic_dirs:
  if not os.path.isdir(item):
    os.makedirs(item)

#根据用户名查找企业名    
job51_account_info={'test0005':'盛德咨询2'}    


# url_post("http://www.baicu.com", {"keyword": "php"});

# url_post("http://www.baicu.com", 'postdict');

# post_data= "__EVENTTARGET=ctrlSerach%24btnConditionQuery&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=%2FwEPDwUKMTUzODk3NDA3OA8WGh4JUGFnZUluZGV4Zh4Mc3RyU2VsZWN0Q29sBTNBR0UsV09SS1lFQVIsU0VYLEFSRUEsVE9QREVHUkVFLFdPUktGVU5DLExBU1RVUERBVEUeCFBhZ2VTaXplAjIeBElzRU5oHhB2c1NlbGVjdGVkRmllbGRzBTNBR0UsV09SS1lFQVIsU0VYLEFSRUEsVE9QREVHUkVFLFdPUktGVU5DLExBU1RVUERBVEUeC0xvZ0ZpbGVOYW1lBRFzZWFyY2hyZXN1bWUuYXNweB4JUGFnZUNvdW50BQMyMDAeCFBhZ2VEYXRhBfMOMzMzNDUxMzY1fDMzNTU2MzgzN3wzMzU0MDkwODd8ODAxMzg5OTd8OTE3ODM0NTJ8MzI3NTUwODIzfDMzNDQ5ODIyMnwzMjU1OTAwMjd8OTk0MTAwMnwzMzU2NjY1MjN8NTkwNzc4OTd8ODc5MTk3MjF8MzM2Mzg2Mzk4fDUxNDAxNTk3fDg4NzE1MjM1fDMwNzE0OTExfDMzNTkwOTA4OXwyNDYwOTMwMnwzMzUxMTQzMjB8MzEwMzc4MDIyfDg1NDg2NDY0fDMzNTE1OTYyMHw4MzE0MzMwOXwzMjI4ODUzNzR8MzMyNTM5MjEwfDMzNTYxMTM4MHwzMjk2MDIzNTB8OTM3NjUyMjJ8Njg5MDM5MDd8MzAzNTAyODk4fDg5MDc5NzI2fDk1ODA5MjA2fDMyNDcxNzI5M3wzMzYzODU0ODd8MzI1NjY2NTcwfDg5ODM1Nzc5fDMyMjUxOTk1MnwzMDExMjMwMzZ8MzM2MjQwNDI2fDE5MjQ5MzR8MzM1MjUwODEyfDk0NTQwMjgwfDMwNTE3MjAxNXwyNzk2MjAwMXw1MTYzMTM0fDMzNjAzMzEwNHw4OTQ1ODU2OXwzMzU0MzA1MjF8NzU1MTA4ODl8OTM5MDIxMzN8MzIyMzMyMjA5fDMzNDg2NTk1MHwzMjU1MjY3OTl8MTIwNzA4MTR8MzIwMzc2NDg4fDMzMzMyOTk0MHwzMjc3OTI3MTB8NTg4NTM1MDZ8MzMwMzkzNzQxfDMxODA0MDk5OXw3MDUyNTA4NnwzMjE0MzIwMjh8OTI0NjgxOTF8MzM1ODA0MjE3fDE5NTg2ODg4fDExODcwNjU1fDc4Mzc4NTAyfDk1NjMwMDU4fDE1MTkzMzZ8MzM2MzEwMTIxfDMxMTg2OTA1Mnw3ODA1Mjk5N3w2OTg2MTk1fDkwNDcxNzc0fDYxOTA3OTN8MzA2MjA0NTQyfDkwNDM0MjAzfDMyOTA3MzAxNnw2NjczNjcwM3wzMzYyNDE5Mjh8MzM2MjU5MzQ1fDMxOTQ0MDYwOXwxOTY2OTExOXwxODk5OTg0fDMyMDExMzYzOXwzMzYzNzM2NjN8MzI2OTg5MTUzfDMzNjM3NzI0NHwzMTU4NzUzMTd8MzIxMDgxNTYwfDMzNjA3MzIxMHwzMzYzODYxNTF8ODMzNDczNDd8OTEzODg2ODZ8NzkzMTA3NDh8MzA4NzU0NDU5fDg2MjkwNzgyfDgxMjEzNzUwfDMyMjk0MDQ5OHwzMTUwMDE4MDd8MzIxNjc4NTE3fDMzNTE0OTE3NnwzMzQxMDkwMDN8MzM0MzE2NTI3fDc0NjM3NDQyfDMwOTk3NjU1NHwyOTUyNzIwNnwzMzU4NTY1NzN8MzM1MjE0MjUxfDkyNDE3MTkwfDMwNjc4MDUzN3wzMzM5MzMxMjh8ODM5NTcyMzF8MzMzMjcxNTAyfDY3NjAzMTE3fDMxOTQ0NTYwOXwzMjY3OTQ3ODZ8NTQyMzI4Mzd8NjMyNTg2MjB8Nzk3NDY2MDZ8MzIxODAyMDM4fDUyMzUxMTkxfDMyODY2NjE1NXwzMzQ2MjI3NTZ8MzE0NjQ0MzAzfDMyMjkxMTE5MnwzMTQzOTI5MTF8OTAwMjQ0OTd8MzAwMDQ0MTk3fDMzNDkxNTYwN3wyMDIwMDc2MHwzMTcxMDI3MTR8MzM2MTg0NDI3fDc5MTM0MTgzfDMyMjEzNDgwM3wzMTU0OTA3MjJ8NzQ1Mzg0MzR8MzEzNDAxNjM4fDMzNjEwMTA5OHw5NjYwNDI1OHwzMTM4MzgzODZ8MzIwODUzNDkzfDMyNzA2ODMyN3wzMTk0MDQ4Mzl8MzI5ODI5OTM3fDMyOTI1NjM1NnwzMzU3ODQ4NDd8MTA2MzE1NTV8MzI1OTM4OTAwfDMzMjY5MjMyMnwzMzQ2NTY3NDN8NTUwODI0ODB8MzAxNTc3Mzc1fDMzNDAyOTA1MHw3NTU2MDY4N3w3OTY4NjQ5MnwzMjU1NDQ2NDZ8MzM2MzM1MjI5fDEzMjM4MjgxfDQ5NzkwNTY1fDMyNzI4MDg4OHw2MDA5MTAxfDMzNjM4Njc5Nnw1Nzg4NzkzN3w3MzI3MjQwNHwxNzQzNjIyNHw3ODM3Mzg5OHwzMTc4NzI1NDN8MzA3MDYzMDE5fDg4NTk5MzAzfDMyODAxMjU5MHwzMzYzMjcxODF8MzE4MjQ4MTE4fDMyOTkzMTc0OXw2ODU2ODE2MHw5NDAzMTQ1OXw5NjQyMjcyMnw4NjkyNDM5OHwzMjE0NDEzMTZ8MzMzMzYyNDUyfDY1NjM2NTcwfDE1NjU0MTAyfDkzNjQyNTc3fDg4MzExMjIxfDMxMjc1NDczM3wzMzYyMzk2NzZ8MzI4MDg3NDgwfDc1NjY4NTE5fDMyMjg1NjU2MHwzMjMzODgyNTl8NjYwMjg4Mzl8MzI0ODQwNzQ1fDMyNzMxNDQxOXwzMDYzMTA2NzB8MzM2Mzg2NTgxfDYyMjAyMTU2fDMzMDQzMzU3MXw2NDUzNDA1MHw1MDcxOTIzMnwzMzYzNjkyMjUeDFRvdGFsUmVjb3JkcwK4Fx4JQmVnaW5QYWdlAgEeDVNlYXJjaFRpbWVPdXQFATAeB0VuZFBhZ2UCyAEeCHN0ckNvdW50BQM0MDQWAgIBD2QWFAIDD2QWBmYPDxYCHgRUZXh0ZWRkAgEPDxYCHw1lZGQCAg8WAh4EaHJlZgUBI2QCBA8PFgweCUV2ZW50RmxhZwUBMB4RSXNDb3JyZWxhdGlvblNvcnQFATAeCFNRTFdoZXJlBbUBMDAjMCMwIzB8OTl8MjAxNTA1MDJ8MjAxNTExMDJ8OTl8OTl8OTl8OTl8OTl8MDAwMDAwfDAwMDAwMHw5OXw5OXw5OXwwMDAwfDk5fDk5fDk5fDAwfDAwMDB8OTl8OTl8OTl8MDAwMHw5OXw5OXwwMHw5OXw5OXw5OXw5OXw5OXw5OXw5OXw5OXw5OXwwMzAyMDB8MHwwfDAwMDB8OTkjJUJlZ2luUGFnZSUjJUVuZFBhZ2UlIx4IU1FMVGFibGUFH1NfcmVzdW1lc2VhcmNoNiBhIFdJVEggKE5PTE9DSykeBVZhbHVlBXZLRVlXT1JEVFlQRSMwKkxBU1RNT0RJRllTRUwjNSpBR0UjfCpXT1JLWUVBUiMwfDk5KlRPUERFR1JFRSN8KkVYUEVDVEpPQkFSRUEjMDMwMjAwKktFWVdPUkQj5aSa5YWz6ZSu5a2X55So56m65qC86ZqU5byAHw0F3gHnroDljobmm7TmlrAgOiDlha3kuKrmnIjlhoUgIDvlubTpvoQgOiAtICA75bel5L2c5bm06ZmQIDogMC05OSAgO%2BWxheS9j%2BWcsCA6IOmAieaLqS%2Fkv67mlLkgIDvlrabljoYgOiAtICA76KGM5LiaIDog6YCJ5oupL%2BS%2FruaUuSAgO%2BiBjOiDvSA6IOmAieaLqS%2Fkv67mlLkgIDvmnJ%2FmnJvlt6XkvZzlnLAgOiDlub%2Flt54gIDvlhbPplK7lrZcgOiDlpJrlhbPplK7lrZfnlKjnqbrmoLzpmpTlvIBkFgwCAg9kFgJmD2QWBAIBDxBkEBUDEuivt%2BmAieaLqeaQnOe0ouWZqAblub%2Flt54G5ri45oiPFQMABzE5NTY5MzgHMjAxMDg1NhQrAwNnZ2cWAWZkAgMPDxYCHw0FBuWIoOmZpBYCHgdvbmNsaWNrBRdyZXR1cm4gY29uZmlybURlbENvbmQoKWQCAw8WBB8UBRhpZighY2hlY2tGb3JtKCkpIHJldHVybjseBXZhbHVlBQbmn6Xor6JkAgQPDxYCHw0FGOS%2FruaUueabtOWkmuafpeivouadoeS7tmRkAgUPZBYCZg9kFgICBQ9kFgoCBw9kFgRmDw8WBB8NBQ3pgInmi6kv5L%2Bu5pS5HgdUb29sVGlwBQ3pgInmi6kv5L%2Bu5pS5ZGQCAQ8WAh8TBQ3pgInmi6kv5L%2Bu5pS5ZAIKDxAPZBYCHghvbkNoYW5nZQVBcmV0dXJuIGlzTUJBKCdjdHJsU2VyYWNoX1RvcERlZ3JlZUZyb20nLCdjdHJsU2VyYWNoX1RvcERlZ3JlZVRvJylkZGQCGQ9kFgRmDw8WBB8NBQ3pgInmi6kv5L%2Bu5pS5HxYFDemAieaLqS%2Fkv67mlLlkZAIBDxYCHxMFDemAieaLqS%2Fkv67mlLlkAh4PZBYEZg8PFgQfDQUN6YCJ5oupL%2BS%2FruaUuR8WBQ3pgInmi6kv5L%2Bu5pS5ZGQCAQ8WAh8TBQ3pgInmi6kv5L%2Bu5pS5ZAImD2QWBGYPDxYEHw0FBuW5v%2BW3nh8WBQblub%2Flt55kZAIBDxYCHxMFBuW5v%2BW3nmQCBg8PFgIfDQUG5p%2Bl6K%2BiZGQCDg9kFgJmD2QWAgICDxYEHxUFBuehruWumh8UBTBpZighY3VzdG9tUXVlcnlOdW1zLmlzT3V0TWF4UXVlcnlOdW1zKCkpIHJldHVybjtkAgUPFgIeBXN0eWxlBQ5kaXNwbGF5OmJsb2NrOxYCZg8PFgIfDQWHAuaCqOebruWJjei%2FmOaciSBbIDxhIGhyZWY9ImphdmFzY3JpcHQ6dm9pZCgwKSIgc3R5bGUgPSJjb2xvcjojMjY2RUI5ICIgb25jbGljaz0iamF2YXNjcmlwdDp3aW5kb3cub3BlbignLi4vQ29tbW9uUGFnZS9Kb2JzRG93bk51bWJMaXN0LmFzcHgnLCdfYmxhbmsnLCdzY3JvbGxiYXJzPXllcyxXaWR0aD00MjhweCxIZWlnaHQ9NDUwcHgscmVzaXphYmxlPXllcycpIj48YiBjbGFzcz0iaW5mb19hdHQiPjQwNDwvYj48L2E%2BIF0g5Lu9566A5Y6G5Y%2Bv5Lul5LiL6L29ZGQCBg8WAh8YBQ1kaXNwbGF5Om5vbmU7ZAIHDxYCHgxVc2VyQnRuV2lkdGgbAAAAAABAU0ABAAAAZAIID2QWDmYPZBYCZg8PFgIfDWVkZAIBDw8WCh8DaB4KUFBhZ2VJbmRleGYfAgIyHwgCuBceE0lzUmVzdW1lQmV0YVJlcXVlc3RnZBYGZg8PFgQeCENzc0NsYXNzBRFjdHJsUGFnaW5hdGlvbkJ0MB4EXyFTQgICZGQCAQ8PFgQfHAURY3RybFBhZ2luYXRpb25CdDAfHQICZGQCAg8PFgQfHAURY3RybFBhZ2luYXRpb25CdDEfHQICZGQCAg8PFgIeCEltYWdlVXJsBU1odHRwOi8vaW1nMDEuNTFqb2JjZG4uY29tL2ltZWhpcmUvZWhpcmUyMDA3L2RlZmF1bHQvaW1hZ2UvaW5ib3gvbGlzdF9vdmVyLmdpZmRkAgMPDxYCHx4FTmh0dHA6Ly9pbWcwMS41MWpvYmNkbi5jb20vaW1laGlyZS9laGlyZTIwMDcvZGVmYXVsdC9pbWFnZS9pbmJveC9kZXRhaWxfb3V0LmdpZmRkAgQPZBYEAgEPDxYEHxwFEnJlc3VtZV9idXR0b24xX291dB8dAgJkZAIDDw8WBB8cBRFyZXN1bWVfYnV0dG9uMV9vbh8dAgJkZAIGDxYCHgdWaXNpYmxlaBYCAgEPDxYCHx4FSWh0dHA6Ly9pbWcwMS41MWpvYmNkbi5jb20vaW1laGlyZS9laGlyZTIwMDcvZGVmYXVsdC9pbWFnZS9zZWFyY2hfbW9yZS5naWZkZAIHDw8WCh8DaB8aZh8CAjIfCAK4Fx8bZ2QWDgIBDw8WCh8NBQMgMSAeD0NvbW1hbmRBcmd1bWVudAUBMR8WBQExHxwFEWN0cmxQYWdpbmF0aW9uQnQxHx0CAmRkAgIPDxYKHw0FAyAyIB8gBQEyHxYFATIfHAURY3RybFBhZ2luYXRpb25CdDAfHQICZGQCAw8PFgofDQUDIDMgHyAFATMfFgUBMx8cBRFjdHJsUGFnaW5hdGlvbkJ0MB8dAgJkZAIEDw8WCh8NBQMgNCAfIAUBNB8WBQE0HxwFEWN0cmxQYWdpbmF0aW9uQnQwHx0CAmRkAgUPDxYKHw0FAyA1IB8gBQE1HxYFATUfHAURY3RybFBhZ2luYXRpb25CdDAfHQICZGQCBg8PFgIfDWVkZAIHDw8WAh8NBQMuLi5kZAIJDxYCHxkbAAAAAACAYkABAAAAZAIKDxYCHxkbAAAAAACgYEABAAAAZAILDxYCHxkbAAAAAACAT0ABAAAAZAINDxBkEBURBuW5tOm%2BhAzlt6XkvZzlubTpmZAG5oCn5YirBuaIt%2BWPownlsYXkvY%2FlnLAH6K%2Bt6KiAMQznm67liY3mnIjolqoM5pyf5pyb5pyI6JaqBuS4k%2BS4mgblrabljoYJSVTmioDog70xCUlU5oqA6IO9MgbooYzkuJoG6IGM6IO9EueugOWOhuabtOaWsOaXtumXtAnlrabmoKHlkI0M5rGC6IGM54q25oCBFREDQUdFCFdPUktZRUFSA1NFWAVIVUtPVQRBUkVBA0ZMMQ1DVVJSRU5UU0FMQVJZDEVYUEVDVFNBTEFSWQhUT1BNQUpPUglUT1BERUdSRUUHSVRUWVBFMQdJVFRZUEUyDFdPUktJTkRVU1RSWQhXT1JLRlVOQwpMQVNUVVBEQVRFCVRPUFNDSE9PTBBDVVJSRU5UU0lUVUFUSU9OFCsDEWdnZ2dnZ2dnZ2dnZ2dnZ2dnZGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFhYFE2N0cmxTZXJhY2gkZGluZ3l1ZTEFFmN0cmxTZXJhY2gkY2hrX2RlZmF1bHQFB2ltZ0RpczEFB2ltZ0RpczIFDGNieENvbHVtbnMkMAUMY2J4Q29sdW1ucyQxBQxjYnhDb2x1bW5zJDIFDGNieENvbHVtbnMkMwUMY2J4Q29sdW1ucyQ0BQxjYnhDb2x1bW5zJDUFDGNieENvbHVtbnMkNgUMY2J4Q29sdW1ucyQ3BQxjYnhDb2x1bW5zJDgFDGNieENvbHVtbnMkOQUNY2J4Q29sdW1ucyQxMAUNY2J4Q29sdW1ucyQxMQUNY2J4Q29sdW1ucyQxMgUNY2J4Q29sdW1ucyQxMwUNY2J4Q29sdW1ucyQxNAUNY2J4Q29sdW1ucyQxNQUNY2J4Q29sdW1ucyQxNgUNY2J4Q29sdW1ucyQxNg%3D%3D&MainMenuNew1%24CurMenuID=MainMenuNew1_imgResume%7Csub4&ctrlSerach%24hidTab=&ctrlSerach%24hidFlag=&ctrlSerach%24ddlSearchName=&ctrlSerach%24hidSearchID=23%2C7%2C5%2C3%2C6%2C4%2C1%2C24%2C2&ctrlSerach%24hidChkedExpectJobArea=0&ctrlSerach%24KEYWORD=%E5%A4%9A%E5%85%B3%E9%94%AE%E5%AD%97%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80&ctrlSerach%24KEYWORDTYPE=0&ctrlSerach%24AREA%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24AREA%24Value=&ctrlSerach%24TopDegreeFrom=&ctrlSerach%24TopDegreeTo=&ctrlSerach%24LASTMODIFYSEL=5&ctrlSerach%24WorkYearFrom=0&ctrlSerach%24WorkYearTo=99&ctrlSerach%24WORKFUN1%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24WORKFUN1%24Value=&ctrlSerach%24WORKINDUSTRY1%24Text=%E9%80%89%E6%8B%A9%2F%E4%BF%AE%E6%94%B9&ctrlSerach%24WORKINDUSTRY1%24Value=&ctrlSerach%24AgeFrom=&ctrlSerach%24AgeTo=&ctrlSerach%24EXPECTJOBAREA%24Text=%E5%8C%97%E4%BA%AC&ctrlSerach%24EXPECTJOBAREA%24Value=010000&ctrlSerach%24txtUserID=-%E5%A4%9A%E4%B8%AA%E7%AE%80%E5%8E%86ID%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80-&ctrlSerach%24txtSearchName=&pagerBottom%24txtGO=1&cbxColumns%240=AGE&cbxColumns%241=WORKYEAR&cbxColumns%242=SEX&cbxColumns%244=AREA&cbxColumns%249=TOPDEGREE&cbxColumns%2413=WORKFUNC&cbxColumns%2414=LASTUPDATE&hidSearchHidden=&hidUserID=&hidCheckUserIds=333451365%2C335563837%2C335409087%2C80138997%2C91783452%2C327550823%2C334498222%2C325590027%2C9941002%2C335666523%2C59077897%2C87919721%2C336386398%2C51401597%2C88715235%2C335909089%2C30714911%2C335114320%2C24609302%2C310378022%2C335159620%2C85486464%2C83143309%2C332539210%2C322885374%2C335611380%2C329602350%2C93765222%2C303502898%2C68903907%2C89079726%2C95809206%2C336385487%2C324717293%2C325666570%2C322519952%2C89835779%2C301123036%2C336240426%2C335250812%2C1924934%2C94540280%2C305172015%2C27962001%2C5163134%2C336033104%2C89458569%2C335430521%2C75510889%2C93902133&hidCheckKey=33f91c213d822ddf84aec9655728933f&hidEvents=&hidBtnType=&hidDisplayType=0&hidJobID=&hidValue=KEYWORDTYPE%230*LASTMODIFYSEL%235*AGE%23%7C*WORKYEAR%230%7C99*TOPDEGREE%23%7C*EXPECTJOBAREA%23030200*KEYWORD%23%E5%A4%9A%E5%85%B3%E9%94%AE%E5%AD%97%E7%94%A8%E7%A9%BA%E6%A0%BC%E9%9A%94%E5%BC%80&hidWhere=00%230%230%230%7C99%7C20150502%7C20151102%7C99%7C99%7C99%7C99%7C99%7C000000%7C000000%7C99%7C99%7C99%7C0000%7C99%7C99%7C99%7C00%7C0000%7C99%7C99%7C99%7C0000%7C99%7C99%7C00%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C99%7C030200%7C0%7C0%7C0000%7C99%23%25BeginPage%25%23%25EndPage%25%23&hidSearchNameID=&hidEhireDemo=&hidNoSearch=&hidYellowTip=0"
# // 替换 POST_dATA 广州 成 北京
#url_post("http://www.baicu.com", POST_dATA);


def url_post(url,postdict={},headers={},timeout=10):
  '''功能描述：通用post方法提交'''
  try:
    if not url.startswith("http://"):
      url = r"http://"+url
    post_str=''  
    cj = cookielib.CookieJar()
    #opener = urllib2.build_opener(urllib2.ProxyHandler({'http': '127.0.0.1:8888'}), urllib2.HTTPCookieProcessor(cj)) #通过代理强求转发post
    # proxy_handler = urllib2.ProxyHandler({'http':'192.168.1.92:8888'})
    # cookie_support = urllib2.HTTPCookieProcessor(cj)
    # opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)
    # urllib2.install_opener(opener)
   # if postdict is string:
   #  post_str = postdict
    if isinstance(postdict,dict):
      post_str = urllib.urlencode(postdict)
    if postdict:
      post_str = postdict
    if post_str:
      if headers:
        req = urllib2.Request(url,post_str,headers)
      else:
        req = urllib2.Request(url,post_str)
    else:
      if headers:
        req = urllib2.Request(url,'',headers)
      else:
        req = urllib2.Request(url)    

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
      html = response.read()   
      return html
    except urllib2.URLError as e:
      pass
    finally:
      if response:
        response.close()
  except Exception,e:
    logging.debug('post request error msg is %s' % str(e))
    return ''


def url_get(url,getdict={},headers={},timeout=10):
  '''功能描述：通用post方法提交'''
  try:
    if not url.startswith("http://"):
      url = r"http://"+url

    get_str= ''
    if getdict:
      get_str = urllib.urlencode(getdict)
    if get_str:
      if headers:
        req = urllib2.Request(url+'?'+get_str)
        for item in headers.keys():
          req.add_header(item,headers[item])
      else:
        req = urllib2.Request(url+'?'+get_str)
    else:
      req = urllib2.Request(url) 
      if headers:        
        for item in headers.keys():
          req.add_header(item,headers[item])

    cj = cookielib.CookieJar()

    # 正常跑不走代理的情况
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    #调试走代理的
    # proxy_handler = urllib2.ProxyHandler({'http':'192.168.1.16:8888'})
    # cookie_support = urllib2.HTTPCookieProcessor(cj)
    # opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)

    urllib2.install_opener(opener)
    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
      html = response.read()
      return html 
    except urllib2.URLError as e:
      pass
    finally:
      if response:
        response.close() 
  except Exception,e:
    logging.debug('get request error msg is %s' % str(e))
    return ''

def proxy_url_get(url,ip,getdict={},headers={},timeout=5):
  """ 通过代理请求 """
  try:
    if not url.startswith("http://"):
      url = r"http://"+url

    get_str= ''
    if getdict:
      get_str = urllib.urlencode(getdict)
    if get_str:
      if headers:
        req = urllib2.Request(url+'?'+get_str)
        for item in headers.keys():
          req.add_header(item,headers[item])
      else:
        req = urllib2.Request(url+'?'+get_str)
    else:
      req = urllib2.Request(url)
      if headers:
        for item in headers.keys():
          req.add_header(item,headers[item])

    cj = cookielib.CookieJar()

    # 正常跑不走代理的情况
    # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

    # 调试走代理的
    proxy_handler = urllib2.ProxyHandler({'http': ip})
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(proxy_handler,cookie_support,urllib2.HTTPHandler)

    urllib2.install_opener(opener)
    html = None
    response = None
    try:
      response = urllib2.urlopen(req,timeout=timeout)
      html = response.read()
      return html
    except urllib2.URLError as e:
      pass
    finally:
      if response:
        response.close()
  except Exception,e:
    logging.debug('get proxy request error msg is %s' % str(e))
    return ''
  
def move_file(src,dst):
  '''功能描述：安全方式移动文件'''
  try:
    if os.path.isfile(src):
      if os.path.isfile(dst):
        os.remove(dst)
      shutil.copy(src,dst)
      #os.remove(src)
    return True
  except Exception,e:
    logging.debug('error msg is %s' % str(e))
    return False  
  
def clear_dir(dir_path=''):
  '''功能描述：清空特定目录'''
  try:
    if dir_path:
      if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
      os.makedirs(dir_path)
      return True
    else:
      return False
  except Exception,e:
    logging.debug('error msg is %s' % str(e))
    return False
  
def write_file(fpath,file_str=''):
  '''功能描述：安全方式写入文件，自动处理目录以及重名问题'''
  try:
    father_dir=os.path.dirname(fpath)
    if not os.path.exists(father_dir):
      os.makedirs(father_dir)
    f=open(fpath+'.tmp','wb')
    f.write(file_str)
    f.close()
    os.rename(fpath+'.tmp',fpath)
    return True
  except Exception,e:
    logging.debug('error msg is %s' % str(e))
    return False
  

def sendEmail(moudle_name='', title='', message='',msg_type=0, des='T'):
  '''功能描述：通用发信模块，发送简要的email信息,
  新增加一参数，新增P报表'''
  try: 
    if os.path.exists(basic_confpath):
      cf = ConfigParser.ConfigParser()
      cf.read(basic_confpath)
      server_host=cf.get('email','server')
      uname=cf.get('email','username')
      upass=cf.get('email','password')
      tmp_user=cf.get('email','default_users')
      tmp_puser=cf.get('email','product_users')
      default_list = []
      product_list = []
      for m in tmp_user.split(';'):
        if m and default_list.count(m) == 0:
          default_list.append(m)
      users= default_list
      #产品的邮箱地址
      for m in tmp_puser.split(';'):
        if m and product_list.count(m) == 0:
          product_list.append(m)
      pusers = product_list
      operation_users = ['jerry@tuikor.com', 'vinsonli@tuikor.com']
      if msg_type == 1 and not users:
        users=['kelvin@tuikor.com']
      if des == 'P':
        users=pusers + users
      elif des == 'op':
        users = pusers + operation_users + users
    else:
      logging.info('defaulte conf file not exist.') 
      server_host='smtp.163.com'
      uname='hickwu@163.com'
      upass='HickWu608'
      users=['hick@tuikor.com']
      
    if server_host and uname and upass and users:
      msg = MIMEText(message, _subtype='html', _charset='UTF-8')
      #msg['From'] = uname
      msg['Subject'] = title
      msg['From'] = uname
      msg['To'] = ';'.join(users)

      s = smtplib.SMTP()
      #s.set_debuglevel(1)
      s.connect(server_host)
      s.login(uname,upass)
      s.sendmail(uname, users, msg.as_string())
      s.close()
      return True
    else:
      return False
  except Exception,e:
    logging.debug('error msg is %s ' % str(e))
    return False
  
  
  
if __name__ =='__main__':
  print 'dsdsdsddd'
  
