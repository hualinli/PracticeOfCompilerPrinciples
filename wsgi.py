import os
from flask import Flask, redirect, render_template, request, send_file, url_for
from lab1.lexer import lexer
from lab2.parser import parser
from lab3.codegenerate import *
app = Flask(__name__)


UPLOAD_DIR = 'uploads/'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
OUTPUT_DIR = 'output/'
app.config['UPLOAD_DIR'] = UPLOAD_DIR

def read_code(file_path):
    """
    读取代码文件,添加行号
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    numbered_lines = ['{}.{}'.format(i+1, line) for i, line in enumerate(lines)]
    return '\n'.join(numbered_lines)

def read_tokens(file_path):
    """
    读取tokens文件
    """
    with open(file_path, 'r') as f:
        tokens = f.read().splitlines()
    return tokens

def read_symbols(file_path):
    """
    读取symbols文件
    """
    with open(file_path, 'r') as f:
        symbols = f.read().splitlines()
    return symbols


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/delete_files', methods=['POST'])
def delete_files():
    # Delete all files in the uploads and outputs directories
    for dir_path in [UPLOAD_DIR, OUTPUT_DIR]:
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            os.remove(file_path)
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)



@app.route('/lab1', methods=['GET', 'POST'])
def lab1():
    if request.method == 'POST':
        # 获取用户上传的文件
        code_file = request.files['code_file']
        # 保存文件到upload目录
        code_file.save(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        source_code = read_code(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        # 处理代码文件,生成tokens和symbols文件
        tokens_file, symbols_file = lexer(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        
        # 读取tokens和symbols文件
        tokens = read_tokens(tokens_file)
        symbols = read_symbols(symbols_file)
        
        # 渲染模板,显示代码和结果
        return render_template('lab1.html', code=source_code, tokens=tokens, symbols=symbols)
    return render_template('lab1.html')


@app.route('/lab2', methods=['GET', 'POST'])
def lab2():
    source_codes = None
    tokens = None
    behaviors = None
    symbols = None
    errors = None
    if request.method == 'POST':
        code_file = request.files['code_file']
        code_file.save(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        parser(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        source_codes = read_code(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        tokens = read_tokens(os.path.join(OUTPUT_DIR, 'tokens.txt'))
        behaviors = read_tokens(os.path.join(OUTPUT_DIR, 'behavior.txt'))
        symbols = read_tokens(os.path.join(OUTPUT_DIR, 'output.txt'))
        errors = read_tokens(os.path.join(OUTPUT_DIR, 'error.txt'))
    return render_template('lab2.html', code=source_codes, tokens=tokens, behavior=behaviors, symbol_stack=symbols, error=errors)

@app.route('/lab3', methods=['GET', 'POST'])
def lab3():
    source_code = None
    codes = None
    result = None
    if request.method == 'POST':
        code_file = request.files['code_file']
        code_file.save(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        source_code = read_code(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        scanner = LexicalScanner(os.path.join(app.config['UPLOAD_DIR'], code_file.filename))
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze_grammar(scanner.lexical_analysis())
        codes = analyzer.output_code()
        with open(os.path.join(OUTPUT_DIR, 'code.txt'), 'w') as f:
            f.write(codes)
    return render_template('lab3.html', code=source_code, result_codes=codes.split('\n'), result=result)

if __name__ == '__main__':
    app.run(debug=True)