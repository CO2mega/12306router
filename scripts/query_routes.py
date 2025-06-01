import sqlite3

# 城市到多个车站的映射
city_stations = {
    "北京": ["北京", "北京西", "北京南", "北京东"],
    "上海": ["上海", "上海虹桥", "上海南", "上海西"],
    "天津": ["天津", "天津西", "天津南"],
    "重庆": ["重庆", "重庆北", "重庆西", "重庆南"],
    "长沙": ["长沙", "长沙南", "长沙西"],
    "长春": ["长春", "长春西", "长春南"],
    "成都": ["成都", "成都东", "成都南", "成都西"],
    "福州": ["福州", "福州南"],
    "广州": ["广州", "广州南", "广州东", "广州北"],
    "贵阳": ["贵阳", "贵阳北"],
    "呼和浩特": ["呼和浩特", "呼和浩特东"],
    "哈尔滨": ["哈尔滨", "哈尔滨西", "哈尔滨东"],
    "合肥": ["合肥", "合肥南"],
    "杭州": ["杭州", "杭州东", "杭州南"],
    "海口": ["海口", "海口东"],
    "济南": ["济南", "济南西"],
    "昆明": ["昆明", "昆明南", "昆明西"],
    "拉萨": ["拉萨"],
    "兰州": ["兰州", "兰州西"],
    "南宁": ["南宁", "南宁东"],
    "南京": ["南京", "南京南"],
    "南昌": ["南昌", "南昌西"],
    "沈阳": ["沈阳", "沈阳北", "沈阳南"],
    "石家庄": ["石家庄", "石家庄北"],
    "太原": ["太原", "太原南"],
    "乌鲁木齐": ["乌鲁木齐", "乌鲁木齐南"],
    "武汉": ["武汉", "汉口", "武昌"],
    "西宁": ["西宁"],
    "西安": ["西安", "西安北", "西安南", "西安西"],
    "银川": ["银川"],
    "郑州": ["郑州", "郑州东"],
    "深圳": ["深圳", "深圳北", "深圳西", "深圳东"],
    "厦门": ["厦门", "厦门北", "厦门高崎"]
}

def query_direct_routes(start_city, end_city):
    """
    查询两个城市之间所有车站的直达路线，使用索引优化
    """
    try:
        # 连接数据库
        conn_stations = sqlite3.connect('stations.db')
        conn_trains = sqlite3.connect('trains.db')

        # 获取车站游标
        cursor_stations = conn_stations.cursor()
        cursor_trains = conn_trains.cursor()

        # 获取城市对应车站名列表
        start_stations = city_stations.get(start_city, [])
        end_stations = city_stations.get(end_city, [])

        if not start_stations:
            print(f"未找到出发城市：{start_city}")
            return
        if not end_stations:
            print(f"未找到到达城市：{end_city}")
            return

        # 使用 IN 子句和索引获取车站ID
        placeholders = ','.join(['?'] * len(start_stations))
        cursor_stations.execute(f"""
            SELECT name, id 
            FROM stations 
            WHERE name IN ({placeholders})
            /* 使用stations表的name索引 */
        """, start_stations)
        start_ids = cursor_stations.fetchall()

        placeholders = ','.join(['?'] * len(end_stations))
        cursor_stations.execute(f"""
            SELECT name, id 
            FROM stations 
            WHERE name IN ({placeholders})
            /* 使用stations表的name索引 */
        """, end_stations)
        end_ids = cursor_stations.fetchall()

        if not start_ids or not end_ids:
            print("未能找到城市中的有效车站")
            return

        # 建立ID->站名映射
        station_id_to_name = {name_id[1]: name_id[0] for name_id in start_ids + end_ids}

        # 使用CTE和索引优化查询
        query = """
        WITH start_routes AS (
            SELECT DISTINCT train_code, station_id, station_no
            FROM train_routes
            INDEXED BY idx_route_search  /* 使用综合索引 */
            WHERE station_id IN ({})
        ),
        end_routes AS (
            SELECT DISTINCT train_code, station_id, station_no
            FROM train_routes
            INDEXED BY idx_route_search  /* 使用综合索引 */
            WHERE station_id IN ({})
        )
        SELECT DISTINCT 
            s.train_code,
            s.station_id as start_id,
            e.station_id as end_id,
            s.station_no as start_no,
            e.station_no as end_no
        FROM start_routes s
        JOIN end_routes e 
            ON s.train_code = e.train_code  /* 使用train_code索引 */
        WHERE s.station_no < e.station_no
        ORDER BY s.train_code
        """.format(
            ','.join('?' * len(start_ids)),
            ','.join('?' * len(end_ids))
        )

        # 准备参数
        params = [id[1] for id in start_ids] + [id[1] for id in end_ids]
        cursor_trains.execute(query, params)
        
        # 获取结果
        routes = [
            (
                row[0],  # 车次
                station_id_to_name[row[1]],  # 出发站
                row[3],  # 出发站序
                station_id_to_name[row[2]],  # 到达站
                row[4]   # 到达站序
            )
            for row in cursor_trains.fetchall()
        ]

        # 打印结果
        if not routes:
            print(f"\n未找到从 {start_city} 到 {end_city} 的直达线路")
        else:
            print(f"\n从 {start_city} 到 {end_city} 的直达线路：")
            print("\n车次代码    | 上车站(序号) -> 下车站(序号)")
            print("-" * 50)
            for route in routes:
                print(f"{route[0]:<12} | {route[1]}({route[2]}) -> {route[3]}({route[4]})")
            print(f"\n共找到 {len(routes)} 条直达线路")

    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        conn_stations.close()
        conn_trains.close()

if __name__ == '__main__':
    start = input("请输入出发城市：")
    end = input("请输入到达城市：")
    query_direct_routes(start, end)
