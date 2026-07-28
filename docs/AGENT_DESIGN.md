# Agent设计文档


# 1. Agent列表


|Agent|职责|
|-|-|
|Assistant Agent|入口|
|Router Agent|意图识别|
|Chitchat Agent|闲聊|
|Knowledge Agent|知识问答|
|Experiment Status Agent|试验查询|
|Quotation Agent|报价|
|Reservation Agent|预约|
|Report Agent|报告查询|
|Summary Agent|结果整合|


---

# 2. Router Agent


输入：

用户消息


输出：

```json
{
"intent":"quotation"
}
```


---

# 3. Knowledge Agent


## 输入


```
新能源汽车电池检测标准
```


## 输出


检测方案说明。


## Tool


```
retrieval_tool
```


---

# 4. Experiment Status Agent


## Tool


```python
query_experiment_status()
```


## 输入


订单号。


## 输出


```json
{
"status":"TESTING",
"progress":60
}
```


---

# 5. Quotation Agent


## 核心流程


```
用户需求

↓

识别检测项目

↓

query_price_tool

↓

calculate_tool

↓

输出报价
```


## Tools


### 查询价格

```
query_test_price
```


### 计算价格

```
calculate_total_price
```


禁止：

Agent直接计算金额。


---

# 6. Summary Agent


负责：

- 合并结果
- 格式化输出
- 生成自然语言回复