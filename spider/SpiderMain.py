# 备份说明：此文件已被备份，新的Scrapy爬虫位于 scrapy_spider/ 目录
# 备份时间：2025-06-21
# 原始爬虫保留作为参考和回滚使用

import requests  # 用于获取响应
from lxml import etree  # 用于解析HTML网页
import time  # 用于控制时间
import pymysql
cnx = pymysql.connect(
    host="localhost",
    user="root",
    password="123456",
    database="guangzhou_house"
)
cursor = cnx.cursor()
# 导入写好的连接数据库的包
headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'}
# 定义网页
url = 'https://gz.lianjia.com/zufang/pg45/#contentList'# 修改成自己需要爬取得城市名得即可
res = requests.get(url, headers=headers)
# 用于解决etree.HTML解析异常
html = etree.HTML(res.text)
# 使用xpath获取 房源标题 信息
name = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[1]/a/text()')
hrefs = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[1]/a/@href')
tags = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[3]/i[1]/text()')
print(tags)
# 去除列表中的 换行符 \n
name = [x.strip() for x in name if x.strip() != '']
# 所在区
district = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/a[1]/text()')
# 所在路
street = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/a[2]/text()')
# 房屋面积
floor_space1 = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/text()[5]')
# 定义一个空列表
floor_space = []
for i in floor_space1:
    # 将获取到的数据去除不需要的符号、空格、换行符
    floor_space1 = str(i).replace('㎡', '').replace("\n", '').replace(' ', '')
    floor_space.append(floor_space1) # 使用.append()方法将处理过的数据已追加的方存入列表中
# 朝向
orientation = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/text()[6]')
# 房型
house_type = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/p[2]/text()[7]')
# 去除列表中的 换行符 \n
house_type = [x.strip() for x in house_type if x.strip() != '']
# 价格
price = html.xpath('//*[@id="content"]/div[1]/div[1]/div/div/span/em/text()')
imgs = html.xpath('//*[@id="content"]/div[1]/div[1]/div/a/img/@data-src')
print(imgs[0])
for i in range(len(name)):
    try:
        print('开始爬取第'+str(i+1)+'条数据')
        title = name[i].split('·')[1].split(' ')[0]
        type = name[i].split('·')[0]
        building = name[i].split('·')[1].split(' ')[1]
        city = district[i]
        street1 = street[i]
        if '.' not in floor_space[i].strip():
            area = 80.00
        else:
            area = float(floor_space[i].strip())
        direct = orientation[i].strip().replace('㎡','')
        price1 = float(price[i])
        # 提取每个 <i> 标签的文本内容
        tag = tags[i]
        link = hrefs[i]
        img = imgs[i]
        print(title,type,building,city,street1,area,direct,price1,link,tag,img)
        insert_query = "INSERT INTO House(title,type,building,city,street,area,direct,price,link,tag,img) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s, %s, %s)"
        data = (title,type,building,city,street1,area,direct,price1,link,tag,img)
        cursor.execute(insert_query, data)
        cnx.commit()
        data = ()
    except Exception as e:
        print(e)
cursor.close()
cnx.close()
print('爬取完毕')
