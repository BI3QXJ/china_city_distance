#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 查询中国两地直线距离

import os
import sys
import json
import sqlite3
from geopy.distance import geodesic

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_PATH, 'geoinfo-all.json')
DB_PATH = os.path.join(BASE_PATH, 'geoinfo-all.db')


def save_db(all_city_list):
    """ save [(city_name,(lat,log),level),..] into db """
    cx = sqlite3.connect(DB_PATH)
    cu = cx.cursor()
    cu.execute("""create table if not exists geo_info(
        district varchar(50), city varchar(50), prov varchar(50),
        lat real, log real, LEVEL integer)""")
    cu.execute("delete from geo_info")

    cx.commit()

    for item in all_city_list:
        cu.execute("insert into geo_info values (?,?,?,?,?,?)", item)

    cx.commit()
    cx.close()


def query_db(loc_name):
    # loc_name = loc_name.strip()
    cx = sqlite3.connect(DB_PATH)
    cu = cx.cursor()
    cu.execute("select * from geo_info where district like '"+loc_name+"%'", )
    cf = cu.fetchall()
    if len(cf) != 1:
        print('[%s]查询结果不唯一, 请输入更准确的地名' % loc_name)
        for city in cf:
            print(city[0], city[1], city[2], city[3], city[4])
        print('\n')
        return
    else:
        city = cf[0]
        return(city[0], city[1], city[2], city[3], city[4])


def load_data():
    with open(JSON_PATH, 'r') as fj:
        geo_json = json.loads(fj.read())

    all_city = []
    for prov in geo_json:
        if len(prov['districts']) == 0:
            all_city.append((
                prov['name'],
                prov['name'],
                prov['name'],
                float(prov['center'].split(',')[1]),
                float(prov['center'].split(',')[0]),
                1
            ))
        for city in prov['districts']:
            all_city.append((
                city['name'],
                city['name'],
                prov['name'],
                float(city['center'].split(',')[1]),
                float(city['center'].split(',')[0]),
                2
            ))
            for district in city['districts']:
                all_city.append((
                    district['name'],
                    city['name'],
                    prov['name'],
                    float(district['center'].split(',')[1]),
                    float(district['center'].split(',')[0]),
                    3
                ))

    return all_city


def main(argv):
    # save_db(load_data())      # 若需要重新生成, 请再次执行
    if len(argv) != 3:
        city_a = input('输入起点:')
        city_b = input('输入终点:')
    else:
        city_a = argv[1]
        city_b = argv[2]

    city_a = query_db(city_a)
    city_b = query_db(city_b)

    if city_a and city_b:
        loc_a = (city_a[3], city_a[4])
        loc_b = (city_b[3], city_b[4])
        print("从[%s]到[%s]的距离是: %d km" % (
            city_a[2]+'-'+city_a[1]+'-'+city_a[0],
            city_b[2]+'-'+city_b[1]+'-'+city_b[0],
            int(geodesic(loc_a, loc_b).km)
            ))


if __name__ == '__main__':
    main(sys.argv)