import os
import xlsxwriter
# 加载txt列表寻找关键词并保存到excel
def matchKeyWords(ThePath,aim_path):
    dir_list = os.listdir(ThePath)
    print(dir_list)
    book = xlsxwriter.Workbook(aim_path)

    sheet = book.add_worksheet('字节统计')
    sheet.write(0, 0, 'code')
    sheet.write(0, 1, 'year')
    sheet.write(0, 2, 'size')
    index=0
    for dir in dir_list:
        #dir_path = ThePath + '/' + dir
        #files = os.listdir(dir_path)
        #for file in files:
            if os.path.splitext(dir)[-1] == ".txt":
                txt_path = os.path.join(ThePath, dir)
                stock_code = dir.split("_")[0]
                #year = dir.split("_")[1]
                year= dir.split("_")[1]
                year = year.split(".")[0]
                sheet.write(index + 1, 0, stock_code)#index表示列数
                sheet.write(index + 1, 1, year)
                print(f'正在统计{ThePath}-{dir}')
                size = os.path.getsize(txt_path)  # 文件路径及文件名
                sheet.write(index+1, 2, size)
                index+=1
    #book.save(aim_path)
    book.close()

ThePath= r'/提取内容/2017'
aim_path=r'/Result'#统计结果

matchKeyWords(ThePath, f'{aim_path}\ 2017字节数.xlsx')
