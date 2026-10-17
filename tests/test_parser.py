import pytest

from app.parser import detect_error_type, parse_junit

SAMPLE_XML = b"""<?xml version="1.0" encoding="utf-8"?>
<testsuites name="pytest tests">
  <testsuite name="pytest" errors="0" failures="2" skipped="0" tests="4">
    <testcase classname="tests.test_pricing" name="test_discount_ten_percent" time="0.001">
      <failure message="assert 89.0 == 90.0">def test_discount_ten_percent():
&gt;       assert apply_discount(100.0, 10) == 90.0
E       assert 89.0 == 90.0</failure>
    </testcase>
    <testcase classname="tests.test_inventory" name="test_supplier_price_lookup" time="0.002">
      <failure message="TimeoutError: supplier lookup for book exceeded 0.2 seconds">trace here</failure>
    </testcase>
    <testcase classname="tests.test_cart" name="test_subtotal_counts_quantity" time="0.001" />
    <testcase classname="tests.test_cart" name="test_add_rejects_zero_quantity" time="0.001" />
  </testsuite>
</testsuites>
"""


def test_counts_total_and_failures():
    report = parse_junit(SAMPLE_XML)
    assert report.total_tests == 4
    assert len(report.failures) == 2


def test_assertion_failure_fields():
    failure = parse_junit(SAMPLE_XML).failures[0]
    assert failure.test_name == "test_discount_ten_percent"
    assert failure.classname == "tests.test_pricing"
    assert failure.error_type == "AssertionError"
    assert "89.0 == 90.0" in failure.stack_trace


def test_exception_failure_error_type():
    failure = parse_junit(SAMPLE_XML).failures[1]
    assert failure.error_type == "TimeoutError"


def test_bare_testsuite_root_is_accepted():
    xml = b'<testsuite tests="1"><testcase classname="a" name="b" time="0.1"/></testsuite>'
    assert parse_junit(xml).total_tests == 1


def test_error_element_counts_as_failure():
    xml = b'<testsuite><testcase classname="a" name="b"><error message="KeyError: 1">x</error></testcase></testsuite>'
    report = parse_junit(xml)
    assert report.failures[0].error_type == "KeyError"


def test_invalid_xml_raises():
    with pytest.raises(ValueError):
        parse_junit(b"not xml at all")


def test_non_junit_root_raises():
    with pytest.raises(ValueError):
        parse_junit(b"<html></html>")


@pytest.mark.parametrize(
    "message,expected",
    [
        ("assert 1 == 2", "AssertionError"),
        ("KeyError: 'ghost'", "KeyError"),
        ("app.inventory.OutOfStockError: not enough book", "OutOfStockError"),
        ("something odd happened", "UnknownError"),
    ],
)
def test_detect_error_type(message, expected):
    assert detect_error_type(message) == expected