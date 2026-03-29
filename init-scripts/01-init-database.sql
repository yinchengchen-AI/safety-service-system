-- 初始化数据库
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 设置时区
SET TIMEZONE = 'Asia/Shanghai';

-- 日志输出
\echo 'Database initialized successfully!'
