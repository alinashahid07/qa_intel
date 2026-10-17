import re
from dataclasses import dataclass, field

from defusedxml import ElementTree as ET

ERROR_TYPE_PATTERN = re.compile(r"^([A-Za-z_][\w.]*(?:Error|Exception|Exit|Interrupt|Warning)):")


@dataclass
class ParsedFailure:
    test_name: str
    classname: str
    error_type: str
    message: str
    stack_trace: str
    duration: float


@dataclass
class ParsedReport:
    total_tests: int = 0
    failures: list[ParsedFailure] = field(default_factory=list)


def detect_error_type(message: str) -> str:
    # exception messages start with the class name while plain asserts start with the word assert
    match = ERROR_TYPE_PATTERN.match(message)
    if match:
        return match.group(1).split(".")[-1]
    if message.startswith("assert"):
        return "AssertionError"
    return "UnknownError"


def parse_junit(xml_bytes: bytes) -> ParsedReport:
    # defusedxml blocks malicious xml tricks and raises a value error subclass for them
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"report is not valid xml: {exc}") from exc

    if root.tag not in ("testsuite", "testsuites"):
        raise ValueError("report is not a junit file and has no testsuite element")

    report = ParsedReport()
    for case in root.iter("testcase"):
        report.total_tests += 1
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is None:
            continue
        message = (problem.get("message") or "").strip()
        report.failures.append(
            ParsedFailure(
                test_name=case.get("name", "unknown"),
                classname=case.get("classname", ""),
                error_type=detect_error_type(message),
                message=message,
                stack_trace=(problem.text or "").strip(),
                duration=float(case.get("time", 0) or 0),
            )
        )
    return report