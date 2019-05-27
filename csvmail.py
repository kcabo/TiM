
def make_all_data_lists(block, all_data):
    parent_list = []
    col_1 = [block.category,block.description]
    col_2 = [block.cycle]
    parent_list.append(col_1)
    parent_list.append(col_2)
    print(parent_list)

    str = ""
    for child in parent_list:
        str += child[0]
        print(str)




class bb():
    category = "swim"
    description = "50*4*1 Hard"
    cycle = "1:00"

if __name__ == '__main__':
    all_data = []
    bl = bb()
    make_all_data_lists(bl,all_data)
