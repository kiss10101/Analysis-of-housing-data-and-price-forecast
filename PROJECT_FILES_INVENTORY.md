# 📁 项目文件清单

## 📅 清单信息
- **生成时间**: 2025-06-22 17:40:00
- **项目版本**: v2.0
- **清单类型**: 完整文件清单

## 🗂️ 核心配置文件

### **Django配置**
| 文件路径 | 描述 | 状态 | 最后修改 |
|---------|------|------|----------|
| `manage.py` | Django管理脚本 | ✅ | 项目初始 |
| `Python租房房源数据可视化分析/settings.py` | Django主配置文件 | ✅ | 2025-06-22 |
| `Python租房房源数据可视化分析/urls.py` | 主URL配置 | ✅ | 项目初始 |
| `Python租房房源数据可视化分析/wsgi.py` | WSGI配置 | ✅ | 项目初始 |

### **应用配置**
| 文件路径 | 描述 | 状态 | 最后修改 |
|---------|------|------|----------|
| `app/urls.py` | MySQL版本URL配置 | ✅ | 项目初始 |
| `app/views.py` | MySQL版本视图函数 | ✅ | 项目初始 |
| `app/models.py` | MySQL版本数据模型 | ✅ | 项目初始 |
| `app_mongo/urls.py` | MongoDB版本URL配置 | ✅ | 2025-06-22 |
| `app_mongo/views.py` | MongoDB版本视图函数 | ✅ | 2025-06-22 |
| `app_mongo/models.py` | MongoDB版本数据模型 | ✅ | 2025-06-22 |

## 📄 模板文件

### **MySQL版本模板** (templates/)
| 文件名 | 描述 | 状态 |
|--------|------|------|
| `login.html` | 登录页面 | ✅ |
| `register.html` | 注册页面 | ✅ |
| `index.html` | 首页 | ✅ |
| `tableData.html` | 数据表格 | ✅ |
| `collectTableData.html` | 收藏数据 | ✅ |
| `selfInfo.html` | 个人信息 | ✅ |
| `houseDistribute.html` | 房源分布 | ✅ |
| `typeincity.html` | 户型占比 | ✅ |
| `housewordcloud.html` | 词云汇总 | ✅ |
| `housetyperank.html` | 房型排名 | ✅ |
| `servicemoney.html` | 价钱影响 | ✅ |
| `pricePredict.html` | 房价预测 | ✅ |

### **MongoDB版本模板** (templates/mongo/)
| 文件名 | 描述 | 状态 | 创建时间 |
|--------|------|------|----------|
| `login.html` | 登录页面 | ✅ | 2025-06-22 |
| `register.html` | 注册页面 | ✅ | 2025-06-22 |
| `index.html` | 首页 | ✅ | 2025-06-22 |
| `tableData.html` | 数据表格 | ✅ | 2025-06-22 |
| `collectTableData.html` | 收藏数据 | ✅ | 2025-06-22 |
| `selfInfo.html` | 个人信息 | ✅ | 2025-06-22 |
| `houseDistribute.html` | 房源分布 | ✅ | 2025-06-22 |
| `typeincity.html` | 户型占比 | ✅ | 2025-06-22 |
| `housewordcloud.html` | 词云汇总 | ✅ | 2025-06-22 |
| `housetyperank.html` | 房型排名 | ✅ | 2025-06-22 |
| `servicemoney.html` | 价钱影响 | ✅ | 2025-06-22 |
| `heatmap_analysis.html` | 热力图分析 | ✅ | 2025-06-22 |
| `pricePredict.html` | 房价预测 | ✅ | 2025-06-22 |

## 🎨 静态资源文件

### **CSS样式文件** (static/css/)
| 文件名 | 描述 | 状态 |
|--------|------|------|
| `bootstrap.css` | Bootstrap框架 | ✅ |
| `neon-core.css` | 核心样式 | ✅ |
| `neon-theme.css` | 主题样式 | ✅ |
| `neon-forms.css` | 表单样式 | ✅ |
| `custom.css` | 自定义样式 | ✅ |
| `entypo.css` | 图标字体 | ✅ |
| `font-awesome.min.css` | FontAwesome图标 | ✅ |

### **JavaScript文件** (static/js/)
| 文件名 | 描述 | 状态 |
|--------|------|------|
| `jquery-1.11.0.min.js` | jQuery库 | ✅ |
| `bootstrap.js` | Bootstrap脚本 | ✅ |
| `echarts.js` | ECharts图表库 | ✅ |
| `neon-api.js` | 核心API | ✅ |
| `neon-custom.js` | 自定义脚本 | ✅ |
| `datatables.min.js` | 数据表格插件 | ✅ |

## 🔧 工具脚本

### **数据迁移工具**
| 文件路径 | 描述 | 状态 | 创建时间 |
|---------|------|------|----------|
| `mongodb_integration/migrate_house_data.py` | 房源数据迁移 | ✅ | 2025-06-22 |
| `mongodb_integration/migrate_all_data.py` | 全量数据迁移 | ✅ | 2025-06-22 |

### **开发工具**
| 文件路径 | 描述 | 状态 | 创建时间 |
|---------|------|------|----------|
| `create_mongo_templates.py` | 批量模板创建 | ✅ | 2025-06-22 |

### **中间件模块**
| 文件路径 | 描述 | 状态 | 创建时间 |
|---------|------|------|----------|
| `middleware/performance_middleware.py` | 性能监控中间件 | ✅ | 2025-06-22 |
| `app_mongo/cache_utils.py` | 缓存工具模块 | ✅ | 2025-06-22 |

## 📊 数据库相关文件

### **MongoDB集成**
| 文件路径 | 描述 | 状态 |
|---------|------|------|
| `mongodb_integration/models/mongo_models.py` | MongoDB数据模型 | ✅ |
| `mongodb_integration/pipelines/mongo_pipeline.py` | MongoDB管道 | ✅ |

### **数据库配置**
| 配置项 | 值 | 状态 |
|--------|---|------|
| MySQL数据库 | guangzhou_house | ✅ |
| MongoDB数据库 | house_data | ✅ |
| MySQL端口 | 3306 | ✅ |
| MongoDB端口 | 27017 | ✅ |

## 📚 文档文件

### **项目文档**
| 文件名 | 描述 | 状态 | 创建时间 |
|--------|------|------|----------|
| `README.md` | 项目说明文档 | ✅ | 2025-06-22 |
| `PROJECT_STATUS.md` | 项目状态总览 | ✅ | 2025-06-22 |
| `CHANGELOG.md` | 更新日志 | ✅ | 2025-06-22 |
| `DOCUMENTATION_INDEX.md` | 文档索引 | ✅ | 2025-06-22 |
| `PROJECT_FILES_INVENTORY.md` | 文件清单(本文档) | ✅ | 2025-06-22 |

### **技术报告**
| 文件名 | 描述 | 状态 | 创建时间 |
|--------|------|------|----------|
| `mongo_frontend_migration_report.md` | MongoDB前端移植报告 | ✅ | 2025-06-22 |
| `performance_optimization_report.md` | 性能优化报告 | ✅ | 2025-06-22 |
| `performance_optimization_corrected_report.md` | 性能优化修正报告 | ✅ | 2025-06-22 |

## 🗃️ 媒体文件

### **用户头像** (media/)
| 文件类型 | 数量 | 状态 |
|---------|------|------|
| 用户头像图片 | 10+ | ✅ |
| 默认头像 | 1 | ✅ |

### **系统图标** (static/picture/)
| 文件名 | 描述 | 状态 |
|--------|------|------|
| `mapview.png` | 网站图标 | ✅ |

## 📈 统计信息

### **文件数量统计**
| 类型 | 数量 | 状态 |
|------|------|------|
| Python文件 | 20+ | ✅ |
| HTML模板 | 25 | ✅ |
| CSS文件 | 10+ | ✅ |
| JavaScript文件 | 15+ | ✅ |
| 文档文件 | 8 | ✅ |
| 配置文件 | 5 | ✅ |

### **代码行数统计** (估算)
| 类型 | 行数 | 占比 |
|------|------|------|
| Python代码 | 3000+ | 40% |
| HTML模板 | 2500+ | 35% |
| JavaScript | 1000+ | 15% |
| CSS样式 | 500+ | 7% |
| 配置文件 | 200+ | 3% |

## 🔍 文件状态说明

### **状态标识**
- ✅ **正常**: 文件存在且功能正常
- ⚠️ **警告**: 文件存在但可能需要更新
- ❌ **错误**: 文件缺失或有问题
- 🔄 **更新中**: 文件正在更新

### **重要文件备份**
| 原文件 | 备份文件 | 备份时间 |
|--------|----------|----------|
| `settings.py` | `settings.py.backup` | 2025-06-22 |

## 📋 维护清单

### **定期检查项目**
- [ ] 检查所有模板文件完整性
- [ ] 验证静态资源文件可访问性
- [ ] 确认数据库连接正常
- [ ] 测试所有功能模块
- [ ] 更新文档和清单

### **文件清理建议**
- [ ] 清理临时文件
- [ ] 删除未使用的静态资源
- [ ] 压缩图片文件
- [ ] 优化CSS和JavaScript文件

---

**清单维护**: 本清单应在每次重大更新后及时更新  
**最后更新**: 2025-06-22 17:40:00  
**维护人员**: AI Assistant
