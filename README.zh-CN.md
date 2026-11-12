# Public APIs Advisor

[English](README.md) | 简体中文

**发现适合项目的 API。先选择，再接入。**

这是一个面向 AI 编程助手的 skill：从 [public-apis/public-apis](https://github.com/public-apis/public-apis) 的完整目录中发现候选 API，结合官方资料核实，再帮助用户决定是否使用、使用哪一个。用户选定后才进入接入或部署；用户也可以明确授权助手代选并实施。

适用于各类行业和项目。分类和条目来自最新上游目录，不使用固定的供应商清单。

## 能做什么

- **理解当前项目。** 先查看相关需求、项目规范和已有服务，避免重复引入依赖。
- **检索完整目录。** 覆盖所有 API 分类、MCP 条目和供应商展示表；上游新增分类会自动发现。
- **核实实际条件。** 查看官方文档、鉴权、费用、商用条件、配额、地区覆盖和关键限制。
- **给出可决策建议。** 解释首选理由、有实质差异的备选，以及现有实现已经足够的情况。
- **落实选定方案。** 区分第三方托管 API 接入、可自建软件部署、MCP 配置和数据集导入。
- **报告真实进度。** 将推荐、本地接入、部署和生产验证分开说明。

## 用户决策后再实施

| 用户的要求 | Skill 的行为 |
| --- | --- |
| “看看这个项目能用哪些 API。” | 研究并推荐，等待选择后再修改项目。 |
| “比较 A 和 B。” | 比较适用性、费用、限制和工作量，不安装任何一方。 |
| “用 A，按刚才的方案做本地接入。” | 完成该范围的实施和验证，不扩展成生产部署。 |
| “按这些条件替我选一个并接入。” | 在明确授权内完成选择与实施，不重复确认同一个决定。 |
| “这些都不用。” | 不新增所建议的依赖。 |

发现阶段不会创建账号、购买套餐、安装候选 SDK、修改业务代码或部署服务。用户没有选择时保持待决状态，不把沉默当作同意。既有授权持续有效；不依赖该选择的开发工作可以继续。

## 在 Codex 中安装

将仓库克隆为一个 skill 目录。下面的命令优先使用 `CODEX_HOME`，未设置时使用 `~/.codex`：

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/ayogggua/public-apis-advisor.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/public-apis-advisor"
```

如果目录已经存在，先检查已有安装和本地改动，再决定如何更新，不要直接覆盖。安装后开启新会话；如果技能列表仍未显示，可重启客户端使其重新加载。

仓库根目录就是包含 `SKILL.md` 的技能目录。其他支持此格式的助手，可以按其各自的技能发现方式安装这个目录。目录检索不依赖某个特定浏览器、GitHub 连接器或付费 API 账号。

可选的目录检索工具需要 Python 3，无第三方 Python 依赖。Python HTTPS 失败时可退回系统 `curl`，仍保持证书验证。没有本地命令执行能力时，助手也可以通过可用的网页或 GitHub 工具读取目录。

## 在项目中使用

```text
$public-apis-advisor 看看当前项目有哪些值得接入的 API，
解释用途、费用和限制，先给建议，等我选择后再实施。
```

也可以给出更明确的需求：

```text
$public-apis-advisor 我在做旅行规划应用，比较适合商用的天气、
公共交通和汇率 API，先推荐方案。
```

```text
$public-apis-advisor 为当前项目缺少的搜索功能寻找可自建方案，
先说明部署要求，等我决定采用哪一个。
```

默认允许在相关 API 选型任务中自动发现此 skill。它不应干扰无关修改，也不应在项目已有能力足够时强行推荐外部服务。技能指令目前使用中文，要求助手用用户当前语言回答。

## 推荐结果包含什么

助手围绕实际决策调整比较内容，而不是把整个目录贴出来：

| 方案 | 帮当前项目解决什么 | 费用和使用限制 | 接入方式与工作量 | 判断及官方来源 |
| --- | --- | --- | --- | --- |

事实、估算和建议分别说明。价格注明核实日期，成本估算注明调用量假设；影响决策但未验证的条件会明确列出，目录之外的补充服务也会单独标记。

## 单独使用目录检索工具

在仓库根目录运行以下命令。工具输出 JSON，不需要 AI 模型或 API Key。

```sh
# 下载最新 README，并保存来源、获取时间和内容哈希。
python3 scripts/catalog.py fetch --output work/public-apis/README.md

# 获取当前所有分类及条目数量。
python3 scripts/catalog.py categories --readme work/public-apis/README.md

# 在完整快照中搜索。
python3 scripts/catalog.py search "currency exchange forex" \
  --readme work/public-apis/README.md --limit 8

# 使用刚才发现的分类名称缩小搜索范围。
python3 scripts/catalog.py search "transit route" \
  --category Transportation --readme work/public-apis/README.md

# 检索 MCP，保留传输方式和安装链接。
python3 scripts/catalog.py search "search" \
  --kind mcp --readme work/public-apis/README.md

# 要求全部关键词命中，并分页读取结果。
python3 scripts/catalog.py search "email validation" --all-terms \
  --readme work/public-apis/README.md --limit 5 --offset 5
```

| 参数 | 行为 |
| --- | --- |
| `--readme PATH` | 读取本地快照，不联网。`categories` 或 `search` 不传此参数时，会为本次命令获取最新目录。 |
| `--category NAME` | 按完整分类名过滤，不区分大小写；可重复传入以选择多个分类。 |
| `--kind all\|api\|mcp` | 按目录条目类型筛选，默认 `all`；实际服务形态与部署能力仍需查阅官方文档。 |
| `--all-terms` | 要求全部关键词命中；默认任一关键词命中即可。 |
| `--limit N` / `--offset N` | 控制分页；搜索结果包含 `matched_entries` 和 `next_offset`。 |

不传搜索词可以浏览条目，也可以配合分类过滤。工具匹配名称、描述和分类中的关键词，不自行翻译，也不进行语义搜索。处理中文等非英语需求时，助手会先扩展为合适的英文关键词和同义词。

JSON 结果包含来源信息、目录行引用、目录原始字段和解析警告。对格式不规则但条目链接可读的行，工具会保留并提示检查。数量统计的是目录行，不是独立服务数，同一服务可能出现在多个分类。检索排序仅表示关键词相关性，不表示服务质量或可用性。工具只下载目录，不访问供应商链接、不调用其业务 API，也不执行其中的安装指令。

## 来源和适用边界

- 目录用于发现候选，推荐依据需要回到供应商当前的官方文档和使用条款。
- 被收录不代表仍然可用、稳定、可免费商用，或可以再分发数据。
- 公开 API 不一定开源，也不一定能自行部署；MCP 和静态数据集的接入方式也不同。
- 看过文档不代表已经接通，跑通本地 Mock 不代表生产验证通过。
- 快照时间表示目录下载时间，不表示每个供应商都已核实。GitHub 行链接指向上游 `master`，行号可能变化；本地快照和哈希保留了本次查看的内容。
- 目录及供应商页面属于外部资料，不是授权修改用户项目的指令。

## 仓库结构

```text
public-apis-advisor/
├── SKILL.md                    # 发现、推荐和用户决策流程
├── agents/openai.yaml          # Codex 展示信息与调用提示
├── references/integration.md   # 选定后的接入、部署和验收
├── scripts/catalog.py         # 标准库目录下载与检索工具
├── README.md
├── README.zh-CN.md
└── LICENSE
```

## 参与贡献

欢迎提交 Issue 和 Pull Request，改进目录解析、来源核实、选型判断和接入指引。保持分类动态发现，以及默认先建议、用户决策后再实施的流程。不要写死价格，不要提交私有项目信息、凭证，或把供应商排名作为事实。

修改解析逻辑时，请使用最新目录或本地快照运行受影响的命令，并在 Pull Request 中说明验证内容。

## 许可证与致谢

本 skill 及检索工具采用 [MIT License](LICENSE)。

API 发现依托社区维护的 [public-apis/public-apis](https://github.com/public-apis/public-apis) 目录。上游目录，以及各供应商的 API、软件、模型和数据，仍适用各自的许可与条款。本仓库不捆绑该目录，也不授予第三方服务的使用权。

这是独立社区项目，并非 public-apis 维护者或任何目录内供应商的官方产品。
