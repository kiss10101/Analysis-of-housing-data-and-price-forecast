from app.models import Histroy
import json
from django.db.models import F
def addHistory(userInfo,houseID):
    hisData = Histroy.objects.filter(house_id=houseID,user=userInfo)
    if len(hisData):
        hisData[0].count = F("count") + 1
        hisData[0].save()
    else:
        Histroy.objects.create(house_id=houseID, user=userInfo)


def getHistoryData(userInfo):
    data = list(Histroy.objects.filter(user=userInfo).order_by("-count"))
    return data

