from flask import Flask, request, render_template
from model.segment import segment_3_parts
import json
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        speech = request.form['speech']
        extration_result = segment_3_parts(speech)
        return render_template('index.html', **extration_result)

@app.route('/extration/<speech>/', methods=['GET'])
def extration(speech):
    extration_result = segment_3_parts(speech)
    return json.dumps(extration_result, ensure_ascii=False)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=True)
