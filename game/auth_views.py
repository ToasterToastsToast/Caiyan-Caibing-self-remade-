# game/auth_views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
import random
import string
import subprocess

from .models import regUser, EmailVerification
from .forms import RegisterForm, LoginForm

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = regUser.objects.filter(email=email).first()
            if user and check_password(password, user.password):
                request.session['username'] = user.username
                request.session['user_email'] = user.email
                return redirect('chat')
            else:
                form.add_error(None, '邮箱或密码错误')
    else:
        form = LoginForm()
    return render(request, 'game/login.html', {'form': form})

@csrf_exempt
def send_code(request):
    email = request.GET.get('email')
    if not email:
        return JsonResponse({'msg': '邮箱不能为空'})
    
    EmailVerification.objects.filter(email=email).delete()
    code = ''.join(random.choices(string.digits, k=6))
    EmailVerification.objects.create(email=email, code=code)
    
    try:
        subprocess.run(['python', 'd:/djangostuff/doctor_game/game/send_email.py', email, code], check=True)
        return JsonResponse({'success': True, 'msg': '验证码已发送，请查收邮箱'})
    except Exception as e:
        return JsonResponse({'success': False, 'msg': f'邮件发送失败: {e}'})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            email_code = form.cleaned_data['email_code']
            
            # 校验验证码
            try:
                verification = EmailVerification.objects.get(email=email, code=email_code)
                # 验证码有效，检查用户名是否已存在
                if regUser.objects.filter(username=username).exists():
                    form.add_error('username', '用户名已存在')
                else:
                    # 创建用户
                    regUser.objects.create(
                        email=email,
                        username=username,
                        password=make_password(password)
                    )
                    # 删除已使用的验证码
                    verification.delete()
                    messages.success(request, '注册成功，请登录')
                    return redirect('login')
            except EmailVerification.DoesNotExist:
                form.add_error('email_code', '验证码错误或已过期')
    else:
        form = RegisterForm()
    return render(request, 'game/register.html', {'form': form})

def logout(request):
    request.session.flush()
    return redirect('login')

@csrf_exempt
def check_email(request):
    if request.method == 'GET':
        email = request.GET.get('email', '').strip()
        if not email:
            return JsonResponse({'valid': False, 'msg': '请输入邮箱'})
        
        if regUser.objects.filter(email=email).exists():
            return JsonResponse({'valid': False, 'msg': '该邮箱已被注册'})
        else:
            return JsonResponse({'valid': True, 'msg': '邮箱可用'})
        

# 在 auth_views.py 中添加以下视图函数

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = regUser.objects.filter(email=email).first()
        
        if user:
            # 生成重置令牌
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            EmailVerification.objects.filter(email=email).delete()
            EmailVerification.objects.create(email=email, code=token, is_reset_token=True)
            
            # 发送重置邮件
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'token': token}))
            
            try:
                subprocess.run([
                    'python', 
                    'd:/djangostuff/doctor_game/game/send_email.py', 
                    email, 
                    f'请点击以下链接重置密码: {reset_link}'
                ], check=True)
                messages.success(request, '密码重置链接已发送到您的邮箱，请查收')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'发送邮件失败: {e}')
        else:
            messages.error(request, '该邮箱未注册')
    
    return render(request, 'game/password_reset.html')

def password_reset_confirm(request, token):
    try:
        verification = EmailVerification.objects.get(code=token, is_reset_token=True)
    except EmailVerification.DoesNotExist:
        messages.error(request, '无效或过期的重置链接')
        return redirect('login')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, '两次输入的密码不一致')
        else:
            user = regUser.objects.get(email=verification.email)
            user.password = make_password(password)
            user.save()
            verification.delete()
            messages.success(request, '密码重置成功，请使用新密码登录')
            return redirect('login')
    
    return render(request, 'game/password_reset_confirm.html', {'token': token})