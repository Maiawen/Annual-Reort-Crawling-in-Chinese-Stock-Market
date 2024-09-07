# Annual-Reort-Crawling-in-Chinese-Stock-Market
# Project Name

**Project Introduction**:
This project is mainly used to obtain the basic information of listed companies, crawl the links to the annual report PDFs, and filter and clean the data. At the same time, it uses multi-threading to download the annual reports, obtains the information of specific chapters of the annual report PDFs and converts them into txt format. Finally, it filters out the files without content based on the byte size of the obtained txt files and conducts word frequency statistics through the constructed dictionary.

## Project Structure
```
project_root/
│   README.md
│
└───src/
│   │   data_collection.py
│   │   data_processing.py
│   │   text_extraction.py
│   │   word_frequency.py
│
└───data/
│   │   raw_data/
│   │   processed_data/
```

## Function Introduction

### Part 1: Data Acquisition and Filtering
- `data_collection.py`: Responsible for obtaining the basic information of listed companies, crawling the links to the annual report PDFs, and filtering the data, such as cleaning delisted, ST, and B-share companies.

### Part 2: Annual Report Download
- `data_processing.py`: Merges the obtained data and uses multi-threading to download the annual reports.

### Part 3: Text Extraction
- `text_extraction.py`: Obtains the information of specific chapters of the annual report PDFs and converts it into txt format.

### Part 4: Word Frequency Statistics
- `word_frequency.py`: Filters out the files without content based on the byte size of the obtained txt files and conducts word frequency statistics through the constructed dictionary.

## Usage
1. Run `1.1获得巨潮网所有上市公司基本信息.py` to obtain the basic information of all listed companies on the Juchao website.
2. Run `1.2爬取年报pdf链接（多线程处理）.py` to crawl the links to the annual report PDFs using multi-threading.
3. Run `1.3数据清洗.py` to clean the data.
4. Run `2.1merge.py` to merge the data.
5. Run `2.2下载年报（多线程）.ipynb` to download the annual reports using multi-threading.
6. Run `3.1读取特定章节new.py` to read the specific chapters of the annual reports.
7. Run `3.2转换txt.py` to convert the data into txt format.
8. Run `4.1读取字节大小（筛选无效txt）.py` to read the byte size of the txt files and filter out the invalid ones.
9. Run `4.2词频统计.py` to conduct word frequency statistics.

## Notes
1. Before running the scripts, please ensure that the network connection is normal.
2. The data storage path can be modified according to needs.

---

The above is the README document of this project. I hope it will be helpful to you. If you have any questions, please feel free to contact us.
