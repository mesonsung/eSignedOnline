import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
import logging
import ssl

logger = logging.getLogger(__name__)

async def send_activation_email(email: str, activation_code: str, language: str = "zh-TW"):
    """發送啟用郵件 - 正式郵件發送版本"""
    
    try:
        logger.info(f"準備發送啟用郵件到: {email}")
        
        # 多語言郵件內容（HTML格式）
        email_templates = {
            "zh-TW": {
                "subject": "eSignedOnline 帳號啟用",
                "body": f"""
                <html>
                <body>
                    <h2>歡迎使用 eSignedOnline</h2>
                    <p>您的帳號已成功註冊。請使用以下啟用碼啟用您的帳號：</p>
                    <h3 style="color: #1976d2;">{activation_code}</h3>
                    <p>請在系統中輸入此啟用碼以完成帳號啟用。</p>
                    <p>此啟用碼將在24小時後過期。</p>
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
                    <p>Your account has been successfully registered. Please use the following activation code:</p>
                    <h3 style="color: #1976d2;">{activation_code}</h3>
                    <p>Please enter this activation code in the system to complete your account activation.</p>
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
                    <p>Tài khoản của bạn đã được đăng ký thành công. Vui lòng sử dụng mã kích hoạt sau:</p>
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
        
        # 創建郵件
        message = MIMEMultipart("alternative")
        message["From"] = settings.smtp_username
        message["To"] = email
        message["Subject"] = template["subject"]
        
        # 添加HTML內容
        html_part = MIMEText(template["body"], "html")
        message.attach(html_part)
        
        # 嘗試使用標準 SMTP 發送
        try:
            logger.info(f"嘗試使用標準 SMTP 發送: {settings.smtp_host}:{settings.smtp_port}")
            
            smtp = aiosmtplib.SMTP(
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                use_tls=False
            )
            
            await smtp.connect()
            await smtp.starttls()
            await smtp.login(settings.smtp_username, settings.smtp_password)
            await smtp.send_message(message)
            await smtp.quit()
            
            logger.info(f"啟用郵件已成功發送到: {email}")
            return True
            
        except Exception as smtp_error:
            logger.warning(f"標準 SMTP 發送失敗: {smtp_error}")
            logger.info("嘗試備用 SMTP 方法...")
            # 使用備用方法
            return await send_activation_email_fallback(email, activation_code, language)
        
    except Exception as e:
        logger.error(f"郵件發送失敗: {e}")
        # 記錄啟用碼到日誌供管理員查看
        logger.error(f"!!! 重要：用戶 {email} 的啟用碼是: {activation_code} !!!")
        print(f"!!! 重要：用戶 {email} 的啟用碼是: {activation_code} !!!")
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
        # 方法1: 嘗試使用 SSL 端口 (465)
        logger.info(f"備用方法1: 嘗試使用 SSL 端口 465")
        
        smtp = aiosmtplib.SMTP(
            hostname=settings.smtp_host,
            port=465,  # Gmail SSL 端口
            use_tls=True,
            validate_certs=False
        )
        
        await smtp.connect()
        await smtp.login(settings.smtp_username, settings.smtp_password)
        await smtp.send_message(message)
        await smtp.quit()
        
        logger.info(f"備用方法1成功：啟用郵件已發送到 {email}")
        return True
        
    except Exception as ssl_error:
        logger.warning(f"備用方法1 (SSL) 失敗: {ssl_error}")
        
        # 方法2: 嘗試使用 TLS 端口 (587) 但不啟用 STARTTLS
        try:
            logger.info(f"備用方法2: 嘗試 TLS 端口 587")
            
            smtp = aiosmtplib.SMTP(
                hostname=settings.smtp_host,
                port=587,
                use_tls=False
            )
            
            await smtp.connect()
            await smtp.login(settings.smtp_username, settings.smtp_password)
            await smtp.send_message(message)
            await smtp.quit()
            
            logger.info(f"備用方法2成功：啟用郵件已發送到 {email}")
            return True
            
        except Exception as tls_error:
            logger.error(f"備用方法2也失敗: {tls_error}")
            
            # 所有方法都失敗，記錄詳細錯誤信息
            logger.error(f"所有SMTP方法都失敗。SMTP配置:")
            logger.error(f"  主機: {settings.smtp_host}")
            logger.error(f"  用戶名: {settings.smtp_username}")
            logger.error(f"  密碼長度: {len(settings.smtp_password) if settings.smtp_password else 0}")
            logger.error(f"!!! 重要：用戶 {email} 的啟用碼: {activation_code} !!!")
            print(f"!!! 重要：用戶 {email} 的啟用碼: {activation_code} !!!")
            
            return False
