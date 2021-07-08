# -*- coding: utf-8 -*-

# 2021.07.08
# Python 3.6.8 / centos7.4
# API V4r2で動作確認
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
# ログインして属性取得、可能額取得、注文一覧の取得、現物保有株一覧の取得、信用建玉一覧の取得、ログアウトします。

import urllib3
import datetime
import json
import time

# システム時刻を"p_sd_date"の書式の文字列で返す。
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# request項目を保存するクラス。配列として使う。
# 'p_no'、'p_sd_date'は格納せず、func_make_url_requestで生成する。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_cust_property:
    def __init__(self):
        self.sUrlRequest = ''     # request用仮想URL
        self.sUrlEvent = ''         # event用仮想URL
        self.sZyoutoekiKazeiC = ''          # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = ''    # 22.第二パスワード  APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        
    def set_property(self, my_sUrlRequest, my_sUrlEvent, my_sZyoutoekiKazeiC, my_sSecondPassword):
        self.sUrlRequest = my_sUrlRequest     # request用仮想URL
        self.sUrlEvent = my_sUrlEvent         # event用仮想URL
        self.sZyoutoekiKazeiC = my_sZyoutoekiKazeiC          # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
        self.sSecondPassword = my_sSecondPassword    # 22.第二パスワード    APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照



# request文字列を作成し返す。
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された'sUrlRequest'の値（仮想url）をセット。
# 第３引数： requestを投げるとき1カウントアップする。参照渡しで値を引き継ぐため、配列として受け取る。
# 第４引数： 'p_no'、'p_sd_date'以外の要求項目がセットされている必要がある。クラスの配列として受取る。
def func_make_url_request(auth_flg, url_target, int_p_no, work_class_req) :
    int_p_no[0] += 1
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得
    
    work_url = url_target
    if auth_flg == True :
        work_url = work_url + 'auth/'
    
    work_url = work_url + '?{\n\t'
    work_url = work_url + '"p_no":' + func_check_json_dquat(str(int_p_no[0])) + ',\n\t'
    work_url = work_url + '"p_sd_date":' + func_check_json_dquat(str_p_sd_date) + ',\n\t'
    
    for i in range(len(work_class_req)) :
        if len(work_class_req[i].str_key) > 0:
            work_url = work_url + work_class_req[i].str_key + ':' + work_class_req[i].str_value + ',\n\t'
        
    work_url = work_url[:-3] + '\n}'
    return work_url


# APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第２引数： ログインは、APIのurlをセット。それ以外はログインで返された'sUrlRequest'の値（仮想url）をセット。
# 第３引数： requestを投げるときは、1カウントアップする（func_make_url_request関数内で実行）。参照渡しで値を引き継ぐため、配列として受け取る。
# 第４引数： 'p_no'、'p_sd_date'以外の要求項目がセットされている必要がある。クラスの配列として受取る。
def func_api_req(auth_flg, url_target, int_p_no, work_class_req):
    work_url = func_make_url_request(auth_flg, url_target, int_p_no, work_class_req)  # ログインは第１引数にTrueをセット
    print('送信文字列＝')
    print(work_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', work_url)
    print("req.status= ", req.status )

    # 取得したデータがbytes型なので、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req



# ログイン関数
# 引数：アクセスするurl（'auth/'以下は付けない）、ユーザーID、パスワード、int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_login(url_base, my_userid, my_passwd, int_p_no):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。
    req_item = [class_req()]   
    
    str_key = '"sCLMID"'
    str_value = 'CLMAuthLoginRequest'
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sUserId"'
    str_value = my_userid
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sPassword"'
    str_value = my_passwd
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # ログインとログイン後の電文が違うため、第１引数で指示。
    # ログインはTrue。それ以外はFalse。
    # このプログラムでの仕様。APIの仕様ではない。
    json_return = func_api_req(True, url_base, int_p_no, req_item)  
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

    return json_return



# 可能額取得
# 引数：int_p_no（request通番）, 口座属性クラス
def func_kanougaku( int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/43 No.10 引数名:CLMZanKaiKanougaku を参照してください。

    req_item = [class_req()]
    
    str_key = '"sCLMID"'
    str_value = 'CLMZanKaiKanougaku'  # 買余力を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/43 No.10 引数名:CLMZanKaiKanougaku を参照してください。

    return json_return





# 現物買い注文関数
# 引数：銘柄コード、市場（現在、東証'00'のみ）、執行条件、価格、株数、int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_order_buy_genbutsu(my_sIssueCode, my_sSizyouC, my_sCondition, my_sOrderPrice, my_sOrderSuryou, int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p4/43 No.5 引数名:CLMKabuNewOrder を参照してください。
    
    req_item = [class_req()]
        
    my_sGenkinShinyouKubun = '0'    # 16.現金信用区分  0:現物、2:新規(制度信用6ヶ月)、4:返済(制度信用6ヶ月)、6:新規(一般信用6ヶ月)、8:返済(一般信用6ヶ月)。
    my_sBaibaiKubun = '3'   # 12.売買区分  1:売、3:買、5:現渡、7:現引。

    # 固定パラメーターセット
    #my_sZyoutoekiKazeiC            # 8.譲渡益課税区分    1：特定  3：一般  5：NISA     ログインの返信データで設定済み。 
    my_sOrderExpireDay = '0'        # 17.注文期日  0:当日、上記以外は、注文期日日(YYYYMMDD)[10営業日迄]。
    my_sGyakusasiOrderType = '0'    # 18.逆指値注文種別  0:通常、1:逆指値、2:通常+逆指値
    my_sGyakusasiZyouken = '0'      # 19.逆指値条件  0:指定なし、条件値段(トリガー価格)
    my_sGyakusasiPrice = '*'        # 20.逆指値値段  *:指定なし、0:成行、*,0以外は逆指値値段。
    my_sTatebiType = '*'            # 21.建日種類  *:指定なし(現物または新規) 、1:個別指定、2:建日順、3:単価益順、4:単価損順。
    my_sTategyokuZyoutoekiKazeiC =  '*'    # 9.建玉譲渡益課税区分  信用建玉における譲渡益課税区分(現引、現渡で使用)。  *:現引、現渡以外の取引、1:特定、3:一般、5:NISA
    #my_sSecondPassword             # 22.第二パスワード    APIでは第２暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照     ログインの返信データで設定済み。
    

    # API request区分
    str_key = '"sCLMID"'
    str_value = 'CLMKabuNewOrder'  # 新規注文を指示。
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 現物信用区分
    str_key = '"sGenkinShinyouKubun"'    # 現金信用区分
    str_value = my_sGenkinShinyouKubun
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # 注文パラメーターセット
    str_key = '"sIssueCode"'    # 銘柄コード
    str_value = my_sIssueCode
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSizyouC"'    # 市場C
    str_value = my_sSizyouC
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sBaibaiKubun"'    # 売買区分
    str_value = my_sBaibaiKubun
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sCondition"'    # 執行条件
    str_value = my_sCondition
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderPrice"'    # 注文値段
    str_value = my_sOrderPrice
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderSuryou"'    # 注文数量
    str_value = my_sOrderSuryou
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    # 固定パラメーターセット
    str_key = '"sZyoutoekiKazeiC"'  # 税口座区分
    str_value = class_cust_property.sZyoutoekiKazeiC    # 引数の口座属性クラスより取得
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sOrderExpireDay"'    # 注文期日
    str_value = my_sOrderExpireDay
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiOrderType"'    # 逆指値注文種別
    str_value = my_sGyakusasiOrderType
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiZyouken"'    # 逆指値条件
    str_value = my_sGyakusasiZyouken
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sGyakusasiPrice"'    # 逆指値値段
    str_value = my_sGyakusasiPrice
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sTatebiType"'    # 建日種類
    str_value = my_sTatebiType
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sTategyokuZyoutoekiKazeiC"'     # 9.建玉譲渡益課税区分
    str_value = my_sTategyokuZyoutoekiKazeiC
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSecondPassword"'    # 第二パスワード   APIでは第２暗証番号を省略できない。 
    str_value = class_cust_property.sSecondPassword     # 引数の口座属性クラスより取得
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p4-5/43 No.5 引数名:CLMKabuNewOrder 項目1-28 を参照してください。
    
    return json_return      # 注文のjson応答文を返す



# 注文取消
# 引数：注文番号、営業日、int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_cancel_order(work_sOrderNumber, work_sEigyouDay, int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」(api_request_if_clumn_v4.pdf)
    # p6/43 No.7 引数名:CLMKabuCancelOrder を参照してください。
    # 注文取り消しは、現物、信用等の区別はない。

    req_item = [class_req()]
        
    # API request区分
    str_key = '"sCLMID"'
    str_value = '"CLMKabuCancelOrder"'  # 注文取消を指示。
    # req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 注文番号
    str_key = '"sOrderNumber"'    # 注文番号
    str_value = work_sOrderNumber
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    str_key = '"sEigyouDay"'    # 営業日
    str_value = work_sEigyouDay
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSecondPassword"'    # 第二パスワード  APIでは第２暗証番号を省略しない。
    str_value = class_cust_property.sSecondPassword
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)


    for i in range(30):     # 元注文が処理中の場合の待機処理
        json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
        # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
        # p6/43 No.7 引数名:CLMKabuCancelOrder を参照してください。
        
        if json_return.get('sResultCode') == '13290':   # 元注文が処理中の場合
            time.sleep(1)   # 引数の秒数のウエイト
            print('wait : ', (i+1))

        else:
            break

    return json_return




# 注文一覧の取得
# 引数：銘柄コード（指定無しは全一覧を取得）、int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_get_order_list(str_code, int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p12/43 No.13 引数名:CLMOrderList を参照してください。
        
    req_item = [class_req()]
    
    str_key = '"sCLMID"'
    str_value = 'CLMOrderList'
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sIssueCode"'
    str_value = str_code
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sSikkouDay"'
    str_value = datetime.datetime.now().strftime('%Y%m%d')
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p12-14/43 No.13 引数名:CLMOrderList 1-42 を参照してください。
    # 複数行データがあるとjsonデータがネストする

    return json_return



# 現物保有株一覧の取得
# 引数：銘柄コード（指定無しは全一覧を取得）、int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_get_genbutukabu_list(str_code, int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p7/43 No.8 引数名:CLMGenbutuKabuList を参照してください。

    req_item = [class_req()]
    
    str_key = '"sCLMID"'
    str_value = 'CLMGenbutuKabuList'
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sIssueCode"'
    str_value = str_code
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p7-8/43 No.8 引数名:CLMGenbutuKabuList 1-31 を参照してください。
    # 複数行データがあるとjsonデータがネストする

    return json_return



# 信用建玉一覧の取得
# 引数：銘柄コード（指定無しは全一覧を取得）、int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_get_shinyou_tategyoku_list(str_code, int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p7/43 No.8 引数名:CLMGenbutuKabuList を参照してください。

    req_item = [class_req()]
    
    str_key = '"sCLMID"'
    str_value = '"CLMShinyouTategyokuList"'
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"sIssueCode"'
    str_value = str_code
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p7-8/43 No.8 引数名:CLMGenbutuKabuList 1-31 を参照してください。
    # 複数行データがあるとjsonデータがネストする

    return json_return



# ログアウト
# 引数：int_p_no（request通番）, 口座属性クラス
# 返値：辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
def func_logout(int_p_no, class_cust_property):
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    req_item = [class_req()]   

    str_key = '"sCLMID"'
    str_value = 'CLMAuthLogoutRequest'  # logoutを指示。
    # req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = '5'    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    json_return = func_api_req(False, class_cust_property.sUrlRequest, int_p_no, req_item)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。

    return json_return




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================


# --- 利用時に変数を設定してください -------------------------------------------------------

# デモ環境（新バージョンになった場合、適宜変更）
# デモ環境は今のところメンテナンス待ちのため、注文、取消では利用できません。
url_base = 'https://demo-kabuka.e-shiten.jp/e_api_v4r2/'
#url_base = 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/'

# 本番環境（新バージョンになった場合、適宜変更）
# ＊＊！！実際に市場に注文が出るので注意！！＊＊
# url_base = 'https://kabuka.e-shiten.jp/e_api_v4r2/'
# url_base = 'https://kabuka.e-shiten.jp/e_api_v4r1/'


my_userid = 'MY_USERID' # 自分のuseridに書き換える
my_passwd = 'MY_PASSWD' # 自分のpasswordに書き換える
my_2pwd = 'MY_2PASSWD'  # 自分の第２passwordに書き換える


my_code = ''    # 銘柄コード     ''：指定なし の場合、一覧全体を取得する。


# --- 以上設定項目 -------------------------------------------------------------------------


int_p_no = [0]      # request通番
class_cust_property = class_def_cust_property()     # 口座属性クラス


print('-- login -----------------------------------------------------')
## 「ｅ支店・ＡＰＩ、ブラウザからの利用方法」に記載のログイン例
## 'https://demo-kabuka.e-shiten.jp/e_api_v4r1/auth/?{"p_no":"1","p_sd_date":"2020.11.07-13:46:35.000",'
## '"sCLMID":"CLMAuthLoginRequest","sPassword":"xxxxxx","sUserId":"xxxxxxxx","sJsonOfmt":"5"}'
##
# 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.1 引数名:CLMAuthLoginRequest を参照してください。

# ログイン処理
json_return = func_login(url_base, my_userid, my_passwd,  int_p_no)
# 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
# p2/43 No.2 引数名:CLMAuthLoginAck を参照してください。

my_p_error = int(json_return.get('p_errno'))    # p_erronは、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇ｒ〇）、REQUEST I/F、利用方法、データ仕様」を参照ください。
if my_p_error ==  0 :    # ログインエラーでない場合
    my_sZyoutoekiKazeiC = json_return.get('sZyoutoekiKazeiC')
    print('sZyoutoekiKazeiC= ', my_sZyoutoekiKazeiC, '  税口座区分  1:特定、3:一般、5:NISA')
    
    my_sSecondPasswordOmit = json_return.get('sSecondPasswordOmit')
    print('sSecondPasswordOmit= ', my_sSecondPasswordOmit, '  暗証番号省略有無C  1:有,0:無     APIでは第２暗証番号は省略不可')
        
    my_sUrlRequest = json_return.get('sUrlRequest')     # request用仮想URL
    my_sUrlEvent = json_return.get('sUrlEvent')         # event用仮想URL

    # 口座属性クラスに取得した値をセット
    class_cust_property.set_property(my_sUrlRequest, my_sUrlEvent, my_sZyoutoekiKazeiC, my_2pwd)

else :  # ログインに問題があった場合
    my_sUrlRequest = ''     # request用仮想URL
    my_sUrlEvent = ''       # event用仮想URL


if len(my_sUrlRequest) > 0 and len(my_sUrlEvent) > 0 :  # ログインOKの場合

    print()
    print('-- 買余力の照会 -------------------------------------------------------------')
    
    json_return = func_kanougaku(int_p_no, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p10/43 No.10 引数名:CLMZanKaiKanougaku を参照してください。
    
    print('更新日時= ', json_return.get("sSummaryUpdate"))     # 株式現物買付可能額
    print('株式現物買付可能額= ', json_return.get("sSummaryGenkabuKaituke"))     # 株式現物買付可能額
    print('NISA口座買付可能額= ', json_return.get("sSummaryNisaKaitukeKanougaku"))     # NISA口座買付可能額




    print()
    print('-- 注文約定一覧 -------------------------------------------------------------')
    
    my_sIssueCode = my_code     # ''：指定なし の場合全注文を取得する。プログラム最初の部分で設定した銘柄コード。
    json_return = func_get_order_list(my_sIssueCode, int_p_no, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p12-14/43 No.13 引数名:CLMOrderList 1-42 を参照してください。
        
    print('oderlist= ')
    
    dic_return = json_return.get('aOrderList')
    
    # 複数行の注文データが返るとjsonデータがネストする
    print('len(dic_return)= ', len(dic_return))     # 取得データ件数
            
    for i in range(len(dic_return)):
        print(dic_return[i].get('sOrderOrderNumber'))               # 注文番号
        print(dic_return[i].get('sOrderIssueCode'))      # 銘柄コード
        print(dic_return[i].get('sOrderBaibaiKubun'))    # 売買
        print(dic_return[i].get('sOrderOrderPrice'))     # 価格
        print(dic_return[i].get('sOrderOrderSuryou'))    # 株数
        print(dic_return[i].get('sOrderStatusCode'))     # 注文状態コード
        print(dic_return[i].get('sOrderStatus'))         # 注文状態
        print()



    
    print()
    print('-- 現物保有銘柄一覧 -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p7/43 No.8 引数名:CLMGenbutuKabuList を参照してください。
    
    my_sIssueCode = my_code     # ''：指定なし の場合全一覧を取得する。プログラム最初の部分で設定した銘柄コード。
    json_return = func_get_genbutukabu_list(my_sIssueCode, int_p_no, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p7-8/43 No.8 引数名:CLMGenbutuKabuList 1-31 を参照してください。
        
    print('aGenbutuKabuList= ')
    
    dic_return = json_return.get('aGenbutuKabuList')
    
    # 複数行のデータが返るとjsonデータがネストする
    print('len(dic_return)= ', len(dic_return))     # 取得データ件数
            
    for i in range(len(dic_return)):
        print(dic_return[i].get('sUriOrderIssueCode'))                          # 銘柄コード
        print(dic_return[i].get('sUriOrderZyoutoekiKazeiC'))   # 税口座
        print(dic_return[i].get('sUriOrderZanKabuSuryou'))     # 残高株数
        print(dic_return[i].get('sUriOrderUritukeKanouSuryou'))     # 売付可能株数
        print(dic_return[i].get('sUriOrderGaisanBokaTanka'))   # 概算簿価単価
        print(dic_return[i].get('sUriOrderHyoukaTanka'))       # 評価単価
        print(dic_return[i].get('sUriOrderGaisanHyoukaSoneki'))     # 評価損益
        print()



    
    print()
    print('-- 信用建玉一覧 -------------------------------------------------------------')
    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p8/43 No.9 引数名:CLMShinyouTategyokuList を参照してください。
    
    my_sIssueCode = my_code     # ''：指定なし の場合全一覧を取得する。ププログラム最初の部分で設定した銘柄コード。
    json_return = func_get_shinyou_tategyoku_list(my_sIssueCode, int_p_no, class_cust_property)
    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p8-10/43 No.9 引数名:CLMShinyouTategyokuList 1-47 を参照してください。
        
    print('aShinyouTategyokuList= ')
    
    dic_return = json_return.get('aShinyouTategyokuList')
    
    # 複数行のデータが返るとjsonデータがネストする
    print('len(dic_return)= ', len(dic_return))     # 取得データ件数
            
    for i in range(len(dic_return)):
        print(dic_return[i].get('sOrderTategyokuNumber'))   # 建玉番号
        print(dic_return[i].get('sOrderIssueCode'))         # 銘柄コード
        print(dic_return[i].get('sOrderBaibaiKubun'))       # 売買  1:売、3:買、5:現渡、7:現引
        print(dic_return[i].get('sOrderBensaiKubun'))       # 弁済区分  00:なし、26:制度信用6ヶ月、29:制度信用無期限、36:一般信用6ヶ月、39:一般信用無期限
        print(dic_return[i].get('sOrderZyoutoekiKazeiC'))   # 譲渡益課税区分  1:特定、3:一般、5:NISA
        print(dic_return[i].get('sOrderTategyokuSuryou'))   # 建株数
        print(dic_return[i].get('sOrderGaisanHyoukaSoneki'))    # 評価損益
        print()



    
    print()
    print('-- logout -------------------------------------------------------------')
    ## マニュアルの解説「（２）ログアウト」
    ##        {
    ##　　　　　"p_no":"2",
    ##　　　　　"p_sd_date":"2020.07.01-10:00:00.100",
    ##　　　　　"sCLMID":"CLMAuthLogoutRequest"
    ##　　　　}
    ##
    ##　　　要求例：
    ##　　　　仮想ＵＲＬ（REQUEST）/?{"p_no":"2","p_sd_date":"2020.07.01-10:00:00.100","sCLMID":"CLMAuthLogoutRequest"}

    # 送信項目の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.3 引数名:CLMAuthLogoutRequest を参照してください。
    
    json_return = func_logout(int_p_no, class_cust_property)

    # 戻り値の解説は、マニュアル「立花証券・ｅ支店・ＡＰＩ（ｖ〇）、REQUEST I/F、機能毎引数項目仕様」
    # p3/43 No.4 引数名:CLMAuthLogoutAck を参照してください。
    print('p_no= ', json_return.get("p_no"))
    print('sCLMID= ', json_return.get("sCLMID"))
    print('sResultCode= ', json_return.get('sResultCode'))  # 業務処理.エラーコード 0:正常、5桁数字:「結果テキスト」に対応するエラーコード
    
else :
    print('ログインに失敗しました')
