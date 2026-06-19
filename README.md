# 欧洲特价机票监控器（个人版）

每天自动抓取公开机票特价信息，筛选从香港、深圳、广州出发且符合条件的欧洲机票，并通过 SMTP 邮件通知。也支持少量自定义航线低价提醒。

当前第一版数据源：

- Secret Flying

项目不包含前端、用户系统和数据库，重点是稳定定时运行，以及方便后续扩展更多数据源。

## 功能

- Python 3.12+
- GitHub Actions 每天定时运行，并支持手动触发
- SMTP 邮件通知
- 所有敏感配置通过环境变量读取
- 插件化数据源设计
- 固定汇率换算，预留后续实时汇率接口
- 使用 `data/notified.json` 避免重复通知

## 监控条件

保留同时满足以下条件的机票：

- 出发地为 `HKG`、`SZX`、`CAN`
- 可从文本中识别 `Hong Kong`、`Shenzhen`、`Guangzhou`、`香港`、`深圳`、`广州`
- 目的地为欧洲国家
- 排除 United Kingdom、England、Scotland、Wales、Northern Ireland、Britain、Ireland，以及中文 `英国`、`爱尔兰`
- 折算后总价 `<= 4000 RMB`
- 去程日期早于 `2026-10-05`
- 行程类型为 `round_trip` 或 `open_jaw`

如果无法解析去程日期，则不会发送通知。

额外自定义航线提醒：

- `TOS` 特罗姆瑟到 `TLL` 塔林，单程，出发日期在 `2027-02-01` 至 `2027-02-28`，价格 `<= 500 RMB`
- `TOS` 特罗姆瑟到 `HEL` 赫尔辛基，单程，出发日期在 `2027-02-01` 至 `2027-02-28`，价格 `<= 500 RMB`
- `PAR` 巴黎到 `HAM` 汉堡，单程，出发日期在 `2027-01-20` 至 `2027-01-31`，价格 `<= 300 RMB`

当前 Secret Flying 数据源会从公开特价文章或首页卡片中识别这些路线。要做更稳定的指定航线每日最低价监控，后续可以继续接入 Skyscanner、Trip.com 或航司 API 作为新数据源。

## 安装

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 环境变量

复制 `.env.example` 后按你的邮箱服务商填写：

```bash
cp .env.example .env
```

示例：

```text
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASSWORD=your_app_password
EMAIL_TO=orchidzhang@outlook.com
```

如果没有设置 `EMAIL_TO`，默认收件邮箱为：

```text
orchidzhang@outlook.com
```

本地运行时可以这样加载环境变量：

```bash
export SMTP_HOST=smtp.office365.com
export SMTP_PORT=587
export SMTP_USER=your_email@example.com
export SMTP_PASSWORD=your_app_password
export EMAIL_TO=orchidzhang@outlook.com
python main.py
```

## GitHub Actions 配置

在 GitHub 仓库中添加以下 Secrets：

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_TO`

工作流文件位于：

```text
.github/workflows/daily.yml
```

运行规则：

- 每天 UTC 01:00 和 UTC 09:00 自动运行
- 换算为北京时间约为每天 09:00 和 17:00
- 支持在 GitHub Actions 页面手动触发

运行后，如果发送了新通知，工作流会把更新后的 `data/notified.json` 自动提交回仓库，用于避免重复通知。

## 项目结构

```text
project/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
│
├── data/
│   └── notified.json
│
├── models/
│   └── flight.py
│
├── sources/
│   ├── base.py
│   └── secret_flying.py
│
├── services/
│   ├── filter.py
│   ├── dedupe.py
│   ├── currency.py
│   └── notifier_email.py
│
└── .github/
    └── workflows/
        └── daily.yml
```

## 数据模型

所有数据源都需要输出统一结构：

```python
{
    "source": "Secret Flying",
    "title": "",
    "origin": "",
    "destination": "",
    "destination_country": "",
    "price_cny": 0,
    "currency": "CNY",
    "trip_type": "",
    "departure_date": "",
    "return_date": "",
    "url": "",
    "raw_text": ""
}
```

## 增加新的数据源

新增一个文件，例如：

```text
sources/cathay_pacific.py
```

实现 `FlightSource` 接口：

```python
from sources.base import FlightSource
from models.flight import FlightDeal


class CathayPacificSource(FlightSource):
    name = "Cathay Pacific"

    def fetch(self) -> list[FlightDeal]:
        return []
```

然后在 `main.py` 中加入：

```python
from sources.cathay_pacific import CathayPacificSource

sources = [
    SecretFlyingSource(),
    CathayPacificSource(),
]
```

未来可按同样方式增加：

- Cathay Pacific
- Hong Kong Airlines
- Singapore Airlines
- Emirates
- Trip.com
- Skyscanner

## 去重机制

唯一键由以下字段拼接生成：

```text
origin + destination + departure_date + return_date + price
```

已通知记录保存在：

```text
data/notified.json
```

同一条记录只会通知一次。

## 邮件内容

邮件主题：

```text
发现符合条件的欧洲特价机票
```

邮件正文会包含来源、行程类型、出发地、目的地、价格、去程、返程和链接。
