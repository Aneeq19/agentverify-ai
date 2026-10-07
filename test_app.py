"""Exercise actual Streamlit interaction and export state offline."""
from streamlit.testing.v1 import AppTest


def button(app, label):
    return next(b for b in app.button if b.label == label)


def test_all_demo_scenarios_and_review_status():
    app = AppTest.from_file("app.py", default_timeout=20).run()
    assert not app.exception
    for name in ["Incomplete crown case", "Synthetic dental benefits",
                 "Medical-only response", "Source error", "Conflicting annual maximum"]:
        button(app, name).click().run()
        button(app, "Prepare review").click().run()
        assert not app.exception
        review = app.session_state["review"]
        assert review is not None
        assert len(app.dataframe) == 1
    next(c for c in app.checkbox if c.label == "I reviewed this fictional example").check().run()
    assert not app.exception
    assert app.session_state["review"].review_status == "Reviewed fictional example"
    button(app, "Synthetic dental benefits").click().run()
    button(app, "Prepare review").click().run()
    assert app.session_state["review"].review_status == "Needs review"


def test_stedi_saved_example_and_knowledge_abstention():
    app = AppTest.from_file("app.py", default_timeout=20).run()
    button(app, "Review saved Stedi example").click().run()
    assert not app.exception
    result = app.session_state["stedi_review"]
    dental = next(f for f in result.fields if f.name == "Dental coverage")
    assert dental.value == "NON_COVERED"
    next(t for t in app.text_input if t.label == "Search your workflow knowledge").set_value("volcano astrophysics").run()
    assert any("Not found" in i.value for i in app.info)


def test_openai_missing_credentials_keeps_review_and_limits_attempts(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    app = AppTest.from_file("app.py", default_timeout=20).run()
    next(r for r in app.radio if r.label == "Preparation mode").set_value("OpenAI assisted").run()
    button(app, "Synthetic dental benefits").click().run()
    button(app, "Prepare review").click().run()
    expected = app.session_state["review"].fields
    button(app, "Prioritize with OpenAI").click().run()
    assert not app.exception
    assert app.session_state["review"].fields == expected
    assert "configure" in app.session_state["review"].ai_status
    button(app, "Prioritize with OpenAI").click().run()
    assert app.session_state["ai_count"] == 1  # Cached identical request.
