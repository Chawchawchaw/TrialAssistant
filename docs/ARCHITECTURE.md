# Trial Assistant 系统架构设计


# 1. 总体架构


```
                 User

                  |

             FastAPI API

                  |

          LangGraph Workflow

                  |

          Intent Router Agent

                  |

 ------------------------------------------------

 |        |          |          |          |

Chat   Knowledge  Status   Quotation Reservation


 |        |          |          |          |

LLM    Milvus      LIMS      LIMS       LIMS


                  |

             Summary Agent

                  |

              Response

```


---

# 2. 分层设计


## API层


职责：

- 接收请求
- 用户认证
- 参数校验


技术：

FastAPI


---

## Agent层


职责：

- 任务规划
- 意图识别
- Agent执行


技术：

LangGraph


---

## Tool层


职责：

封装外部能力。


包括：

- LIMS查询
- 价格查询
- 报告查询
- 计算服务


---

## 数据层


包括：

- PostgreSQL
- Redis
- Milvus


---

# 3. LangGraph流程


```
START

↓

Assistant Node

↓

Router Node

↓

Conditional Edge

↓

Business Agent

↓

Tool Node

↓

Summary Node

↓

END
```


---

# 4. 外部系统


## LIMS


负责：

- 试验数据
- 项目价格
- 实验室资源
- 报告信息


---

## Knowledge Base


负责：

- 标准文档
- 技术资料


流程：

```
Document

↓

MinerU

↓

Embedding

↓

Milvus

```


---

# 5. 状态管理


使用：

LangGraph Checkpointer


保存：

- Message
- Agent状态
- Tool结果


存储：

PostgreSQL