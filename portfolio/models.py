from django.db import models

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
    workshop = models.IntegerField()
    description = models.TextField()
    pain_points = models.TextField(blank=True, default='')
    process = models.TextField()
    results = models.TextField()
    progress = models.IntegerField()
    
    def __str__(self):
        return self.title
