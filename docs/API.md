# API接口设计


Base URL:

```
/api/v1
```


---

# 1. Chat接口


## 请求


POST


```
/chat
```


Request:


```json
{
"user_id":"001",

"message":"我的检测做到哪一步了"
}
```


Response:


```json
{
"answer":

"当前正在高温测试阶段"
}
```


---

# 2. 查询试验状态


GET


```
/experiment/status/{order_no}
```


Response:


```json
{

"order_no":"A001",

"status":"TESTING",

"progress":60

}
```


---

# 3. 报价接口


POST


```
/quotation
```


Request:


```json
{

"product":"新能源汽车电池",

"tests":[

"高温测试",

"循环测试"

]

}
```


Response:


```json
{

"items":[

{

"name":"高温测试",

"price":3000

}

],

"total_price":8000

}
```


---

# 4. 报告查询


GET


```
/report/{order_id}
```


---

# 5. 创建预约


POST


```
/reservation
```


需要Human确认。