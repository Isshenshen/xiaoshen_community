#!/usr/bin/env python3
"""
独角发卡 FastAPI - 完整API测试脚本

测试所有API接口，包括认证、用户管理、商品管理、订单管理、支付管理、后台管理等模块。
自动识别问题接口并生成测试报告。

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
class TestResult:
    """测试结果数据类"""
    api_name: str
    endpoint: str
    method: str
    status_code: int
    success: bool
    error_message: Optional[str] = None
    response_time: float = 0.0
    request_data: Optional[Dict] = None
    response_data: Optional[Any] = None


class APITester:
    """API测试器类"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
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
            'Content-Type': 'application/json',
            'User-Agent': 'API-Test-Script/1.0'
        })

        # 测试数据存储
        self.test_users = []
        self.test_products = []
        self.test_orders = []
        self.tokens = {}

        # 测试结果
        self.results: List[TestResult] = []

    def make_request(self, method: str, endpoint: str, **kwargs) -> TestResult:
        """发送HTTP请求并记录结果"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            # 处理请求体和Content-Type
            if 'json' in kwargs and kwargs['json'] is not None:
                request_data = kwargs['json']
                # 对于JSON请求，确保Content-Type正确
                kwargs.setdefault('headers', {})
                kwargs['headers']['Content-Type'] = 'application/json'
            elif 'data' in kwargs and kwargs['data'] is not None:
                request_data = kwargs['data']
                # 对于表单数据，使用表单Content-Type
                kwargs.setdefault('headers', {})
                kwargs['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
            else:
                request_data = None

            response = self.session.request(method.upper(), url, **kwargs)
            response_time = time.time() - start_time

            # 尝试解析响应
            try:
                response_data = response.json()
            except:
                response_data = response.text

            result = TestResult(
                api_name=endpoint.split('/')[1] if len(endpoint.split('/')) > 1 else 'root',
                endpoint=endpoint,
                method=method.upper(),
                status_code=response.status_code,
                success=response.status_code < 400,
                response_time=round(response_time, 3),
                request_data=request_data,
                response_data=response_data
            )

        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            result = TestResult(
                api_name=endpoint.split('/')[1] if len(endpoint.split('/')) > 1 else 'root',
                endpoint=endpoint,
                method=method.upper(),
                status_code=0,
                success=False,
                error_message=str(e),
                response_time=round(response_time, 3),
                request_data=request_data if 'request_data' in locals() else None
            )

        self.results.append(result)
        return result

    def login_user(self, username: str, password: str) -> Optional[str]:
        """用户登录获取token"""
        result = self.make_request('POST', '/api/v1/auth/login',
                                 data={'username': username, 'password': password})

        if result.success and isinstance(result.response_data, dict):
            token = result.response_data.get('access_token')
            if token:
                self.session.headers['Authorization'] = f'Bearer {token}'
                return token
        return None

    def switch_to_admin(self):
        """切换到管理员账户"""
        # 使用默认管理员账户
        admin_token = self.login_user('admin', 'admin123')
        if admin_token:
            self.tokens['admin'] = admin_token
            return True

        # 如果默认管理员不存在，尝试创建
        register_result = self.make_request('POST', '/api/v1/auth/register', json={
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin123',
            'full_name': 'Administrator',
            'is_superuser': True
        })

        if register_result.success:
            admin_token = self.login_user('admin', 'admin123')
            if admin_token:
                self.tokens['admin'] = admin_token
                return True

        return False

    def switch_to_user(self, username: str = 'testuser_normal', password: str = 'test123'):
        """切换到普通用户账户"""
        # 尝试多种密码（因为可能在其他测试中被修改过）
        possible_passwords = [password, 'newpass123', 'newtest456']

        for pwd in possible_passwords:
            user_token = self.login_user(username, pwd)
            if user_token:
                self.tokens['user'] = user_token
                return True

        # 如果登录失败，创建用户
        register_result = self.make_request('POST', '/api/v1/auth/register', json={
            'username': username,
            'email': f'{username}@example.com',
            'password': password,
            'full_name': f'Test User {username}'
        })

        # 如果注册成功或用户已存在，尝试登录
        if register_result.success or (register_result.status_code == 400 and
                                      ('already exists' in str(register_result.response_data) or
                                       '用户名' in str(register_result.response_data) or
                                       '邮箱' in str(register_result.response_data))):
            user_token = self.login_user(username, password)
            if user_token:
                self.tokens['user'] = user_token
                return True

        return False

    def set_auth_token(self, token_type: str = 'user'):
        """设置认证token"""
        token = self.tokens.get(token_type)
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
        else:
            self.session.headers.pop('Authorization', None)

    def test_health_check(self):
        """测试健康检查接口"""
        print("🔍 测试健康检查接口...")
        result = self.make_request('GET', '/health')
        print(f"   状态码: {result.status_code}, 成功: {result.success}")
        return result

    def test_auth_apis(self):
        """测试认证相关API"""
        print("\n🔐 测试认证API...")

        # 清除认证头
        self.session.headers.pop('Authorization', None)

        # 使用唯一的测试用户名
        test_username = 'testuser_auth'
        test_password = 'test123456'
        test_email = 'testuser_auth@example.com'

        # 1. 用户注册（先尝试删除已存在的用户）
        print("   📝 测试用户注册...")
        result = self.make_request('POST', '/api/v1/auth/register', json={
            'username': test_username,
            'email': test_email,
            'password': test_password,
            'full_name': 'Auth Test User'
        })
        # 如果用户已存在（400错误），这是可以接受的
        success = result.success or (result.status_code == 400 and
                                    ('already exists' in str(result.response_data) or
                                     '用户名' in str(result.response_data) or
                                     '邮箱' in str(result.response_data)))
        print(f"      状态码: {result.status_code}, 成功: {success}")

        # 2. 用户登录
        print("   🔑 测试用户登录...")
        result = self.make_request('POST', '/api/v1/auth/login',
                                 data={'username': test_username, 'password': test_password})
        auth_token = None
        if result.success and isinstance(result.response_data, dict):
            auth_token = result.response_data.get('access_token')
            if auth_token:
                self.tokens['auth_test_user'] = auth_token
        print(f"      状态码: {result.status_code}, 成功: {result.success}")

        # 3. 获取用户信息（需要认证）
        if auth_token:
            self.set_auth_token('auth_test_user')
            print("   👤 测试获取用户信息...")
            result = self.make_request('GET', '/api/v1/auth/me')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 4. 更新用户信息
            print("   ✏️ 测试更新用户信息...")
            result = self.make_request('PUT', '/api/v1/auth/me', json={
                'full_name': 'Updated Auth Test User',
                'phone': '13800138000'
            })
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 5. 修改密码
            print("   🔒 测试修改密码...")
            result = self.make_request('POST', '/api/v1/auth/change-password', params={
                'old_password': test_password,
                'new_password': 'newtest456'
            })
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 更新密码以便后续测试
            test_password = 'newtest456'

    def test_user_apis(self):
        """测试用户管理API"""
        print("\n👥 测试用户管理API...")

        # 切换到普通用户
        if self.switch_to_user():
            # 1. 获取当前用户信息
            print("   👤 测试获取当前用户信息...")
            result = self.make_request('GET', '/api/v1/users/me')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 2. 更新当前用户信息
            print("   ✏️ 测试更新当前用户信息...")
            result = self.make_request('PUT', '/api/v1/users/me', json={
                'full_name': 'Updated User',
                'phone': '13900139000'
            })
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 3. 获取用户余额
            print("   💰 测试获取用户余额...")
            result = self.make_request('GET', '/api/v1/users/balance')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 4. 充值余额
            print("   💳 测试充值余额...")
            result = self.make_request('POST', '/api/v1/users/recharge?amount=100.0')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 5. 修改密码
            print("   🔒 测试修改密码...")
            result = self.make_request('POST', '/api/v1/users/change-password', params={
                'old_password': 'test123',
                'new_password': 'newpass123'
            })
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

        # 切换到管理员测试管理员功能
        if self.switch_to_admin():
            # 6. 获取用户列表（管理员）
            print("   📋 测试获取用户列表（管理员）...")
            result = self.make_request('GET', '/api/v1/users/?limit=10')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 7. 获取指定用户信息（管理员）
            print("   🔍 测试获取指定用户信息（管理员）...")
            result = self.make_request('GET', '/api/v1/users/1')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

    def test_product_apis(self):
        """测试商品管理API"""
        print("\n📦 测试商品管理API...")

        # 清除认证头（商品查询不需要认证）
        self.session.headers.pop('Authorization', None)

        # 1. 获取商品分类列表
        print("   📂 测试获取商品分类列表...")
        result = self.make_request('GET', '/api/v1/products/categories')
        print(f"      状态码: {result.status_code}, 成功: {result.success}")

        # 2. 获取商品列表
        print("   📋 测试获取商品列表...")
        result = self.make_request('GET', '/api/v1/products/?limit=10')
        print(f"      状态码: {result.status_code}, 成功: {result.success}")

        # 尝试获取商品详情（如果有商品）
        if result.success and isinstance(result.response_data, dict):
            items = result.response_data.get('items', [])
            if items:
                product_id = items[0].get('id')
                print(f"   🔍 测试获取商品详情 (ID: {product_id})...")
                result = self.make_request('GET', f'/api/v1/products/{product_id}')
                print(f"      状态码: {result.status_code}, 成功: {result.success}")

        # 切换到管理员测试管理功能
        if self.switch_to_admin():
            # 3. 创建商品分类
            print("   ➕ 测试创建商品分类（管理员）...")
            result = self.make_request('POST', '/api/v1/products/categories', json={
                'name': '测试分类',
                'description': 'API测试创建的分类',
                'sort_order': 1
            })
            category_id = None
            if result.success and isinstance(result.response_data, dict):
                category_id = result.response_data.get('id')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 4. 创建商品
            if category_id:
                print("   ➕ 测试创建商品（管理员）...")
                result = self.make_request('POST', '/api/v1/products/', json={
                    'name': 'API测试商品',
                    'description': '这是通过API测试创建的商品',
                    'price': 99.99,
                    'stock': 100
                })
                product_id = None
                if result.success and isinstance(result.response_data, dict):
                    product_id = result.response_data.get('id')
                    self.test_products.append(product_id)
                elif result.status_code == 500:
                    # 如果创建失败，尝试使用已存在的商品
                    print("      商品创建失败，尝试查找现有商品...")
                    products_result = self.make_request('GET', '/api/v1/products/?limit=1')
                    if products_result.success and isinstance(products_result.response_data, dict):
                        items = products_result.response_data.get('items', [])
                        if items:
                            product_id = items[0].get('id')
                            self.test_products.append(product_id)
                            print(f"      使用现有商品ID: {product_id}")
                print(f"      状态码: {result.status_code}, 成功: {result.success}")

                # 5. 更新商品
                if product_id:
                    print(f"   ✏️ 测试更新商品（管理员，ID: {product_id}）...")
                    result = self.make_request('PUT', f'/api/v1/products/{product_id}', json={
                        'name': '更新的API测试商品',
                        'price': 89.99,
                        'stock': 150
                    })
                    print(f"      状态码: {result.status_code}, 成功: {result.success}")

                    # 6. 更新商品库存
                    print(f"   📊 测试更新商品库存（管理员，ID: {product_id}）...")
                    result = self.make_request('POST', f'/api/v1/products/{product_id}/stock?quantity=200')
                    print(f"      状态码: {result.status_code}, 成功: {result.success}")

    def test_order_apis(self):
        """测试订单管理API"""
        print("\n📋 测试订单管理API...")

        # 切换到管理员测试管理功能（订单主要由管理员管理）
        if self.switch_to_admin():
            # 1. 获取订单列表
            print("   📋 测试获取订单列表...")
            result = self.make_request('GET', '/api/v1/orders/?limit=10')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 由于没有现有订单，跳过订单详情等测试
            print("   ⏭️ 跳过订单详情测试（无可用订单）")

    def test_payment_apis(self):
        """测试支付管理API"""
        print("\n💳 测试支付管理API...")

        # 切换到管理员测试管理功能
        if self.switch_to_admin():
            # 1. 获取支付记录列表
            print("   📋 测试获取支付记录...")
            result = self.make_request('GET', '/api/v1/payments/?limit=10')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 2. 尝试创建支付记录（需要有效的订单）
            # 首先检查是否有现有的订单
            orders_result = self.make_request('GET', '/api/v1/orders/?limit=1')
            if orders_result.success and isinstance(orders_result.response_data, dict):
                orders = orders_result.response_data.get('items', [])
                if orders:
                    order = orders[0]
                    order_id = order.get('id')
                    user_id = order.get('user_id')

                    print(f"   ➕ 测试创建支付记录（管理员，订单ID: {order_id}）...")
                    result = self.make_request('POST', '/api/v1/payments/', json={
                        'user_id': user_id,
                        'order_id': order_id,
                        'amount': float(order.get('total_amount', 99.99)),
                        'payment_method': 'balance'
                    })
                    payment_id = None
                    if result.success and isinstance(result.response_data, dict):
                        payment_id = result.response_data.get('id')
                    print(f"      状态码: {result.status_code}, 成功: {result.success}")

                    # 3. 获取支付记录详情（如果创建成功）
                    if payment_id:
                        print(f"   🔍 测试获取支付记录详情（ID: {payment_id}）...")
                        result = self.make_request('GET', f'/api/v1/payments/{payment_id}')
                        print(f"      状态码: {result.status_code}, 成功: {result.success}")
                    else:
                        print("   ⚠️ 跳过支付记录详情测试（无有效支付记录）")
                else:
                    print("   ⚠️ 跳过支付测试（无有效订单）")
            else:
                print("   ⚠️ 跳过支付测试（无法获取订单数据）")

    def test_admin_apis(self):
        """测试后台管理API"""
        print("\n👑 测试后台管理API...")

        # 切换到管理员
        if self.switch_to_admin():
            # 1. 获取仪表盘统计数据
            print("   📊 测试获取仪表盘统计数据...")
            result = self.make_request('GET', '/api/v1/admin/dashboard/stats')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 2. 获取仪表盘图表数据
            print("   📈 测试获取仪表盘图表数据...")
            result = self.make_request('GET', '/api/v1/admin/dashboard/charts?days=7')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

            # 3. 获取系统信息
            print("   🖥️ 测试获取系统信息...")
            result = self.make_request('GET', '/api/v1/admin/system/info')
            print(f"      状态码: {result.status_code}, 成功: {result.success}")

    def generate_report(self) -> str:
        """生成测试报告"""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests

        # 按API模块分组统计
        module_stats = {}
        failed_apis = []

        for result in self.results:
            module = result.api_name
            if module not in module_stats:
                module_stats[module] = {'total': 0, 'success': 0, 'failed': 0}

            module_stats[module]['total'] += 1
            if result.success:
                module_stats[module]['success'] += 1
            else:
                module_stats[module]['failed'] += 1
                failed_apis.append(result)

        # 生成报告
        report = []
        report.append("# 🚀 独角发卡 FastAPI - API测试报告")
        report.append("")
        report.append(f"**测试时间:** {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**测试服务:** {self.base_url}")
        report.append("")
        report.append("## 📊 测试概览")
        report.append("")
        report.append(f"- **总测试数:** {total_tests}")
        report.append(f"- **成功测试:** {successful_tests}")
        report.append(f"- **失败测试:** {failed_tests}")
        report.append(f"- **成功率:** {(successful_tests/total_tests*100):.1f}%")
        report.append("")

        report.append("## 📋 各模块测试结果")
        report.append("")
        for module, stats in module_stats.items():
            success_rate = (stats['success']/stats['total']*100) if stats['total'] > 0 else 0
            status_icon = "✅" if stats['failed'] == 0 else "❌"
            report.append(f"### {status_icon} {module.upper()}")
            report.append(f"- 总测试: {stats['total']}")
            report.append(f"- 成功: {stats['success']}")
            report.append(f"- 失败: {stats['failed']}")
            report.append(f"- 成功率: {success_rate:.1f}%")
            report.append("")

        if failed_apis:
            report.append("## ❌ 失败的API接口")
            report.append("")
            for result in failed_apis:
                report.append(f"### {result.method} {result.endpoint}")
                report.append(f"- **状态码:** {result.status_code}")
                if result.error_message:
                    report.append(f"- **错误信息:** {result.error_message}")
                if result.request_data:
                    report.append(f"- **请求数据:** {json.dumps(result.request_data, ensure_ascii=False, indent=2)}")
                report.append(f"- **响应时间:** {result.response_time}s")
                report.append("")

        report.append("## 📝 测试详情")
        report.append("")
        for result in self.results:
            status_icon = "✅" if result.success else "❌"
            report.append(f"{status_icon} {result.method} {result.endpoint} - {result.status_code} ({result.response_time}s)")

        return "\n".join(report)

    def run_all_tests(self):
        """运行所有API测试"""
        print("🚀 开始API测试...")
        print("=" * 50)

        # 基础功能测试
        self.test_health_check()

        # API功能测试
        self.test_auth_apis()
        self.test_user_apis()
        self.test_product_apis()
        self.test_order_apis()
        self.test_payment_apis()
        self.test_admin_apis()

        print("=" * 50)
        print("✅ API测试完成！")

        # 生成报告
        report = self.generate_report()
        print("\n" + "=" * 50)
        print("📋 测试报告预览:")
        print("=" * 50)

        # 显示关键统计信息
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests

        print(f"总测试数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "成功率: 0.0%")
        # 显示失败的API
        failed_apis = [r for r in self.results if not r.success]
        if failed_apis:
            print(f"\n❌ 发现 {len(failed_apis)} 个问题接口:")
            for result in failed_apis[:5]:  # 只显示前5个
                print(f"   - {result.method} {result.endpoint} (状态码: {result.status_code})")
            if len(failed_apis) > 5:
                print(f"   ... 还有 {len(failed_apis) - 5} 个失败的接口")

        # 保存详细报告
        with open('api_test_report.md', 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 详细报告已保存到: api_test_report.md")

        return report


def main():
    """主函数"""
    print("独角发卡 FastAPI - API测试工具")
    print("=" * 40)

    # 创建测试器
    tester = APITester()

    # 运行所有测试
    report = tester.run_all_tests()

    # 返回测试结果摘要
    return tester.results


if __name__ == "__main__":
    results = main()
