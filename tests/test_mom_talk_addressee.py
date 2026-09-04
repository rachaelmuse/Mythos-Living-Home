"""Mom talk addressee: named resident wins over default Gemini."""
from __future__ import annotations

from living_home import _named_addressee, _resolve_mom_addressee


def test_hello_aster_routes_to_aster_not_gemini():
    assert _named_addressee("hello aster where are you?") == "aster"
    assert _resolve_mom_addressee("gemini", "hello aster where are you?") == "aster"


def test_proceed_gemini_keeps_gemini():
    assert _named_addressee("proceed gemini") == "gemini"
    assert _resolve_mom_addressee("gemini", "proceed gemini") == "gemini"


def test_are_you_ok_without_name_keeps_focus():
    assert _named_addressee("are you ok?") is None
    assert _resolve_mom_addressee("aster", "are you ok?") == "aster"
    assert _resolve_mom_addressee("gemini", "are you ok?") == "gemini"


def test_empty_focus_without_name_defaults_gemini():
    assert _resolve_mom_addressee("", "are you ok?") == "gemini"
    assert _resolve_mom_addressee("all", "good morning") == "gemini"


def test_does_not_treat_mom_as_addressee():
    assert _named_addressee("Mom, are you ok?") is None
    assert _resolve_mom_addressee("aster", "i am sorry.") == "aster"
