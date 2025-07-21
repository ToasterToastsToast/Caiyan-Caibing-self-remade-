from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import regUser,SubmittedDisease
import json
class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
        error_messages={
            'required': '请输入密码',
        }
    )
    password2 = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput,
        error_messages={
            'required': '请再次输入密码',
        }
    )
    email_code = forms.CharField(
        label='邮箱验证码',
        error_messages={
            'required': '请输入邮箱验证码',
        }
    )

    class Meta:
        model = regUser
        fields = ['username', 'email']
        error_messages = {
            'username': {
                'required': '请输入用户名',
                'unique': '该用户名已被使用',
                'max_length': '用户名过长',
            },
            'email': {
                'required': '请输入邮箱',
                'invalid': '请输入有效的邮箱地址',
                'unique': '该邮箱已被注册',
            }
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', '两次输入的密码不一致')

        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
        error_messages={
            'required': '请输入邮箱',
            'invalid': '请输入有效的邮箱地址',
        }
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput,
        error_messages={
            'required': '请输入密码',
        }
    )

class DiseaseSubmissionForm(forms.ModelForm):
    symptoms = forms.CharField(
        widget=forms.Textarea,
        help_text="用逗号分隔多个症状或直接描述症状"
    )
    examinations = forms.CharField(
        widget=forms.Textarea,
        help_text='描述检查结果，例如：体温38.5°C，血常规显示白细胞升高'
    )
    
    class Meta:
        model = SubmittedDisease
        fields = ['name', 'symptoms', 'onset', 'examinations', 'notes', 'link']
        
    def clean_symptoms(self):
        # 不再强制转换为列表，直接返回文本
        return self.cleaned_data['symptoms']
        
    def clean_examinations(self):
        # 不再验证JSON，直接返回文本
        return self.cleaned_data['examinations']
    
    def save(self, commit=True):
        # 保存方法可以保持不变，因为模型字段已经是JSONField，但会存储普通文本
        instance = super().save(commit=False)
        instance.examinations = self.cleaned_data['examinations']
        instance.symptoms = self.cleaned_data['symptoms']

        if commit:
            instance.save()
        return instance