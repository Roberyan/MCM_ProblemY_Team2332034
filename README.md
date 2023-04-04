# Materials of MCM Problem Y by coder of the Team 2332034

## File Y 
* Original file of the MCM problem Y
* A translated version of the orignal file in Chinese by the [DeepL translator](https://www.deepl.com/en/translator)
* the analysis of the Y by George Liew

## File Crawler Codes
The python programs totally written by George to crawler sailboats data, and the raw data before cleaning. The .ipynb files are mainly used for debugging, checking logics and knowing the middle process results. After being tried successfully on .ipynb, the codes are organized into functions to run in .py files. The basic method is the same for the two cases, the difference is mainly about parsing different websites.

### data
All the raw data in their original forms, those related to sailboats are obtained through python programs, while others are collected mannually from the Internet. I am mainly responsible to crawl  information about the physical traits of sailboats from related websites.

### Crawler_For_More_Samples
Crawlering the [YatchWorld.com](https://www.yachtworld.com/boats-for-sale/type-sail/) for more training samples, which can provide over 8,000 used sailboats information.

### Crawler_For_More_Features
Crawlering the [SailboatData.com](https://sailboatdata.com/?paginate=25&page=1） for more sailboat specifications like length, beam, displacement, etc. We can gather features of over 1,500 types of sailboat from the site. But pratically speaking, it is suggested to crawl related information basing on the the searching results website with sample's "Make", "Variant", "Year" as key words. Which is the latest version of the code.

