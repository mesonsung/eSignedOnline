import os
import base64
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import tempfile

def add_signature_to_pdf(original_pdf_path: str, signature_image_data: str, signature_info: dict, output_path: str):
    """
    將簽名以透明背景的方式合成到PDF文件的最後一頁
    
    Args:
        original_pdf_path: 原始 PDF 文件路徑
        signature_image_data: Base64 編碼的簽名圖像數據
        signature_info: 簽名信息字典，包含 name, title, reason, timestamp
        output_path: 輸出文件路徑
    """
    try:
        # 讀取原始 PDF
        reader = PdfReader(original_pdf_path)
        writer = PdfWriter()
        
        # 獲取最後一頁
        last_page = reader.pages[-1]
        
        # 創建臨時文件來繪製透明簽名
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # 獲取最後一頁的尺寸
        page_width = float(last_page.mediabox.width)
        page_height = float(last_page.mediabox.height)
        
        # 創建 PDF 畫布，使用與最後一頁相同的尺寸
        c = canvas.Canvas(temp_file.name, pagesize=(page_width, page_height))
        
        # 解析簽名圖像數據
        if signature_image_data.startswith('data:image'):
            # 移除 data:image/png;base64, 前綴
            signature_image_data = signature_image_data.split(',')[1]
        
        # 解碼 Base64 圖像
        image_data = base64.b64decode(signature_image_data)
        image = Image.open(BytesIO(image_data))
        
        # 確保圖像是 RGBA 模式以支持透明度
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 調整圖像大小
        max_width = 200
        max_height = 80
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # 保存調整後的圖像到臨時文件（保持透明度）
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image_file.name, 'PNG')
        temp_image_file.close()
        
        # 簽名位置：右下角
        signature_x = page_width - 250
        signature_y = 100
        
        # 繪製簽名圖像（保持透明度）
        c.drawImage(temp_image_file.name, signature_x, signature_y, width=200, height=80, mask='auto')
        
        # 繪製簽名信息（使用半透明文字）
        c.setFillColorRGB(0, 0, 0, 0.8)  # 半透明黑色文字
        c.setFont("Helvetica", 10)
        c.drawString(signature_x, signature_y - 20, f"簽名者: {signature_info.get('name', '')}")
        
        if signature_info.get('title'):
            c.drawString(signature_x, signature_y - 35, f"職位: {signature_info['title']}")
        
        c.drawString(signature_x, signature_y - 50, f"簽名時間: {signature_info.get('timestamp', '')}")
        
        if signature_info.get('reason'):
            # 處理長文本的換行
            reason_text = signature_info['reason']
            if len(reason_text) > 30:
                reason_text = reason_text[:30] + "..."
            c.drawString(signature_x, signature_y - 65, f"簽名原因: {reason_text}")
        
        c.save()
        
        # 讀取簽名頁面
        signature_reader = PdfReader(temp_file.name)
        signature_page = signature_reader.pages[0]
        
        # 將簽名頁面合併到最後一頁（透明合成）
        last_page.merge_page(signature_page)
        
        # 添加所有頁面到 writer
        for page_num in range(len(reader.pages) - 1):
            writer.add_page(reader.pages[page_num])
        
        # 添加已簽名的最後一頁
        writer.add_page(last_page)
        
        # 寫入輸出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # 清理臨時文件
        os.unlink(temp_file.name)
        os.unlink(temp_image_file.name)
        
        return True
        
    except Exception as e:
        print(f"PDF 簽名處理錯誤: {e}")
        # 清理臨時文件
        try:
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
            if 'temp_image_file' in locals():
                os.unlink(temp_image_file.name)
        except:
            pass
        return False

def create_signature_page(signature_image_data: str, signature_info: dict):
    """
    創建一個包含簽名的 PDF 頁面
    
    Args:
        signature_image_data: Base64 編碼的簽名圖像數據
        signature_info: 簽名信息字典
        
    Returns:
        PDF 頁面的二進制數據
    """
    try:
        # 創建臨時文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        # 創建 PDF 畫布
        c = canvas.Canvas(temp_file.name, pagesize=letter)
        width, height = letter
        
        # 解析簽名圖像數據
        if signature_image_data.startswith('data:image'):
            signature_image_data = signature_image_data.split(',')[1]
        
        # 解碼 Base64 圖像
        image_data = base64.b64decode(signature_image_data)
        image = Image.open(BytesIO(image_data))
        
        # 調整圖像大小
        max_width = 300
        max_height = 120
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # 保存調整後的圖像到臨時文件
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image_file.name, 'PNG')
        temp_image_file.close()
        
        # 在頁面中央繪製簽名
        signature_x = (width - 300) / 2
        signature_y = (height - 200) / 2
        
        # 繪製標題
        c.setFont("Helvetica-Bold", 16)
        c.drawString(signature_x, signature_y + 150, "電子簽名")
        
        # 繪製簽名圖像
        c.drawImage(temp_image_file.name, signature_x, signature_y + 50, width=300, height=120)
        
        # 繪製簽名信息
        c.setFont("Helvetica", 12)
        c.drawString(signature_x, signature_y + 20, f"簽名者: {signature_info.get('name', '')}")
        
        if signature_info.get('title'):
            c.drawString(signature_x, signature_y + 5, f"職位: {signature_info['title']}")
        
        c.drawString(signature_x, signature_y - 10, f"簽名時間: {signature_info.get('timestamp', '')}")
        
        if signature_info.get('reason'):
            # 處理長文本
            reason_text = signature_info['reason']
            if len(reason_text) > 50:
                reason_text = reason_text[:50] + "..."
            c.drawString(signature_x, signature_y - 25, f"簽名原因: {reason_text}")
        
        # 繪製簽名框
        c.rect(signature_x - 10, signature_y - 40, 320, 200)
        
        c.save()
        
        # 讀取生成的 PDF
        with open(temp_file.name, 'rb') as f:
            pdf_data = f.read()
        
        # 清理臨時文件
        os.unlink(temp_file.name)
        os.unlink(temp_image_file.name)
        
        return pdf_data
        
    except Exception as e:
        print(f"創建簽名頁面錯誤: {e}")
        # 清理臨時文件
        try:
            if 'temp_file' in locals():
                os.unlink(temp_file.name)
            if 'temp_image_file' in locals():
                os.unlink(temp_image_file.name)
        except:
            pass
        return None
