import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import random

user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
                "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
                "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                ]


def getLinkListFromURL(targetWeb):
    headers = {'User-Agent': random.choice(user_agent_list)}
    page = requests.get(targetWeb, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    resultTable = soup.select("div.table-responsive tbody td a")
    resultLinks = []
    for result in resultTable:
        link = result.attrs["href"]
        resultLinks.append(link+"?units=imperial")

    return resultLinks


def getSailboatInfoFromURL(targetWeb):
    headers = {'User-Agent': random.choice(user_agent_list)}
    page = requests.get(targetWeb, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    keys = []
    values = []

    keys.append("Type")
    name = targetWeb.split("?")[0].split("/")[-1]
    values.append(name)

    infoCursor = soup.select("div.sailboat-details div.row")
    for i in range(len(infoCursor)):
        infoName = infoCursor[i].find(
            'div', attrs={"class": "sailboatdata-label"})
        if infoName == None:
            continue
        else:
            infoName = infoName.text.strip()[:-1]
        infoValue = infoCursor[i].find(
            'div', attrs={"class": "sailboatdata-data"}).text.strip()
        keys.append(infoName)
        values.append(infoValue)
        if infoName == "Designer":
            break
    return pd.DataFrame([values], columns=keys)

def getSailboatFeatures(searchKey, year):
    if '&' in searchKey:
        searchKey = searchKey.replace('&',"%26")
    aimURL = "https://sailboatdata.com/sailboat?filter%5Bname%5D="+ searchKey +"&paginate=25&units=imperial&sort=name"
    answers = getLinkListFromURL(aimURL)
    # 有搜索结果
    if len(answers) > 0:
        # 有唯一的搜索结果
        if(len(answers) == 1):
            df_features = getSailboatInfoFromURL(answers[0])
        else:
            # 有多个搜索结果,比较制造年限选择
            for i in range(len(answers)):
                df_features = getSailboatInfoFromURL(answers[i])
                builtYear = int(df_features.loc[0,"First Built"])
                if builtYear <= year:
                    break 
    # 无搜索结果
    else:
        return searchKey + " No Answer!" 
    
    return df_features

def mainFeatureCrawledSolo():
    totalPage = 353
    pageTemplate = "https://sailboatdata.com/?paginate=25&page="

    successNum = 0
    result = None

    print("########### Crawling Begin! #############")
    for i in range(1, totalPage+1):
        pageURL = pageTemplate + str(i)
        boatsURL = getLinkListFromURL(pageURL)
        for boatLink in boatsURL:
            try:
                df_boatInfo = getSailboatInfoFromURL(boatLink)
                if successNum == 0:
                    result = df_boatInfo
                else:
                    result = pd.concat([result, df_boatInfo])
                successNum += 1
                print("{} has been crawled successfully!".format(successNum))
            except:
                print("Failed!")
        
        if (successNum % 500) == 0:
            result.to_excel("./temp.xlsx", index=False)
        
        print("Page{}/{} has been crawled!".format(i, totalPage))

    print("Total samples: {}".format(successNum))
    result.to_excel("./crawledData_SailboatFeatures.xlsx", index=False)
    print("########## Crawling Success! ##########")

def manuallyRestart(continueNum = 2960):
    dataSailboats = pd.read_excel("./crawler2/totalSailData.xlsx")
    dataSailboats.reset_index(inplace=True)
    dataSailboats = dataSailboats.rename(columns={'index': 'sampleID'}) # 对应拼接用
    
    numNoResult = 222
    numSuccess = 2738
    savePeriod = 100
    infoExtra = pd.read_excel("./tempInfoExtra.xlsx")

    for sampleNum in range(continueNum, dataSailboats.shape[0]):
        sample = dataSailboats.iloc[sampleNum]
        searchKey = dataSailboats.iloc[sampleNum]["Make"] + " " + str(dataSailboats.iloc[sampleNum]["Variant"])
        searchYear = int(dataSailboats.iloc[sampleNum]["Year"])
        searchResult = getSailboatFeatures(searchKey, searchYear)
        # 查询不到
        if type(searchResult) == str:
            numNoResult += 1
            # 创建一个空的 Series，长度和 df 的列数相同
            empty_row = pd.Series([sampleNum]*len(infoExtra.columns), index=infoExtra.columns).to_frame()
            # 将空行添加到dataframe最后一行
            infoExtra = pd.concat([infoExtra, empty_row.T], ignore_index=True)
        else:
            numSuccess += 1
            searchResult['sampleID'] = sampleNum
            if sampleNum == 0:
                infoExtra = searchResult
            else:
                # infoExtra = pd.concat([infoExtra, searchResult], ignore_index=True)
                try:
                    infoExtra = pd.concat([infoExtra.reset_index(drop=True), searchResult.reset_index(drop=True)], axis=0)
                except:
                    numSuccess -= 1
                    numNoResult += 1
                    # 创建一个空的 Series，长度和 df 的列数相同
                    empty_row = pd.Series([sampleNum]*len(infoExtra.columns), index=infoExtra.columns).to_frame()
                    # 将空行添加到dataframe最后一行
                    infoExtra = pd.concat([infoExtra, empty_row.T], ignore_index=True)
                    print("pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects")
                    
        if (sampleNum%savePeriod) == 0:
            infoExtra.to_excel("./tempInfoExtra.xlsx")
        
        print("Processing {}/{}= {}%... \t success:{} \t noResult:{}".format((sampleNum+1),dataSailboats.shape[0],(sampleNum+1)/dataSailboats.shape[0]*100, numSuccess, numNoResult))

    infoExtra.to_excel("./tempInfoExtra.xlsx")
    merged_df = dataSailboats.merge(infoExtra, on='sampleID')
    merged_df.to_excel("./sailboatDataExtraV0.xlsx", index=False)
    
    newData = pd.concat([dataSailboats, infoExtra], axis=1).reset_index(drop=True)
    newData.to_excel("./sailboatDataExtra.xlsx", index=False)
    

if __name__ == "__main__":
    # originalFile = "./data/2023_MCM_Problem_Y_Boats.xlsx"
    # data_MonohulledSailboats = pd.read_excel(originalFile,sheet_name="Monohulled Sailboats ")
    # data_Catamarans = pd.read_excel(originalFile,sheet_name="Catamarans")
    
    # data_MonohulledSailboats["Class"] = "Monohulled"
    # data_Catamarans["Class"] = "Catamarans" 
    # dataSailboats = pd.concat([data_Catamarans, data_MonohulledSailboats])
    
    # dataSailboats.reset_index(inplace=True)
    # dataSailboats = dataSailboats.rename(columns={'index': 'sampleID'}) # 对应拼接用
    
    # numNoResult = 0
    # numSuccess = 0
    # savePeriod = 100

    # for sampleNum in range(dataSailboats.shape[0]):
    #     sample = dataSailboats.iloc[sampleNum]
    #     searchKey = dataSailboats.iloc[sampleNum]["Make"] + " " + str(dataSailboats.iloc[sampleNum]["Variant"])
    #     searchYear = int(dataSailboats.iloc[sampleNum]["Year"])
    #     searchResult = getSailboatFeatures(searchKey, searchYear)
    #     # 查询不到
    #     if type(searchResult) == str:
    #         numNoResult += 1
    #         # 创建一个空的 Series，长度和 df 的列数相同
    #         empty_row = pd.Series([sampleNum]*len(infoExtra.columns), index=infoExtra.columns).to_frame()
    #         # 将空行添加到dataframe最后一行
    #         infoExtra = pd.concat([infoExtra, empty_row.T], ignore_index=True)
    #     else:
    #         numSuccess += 1
    #         searchResult['sampleID'] = sampleNum
    #         if sampleNum == 0:
    #             infoExtra = searchResult
    #         else:
    #             # infoExtra = pd.concat([infoExtra, searchResult], ignore_index=True)
    #             try:
    #                 infoExtra = pd.concat([infoExtra.reset_index(drop=True), searchResult.reset_index(drop=True)], axis=0)
    #             except:
    #                 numSuccess -= 1
    #                 numNoResult += 1
    #                 # 创建一个空的 Series，长度和 df 的列数相同
    #                 empty_row = pd.Series([sampleNum]*len(infoExtra.columns), index=infoExtra.columns).to_frame()
    #                 # 将空行添加到dataframe最后一行
    #                 infoExtra = pd.concat([infoExtra, empty_row.T], ignore_index=True)
    #                 print("pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects")
                    
    #     if (sampleNum%savePeriod) == 0:
    #         infoExtra.to_excel("./tempInfoExtra.xlsx")
        
    #     print("Processing {}/{}= {}%... \t success:{} \t noResult:{}".format((sampleNum+1),dataSailboats.shape[0],(sampleNum+1)/dataSailboats.shape[0]*100, numSuccess, numNoResult))
    
    # merged_df = dataSailboats.merge(infoExtra, on='sampleID')
    # merged_df.to_excel("./sailboatDataExtraV0.xlsx", index=False)
    
    # newData = pd.concat([dataSailboats, infoExtra], axis=1).reset_index(drop=True)
    # newData.to_excel("./sailboatDataExtra.xlsx", index=False)
    manuallyRestart()