
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys
from django.conf import settings

def send_reset_email(recipient_email, reset_code):
    # 邮件服务器配置
    smtp_server = ''
    smtp_port = 
    sender_email = ''
    sender_password = ''

    # 邮件内容
    content = f"您好，您的验证码是：{reset_code}，请尽快完成重置操作。"
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(f'医生诊断挑战 <{sender_email}>', 'utf-8')
    message['To'] = Header(f'用户 <{recipient_email}>', 'utf-8')
    message['Subject'] = Header('验证码', 'utf-8')

    try:
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.login(sender_email, sender_password)
        smtp_connection.sendmail(sender_email, recipient_email, message.as_string())
        smtp_connection.quit()
        return True
    except Exception as e:
        print("邮件发送失败：", e)
        return False

if __name__ == '__main__':
    recipient_email = sys.argv[1]
    reset_code = sys.argv[2]
    send_reset_email(recipient_email, reset_code)

# 在 send_email.py 中添加新函数

def send_reset_link(recipient_email, reset_link):
    smtp_server = ''
    smtp_port = 
    sender_email = ''
    sender_password = ''

    # 邮件内容
    content = f"请点击以下链接重置您的密码(30分钟内有效):\n\n{reset_link}\n\n如果您没有请求重置密码，请忽略此邮件。"
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(f'医生诊断挑战 <{sender_email}>', 'utf-8')
    message['To'] = Header(f'用户 <{recipient_email}>', 'utf-8')
    message['Subject'] = Header('密码重置链接', 'utf-8')

    try:
        smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
        smtp_connection.login(sender_email, sender_password)
        smtp_connection.sendmail(sender_email, recipient_email, message.as_string())
        smtp_connection.quit()
        return True
    except Exception as e:
        print("邮件发送失败：", e)
        return False