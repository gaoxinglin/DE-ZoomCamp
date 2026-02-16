# 出租车数据重复记录调查报告

## 📋 执行摘要

在对出租车行程数据进行分析后，发现了 **684,749条重复记录** (占总数据的0.6%)。这些重复记录主要由以下原因导致：

### 主要发现

1. **数据质量问题最严重**: 83% 的重复 (568,420条记录) 包含负数值
2. **不是真正的完全重复**: 99.98% 的重复记录是"部分重复" - 即关键字段相同但其他字段不同
3. **主要影响Yellow出租车**: 318,912组重复来自Yellow，23,285组来自Green

---

## 🔍 详细分析

### 1. 负数值问题 (NEGATIVE_VALUES) 
**影响最大 - 568,420条记录**

**特征:**
- 包含负数的 `fare_amount`, `total_amount` 或 `trip_distance`
- 284,080 个重复组

**示例:**
```sql
-- 查看负数值的重复记录
SELECT * FROM dev.int_trips_unioned 
WHERE vendor_id = 2 
  AND pickup_datetime = '2019-01-01 03:25:40'
ORDER BY fare_amount;

-- 结果显示同一行程有:
-- fare_amount: -5.000, 5.000, 6.500
-- 明显的数据错误
```

**根本原因:**
- 数据录入错误
- 系统调整或退款记录（应该在单独的表中）
- ETL过程中的错误

**建议解决方案:**
- ✅ 过滤掉所有负数值的记录
- ✅ 或标记为"调整/退款"记录，单独处理

---

### 2. 距离和费用不一致 (DISTANCE_AND_FARE_VARY)
**影响: 53,105条记录**

**特征:**
- 相同的 vendor_id + pickup_datetime + dropoff_datetime
- 但 trip_distance 和 fare_amount 不同

**示例:**
```sql
SELECT * FROM dev.int_trips_unioned 
WHERE vendor_id = 1 
  AND pickup_datetime = '2020-10-05 13:33:01'
ORDER BY trip_distance;

-- 同一行程显示:
-- trip_distance: 0.4, 0.6, 1.0, 1.5
-- fare_amount: 4.000, 5.000, 6.000, 7.500
```

**根本原因:**
- GPS/计价器读数不准确
- 多次记录同一行程（司机端/乘客端/系统端）
- 数据同步问题

**建议解决方案:**
- ✅ 保留费用最高的记录（通常最完整）
- ✅ 或使用中位数逻辑

---

### 3. 付款方式和费用不一致 (PAYMENT_AND_FARE_VARY)
**影响: 33,844条记录**

**特征:**
- payment_type 不同（信用卡/现金/其他）
- fare_amount 也不同

**根本原因:**
- 付款方式更改（乘客改变主意）
- 小费计算差异
- 后期调整

**建议解决方案:**
- ✅ 优先保留最常见的付款方式（信用卡=1，现金=2）
- ✅ 使用最终的 total_amount

---

### 4. 地点信息不一致 (LOCATION_VARIES)
**影响: 28,521条记录**

**特征:**
- pickup_location_id 或 dropoff_location_id 不同
- 但时间戳相同

**根本原因:**
- GPS漂移
- 手动位置调整
- 区域边界问题

---

### 5. 瞬时行程 (INSTANT_TRIP)
**影响: 492条记录**

**特征:**
- pickup_datetime = dropoff_datetime（完全相同）

**根本原因:**
- 取消的行程
- 系统测试数据
- 时间戳记录错误

**建议解决方案:**
- ✅ 过滤掉瞬时行程（不合理的数据）

---

## 🛠️ 实施建议

### 方案1: 严格过滤（推荐用于分析）
```sql
-- 过滤所有异常数据
WHERE fare_amount >= 0
  AND total_amount >= 0
  AND trip_distance >= 0
  AND pickup_datetime < dropoff_datetime
  AND trip_distance < 1000
  AND fare_amount < 10000
```

### 方案2: 智能去重（推荐用于事实表）
```sql
-- 使用 row_number() 按优先级选择最佳记录
row_number() over (
    partition by vendor_id, pickup_datetime, service_type, dropoff_datetime
    order by
        -- 1. 优先正常付款方式
        case when payment_type in (1, 2) then 0 else 1 end,
        -- 2. 选择较大的金额（更完整）
        total_amount desc,
        -- 3. 选择较大的距离
        trip_distance desc,
        -- 4. 有乘客数的记录
        case when passenger_count > 0 then 0 else 1 end
)
```

### 方案3: 标记而不删除（用于审计）
```sql
-- 添加 data_quality_flag
case 
    when fare_amount < 0 then 'NEGATIVE_FARE'
    when pickup_datetime = dropoff_datetime then 'INSTANT_TRIP'
    when trip_distance > 1000 then 'ABNORMAL_DISTANCE'
    else 'VALID'
end as data_quality_flag
```

---

## 📊 如何使用分析模型

### 1. 查看总体统计
```bash
cd /Users/xinglingao/workshop/DE-ZoomCamp/Module-4-analytics-engineering/taxi_rides_ny
uv run dbt run --select duplicate_summary
uv run duckdb taxi_rides_ny.duckdb -markdown -c "SELECT * FROM dev.duplicate_summary"
```

### 2. 查看详细分析
```bash
uv run dbt run --select duplicate_analysis
uv run duckdb taxi_rides_ny.duckdb -c "
    SELECT * FROM dev.duplicate_analysis 
    WHERE duplicate_type = 'PARTIAL_DUPLICATE' 
    LIMIT 10
"
```

### 3. 查看根本原因分类
```bash
uv run dbt run --select duplicate_root_cause_analysis
uv run duckdb taxi_rides_ny.duckdb -markdown -c "
    SELECT * FROM dev.duplicate_root_cause_analysis 
    ORDER BY total_records_affected DESC
"
```

### 4. 使用改进的fct_trips
```bash
uv run dbt run --select fct_trips_improved
```

---

## ✅ 下一步行动

1. **立即**: 使用 `fct_trips_improved.sql` 替换现有的 `fct_trips.sql`
2. **短期**: 与数据源团队沟通，修复负数值问题
3. **中期**: 实施数据质量检查（dbt tests）
4. **长期**: 建立数据治理流程，防止未来出现类似问题

---

## 🔗 相关文件

- [duplicate_summary.sql](models/marts/duplicate_summary.sql) - 总体统计
- [duplicate_analysis.sql](models/marts/duplicate_analysis.sql) - 详细分析  
- [duplicate_root_cause_analysis.sql](models/marts/duplicate_root_cause_analysis.sql) - 根本原因
- [fct_trips_improved.sql](models/marts/fct_trips_improved.sql) - 改进的事实表

---

**报告生成时间**: 2026-02-15
**数据范围**: 114,827,251 条记录
**分析工具**: dbt + DuckDB
