from django.db import models
from django.utils import timezone
import os

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

class Project(models.Model):
    """项目模型"""
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """任务模型"""
    id = models.IntegerField(primary_key=True)
    project_id = models.IntegerField()
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    technology = models.CharField(max_length=200)
    workshop = models.IntegerField()
    description = models.TextField()
    process = models.TextField()
    results = models.TextField()
    progress = models.IntegerField()
    
    def __str__(self):
        return self.title
