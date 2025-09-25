import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging
import ssl

logger = logging.getLogger(__name__)

async def send_activation_email(email: str, activation_code: str, language: str = "zh-TW"):
    """發送啟用郵件 - 開發環境版本"""
    
    try:
        # 在開發環境中，我們直接記錄啟用碼到日誌，避免 SMTP 配置問題
        print(f"=== 用戶註冊啟用碼 ===")
        print(f"Email: {email}")
        print(f"啟用碼: {activation_code}")
        print(f"語言: {language}")
        print(f"========================")
        
        logger.info(f"=== 用戶註冊啟用碼 ===")
        logger.info(f"Email: {email}")
        logger.info(f"啟用碼: {activation_code}")
        logger.info(f"語言: {language}")
        logger.info(f"========================")
        
        # 多語言郵件內容（用於日誌顯示）
        email_templates = {
            "zh-TW": {
                "subject": "eSignedOnline 帳號啟用",
                "body": f"您的帳號已成功註冊，請使用以下啟用碼啟用您的帳號：{activation_code}"
            },
            "en": {
                "subject": "eSignedOnline Account Activation", 
                "body": f"Your account has been successfully registered. Please use the following activation code: {activation_code}"
            },
            "vi": {
                "subject": "Kích hoạt tài khoản eSignedOnline",
                "body": f"Tài khoản của bạn đã được đăng ký thành công. Mã kích hoạt: {activation_code}"
            }
        }
        
        template = email_templates.get(language, email_templates["zh-TW"])
        print(f"郵件主題: {template['subject']}")
        print(f"郵件內容: {template['body']}")
        
        logger.info(f"郵件主題: {template['subject']}")
        logger.info(f"郵件內容: {template['body']}")
        
        # 在開發環境中，我們認為郵件發送成功
        return True
    except Exception as e:
        print(f"郵件發送函數錯誤: {e}")
        logger.error(f"郵件發送函數錯誤: {e}")
        return False

async def send_activation_email_fallback(email: str, activation_code: str, language: str = "zh-TW"):
    """備用郵件發送方法 - 使用不同的 SMTP 配置"""
    
    # 多語言郵件內容
    email_templates = {
        "zh-TW": {
            "subject": "eSignedOnline 帳號啟用",
            "body": f"""
            <html>
            <body>
                <h2>歡迎使用 eSignedOnline</h2>
                <p>您的帳號已成功註冊，請使用以下啟用碼啟用您的帳號：</p>
                <h3 style="color: #1976d2;">{activation_code}</h3>
                <p>請在系統中輸入此啟用碼以完成帳號啟用。</p>
                <p>此啟用碼將在 24 小時後失效。</p>
                <br>
                <p>謝謝！</p>
                <p>eSignedOnline 團隊</p>
            </body>
            </html>
            """
        },
        "en": {
            "subject": "eSignedOnline Account Activation",
            "body": f"""
            <html>
            <body>
                <h2>Welcome to eSignedOnline</h2>
                <p>Your account has been successfully registered. Please use the following activation code to activate your account:</p>
                <h3 style="color: #1976d2;">{activation_code}</h3>
                <p>Please enter this activation code in the system to complete account activation.</p>
                <p>This activation code will expire in 24 hours.</p>
                <br>
                <p>Thank you!</p>
                <p>eSignedOnline Team</p>
            </body>
            </html>
            """
        },
        "vi": {
            "subject": "Kích hoạt tài khoản eSignedOnline",
            "body": f"""
            <html>
            <body>
                <h2>Chào mừng đến với eSignedOnline</h2>
                <p>Tài khoản của bạn đã được đăng ký thành công. Vui lòng sử dụng mã kích hoạt sau để kích hoạt tài khoản:</p>
                <h3 style="color: #1976d2;">{activation_code}</h3>
                <p>Vui lòng nhập mã kích hoạt này vào hệ thống để hoàn tất việc kích hoạt tài khoản.</p>
                <p>Mã kích hoạt này sẽ hết hạn sau 24 giờ.</p>
                <br>
                <p>Cảm ơn!</p>
                <p>Đội ngũ eSignedOnline</p>
            </body>
            </html>
            """
        }
    }
    
    template = email_templates.get(language, email_templates["zh-TW"])
    
    message = MIMEMultipart("alternative")
    message["From"] = settings.smtp_username
    message["To"] = email
    message["Subject"] = template["subject"]
    
    html_part = MIMEText(template["body"], "html")
    message.attach(html_part)
    
    try:
        # 嘗試使用不同的端口和配置
        smtp = aiosmtplib.SMTP(
            hostname=settings.smtp_host,
            port=465,  # 使用 SSL 端口
            use_tls=True,
            validate_certs=False
        )
        
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(settings.smtp_username, settings.smtp_password)
        await smtp.send_message(message)
        await smtp.quit()
        
        logger.info(f"備用方法：啟用郵件已發送到 {email}")
        return True
    except Exception as e:
        logger.error(f"備用方法發送郵件也失敗: {e}")
        # 如果所有方法都失敗，至少記錄啟用碼到日誌
        logger.info(f"用戶 {email} 的啟用碼: {activation_code}")
        return False
