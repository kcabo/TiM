def record_matrix(self):
    raw_records = [self.swimmer] + self.times.split(',')
    base_records = list(map(self.fmt_to_val, raw_records))
    # lap_indicator = [0]*len(base_records)
    # for i, indicator in enumerate(lap_indicator,-1):
    #     if base_records[i] > 0 and
    lap_records = [base_records[i]-base_records[i-1] if base_records[i-1]>0 else 0 for i in range(len(base_records))]

    print(raw_records,base_records,lap_records, end='\n')

    if max(lap_records) > 0:
        self.matrix = [raw_records,[self.val_to_fmt(v) if v > 2200 else '' for v in lap_records],[]]
    else:
        self.matrix = [raw_records,[]]

def fmt_to_val(self, fmt):
    try:
        posi = fmt.find(":")
        if posi == -1:
            return 0
        else:
            minutes = int(fmt[:posi])
            seconds = int(fmt[posi + 1:].replace(".","")) #100倍した秒数
            time_value = seconds + minutes * 6000
            return time_value
    except:
        return 0

def val_to_fmt(self, val):
    minutes = val // 6000
    seconds = str(val % 6000).zfill(4)
    time_str = "{0}:{1}.{2}".format(str(minutes),seconds[-4:-2],seconds[-2:])
    return time_str

menu_query = Menu.query.filter_by(date = e.user.date).order_by(Menu.sequence).all()
if menu_query == []:
    e.send_text('メールで送るデータがありません')
else:
    csv = ''
    for m in menu_query:
        record_queries = Record.query.filter_by(date = m.date, sequence = m.sequence).all()
        record_matrix = [[m.category, m.description], ['',m.cycle]]
        for r in record_queries:
            r.record_matrix()
            record_matrix.extend(r.matrix)

        trans = [['']*len(record_matrix) for i in range(len(max(record_matrix, key=len)))]
        for column, list in enumerate(record_matrix):
            for i, d in enumerate(list):
                trans[i][column] = d

        for row in trans:
            csv += ','.join(row) + '\n'

        csv += '..\n'

    emailAgent.email(e.user, csv)
    msg_otsukaresama = [{"type": "sticker", "packageId": "11537", "stickerId": "52002734"},
            {'type' : 'text', 'text' : "メールで送ったよ！ありがとう！おつかれさま！😆😆" }]
    e.post_reply(msg_otsukaresama)
e.user.set_value(status = '')
