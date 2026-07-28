# 数据库设计


数据库：

PostgreSQL


# 1. 用户表


```sql
user

id

username

password

created_time
```


---

# 2. 会话表


```sql
conversation

id

user_id

messages

created_time
```


---

# 3. 试验订单表


```sql
experiment_order


id


order_no


customer_name


product_name


status


current_stage


progress


expected_finish


created_time

```


---

# 4. 检测项目价格表


```sql
test_price


id


test_name


standard


price


duration


```


---

# 5. 报告表


```sql
report


id


order_id


status


file_url


created_time

```


---

# 6. Agent执行记录


```sql
agent_trace


id


conversation_id


agent_name


tool_name


input


output


created_time

```


用于：

- 调试
- 监控
- 问题追踪