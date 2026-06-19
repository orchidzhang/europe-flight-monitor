from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import unescape
from typing import Iterable

import dateparser
import requests
from bs4 import BeautifulSoup
from dateparser.search import search_dates

from models.flight import FlightDeal
from services.currency import CurrencyConverter
from sources.base import FlightSource


@dataclass
class Article:
    title: str
    url: str
    summary: str


class SecretFlyingSource(FlightSource):
    name = "Secret Flying"
    feed_url = "https://www.secretflying.com/feed/"
    home_url = "https://www.secretflying.com/"

    ORIGIN_PATTERNS = {
        "HKG": [r"\bHKG\b", r"\bHong Kong\b", r"香港"],
        "SZX": [r"\bSZX\b", r"\bShenzhen\b", r"深圳"],
        "CAN": [r"\bCAN\b", r"\bGuangzhou\b", r"广州"],
    }

    ROUND_TRIP_PATTERNS = [
        r"\breturn\b",
        r"\bround trip\b",
        r"\bround-trip\b",
        r"\broundtrip\b",
        r"往返",
    ]

    OPEN_JAW_PATTERNS = [
        r"\bopen jaw\b",
        r"\bmulti-city\b",
        r"\bdifferent return city\b",
        r"开口",
        r"异地返回",
    ]

    COUNTRY_PATTERNS = {
        "Albania": ["Albania", "阿尔巴尼亚"],
        "Andorra": ["Andorra", "安道尔"],
        "Austria": ["Austria", "奥地利"],
        "Belarus": ["Belarus", "白俄罗斯"],
        "Belgium": ["Belgium", "比利时"],
        "Bosnia and Herzegovina": ["Bosnia", "Herzegovina", "波黑", "波斯尼亚"],
        "Bulgaria": ["Bulgaria", "保加利亚"],
        "Croatia": ["Croatia", "克罗地亚"],
        "Cyprus": ["Cyprus", "塞浦路斯"],
        "Czech Republic": ["Czech", "Czechia", "Prague", "捷克", "布拉格"],
        "Denmark": ["Denmark", "Copenhagen", "丹麦", "哥本哈根"],
        "Estonia": ["Estonia", "Tallinn", "爱沙尼亚", "塔林"],
        "Finland": ["Finland", "Helsinki", "芬兰", "赫尔辛基"],
        "France": ["France", "Paris", "Nice", "Lyon", "法国", "巴黎", "尼斯", "里昂"],
        "Germany": ["Germany", "Frankfurt", "Munich", "Berlin", "Dusseldorf", "德国", "法兰克福", "慕尼黑", "柏林", "杜塞尔多夫"],
        "Greece": ["Greece", "Athens", "Santorini", "希腊", "雅典", "圣托里尼"],
        "Hungary": ["Hungary", "Budapest", "匈牙利", "布达佩斯"],
        "Iceland": ["Iceland", "Reykjavik", "冰岛", "雷克雅未克"],
        "Ireland": ["Ireland", "Dublin", "爱尔兰", "都柏林"],
        "Italy": ["Italy", "Rome", "Milan", "Venice", "Florence", "Bologna", "意大利", "罗马", "米兰", "威尼斯", "佛罗伦萨", "博洛尼亚"],
        "Kosovo": ["Kosovo", "科索沃"],
        "Latvia": ["Latvia", "Riga", "拉脱维亚", "里加"],
        "Liechtenstein": ["Liechtenstein", "列支敦士登"],
        "Lithuania": ["Lithuania", "Vilnius", "立陶宛", "维尔纽斯"],
        "Luxembourg": ["Luxembourg", "卢森堡"],
        "Malta": ["Malta", "马耳他"],
        "Moldova": ["Moldova", "摩尔多瓦"],
        "Monaco": ["Monaco", "摩纳哥"],
        "Montenegro": ["Montenegro", "黑山"],
        "Netherlands": ["Netherlands", "Amsterdam", "Holland", "荷兰", "阿姆斯特丹"],
        "North Macedonia": ["Macedonia", "Skopje", "北马其顿"],
        "Norway": ["Norway", "Oslo", "挪威", "奥斯陆"],
        "Poland": ["Poland", "Warsaw", "Krakow", "波兰", "华沙", "克拉科夫"],
        "Portugal": ["Portugal", "Lisbon", "Porto", "葡萄牙", "里斯本", "波尔图"],
        "Romania": ["Romania", "Bucharest", "罗马尼亚", "布加勒斯特"],
        "San Marino": ["San Marino", "圣马力诺"],
        "Serbia": ["Serbia", "Belgrade", "塞尔维亚", "贝尔格莱德"],
        "Slovakia": ["Slovakia", "Bratislava", "斯洛伐克"],
        "Slovenia": ["Slovenia", "Ljubljana", "斯洛文尼亚"],
        "Spain": ["Spain", "Madrid", "Barcelona", "Malaga", "西班牙", "马德里", "巴塞罗那", "马拉加"],
        "Sweden": ["Sweden", "Stockholm", "Gothenburg", "瑞典", "斯德哥尔摩"],
        "Switzerland": ["Switzerland", "Zurich", "Geneva", "瑞士", "苏黎世", "日内瓦"],
        "Turkey": ["Turkey", "Istanbul", "Turkiye", "土耳其", "伊斯坦布尔"],
        "Ukraine": ["Ukraine", "Kyiv", "乌克兰", "基辅"],
        "United Kingdom": ["United Kingdom", "England", "Scotland", "Wales", "Northern Ireland", "Britain", "London", "Manchester", "英国", "伦敦", "曼彻斯特"],
        "Vatican City": ["Vatican", "梵蒂冈"],
    }

    AIRPORT_CITY_PATTERNS = {
        "Amsterdam AMS": ["Amsterdam", "AMS", "阿姆斯特丹"],
        "Athens ATH": ["Athens", "ATH", "雅典"],
        "Barcelona BCN": ["Barcelona", "BCN", "巴塞罗那"],
        "Berlin BER": ["Berlin", "BER", "柏林"],
        "Brussels BRU": ["Brussels", "BRU", "布鲁塞尔"],
        "Copenhagen CPH": ["Copenhagen", "CPH", "哥本哈根"],
        "Frankfurt FRA": ["Frankfurt", "FRA", "法兰克福"],
        "Geneva GVA": ["Geneva", "GVA", "日内瓦"],
        "Helsinki HEL": ["Helsinki", "HEL", "赫尔辛基"],
        "Istanbul IST": ["Istanbul", "IST", "伊斯坦布尔"],
        "Lisbon LIS": ["Lisbon", "LIS", "里斯本"],
        "Madrid MAD": ["Madrid", "MAD", "马德里"],
        "Milan MXP": ["Milan", "MXP", "Malpensa", "米兰"],
        "Munich MUC": ["Munich", "MUC", "慕尼黑"],
        "Oslo OSL": ["Oslo", "OSL", "奥斯陆"],
        "Paris CDG": ["Paris", "CDG", "巴黎"],
        "Prague PRG": ["Prague", "PRG", "布拉格"],
        "Rome FCO": ["Rome", "FCO", "罗马"],
        "Stockholm ARN": ["Stockholm", "ARN", "斯德哥尔摩"],
        "Vienna VIE": ["Vienna", "VIE", "维也纳"],
        "Warsaw WAW": ["Warsaw", "WAW", "华沙"],
        "Zurich ZRH": ["Zurich", "ZRH", "苏黎世"],
    }

    def __init__(self, timeout: int = 30, limit: int = 30) -> None:
        self.timeout = timeout
        self.limit = limit
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (compatible; EuropeFlightDealMonitor/1.0; "
                    "+https://github.com/)"
                )
            }
        )
        self.converter = CurrencyConverter()

    def fetch(self) -> list[FlightDeal]:
        articles = self._fetch_feed()
        deals: list[FlightDeal] = []

        for article in articles[: self.limit]:
            text = "" if "skyscanner." in article.summary else self._fetch_article_text(article.url)
            raw_text = self._clean_text(f"{article.title}\n{article.summary}\n{text}")
            deal = self._parse_article(article, raw_text)
            if deal is not None:
                deals.append(deal)

        return deals

    def _fetch_feed(self) -> list[Article]:
        try:
            response = self.session.get(self.feed_url, timeout=self.timeout)
            response.raise_for_status()
            if self._is_cloudflare_challenge(response.text):
                raise requests.RequestException("Cloudflare challenge returned for RSS feed")
        except requests.RequestException as exc:
            print(f"RSS feed unavailable, falling back to homepage cards: {exc}")
            return self._fetch_homepage_articles()

        soup = BeautifulSoup(response.content, "xml")

        articles: list[Article] = []
        for item in soup.find_all("item"):
            title = self._node_text(item, "title")
            url = self._node_text(item, "link")
            summary = self._node_text(item, "description")
            if title and url:
                articles.append(Article(title=title, url=url, summary=summary))

        return articles

    def _fetch_homepage_articles(self) -> list[Article]:
        response = self.session.get(self.home_url, timeout=self.timeout)
        response.raise_for_status()
        if self._is_cloudflare_challenge(response.text):
            raise RuntimeError("Secret Flying homepage returned a Cloudflare challenge")

        soup = BeautifulSoup(response.text, "html.parser")
        articles: list[Article] = []
        seen_urls: set[str] = set()

        for card in soup.find_all("article"):
            post_links = [
                link.get("href", "").strip()
                for link in card.find_all("a")
                if "/posts/" in link.get("href", "")
            ]
            if not post_links:
                continue

            url = post_links[0]
            if url in seen_urls:
                continue
            seen_urls.add(url)

            title_node = card.find(["h1", "h2", "h3"])
            title = title_node.get_text(" ", strip=True) if title_node else ""
            summary = card.get_text(" ", strip=True)
            href_text = " ".join(post_links)
            skyscanner_links = [
                link.get("href", "").strip()
                for link in card.find_all("a")
                if "skyscanner." in link.get("href", "")
            ]
            if skyscanner_links:
                href_text = f"{href_text} {' '.join(skyscanner_links)}"

            if title and url:
                articles.append(Article(title=title, url=url, summary=f"{summary} {href_text}"))

        print(f"Found {len(articles)} homepage cards from Secret Flying.")
        return articles

    def _fetch_article_text(self, url: str) -> str:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            if self._is_cloudflare_challenge(response.text):
                raise requests.RequestException("Cloudflare challenge returned for article")
        except requests.RequestException as exc:
            print(f"Failed to fetch article {url}: {exc}")
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("article") or soup.find("main") or soup.body
        if article is None:
            return ""

        for tag in article(["script", "style", "noscript"]):
            tag.decompose()

        return article.get_text(" ", strip=True)

    def _parse_article(self, article: Article, raw_text: str) -> FlightDeal | None:
        origin = self._detect_origin(raw_text)
        destination_country = self._detect_country(raw_text)
        price_cny, currency = self._detect_price(raw_text)
        departure_date, return_date = self._detect_dates(raw_text)
        trip_type = self._detect_trip_type(raw_text)
        destination = self._detect_destination(raw_text, destination_country)

        if not all([origin, destination_country, price_cny, departure_date, trip_type]):
            return None

        return FlightDeal(
            source=self.name,
            title=article.title,
            origin=origin,
            destination=destination,
            destination_country=destination_country,
            price_cny=price_cny,
            currency=currency,
            trip_type=trip_type,
            departure_date=departure_date,
            return_date=return_date,
            url=article.url,
            raw_text=raw_text,
        )

    def _detect_origin(self, text: str) -> str:
        for code, patterns in self.ORIGIN_PATTERNS.items():
            if self._contains_any(text, patterns):
                return code
        return ""

    def _detect_country(self, text: str) -> str:
        for country, patterns in self.COUNTRY_PATTERNS.items():
            if self._contains_any(text, patterns):
                return country
        return ""

    def _detect_destination(self, text: str, country: str) -> str:
        for city, patterns in self.AIRPORT_CITY_PATTERNS.items():
            if self._contains_any(text, patterns):
                return city
        return country

    def _detect_trip_type(self, text: str) -> str:
        if self._contains_any(text, self.OPEN_JAW_PATTERNS):
            return "open_jaw"
        if self._contains_any(text, self.ROUND_TRIP_PATTERNS):
            return "round_trip"
        return ""

    def _detect_price(self, text: str) -> tuple[int, str]:
        patterns = [
            r"(?P<currency>RMB|CNY|¥|￥)\s*(?P<amount>[0-9][0-9,]*(?:\.\d+)?)",
            r"(?P<amount>[0-9][0-9,]*(?:\.\d+)?)\s*(?P<currency>RMB|CNY|¥|￥)",
            r"(?P<currency>EUR|USD|HKD|GBP|JPY|SGD|€|\$|HK\$|£)\s*(?P<amount>[0-9][0-9,]*(?:\.\d+)?)",
            r"(?P<amount>[0-9][0-9,]*(?:\.\d+)?)\s*(?P<currency>EUR|USD|HKD|GBP|JPY|SGD|€|\$|HK\$|£)",
        ]

        prices: list[tuple[int, str]] = []
        for pattern in patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                amount = float(match.group("amount").replace(",", ""))
                currency = self.converter.normalize_currency(match.group("currency"))
                try:
                    prices.append((self.converter.to_cny(amount, currency), currency))
                except ValueError:
                    continue

        if not prices:
            return 0, ""

        return min(prices, key=lambda item: item[0])

    def _detect_dates(self, text: str) -> tuple[str, str]:
        explicit_dates = self._find_explicit_dates(text)
        if explicit_dates:
            dates = sorted(set(explicit_dates))
            departure = dates[0].isoformat()
            return_date = dates[1].isoformat() if len(dates) > 1 else ""
            return departure, return_date

        parsed = search_dates(
            text,
            languages=["en", "zh"],
            settings={
                "PREFER_DAY_OF_MONTH": "first",
                "DATE_ORDER": "YMD",
                "REQUIRE_PARTS": ["year", "month", "day"],
                "RETURN_AS_TIMEZONE_AWARE": False,
            },
        )
        if not parsed:
            return "", ""

        dates = sorted({value.date() for _, value in parsed})
        departure = dates[0].isoformat()
        return_date = dates[1].isoformat() if len(dates) > 1 else ""
        return departure, return_date

    def _find_explicit_dates(self, text: str) -> list[date]:
        dates: list[date] = []

        numeric_patterns = [
            r"\b(2026)[-/\.](0?[1-9]|1[0-2])[-/\.](0?[1-9]|[12]\d|3[01])\b",
            r"\b(0?[1-9]|[12]\d|3[01])[-/\.](0?[1-9]|1[0-2])[-/\.](2026)\b",
        ]
        for pattern in numeric_patterns:
            for match in re.finditer(pattern, text):
                parts = match.groups()
                if len(parts[0]) == 4:
                    year, month, day = map(int, parts)
                else:
                    day, month, year = map(int, parts)
                self._append_date(dates, year, month, day)

        month_names = (
            "Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|"
            "Aug|August|Sep|Sept|September|Oct|October|Nov|November|Dec|December"
        )
        month_pattern = rf"\b(?P<day>[0-3]?\d)\s+(?P<month>{month_names})\s+(?P<year>2026)\b|\b(?P<month2>{month_names})\s+(?P<day2>[0-3]?\d),?\s+(?P<year2>2026)\b"
        for match in re.finditer(month_pattern, text, flags=re.IGNORECASE):
            if match.group("year"):
                parsed = dateparser.parse(match.group(0), languages=["en"])
            else:
                parsed = dateparser.parse(match.group(0), languages=["en"])
            if parsed:
                dates.append(parsed.date())

        return dates

    @staticmethod
    def _append_date(dates: list[date], year: int, month: int, day: int) -> None:
        try:
            dates.append(date(year, month, day))
        except ValueError:
            pass

    @staticmethod
    def _contains_any(text: str, patterns: Iterable[str]) -> bool:
        return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)

    @staticmethod
    def _node_text(parent: BeautifulSoup, name: str) -> str:
        node = parent.find(name)
        if node is None:
            return ""
        return unescape(node.get_text(" ", strip=True))

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", unescape(text)).strip()

    @staticmethod
    def _is_cloudflare_challenge(text: str) -> bool:
        lower_text = text.lower()
        return "just a moment" in lower_text and "cloudflare" in lower_text
