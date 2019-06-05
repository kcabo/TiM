from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

def make_all_data_lists(block, all_data):
    #この処理は同一ブロックIDごとにおこなう
    reversed_two_dimensions = []
    col_1 = [block.category,block.description]
    col_2 = ["",block.cycle]
    reversed_two_dimensions.append(col_1)
    reversed_two_dimensions.append(col_2)
    # print(reversed_two_dimensions)

    # str = ""
    # for child in reversed_two_dimensions:
    #     str += child[0]
    #     print(str)

    max_row_list = []
    length = len(all_data)

    for i in range(length):
        if i == length - 1:
            max_row_list.append(all_data[i].row)
        elif all_data[i+1].row == 1:
            max_row_list.append(all_data[i].row)

    print(max_row_list)

    index = 0

    for max_row in max_row_list:
        #max_rowのひとつひとつが選手一人分
        main_data = [all_data[index].swimmer]
        styles = [""]

        #jはゼロから始まる indexに値を足していく その選手が持つ行分繰り返す
        for j in range(max_row):
            main_data.append(all_data[index + j].data)
            styles.append(all_data[index + j].style)

        reversed_two_dimensions.append(main_data)
        index += max_row #次の要素についても

    print(reversed_two_dimensions)
    return reversed_two_dimensions

def send_mail():
    #iPhoneのgmailアプリではBOMつけないと文字化けする utf-8-sigがBOM付きUTF-8
    #Excelのデフォルト文字コードはShiftJISであり、UTF-8はBOM付きでないと認識されない。文字化けする
    #\nはラインフィード、\rはキャリッジリターンである。
    #つまり\nだけだとWindows純正メモソフトで開いたときに改行してくれない。まあそれだけなんだけど
    Subject = "これは件名"
    addr_to = "k7cabo@gmail.com"
    addr_from = "gin.mail.bot@gmail.com"
    body_text = "本文です。"
    filename = '添付ファイル.csv'
    atch_content = "thisisあああ21,niko2\r\n３こめ"


    msg = MIMEMultipart()
    msg["Subject"] = Header(Subject, 'utf-8')
    msg["To"] = addr_to
    msg["From"] = addr_from
    msg.attach(MIMEText(body_text,'plain','utf-8'))

    attachment = MIMEText(atch_content, 'plain', 'utf-8-sig')
    attachment.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', filename))
    msg.attach(attachment)


    with smtplib.SMTP_SSL('smtp.gmail.com') as smtp:
        smtp.login('gin.mail.bot', 'jmikmbdekiwuwzax')
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
