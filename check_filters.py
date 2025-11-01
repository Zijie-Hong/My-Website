from portfolio.templatetags.portfolio_filters import register

print("已注册的过滤器列表:")
for filter_name in register.filters:
    print(f"- {filter_name}")

# 检查我们新添加的过滤器是否存在
new_filters = [
    'count_tasks_by_workshop',
    'count_tasks_by_workshop_for_project',
    'count_completed_tasks_by_workshop_for_project',
    'get_workshop_completion_rate',
    'filter_tasks_by_workshop'
]

print("\n新添加的过滤器检查:")
for f in new_filters:
    if f in register.filters:
        print(f"✅ {f} 过滤器已正确注册")
    else:
        print(f"❌ {f} 过滤器未注册")