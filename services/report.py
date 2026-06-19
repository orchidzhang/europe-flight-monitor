from __future__ import annotations

import os
from pathlib import Path

from models.flight import FlightDeal


def write_run_report(
    source_counts: dict[str, int],
    fetched_count: int,
    matched_deals: list[FlightDeal],
    new_deals: list[FlightDeal],
    email_sent: bool,
    failed_sources: list[str],
    path: str | Path = "data/latest_report.md",
) -> None:
    report = build_run_report(
        source_counts=source_counts,
        fetched_count=fetched_count,
        matched_deals=matched_deals,
        new_deals=new_deals,
        email_sent=email_sent,
        failed_sources=failed_sources,
    )

    Path(path).write_text(report, encoding="utf-8")

    github_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if github_summary:
        with Path(github_summary).open("a", encoding="utf-8") as file:
            file.write(report)
            file.write("\n")


def build_run_report(
    source_counts: dict[str, int],
    fetched_count: int,
    matched_deals: list[FlightDeal],
    new_deals: list[FlightDeal],
    email_sent: bool,
    failed_sources: list[str],
) -> str:
    lines = [
        "# 机票监控运行报告",
        "",
        "## 本次结果",
        "",
        f"- 抓取并解析出的候选机票：{fetched_count} 条",
        f"- 符合条件的机票：{len(matched_deals)} 条",
        f"- 去重后新机票：{len(new_deals)} 条",
        f"- 是否发送邮件：{'是' if email_sent else '否'}",
    ]

    if failed_sources:
        lines.append(f"- 失败的数据源：{', '.join(failed_sources)}")

    lines.extend(["", "## 数据源", ""])
    if source_counts:
        for source, count in source_counts.items():
            lines.append(f"- {source}: {count} 条候选机票")
    else:
        lines.append("- 没有成功返回候选机票的数据源")

    lines.extend(["", "## 匹配详情", ""])
    if matched_deals:
        for index, deal in enumerate(matched_deals, 1):
            status = "新票，已尝试通知" if deal in new_deals else "之前已通知过"
            lines.extend(
                [
                    f"### {index}. {deal.title or deal.destination}",
                    "",
                    f"- 状态：{status}",
                    f"- 来源：{deal.source}",
                    f"- 航线：{deal.origin} → {deal.destination}",
                    f"- 国家：{deal.destination_country}",
                    f"- 行程类型：{deal.trip_type}",
                    f"- 价格：{deal.price_cny} RMB",
                    f"- 去程：{deal.departure_date}",
                    f"- 返程：{deal.return_date or '无'}",
                    f"- 链接：{deal.url}",
                    "",
                ]
            )
    else:
        lines.append("本次没有符合条件的新机票。")

    lines.extend(
        [
            "",
            "## 说明",
            "",
            "- 绿色成功只代表程序运行完成，不代表一定有票。",
            "- 如果符合条件的新票数量大于 0，系统会通过邮件通知。",
            "- 已通知过的同一条票会被 `data/notified.json` 去重，不会重复发送。",
        ]
    )

    return "\n".join(lines)
