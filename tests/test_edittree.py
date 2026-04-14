"""Test that the apply method of the EditTreeNode class works as a lemmatizer rather than a paradigm completion method now
"""

from rumlem.edittree import editTree


def test_simple_replacements():
    et = editTree("fairs", "fair")
    assert et.apply("fairs") == "fair"  # lemmatization: remove 's'
    assert et.apply("disfavorerels") == "disfavorerel"

    # Str without an s at the end should not be valid for this edit tree
    assert et.apply("cat") == -1

    et = editTree("fairas", "fair")
    assert et.apply("fairas") == "fair"  # lemmatization: remove 's'
    assert et.apply("disfavorerelas") == "disfavorerel"

    # Str without an s at the end should not be valid for this edit tree
    assert et.apply("cat") == -1

def test_longer_replacements():
    """Are more complicated edit trees applied correctly? based on surmiran adj endings"""
    et = editTree("indisponsibla", "indisponsibel")

    assert et.apply("disponsibla") == "disponsibel"
    assert et.apply("alel") == -1

    et = editTree("varieida", "variia")

    assert et.apply("parieida") == "pariia"
    assert et.apply("varida") == -1
