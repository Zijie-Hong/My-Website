import os
import django
from django.template import Template, Context
from django.template import engines

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_site.settings')
django.setup()

# 模拟数据
class MockProject:
    def __init__(self, tasks):
        self.tasks = tasks

class MockTask:
    def __init__(self, category, progress):
        self.category = category
        self.progress = progress

# 创建模拟数据
mock_tasks = [
    MockTask('R&D', 50),
    MockTask('R&D', 100),
    MockTask('UAT', 75),
    MockTask('UAT', 100),
    MockTask('UAT', 25),
    MockTask('Support', 100),
    MockTask('Support', 0),
]

mock_project = MockProject(mock_tasks)

# 测试过滤器
template_engine = engines['django']

test_template = template_engine.from_string('''
{% load portfolio_filters %}
任务总数: {{ project.tasks|length }}
已完成任务: {{ project.tasks|count_completed_tasks_for_project }}
R&D任务数: {{ project.tasks|count_tasks_for_project:"R&D" }}
UAT任务数: {{ project.tasks|count_tasks_for_project:"UAT" }}
Support任务数: {{ project.tasks|count_tasks_for_project:"Support" }}
''')

# 使用字典作为上下文
context = {'project': mock_project}
result = test_template.render(context)
print("测试结果:")
print(result)