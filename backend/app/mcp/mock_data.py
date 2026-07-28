"""Mock data simulating LIMS (Laboratory Information Management System).

This module provides realistic mock data for development and testing
until a real LIMS integration is available.
"""

from datetime import datetime, timedelta
from typing import Any

# ── Experiment Orders ─────────────────────────────────────────────
MOCK_ORDERS: list[dict[str, Any]] = [
    {
        "order_no": "TA2024070001",
        "customer_name": "深圳新能源科技",
        "product_name": "新能源汽车锂电池组",
        "status": "TESTING",
        "current_stage": "高温循环测试",
        "progress": 60,
        "expected_finish": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "stages": [
            {"name": "样品接收", "status": "DONE", "completed_at": "2024-07-10"},
            {"name": "外观检查", "status": "DONE", "completed_at": "2024-07-11"},
            {"name": "容量标定", "status": "DONE", "completed_at": "2024-07-13"},
            {"name": "高温循环测试", "status": "IN_PROGRESS", "completed_at": None},
            {"name": "安全性能测试", "status": "PENDING", "completed_at": None},
            {"name": "数据整理", "status": "PENDING", "completed_at": None},
        ],
    },
    {
        "order_no": "TA2024070002",
        "customer_name": "北京电子研究所",
        "product_name": "军用电源适配器",
        "status": "SAMPLE_RECEIVED",
        "current_stage": "样品接收",
        "progress": 10,
        "expected_finish": (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d"),
        "stages": [
            {"name": "样品接收", "status": "DONE", "completed_at": "2024-07-15"},
            {"name": "外观检查", "status": "PENDING", "completed_at": None},
            {"name": "电性能测试", "status": "PENDING", "completed_at": None},
            {"name": "环境适应性测试", "status": "PENDING", "completed_at": None},
            {"name": "EMC测试", "status": "PENDING", "completed_at": None},
        ],
    },
    {
        "order_no": "TA2024070003",
        "customer_name": "上海精密仪器",
        "product_name": "医用CT机电源模块",
        "status": "COMPLETED",
        "current_stage": "已完成",
        "progress": 100,
        "expected_finish": "2024-07-20",
        "stages": [
            {"name": "样品接收", "status": "DONE", "completed_at": "2024-06-01"},
            {"name": "外观检查", "status": "DONE", "completed_at": "2024-06-02"},
            {"name": "绝缘测试", "status": "DONE", "completed_at": "2024-06-05"},
            {"name": "负载测试", "status": "DONE", "completed_at": "2024-06-10"},
            {"name": "可靠性测试", "status": "DONE", "completed_at": "2024-06-20"},
            {"name": "报告审核", "status": "DONE", "completed_at": "2024-07-01"},
            {"name": "已完成", "status": "DONE", "completed_at": "2024-07-20"},
        ],
    },
    {
        "order_no": "TA2024070004",
        "customer_name": "广州电子科技",
        "product_name": "5G基站射频模块",
        "status": "REPORT_REVIEW",
        "current_stage": "报告审核",
        "progress": 90,
        "expected_finish": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "stages": [
            {"name": "样品接收", "status": "DONE", "completed_at": "2024-06-15"},
            {"name": "外观检查", "status": "DONE", "completed_at": "2024-06-16"},
            {"name": "射频性能测试", "status": "DONE", "completed_at": "2024-06-25"},
            {"name": "功耗测试", "status": "DONE", "completed_at": "2024-07-01"},
            {"name": "环境测试", "status": "DONE", "completed_at": "2024-07-10"},
            {"name": "报告审核", "status": "IN_PROGRESS", "completed_at": None},
        ],
    },
]

# ── Test Prices ───────────────────────────────────────────────────
MOCK_TEST_PRICES: list[dict[str, Any]] = [
    {"test_name": "高温测试", "standard": "GB/T 2423.2", "price": 3000, "duration": "5个工作日"},
    {"test_name": "低温测试", "standard": "GB/T 2423.1", "price": 2800, "duration": "5个工作日"},
    {"test_name": "恒温恒湿测试", "standard": "GB/T 2423.3", "price": 3500, "duration": "7个工作日"},
    {"test_name": "温度循环测试", "standard": "GB/T 2423.22", "price": 4000, "duration": "7个工作日"},
    {"test_name": "振动测试", "standard": "GB/T 2423.56", "price": 5000, "duration": "5个工作日"},
    {"test_name": "冲击测试", "standard": "GB/T 2423.5", "price": 4500, "duration": "3个工作日"},
    {"test_name": "盐雾测试", "standard": "GB/T 2423.17", "price": 3800, "duration": "10个工作日"},
    {"test_name": "IP防护等级测试", "standard": "GB/T 4208", "price": 6000, "duration": "5个工作日"},
    {"test_name": "绝缘电阻测试", "standard": "GB/T 10064", "price": 1500, "duration": "2个工作日"},
    {"test_name": "介电强度测试", "standard": "GB/T 1408.1", "price": 2000, "duration": "2个工作日"},
    {"test_name": "EMC辐射测试", "standard": "GB/T 9254", "price": 8000, "duration": "7个工作日"},
    {"test_name": "EMC抗扰度测试", "standard": "GB/T 17626", "price": 7500, "duration": "7个工作日"},
    {"test_name": "跌落测试", "standard": "GB/T 2423.7", "price": 2500, "duration": "2个工作日"},
    {"test_name": "外观检查", "standard": "GB/T 2828.1", "price": 500, "duration": "1个工作日"},
    {"test_name": "容量标定", "standard": "GB/T 36972", "price": 2000, "duration": "3个工作日"},
    {"test_name": "循环寿命测试", "standard": "GB/T 31484", "price": 12000, "duration": "30个工作日"},
    {"test_name": "安全性能测试", "standard": "GB/T 31485", "price": 6000, "duration": "7个工作日"},
    {"test_name": "负载测试", "standard": "GB/T 7260.3", "price": 3500, "duration": "5个工作日"},
    {"test_name": "可靠性测试", "standard": "GB/T 37977", "price": 10000, "duration": "20个工作日"},
    {"test_name": "射频性能测试", "standard": "YD/T 2583", "price": 9000, "duration": "7个工作日"},
    {"test_name": "功耗测试", "standard": "GB/T 33798", "price": 3000, "duration": "3个工作日"},
]

# ── Reports ───────────────────────────────────────────────────────
MOCK_REPORTS: list[dict[str, Any]] = [
    {
        "order_no": "TA2024070003",
        "report_id": "REP-2024-0123",
        "status": "COMPLETED",
        "file_url": "https://lims.example.com/reports/REP-2024-0123.pdf",
        "created_at": "2024-07-20",
        "summary": "所有测试项目均合格，符合GB/T 7260.3标准要求。",
    },
    {
        "order_no": "TA2024070004",
        "report_id": "REP-2024-0124",
        "status": "REVIEWING",
        "file_url": None,
        "created_at": None,
        "summary": "报告正在审核中，预计2个工作日内完成。",
    },
    {
        "order_no": "TA2024070001",
        "report_id": None,
        "status": "NOT_AVAILABLE",
        "file_url": None,
        "created_at": None,
        "summary": "试验尚未完成，暂无可下载报告。",
    },
]

# ── Labs ──────────────────────────────────────────────────────────
MOCK_LABS: list[dict[str, Any]] = [
    {
        "lab_id": "LAB-001",
        "name": "环境可靠性实验室",
        "location": "A栋3楼",
        "equipment": [
            {"name": "恒温恒湿箱", "model": "TH-800", "status": "AVAILABLE"},
            {"name": "温度冲击箱", "model": "TS-500", "status": "IN_USE"},
            {"name": "振动台", "model": "VT-3000", "status": "AVAILABLE"},
            {"name": "盐雾箱", "model": "SS-200", "status": "MAINTENANCE"},
        ],
        "available_slots": [
            {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "slots": ["09:00-12:00", "14:00-17:00"]},
            {"date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), "slots": ["09:00-12:00", "13:00-16:00"]},
            {"date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"), "slots": ["14:00-17:00"]},
        ],
    },
    {
        "lab_id": "LAB-002",
        "name": "EMC测试实验室",
        "location": "B栋1楼",
        "equipment": [
            {"name": "电磁兼容测试系统", "model": "EMC-1000", "status": "AVAILABLE"},
            {"name": "屏蔽室", "model": "SR-6x4x3", "status": "AVAILABLE"},
        ],
        "available_slots": [
            {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "slots": ["09:00-12:00"]},
            {"date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"), "slots": ["09:00-12:00", "13:00-17:00"]},
            {"date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), "slots": ["09:00-12:00", "13:00-17:00"]},
        ],
    },
    {
        "lab_id": "LAB-003",
        "name": "电性能测试实验室",
        "location": "A栋5楼",
        "equipment": [
            {"name": "电池充放电测试系统", "model": "BTS-5000", "status": "AVAILABLE"},
            {"name": "绝缘电阻测试仪", "model": "IR-2000", "status": "AVAILABLE"},
            {"name": "耐压测试仪", "model": "WT-100", "status": "IN_USE"},
        ],
        "available_slots": [
            {"date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), "slots": ["13:00-17:00"]},
            {"date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"), "slots": ["09:00-12:00", "13:00-17:00"]},
        ],
    },
]

# ── Reservations ──────────────────────────────────────────────────
MOCK_RESERVATIONS: list[dict[str, Any]] = []
