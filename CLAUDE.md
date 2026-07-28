# CLAUDE.md

# Trial Assistant AI Agent Platform


## 项目名称

Trial Assistant


## 产品名称

检测宝 AI Agent 平台


## 项目定位


Trial Assistant 是一个面向第三方检测机构的企业级 Multi-Agent 业务自动化平台。

通过多个专业 Agent 协同，实现：

- 检测知识咨询
- 检测标准查询
- 试验状态查询
- 自动报价
- 实验室预约
- 报告查询


---

# 1. 项目开发目标


实现一个基于大语言模型的检测业务智能助手。


核心能力：

```
用户自然语言输入

↓

Intent识别

↓

Agent路由

↓

调用业务Tool

↓

生成业务结果

```


系统目标：

将传统人工客服查询流程转变为 AI Agent 自动化流程。


---

# 2. 技术栈约束


## Backend


Python:

```
3.11+
```


Web Framework:

```
FastAPI
```


数据模型：

```
Pydantic
```


ORM：

```
SQLAlchemy
```


---

## AI Framework


Agent：

```
LangGraph
```


LLM Application：

```
LangChain
```


---

## Storage


Vector Database:

```
Milvus
```


Database:

```
PostgreSQL
```


Cache:

```
Redis
```


---

## Message Queue


```
RabbitMQ
```


---

## Deployment


```
Docker

Docker Compose
```


---

# 3. 架构设计原则


## 3.1 Agent First


所有智能业务逻辑必须通过 Agent 完成。


禁止：

```
API

↓

直接调用LLM

↓

返回结果
```


正确：


```
API

↓

LangGraph Workflow

↓

Agent

↓

Tool

↓

Business System

```


---

## 3.2 Tool First


所有企业能力必须封装为 Tool。


例如：


正确：

```
Quotation Agent

↓

query_price_tool

↓

LIMS
```


错误：

```
Quotation Agent

↓

直接访问数据库
```


---

## 3.3 LLM职责边界


LLM负责：

- 用户意图理解
- 参数提取
- Agent规划
- 自然语言生成


LLM禁止负责：

- 金额计算
- 数据存储
- 业务状态修改
- 权限判断


---

# 4. 系统整体架构


```
                         User

                          |

                 Assistant Agent

                          |

                Intent Router Agent

                          |

 --------------------------------------------------

 |             |              |             |      |

Chitchat   Knowledge   Experiment   Quotation  Reservation

 Agent       Agent       Status       Agent       Agent

                          Agent


 |             |              |             |

 LLM          RAG            LIMS          LIMS


                          |

                    Report Agent


                          |

                   Summary Agent

```


---

# 5. 项目目录规范


```
trial_assistant/


├── CLAUDE.md

├── README.md


├── docs/

│
├── PRD.md

├── ARCHITECTURE.md

├── AGENT_DESIGN.md

├── DATABASE.md

├── API.md

└── DEVELOPMENT_PLAN.md


├── backend/


│
├── app/


│
├── agents/


│   ├── router/

│   ├── chitchat/

│   ├── knowledge/

│   ├── experiment_status/

│   ├── quotation/

│   ├── reservation/

│   └── report/


│
├── workflows/


├── tools/


├── mcp/


├── models/


├── services/


└── api/


├── frontend/


├── docker-compose.yml


└── .env.example

```


---

# 6. LangGraph设计规范


所有 Agent 编排必须使用：

```
StateGraph
```


禁止：

- Agent之间直接调用
- Agent自行维护状态


---

## Agent State


统一状态：


```python
class AgentState:

    messages:list

    user_id:str

    conversation_id:str

    intent:str

    current_agent:str

    tool_results:dict

    need_human:bool

    final_answer:str

```


---

# 7. Agent设计规范


每个Agent必须包含：


```
agent.py

prompt.py

tools.py

schema.py
```


---

# 8. Agent功能定义


# 8.1 Assistant Agent


职责：

系统入口。


负责：

- 接收用户消息
- 创建会话
- 初始化State
- 调用Router


---

# 8.2 Intent Router Agent


职责：

识别用户意图。


输入：

```
我的检测报告出来了吗？
```


输出：

```json
{
 "intent":"report_query",

 "confidence":0.96
}
```


支持Intent：


|Intent|Agent|
|-|-|
|chitchat|Chitchat Agent|
|knowledge_query|Knowledge Agent|
|experiment_status|Experiment Status Agent|
|quotation|Quotation Agent|
|reservation|Reservation Agent|
|report_query|Report Agent|


---

# 8.3 Chitchat Agent


职责：

处理非业务聊天。


例如：

用户：

```
你好
```


回复：

```
您好，我是检测宝智能助手，可以帮助您查询检测相关业务。
```


规则：

禁止调用：

- Milvus
- LIMS
- Business Tool


---

# 8.4 Knowledge Agent


职责：

检测知识问答。


使用：

RAG


数据来源：

- 国家标准
- 行业标准
- 检测规范
- 产品资料


流程：


```
Question

↓

Query Rewrite

↓

Embedding

↓

Milvus Search

↓

Rerank

↓

LLM

↓

Answer

```


---

# 8.5 Experiment Status Agent


职责：

查询客户试验执行状态。


数据来源：

LIMS。


查询：

- 委托单
- 样品状态
- 当前试验阶段
- 完成进度
- 预计完成时间


Tool：


```python
@tool
def query_experiment_status(
    order_id:str
):

    """
    查询试验状态

    """

    return result

```


---

# 8.6 Quotation Agent


职责：

根据检测需求生成报价。


核心流程：


```
用户需求

↓

Quotation Agent

↓

解析检测项目

↓

调用LIMS价格接口

↓

获取单项价格

↓

调用Calculate Tool

↓

生成报价结果

```


---

## Quotation业务规则


非常重要：


禁止：


```
LLM计算金额
```


原因：

- 大模型数学不稳定
- 金额属于强业务数据


---

## Price Query Tool


负责：

从LIMS获取检测项目价格。


```python
@tool

def query_test_price(
    test_items:list
):

    """
    查询检测项目价格

    """

    return prices

```


返回：

```json
{
 "items":[

 {
  "name":"高温测试",

  "price":3000
 }

 ]

}

```


---

## Calculate Tool


专门负责金额计算。


```python
@tool

def calculate_total_price(
    prices:list
):

    """
    计算报价总金额

    """

    return sum(prices)

```


---

报价输出：


```json
{

"items":[

 {
  "name":"高温测试",

  "price":3000
 }

],


"total_price":3000

}

```


---

# 8.7 Reservation Agent


职责：

实验室预约。


能力：

- 查询实验室资源
- 查询设备
- 查询时间
- 创建预约


Tools：

```
query_lab()

create_booking()

```


---

# 8.8 Report Agent


职责：

报告查询。


能力：

- 查询报告状态
- 查询审核状态
- 获取报告


Tools：

```
query_report()

download_report()

```


---

# 8.9 Summary Agent


职责：

整合多个 Agent 输出。


例如：


Quotation Agent:

```
费用5000元
```


Experiment Agent:

```
预计15天完成
```


Summary Agent：

生成最终回复。


---

# 9. MCP设计规范


MCP用于统一企业系统能力。


架构：


```
Agent

↓

MCP Server

↓

----------------

LIMS

CRM

报价系统

知识服务

```


示例：


```json
{

"name":

"query_experiment_status",


"description":

"查询试验状态"

}

```


---

# 10. 数据库规范


禁止：

业务数据写死。


所有数据使用数据库。


---

## Experiment Order


```sql
experiment_order

id

customer_name

product

status

current_stage

progress

expected_finish

```


---

## Test Price


```sql
test_price

id

test_name

standard

price

duration

```


---

## Report


```sql
report

id

order_id

status

url

create_time

```


---

# 11. Memory设计


保存：

- 用户历史消息
- Agent状态
- Tool调用记录


技术：

```
PostgreSQL

+

LangGraph Checkpointer

```


---

# 12. Human In The Loop


使用场景：

- 创建预约
- 修改业务订单
- 提交正式操作


流程：


```
Agent

↓

interrupt()

↓

Human Confirm

↓

continue()

```


---

# 13. RabbitMQ异步任务


场景：

知识库更新。


流程：


```
上传PDF

↓

RabbitMQ

↓

Document Worker

↓

MinerU解析

↓

Embedding

↓

Milvus更新

```


---

# 14. API规范


统一前缀：

```
/api/v1
```


---

## Experiment Status


```
GET

/api/v1/experiment/status/{order_id}

```


---

## Quotation


```
POST

/api/v1/quotation

```


请求：

```json
{

"product":"新能源汽车电池",

"tests":[

"高温测试"

]

}

```


---

# 15. 开发阶段


## Phase 1


基础框架：

完成：

- FastAPI
- LangGraph
- Router Agent
- Chitchat Agent


---

## Phase 2


知识能力：

完成：

- RAG
- Milvus
- Knowledge Agent


---

## Phase 3


业务Agent：

完成：

- LIMS Mock
- Experiment Status Agent
- Quotation Agent
- Calculate Tool


---

## Phase 4


企业能力：

完成：

- MCP
- HITL
- Checkpointer
- RabbitMQ


---

# 16. Coding规范


要求：

- Python Type Hint
- 模块化设计
- 完整异常处理
- Tool调用日志
- Prompt版本管理
- Swagger API文档


---

# 17. 开发流程


禁止一次生成整个项目。


必须按照：

```
需求分析

↓

设计模块

↓

创建工程

↓

实现Phase

↓

运行测试

↓

继续开发

```


每完成一个阶段：

必须：

- 验证运行
- 修复问题
- 更新README

