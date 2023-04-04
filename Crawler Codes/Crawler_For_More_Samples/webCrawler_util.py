import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}


def getLinkListFromURL(targetWebURL):
    page = requests.get(targetWebURL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    sailboatLinks = soup.select("div.search-right-col a")
    sailboats = []
    for sample in sailboatLinks:
        itemLink = sample.attrs["href"]
        try:
            itemId = sample.attrs["data-reporting-click-product-id"]
        except:
            continue
        sailboats.append(tuple([itemId, itemLink]))
    return sailboats


def getSailboatInfoFromURL(targetWebURL):
    page = requests.get(targetWebURL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    keys = []
    values = []

    infoCursor = soup.select("div.boat-details-content .summary")
    # 价格获取
    price = infoCursor[0].find(
        'span', attrs={"class": "payment-total"}).text.strip()
    keys.append("Listing Price (USD)")
    values.append(price)
    # 位置获取
    place = infoCursor[0].find(
        'h2', attrs={"class": "location"}).text.strip()
    keys.append("Location")
    values.append(place)

    # 基本信息获取(所有船前六个相同)
    infoCursor = soup.select("div.boat-details-content .details")
    tableBasics = infoCursor[0].find(
        'tbody', attrs={"class": "datatable-section"})
    for trtag in tableBasics:
        tdlist = trtag.find_all("td")
        keys.append(tdlist[0].text.strip())
        values.append(tdlist[1].text.strip())

    # 船体规格数据（不同船特征数量不同）
    infoCursor = soup.select(
        "div.boat-details-content .measurements .datatable-category")
    for cursor in infoCursor:
        if cursor.find("h3", attrs={"class": "sub-title"}).text.strip() == "Dimensions":
            dimensionTable = infoCursor[0].find(
                'tbody', attrs={"class": "datatable-section"})
            for trtag in dimensionTable:
                tdlist = trtag.find_all("td")
                if tdlist[0].text.strip() == "Length Overall":
                    keys.append("Length (ft)")
                    values.append(tdlist[1].text.strip())

                if tdlist[0].text.strip() == "Beam":
                    keys.append("Beam")
                    values.append(tdlist[1].text.strip())

    return pd.DataFrame([values], columns=keys)


def getSailboatInfoFromURL_V0(targetWebURL):
    page = requests.get(targetWebURL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    keys = []
    values = []

    infoCursor = soup.select("div.boat-details-content .summary")
    # 价格获取
    price = infoCursor[0].find(
        'span', attrs={"class": "payment-total"}).text.strip()
    keys.append("Listing Price (USD)")
    values.append(price)
    # 位置获取
    place = infoCursor[0].find(
        'h2', attrs={"class": "location"}).text.strip()
    keys.append("Location")
    values.append(place)

    # 基本信息获取(不同船特征数量不同)
    infoCursor = soup.select("div.boat-details-content .details")
    tableBasics = infoCursor[0].find(
        'tbody', attrs={"class": "datatable-section"})
    for trtag in tableBasics:
        tdlist = trtag.find_all("td")
        keys.append(tdlist[0].text.strip())
        values.append(tdlist[1].text.strip())

    # 动力信息获取（不同船特征数量不同）
    infoCursor = soup.select("div.boat-details-content .propulsion")
    tablePropulsion = infoCursor[0].find(
        'tbody', attrs={"class": "datatable-section"})
    for trtag in tablePropulsion:
        tdlist = trtag.find_all("td")
        keys.append(tdlist[0].text.strip())
        values.append(tdlist[1].text.strip())

    # 船体规格数据（不同船特征数量不同）
    infoCursor = soup.select(
        "div.boat-details-content .measurements .datatable-category")
    dimensionTable = infoCursor[0].find(
        'tbody', attrs={"class": "datatable-section"})
    for trtag in dimensionTable:
        tdlist = trtag.find_all("td")
        keys.append(tdlist[0].text.strip())
        values.append(tdlist[1].text.strip())

    tanksTable = infoCursor[1].find(
        'tbody', attrs={"class": "datatable-section"})
    for trtag in tanksTable:
        tdlist = trtag.find_all("td")
        keys.append(tdlist[0].text.strip())
        values.append(tdlist[1].text.strip())

    accommodationsTable = infoCursor[2].find(
        'tbody', attrs={"class": "datatable-section"})
    for trtag in accommodationsTable:
        tdlist = trtag.find_all("td")
        keys.append(tdlist[0].text.strip())
        values.append(tdlist[1].text.strip())

    return pd.DataFrame([values], columns=keys)
