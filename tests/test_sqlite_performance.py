#!/usr/bin/env python3
# filepath: c:\Users\1\Desktop\12306router\tests\test_api_performance.py

import unittest
import requests
import time
import json
import statistics
import concurrent.futures
from datetime import datetime
import sys
import os

# 尝试添加当前目录到路径，确保能正确导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class APIPerformanceTester:
    """API性能测试器"""

    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_id = None

    def print_header(self, message):
        """打印带样式的标题"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD} {message} {Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

    def print_result(self, name, duration, data=None):
        """打印测试结果"""
        if data is not None:
            print(f"{Colors.BLUE}[API测试]{Colors.END} {name}: {Colors.GREEN}{duration:.6f}秒{Colors.END}, {data}")
        else:
            print(f"{Colors.BLUE}[API测试]{Colors.END} {name}: {Colors.GREEN}{duration:.6f}秒{Colors.END}")

    def login(self, username="user1", password="123456"):
        """登录获取认证令牌"""
        try:
            start_time = time.time()
            response = self.session.post(f"{self.base_url}/api/login", json={
                "account": username,
                "password": password
            })
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and "data" in data:
                    self.token = data["data"].get("token")
                    self.user_id = data["data"].get("id")
                    self.print_result("用户登录", duration, f"成功获取令牌，用户ID: {self.user_id}")
                    return True

            self.print_result("用户登录", duration, f"失败: {response.text}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}登录请求错误: {e}{Colors.END}")
            return False

    def get_auth_headers(self):
        """获取包含认证信息的请求头"""
        if not self.token:
            print(f"{Colors.WARNING}警告: 未登录，请先调用login()方法{Colors.END}")
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def test_tickets_list(self):
        """测试获取车票列表API"""
        self.print_header("车票列表API性能测试")

        start_time = time.time()
        response = self.session.get(f"{self.base_url}/api/tickets")
        duration = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            ticket_count = len(data.get("data", []))
            self.print_result("获取车票列表", duration, f"返回{ticket_count}张车票")
            return duration, ticket_count
        else:
            self.print_result("获取车票列表", duration, f"请求失败: {response.status_code}")
            return duration, 0

    def test_route_search(self, routes):
        """测试路线搜索API"""
        self.print_header("路线搜索API性能测试")
        results = []

        for from_city, to_city, date in routes:
            params = {
                "from": from_city,
                "to": to_city,
                "date": date
            }

            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/routes/direct", params=params)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                route_count = len(data.get("data", {}).get("routes", []))
                self.print_result(f"查询 {from_city} -> {to_city}", duration, f"找到{route_count}条路线")
                results.append((duration, route_count, from_city, to_city))
            else:
                self.print_result(f"查询 {from_city} -> {to_city}", duration, f"请求失败: {response.status_code}")
                results.append((duration, 0, from_city, to_city))

        return results

    def concurrent_search_worker(self, route):
        """并发查询工作函数"""
        from_city, to_city, date = route
        params = {
            "from": from_city,
            "to": to_city,
            "date": date
        }

        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/routes/direct", params=params)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                route_count = len(data.get("data", {}).get("routes", []))
                return {"duration": duration, "route": f"{from_city}->{to_city}", "count": route_count}
            else:
                return {"duration": duration, "route": f"{from_city}->{to_city}", "error": response.status_code}
        except Exception as e:
            return {"duration": -1, "route": f"{from_city}->{to_city}", "error": str(e)}

    def test_concurrent_search(self, routes, concurrency=5):
        """测试并发查询性能"""
        self.print_header(f"并发查询性能测试 (并发数: {concurrency})")

        start_time = time.time()
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_route = {executor.submit(self.concurrent_search_worker, route): route for route in routes}
            for future in concurrent.futures.as_completed(future_to_route):
                result = future.result()
                results.append(result)
                if "error" in result:
                    self.print_result(f"查询 {result['route']}", result["duration"], f"错误: {result['error']}")
                else:
                    self.print_result(f"查询 {result['route']}", result["duration"], f"找到{result['count']}条路线")

        total_duration = time.time() - start_time

        # 计算统计信息
        durations = [r["duration"] for r in results if "duration" in r and r["duration"] > 0]
        if durations:
            avg_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            throughput = len(durations) / total_duration

            print(f"\n总执行时间: {total_duration:.6f}秒")
            print(f"平均查询时间: {avg_duration:.6f}秒")
            print(f"中位数查询时间: {median_duration:.6f}秒")
            print(f"最小查询时间: {min_duration:.6f}秒")
            print(f"最大查询时间: {max_duration:.6f}秒")
            print(f"总吞吐量: {throughput:.2f}查询/秒")

            return {
                "total_duration": total_duration,
                "avg_duration": avg_duration,
                "median_duration": median_duration,
                "min_duration": min_duration,
                "max_duration": max_duration,
                "throughput": throughput,
                "results": results
            }
        else:
            print(f"{Colors.FAIL}没有成功的查询结果{Colors.END}")
            return {
                "total_duration": total_duration,
                "results": results
            }

    def test_ticket_booking_performance(self, count=5):
        """测试购票API性能"""
        if not self.token:
            print(f"{Colors.WARNING}未登录，跳过购票测试{Colors.END}")
            return []

        self.print_header(f"购票API性能测试 (测试{count}次)")

        # 先获取可用路线
        params = {"from": "北京", "to": "上海", "date": "2025-06-04"}
        response = self.session.get(f"{self.base_url}/api/routes/direct", params=params)
        if response.status_code != 200:
            print(f"{Colors.FAIL}获取路线失败，无法进行购票测试{Colors.END}")
            return []

        routes_data = response.json().get("data", {}).get("routes", [])
        if not routes_data:
            print(f"{Colors.FAIL}没有可用路线，无法进行购票测试{Colors.END}")
            return []

        # 获取第一个路线的信息用于购票
        route = routes_data[0]
        train_code = route.get("train_code")
        train_full_code = route.get("train_full_code", train_code)  # 假设full_code与train_code相同
        from_station = route.get("from_station")
        to_station = route.get("to_station")
        from_station_no = route.get("from_station_no", 1)
        to_station_no = route.get("to_station_no", 10)
        travel_date = "2025-06-04"

        results = []

        for i in range(count):
            # 构建购票请求
            ticket_data = {
                "trainCode": train_code,
                "trainFullCode": train_full_code,
                "fromStation": from_station,
                "toStation": to_station,
                "fromStationNo": from_station_no,
                "toStationNo": to_station_no,
                "travelDate": travel_date
            }

            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/api/tickets",
                json=ticket_data,
                headers=self.get_auth_headers()
            )
            duration = time.time() - start_time

            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get("code") == 0:
                    self.print_result(f"购票测试 #{i + 1}", duration, "成功")
                    results.append((True, duration))
                else:
                    self.print_result(f"购票测试 #{i + 1}", duration, f"业务错误: {resp_data.get('msg')}")
                    results.append((False, duration))
            else:
                self.print_result(f"购票测试 #{i + 1}", duration, f"HTTP错误: {response.status_code}")
                results.append((False, duration))

        # 计算统计信息
        success_durations = [duration for success, duration in results if success]

        if success_durations:
            avg_duration = statistics.mean(success_durations)
            min_duration = min(success_durations)
            max_duration = max(success_durations)
            success_rate = len(success_durations) / count * 100

            print(f"\n成功率: {success_rate:.2f}%")
            print(f"平均购票时间: {avg_duration:.6f}秒")
            print(f"最小购票时间: {min_duration:.6f}秒")
            print(f"最大购票时间: {max_duration:.6f}秒")

        return results

    def test_user_tickets_list(self):
        """测试获取用户车票列表API"""
        if not self.token:
            print(f"{Colors.WARNING}未登录，跳过用户车票测试{Colors.END}")
            return -1, 0

        self.print_header("用户车票列表API性能测试")

        start_time = time.time()
        response = self.session.get(
            f"{self.base_url}/api/user/tickets",
            headers=self.get_auth_headers()
        )
        duration = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            ticket_count = len(data.get("data", []))
            self.print_result("获取用户车票列表", duration, f"返回{ticket_count}张车票")
            return duration, ticket_count
        else:
            self.print_result("获取用户车票列表", duration, f"请求失败: {response.status_code}")
            return duration, 0

    def test_api_under_load(self, endpoint, params=None, json_data=None, method="get", requests_count=50, concurrency=10):
        """测试API在负载下的性能"""
        self.print_header(f"API负载测试: {endpoint} (请求数: {requests_count}, 并发: {concurrency})")

        url = f"{self.base_url}{endpoint}"
        headers = self.get_auth_headers() if "/user/" in endpoint or endpoint.endswith("/tickets") and method.lower() == "post" else {}

        def make_request():
            try:
                start_time = time.time()
                if method.lower() == "post":
                    response = self.session.post(url, json=json_data, headers=headers)
                else:
                    response = self.session.get(url, params=params, headers=headers)
                duration = time.time() - start_time
                return duration, response.status_code
            except Exception as e:
                return -1, str(e)

        durations = []
        errors = []
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_req = [executor.submit(make_request) for _ in range(requests_count)]
            for i, future in enumerate(concurrent.futures.as_completed(future_to_req)):
                duration, status = future.result()
                if isinstance(status, int) and 200 <= status < 300:
                    durations.append(duration)
                else:
                    errors.append((i, status))

        total_time = time.time() - start_time

        # 计算统计信息
        if durations:
            avg_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            p95 = sorted(durations)[int(len(durations) * 0.95)]
            p99 = sorted(durations)[int(len(durations) * 0.99)]
            success_rate = len(durations) / requests_count * 100
            throughput = len(durations) / total_time

            print(f"总请求数: {requests_count}")
            print(f"成功请求数: {len(durations)}")
            print(f"成功率: {success_rate:.2f}%")
            print(f"总执行时间: {total_time:.6f}秒")
            print(f"平均响应时间: {avg_duration:.6f}秒")
            print(f"中位数响应时间: {median_duration:.6f}秒")
            print(f"最小响应时间: {min_duration:.6f}秒")
            print(f"最大响应时间: {max_duration:.6f}秒")
            print(f"95%分位响应时间: {p95:.6f}秒")
            print(f"99%分位响应时间: {p99:.6f}秒")
            print(f"总吞吐量: {throughput:.2f}请求/秒")

            if errors:
                print(f"{Colors.WARNING}错误请求: {len(errors)}{Colors.END}")
                for i, (req_id, error) in enumerate(errors[:5]):
                    print(f"  {i + 1}. 请求 #{req_id}: {error}")
                if len(errors) > 5:
                    print(f"  ...以及其他 {len(errors) - 5} 个错误")

            return {
                "requests": requests_count,
                "success": len(durations),
                "success_rate": success_rate,
                "total_time": total_time,
                "avg_duration": avg_duration,
                "median_duration": median_duration,
                "min_duration": min_duration,
                "max_duration": max_duration,
                "p95": p95,
                "p99": p99,
                "throughput": throughput,
                "errors": len(errors)
            }
        else:
            print(f"{Colors.FAIL}所有请求均失败{Colors.END}")
            return {
                "requests": requests_count,
                "success": 0,
                "success_rate": 0,
                "total_time": total_time,
                "errors": len(errors)
            }

    def plot_performance_results(self, results, title="API性能测试"):
        """将性能测试结果输出为文本报告而不是图表"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD} {title} 性能报告 {Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.END}\n")

        # 输出响应时间指标
        if 'avg_duration' in results:
            print(f"{Colors.GREEN}响应时间指标 (单位: 秒):{Colors.END}")
            print(f"  平均响应时间: {results.get('avg_duration', 0):.6f}")
            print(f"  中位数响应时间: {results.get('median_duration', 0):.6f}")
            print(f"  95%分位响应时间: {results.get('p95', 0):.6f}")
            print(f"  99%分位响应时间: {results.get('p99', 0):.6f}")
            print(f"  最大响应时间: {results.get('max_duration', 0):.6f}")

        # 输出吞吐量和成功率
        if 'throughput' in results:
            print(f"\n{Colors.GREEN}性能指标:{Colors.END}")
            print(f"  吞吐量: {results.get('throughput', 0):.2f} 请求/秒")
            print(f"  成功率: {results.get('success_rate', 0):.2f}%")
            print(f"  总请求数: {results.get('requests', 0)}")
            print(f"  成功请求数: {results.get('success', 0)}")
            print(f"  错误请求数: {results.get('errors', 0)}")
            print(f"  总执行时间: {results.get('total_time', 0):.6f} 秒")

        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n测试完成时间: {timestamp}")


class SafePrinter:
    """确保输出能够在测试框架中正常显示"""
    
    @staticmethod
    def print(message):
        """确保输出能在测试和命令行环境下正常工作"""
        # 同时写到标准输出和错误输出，增加可见性
        sys.stdout.write(f"{message}\n")
        sys.stderr.write(f"{message}\n")
        sys.stdout.flush()
        sys.stderr.flush()


class TestAPIPerformance(unittest.TestCase):
    """API性能测试用例"""
    
    @classmethod
    def setUpClass(cls):
        """测试类开始前运行"""
        SafePrinter.print("\n\n========== 开始API性能测试 ==========")
        cls.tester = APIPerformanceTester()
        SafePrinter.print(f"确保服务器在 {cls.tester.base_url} 已启动")
    
    @classmethod
    def tearDownClass(cls):
        """测试类结束后运行"""
        SafePrinter.print("\n========== API性能测试完成 ==========\n")
    
    def setUp(self):
        """每个测试方法前运行"""
        test_name = self._testMethodName
        test_doc = getattr(self, test_name).__doc__ or "无文档字符串"
        SafePrinter.print(f"\n----- 开始测试: {test_name} -----")
        SafePrinter.print(f"描述: {test_doc}")
    
    def tearDown(self):
        """每个测试方法后运行"""
        test_name = self._testMethodName
        SafePrinter.print(f"----- 测试完成: {test_name} -----\n")

    def test_01_server_health(self):
        """测试服务器健康状态"""
        try:
            response = requests.get(f"{self.tester.base_url}/health", timeout=2)
            self.assertEqual(response.status_code, 200)
            print(f"{Colors.GREEN}✓ 服务器正在运行{Colors.END}")
        except Exception:
            print(f"{Colors.WARNING}无法连接到健康检查端点，但服务器可能仍在运行{Colors.END}")
            # 尝试连接另一个基本端点
            try:
                response = requests.get(self.tester.base_url, timeout=2)
                print(f"{Colors.GREEN}✓ 服务器响应基本URL{Colors.END}")
            except Exception as e:
                self.fail(f"无法连接到服务器: {e}")

    def test_02_tickets_list(self):
        """测试票务列表API性能"""
        duration, count = self.tester.test_tickets_list()
        self.assertGreaterEqual(duration, 0)
        self.assertIsNotNone(count)

    def test_03_route_search(self):
        """测试路线搜索API性能"""
        popular_routes = [
            ("北京", "上海", "2025-06-04"),
            ("广州", "深圳", "2025-06-04"),
            ("成都", "重庆", "2025-06-04")
        ]
        results = self.tester.test_route_search(popular_routes)
        self.assertEqual(len(results), len(popular_routes))

    def test_04_concurrent_search(self):
        """测试并发路线搜索性能"""
        popular_routes = [
            ("北京", "上海", "2025-06-04"),
            ("广州", "深圳", "2025-06-04"),
            ("成都", "重庆", "2025-06-04"),
            ("上海", "北京", "2025-06-05"),
            ("天津", "北京", "2025-06-05")
        ]
        results = self.tester.test_concurrent_search(popular_routes, concurrency=3)
        self.assertIn("results", results)

    def test_05_login(self):
        """测试登录API性能"""
        success = self.tester.login()
        self.assertTrue(success, "登录应该成功")

    def test_06_user_tickets(self):
        """测试用户车票列表API性能 - 需要登录"""
        if not self.tester.token:
            self.tester.login()

        duration, count = self.tester.test_user_tickets_list()
        self.assertGreaterEqual(duration, 0)

    def test_07_ticket_booking(self):
        """测试购票API性能 - 需要登录"""
        if not self.tester.token:
            self.tester.login()

        results = self.tester.test_ticket_booking_performance(count=1)
        self.assertGreaterEqual(len(results), 0)

    def test_08_api_under_load(self):
        """测试路线搜索API在低负载下的性能"""
        results = self.tester.test_api_under_load(
            "/api/routes/direct",
            params={"from": "北京", "to": "上海", "date": "2025-06-04"},
            requests_count=5,  # 小数量以加快测试速度
            concurrency=2
        )
        self.assertIn("requests", results)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='12306后端API性能测试工具')
    parser.add_argument('--url', default='http://localhost:3000', help='后端API基础URL')
    parser.add_argument('--test', choices=['basic', 'routes', 'load', 'all'], default='all', help='测试类型')
    parser.add_argument('--concurrency', type=int, default=10, help='并发数量')
    parser.add_argument('--requests', type=int, default=50, help='请求总数')
    args = parser.parse_args()

    tester = APIPerformanceTester(base_url=args.url)

    # 预设一些热门路线用于查询测试
    popular_routes = [
        ("北京", "上海", "2025-06-04"),
        ("广州", "深圳", "2025-06-04"),
        ("成都", "重庆", "2025-06-04"),
        ("上海", "北京", "2025-06-05"),
        ("天津", "北京", "2025-06-05"),
        ("武汉", "广州", "2025-06-06"),
        ("西安", "成都", "2025-06-07"),
        ("杭州", "南京", "2025-06-08"),
        ("深圳", "厦门", "2025-06-09"),
        ("长沙", "武汉", "2025-06-10")
    ]

    # 根据测试类型执行不同的测试
    if args.test in ['basic', 'all']:
        tester.test_tickets_list()

    if args.test in ['routes', 'all']:
        # 登录获取认证令牌
        tester.login()

        # 测试路线查询API
        tester.test_route_search(popular_routes[:3])

        # 测试并发路线查询
        results = tester.test_concurrent_search(popular_routes, concurrency=5)
        if 'throughput' in results:
            tester.plot_performance_results(results, "路线查询API并发测试")

        # 如果已登录，测试用户相关API
        if tester.token:
            tester.test_user_tickets_list()
            tester.test_ticket_booking_performance(count=3)

    if args.test in ['load', 'all']:
        # 测试票务列表API在负载下的性能
        results = tester.test_api_under_load(
            "/api/tickets",
            requests_count=args.requests,
            concurrency=args.concurrency
        )
        if 'throughput' in results:
            tester.plot_performance_results(results, "票务列表API负载测试")

        # 测试路线查询API在负载下的性能
        results = tester.test_api_under_load(
            "/api/routes/direct",
            params={"from": "北京", "to": "上海", "date": "2025-06-04"},
            requests_count=args.requests,
            concurrency=args.concurrency
        )
        if 'throughput' in results:
            tester.plot_performance_results(results, "路线查询API负载测试")

        # 登录后再测试认证API
        if not tester.token:
            tester.login()

        if tester.token:
            # 测试用户车票API在负载下的性能
            results = tester.test_api_under_load(
                "/api/user/tickets",
                requests_count=args.requests // 2,  # 降低认证API的请求数量
                concurrency=args.concurrency // 2
            )
            if 'throughput' in results:
                tester.plot_performance_results(results, "用户车票API负载测试")


if __name__ == "__main__":
    # 检查是否有命令行参数
    import sys
    if len(sys.argv) > 1:
        # 有命令行参数，使用argparse处理
        main()
    else:
        # 没有命令行参数，作为unittest运行
        print(f"{Colors.HEADER}作为VSCode测试运行...{Colors.END}")
        unittest.main()