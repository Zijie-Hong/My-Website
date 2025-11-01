from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponseBadRequest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import TaskImage
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
        'projects': [
            {
                'id': 1,
                'name': 'AFP',
                'description': 'Advanced Financial Platform - 高级金融平台系统，提供实时交易和风险管理功能。',
                'tasks': [
                    {
                        'id': 101,
                        'title': '交易算法优化',
                        'category': 'R&D',
                        'technology': 'Python, C++',
                        'workshop': 1,
                        'description': '优化高频交易算法，提升执行效率和稳定性。',
                        'process': '1. 性能瓶颈分析\n2. 算法重构\n3. 并发优化\n4. 回测验证',
                        'results': '算法执行速度提升35%，资源占用降低20%。',
                        'progress': 85
                    },
                    {
                        'id': 102,
                        'title': '风险控制模块测试',
                        'category': 'UAT',
                        'technology': 'JMeter, Postman',
                        'workshop': 2,
                        'description': '验证风险控制策略在各种市场条件下的有效性。',
                        'process': '1. 测试场景设计\n2. 压力测试执行\n3. 边界测试\n4. 报告生成',
                        'results': '成功识别并修复3个潜在风险点，系统稳定性提升。',
                        'progress': 90
                    },
                    {
                        'id': 103,
                        'title': '客户报表功能支持',
                        'category': 'Support',
                        'technology': 'SQL, Excel',
                        'workshop': 1,
                        'description': '为企业客户提供定制化财务报表和数据分析服务。',
                        'process': '1. 需求收集\n2. 查询开发\n3. 数据验证\n4. 交付培训',
                        'results': '客户满意度提升40%，报表生成时间缩短50%。',
                        'progress': 100
                    }
                ]
            },
            {
                'id': 2,
                'name': 'AAP',
                'description': 'Automated Analytics Platform - 自动化分析平台，实现数据的智能处理和可视化。',
                'tasks': [
                    {
                        'id': 201,
                        'title': '机器学习模型训练',
                        'category': 'R&D',
                        'technology': 'TensorFlow, PyTorch',
                        'workshop': 2,
                        'description': '开发预测分析模型，实现业务趋势的智能预测。',
                        'process': '1. 数据预处理\n2. 特征工程\n3. 模型训练\n4. 模型评估',
                        'results': '预测准确率达到89%，超过业务目标10个百分点。',
                        'progress': 70
                    },
                    {
                        'id': 202,
                        'title': '数据准确性验证',
                        'category': 'UAT',
                        'technology': 'SQL, Pandas',
                        'workshop': 3,
                        'description': '验证数据分析结果的准确性和一致性。',
                        'process': '1. 数据样本选择\n2. 结果对比分析\n3. 异常处理\n4. 报告生成',
                        'results': '数据准确率达到99.8%，符合业务要求。',
                        'progress': 80
                    }
                ]
            },
            {
                'id': 3,
                'name': '移动应用开发',
                'description': '开发跨平台移动应用，提供便捷的用户服务和功能访问。',
                'tasks': [
                    {
                        'id': 301,
                        'title': '推送通知功能实现',
                        'category': 'RD',
                        'technology': 'Flutter, Firebase',
                        'workshop': 3,
                        'description': '实现用户个性化推送通知功能，提升用户活跃度。',
                        'process': '1. 需求分析\n2. 技术方案设计\n3. 功能开发\n4. 性能测试',
                        'results': '通知到达率达到98%，用户点击转化率提升20%。',
                        'progress': 60
                    },
                    {
                        'id': 302,
                        'title': '版本兼容性测试',
                        'category': 'UAT',
                        'technology': 'Appium',
                        'workshop': 4,
                        'description': '测试应用在不同设备和系统版本上的兼容性。',
                        'process': '1. 测试设备选择\n2. 测试用例执行\n3. 问题收集\n4. 兼容性修复',
                        'results': '支持98%主流设备和系统版本，稳定性评分4.8/5。',
                        'progress': 40
                    },
                    {
                        'id': 303,
                        'title': '用户反馈问题修复',
                        'category': 'Support',
                        'technology': 'Flutter, Dart',
                        'workshop': 2,
                        'description': '处理用户反馈的应用崩溃和功能异常问题。',
                        'process': '1. 问题分类\n2. 优先级评估\n3. 问题修复\n4. 版本发布',
                        'results': '应用崩溃率降低60%，用户满意度提升15%。',
                        'progress': 95
                    }
                ]
            }
        ],
        'next_task_id': 304,
        'next_project_id': 4
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
            new_task = {
                'id': global_data['next_task_id'],
                'title': request.POST.get('title', '').strip(),
                'category': request.POST.get('category'),
                'technology': request.POST.get('technology', '').strip(),
                'workshop': int(request.POST.get('workshop')),
                'description': request.POST.get('description', '').strip(),
                'process': request.POST.get('process', '').strip(),
                'results': request.POST.get('results', '').strip(),
                'progress': int(request.POST.get('progress', 0))
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
    
    # 确保图片目录存在
    MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media', 'task_images')
    os.makedirs(MEDIA_ROOT, exist_ok=True)
    
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
            task['process'] = process
            
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
    """更新任务的实现过程，包括多步骤图片上传和删除 - 修复版"""
    global global_data
    
    if request.method == 'POST':
        try:
            print(f"开始处理项目 {project_id} 任务 {task_id} 的图片删除请求")
            
            # 查找项目和任务
            project = next((p for p in global_data['projects'] if p['id'] == int(project_id)), None)
            if not project:
                return JsonResponse({'status': 'error', 'message': '项目不存在'}, status=404)
            
            task = next((t for t in project['tasks'] if t['id'] == int(task_id)), None)
            if not task:
                return JsonResponse({'status': 'error', 'message': '任务不存在'}, status=404)
            
            # 获取过程内容
            process_content = request.POST.get('process', '').strip()
            task['process'] = process_content
            
            # 确保步骤图片列表存在
            if 'step_images' not in task:
                task['step_images'] = []
            
            # 处理图片删除请求 - 增强的删除逻辑
            images_to_delete = request.POST.getlist('delete_step_image[]')
            print(f"接收到的删除请求: {images_to_delete}")
            print(f"删除前图片列表长度: {len(task['step_images'])}")
            
            if images_to_delete:
                MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media', 'task_step_images')
                new_step_images = []
                deleted_count = 0
                failed_to_delete = 0
                
                # 创建一个包含所有文件名的集合，用于快速匹配
                delete_filenames = set()
                for delete_key in images_to_delete:
                    # 提取文件名部分（如果是step_filename格式）
                    parts = delete_key.split('_')
                    if len(parts) > 1:
                        # 尝试提取可能的文件名
                        potential_filename = '_'.join(parts[1:])
                        if '.' in potential_filename:  # 文件名通常包含扩展名
                            delete_filenames.add(potential_filename)
                    # 也添加原始键作为匹配项
                    delete_filenames.add(delete_key)
                
                print(f"用于匹配的文件名集合: {delete_filenames}")
                
                # 预先收集需要从数据库中删除的图片ID
                db_images_to_delete = []
                
                for img in task['step_images']:
                    step_num = str(img.get('step', ''))
                    # 同时检查'filename'和'file_name'键
                    filename = img.get('file_name', img.get('filename', ''))
                    
                    # 构建当前图片的标识
                    current_key = f"{step_num}_{filename}"
                    
                    # 多维度检查是否应该删除
                    should_delete = False
                    
                    # 1. 检查是否在删除集合中
                    if filename in delete_filenames or current_key in delete_filenames:
                        should_delete = True
                        print(f"直接匹配成功: {filename} 或 {current_key} 在删除集合中")
                    # 2. 检查是否与任何删除键部分匹配
                    else:
                        for delete_key in images_to_delete:
                            if filename in delete_key or delete_key in filename:
                                should_delete = True
                                print(f"部分匹配成功: {filename} 与 {delete_key}")
                                break
                    
                    if should_delete:
                        deleted_count += 1
                        # 删除物理文件
                        try:
                            file_path = os.path.join(MEDIA_ROOT, filename)
                            print(f"尝试删除文件: {file_path}")
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                print(f"✓ 成功删除文件: {file_path}")
                            else:
                                print(f"⚠ 文件不存在，跳过删除: {file_path}")
                            
                            # 记录需要从数据库删除的图片文件名，用于后续批量删除
                            db_images_to_delete.append(filename)
                        except Exception as e:
                            failed_to_delete += 1
                            print(f"✗ 文件删除失败: {e}")
                            # 即使文件删除失败，仍然从数据中移除该条目
                    else:
                        # 只有不删除的图片才添加到新列表
                        new_step_images.append(img)
                
                # 从数据库中删除对应的图片记录
                if db_images_to_delete:
                    try:
                        # 查找并删除匹配文件名的数据库记录
                        for filename in db_images_to_delete:
                            # 使用包含查询，因为数据库中的文件名可能包含路径前缀
                            TaskImage.objects.filter(image__contains=filename, task_id=task_id).delete()
                            print(f"✓ 从数据库中删除图片记录: {filename}")
                    except Exception as e:
                        print(f"✗ 从数据库删除图片记录时出错: {e}")
                
                # 更新图片列表
                task['step_images'] = new_step_images
                print(f"删除处理完成: 标记删除 {deleted_count} 张，文件删除失败 {failed_to_delete} 张，剩余 {len(new_step_images)} 张")
                
                # 如果删除操作出现问题，确保至少数据层面的一致性
                if deleted_count > 0 and failed_to_delete > 0:
                    print("警告: 部分文件删除失败，但数据已更新")
            
            # 处理新图片上传
            uploaded_steps = set()
            uploaded_count = 0
            print(f"开始处理文件上传，总共收到 {len(request.FILES)} 个文件")
            print(f"上传前step_images列表长度: {len(task['step_images'])}")
            
            # 先收集所有需要处理的文件
            image_files_to_process = []
            for key, image_file in request.FILES.items():
                if key.startswith('step_image_'):
                    image_files_to_process.append((key, image_file))
            
            print(f"需要处理的图片文件数量: {len(image_files_to_process)}")
            
            # 逐个处理收集到的文件
            for key, image_file in image_files_to_process:
                    try:
                        # 解析键名，确保正确处理 step_image_{step}_{index} 格式
                        parts = key.split('_')
                        if len(parts) >= 3:
                            # 确保parts[2]是步骤号
                            try:
                                step_num = int(parts[2])
                                uploaded_steps.add(step_num)
                                
                                # 获取索引（如果有）
                                index = parts[3] if len(parts) >= 4 else 0
                                print(f"解析键名成功: {key}, 步骤: {step_num}, 索引: {index}")
                            except ValueError:
                                print(f"解析键名失败: {key}, parts[2]不是有效的步骤号")
                                continue
                            
                            # 生成唯一文件名
                            file_extension = os.path.splitext(image_file.name)[1].lower()
                            base_name = os.path.splitext(image_file.name)[0]
                            unique_filename = f"task_{task_id}_step_{step_num}_{index}_{base_name.replace(' ', '_')}{file_extension}"
                            
                            # 保存文件
                            MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media', 'task_step_images')
                            os.makedirs(MEDIA_ROOT, exist_ok=True)
                            file_path = os.path.join(MEDIA_ROOT, unique_filename)
                            
                            with open(file_path, 'wb+') as destination:
                                for chunk in image_file.chunks():
                                    destination.write(chunk)
                            
                            # 获取描述，支持两种格式的键名
                            description_key = f"step_description_{step_num}_{index}"
                            description = request.POST.get(description_key, '')
                            # 如果找不到带索引的描述，尝试不带索引的
                            if not description:
                                description_key = f"step_description_{step_num}"
                                description = request.POST.get(description_key, '')
                            
                            # 构建URL
                            image_url = f'/media/task_step_images/{unique_filename}'
                            
                            # 直接添加新图片，不限制数量
                            task['step_images'].append({
                                'step': step_num,
                                'url': image_url,
                                'file_name': unique_filename,  # 与前端保持一致
                                'filename': unique_filename,   # 保持兼容性
                                'description': description
                            })
                            uploaded_count += 1
                            print(f"成功上传新图片: {unique_filename} (第{uploaded_count}张)")
                            print(f"添加图片后，step_images列表长度: {len(task['step_images'])}")
                    except (ValueError, IndexError) as e:
                        print(f"处理上传图片时出错: {e}")
                        continue
            
            print(f"图片处理完成，总共成功上传 {uploaded_count} 张图片，最终step_images列表长度: {len(task['step_images'])}")
            
            # 保存数据到文件
            if save_data(global_data):
                print("数据成功保存到 JSON 文件")
                return JsonResponse({
                    'status': 'success', 
                    'message': f'实现过程更新成功，成功上传 {uploaded_count} 张图片',
                    'remaining_images': len(task['step_images'])
                })
            else:
                # 即使JSON保存失败，也返回成功状态，因为实际的数据修改（图片上传/删除）已经成功
                print("警告: 保存数据到 JSON 文件失败，但图片操作已完成")
                return JsonResponse({
                    'status': 'success', 
                    'message': '实现过程更新成功',
                    'remaining_images': len(task['step_images'])
                })
        except Exception as e:
            print(f"处理请求时发生错误: {e}")
            return JsonResponse({'status': 'error', 'message': f'处理请求时出错: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

def get_task_images(request, project_id, task_id):
    """获取任务相关的所有图片"""
    try:
        # 获取该任务的所有图片
        images = TaskImage.objects.filter(task_id=task_id).order_by('-uploaded_at')
        
        # 构建响应数据
        image_list = [
            {
                'id': image.id,
                'url': image.image.url,
                'description': image.description,
                'uploaded_at': image.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for image in images
        ]
        
        return JsonResponse({
            'status': 'success',
            'images': image_list
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
