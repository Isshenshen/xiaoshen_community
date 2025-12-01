#!/usr/bin/env python3
"""
独角发卡前端页面测试脚本

测试所有前端页面功能和API接口连接，包括：
- 页面加载测试
- 路由导航测试
- API调用测试
- 权限控制测试
- 数据展示测试

作者: AI Assistant
日期: 2025年11月30日
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class PageTestResult:
    """页面测试结果数据类"""
    page_name: str
    page_url: str
    status_code: int
    load_time: float
    api_calls: List[Dict] = None
    has_errors: bool = False
    error_message: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if self.api_calls is None:
            self.api_calls = []


@dataclass
class ApiTestResult:
    """API测试结果数据类"""
    api_name: str
    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    request_data: Optional[Dict] = None
    response_data: Optional[Any] = None


class FrontendTester:
    """前端测试器类"""

    def __init__(self, frontend_url: str = "http://localhost:3000", backend_url: str = "http://localhost:8000"):
        self.frontend_url = frontend_url.rstrip('/')
        self.backend_url = backend_url.rstrip('/')
        self.session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Frontend-Test-Script/1.0'
        })

        # 测试结果存储
        self.page_results: List[PageTestResult] = []
        self.api_results: List[ApiTestResult] = []

        # 认证token
        self.admin_token = None
        self.user_token = None

    def set_auth_header(self, token: Optional[str] = None):
        """设置或清除认证头"""
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
        else:
            self.session.headers.pop('Authorization', None)

    def make_api_request(self, method: str, endpoint: str, **kwargs) -> ApiTestResult:
        """发送API请求并记录结果"""
        url = f"{self.backend_url}{endpoint}"
        start_time = time.time()

        # 处理请求体
        if 'json' in kwargs and kwargs['json'] is not None:
            request_data = kwargs['json']
        elif 'data' in kwargs and kwargs['data'] is not None:
            request_data = kwargs['data']
        else:
            request_data = None

        try:
            response = self.session.request(method.upper(), url, **kwargs)
            response_time = time.time() - start_time

            # 尝试解析响应
            try:
                response_data = response.json()
            except:
                response_data = response.text

            result = ApiTestResult(
                api_name=endpoint.split('/')[2] if len(endpoint.split('/')) > 2 else 'unknown',
                endpoint=endpoint,
                method=method.upper(),
                status_code=response.status_code,
                response_time=round(response_time, 3),
                success=response.status_code < 400,
                request_data=request_data,
                response_data=response_data
            )

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            result = ApiTestResult(
                api_name=endpoint.split('/')[2] if len(endpoint.split('/')) > 2 else 'unknown',
                endpoint=endpoint,
                method=method.upper(),
                status_code=0,
                response_time=round(response_time, 3),
                success=False,
                error_message=str(e),
                request_data=request_data
            )

        self.api_results.append(result)
        return result

    def test_page_load(self, page_name: str, page_path: str, expected_apis: List[str] = None) -> PageTestResult:
        """测试页面加载"""
        url = f"{self.frontend_url}{page_path}"
        start_time = time.time()

        try:
            response = self.session.get(url, timeout=10)
            load_time = time.time() - start_time

            result = PageTestResult(
                page_name=page_name,
                page_url=url,
                status_code=response.status_code,
                load_time=round(load_time, 3),
                has_errors=response.status_code != 200
            )

            if response.status_code != 200:
                result.error_message = f"HTTP {response.status_code}"
            else:
                # 检查页面内容是否包含预期元素
                content = response.text.lower()
                if 'error' in content and 'exception' in content:
                    result.has_errors = True
                    result.error_message = "页面包含错误信息"
                elif len(content) < 1000:
                    result.notes = "页面内容过少，可能未正确加载"

        except requests.exceptions.RequestException as e:
            load_time = time.time() - start_time
            result = PageTestResult(
                page_name=page_name,
                page_url=url,
                status_code=0,
                load_time=round(load_time, 3),
                has_errors=True,
                error_message=str(e)
            )

        # 测试相关API
        if expected_apis:
            for api_endpoint in expected_apis:
                api_result = self.make_api_request('GET', api_endpoint)
                result.api_calls.append({
                    'endpoint': api_endpoint,
                    'method': 'GET',
                    'status_code': api_result.status_code,
                    'success': api_result.success
                })

        self.page_results.append(result)
        return result

    def authenticate_admin(self) -> bool:
        """管理员认证"""
        result = self.make_api_request('POST', '/api/v1/auth/login',
                                     data={'username': 'admin', 'password': 'admin123'})

        if result.success and isinstance(result.response_data, dict):
            token = result.response_data.get('access_token')
            if token:
                self.admin_token = token
                return True
        return False

    def authenticate_user(self) -> bool:
        """普通用户认证"""
        username = 'testuser_normal'
        password = 'test123'

        def try_login() -> bool:
            login_result = self.make_api_request('POST', '/api/v1/auth/login',
                                              data={'username': username, 'password': password})
            if login_result.success and isinstance(login_result.response_data, dict):
                token = login_result.response_data.get('access_token')
                if token:
                    self.user_token = token
                    return True
            return False

        if try_login():
            return True

        register_result = self.make_api_request('POST', '/api/v1/auth/register', json={
            'username': username,
            'email': f'{username}@example.com',
            'password': password,
            'full_name': 'Test User Normal'
        })

        if register_result.success or (
            register_result.status_code == 400 and
            ('already exists' in str(register_result.response_data) or
             '用户名' in str(register_result.response_data) or
             '邮箱' in str(register_result.response_data))
        ):
            return try_login()

        return False

    def test_public_pages(self):
        """测试公开页面"""
        print("\n🌐 测试公开页面...")
        self.set_auth_header(None)

        # 首页
        result = self.test_page_load("首页", "/", [])
        print(f"   🏠 首页: {result.status_code}, 加载时间: {result.load_time}s")
        if result.has_errors:
            print(f"      ❌ 错误: {result.error_message}")

        # 关于页面
        result = self.test_page_load("关于页面", "/about", [])
        print(f"   📄 关于页面: {result.status_code}, 加载时间: {result.load_time}s")
        if result.has_errors:
            print(f"      ❌ 错误: {result.error_message}")

        # 商品列表页
        result = self.test_page_load("商品列表", "/products", ["/api/v1/products/", "/api/v1/products/categories"])
        print(f"   📦 商品列表: {result.status_code}, 加载时间: {result.load_time}s")
        if result.has_errors:
            print(f"      ❌ 错误: {result.error_message}")

        # 登录页面
        result = self.test_page_load("登录页面", "/login", [])
        print(f"   🔑 登录页面: {result.status_code}, 加载时间: {result.load_time}s")
        if result.has_errors:
            print(f"      ❌ 错误: {result.error_message}")

        # 注册页面
        result = self.test_page_load("注册页面", "/register", [])
        print(f"   📝 注册页面: {result.status_code}, 加载时间: {result.load_time}s")
        if result.has_errors:
            print(f"      ❌ 错误: {result.error_message}")

    def test_user_pages(self):
        """测试用户页面"""
        print("\n👤 测试用户页面...")

        # 认证为普通用户
        if self.authenticate_user():
            print("   ✅ 用户认证成功")
            previous_header = self.session.headers.get('Authorization')
            self.set_auth_header(self.user_token)
            try:
                # 个人资料页
                result = self.test_page_load("个人资料", "/profile", ["/api/v1/users/me"])
                print(f"   👤 个人资料: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")

                # 购物车页面
                result = self.test_page_load("购物车", "/cart", [])
                print(f"   🛒 购物车: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")

                # 订单列表页
                result = self.test_page_load("订单列表", "/orders", ["/api/v1/orders/"])
                print(f"   📋 订单列表: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")

                # 充值页面
                result = self.test_page_load("充值页面", "/recharge", ["/api/v1/users/balance"])
                print(f"   💰 充值页面: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")
            finally:
                if previous_header:
                    self.session.headers['Authorization'] = previous_header
                else:
                    self.set_auth_header(None)
        else:
            print("   ❌ 用户认证失败，跳过用户页面测试")

    def test_admin_pages(self):
        """测试管理员页面"""
        print("\n👑 测试管理员页面...")

        # 认证为管理员
        if self.authenticate_admin():
            print("   ✅ 管理员认证成功")
            previous_header = self.session.headers.get('Authorization')
            self.set_auth_header(self.admin_token)
            try:
                # 管理员仪表盘
                result = self.test_page_load("管理员仪表盘", "/admin/dashboard",
                                           ["/api/v1/admin/dashboard/stats", "/api/v1/admin/dashboard/charts"])
                print(f"   📊 仪表盘: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")

                # 用户管理页面
                result = self.test_page_load("用户管理", "/admin/users", ["/api/v1/users/"])
                print(f"   👥 用户管理: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")

                # 商品管理页面
                result = self.test_page_load("商品管理", "/admin/products",
                                           ["/api/v1/products/", "/api/v1/products/categories"])
                print(f"   📦 商品管理: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")

                # 订单管理页面
                result = self.test_page_load("订单管理", "/admin/orders", ["/api/v1/orders/"])
                print(f"   📋 订单管理: {result.status_code}, 加载时间: {result.load_time}s")
                if result.has_errors:
                    print(f"      ❌ 错误: {result.error_message}")
            finally:
                if previous_header:
                    self.session.headers['Authorization'] = previous_header
                else:
                    self.set_auth_header(None)
        else:
            print("   ❌ 管理员认证失败，跳过管理员页面测试")

    def test_api_endpoints(self):
        """测试关键API端点"""
        print("\n🔗 测试API端点...")

        if not self.admin_token:
            self.authenticate_admin()
        if not self.user_token:
            self.authenticate_user()

        original_header = self.session.headers.get('Authorization')

        # 基础API测试
        apis_to_test = [
            ("健康检查", "GET", "/health", None),
            ("API文档", "GET", "/api/v1/openapi.json", None),
            ("商品分类", "GET", "/api/v1/products/categories", None),
            ("商品列表", "GET", "/api/v1/products/", None),
            ("用户列表(管理员)", "GET", "/api/v1/users/", "admin"),
            ("订单列表(管理员)", "GET", "/api/v1/orders/", "admin"),
            ("支付记录(管理员)", "GET", "/api/v1/payments/", "admin"),
            ("仪表盘统计", "GET", "/api/v1/admin/dashboard/stats", "admin"),
        ]

        for api_name, method, endpoint, auth_required in apis_to_test:
            if auth_required == 'admin' and self.admin_token:
                self.set_auth_header(self.admin_token)
            elif auth_required == 'user' and self.user_token:
                self.set_auth_header(self.user_token)
            else:
                self.set_auth_header(None)

            result = self.make_api_request(method, endpoint)
            status = "✅" if result.success else "❌"
            print(f"   {status} {api_name}: {result.status_code} ({result.response_time}s)")
            if not result.success and result.status_code not in [401, 403]:  # 忽略认证错误
                print(f"      错误: {result.error_message}")

        if original_header:
            self.session.headers['Authorization'] = original_header
        else:
            self.set_auth_header(None)

    def generate_report(self) -> str:
        """生成测试报告"""
        total_pages = len(self.page_results)
        successful_pages = len([r for r in self.page_results if not r.has_errors])
        failed_pages = total_pages - successful_pages

        total_apis = len(self.api_results)
        successful_apis = len([r for r in self.api_results if r.success])
        failed_apis = total_apis - successful_apis

        # 生成报告
        report = []
        report.append("# 🌐 独角发卡前端页面测试报告")
        report.append("")
        report.append(f"**测试时间:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**前端服务:** {self.frontend_url}")
        report.append(f"**后端服务:** {self.backend_url}")
        report.append("")

        # 总体统计
        report.append("## 📊 测试概览")
        report.append("")
        report.append("### 页面测试统计")
        report.append(f"- **总页面数:** {total_pages}")
        report.append(f"- **成功页面:** {successful_pages}")
        report.append(f"- **失败页面:** {failed_pages}")
        report.append(f"- **页面成功率:** {(successful_pages/total_pages*100):.1f}%")
        report.append("")

        report.append("### API测试统计")
        report.append(f"- **总API数:** {total_apis}")
        report.append(f"- **成功API:** {successful_apis}")
        report.append(f"- **失败API:** {failed_apis}")
        report.append(f"- **API成功率:** {(successful_apis/total_apis*100):.1f}%")
        report.append("")

        # 页面测试详情
        report.append("## 📄 页面测试结果")
        report.append("")
        for result in self.page_results:
            status_icon = "✅" if not result.has_errors else "❌"
            report.append(f"### {status_icon} {result.page_name}")
            report.append(f"- **URL:** {result.page_url}")
            report.append(f"- **状态码:** {result.status_code}")
            report.append(f"- **加载时间:** {result.load_time}s")

            if result.api_calls:
                report.append("- **API调用:**")
                for api_call in result.api_calls:
                    api_status = "✅" if api_call['success'] else "❌"
                    report.append(f"  - {api_status} {api_call['method']} {api_call['endpoint']} ({api_call['status_code']})")

            if result.has_errors:
                report.append(f"- **错误:** {result.error_message}")

            if result.notes:
                report.append(f"- **备注:** {result.notes}")

            report.append("")

        # API测试详情
        report.append("## 🔗 API测试结果")
        report.append("")
        for result in self.api_results:
            status_icon = "✅" if result.success else "❌"
            report.append(f"### {status_icon} {result.api_name.upper()}")
            report.append(f"- **端点:** {result.method} {result.endpoint}")
            report.append(f"- **状态码:** {result.status_code}")
            report.append(f"- **响应时间:** {result.response_time}s")

            if not result.success:
                if result.error_message:
                    report.append(f"- **错误信息:** {result.error_message}")
                if result.request_data:
                    report.append(f"- **请求数据:** {json.dumps(result.request_data, ensure_ascii=False, indent=2)}")

            report.append("")

        # 问题总结
        failed_pages_list = [r for r in self.page_results if r.has_errors]
        failed_apis_list = [r for r in self.api_results if not r.success and r.status_code not in [401, 403]]

        if failed_pages_list or failed_apis_list:
            report.append("## ❌ 发现的问题")
            report.append("")

            if failed_pages_list:
                report.append("### 页面问题")
                for result in failed_pages_list:
                    report.append(f"- **{result.page_name}**: {result.error_message}")

            if failed_apis_list:
                report.append("### API问题")
                for result in failed_apis_list:
                    report.append(f"- **{result.method} {result.endpoint}**: {result.error_message or f'HTTP {result.status_code}'}")

            report.append("")

        # 结论
        report.append("## 📝 测试结论")
        report.append("")

        if successful_pages / total_pages > 0.8 and successful_apis / total_apis > 0.8:
            report.append("✅ **测试通过** - 前后端集成正常，核心功能工作良好")
        elif successful_pages / total_pages > 0.6 and successful_apis / total_apis > 0.6:
            report.append("⚠️ **基本通过** - 存在一些问题，但不影响核心功能")
        else:
            report.append("❌ **测试失败** - 存在严重问题，需要修复")

        report.append("")
        report.append("### 性能指标")
        avg_page_load = sum(r.load_time for r in self.page_results) / len(self.page_results) if self.page_results else 0
        avg_api_response = sum(r.response_time for r in self.api_results) / len(self.api_results) if self.api_results else 0

        report.append(f"- **平均页面加载时间:** {avg_page_load:.3f}s")
        report.append(f"- **平均API响应时间:** {avg_api_response:.3f}s")
        report.append("")

        return "\n".join(report)

    def run_all_tests(self):
        """运行所有前端测试"""
        print("🚀 开始前端页面测试...")
        print("=" * 50)

        # 测试服务连接
        print("🔗 测试服务连接...")
        self.test_api_endpoints()

        # 测试页面
        self.test_public_pages()
        self.test_user_pages()
        self.test_admin_pages()

        print("=" * 50)
        print("✅ 前端测试完成！")

        # 生成报告
        report = self.generate_report()

        # 显示关键统计信息
        total_pages = len(self.page_results)
        successful_pages = len([r for r in self.page_results if not r.has_errors])
        total_apis = len(self.api_results)
        successful_apis = len([r for r in self.api_results if r.success])

        print("\n" + "=" * 50)
        print("📋 测试报告预览:")
        print("=" * 50)
        print(f"页面测试: {successful_pages}/{total_pages} ({successful_pages/total_pages*100:.1f}%)")
        print(f"API测试: {successful_apis}/{total_apis} ({successful_apis/total_apis*100:.1f}%)")

        # 保存详细报告
        with open('frontend_test_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 详细报告已保存到: frontend_test_report.md")

        return report


def main():
    """主函数"""
    print("独角发卡前端页面测试工具")
    print("=" * 40)

    # 创建测试器
    tester = FrontendTester()

    # 运行所有测试
    report = tester.run_all_tests()

    return tester.page_results, tester.api_results


if __name__ == "__main__":
    page_results, api_results = main()
