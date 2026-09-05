# NekroAgent 时间差感知

> 记录用户的交互时间和近期活跃事实，并以简短、温和的时间背景提供给 Agent。

## 快速开始

将整个 `nekro_plugin_timediff` 目录复制到 NekroAgent 数据目录的插件工作区：

```text
DATA_DIR/plugins/workdir/nekro_plugin_timediff/
```

确认目录中包含 `__init__.py`，然后按照 NekroAgent 的插件加载流程启动。插件只支持 OneBot V11 适配器。

## 插件结构

```text
nekro_plugin_timediff/
├── __init__.py   # 插件实例、配置与包导出
├── models.py     # 存储数据模型
├── storage.py    # PluginStore 读写
├── analysis.py   # 时间差计算
├── prompt.py     # 时间背景文本渲染
├── tracking.py   # 用户消息跟踪
├── commands.py   # 管理命令
├── lifecycle.py  # 提示词注入与资源清理
└── registry.py   # 回调注册
```

## 功能说明

- 跟踪用户最近一次交互时间和活跃时间。
- 按配置阈值计算时间间隔，并生成简短的时间背景。
- 使用一次消费式聊天缓存，将背景注入当前会话。
- 通过结构化存储数据保持跨会话状态，并兼容现有存储 schema。
- 不改变 Agent 的核心作息或频道状态。

注入文本使用稳定的结构：

```text
【时间感知】
时间间隔：...
语境提示：...
```

## 配置

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| `notice_threshold_minutes` | `30` | 触发时间背景的最小间隔，单位为分钟 |
| `blame_threshold_hours` | `4` | 显著时间间隔阈值，单位为小时；字段名为历史兼容名称 |
| `jealousy_window_minutes` | `60` | 近期活跃判定窗口，单位为分钟；字段名为历史兼容名称 |
| `abandon_days_threshold` | `3` | 长期未交互判定阈值，单位为天；字段名为历史兼容名称 |
| `abandon_active_window_minutes` | `1440` | 长期未交互后的活跃判定窗口，单位为分钟 |
| `debug_log` | `True` | 是否输出调试日志 |

## 命令与提示词

### `update_last_seen`

管理员命令，用于修正用户的交互时间和活跃时间。支持同步设置一个时间，也支持分别设置两个时间。

### `time_diff_context`

在当前聊天中消费一次缓存的时间背景，并提供给 Agent。缓存按聊天键隔离。

## 存储兼容

插件使用以下固定存储范围和键名：

```text
范围：timediff_global_scope
键名：interaction_data_v2
```

存储内容使用结构化 JSON，schema 版本保持为 `1.0.0`。调整配置或代码时不要直接删除已有数据。

## 开发

修改后可执行插件目录下的 Python 语法检查：

```powershell
python -m py_compile *.py
```

时间差计算可通过独立函数进行静态和单元测试。完整行为需要真实的 NekroAgent、OneBot V11、PluginStore 和提示词注入环境验证。

## 相关资源

- [NekroAgent 官方文档](https://doc.nekro.ai/)
- [插件开发快速上手](https://doc.nekro.ai/docs/04_plugin_dev/01_quick_start.html)
- [Nekro 插件模板](https://github.com/KroMiose/nekro-plugin-template)

## 许可证

本项目当前未单独声明许可证。
