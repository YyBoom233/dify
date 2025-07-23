"""
TXT2SQL Agent with Knowledge Base Integration
结合三个知识库的高准确率SQL生成器
"""

class TXT2SQLAgent:
    def __init__(self, llm_client, knowledge_bases):
        self.llm_client = llm_client
        self.ddl_kb = knowledge_bases['ddl']           # DDL知识库
        self.q2sql_kb = knowledge_bases['q2sql']       # Q→SQL样本库  
        self.db_desc_kb = knowledge_bases['db_desc']   # DB Description知识库
        
    def generate_sql(self, user_question):
        """
        生成SQL查询的主函数
        """
        # 1. 从三个知识库检索相关信息
        ddl_info = self.retrieve_ddl_info(user_question)
        q2sql_samples = self.retrieve_q2sql_samples(user_question)
        db_descriptions = self.retrieve_db_descriptions(user_question)
        
        # 2. 构建完整的prompt
        system_prompt = self.build_system_prompt()
        user_prompt = self.build_user_prompt(
            user_question, ddl_info, q2sql_samples, db_descriptions
        )
        
        # 3. 调用LLM生成SQL
        response = self.llm_client.chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        return response
    
    def retrieve_ddl_info(self, question):
        """从DDL知识库检索相关表结构"""
        # 这里应该调用你的知识库检索接口
        # 根据问题关键词检索相关的表创建语句
        return self.ddl_kb.search(question, top_k=5)
    
    def retrieve_q2sql_samples(self, question):
        """从Q→SQL样本库检索相似问题和SQL"""
        # 检索类似的问答对
        return self.q2sql_kb.search(question, top_k=3)
    
    def retrieve_db_descriptions(self, question):
        """从DB Description检索表和字段说明"""
        # 检索相关的表和字段描述
        return self.db_desc_kb.search(question, top_k=5)
    
    def build_system_prompt(self):
        """构建系统prompt"""
        return """你是一个专业的Text-to-SQL转换专家。你的任务是将用户的自然语言问题转换为准确的SQL查询语句。

## 严格约束条件：
1. 你只能回答与SQL查询生成相关的问题
2. 你的输出只能包含：SQL语句 + SQL执行流程解释
3. 拒绝回答任何非SQL相关的问题

## 知识库使用策略：

### DDL知识库（表结构定义）
- 这是你的权威数据源，包含所有表的创建语句
- 必须严格按照DDL中的表名、字段名、数据类型生成SQL
- 如果DDL中不存在相关表或字段，明确告知无法生成SQL

### Q→SQL样本库（问答样本）
- 参考类似问题的SQL模式和最佳实践
- 学习常见的查询模式、JOIN方式、聚合函数使用
- 借鉴解决思路，但必须结合实际DDL调整

### DB Description（表字段说明）
- 理解每个表和字段的业务含义
- 根据字段描述选择正确的过滤和关联条件
- 确保生成的SQL符合实际业务逻辑

## 必须遵循的输出格式：

**SQL语句：**
```sql
[这里是生成的SQL语句]
```

**执行流程解释：**
1. **表选择依据**：说明为什么选择这些表
2. **字段选择理由**：解释选择的字段及原因  
3. **连接逻辑**：说明表之间的关联关系
4. **过滤条件**：解释WHERE条件的设置依据
5. **排序/分组逻辑**：如有ORDER BY/GROUP BY，说明原因
6. **预期结果**：描述查询将返回什么数据

## 质量标准：
✓ SQL语法完全正确
✓ 基于真实存在的表和字段
✓ 逻辑符合业务需求
✓ 考虑查询性能优化

现在请根据用户的自然语言问题，结合提供的知识库信息，生成准确的SQL查询。"""

    def build_user_prompt(self, question, ddl_info, q2sql_samples, db_descriptions):
        """构建用户prompt，包含检索到的知识库信息"""
        prompt = f"""用户问题：{question}

## 相关DDL信息（表结构定义）：
{self.format_ddl_info(ddl_info)}

## 相似Q→SQL样本：
{self.format_q2sql_samples(q2sql_samples)}

## 相关表字段描述：
{self.format_db_descriptions(db_descriptions)}

请基于以上知识库信息，为用户问题生成准确的SQL查询。"""
        
        return prompt
    
    def format_ddl_info(self, ddl_info):
        """格式化DDL信息"""
        if not ddl_info:
            return "未找到相关表结构信息"
        
        formatted = ""
        for item in ddl_info:
            formatted += f"表名：{item.get('table_name', '')}\n"
            formatted += f"DDL语句：\n{item.get('ddl_statement', '')}\n\n"
        
        return formatted
    
    def format_q2sql_samples(self, samples):
        """格式化Q→SQL样本"""
        if not samples:
            return "未找到相似问题样本"
        
        formatted = ""
        for i, sample in enumerate(samples, 1):
            formatted += f"样本{i}：\n"
            formatted += f"问题：{sample.get('question', '')}\n"
            formatted += f"SQL：{sample.get('sql', '')}\n\n"
        
        return formatted
    
    def format_db_descriptions(self, descriptions):
        """格式化数据库描述信息"""
        if not descriptions:
            return "未找到相关表字段描述"
        
        formatted = ""
        for desc in descriptions:
            formatted += f"表：{desc.get('table_name', '')}\n"
            formatted += f"字段：{desc.get('field_name', '')}\n"
            formatted += f"描述：{desc.get('description', '')}\n\n"
        
        return formatted

# 使用示例
def main():
    # 初始化知识库（这里是伪代码，需要根据你的实际知识库系统调整）
    knowledge_bases = {
        'ddl': DDLKnowledgeBase(),
        'q2sql': Q2SQLKnowledgeBase(), 
        'db_desc': DBDescriptionKnowledgeBase()
    }
    
    # 初始化LLM客户端
    llm_client = YourLLMClient()
    
    # 创建agent
    agent = TXT2SQLAgent(llm_client, knowledge_bases)
    
    # 测试查询
    user_question = "查询销售金额大于1000的订单信息"
    result = agent.generate_sql(user_question)
    
    print("生成的SQL结果：")
    print(result)

if __name__ == "__main__":
    main()