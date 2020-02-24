from flask import Flask, request
import requests
import datetime
import json

app = Flask(__name__)

appId = "FSAID_1318a7d"
appSecret = "843ea0736ad14e7d861544e2c2bf6087"
permanentCode = "FA7CF078C9587CE5DB3F42ACF16F2491"
_headers = {'Content-Type': 'application/json'}
OpenUserId = "FSUID_626246E2FF28FE8757EA4CF3F88C9B40"
dataObjectApiName = "AccountObj"


@app.route('/')
def ping():
    return 'pong'


@app.route('/test', methods=['get', 'post'])
def test():
    issues = all_issue_query()
    return issues


def doPost(_url, _data):
    response = requests.post(_url, headers=_headers, data=_data.encode('utf-8'))
    return response.content


def doLog(_text):
    time_stamp = datetime.datetime.now()
    time = str(time_stamp)
    print(time + " : " + _text)


# 获取corpAccessToken & corpId
def getCorpAccessToken():
    doLog('execute getCorpAccessToken and corpId')
    url = "https://open.fxiaoke.com/cgi/corpAccessToken/get/V2"
    payload = '''{"appId":%s, "appSecret": %s, "permanentCode": %s}''' % (appId, appSecret, permanentCode)
    content = doPost(url, payload)
    content_dict = json.loads(content)
    corpAccessToken = content_dict["corpAccessToken"]
    corpId = content_dict["corpId"]
    expiresIn = content_dict['expiresIn']
    print('corpAccessToken:' + corpAccessToken + "---" + 'corpId:' + corpId + "---" + 'expiresIn:' + str(expiresIn))
    return corpAccessToken, corpId


# 根据客户名称LIKE客户_id
def getCustomer_id(customer_name):
    doLog("get customer _id by customer name")
    url = "https://open.fxiaoke.com/cgi/crm/v2/data/query"
    corpAccessToken, corpId = getCorpAccessToken()
    print(isinstance(corpAccessToken, str))
    payload = '''{"corpAccessToken": %s,"corpId":%s,"currentOpenUserId":%s,"data": {"dataObjectApiName": %s,"search_query_info": {"limit": 5,"offset": 0,"filters": [{"field_name": "name","field_values": [%s],"operator": "LIKE"},{"field_name": "life_status","field_values": ["normal"],"operator": "IN"}],"orders": [{"fieldName": "payment_amount","isAsc": false}],"fieldProjection": ["_id", "name"]}}}''' % (
        corpAccessToken, corpId, OpenUserId, dataObjectApiName, customer_name)
    customrer_info = doPost(url, payload)
    customrer_info_dict = json.loads(customrer_info)
    _id = customrer_info_dict['data']['dataList'][0]['_id']
    return _id


# 将jira中json数据提取出来
def getJiraField(data):
    # dumps:把字典转换为json字符串
    data_str = json.dumps(data)
    # loads:把json转换为dict
    data_dict = json.loads(data_str)
    issue_event_type_name = data_dict['issue_event_type_name']          # 工单类型 ？？？？？？
    SH_id = data_dict['issue']['key']                                   # 工单id
    value = data_dict['issue']['customfield_10505']['value']            # 是否签约
    custom_name = data_dict['issue']['customfield_10507']               # 客户名称
    custom_dp_env = data_dict['issue']['customfield_10508']             # 客户集群信息
    dp_version = data_dict['issue']['customfield_10509']['name']        # dp版本
    created = data_dict['issue']['created']                             # 创建时间
    priority = data_dict['issue']['priority']['name']                   # 优先级
    issuelinks = data_dict['issue']['issuelinks']                       # 对应的jira链接
    statusCategory = data_dict['issue']['statusCategory']['name']       # 当前工单所处状态
    taskCategory = data_dict['issue']['customfield_10530']['value']     # 任务类型（生产&测试）
    updated = data_dict['issue']['updated']                             # 更新时间
    status = data_dict['issue']['status']['name']                       # 工单当前状态
    isWorkTime = data_dict['issue']['customfield_10600']['value']       # 是否为工作时间
    title = data_dict['issue']['summary']                               # 工单标题
    issue_descp = data_dict['issue']['customfield_10515']               # 问题描述
    remark01 = data_dict['comment']['comments']                         # 备注
    body = data_dict['issue']['body']                                   # 解决描述


# CRM对象接口-自定义对象-新增对象
def createIssue(data):
    doLog("create issue")
    url = 'https://open.fxiaoke.com/cgi/crm/custom/data/create'
    corpAccessToken, corpId = getCorpAccessToken()
    customer_name = data['customer']
    customer_id = getCustomer_id(customer_name)
    payload = {
        "corpAccessToken": corpAccessToken,
        "corpId": corpId,
        "currentOpenUserId": OpenUserId,
        "triggerWorkFlow": 'false',
        "data": {
            "object_data": {
                "dataObjectApiName": "object_Yhf2o__c",
                "field_2851f__c": "技术咨询",
                "field_O48qF__c": "完成",
                "field_kd817__c": "技术咨询",
                "field_vSUI1__c": "中油瑞飞FLOAT支持",
                "field_0MgDL__c": "已签约",
                "field_631F4__c": "P3",
                "owner_department": "1005",
                "field_hFnac__c": "",
                "create_time": 1580865807900,
                "field_1ng4L__c": "",
                "created_by": ["FSUID_626246E2FF28FE8757EA4CF3F88C9B40"],
                "field_mb1y5__c": customer_id,
                "name": "SH01",
                "field_T534k__c": "是",
                "owner": ["FSUID_626246E2FF28FE8757EA4CF3F88C9B40"]
            }
        }
    }
    info = doPost(url, data)
    return info

# CRM对象接口-自定义对象-查询对象数据列表 --- 查询所有工单
def all_issue_query():
    doLog("query all issue")
    url = 'https://open.fxiaoke.com/cgi/crm/custom/data/query'
    corpAccessToken, corpId = getCorpAccessToken()
    payload = {
        "corpAccessToken": "E1F4D857FA579BD8C1A1A011249ECDBA",
        "corpId": "FSCID_6F77ADFA946108AECFE66A93FFC9E1F2",
        "currentOpenUserId": "FSUID_626246E2FF28FE8757EA4CF3F88C9B40",
        "data": {
            "dataObjectApiName": "object_Yhf2o__c",
            "search_query_info": {
                "offset": 0,
                "limit": 100
            }
        }
    }
    data = json.dumps(payload)
    all_issues = doPost(url, data)
    return all_issues


# CRM对象接口-自定义对象-更新对象数据 --- 更新工单
def updateIssueById(_id):
    doLog("query all issue")
    url = 'https://open.fxiaoke.com/cgi/crm/custom/data/update'
    corpAccessToken, corpId = getCorpAccessToken()
    payload = {
        "_id":_id
    }
    data = json.dumps(payload)
    backCodes = doPost(url, data)
    return backCodes

@app.route('/hook', methods=['get', 'post'])
def hook():
    # 1.获取JIRA传递过来的参数
    requestData = request.data
    # 2.判断提交数据的类型，是更新还是新增
    # 3.拆解传递过来的参数，把有用的数据获取到
    # 4.组织提交参数
    # 5.调用CRM系统并且把参数传递进去
    #     5.1 需要获取连接的参数，比如openUserId之类的
    #     5.2 访问目标CRM的API
    print(request.data)

    # dumps:把字典转换为json字符串
    jsonStr = json.dumps(requestData)

    # loads:把json转换为dict
    jsonObject = json.loads(jsonStr)
    print(jsonObject["key_in_json"])

    # get方法demo
    url = "http://my.os/notification/charm/"
    payload = {'message': "Opportunities and challenges together"}
    response = requests.get(url, headers=_headers, params=payload)
    print(response.status_code)
    print(response.content)

    # post方法demo
    url = "http://my.os/api/notification/charm/"
    payload = {'message': "Opportunities and challenges together"}
    response = requests.post(url, headers=_headers, data=payload)
    print(response.status_code)
    print(response.content)

    return request.data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40000)
