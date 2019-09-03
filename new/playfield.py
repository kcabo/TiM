# d = {1:"kkk","u":"8","d":{"l":"iu","tt":"uu"}}

# print(d.get("h",{"tt":None}).get("tt"))


# def hoge(*a):
#     for i in a:
#         print(i)
#
# hoge(3,3,3,9)
#
# tu = ("kk",8,{7:8,7:{9:0}})
#
# print(tuple({d}))
# print()
#
#
# import datetime
#
# # print(type(int(datetime.date.today().strftime('%Y%m%d'))))
# print(datetime.date.today().strftime('%m/%d(%a)'))

# n = None
#
# print(i for i in list(None))

import flex_constructor

class menu():
    description = "あああああああああああああｓ"
    cycle = "cycle"
    category = "category"
    serial = 8



m = menu()
# print(m.category)

chain_date = "190903"

def hoge():
    return flex_constructor.design_flex_menu_list(chain_date, [m,m,m,m,m,m,m])

# def sub(n):
#     if n != 0:
#         n-=1
#         print(n)
#         sub(n)
#     else:
#         print("finish")
#
# sub(8000)
