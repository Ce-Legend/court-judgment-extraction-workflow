# Court Judgment Extraction Workflow

这个项目来自一次裁判文书数据整理任务。流程从浏览器里已经打开的裁判文书网搜索结果开始，逐页读取案件列表，进入详情页抓取正文，边跑边写 CSV，后面再把判决书文本整理成可以分析的字段。

我觉得它值得单独放进作品集，是因为它记录了一类很常见的真实问题：网页能打开，结果也能看到，但要稳定拿到几百份正文、不中断丢数据、最后还能整理成 Excel 和结构化字段，需要一整条可恢复的工作流。

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-browser%20control-43B02A?logo=selenium&logoColor=white)
![CSV](https://img.shields.io/badge/output-CSV%20%2F%20Excel-0F766E)
![License](https://img.shields.io/badge/license-MIT-green)

```mermaid
flowchart LR
    A[手动打开搜索结果页] --> B[连接调试端口浏览器]
    B --> C[解析列表页案件]
    C --> D[点击详情页]
    D --> E[抽取判决书正文]
    E --> F[逐条追加 CSV]
    F --> G[中断后续跑]
    G --> H[合并清洗]
    H --> I[字段抽取 / Excel 交付]
```

关键词：裁判文书、法律文本抽取、Selenium、浏览器接管、断点续跑、CSV 清洗、判决书结构化。

## 🚀 先跑文本解析测试

公开版不附带真实文书数据。你可以先跑脱敏样例，确认解析和清洗逻辑：

```bash
git clone https://github.com/Ce-Legend/court-judgment-extraction-workflow.git
cd court-judgment-extraction-workflow
python -m pip install -e .[dev]
python -m pytest -q
```

完整采集需要 Windows/Edge 或可调试浏览器环境：

```powershell
msedge.exe --remote-debugging-port=9222 --user-data-dir="C:\selenium\edge_profile"
python start.py
```

运行前先在浏览器里完成检索，确认页面上已经能看到案件列表。

## 📌 这次项目真正解决了什么

### 浏览器接管

文书网这类页面适合保留人工操作入口。搜索条件、登录状态、页面确认可以先在浏览器里处理，脚本只接管重复动作：读列表、点详情、抽正文、保存结果。

`start.py` 通过 `127.0.0.1:9222` 连接已经打开的 Edge 浏览器。这样遇到页面加载异常或需要人工确认时，不会把整个流程封死在无头脚本里。

### 边爬边存

详情页正文需要逐条打开，跑几百条时中断很正常。项目每拿到一条正文就立刻追加到 CSV，尽量减少中断损失。

这样任务可以从已完成数量继续推进。原项目里保留了 `continue_from_325.py`，能看出这套流程确实经历过中途续跑。

### 正文清洗和字段抽取

采到的正文里常混有网页导航、元信息、重复行和换行格式问题。`merge_and_clean.py` 负责把噪音行去掉，`fix_csv_format.py` 处理正文换行导致的 CSV 阅读问题，`export_to_excel.py` 再导出给人看的 Excel。

`extractor/parser.py` 会从判决书文本里提取案号、法院、日期、案由、被告人性别、伤害程度、赔偿金额、刑期、判决结果和审理程序。它更像一层轻量规则引擎，方便后续做统计和人工复核。

## 📁 公开版保留的内容

```text
.
├── start.py                    # 列表页 + 详情页正文采集，逐条写 CSV
├── continue_from_325.py         # 续跑脚本样例
├── merge_and_clean.py           # 合并 CSV、清理正文噪音
├── fix_csv_format.py            # 修复长文本 CSV 阅读问题
├── export_to_excel.py           # 导出 Excel
├── crawler/
│   ├── searcher.py              # 搜索页和列表页解析
│   └── detail.py                # 详情页正文抽取
├── extractor/
│   └── parser.py                # 判决书字段抽取
├── examples/                    # 脱敏样例
└── tests/                       # 不依赖真实网站的解析测试
```

## 🧩 输出字段

采集阶段的 CSV 主要字段：

```text
序号, 标题, 法院, 案号, 日期, 链接, 正文
```

结构化阶段会补充：

```text
案由, 被告人性别, 伤害程度, 赔偿金额, 判决刑期, 判决结果, 审理程序
```

样例见 [examples/sample_cases.csv](examples/sample_cases.csv) 和 [examples/sample_judgment.txt](examples/sample_judgment.txt)。

## ⚙️ 运行边界

这个仓库保留工作流和解析方法，样例数据为脱敏自造文本。

真实采集时建议低频运行，遇到页面阻断或验证提示就回到浏览器里人工确认。脚本的价值在于把可重复步骤接住，把进度和结果保存好。

## ✅ 测试

```bash
python -m pytest -q
```

测试覆盖：

- 判决书核心字段解析。
- 中文刑期抽取。
- 赔偿金额抽取。
- 正文噪音清理和重复行处理。

## License

MIT
