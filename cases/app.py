from flask import Flask, render_template, request, abort
from datetime import timedelta
import os
import re


app = Flask(__name__, template_folder='templates')
app.secret_key = b'abcad#sdf!53'
app.permanent_session_lifetime = timedelta(60 * 60)
UPLOAD_FOLDER = '案件'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
PATTERN = r'^\（\d{4}\）[A-Za-z\u4e00-\u9fa50-9]+号$'

blocked_ips = [
    '211.143.51.116'
]

@app.before_request
def check_ip():
    # 获取请求的客户端 IP 地址
    client_ip = request.remote_addr
    # 如果 IP 在禁止列表中，则返回 403 禁止访问
    if client_ip in blocked_ips:
        abort(403)  # 返回 403 Forbidden

def save_file(file, category):
    if file.filename == '' or not re.match(PATTERN, file.filename.strip('.txt')):
        return False
    category_folder = os.path.join(app.config['UPLOAD_FOLDER'], category)
    os.makedirs(category_folder, exist_ok=True)
    file.save(os.path.join(category_folder, file.filename))
    return True

def save_text(content, category, filename):
    if not content or not re.match(PATTERN, filename):
        return False
    filename =  f"{filename}.txt"
    category_folder = os.path.join(app.config['UPLOAD_FOLDER'], category)
    os.makedirs(category_folder, exist_ok=True)
    
    filepath = os.path.join(category_folder, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"保存文本文件失败：{str(e)}")
        return False

def get_uploaded_case_numbers(case):
    case_folder = os.path.join(UPLOAD_FOLDER, case)
    if not os.path.exists(case_folder):
        return []

    # 列出文件夹中所有的案号文件
    case_files = os.listdir(case_folder)
    case_numbers = [f.split('.')[0] for f in case_files if f.endswith('.txt')]
    return case_numbers

@app.route('/<int:i>', methods=['GET', 'POST'])
def upload_files(i):
    message = []
    cases = ['确认合同效力', '缔约过失', '典型合同', '侵权', '劳动与人事', '物权', '婚姻家庭'][i: i + 1]
    if request.method == 'POST':
        for case in cases:
            if case in request.files:
                civil_file = request.files[case]
                if civil_file.filename != '' and civil_file.filename.endswith('.txt'):
                    if save_file(civil_file, case):
                        message.append(f"{civil_file.filename}文件上传成功")
            # 处理案号文本
            case_number = request.form.get(f"{case}_case_number")
            case_content = request.form.get(f"{case}_content")
            if case_number and case_content:
                if save_text(case_content, case, f"{case_number.strip()}"):
                    message.append(f"{case_number}文件上传成功")
        if not message:
            s = civil_file.filename if civil_file else case_number
            message.append("文件上传失败：" + s)
    
    return render_template(
        'index.html', 
        message=message, 
        cases=cases, 
        uploaded=get_uploaded_case_numbers(cases[0])
    )

@app.route('/all', methods=['GET', 'POST'])
def all_():
    cases = ['确认合同效力', '缔约过失', '典型合同', '侵权', '劳动与人事', '物权', '婚姻家庭']
    r = {}
    for case in cases:
        t = get_uploaded_case_numbers(case)
        r[case] = len(t)
    return f"<h1>{r}</h1><h1>共{sum(r.values())}份</h1>"

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=123,
        debug=True
    )
