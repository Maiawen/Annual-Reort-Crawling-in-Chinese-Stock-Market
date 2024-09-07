#import xlwt  这玩意超过256行报错，用xlsxwriter替代
import os
import xlsxwriter
# 加载txt列表寻找关键词并保存到excel
def matchKeyWords(ThePath, keyWords,aim_path):
    dir_list = os.listdir(ThePath)
    print(dir_list)
    #book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    book = xlsxwriter.Workbook(aim_path)
    #sheet = book.add_sheet('词典统计', cell_overwrite_ok=True)
    #sheet = book.add_worksheet('词典统计', cell_overwrite_ok=True)
    sheet = book.add_worksheet('词典统计')
    sheet.write(0, 0, 'code')
    sheet.write(0, 1, 'year')
    for i,c_word in enumerate(keyWords):
        sheet.write(0, i+2, c_word)
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
                sheet.write(index + 1, 0, stock_code)
                sheet.write(index + 1, 1, year)
                print(f'正在统计{ThePath}-{dir}')
                with open(txt_path, "r", encoding='utf-8', errors='ignore')as fp:
                    text = fp.readlines()
                    s=0
                    for ind,word in enumerate(keyWords):
                        num = 0
                        for line in text:
                            num += line.count(word)
                        word_freq=num
                        s+=num
                        sheet.write(index + 1, ind + 2, str(word_freq))
                    #这里统计一下前面的词频数量
                    sheet.write(index + 1, len(keyWords) + 2, s)
                index+=1
    #book.save(aim_path)
    book.close()

ThePath= r'/提取内容/2022'
aim_path=r'/Result'#统计结果
neg_path=r'neg.txt'
pos_path=r'pos.txt'
#keywords = ['营业收入','估值','资产','股东','智能数据分析','智能机器人','机器学习','深度学习']#词典
negdic=[line.strip().split('\t')[0] for line in open(neg_path, encoding='UTF-8')]
posdic=[line.strip().split('\t')[0] for line in open(pos_path, encoding='UTF-8')]
matchKeyWords(ThePath, negdic,f'{aim_path}\ 2022词频neg.xlsx')
matchKeyWords(ThePath, posdic,f'{aim_path}\ 2022词频pos.xlsx')
