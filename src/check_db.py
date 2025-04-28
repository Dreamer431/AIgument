from sqlalchemy import create_engine, inspect, text
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "instance", "aigument.db")
engine = create_engine(f'sqlite:///{db_path}')

# 检查表
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"数据库中的表：{tables}")

# 检查每个表中的数据
for table in tables:
    print(f"\n表 {table} 中的数据：")
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table}"))
        for row in result:
            print(row) 