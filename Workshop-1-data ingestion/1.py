import dlt

data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

# 创建管道
pipeline = dlt.pipeline(pipeline_name="quick_start", destination="duckdb", dataset_name="my_data")
# 运行
pipeline.run(data, table_name="users")



