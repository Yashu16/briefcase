from src.research.crustdata import evidence_from_enrichment


def test_crustdata_evidence_is_readable_and_skips_unnamed_records():
    rows = evidence_from_enrichment(
        [
            {
                "matches": [
                    {
                        "company_data": {
                            "basic_info": {"name": "Google", "website": "https://goo.gle/example"},
                            "funding": {
                                "acquisitions": [
                                    {"acquiree_company_name": "Lift Labs", "date": "2005-11-17"}
                                ]
                            },
                            "news": [{"title": "Google announces a product update"}],
                            "people": {
                                "founders": [
                                    {"name": "A named founder", "current_title": "Founder"},
                                    {"headline": "Unnamed profile"},
                                ]
                            },
                        }
                    }
                ]
            }
        ],
        "q1",
    )

    claims = [row["claim"] for row in rows]
    assert "Google has acquisition records for Lift Labs (2005-11-17)." in claims
    assert "Google news: Google announces a product update" in claims
    assert "Google leadership: A named founder (Founder)" in claims
    assert all("leader" not in claim or "leadership:" in claim for claim in claims)
    assert all("snapshot" not in claim for claim in claims)
