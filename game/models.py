from django.db import models
from django.utils import timezone
from datetime import date

class GameRecord(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    log = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-score']
        
    def __str__(self):
        return f"{self.name} - {self.score}"

class EmailVerification(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_reset_token = models.BooleanField(default=False)  # 标记是否为密码重置令牌
    def __str__(self):
        return f"{self.email} - {self.code}"

class regUser(models.Model):
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=256)
    high_score = models.IntegerField(default=0)  
    win_count = models.IntegerField(default=0) 
    
    def __str__(self):
        return self.username
    
    def get_diagnosed_diseases(self):
        """获取用户已诊断的疾病列表"""
        return self.diagnosed_diseases.all().order_by('-diagnosed_at')
    
    def add_diagnosed_disease(self, disease_name):
        """添加用户诊断的疾病"""
        if not self.diagnosed_diseases.filter(disease_name=disease_name).exists():
            self.diagnosed_diseases.create(disease_name=disease_name)
            return True
        return False
    
    
class ScoreboardMeta(models.Model):
    last_reset = models.DateField(default=date.today)

# 新增的每日挑战相关模型
class DailyChallenge(models.Model):
    date = models.DateField(unique=True)
    disease = models.CharField(max_length=100)
    persona = models.CharField(max_length=50)
    
    def __str__(self):
        return f"每日挑战 - {self.date}"

class DailyChallengeRecord(models.Model):
    user = models.ForeignKey(regUser, on_delete=models.CASCADE)
    challenge = models.ForeignKey(DailyChallenge, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'challenge')  # 确保每个用户每天只能玩一次
    
    def __str__(self):
        return f"{self.user.username} - {self.challenge.date} - {self.score}"

class DailyChallengeLeaderboard(models.Model):
    date = models.DateField(unique=True)
    top_records = models.ManyToManyField(DailyChallengeRecord, blank=True)
    
    def update_leaderboard(self):
        # 获取当天所有记录并按分数降序排列
        records = DailyChallengeRecord.objects.filter(
            challenge__date=self.date
        ).order_by('-score')[:10]
        
        # 清空现有记录并添加新的前10名
        self.top_records.clear()
        for record in records:
            self.top_records.add(record)
        
        self.save()
    def __str__(self):
        return f"每日挑战排行榜 - {self.date}"
    

class UserDiagnosedDisease(models.Model):
    user = models.ForeignKey(regUser, on_delete=models.CASCADE, related_name='diagnosed_diseases')
    disease_name = models.CharField(max_length=100)
    diagnosed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'disease_name')  # 确保每个用户每种疾病只记录一次
        
    def __str__(self):
        return f"{self.user.username} - {self.disease_name}"
    

class SubmittedDisease(models.Model):
    user = models.ForeignKey(regUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    symptoms = models.TextField()  # 改为TextField
    onset = models.TextField()
    examinations = models.TextField()  # 改为TextField
    notes = models.TextField(blank=True)
    link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝')
    ], default='pending')
    
    def __str__(self):
        return f"{self.name} (提交者: {self.user.username})"