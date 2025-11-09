"""
图片处理相关的后端逻辑集中管理
包含图片模型定义、上传、删除、查询等功能
"""

from django.db import models
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
import os
import json


def task_image_upload_path(instance, filename):
    """为上传的图片生成存储路径"""
    # 获取文件扩展名
    ext = filename.split('.')[-1]
    # 生成新的文件名，包含任务ID和时间戳
    filename = f'task_{instance.task_id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.{ext}'
    # 返回存储路径
    return os.path.join('task_images', filename)


class TaskImage(models.Model):
    """任务图片模型"""
    task_id = models.IntegerField(help_text="关联的任务ID")
    image = models.ImageField(upload_to=task_image_upload_path, help_text="上传的图片")
    description = models.CharField(max_length=200, blank=True, null=True, help_text="图片描述")
    uploaded_at = models.DateTimeField(auto_now_add=True, help_text="上传时间")
    
    def __str__(self):
        return f"Task {self.task_id} - {self.uploaded_at}"


def handle_image_deletion(task, images_to_delete, DATA_FILE):
    """
    处理图片删除逻辑
    
    Args:
        task: 任务对象
        images_to_delete: 需要删除的图片列表
        DATA_FILE: 数据文件路径
    
    Returns:
        dict: 包含删除结果的字典
    """
    print(f"接收到的删除请求: {images_to_delete}")
    print(f"删除前图片列表长度: {len(task['step_images'])}")
    
    if not images_to_delete:
        return {
            'success': True,
            'deleted_count': 0,
            'failed_to_delete': 0,
            'remaining_count': len(task['step_images'])
        }
    
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
        # 同时检查'file_name'和'filename'键
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
                TaskImage.objects.filter(image__contains=filename, task_id=task['id']).delete()
                print(f"✓ 从数据库中删除图片记录: {filename}")
        except Exception as e:
            print(f"✗ 从数据库删除图片记录时出错: {e}")
    
    # 更新图片列表
    task['step_images'] = new_step_images
    print(f"删除处理完成: 标记删除 {deleted_count} 张，文件删除失败 {failed_to_delete} 张，剩余 {len(new_step_images)} 张")
    
    # 如果删除操作出现问题，确保至少数据层面的一致性
    if deleted_count > 0 and failed_to_delete > 0:
        print("警告: 部分文件删除失败，但数据已更新")
    
    return {
        'success': True,
        'deleted_count': deleted_count,
        'failed_to_delete': failed_to_delete,
        'remaining_count': len(new_step_images)
    }


def handle_image_upload(task, request_files, request_post, DATA_FILE):
    """
    处理图片上传逻辑
    
    Args:
        task: 任务对象
        request_files: 请求中的文件对象
        request_post: 请求中的POST数据
        DATA_FILE: 数据文件路径
    
    Returns:
        dict: 包含上传结果的字典
    """
    uploaded_steps = set()
    uploaded_count = 0
    print(f"开始处理文件上传，总共收到 {len(request_files)} 个文件")
    print(f"上传前step_images列表长度: {len(task['step_images'])}")
    
    # 先收集所有需要处理的文件，按步骤分组
    files_by_step = {}
    for key, image_file in request_files.items():
        if key.startswith('step_image_'):
            parts = key.split('_')
            if len(parts) >= 3:
                try:
                    step_num = int(parts[2])
                    if step_num not in files_by_step:
                        files_by_step[step_num] = []
                    files_by_step[step_num].append((key, image_file))
                except ValueError:
                    print(f"解析键名失败: {key}, parts[2]不是有效的步骤号")
    
    print(f"按步骤分组后的文件: {json.dumps({k: len(v) for k, v in files_by_step.items()})}")
    
    # 为每个步骤处理文件
    for step_num, files in files_by_step.items():
        uploaded_steps.add(step_num)
        
        # 检查当前步骤已有图片数量
        existing_step_images = [img for img in task['step_images'] if img.get('step') == step_num]
        current_count = len(existing_step_images)
        max_allowed = 3  # 每个步骤最多3张图片
        remaining_slots = max_allowed - current_count
        
        print(f"步骤{step_num}: 当前已有{current_count}张图片, 剩余{remaining_slots}个槽位")
        
        # 限制每个步骤的图片数量
        files_to_process = files[:remaining_slots]
        if len(files) > remaining_slots:
            print(f"警告: 步骤{step_num}超过图片限制，只处理前{remaining_slots}张")
        
        # 处理该步骤的文件
        for index, (key, image_file) in enumerate(files_to_process):
            try:
                # 生成唯一文件名，确保包含步骤号
                file_extension = os.path.splitext(image_file.name)[1].lower()
                base_name = os.path.splitext(image_file.name)[0]
                unique_filename = f"task_{task['id']}_step_{step_num}_{index}_{base_name.replace(' ', '_')}{file_extension}"
                
                # 保存文件
                MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'media', 'task_step_images')
                os.makedirs(MEDIA_ROOT, exist_ok=True)
                file_path = os.path.join(MEDIA_ROOT, unique_filename)
                
                with open(file_path, 'wb+') as destination:
                    for chunk in image_file.chunks():
                        destination.write(chunk)
                
                # 获取描述，支持两种格式的键名
                description_key = f"step_description_{step_num}_{index}"
                description = request_post.get(description_key, '')
                # 如果找不到带索引的描述，尝试不带索引的
                if not description:
                    description_key = f"step_description_{step_num}"
                    description = request_post.get(description_key, '')
                
                # 构建URL
                image_url = f'/media/task_step_images/{unique_filename}'
                
                # 创建图片数据对象，明确关联到当前步骤
                image_data = {
                    'step': step_num,
                    'url': image_url,
                    'file_name': unique_filename,
                    'filename': unique_filename,
                    'description': description
                }
                
                # 添加到任务的步骤图片列表
                task['step_images'].append(image_data)
                uploaded_count += 1
                print(f"成功上传图片到步骤{step_num}: {unique_filename} (第{uploaded_count}张)")
                
                # 同时将图片保存到数据库
                try:
                    task_image = TaskImage(
                        task_id=task['id'],
                        image=os.path.join('task_step_images', unique_filename),
                        description=description
                    )
                    task_image.save()
                    print(f"✓ 图片已保存到数据库: {unique_filename}")
                    # 更新image_data，添加数据库ID
                    image_data['id'] = task_image.id
                except Exception as db_error:
                    print(f"✗ 保存到数据库失败: {db_error}")
            
            except Exception as e:
                print(f"处理步骤{step_num}的图片时出错: {e}")
                continue
            except (ValueError, IndexError) as e:
                print(f"处理上传图片时出错: {e}")
                continue
    
    print(f"图片处理完成，总共成功上传 {uploaded_count} 张图片，最终step_images列表长度: {len(task['step_images'])}")
    
    return {
        'success': True,
        'uploaded_count': uploaded_count,
        'final_image_count': len(task['step_images']),
        'uploaded_steps': list(uploaded_steps)
    }


def get_task_images_view(request, project_id, task_id):
    """
    获取任务相关的所有图片的视图函数
    
    Args:
        request: HTTP请求对象
        project_id: 项目ID
        task_id: 任务ID
    
    Returns:
        JsonResponse: 包含图片列表的JSON响应
    """
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


def update_task_images(task, request, DATA_FILE):
    """
    综合处理任务图片的更新（删除和上传）
    
    Args:
        task: 任务对象
        request: HTTP请求对象
        DATA_FILE: 数据文件路径
    
    Returns:
        dict: 包含更新结果的字典
    """
    # 确保步骤图片列表存在
    if 'step_images' not in task:
        task['step_images'] = []
    
    # 处理图片删除
    images_to_delete = request.POST.getlist('delete_step_image[]')
    delete_result = handle_image_deletion(task, images_to_delete, DATA_FILE)
    
    # 处理新图片上传
    upload_result = handle_image_upload(task, request.FILES, request.POST, DATA_FILE)
    
    return {
        **delete_result,
        **upload_result,
        'total_processed': delete_result['deleted_count'] + upload_result['uploaded_count']
    }
