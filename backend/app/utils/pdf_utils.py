import os
import base64
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import tempfile
import logging
import traceback
from PyPDF2.errors import PdfReadError, PdfReadWarning
from contextlib import suppress

logger = logging.getLogger(__name__)

# 統一的簽名位置和大小標準
SIGNATURE_CONFIG = {
    'width': 200,           # 簽名圖像寬度
    'height': 80,           # 簽名圖像高度  
    'margin_right': 30,     # 距離右邊的間距
    'margin_bottom': 40,    # 距離底部的間距
    'font_size': 11,         # 簽名信息字體大小
    'line_spacing': 20      # 簽名信息行間距
}

def calculate_signature_position(page_width, page_height=None):
    """
    計算統一的簽名位置
    Args:
        page_width: 頁面寬度
        page_height: 頁面高度（可選，用於fallback PDF）
    Returns:
        tuple: (signature_x, signature_y)
    """
    signature_x = page_width - SIGNATURE_CONFIG['width'] - SIGNATURE_CONFIG['margin_right']
    signature_y = SIGNATURE_CONFIG['margin_bottom']
    return signature_x, signature_y

def validate_pdf_file(pdf_path: str) -> bool:
    """
    驗證 PDF 文件是否有效
    """
    try:
        with open(pdf_path, 'rb') as f:
            # 檢查文件頭
            header = f.read(8)
            if not header.startswith(b'%PDF-'):
                logger.error(f"Invalid PDF header in file: {pdf_path}")
                return False
            
            # 檢查文件尾部是否包含 %%EOF
            f.seek(-1024, 2)  # 從文件尾部向前讀取1024字節
            tail = f.read()
            if b'%%EOF' not in tail:
                logger.warning(f"PDF file may be incomplete (no %%EOF): {pdf_path}")
                # 不直接返回 False，因為有些 PDF 可能沒有標準結尾
            
        return True
    except Exception as e:
        logger.error(f"Error validating PDF file {pdf_path}: {e}")
        return False

def read_pdf_safely(pdf_path: str):
    """
    安全地讀取 PDF 文件，使用多種策略處理損壞的 PDF
    """
    logger.info(f"Attempting to read PDF: {pdf_path}")
    
    # 策略 1: 正常讀取
    try:
        reader = PdfReader(pdf_path)
        logger.info(f"Successfully read PDF with {len(reader.pages)} pages")
        return reader
    except PdfReadError as e:
        logger.warning(f"PyPDF2 read error: {e}")
        
    # 策略 2: 忽略警告的嚴格模式讀取
    try:
        reader = PdfReader(pdf_path, strict=False)
        logger.info(f"Successfully read PDF in non-strict mode with {len(reader.pages)} pages")
        return reader
    except Exception as e:
        logger.warning(f"Non-strict mode also failed: {e}")
    
    # 策略 3: 嘗試修復 PDF
    try:
        repaired_path = repair_pdf(pdf_path)
        if repaired_path:
            reader = PdfReader(repaired_path)
            logger.info(f"Successfully read repaired PDF with {len(reader.pages)} pages")
            return reader
    except Exception as e:
        logger.warning(f"Repaired PDF reading failed: {e}")
    
    # 所有策略都失敗
    logger.error(f"All PDF reading strategies failed for: {pdf_path}")
    raise PdfReadError(f"Cannot read PDF file: {pdf_path}")

def repair_pdf(pdf_path: str) -> str:
    """
    嘗試修復損壞的 PDF 文件
    """
    try:
        # 創建修復後的文件路徑
        repaired_path = pdf_path.replace('.pdf', '_repaired.pdf')
        
        # 讀取原始文件內容
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        # 基本修復：確保以 %%EOF 結尾
        if not content.endswith(b'%%EOF\n'):
            if not content.endswith(b'%%EOF'):
                content += b'\n%%EOF\n'
            else:
                content += b'\n'
        
        # 寫入修復後的文件
        with open(repaired_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Created repaired PDF: {repaired_path}")
        return repaired_path
        
    except Exception as e:
        logger.error(f"PDF repair failed: {e}")
        return None

def create_signature_only_pdf(signature_image_data: str, signature_info: dict, output_path: str, original_filename: str = ""):
    """
    當原始 PDF 無法讀取時，創建一個只包含簽名的新 PDF
    """
    try:
        logger.info(f"Creating signature-only PDF: {output_path}")
        
        # 創建新的 PDF 文件
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # 解析簽名圖像數據
        if signature_image_data.startswith('data:image'):
            signature_image_data = signature_image_data.split(',')[1]
        
        # 解碼 Base64 圖像
        image_data = base64.b64decode(signature_image_data)
        image = Image.open(BytesIO(image_data))
        
        # 使用統一的簽名標準調整圖像大小
        image.thumbnail((SIGNATURE_CONFIG['width'], SIGNATURE_CONFIG['height']), Image.Resampling.LANCZOS)
        
        # 保存調整後的圖像到臨時文件
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image_file.name, 'PNG')
        temp_image_file.close()
        
        # 頁面布局
        title_y = height - 100
        content_y = height - 200
        
        # 繪製標題
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, title_y, "電子簽名文件")
        
        # 繪製說明文字
        c.setFont("Helvetica", 12)
        c.drawString(50, content_y, f"原始文件: {original_filename}")
        c.drawString(50, content_y - 20, "注意: 原始 PDF 文件無法正常處理，此為僅包含簽名信息的新文件。")
        c.drawString(50, content_y - 40, "如需完整內容，請聯繫系統管理員。")
        
        # 使用統一的簽名位置計算
        signature_x, signature_y = calculate_signature_position(width, height)
        
        # 繪製簽名圖像 - 統一位置和大小
        c.drawImage(temp_image_file.name, signature_x, signature_y, 
                   width=SIGNATURE_CONFIG['width'], height=SIGNATURE_CONFIG['height'])
        
        # 繪製簽名信息 - 統一字體和間距
        info_y = signature_y - SIGNATURE_CONFIG['line_spacing']
        c.setFont("Helvetica", SIGNATURE_CONFIG['font_size'])
        c.drawString(signature_x, info_y, f"Signer: {signature_info.get('name', '')}")
        
        info_y -= SIGNATURE_CONFIG['line_spacing']
        c.drawString(signature_x, info_y, f"Signature Time: {signature_info.get('timestamp', '')}")
        
        # 移除邊框，保持簡潔外觀
        
        c.save()
        
        # 清理臨時文件
        os.unlink(temp_image_file.name)
        
        logger.info(f"Successfully created signature-only PDF: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating signature-only PDF: {e}")
        return False

def extract_pdf_raw_content(pdf_path: str):
    """
    從損壞的PDF文件中提取原始內容
    """
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read()
        
        # 嘗試提取可讀文本
        text_content = []
        
        # 尋找文本對象
        import re
        
        # PDF文本對象通常以 'BT' 開始，'ET' 結束
        text_objects = re.findall(rb'BT\s*(.+?)\s*ET', content, re.DOTALL)
        
        for text_obj in text_objects:
            try:
                # 嘗試解碼文本對象中的可讀部分
                text_str = text_obj.decode('latin1', errors='ignore')
                # 提取Tj操作符中的文本
                text_matches = re.findall(r'\(([^)]+)\)\s*Tj', text_str)
                text_content.extend(text_matches)
            except:
                continue
        
        # 嘗試找到文件基本信息
        info = {
            'extracted_text': '\n'.join(text_content[:20]) if text_content else '無法提取文本內容',
            'file_size': len(content),
            'has_pdf_header': content.startswith(b'%PDF-'),
            'pdf_version': content[:8].decode('ascii', errors='ignore') if content.startswith(b'%PDF-') else 'Unknown'
        }
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to extract raw PDF content: {e}")
        return None

def create_enhanced_fallback_pdf(signature_image_data: str, signature_info: dict, output_path: str, original_pdf_path: str):
    """
    創建增強的fallback PDF，包含更多原始文件信息
    """
    try:
        logger.info(f"Creating enhanced fallback PDF: {output_path}")
        
        # 嘗試提取原始PDF的內容
        raw_content = extract_pdf_raw_content(original_pdf_path)
        original_filename = os.path.basename(original_pdf_path)
        
        # 創建新的PDF文件
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # 解析簽名圖像數據
        if signature_image_data.startswith('data:image'):
            signature_image_data = signature_image_data.split(',')[1]
        
        # 解碼Base64圖像
        image_data = base64.b64decode(signature_image_data)
        image = Image.open(BytesIO(image_data))
        
        # 使用統一的簽名標準調整圖像大小
        image.thumbnail((SIGNATURE_CONFIG['width'], SIGNATURE_CONFIG['height']), Image.Resampling.LANCZOS)
        
        # 保存調整後的圖像到臨時文件
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image_file.name, 'PNG')
        temp_image_file.close()
        
        # 頁面布局
        current_y = height - 50
        
        # 標題
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, current_y, "電子簽名文件")
        current_y -= 40
        
        # 原始文件信息
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, current_y, "原始文件信息:")
        current_y -= 25
        
        c.setFont("Helvetica", 12)
        c.drawString(70, current_y, f"文件名稱: {original_filename}")
        current_y -= 20
        
        if raw_content:
            c.drawString(70, current_y, f"文件大小: {raw_content['file_size']:,} bytes")
            current_y -= 20
            c.drawString(70, current_y, f"PDF版本: {raw_content['pdf_version']}")
            current_y -= 20
            
            # 顯示提取的文本（如果有）
            if raw_content['extracted_text'] and raw_content['extracted_text'] != '無法提取文本內容':
                c.drawString(70, current_y, "部分提取內容:")
                current_y -= 20
                
                # 將長文本分行顯示
                text_lines = raw_content['extracted_text'][:300].split('\n')
                for line in text_lines[:5]:  # 最多顯示5行
                    if line.strip():
                        c.drawString(90, current_y, line.strip()[:60] + ('...' if len(line.strip()) > 60 else ''))
                        current_y -= 15
        
        current_y -= 20
        
        # 問題說明
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0.8, 0, 0)  # 紅色文字
        c.drawString(50, current_y, "注意事項:")
        current_y -= 20
        
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0, 0, 0)  # 黑色文字
        c.drawString(70, current_y, "• 原始PDF文件存在結構性損壞，無法正常處理")
        current_y -= 15
        c.drawString(70, current_y, "• 系統已盡可能提取原始文件中的可用信息")
        current_y -= 15
        c.drawString(70, current_y, "• 此文件包含完整的電子簽名信息")
        current_y -= 15
        c.drawString(70, current_y, "• 如需完整內容，請聯繫系統管理員重新處理原始文件")
        
        # 使用統一的簽名位置計算
        signature_x, signature_y = calculate_signature_position(width, height)
        
        # 簽名標題
        c.setFont("Helvetica-Bold", 12)
        c.setFillColorRGB(0, 0, 0)
        c.drawString(signature_x, signature_y + SIGNATURE_CONFIG['height'] + 10, "電子簽名")
        
        # 繪製簽名圖像 - 統一位置和大小
        c.drawImage(temp_image_file.name, signature_x, signature_y, 
                   width=SIGNATURE_CONFIG['width'], height=SIGNATURE_CONFIG['height'], mask='auto')
        
        # 繪製簽名信息 - 統一字體和間距
        info_y = signature_y - SIGNATURE_CONFIG['line_spacing']
        c.setFont("Helvetica", SIGNATURE_CONFIG['font_size'])
        c.drawString(signature_x, info_y, f"Signer: {signature_info.get('name', '')}")
        
        info_y -= SIGNATURE_CONFIG['line_spacing']
        c.drawString(signature_x, info_y, f"Signature Time: {signature_info.get('timestamp', '')}")
        
        # 移除所有邊框，保持簡潔外觀
        
        c.save()
        
        # 清理臨時文件
        os.unlink(temp_image_file.name)
        
        logger.info(f"Successfully created enhanced fallback PDF: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating enhanced fallback PDF: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

def create_repaired_pdf_reader(pdf_path: str):
    """
    使用更寬鬆的策略創建PDF讀取器，專門處理有問題的PDF文件
    """
    logger.info(f"Attempting to create repaired PDF reader for: {pdf_path}")
    
    try:
        # 策略1: 使用PyPDF2的忽略錯誤模式
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reader = PdfReader(pdf_path, strict=False)
            # 嘗試訪問頁面來驗證可用性
            _ = len(reader.pages)
            if len(reader.pages) > 0:
                logger.info(f"Strategy 1 successful: loaded {len(reader.pages)} pages")
                return reader
    except Exception as e:
        logger.warning(f"Strategy 1 failed: {e}")
    
    try:
        # 策略2: 讀取原始數據並嘗試修復
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        
        # 基本修復：確保有EOF標記
        if not pdf_data.endswith(b'%%EOF\n'):
            if not pdf_data.endswith(b'%%EOF'):
                pdf_data += b'\n%%EOF\n'
            else:
                pdf_data += b'\n'
        
        # 寫入臨時修復文件
        temp_repaired = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_repaired.write(pdf_data)
        temp_repaired.close()
        
        # 嘗試讀取修復後的文件
        reader = PdfReader(temp_repaired.name, strict=False)
        _ = len(reader.pages)
        if len(reader.pages) > 0:
            logger.info(f"Strategy 2 successful: repaired and loaded {len(reader.pages)} pages")
            return reader
            
    except Exception as e:
        logger.warning(f"Strategy 2 failed: {e}")
    
    try:
        # 策略3: 嘗試跳過損壞的部分
        with open(pdf_path, 'rb') as f:
            # 讀取文件並嘗試找到有效的PDF內容
            content = f.read()
            
        # 尋找PDF對象的開始
        pdf_start = content.find(b'%PDF-')
        if pdf_start == -1:
            raise Exception("No PDF header found")
            
        # 從PDF開始處創建新內容
        clean_content = content[pdf_start:]
        
        # 創建臨時清理文件
        temp_clean = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_clean.write(clean_content)
        temp_clean.close()
        
        reader = PdfReader(temp_clean.name, strict=False)
        _ = len(reader.pages)
        if len(reader.pages) > 0:
            logger.info(f"Strategy 3 successful: cleaned and loaded {len(reader.pages)} pages")
            return reader
            
    except Exception as e:
        logger.warning(f"Strategy 3 failed: {e}")
    
    # 如果所有策略都失敗，拋出異常
    raise PdfReadError(f"All repair strategies failed for PDF: {pdf_path}")

def analyze_pdf_structure(pdf_path: str):
    """
    分析 PDF 文件結構，提供更詳細的診斷信息
    """
    try:
        with open(pdf_path, 'rb') as f:
            content = f.read(2048)  # 讀取前 2KB
            
        logger.info(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
        logger.info(f"PDF header: {content[:50]}")
        
        # 檢查是否包含標準 PDF 元素
        has_xref = b'xref' in content
        has_trailer = b'trailer' in content
        has_startxref = b'startxref' in content
        
        logger.info(f"Has xref table: {has_xref}")
        logger.info(f"Has trailer: {has_trailer}")  
        logger.info(f"Has startxref: {has_startxref}")
        
        # 尋找 PDF 版本
        if content.startswith(b'%PDF-'):
            version_line = content[:20].decode('ascii', errors='ignore')
            logger.info(f"PDF version: {version_line}")
        else:
            logger.warning("File does not start with PDF header")
            
        return {
            'has_xref': has_xref,
            'has_trailer': has_trailer,
            'has_startxref': has_startxref,
            'file_size': os.path.getsize(pdf_path)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing PDF structure: {e}")
        return None

def add_signature_to_pdf(original_pdf_path: str, signature_image_data: str, signature_info: dict, output_path: str):
    """
    將簽名以透明背景的方式合成到PDF文件的最後一頁
    
    Args:
        original_pdf_path: 原始 PDF 文件路徑
        signature_image_data: Base64 編碼的簽名圖像數據
        signature_info: 簽名信息字典，包含 name, title, reason, timestamp
        output_path: 輸出文件路徑
    """
    temp_file = None
    temp_image_file = None
    repaired_pdf_path = None
    
    try:
        logger.info(f"Starting PDF signature process for: {original_pdf_path}")
        
        # 分析 PDF 文件結構（僅用於診斷，不決定是否失敗）
        pdf_analysis = analyze_pdf_structure(original_pdf_path)
        
        # 嘗試讀取原始 PDF（主要策略）
        reader = None
        writer = None
        
        try:
            # 首先嘗試安全讀取
            reader = read_pdf_safely(original_pdf_path)
            writer = PdfWriter()
            logger.info(f"Successfully loaded PDF with {len(reader.pages)} pages")
            
        except Exception as read_error:
            logger.error(f"Failed to read PDF normally: {read_error}")
            
            # 嘗試更寬鬆的讀取策略
            try:
                logger.info("Attempting alternative PDF processing...")
                reader = create_repaired_pdf_reader(original_pdf_path)
                writer = PdfWriter()
                logger.info(f"Successfully loaded PDF using alternative method with {len(reader.pages)} pages")
                
            except Exception as alt_error:
                logger.error(f"Alternative PDF processing also failed: {alt_error}")
                logger.info("Using enhanced fallback strategy - extracting available content")
                
                # 只有在所有策略都失敗時才使用增強的 fallback
                logger.info("All PDF repair strategies failed, using enhanced fallback")
                return create_enhanced_fallback_pdf(
                    signature_image_data=signature_image_data,
                    signature_info=signature_info,
                    output_path=output_path,
                    original_pdf_path=original_pdf_path
                )
        
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
        
        # 使用統一的簽名標準調整圖像大小
        image.thumbnail((SIGNATURE_CONFIG['width'], SIGNATURE_CONFIG['height']), Image.Resampling.LANCZOS)
        
        # 保存調整後的圖像到臨時文件（保持透明度）
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image_file.name, 'PNG')
        temp_image_file.close()
        
        # 使用統一的簽名位置計算
        signature_x, signature_y = calculate_signature_position(page_width, page_height)
        
        # 繪製簽名圖像（保持透明度）- 統一大小
        c.drawImage(temp_image_file.name, signature_x, signature_y, 
                   width=SIGNATURE_CONFIG['width'], height=SIGNATURE_CONFIG['height'], mask='auto')
        
        # 繪製簽名信息（使用半透明文字）- 統一字體和間距
        c.setFillColorRGB(0, 0, 0, 0.8)  # 半透明黑色文字
        c.setFont("Helvetica", SIGNATURE_CONFIG['font_size'])
        
        info_y = signature_y - SIGNATURE_CONFIG['line_spacing']
        c.drawString(signature_x, info_y, f"Signer: {signature_info.get('name', '')}")
        
        info_y -= SIGNATURE_CONFIG['line_spacing']
        c.drawString(signature_x, info_y, f"Signature Time: {signature_info.get('timestamp', '')}")
        
        
        c.save()
        
        # 讀取簽名頁面
        signature_reader = PdfReader(temp_file.name)
        signature_page = signature_reader.pages[0]
        
        # 將簽名頁面合併到最後一頁（透明合成）
        last_page.merge_page(signature_page)
        
        # 保留完整的多頁PDF內容並添加電子簽名
        total_pages = len(reader.pages)
        logger.info(f"Processing {total_pages} page(s) PDF")
        
        if total_pages == 1:
            # 單頁PDF：直接添加已簽名的頁面
            logger.info("Single page PDF: adding signed page")
            writer.add_page(last_page)
        else:
            # 多頁PDF：保留所有前面的頁面，最後一頁添加簽名
            logger.info(f"Multi-page PDF: preserving {total_pages - 1} original pages + 1 signed page")
            
            # 添加除最後一頁外的所有原始頁面
            for page_num in range(total_pages - 1):
                writer.add_page(reader.pages[page_num])
                logger.debug(f"Added original page {page_num + 1}")
            
            # 添加帶簽名的最後一頁
            writer.add_page(last_page)
            logger.info(f"Added signed final page ({total_pages})")
        
        # 寫入輸出文件
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        # 清理臨時文件
        cleanup_temp_files(temp_file, temp_image_file, repaired_pdf_path)
        
        logger.info(f"Successfully created signed PDF: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"PDF 簽名處理錯誤: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # 清理臨時文件
        cleanup_temp_files(temp_file, temp_image_file, repaired_pdf_path)
        return False

def get_pdf_content_for_fallback(original_pdf_path: str):
    """
    嘗試從損壞的PDF中提取一些基本信息用於fallback
    """
    try:
        file_size = os.path.getsize(original_pdf_path)
        with open(original_pdf_path, 'rb') as f:
            header = f.read(50)
        
        info = {
            'file_size': file_size,
            'header': header[:20].decode('ascii', errors='ignore') if header else 'Unknown',
            'filename': os.path.basename(original_pdf_path)
        }
        
        return info
    except Exception as e:
        logger.error(f"Failed to extract PDF info: {e}")
        return {'filename': os.path.basename(original_pdf_path)}

def cleanup_temp_files(*file_paths):
    """
    清理臨時文件
    """
    for file_path in file_paths:
        if file_path:
            try:
                if hasattr(file_path, 'name'):
                    os.unlink(file_path.name)
                elif isinstance(file_path, str) and os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup file {file_path}: {e}")

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
        
        # 使用統一的簽名標準調整圖像大小
        image.thumbnail((SIGNATURE_CONFIG['width'], SIGNATURE_CONFIG['height']), Image.Resampling.LANCZOS)
        
        # 保存調整後的圖像到臨時文件
        temp_image_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_image_file.name, 'PNG')
        temp_image_file.close()
        
        # 使用統一的簽名位置計算
        signature_x, signature_y = calculate_signature_position(width, height)
        
        # 繪製標題
        c.setFont("Helvetica-Bold", 16)
        c.drawString(signature_x, signature_y + SIGNATURE_CONFIG['height'] + 20, "電子簽名")
        
        # 繪製簽名圖像 - 統一位置和大小
        c.drawImage(temp_image_file.name, signature_x, signature_y, 
                   width=SIGNATURE_CONFIG['width'], height=SIGNATURE_CONFIG['height'])
        
        # 繪製簽名信息 - 統一字體和間距
        info_y = signature_y - SIGNATURE_CONFIG['line_spacing']
        c.setFont("Helvetica", SIGNATURE_CONFIG['font_size'])
        c.drawString(signature_x, info_y, f"Signer: {signature_info.get('name', '')}")
        
        info_y -= SIGNATURE_CONFIG['line_spacing']
        c.drawString(signature_x, info_y, f"Signature Time: {signature_info.get('timestamp', '')}")
        
        # 移除簽名框，保持簡潔外觀
        
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
