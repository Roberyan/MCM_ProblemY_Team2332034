from webCrawler_util import getLinkListFromURL, getSailboatInfoFromURL, getSailboatInfoFromURL_V0
import time
import random
import pandas as pd


def main():
    pageNum = 0
    successNum = 0
    failNum = 0
    totalNum = 10146

    savePeriod = 10
    periodID = 1

    file1 = './successfulBoatsURL.txt'
    file2 = './unsuccessfulBoatsURL.txt'

    webURLTemplate = "https://www.yachtworld.com/boats-for-sale/condition-used/type-sail/?page="

    print("########## Begin Data Crawling ##########")
    currentNum = successNum + failNum
    result = None
    while currentNum <= totalNum:
        pageNum += 1
        targetWebURL = webURLTemplate + str(pageNum)
        sailboatList = getLinkListFromURL(targetWebURL)

        for boatId, boatURL in sailboatList:
            # time.sleep(random.randint(0, 3))
            try:
                df_boatInfo = getSailboatInfoFromURL_V0(boatURL)
                if successNum == 0:
                    result = df_boatInfo
                else:
                    result = pd.concat([result, df_boatInfo])

                with open(file1, 'a', encoding='utf-8') as f:
                    row = str(boatId) + " " + str(boatURL) + "\n"
                    f.write(row)
                successNum += 1
                print("{} has been crawled successfully!".format(successNum))

            except:
                failNum += 1
                with open(file2, 'a', encoding='utf-8') as f:
                    row = str(boatId) + " " + str(boatURL) + "\n"
                    f.write(row)
                print("{} has failed!".format(failNum))
                continue

            if (successNum % savePeriod) == 0:
                tempName = ("./data/crawledData_Temp"+str(periodID)+".xlsx")
                periodID += 1
                result.to_excel(tempName, index=False)
                print("###  TempFile Saved!  ###")

        print("Page{} is crawled, {}/{}=  {}%".format(pageNum,
                                                      currentNum, totalNum, currentNum/totalNum * 100))

    print("Total samples: {}".format(successNum))
    result.to_excel("./data/crawledData.xlsx", index=False)
    print("########## Crawling Success! ##########")


main()
