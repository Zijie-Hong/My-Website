from django import template
import re

register = template.Library()

@register.filter(name='split')
def split_string(value, delimiter):
    """将字符串按指定分隔符分割"""
    if isinstance(value, str):
        return value.split(delimiter)
    return []

@register.filter(name='lines')
def split_lines(value):
    """将文本按行分割，支持各种换行符格式"""
    if isinstance(value, str):
        # 使用splitlines()方法处理各种换行符格式（\n, \r\n, \r）
        return value.splitlines()
    return []

@register.filter(name='render_with_images')
def render_with_images(value, project_id):
    """将文本中的图片标记转换为实际的图片显示
    格式: [image:filename.png] 转换为 <img src="/media/task_images/filename.png" alt="图片">
    """
    if not isinstance(value, str):
        return value
    
    # 定义图片标记的正则表达式模式
    pattern = r'\[image:(.*?)\]'
    
    # 替换函数，将匹配的标记转换为img标签
    def replace_image_tag(match):
        filename = match.group(1)
        # 构建图片URL
        image_url = f'/media/task_images/{filename}'
        # 返回img标签，添加适当的样式
        return f'<img src="{image_url}" alt="任务图片" style="max-width: 100%; height: auto; border-radius: 4px; margin: 10px 0;">'
    
    # 执行替换并返回结果
    result = re.sub(pattern, replace_image_tag, value)
    return result


@register.filter(name='get')
def get_item(dictionary, key):
    """安全地从字典中获取值"""
    if isinstance(dictionary, dict) and key in dictionary:
        return dictionary[key]
    return None

@register.filter(name='sum_project_tasks')
def sum_project_tasks(projects):
    """计算所有项目的任务总数"""
    total = 0
    if projects:
        for project in projects:
            if hasattr(project, 'tasks'):
                total += len(project.tasks)
            elif isinstance(project, dict) and 'tasks' in project:
                total += len(project['tasks'])
    return total

@register.filter(name='count_completed_tasks')
def count_completed_tasks(projects):
    """计算已完成的任务数量（进度为100%的任务）"""
    completed = 0
    if projects:
        for project in projects:
            tasks = []
            if hasattr(project, 'tasks'):
                tasks = project.tasks
            elif isinstance(project, dict) and 'tasks' in project:
                tasks = project['tasks']
            
            for task in tasks:
                progress = 0
                if hasattr(task, 'progress'):
                    progress = task.progress
                elif isinstance(task, dict) and 'progress' in task:
                    progress = task['progress']
                
                if progress == 100:
                    completed += 1
    return completed

@register.filter(name='count_tasks_by_category')
def count_tasks_by_category(projects, category_name):
    """按类别统计任务数量"""
    count = 0
    if projects and category_name:
        for project in projects:
            # 支持项目对象和字典两种形式
            tasks = []
            if hasattr(project, 'tasks'):
                tasks = project.tasks
            elif isinstance(project, dict) and 'tasks' in project:
                tasks = project['tasks']
            
            for task in tasks:
                # 支持任务对象和字典两种形式
                task_category = None
                if hasattr(task, 'category'):
                    task_category = task.category
                elif isinstance(task, dict) and 'category' in task:
                    task_category = task['category']
                
                if task_category == category_name:
                    count += 1
    return count

@register.filter(name='filter_tasks_by_category')
def filter_tasks_by_category(tasks, category_name):
    """根据类别筛选任务"""
    filtered_tasks = []
    if tasks and category_name:
        for task in tasks:
            task_category = None
            if hasattr(task, 'category'):
                task_category = task.category
            elif isinstance(task, dict) and 'category' in task:
                task_category = task['category']
            
            if task_category == category_name:
                filtered_tasks.append(task)
    return filtered_tasks

@register.filter(name='filter_tasks_by_workshop')
def filter_tasks_by_workshop(tasks, workshop_number):
    """按workshop过滤任务"""
    if not tasks or not workshop_number:
        return []
    
    filtered = []
    for task in tasks:
        task_workshop = None
        if hasattr(task, 'workshop'):
            task_workshop = task.workshop
        elif isinstance(task, dict) and 'workshop' in task:
            task_workshop = task['workshop']
        
        if task_workshop == workshop_number:
            filtered.append(task)
    
    return filtered

@register.filter(name='count_tasks_for_project')
def count_tasks_for_project(tasks, category_name):
    """统计单个项目中指定类别的任务数量"""
    count = 0
    if tasks and category_name:
        for task in tasks:
            task_category = None
            if hasattr(task, 'category'):
                task_category = task.category
            elif isinstance(task, dict) and 'category' in task:
                task_category = task['category']
            
            if task_category == category_name:
                count += 1
    return count

@register.filter(name='count_completed_tasks_for_project')
def count_completed_tasks_for_project(tasks):
    """统计单个项目中已完成的任务数量"""
    completed = 0
    if tasks:
        for task in tasks:
            progress = 0
            if hasattr(task, 'progress'):
                progress = task.progress
            elif isinstance(task, dict) and 'progress' in task:
                progress = task['progress']
            
            if progress == 100:
                completed += 1
    return completed

@register.filter(name='count_tasks_by_workshop')
def count_tasks_by_workshop(projects, workshop_number):
    """按workshop统计所有项目的任务数量"""
    count = 0
    if projects and workshop_number:
        for project in projects:
            # 支持项目对象和字典两种形式
            tasks = []
            if hasattr(project, 'tasks'):
                tasks = project.tasks
            elif isinstance(project, dict) and 'tasks' in project:
                tasks = project['tasks']
            
            for task in tasks:
                # 支持任务对象和字典两种形式
                task_workshop = None
                if hasattr(task, 'workshop'):
                    task_workshop = task.workshop
                elif isinstance(task, dict) and 'workshop' in task:
                    task_workshop = task['workshop']
                
                if task_workshop == workshop_number:
                    count += 1
    return count

@register.filter(name='count_tasks_by_workshop_for_project')
def count_tasks_by_workshop_for_project(tasks, workshop_number):
    """统计单个项目中指定workshop的任务数量"""
    count = 0
    if tasks and workshop_number:
        for task in tasks:
            task_workshop = None
            if hasattr(task, 'workshop'):
                task_workshop = task.workshop
            elif isinstance(task, dict) and 'workshop' in task:
                task_workshop = task['workshop']
            
            if task_workshop == workshop_number:
                count += 1
    return count

@register.filter(name='count_completed_tasks_by_workshop_for_project')
def count_completed_tasks_by_workshop_for_project(tasks, workshop_number):
    """统计单个项目中指定workshop已完成的任务数量"""
    completed = 0
    if tasks and workshop_number:
        for task in tasks:
            task_workshop = None
            if hasattr(task, 'workshop'):
                task_workshop = task.workshop
            elif isinstance(task, dict) and 'workshop' in task:
                task_workshop = task['workshop']
            
            if task_workshop == workshop_number:
                progress = 0
                if hasattr(task, 'progress'):
                    progress = task.progress
                elif isinstance(task, dict) and 'progress' in task:
                    progress = task['progress']
                
                if progress == 100:
                    completed += 1
    return completed

@register.filter(name='get_workshop_completion_rate')
def get_workshop_completion_rate(tasks, workshop_number):
    """计算指定workshop的任务完成率"""
    total = 0
    completed = 0
    if tasks and workshop_number:
        for task in tasks:
            task_workshop = None
            if hasattr(task, 'workshop'):
                task_workshop = task.workshop
            elif isinstance(task, dict) and 'workshop' in task:
                task_workshop = task['workshop']
            
            if task_workshop == workshop_number:
                total += 1
                progress = 0
                if hasattr(task, 'progress'):
                    progress = task.progress
                elif isinstance(task, dict) and 'progress' in task:
                    progress = task['progress']
                
                if progress == 100:
                    completed += 1
    
    if total > 0:
        return round((completed / total) * 100)
    return 0