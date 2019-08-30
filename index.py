from flask import Flask, request, render_template
from model.get_speech import get_speech,test_doc
from utils import create_a_log,write_a_log,close_a_log
import json
app = Flask(__name__, static_url_path="")


# def get_speech(para):
#     return [('先生', '说', '说过这是一件重要的事情。'),
#             ('她', '表示', '表示，这次升旗礼是特别为香港加油而举行的，希望大家都懂得尊重自己的国家。'),
#             ('蒋靖轩', '认为', '认为，近日香港发生连串')
#             ]


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index_naive.html',origin_text=test_doc,select_tfidf='checked')
    else:
        create_a_log()
        print(request.form)
        speech = request.form['speech']
        finalize_method = request.form['inlineRadioOptions']
        print(finalize_method)
        write_a_log('index','speech',speech)
        write_a_log('index','speech',finalize_method)
        if finalize_method == 'select_tfidf':
            alpha = float(request.form['tfidf_alpha'])
        else:
            alpha = float(request.form['Word2vc_alpha'])
        write_a_log('index','alpha',alpha)
        extration_result = get_speech(speech,finalize_method, alpha)
        print(extration_result)
        write_a_log('index','extration_result',extration_result)
        close_a_log()
        return render_template('index_naive.html',\
            speech=extration_result,origin_text=speech,**{finalize_method:'checked'},alpha=alpha)

@app.route('/my_page', methods=['GET', 'POST'])
def my_page_func():
    if request.method == 'GET':
        return render_template('charts.html',origin_text=test_doc)
    else:
        print(request.form)
        speech = request.form['speech']
        extration_result = get_speech(speech,'select_tfidf', 0.2)
        print(extration_result)

        return render_template('charts.html',\
            speech=extration_result,origin_text=speech)


@app.route('/extration/<speech>/', methods=['GET'])
def extration(speech):
    extration_result = get_speech(speech)
    return json.dumps(extration_result, ensure_ascii=False)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
