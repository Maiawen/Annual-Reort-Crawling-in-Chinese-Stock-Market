
import os
import json
import re

import sys


if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

import multiprocessing#多线程

from PyPDF2 import PdfFileReader#PyPDF2有获取目录的能力，可以直接导出目录及对应的页码

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

# 换行符
end = '\n'


def dispose(root_path, name_suffix=None, is_recover=False, load_cache=True, cache_info_path='pdf_cache.json'):
    """
    处理pdf数据
    :param name_suffix: 文件名后缀
    :param root_path: 处理的根目录
    :param is_recover: 是否覆盖（已导出的）
    :param load_cache: 是否使用缓存（不会重新扫描）
    :param cache_info_path: 缓存保存位置
    :return: None
    """

    if load_cache:
        if not os.path.exists(cache_info_path):
            load_cache = False
            print('没有找到缓存数据......')

    if load_cache:
        # pdf文档的缓存
        pdf_info = load_cache_info(cache_info_path)
    else:
        files = get_files_list(root_path)
        print('开始扫描文档.......')
        pdf_info = scan_pdf_directory(files, '环境和社会责任')#在目录中搜寻章节，环境和社会责任或重要事项
        save_cache_info(pdf_info)
    files = []
    for key, val in pdf_info.items():
        files.append(val.get('file_path'))
    if name_suffix is None:
        name_suffix = ""
    count = 0
    print('开始提取数据.......')
    for index, path in enumerate(files):
        print("处理进度 = {:.2f}%, 文件 = {}".format(index / len(pdf_info) * 100, os.path.basename(path)), end=end)

        info = pdf_info.get(str(index))
        if info.get('is_export') and (not is_recover):
            continue  # 如果已经导出并且不覆盖，则直接处理下一个
        text, info = parse_pdf(info)  # 提取数据
        text_file_name = info.get('stock_code') + '_' + str(name_suffix)#命名
        if info.get('is_have_directory'):
            save_text_file(text_file_name, text)  # 保存有目录的和text不为0的，尝试一下
        else:
            if text:
                save_text_file(text_file_name, text)#保存text不为0的，尝试一下


        info = update_file_info(info, text_length=len(text), is_export=True, output_length=len(text),
                                text_file_name=text_file_name)
        pdf_info.update({str(index): info})  # 更新缓存信息
        save_cache_info(pdf_info)
        count += 1
        if info.get('is_have_directory'):
            res = '有'
        else:
            res = '无'
        print('> 已保存有内容文件，文件名：{}，长度：{}，目录：{}，本次运行处理文件个数：{}'
              .format(text_file_name, len(text), res, count))

def save_cache_info(pdf_info):
    """
    保存处理信息
    :param pdf_info: 处理信息
    :return: None
    """
    with open("pdf_cache.json", 'w') as f:
        json_str = json.dumps(pdf_info)
        f.write(json_str)

def load_cache_info(info_path):
    """
    加载处理信息缓存文件
    :param info_path: 加载配置信息的位置
    :return: pdf缓存对象
    """
    with open(info_path, 'r') as f:
        json_str = f.read()
        pdf_info_cache = json.loads(json_str)
    return pdf_info_cache


def parse_pdf(info: dict):
    """
    解析pdf文档
    :param info: 文档信息
    :return: 文本内容，文档信息（股票代码，日期，起始位置，结束位置）
    """
    path = info.get('file_path')
    if path is None:
        raise ValueError('不存在文件路径')

    file = os.path.basename(path)  # 获取文件名
    stock_code = re.search(r'\d{6}', file).group(0)  # 解析股票代码
    #file_date = re.search(r'-\d{4}', file).group(0)  # 解析日期
    info = update_file_info(info, stock_code=stock_code)  # 更新信息

    text = ''  # 文本缓存
    with open(path, 'rb') as pdf_file:  # 读取pdf文档
        is_have_target_page = info.get('is_have_directory')
        start_page_number = 0
        end_page_number = 0
        page_count = info.get('page_count')
        if is_have_target_page:
            start_page_number = info.get('start_page_number')
            if start_page_number is None:#这里是没有找到页码让从头开始扫描
                start_page_number = 0
                is_have_target_page = False#下面的判断语句
            end_page_number = info.get('end_page_number')
            if end_page_number is None:
                is_have_target_page = False
                #end_page_number = info.get('page_count')
                end_page_number = 0#改成不扫描
        else:
            is_have_target_page = False

        pdf_parse = PDFParser(pdf_file)
        pdf_doc = PDFDocument(pdf_parse)
        if pdf_doc.is_extractable:
            pdf_rm = PDFResourceManager(caching=True)
            pdf_lap = LAParams()
            pdf_pa = PDFPageAggregator(pdf_rm, laparams=pdf_lap)
            pdf_pi = PDFPageInterpreter(pdf_rm, pdf_pa)

            if is_have_target_page:#有目标页
                page_set = set()
                for i in range(start_page_number, end_page_number):
                    page_set.add(i)

                pdf_page = PDFPage.get_pages(pdf_file, pagenos=page_set, password=b'', caching=True)
                print('读取文本->>>')
                for index, page in enumerate(pdf_page):
                    print("部分 : 当前文档进度 : {}/{}".format(index, len(page_set)), end=end)
                    pdf_pi.process_page(page)
                    layout = pdf_pa.get_result()
                    is_find_start_page = False

                    '''for x in layout:
                        if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                            text += x.get_text() + '\n'
                            # print(x.get_text())
                            '''
                    page_text = ''
                    for x in layout:
                        if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                            page_text += x.get_text() + '\n'

                    if re.search(r'重大环保问题.*', page_text):
                           text += page_text # 当前页开始保存
                           is_find_start_page = True
                           info = update_file_info(info, start_page_number=index)
                           continue

                    if is_find_start_page:
                           text += page_text
                           if re.search(r'社会责任情况.*', page_text):  # 找到下一节了，这里没改
                               info = update_file_info(info, end_page_number=index)
                               break
                '''page_set = set()
                for i in range(start_page_number, end_page_number):
                    page_set.add(i)

                pdf_page = PDFPage.get_pages(pdf_file, pagenos=page_set, password=b'', caching=True)
                print('读取文本->>>')
                for index, page in enumerate(pdf_page):
                    print("部分 : 当前文档进度 : {}/{}".format(index, len(page_set)), end=end)
                    pdf_pi.process_page(page)
                    layout = pdf_pa.get_result()

                    for x in layout:
                        if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                            text += x.get_text() + '\n'
                            # print(x.get_text())'''

            else:#没有目标页
                '''
                pdf_page = PDFPage.create_pages(pdf_doc)
                print('读取文本->>>')
                is_find_start_page = False
                #text_cache = ""
                for index, page in enumerate(pdf_page):
                    print("扫描 : 当前文档进度 : {}/{}, 找到起始位置 : {}".format(index, page_count, is_find_start_page),
                          end=end)
                    pdf_pi.process_page(page)
                    layout = pdf_pa.get_result()

                    page_text = ''
                    for x in layout:
                        if isinstance(x, LTTextBoxHorizontal):  # 获取文本内容
                            page_text += x.get_text() + '\n'
                            # print(x.get_text())

                    #text_cache += page_text

                    if re.search(r'第.节\\s*重要事项\s*一', page_text):  # 找到这一节了
                        if re.search(r'.、\\s*环境保护相关的情况*\s*', page_text):
                           text += page_text # 当前页开始保存
                           is_find_start_page = True
                           info = update_file_info(info, start_page_number=index)
                           continue

                    if is_find_start_page:
                        text += page_text
                        if re.search(r'.、\\s*其他重大事项的说明*\s*', page_text):  # 找到下一节了，这里没改
                            info = update_file_info(info, end_page_number=index)
                            break
                #if text == '':#没有的情况
                    #text = text_cache
                    '''

    return text, info


def save_text_file(file_name, txt):
    """
    覆盖保存文本文档到当前脚本目录下的output目录下
    UTF-8编码
    :param file_name: 文件名
    :param txt: 文件内容
    :return: None
    """
    if not file_name.endswith('.txt'):
        file_name += '.txt'  # 补全文件名

    file_path = os.path.join(os.getcwd(), '2022')#保存到代码文件夹，我新建了xxx下文件
    if not os.path.exists(file_path):
        os.mkdir(file_path)  # 创建文件夹

    with open(os.path.join(file_path, file_name), 'w', encoding='utf-8') as txt_file:
        txt_file.write(txt)  # 保存文件到原文档

    #with open(os.path.join(dir_path, file_name), 'w', encoding='utf-8') as txt_file:
        #txt_file.write(txt)  # 保存文件到原文档

def scan_pdf_directory(files_list, key_word):
    """
    扫描pdf文档目录，获得文档总页数，有无目录，有（起始位置，结束位置）
    key_word 用在有目录的情况下，
    不匹配则返回整个文档范围
    :param files_list: 要扫描的文件列表
    :param key_word: 目录关键词
    :return: 字典，每个元素为一个处理单元，有唯一的ID
    """
    pdf_info_dict = {}
    for index, file_path in enumerate(files_list):#可能要先扫描完
        start_page_number = 0  # 开始页码
        is_get_page_number_range = False

        info = update_file_info(file_path=file_path)
        with open(file_path, 'rb') as pdf_file:  # 读取pdf文档
            pdf = PdfFileReader(pdf_file)  # 加载pdf文档
            if pdf.isEncrypted:
                pdf.decrypt('')  # 解密
            try:
              end_page_number = pdf.getNumPages()  # 获取总页码
            except KeyError as e:
            # 跳过无法处理的PDF文件，并打印错误信息
              print(f"Error processing PDF file {file_path}: {e}")
              pass
            except UnboundLocalError as e:
                # 处理异常的代码块
                print(f"发生了一个异常：{e}")
                # 或者跳过这个错误并继续执行
                pass
            info = update_file_info(info, page_count=end_page_number)  # 保存总页数
            pdf_directory = pdf.getOutlines()  # 获取目录

            is_have_start_page_number = False
            for destination in pdf_directory:
                if isinstance(destination, dict):
                    if is_have_start_page_number:
                        end_page_number = pdf.getDestinationPageNumber(destination)
                        is_get_page_number_range = True
                        break

                    title = destination.get('/Title')
                    if key_word in str(title):
                        # 在目录中找到关键词了
                        start_page_number = pdf.getDestinationPageNumber(destination)
                        is_have_start_page_number = True
                        continue
        if is_get_page_number_range:
            info = update_file_info(info, start_page_number=start_page_number, end_page_number=end_page_number,
                                    is_have_directory=True)
            res = "获取页码成功"
        else:
            info = update_file_info(info, is_have_directory=False)
            res = "获取页码失败"
        print("扫描进度 : {:.2f}%, 文件 : {}".format(index / len(files_list) * 100, os.path.basename(file_path)), res, ':',
              '[', start_page_number, ',', end_page_number, ']', end=end)
        pdf_info_dict.update({str(index): info})
    return pdf_info_dict


def update_file_info(info=None, file_path=None, start_page_number=None, end_page_number=None, page_count=None,
                     output_length=None,
                     is_have_directory=None, is_export=None, stock_code=None, text_file_name=None,
                     text_length=None):
    """
    更新字典里的东西，如果不是字典，则被替换成字典
    :param text_length: 导出的文本文件长度
    :param page_count: 总页数
    :param stock_code: 股票代码
    :param text_file_name: 对应的文本文件名
    :param info: 字典
    :param file_path: 更新文件路径
    :param start_page_number: 更新开始页码
    :param end_page_number: 更新结束页码
    :param output_length: 输出长度
    :param is_have_directory: 是否存在目录
    :param is_export: 是否已经导出
    :return: 更新后的info
    """
    if info is None:
        info = {
            'file_path': None,
            'start_page_number': None,
            'end_page_number': None,
            'output_length': None,
            'is_have_directory': None,
            'is_export': None,
            'stock_code': None,
            'text_file_name': None,
            'page_count': None,
            'text_length': None
        }

    if not isinstance(info, dict):
        raise ValueError("传入的值info必须是空或者是字典！")

    if file_path:
        info['file_path'] = file_path

    if start_page_number:
        info['start_page_number'] = start_page_number

    if end_page_number:
        info['end_page_number'] = end_page_number

    if output_length:
        info['output_length'] = output_length

    if is_have_directory:
        info['is_have_directory'] = is_have_directory

    if is_export:
        info['is_export'] = is_export

    if stock_code:
        info['stock_code'] = stock_code

    if text_file_name:
        info['text_file_name'] = text_file_name

    if page_count:
        info['page_count'] = page_count

    if text_length:
        info['text_length'] = text_length

    return info


def get_files_list(path):
    """
    获取传入路径中及其子目录下的所有pdf文件路径
    :param path: 要搜索的根路径
    :return: pdf文件路径列表
    """
    files_list = []
    for i,(root, dirs, files) in enumerate(os.walk(path)):  # 遍历目录
        for file in files:  # 遍历文件
            file_path = os.path.join(root, file)  # 拼接路径
            if file_path.endswith("2022年年度报告.pdf"):  # 如果是pdf文件 #以20xx结尾的
                files_list.append(file_path)  # 添加到列表中
    print(files_list)#test
    return files_list

if __name__ == '__main__':
    # 扫描根目录，文件名后缀，是否覆盖，是否使用缓存信息
    ThePath = r'/2022年报pdf'
        #dispose(ThePath, 2022, True, False)
    dir_process = multiprocessing.Process(target=dispose(ThePath, 2022, True, False))#专门处理一下xxxx年的
    #TRUE表示覆盖，FALSE是表示不用缓存
    dir_process.start()