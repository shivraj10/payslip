from crypt import methods
from flask import Flask,render_template,request,redirect,flash, send_file
from werkzeug.utils import secure_filename
import os
from pdf2image import convert_from_path
import easyocr
import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import json
import io


    
app = Flask(__name__)
app.secret_key = "super secret key"
UPLOAD_FOLDER = '/Users/shivraj/payslip/upload/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DOWNLOAD_FOLDER = '/Users/shivraj/payslip/json'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
EXTENSIONS = {'pdf', 'png', 'jpg'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS

@app.route('/',methods=['GET','POST'])
def index():
    if request.method=='POST':
        file = request.files['file']
        if file.filename == '':
            flash('No file selected','error')
            return render_template('index.html')
        if not allowed_file(file.filename):
            flash('Please upload the file in image or pdf format','error')
            #print(1)
            #print(request.files['file'].filename)
            return render_template('index.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(1)
            if filename[-3:]=='pdf' or filename[-3:]=='PDF':
                print(2)
                i=convert_from_path(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                path1=app.config['UPLOAD_FOLDER']+'/'+filename[:-3]+'jpg'
                for j in i:
                    print(3)
                    j.save(path1)
                reader = easyocr.Reader(['en']) 
                result = reader.readtext(path1,detail=0)
                line=''
                for res in result:
                    line=line+' '+res
                #print(line)
            else:
                reader = easyocr.Reader(['en']) 
                result = reader.readtext(os.path.join(app.config['UPLOAD_FOLDER'], filename),detail=0)
                line=''
                for res in result:
                    line=line+' '+res
            nlp_ner = spacy.load("/Users/shivraj/payslip/model/model-best")
            doc = nlp_ner(line)
            dict={}
            for i in doc.ents:
                dict[i.label_]=i.text
            with open(os.path.join(app.config['DOWNLOAD_FOLDER'], filename.rsplit('.', 1)[0]+'.json'), "w") as outfile:
                json.dump(dict, outfile)
                FILENAME =  filename.rsplit('.', 1)[0]+'.json'
                app.config['FILENAME'] = FILENAME
            flash('You can download your json file now','download')
            return redirect('/')
    else:
        return render_template('index.html')

@app.route('/download',methods=['GET', 'POST'])
def download():
    return send_file(app.config['DOWNLOAD_FOLDER']+'/'+app.config['FILENAME'],as_attachment=True)
    
if __name__ == "__main__":
    app.debug = True
    app.run()

