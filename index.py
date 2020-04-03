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
test_doc = """
新华社香港8月11日电 香港升旗队总会11日在新界元朗一家中学举行“家在中华”升旗礼，吸引多名市民参与。

习近平先生也说过这是一件重要的事情。

正午时分，艳阳高照。由香港多家中学组成的升旗队伍，护送国旗到学校操场的旗杆下。五星红旗伴随着国歌冉冉升起，气氛庄严。
香港升旗队总会主席周世耀在国旗下致辞时表示，最近香港发生很多不愉快的事件，包括部分人侮辱国旗国徽、挑战“一国两制”原则底线，也分化了香港和内地的同胞。希望通过当天举行升旗活动弘扬正能量，并传递一个重要讯息：香港属于中华民族大家庭。

香港升旗队总会总监许振隆勉励年轻人说，要关心社会，关心国家，希望年轻人以国为荣，为国争光。
活动接近尾声，参与者在中国地图上贴上中国国旗，象征大家共同努力建设国家。最后，全体人员合唱《明天会更好》，为香港送上美好祝愿。

今年15岁的郭紫晴在香港土生土长。她表示，这次升旗礼是特别为香港加油而举行的，希望大家都懂得尊重自己的国家。“看着国旗升起，想到自己在中国这片土地上成长，感到十分自豪。”
“升旗仪式(与以往)一样，但意义却不同。”作为当天升旗队成员之一的高中生赵颖贤说，国旗和国徽代表了一个国家的尊严，不容践踏，很期望当天的活动能向广大市民传达这一信息。

即将升读初三的蒋靖轩认为，近日香港发生连串暴力事件，当天的升旗仪式更显意义，希望香港快快恢复平静，港人都团结起来。

"""

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
