import os
from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# กำหนดค่าเริ่มต้นสำหรับ Tesseract (ถ้าจำเป็น)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract' # สำหรับ macOS (ถ้าติดตั้งผ่าน Homebrew)
# pytesseract.pytesseract.tesseract_cmd = r'C:\ Program Files\Tesseract-OCR\tesseract.exe' # สำหรับ Windows

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    """แสดงหน้า HTML หลัก"""
    return render_template('index.html')

@app.route('/ocr', methods=['POST'])
def ocr_process():
    """รับไฟล์, ทำ OCR, และส่งผลลัพธ์กลับไป"""
    if 'file' not in request.files:
        return jsonify({'error': 'ไม่พบไฟล์ใน request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'ไม่ได้เลือกไฟล์'}), 400

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        try:
            extracted_text = ''
            file_extension = os.path.splitext(filepath)[1].lower()

            if file_extension == '.pdf':
                # แปลง PDF เป็นรูปภาพ
                images = convert_from_path(filepath)
                for i, image in enumerate(images):
                    # ใช้ pytesseract กับภาษาไทย (tha) และอังกฤษ (eng)
                    text = pytesseract.image_to_string(image, lang='tha+eng')
                    extracted_text += f'--- Page {i+1} ---\n{text}\n\n'
            
            elif file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']:
                # เปิดไฟล์รูปภาพ
                image = Image.open(filepath)
                # ใช้ pytesseract กับภาษาไทย (tha) และอังกฤษ (eng)
                extracted_text = pytesseract.image_to_string(image, lang='tha+eng')
            
            else:
                os.remove(filepath) # ลบไฟล์ที่ไม่รองรับ
                return jsonify({'error': f'ไฟล์นามสกุล {file_extension} ไม่รองรับ'}), 400

            os.remove(filepath) # ลบไฟล์หลังประมวลผลเสร็จ
            return jsonify({'text': extracted_text})

        except Exception as e:
            # หากเกิดข้อผิดพลาด ให้ลบไฟล์และแจ้ง error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'เกิดข้อผิดพลาดในการอัปโหลดไฟล์'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8088)
