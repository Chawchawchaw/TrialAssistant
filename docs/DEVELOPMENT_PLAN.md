# 开发计划


# Phase 1 基础框架


目标：

完成Agent运行框架。


实现：

- FastAPI
- LangGraph
- Router Agent
- Chitchat Agent


---

# Phase 2 RAG能力


实现：

- 文档上传
- MinerU解析
- Embedding
- Milvus检索
- Knowledge Agent


---

# Phase 3 业务Agent


实现：

## Experiment Status Agent

包括：

- LIMS Mock
- 状态查询Tool


## Quotation Agent

包括：

- Price Query Tool
- Calculate Tool


---

# Phase 4 企业能力


实现：

- MCP Server
- Human-in-loop
- Redis缓存
- RabbitMQ异步任务


---

# Phase 5 优化


增加：

- Agent监控
- Prompt管理
- RAG评估
- 性能优化


---

# 开发原则


不要一次生成全部代码。


每阶段：

1. 设计
2. 编码
3. 测试
4. 文档更新


完成后再进入下一阶段。