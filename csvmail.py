
def make_all_data_lists(block, all_data):
    #この処理は同一ブロックIDごとにおこなう
    reversed_two_dimensions = []
    col_1 = [block.category,block.description]
    col_2 = ["",block.cycle]
    reversed_two_dimensions.append(col_1)
    reversed_two_dimensions.append(col_2)
    print(reversed_two_dimensions)

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



class bb():
    category = "swim"
    description = "50*4*1 Hard"
    cycle = "1:00"



if __name__ == '__main__':
    all_data = [1,2,3,4,1,2,1,1,1,2,3]
    bl = bb()
    make_all_data_lists(bl,all_data)