#!/usr/bin/env python3
# filepath: c:\Users\1\Desktop\12306router\fix_train_routes_cities.py

import sqlite3
import os
import sys

def fix_train_routes_cities():
    """补全trains.db中train_routes表的city列中所有城市名"""
    try:
        # 确保数据库文件存在
        if not os.path.exists('trains.db'):
            print("错误: trains.db 文件不存在")
            return False
        
        # 连接trains.db数据库
        conn = sqlite3.connect('trains.db')
        cursor = conn.cursor()
        
        # 定义城市名称映射(缩写或可能的变体 -> 标准名称)
        city_mapping = {
            "北京": "北京",
            "上海": "上海", 
            "天津": "天津",
            "重庆": "重庆",
            "长沙": "长沙",
            "长春": "长春",
            "成都": "成都",
            "福州": "福州",
            "广州": "广州",
            "贵阳": "贵阳",
            "呼和": "呼和浩特",
            "呼市": "呼和浩特",
            "哈尔": "哈尔滨",
            "哈市": "哈尔滨",
            "合肥": "合肥",
            "杭州": "杭州",
            "海口": "海口",
            "济南": "济南",
            "昆明": "昆明",
            "拉萨": "拉萨",
            "兰州": "兰州",
            "南宁": "南宁",
            "南京": "南京",
            "南昌": "南昌",
            "沈阳": "沈阳",
            "石家": "石家庄",
            "石市": "石家庄",
            "太原": "太原",
            "乌鲁": "乌鲁木齐",
            "乌市": "乌鲁木齐",
            "武汉": "武汉",
            "西宁": "西宁",
            "西安": "西安",
            "银川": "银川",
            "郑州": "郑州",
            "深圳": "深圳",
            "厦门": "厦门",
            "大连": "大连",
            "青岛": "青岛"
        }
        
        # 扩展城市名映射，增加各种可能的变体
        expanded_mapping = {}
        for short, full in city_mapping.items():
            expanded_mapping[short] = full
            # 增加带"站"、"市"的变体
            expanded_mapping[f"{short}站"] = full
            expanded_mapping[f"{short}市"] = full
            expanded_mapping[f"{full}站"] = full
            expanded_mapping[f"{full}市"] = full
            # 如果是全名，加入各种前缀
            if len(full) > 2:
                expanded_mapping[full[:2]] = full
        
        # 首先检查train_routes表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='train_routes'")
        if not cursor.fetchone():
            print("错误: train_routes表不存在")
            return False
        
        # 检查city列是否存在于train_routes表中
        cursor.execute("PRAGMA table_info(train_routes)")
        columns = [col[1] for col in cursor.fetchall()]
        if "city" not in columns:
            print("错误: train_routes表中不存在city列")
            return False
        
        # 查询所有城市
        cursor.execute("SELECT DISTINCT city FROM train_routes")
        cities = [row[0] for row in cursor.fetchall() if row[0] and len(row[0]) > 0]
        print(f"发现 {len(cities)} 个不同的城市名称")
        
        # 输出样例城市
        print("\n当前城市名称示例:")
        unusual_cities = []
        for city in cities:
            if len(city) <= 2 or any(marker in city for marker in ["市", "站", "县"]):
                unusual_cities.append(city)
                if len(unusual_cities) <= 20:  # 仅显示前20个异常示例
                    print(f"- {city}")
        
        print(f"\n发现 {len(unusual_cities)} 个可能需要更新的城市名称")
        
        # 创建更新记录
        updates_count = 0
        
        # 更新有明确映射的城市名称
        for old_name, new_name in expanded_mapping.items():
            cursor.execute(
                "UPDATE train_routes SET city = ? WHERE city = ?",
                (new_name, old_name)
            )
            updates = cursor.rowcount
            if updates > 0:
                updates_count += updates
                print(f"已更新: {old_name} -> {new_name}, {updates}条记录")
        
        # 处理乌鲁木齐特例（可能有不同的写法）
        cursor.execute(
            "UPDATE train_routes SET city = '乌鲁木齐' WHERE city LIKE '%乌%' AND city LIKE '%鲁%'"
        )
        updates = cursor.rowcount
        if updates > 0:
            updates_count += updates
            print(f"已更新: *乌*鲁* -> 乌鲁木齐, {updates}条记录")
        
        # 处理呼和浩特特例
        cursor.execute(
            "UPDATE train_routes SET city = '呼和浩特' WHERE city LIKE '%呼和%'"
        )
        updates = cursor.rowcount
        if updates > 0:
            updates_count += updates
            print(f"已更新: *呼和* -> 呼和浩特, {updates}条记录")
        
        # 处理哈尔滨特例
        cursor.execute(
            "UPDATE train_routes SET city = '哈尔滨' WHERE city LIKE '%哈尔%'"
        )
        updates = cursor.rowcount
        if updates > 0:
            updates_count += updates
            print(f"已更新: *哈尔* -> 哈尔滨, {updates}条记录")
        
        # 处理石家庄特例
        cursor.execute(
            "UPDATE train_routes SET city = '石家庄' WHERE city LIKE '%石家%'"
        )
        updates = cursor.rowcount
        if updates > 0:
            updates_count += updates
            print(f"已更新: *石家* -> 石家庄, {updates}条记录")
        
        conn.commit()
        
        # 统计完成后的城市列表
        cursor.execute("SELECT DISTINCT city FROM train_routes")
        cities_after = [row[0] for row in cursor.fetchall() if row[0] and len(row[0]) > 0]
        print(f"\n更新完成! 共更新 {updates_count} 条记录")
        print(f"现在有 {len(cities_after)} 个不同的城市名称")
        
        # 输出部分城市示例进行验证
        print("\n更新后的城市名称示例:")
        for city in sorted(cities_after)[:20]:
            print(f"- {city}")
        
        # 检查可能仍然存在问题的城市
        print("\n可能仍需检查的城市名称:")
        problem_cities = []
        for city in cities_after:
            if len(city) <= 2 and city not in city_mapping.keys():
                problem_cities.append(city)
                
        for city in problem_cities[:20]:
            print(f"- {city}")
        
        if problem_cities:
            print(f"\n仍有 {len(problem_cities)} 个可能需要进一步检查的城市名称")
        
        # 检查特定城市是否已被正确处理
        cursor.execute("SELECT COUNT(*) FROM train_routes WHERE city = '乌鲁木齐'")
        urumqi_count = cursor.fetchone()[0]
        print(f"\n乌鲁木齐站点数量: {urumqi_count}")
        
        cursor.execute("SELECT COUNT(*) FROM train_routes WHERE city = '北京'")
        beijing_count = cursor.fetchone()[0]
        print(f"北京站点数量: {beijing_count}")
        
        return True
        
    except Exception as e:
        print(f"错误: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

# 主函数
if __name__ == "__main__":
    print("开始补全trains.db中train_routes表的city列中城市名称...")
    success = fix_train_routes_cities()
    sys.exit(0 if success else 1)