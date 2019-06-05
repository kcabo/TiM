from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib

def make_all_data_lists(block, all_data):
    #この処理は同一ブロックIDごとにおこなう
    reversed_two_dimensions = []
    col_1 = [block.category,block.description]
    col_2 = ["",block.cycle]
    reversed_two_dimensions.append(col_1)
    reversed_two_dimensions.append(col_2)

    #各選手のデータがいくつ行を持っているか
    max_row_list = []
    length = len(all_data)
    for i in range(length):
        if i == length - 1: #一番最後の行データ
            max_row_list.append(all_data[i].row)
        elif all_data[i+1].row == 1:
            max_row_list.append(all_data[i].row)

    index = 0
    for max_row in max_row_list:
        #max_rowが一選手の持つデータ数
        one_swimmer_time_data = [all_data[index].swimmer]
        one_swimmer_styles = [""]

        #jはゼロから始まる indexに値を足していく その選手が持つ行分繰り返す
        for j in range(max_row):
            target = all_data[index + j]
            one_swimmer_time_data.append(target.data)
            one_swimmer_styles.append(target.style)

        time_values = []
        lap_indicator = []
        for td in one_swimmer_time_data:
            val = conv_to_100sec(td)
            time_values.append(val)
            if val == None:
                lap_indicator.append(0)
            else:
                lap_indicator.append(1)

        rows_length = len(lap_indicator)
        for x in range(rows_length):
            if lap_indicator[x] > 0:
                if lap_indicator[x-1] > 0: #上のとandでつなげると一個目がindexエラーになる
                    gap = time_values[x] - time_values[x-1]
                    if gap > 2200:
                         lap_indicator[x] = lap_indicator[x-1] + 1

        print(lap_indicator,time_values)
        max_len_styles = max(one_swimmer_styles,key=len)
        if max_len_styles != "": #スタイルが一つでも存在している
            reversed_two_dimensions.append(one_swimmer_styles)

        reversed_two_dimensions.append(one_swimmer_time_data)
        blank = []
        reversed_two_dimensions.append(blank)
        index += max_row #次の選手のデータが始まるindexを指定

    print(reversed_two_dimensions)
    return reversed_two_dimensions

def conv_to_100sec(time_str):
    try:
        posi = time_str.find(":")
        if posi == -1:
            return None
        else:
            minutes = time_str[:posi]
            seconds = float(time_str[posi + 1:])
            time_value = 0.0
            time_value = seconds + int(minutes) * 60
            time_value = int(time_value * 100)
            return time_value
    except:
        return None
def send_mail(content):
    #iPhoneのgmailアプリではBOMつけないと文字化けする utf-8-sigがBOM付きUTF-8
    #Excelのデフォルト文字コードはShiftJISであり、UTF-8はBOM付きでないと認識されない。文字化けする
    #\nはラインフィード、\rはキャリッジリターンである。
    #つまり\nだけだとWindows純正メモソフトで開いたときに改行してくれない。まあそれだけなんだけど
    Subject = "これは件名"
    addr_to = os.environ['TO_ADDRESS']
    addr_from = os.environ['SENDER_GMAIL_ACCOUNT']
    body_text = "本文です。"
    filename = '添付ファイル.csv'
    atch_content = content
    sender = os.environ['SENDER_GMAIL_ACCOUNT']
    application_pw = os.environ['GMAIL_APPLICATION_PASSWORD']

    msg = MIMEMultipart()
    msg["Subject"] = Subject
    msg["To"] = addr_to
    msg["From"] = addr_from
    msg.attach(MIMEText(body_text,'plain','utf-8'))

    attachment = MIMEText(atch_content, 'plain', 'utf-8-sig')
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment)

    with smtplib.SMTP_SSL('smtp.gmail.com') as smtp:
        smtp.login(sender, application_pw)
        smtp.send_message(msg)

class bb():
    category = "swim"
    description = "50*4*1 Hard"
    cycle = "1:00"

if __name__ == '__main__':
    all_data = [1,2,3,4,1,2,1,1,1,2,3]
    bl = bb()
    make_all_data_lists(bl,all_data)


#以下試行錯誤の軌跡
# from email.header import Header
# from email import encoders
# from email.mime.application import MIMEApplication
# ファイルを添付
# path = "csvdata.txt"
# with open(path, 'r', encoding="utf-8") as afile:
#     rd = afile.read()
#     print(rd,type(rd))
#     part = MIMEApplication("どどｄ",Name="test.txt")
#     encoders.encode_base64(part)

# part = MIMEText("thisisあああ21".encode('utf-8'),'plain','utf-8')
# part.add_header('Content-Disposition', 'attachment', filename="waaい.txt", charset='utf-8')
# encoders.encode_base64(part)
# msg.attach(part)

# メール送信処理
# server = smtplib.SMTP("smtp.gmail.com", 587)
# server.ehlo() #必要？
# server.starttls()
# server.ehlo()
# server.login(account, password)
# server.send_message(account, "k7cabo@gmail.com", msg.as_string())
# server.close()
