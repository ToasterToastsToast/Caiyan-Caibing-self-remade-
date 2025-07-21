from django.urls import path
from . import views
from .auth_views import login, register, logout, send_code, check_email,password_reset, password_reset_confirm
urlpatterns = [
    path('', views.chat, name='chat'),
    path('chat/', views.chat, name='chat'),
    path('handle_chat/', views.handle_chat, name='handle_chat'),
    path('win/', views.win, name='win'),
    path('save_score/', views.save_score, name='save_score'),
    path('scoreboard/', views.scoreboard, name='scoreboard'),
    path('get_log/<int:record_id>/', views.get_log, name='get_log'),
    path('register/', register, name='register'),  # 直接使用导入的函数
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('send_code/', send_code, name='send_code'),
    path('check_email/', check_email, name='check_email'),
    path('get_persona/', views.get_persona, name='get_persona'),
    path('profile/', views.profile, name='profile'),
    path('daily-challenge/', views.daily_challenge, name='daily_challenge'),
    path('daily-leaderboard/', views.daily_challenge_leaderboard, name='daily_challenge_leaderboard'),
    path('daily-leaderboard/<str:date_str>/', views.daily_challenge_leaderboard, name='daily_challenge_leaderboard_date'),
    path('daily-challenge/chat/', views.daily_challenge_chat, name='daily_challenge_chat'),
    path('handle_daily_challenge/', views.handle_daily_challenge, name='handle_daily_challenge'),
    path('submit-disease/', views.submit_disease, name='submit_disease'),
    path('password_reset/', password_reset, name='password_reset'),
    path('password_reset/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
]