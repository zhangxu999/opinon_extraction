from flask import Flask, request, render_template
from model.get_speech import get_speech,test_doc

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
        speech = request.form['speech']
        finalize_method = request.form['inlineRadioOptions']
        print(finalize_method)
        extration_result = get_speech(speech,finalize_method)
        print(extration_result)
        return render_template('index_naive.html',\
            speech=extration_result,origin_text=speech,**{finalize_method:'checked'})


@app.route('/extration/<speech>/', methods=['GET'])
def extration(speech):
    extration_result = get_speech(speech)
    return json.dumps(extration_result, ensure_ascii=False)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
