#  encoding:utf-8

import requests
from bs4 import BeautifulSoup
import os
import sqlite3
# from win32.win32crypt import CryptUnprotectData
import re
from time import sleep
import json
import sys
import base64

reload(sys)
sys.setdefaultencoding('utf-8')

public_date = '2017-12-22'
name_keyword = ['*']

url = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/executeSmartSearch1207-executeSmartSearch.shtml'
url2 = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/showSearchResult-startWa.shtml'
url3 = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/viewAbstractInfo0529-viewAbstractInfo.shtml'
url4 = 'http://www.pss-system.gov.cn/sipopublicsearch/patentsearch/retrieveUrls.shtml'
url5 = ''
# urlimg = 'http://www.pss-system.gov.cn/sipopublicsearch'

sleeptime = 15

domain = 'www.pss-system.gov.cn'

keys = '公开（公告）日>=%s AND 发明名称=(%s)' % (public_date, ' '.join(name_keyword))
vdb = "VDB:((PD>='%s' AND (TIVIEW='%s')))" % (public_date, "' or TIVIEW='".join(name_keyword))
data = {'searchCondition.searchExp': keys,
        'searchCondition.dbId': 'VDB',
        'searchCondition.searchType': 'Sino_foreign',
        'searchCondition.extendInfo[\'MODE\']': 'MODE_TABLE',
        'searchCondition.extendInfo[\'STRATEGY\']': 'STRATEGY_CALCULATE',
        'searchCondition.originalLanguage': '',
        'searchCondition.targetLanguage': '',
        'wee.bizlog.modulelevel': '0201203',
        'resultPagination.limit': 12}

start = 0
limit = 12
data2 = {'resultPagination.limit': limit,
         'resultPagination.sumLimit': 10,
         'resultPagination.start': start,
         'resultPagination.totalCount': 1563358,
         'searchCondition.searchType': 'Sino_foreign',
         'searchCondition.dbId': '',
         'searchCondition.extendInfo[\'STRATEGY\']': 'STRATEGY_CALCULATE',
         'searchCondition.strategy': '',
         'searchCondition.literatureSF': keys,
         'searchCondition.targetLanguage': '',
         'searchCondition.originalLanguage': '',
         'searchCondition.extendInfo[\'MODE\']': 'MODE_TABLE',
         'searchCondition.searchExp': keys,
         'resultPagination.sumLimit': 10,
         'searchCondition.executableSearchExp': vdb,
         'wee.bizlog.modulelevel': '0201203',
         'searchCondition.searchKeywords': '[2][ ]{0,}[0][ ]{0,}[1][ ]{0,}[7][ ]{0,}[.][ ]{0,}[1][ ]{0,}[2][ ]{0,}[.][ ]{0,}[2][ ]{0,}[2][ ]{0,}'
         }

data3 = {'nrdAn': 0,
         'sid': 0,
         'cid': 0,
         'wee.bizlog.modulelevel': '0201203'
         }

data4 = {'figureUrl': 0,
         'rids[0]': 0,
         'wee.bizlog.modulelevel': '0201203'

         }

cookiedata = {'IS_LOGIN': 'true',
              'WEE_SID': 'YM0gji8-WugD2G2pvZ8g2MDP98EshgXknhd-h2pgQfh9SznKRZuL!1482526794!792269866!1542439448383',
              'wee_password': 'eHR6eDAwMQ%3D%3D',
              'wee_username': 'YmpzeXh0Y3h6eDAwMQ%3D%3D',
              'avoid_declare': 'declare_pass',
              'JSESSIONID': 'YM0gji8-WugD2G2pvZ8g2MDP98EshgXknhd-h2pgQfh9SznKRZuL!1482526794!792269866'
              }

# 代理服务器
proxy = "127.0.0.1:1087"

# 用户名和密码(私密代理/独享代理)
username = "unlich"
password = "ecf0czqd"

proxy_auth = {"http": "http://%(user)s:%(pwd)s@%(ip)s/" % {'user': username, 'pwd': password, 'ip': proxy}}
proxy_whitelist = {"http": "http://%(ip)s" % {'ip': proxy}}

headers = {"Accept-Encoding": "gzip",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
           "Accept-Language": "zh-cn"}  # 使用gzip压缩传输数据让访问更快


def patent_vector():
    return {'name': '',
            'apply_id': '',
            'apply_date': '',
            'public_id': '',
            'public_date': '',
            'IPC': '',
            'apply_person': '',
            'invent_person': '',
            'pr': '',
            'pr_date': '',
            'cpc': '',
            'abstract': '',
            }


def init_file(file):
    header = ['专利名称', '申请号', '申请日', '公开（公告）号', '公开（公告日）', 'IPC分类号', '申请（专利权）人', '发明人', '优先权号', '优先权日', 'CPC分类号', '摘要']
    file.write('\t'.join(header) + '\n')


def deal_page(soup, file):
    reg = re.compile('<[^>]*>')
    dtos = soup.get('searchResultDTO')
    records = dtos.get('searchResultRecord')
    for item in records:
        patents = item.get('fieldMap')
        patent = patent_vector()

        patent['name'] = patents.get('TIVIEW')
        patent['name'] = reg.sub('', patent['name'])

        patent['apply_id'] = patents.get('AP')
        patent['apply_date'] = patents.get('APD')
        patent['public_id'] = patents.get('PN')
        patent['public_date'] = patents.get('PD')
        patent['IPC'] = patents.get('IC')
        patent['apply_person'] = patents.get('PAVIEW')
        patent['invent_person'] = patents.get('INVIEW')
        patent['pr'] = patents.get('PR')
        patent['pr_date'] = patents.get('PRD')

        # 获取摘要和cpc
        data3['nrdAn'] = patent['apply_id']
        data3['sid'] = patents.get('ID')
        data3['cid'] = patents.get('ID')

        response = requests.post(url3, proxies=proxy_whitelist, headers=headers, data=data3, cookies=cookiedata)
        sleep(sleeptime)
        content = response.content.decode('utf-8')

        soupd = json.loads(content)
        adto = soupd.get('abstractInfoDTO')
        abslist = adto.get('abstractItemList')
        patent['cpc'] = abslist[-1].get('value')
        ablist = adto.get('abIndexList')
        patent['abstract'] = ablist[0].get('value')
        patent['abstract'] = reg.sub('', patent['abstract'])

        # 获取图片
        # figrid = adto.get('figureRid')
        # if figrid:
        #     data4['figureUrl'] = figrid
        #     data4['rids[0]'] = figrid
        #     response = requests.post(url4, proxies=proxy_whitelist, headers=headers, data=data4, cookies=cookiedata)
        #     sleep(sleeptime)
        #     content = response.content.decode('utf-8')
        #     soupd = json.loads(content)
        #     figurls = soupd.get('figureUrls')
        #     if figurls:
        #         urlimg = 'http://www.pss-system.gov.cn/sipopublicsearch' + figurls[0]
        #         r = requests.get(urlimg, proxies=proxy_whitelist, headers=headers, data=data4, cookies=cookiedata)
        #         sleep(sleeptime)
        #         imgpath = patent['apply_id'] + '.png'
        #
        #         with open(imgpath, "wb") as f:
        #             f.write(r.content)
        #         f.close()

        write(file, patent)


def write(file, patent):
    line = [patent['name'],
            patent['apply_id'],
            patent['apply_date'],
            patent['public_id'],
            patent['public_date'],
            patent['IPC'],
            patent['apply_person'],
            patent['invent_person'],
            patent['pr'],
            patent['pr_date'],
            patent['cpc'],
            patent['abstract'],
            ]
    #     print('\t'.join(line))
    file.write('\t'.join(line).replace('‑', '') + '\n')


if __name__ == '__main__':
    file = 'res.txt'
    file = open(file, 'w')
    init_file(file)

    start = 0
    limit = 12

    response = requests.post(url2, proxies=proxy_whitelist, headers=headers, data=data, cookies=cookiedata)
    sleep(sleeptime)
    content = response.content.decode('utf-8')

    soup = json.loads(content)

    page_info = soup.get('resultPagination')

    page_count = page_info.get('totalCount')
    print('page_count: %s' % page_count)
    print('page 1')

    deal_page(soup, file)

    for i in range(1, int(page_count)):
        print('page %d' % (i + 1,))
        start += limit
        data2['resultPagination.limit'] = limit
        data2['resultPagination.start'] = start
        response = requests.post(url2, proxies=proxy_whitelist, headers=headers, data=data2, cookies=cookiedata)
        sleep(sleeptime)
        content = response.content.decode('utf-8')
        soup = json.loads(content)
        try:
            deal_page(soup, file)
        except ZeroDivisionError:
            print ("error")

    print('over')
