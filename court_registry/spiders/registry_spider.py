import re
import scrapy
from scrapy import FormRequest, Request
from court_registry.items import DecisionItem


class RegistrySpider(scrapy.Spider):
    name = "registry"
    allowed_domains = ["reyestr.court.gov.ua"]
    start_url = "https://reyestr.court.gov.ua/"

    # Параметри пошуку (варіант 6)
    REGION_VALUE = "3"     # Вінницька область
    COURT_VALUE = "251"    # Барський районний суд Вінницької області
    INST_VALUE = "1"       # Інстанція: Перша
    ITEMS_PER_PAGE = "50"  # 10/25/50/100
    SORT_VALUE = "1"       # за датою ухвалення | за спаданням

    async def start(self):
        yield Request(self.start_url, callback=self.submit_search)

    def submit_search(self, response):
        formdata = {
            "SearchExpression": "",
            "CourtRegion": self.REGION_VALUE,
            "CourtName": self.COURT_VALUE,
            "INSType": self.INST_VALUE,

            "RegNumber": "",
            "RegDateBegin": "",
            "RegDateEnd": "",
            "ImportDateBegin": "",
            "ImportDateEnd": "",

            "PagingInfo.ItemsPerPage": self.ITEMS_PER_PAGE,
            "Sort": self.SORT_VALUE,

        }

        yield FormRequest(
            url=self.start_url,
            formdata=formdata,
            method="POST",
            callback=self.parse_results,
        )

    def parse_results(self, response):
        rows = response.css("table#tableresult tr")[1:]
        for row in rows:
            review_rel = row.css("td.RegNumber a.doc_text2::attr(href)").get(default="").strip()
            if not review_rel:
                continue
            review_url = response.urljoin(review_rel)

            case_number = row.css("td.CaseNumber::text").get(default="").strip()
            reg_date = row.css("td.RegDate::text").get(default="").strip()

            yield Request(
                review_url,
                callback=self.parse_review,
                cb_kwargs={"case_number": case_number, "reg_date": reg_date},
            )

        max_pages = int(self.crawler.settings.getint("MAX_PAGES", 3))
        base = response.url
        for page_num in range(2, max_pages + 1):
            yield Request(
                response.urljoin(f"/Page/{page_num}"),
                callback=self.parse_results,
            )

    @staticmethod
    def _clean_text(text: str, max_len: int = 400) -> str:
        t = re.sub(r"\s+", " ", text or "").strip()
        return t[:max_len].rstrip(" .,\u00A0")

    def _extract_summary_candidates(self, response):
        css_variants = [
            "#contentDecision ::text",
            "#contentDecisionText ::text",
            "#content ::text",
            "#divDecisionDocumentContent ::text",
            "#doc_text ::text",
            ".doc_text ::text",
            "article ::text",
            "pre ::text",
            "body ::text",
        ]
        for sel in css_variants:
            parts = [p.strip() for p in response.css(sel).getall()]
            text = " ".join([p for p in parts if p])
            if len(text) >= 40:
                yield text

    def parse_review(self, response, case_number: str, reg_date: str):
        summary = ""
        for cand in self._extract_summary_candidates(response):
            summary = self._clean_text(cand, max_len=400)
            if summary:
                break

        if not summary:
            title = response.css("title::text").get()
            summary = self._clean_text(title, 120) if title else "Сторінка рішення реєстру"

        yield DecisionItem(
            case_number=case_number,
            date=reg_date,
            summary=summary,
            url=response.url,
        )
