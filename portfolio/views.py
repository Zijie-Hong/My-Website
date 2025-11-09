from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Project, Task
from .image_handlers import TaskImage, get_task_images_view, update_task_images
import json
import os
import re

# 任务分类配置
TASK_CATEGORIES = {
    'R&D': {'name': '研究开发', 'display_name': 'R&D', 'color': '#FF7043', 'bg_color': '#FFF3E0'},
    'UAT': {'name': '用户验收', 'display_name': 'UAT', 'color': '#EC407A', 'bg_color': '#FCE4EC'},
    'Support': {'name': '技术支持', 'display_name': 'Support', 'color': '#4CAF50', 'bg_color': '#E8F5E9'}
}

# Workshop配置
WORKSHOP_NUMBERS = {
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五'
}

# 数据存储文件路径
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

# 初始化或加载数据
def load_data():
    """从文件加载项目和任务数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    # 返回初始数据
    return {
        "projects": [],
        "tasks": []
    }

def save_data(data):
    """保存数据到文件 - 增强的错误处理"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        
        # 检查文件权限
        if os.path.exists(DATA_FILE):
            # 检查是否可写
            if not os.access(DATA_FILE, os.W_OK):
                print(f"错误: 文件不可写: {DATA_FILE}")
                return False
        
        # 尝试保存数据
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 成功保存数据到: {DATA_FILE}")
        return True
    except PermissionError:
        print(f"错误: 没有权限写入文件: {DATA_FILE}")
        return False
    except FileNotFoundError:
        print(f"错误: 找不到目录: {os.path.dirname(DATA_FILE)}")
        return False
    except json.JSONDecodeError:
        print(f"错误: JSON序列化失败")
        return False
    except Exception as e:
        print(f"错误: 保存数据失败: {e}")
        return False

# 初始化全局数据
global_data = load_data()

def home(request):
    """首页视图 - 模块化显示项目"""
    projects = global_data['projects']
    return render(request, 'portfolio/home.html', {
        'projects': projects,
        'task_categories': TASK_CATEGORIES
    })

def project_list(request):
    """项目列表视图"""
    projects = global_data['projects']
    return render(request, 'portfolio/project_list.html', {
        'projects': projects,
        'task_categories': TASK_CATEGORIES
    })

def task_list(request, project_id=None):
    """任务列表视图，支持项目筛选和分类筛选"""
    projects = global_data['projects']
    selected_project_id = project_id
    filtered_tasks = []
    
    # 如果指定了项目，只显示该项目的任务
    if project_id:
        selected_project = next((p for p in projects if p['id'] == int(project_id)), None)
        if not selected_project:
            raise Http404("项目不存在")
        filtered_tasks = selected_project['tasks']
    else:
        # 显示所有项目的任务
        for project in projects:
            filtered_tasks.extend(project['tasks'])
    
    # 获取筛选参数
    category = request.GET.get('category')
    workshop = request.GET.get('workshop')
    
    # 应用筛选
    if category and category != 'all':
        filtered_tasks = [t for t in filtered_tasks if t['category'] == category]
    if workshop and workshop != 'all':
        filtered_tasks = [t for t in filtered_tasks if t['workshop'] == int(workshop)]
    
    # 按项目分组任务
    projects_with_tasks = []
    task_project_map = {}
    
    # 构建任务到项目的映射
    for project in projects:
        task_project_map.update({task['id']: project for task in project['tasks']})
    
    # 按项目分组显示任务
    project_tasks = {}
    for task in filtered_tasks:
        project = task_project_map.get(task['id'])
        if project:
            if project['id'] not in project_tasks:
                project_tasks[project['id']] = {
                    'id': project['id'],
                    'name': project['name'],
                    'tasks': []
                }
            project_tasks[project['id']]['tasks'].append(task)
    
    projects_with_tasks = list(project_tasks.values())
    
    return render(request, 'portfolio/task_list.html', {
        'all_projects': projects,
        'selected_project': selected_project_id,
        'selected_category': category,
        'selected_workshop': workshop,
        'workshop_range': range(1, 6),
        'projects_with_tasks': projects_with_tasks,
        'tasks': filtered_tasks,
        'task_categories': TASK_CATEGORIES,
        'workshop_numbers': WORKSHOP_NUMBERS,
        'selected_category': category,
        'selected_workshop': workshop
    })

def task_detail(request, project_id, task_id):
    """任务详情视图"""
    project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
    if not project:
        raise Http404("项目不存在")
    
    task = next((t for t in project['tasks'] if t['id'] == int(task_id)), None)
    if not task:
        raise Http404("任务不存在")
    
    # 获取workshop中文表示
    task['workshop_text'] = f"第{WORKSHOP_NUMBERS.get(task['workshop'], 'N/A')}次workshop"
    
    # 确保step_images字段存在，即使为空也设置为数组
    if 'step_images' not in task:
        task['step_images'] = []
    
    # 从数据库获取该任务的所有图片并添加到task中
    try:
        db_images = TaskImage.objects.filter(task_id=task_id).order_by('-uploaded_at')
        
        # 将QuerySet转换为可JSON序列化的字典列表
        task['db_images'] = [{
            'id': img.id,
            'task_id': img.task_id,
            'image_url': img.image.url,
            'description': img.description or '',
            'uploaded_at': img.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
        } for img in db_images]
        
        # 如果JSON文件中没有step_images数据，尝试从数据库添加
        if not task['step_images'] and db_images:
            for img in db_images:
                task['step_images'].append({
                    'step': 1,  # 默认步骤为1
                    'url': img.image.url,
                    'image_url': img.image.url,
                    'description': img.description or '',
                    'file_name': os.path.basename(img.image.name)
                })
        
        print(f"任务 {task_id} 图片数据: JSON中{len(task['step_images'])}张，数据库中{len(db_images)}张")
    except Exception as e:
        print(f"获取图片数据时出错: {e}")
        task['db_images'] = []
    
    # 相关任务逻辑 - 获取同一项目中除了当前任务外的其他任务
    related_tasks = [t for t in project['tasks'] if t['id'] != int(task_id)]
    
    return render(request, 'portfolio/task_detail.html', {
        'project': project,
        'task': task,
        'task_categories': TASK_CATEGORIES,
        'related_tasks': related_tasks
    })

def add_task(request, project_id):
    """新增任务视图"""
    projects = global_data['projects']
    
    # 处理POST请求
    if request.method == 'POST':
        # 优先使用表单提交的project_id，如果没有则使用URL参数
        form_project_id = request.POST.get('project_id')
        if form_project_id:
            project_id = form_project_id
        
        # 查找对应的项目
        project = next((p for p in projects if p['id'] == int(project_id)), None)
        if not project:
            return render(request, 'portfolio/add_task.html', {
                'project': None,
                'projects': projects,
                'task_categories': TASK_CATEGORIES,
                'workshop_numbers': WORKSHOP_NUMBERS,
                'workshop_range': range(1, 6),
                'error': '请选择有效的项目'
            })
        
        # 处理表单提交
        try:
            # 先获取原始process字符串
            process_str = request.POST.get('process', '').strip()
            
            # 将process字符串转换为对象数组，只包含title字段
            process_steps = []
            if process_str:
                # 按行分割并过滤空行
                lines = [line.strip() for line in process_str.split('\n') if line.strip()]
                # 为每行创建一个步骤对象，只包含title字段
                for title in lines:
                    process_steps.append({'title': title})
            
            new_task = {
                'id': global_data['next_task_id'],
                'title': request.POST.get('title', '').strip(),
                  'category': request.POST.get('category'),
                  'workshop': int(request.POST.get('workshop')),
                'description': request.POST.get('description', '').strip(),
                'process': process_steps,  # 使用处理后的步骤对象数组
                'results': request.POST.get('results', '').strip(),
                'progress': int(request.POST.get('progress', 0)),
                'pain_points': request.POST.get('pain_points', '').strip()
            }
            
            # 简单验证
            if not new_task['title'] or not new_task['category']:
                raise ValidationError("请填写必要字段")
            
            # 添加到项目
            project['tasks'].append(new_task)
            global_data['next_task_id'] += 1
            
            # 保存数据
            if save_data(global_data):
                # 重定向到新创建的任务详情页
                return redirect('task_detail', project_id=project_id, task_id=new_task['id'])
            else:
                return render(request, 'portfolio/add_task.html', {
                    'project': project,
                    'projects': projects,
                    'task_categories': TASK_CATEGORIES,
                    'workshop_numbers': WORKSHOP_NUMBERS,
                    'workshop_range': range(1, 6),
                    'error': '保存失败，请重试'
                })
        except Exception as e:
            return render(request, 'portfolio/add_task.html', {
                'project': project,
                'projects': projects,
                'task_categories': TASK_CATEGORIES,
                'workshop_numbers': WORKSHOP_NUMBERS,
                'workshop_range': range(1, 6),
                'error': str(e)
            })
    else:
        # GET请求 - 使用URL参数中的project_id
        project = next((p for p in projects if p['id'] == int(project_id)), None)
        if not project:
            raise Http404("项目不存在")
    
    # GET请求 - 显示表单
    return render(request, 'portfolio/add_task.html', {
        'project': project,
        'projects': projects,
        'task_categories': TASK_CATEGORIES,
        'workshop_numbers': WORKSHOP_NUMBERS,
        'workshop_range': range(1, 6)
    })

def project_detail(request, project_id):
    """项目详情视图"""
    project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
    if not project:
        raise Http404("项目不存在")
    
    # 按分类分组任务
    tasks_by_category = {}
    for category in TASK_CATEGORIES.keys():
        tasks_by_category[category] = [t for t in project['tasks'] if t['category'] == category]
    
    # 计算workshop统计数据
    workshop_stats = {}
    for i in range(1, 6):
        workshop_tasks = [task for task in project['tasks'] if task.get('workshop') == i]
        completed_tasks = [task for task in workshop_tasks if task.get('progress') == 100]
        total = len(workshop_tasks)
        completed = len(completed_tasks)
        completion_rate = round((completed / total) * 100) if total > 0 else 0
        
        workshop_stats[i] = {
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': completion_rate,
            'tasks': workshop_tasks
        }
    
    return render(request, 'portfolio/project_detail.html', {
        'project': project,
        'tasks_by_category': tasks_by_category,
        'task_categories': TASK_CATEGORIES,
        'workshop_numbers': WORKSHOP_NUMBERS,
        'workshop_stats': workshop_stats
    })

def about(request):
    """关于我视图"""
    return render(request, 'portfolio/about.html')



# 添加JsonResponse导入在文件顶部
# from django.http import JsonResponse

from django.http import HttpResponse
import os
from django.conf import settings

def edit_task(request, project_id, task_id):
    """编辑任务功能"""
    global global_data
    
    
    # 查找项目
    project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
    if not project:
        return HttpResponse('项目不存在', status=404)
    
    # 查找任务
    task = next((t for t in project['tasks'] if t['id'] == int(task_id)), None)
    if not task:
        return HttpResponse('任务不存在', status=404)
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            title = request.POST.get('title', '').strip()
            category = request.POST.get('category')
            workshop = int(request.POST.get('workshop', 1))
            progress = int(request.POST.get('progress', 0))
            description = request.POST.get('description', '').strip()
            pain_points = request.POST.get('pain_points', '').strip()
            process = request.POST.get('process', '').strip()
            
            # 处理文件上传
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # 生成唯一文件名
                file_extension = os.path.splitext(image_file.name)[1]
                unique_filename = f"task_{task_id}_img_{os.path.basename(image_file.name).replace(' ', '_')}"
                
                # 保存文件
                file_path = os.path.join(MEDIA_ROOT, unique_filename)
                with open(file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                # 更新任务中的图片引用信息，如果不存在则创建
                if 'images' not in task:
                    task['images'] = {}
                task['images'][unique_filename] = os.path.join('media', 'task_images', unique_filename)
            
            # 简单验证
            if not title or not category:
                return render(request, 'portfolio/edit_task.html', {
                    'project': project,
                    'task': task,
                    'task_categories': TASK_CATEGORIES,
                    'workshop_range': range(1, 6),
                    'error': '任务标题和分类不能为空'
                })
            
            # 更新任务数据
            task['title'] = title
            task['category'] = category
            task['workshop'] = workshop
            task['progress'] = progress
            task['description'] = description
            task['pain_points'] = pain_points  # 保存挑战点字段
            
            # 处理process字段，将字符串转换为对象数组格式
            if process.strip():
                # 分割行并过滤空行
                lines = [line.strip() for line in process.strip().split('\n') if line.strip()]
                
                # 准备新的步骤数组，保留原有content值，更新title
                updated_process = []
                # 获取原有的步骤，用于保留content
                original_steps = {i: step for i, step in enumerate(task.get('process', []))}
                
                # 创建更新后的步骤对象
                for i, title_step in enumerate(lines):
                    # 如果有对应位置的原步骤，保留其content值，否则content设为空
                    content = original_steps.get(i, {}).get('content', '')
                    updated_process.append({'title': title_step, 'content': content})
                    
                task['process'] = updated_process
            else:
                # 空内容处理为空数组
                task['process'] = []
            
            # 保存数据到文件
            if save_data(global_data):
                # 重定向到任务详情页
                return redirect('task_detail', project_id=project_id, task_id=task_id)
            else:
                return render(request, 'portfolio/edit_task.html', {
                    'project': project,
                    'task': task,
                    'task_categories': TASK_CATEGORIES,
                    'workshop_range': range(1, 6),
                    'error': '保存失败，请重试'
                })
        except Exception as e:
            return render(request, 'portfolio/edit_task.html', {
                'project': project,
                'task': task,
                'task_categories': TASK_CATEGORIES,
                'workshop_range': range(1, 6),
                'error': f'处理请求时出错: {str(e)}'
            })
    
    # GET请求，显示编辑表单
    return render(request, 'portfolio/edit_task.html', {
        'project': project,
        'task': task,
        'task_categories': TASK_CATEGORIES,
        'workshop_range': range(1, 6)
    })


def delete_task(request, project_id, task_id):
    """删除任务功能"""
    global global_data
    
    if request.method == 'POST':
        try:
            # 查找项目
            project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
            if not project:
                return HttpResponse('项目不存在', status=404)
            
            # 检查任务是否存在
            task_exists = any(t['id'] == int(task_id) for t in project['tasks'])
            if not task_exists:
                return HttpResponse('任务不存在', status=404)
            
            # 删除任务
            project['tasks'] = [t for t in project['tasks'] if t['id'] != int(task_id)]
            
            # 保存数据到文件
            if save_data(global_data):
                # 重定向到项目详情页
                return redirect('project_detail', project_id=project_id)
            else:
                return HttpResponse('保存失败，请重试', status=500)
        except Exception as e:
            return HttpResponse(f'处理请求时出错: {str(e)}', status=500)
    
    # GET请求不允许删除
    return HttpResponse('Method not allowed', status=405)

def test_workshop_stats(request):
    """测试workshop统计功能的视图"""
    # 获取第一个项目进行测试
    if global_data['projects']:
        project = global_data['projects'][0]
        
        # 计算workshop统计数据
        workshop_stats = {}
        for i in range(1, 6):
            workshop_tasks = [task for task in project['tasks'] if task.get('workshop') == i]
            completed_tasks = [task for task in workshop_tasks if task.get('progress') == 100]
            total = len(workshop_tasks)
            completed = len(completed_tasks)
            completion_rate = round((completed / total) * 100) if total > 0 else 0
            
            workshop_stats[i] = {
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': completion_rate,
                'tasks_count': len(workshop_tasks)
            }
        
        return JsonResponse({'project': project.get('title', 'Unknown Project'), 'workshop_stats': workshop_stats})
    
    return JsonResponse({'error': 'No projects found'})

def upload_task_image(request, project_id, task_id):
    """上传任务图片的视图函数"""
    if request.method == 'POST':
        try:
            # 验证任务ID是否有效（这里可以添加更严格的验证）
            if not isinstance(task_id, int) or task_id <= 0:
                return JsonResponse({'status': 'error', 'message': '无效的任务ID'}, status=400)
            
            # 检查是否有文件上传
            if 'image' not in request.FILES:
                return JsonResponse({'status': 'error', 'message': '没有上传文件'}, status=400)
            
            # 获取上传的文件
            image_file = request.FILES['image']
            
            # 验证文件类型
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(image_file.name)[1].lower()
            if file_extension not in valid_extensions:
                return JsonResponse({'status': 'error', 'message': '不支持的文件类型'}, status=400)
            
            # 创建TaskImage实例
            task_image = TaskImage(
                task_id=task_id,
                image=image_file,
                description=request.POST.get('description', '')
            )
            task_image.save()
            
            # 返回成功响应，包含图片URL和文件名
            # 获取文件名（从存储路径中提取）
            file_name = os.path.basename(task_image.image.name)
            
            return JsonResponse({
                'status': 'success',
                'message': '图片上传成功',
                'image_url': task_image.image.url,
                'image_id': task_image.id,
                'file_name': file_name
            })
            
        except IntegrityError as e:
            return JsonResponse({'status': 'error', 'message': '数据库错误'}, status=500)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'}, status=405)

def update_task_process(request, project_id, task_id):
    """更新任务的实现过程，只更新步骤的title字段"""
    global global_data
    
    if request.method == 'POST':
        try:
            print(f"开始处理项目 {project_id} 任务 {task_id} 的步骤标题更新请求")
            
            # 查找项目和任务
            project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
            if not project:
                return JsonResponse({'status': 'error', 'message': '项目不存在'}, status=404)
            
            task = next((t for t in project['tasks'] if t['id'] == int(task_id)), None)
            if not task:
                return JsonResponse({'status': 'error', 'message': '任务不存在'}, status=404)
            
            # 获取过程内容 - 支持新的对象数组格式
            process_content = request.POST.get('process', '')
            
            # 将textarea内容按行分割，并更新content字段
            if process_content.strip():
                # 分割行但保留空行，确保空内容也能被保存
                lines = [line.strip() for line in process_content.strip().split('\n')]
                print(f"process分割后得到 {len(lines)} 行")
                print(f"分割后的前几行: {lines[:3]}")
                
                # 准备新的步骤数组，保留原有content值，更新title
                updated_process = []
                # 获取原有的步骤，用于保留content
                original_steps = {i: step for i, step in enumerate(task.get('process', []))}
                print(f"原有步骤数量: {len(original_steps)}")
                
                # 创建更新后的步骤对象
                for i, title in enumerate(lines):
                    # 如果有对应位置的原步骤，保留其content值，否则content设为空
                    content = original_steps.get(i, {}).get('content', '')
                    updated_process.append({'title': title, 'content': content})
                    
                task['process'] = updated_process
                print(f"成功更新process对象数组的title字段，包含{len(task['process'])}个步骤")
            else:
                # 空内容处理为空数组
                task['process'] = []
                print("process为空，设置为空数组")
            
            # 保存数据到文件
            if save_data(global_data):
                print("数据成功保存到 JSON 文件")
                return JsonResponse({
                    'status': 'success', 
                    'message': '实现过程标题更新成功',
                    'steps_count': len(task['process'])
                })
            else:
                print("警告: 保存数据到 JSON 文件失败")
                return JsonResponse({
                    'status': 'error', 
                    'message': '保存数据失败，请重试'
                })
        except Exception as e:
            print(f"处理请求时发生错误: {e}")
            return JsonResponse({'status': 'error', 'message': f'处理请求时出错: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def update_task_process_content(request, project_id, task_id):
    """更新任务的实现过程内容，包括步骤的content字段和图片处理（上传与删除）"""
    global global_data
    
    if request.method == 'POST':
        try:
            print(f"开始处理项目 {project_id} 任务 {task_id} 的步骤内容和图片更新请求")
            
            # 查找项目和任务
            project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
            if not project:
                return JsonResponse({'status': 'error', 'message': '项目不存在'}, status=404)
            
            task = next((t for t in project['tasks'] if t['id'] == int(task_id)), None)
            if not task:
                return JsonResponse({'status': 'error', 'message': '任务不存在'}, status=404)
            
            # 获取过程内容
            process_content = request.POST.get('process_content', '')
            
            # 将textarea内容按行分割，并更新content字段
            if process_content.strip():
                # 分割行但保留空行
                lines = [line.strip() for line in process_content.split('\n')]
                print(f"process_content分割后得到 {len(lines)} 行")
                print(f"分割后的前几行: {lines[:3]}")
                
                # 准备新的步骤数组，保留原有title值，更新content
                updated_process = []
                # 获取原有的步骤，用于保留title
                original_steps = {i: step for i, step in enumerate(task.get('process', []))}
                print(f"原有步骤数量: {len(original_steps)}")
                
                # 创建更新后的步骤对象
                for i, content in enumerate(lines):
                    # 如果有对应位置的原步骤，保留其title值，否则title设为默认值
                    title = original_steps.get(i, {}).get('title', f'步骤 {i+1}')
                    updated_process.append({'title': title, 'content': content})
                    
                # 对于原有步骤中超出新内容行数的部分，也添加到更新后的数组中
                for i in range(len(lines), len(original_steps)):
                    if i in original_steps:
                        updated_process.append(original_steps[i])
                        
                task['process'] = updated_process
                print(f"成功更新process对象数组的content字段，包含{len(task['process'])}个步骤")
            else:
                # 保留原有步骤结构，只清空content
                if 'process' in task and task['process']:
                    # 遍历现有步骤，保留title，清空content
                    for step in task['process']:
                        step['content'] = ''
                    print(f"保留了{len(task['process'])}个步骤，清空了所有content")
                else:
                    # 如果原本就没有步骤，保持为空数组
                    task['process'] = []
                    print("process_content为空，且原本没有步骤，保持为空数组")
            
            # 使用集中式的图片处理函数
            image_update_result = update_task_images(task, request, DATA_FILE)
            uploaded_count = image_update_result['uploaded_count']
            
            # 保存数据到文件
            if save_data(global_data):
                print("数据成功保存到 JSON 文件")
                return JsonResponse({
                    'status': 'success', 
                    'message': f'实现过程内容和图片更新成功，成功上传 {uploaded_count} 张图片',
                    'steps_count': len(task['process']),
                    'remaining_images': len(task['step_images'])
                })
            else:
                # 即使JSON保存失败，也返回成功状态，因为实际的数据修改（图片上传/删除）已经成功
                print("警告: 保存数据到 JSON 文件失败，但图片操作已完成")
                return JsonResponse({
                    'status': 'success', 
                    'message': '实现过程内容和图片更新成功',
                    'steps_count': len(task['process']),
                    'remaining_images': len(task['step_images'])
                })
        except Exception as e:
            print(f"处理请求时发生错误: {e}")
            return JsonResponse({'status': 'error', 'message': f'处理请求时出错: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

# 使用image_handlers.py中的视图函数
def get_task_images(request, project_id, task_id):
    """获取任务相关的所有图片（代理到image_handlers中的函数）"""
    return get_task_images_view(request, project_id, task_id)
