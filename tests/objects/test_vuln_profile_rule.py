import xmltodict

from panos_util.objects import VulnerabilityProfileRule

EMPTY = """
<entry name="Empty"/>
"""

EMPTY_CHILD = """
<entry name="Empty-Child">
    <vendor-id/>
    <cve/>
    <severity/>
    <action/>
</entry>
"""

SINGLE_CHILD = """
<entry name="Single-Child">
    <vendor-id>
        <member>one</member>
    </vendor-id>
    <cve>
        <member>one</member>
    </cve>
    <severity>
        <member>one</member>
    </severity>
</entry>
"""

MULTI_CHILD = """
<entry name="Multi-Child">
    <vendor-id>
        <member>one</member>
        <member>two</member>
    </vendor-id>
    <cve>
        <member>one</member>
        <member>two</member>
    </cve>
    <severity>
        <member>one</member>
        <member>two</member>
    </severity>
</entry>
"""

BLOCKS = """
<entry name="Blocks">
    <action>
        <reset-both/>
    </action>
    <vendor-id>
        <member>any</member>
    </vendor-id>
    <severity>
        <member>critical</member>
        <member>high</member>
        <member>medium</member>
    </severity>
    <cve>
        <member>any</member>
    </cve>
    <threat-name>any</threat-name>
    <host>any</host>
    <category>any</category>
    <packet-capture>single-packet</packet-capture>
</entry>
"""

ALERT = """
<entry name="Alert">
    <action>
        <alert/>
    </action>
    <vendor-id>
        <member>any</member>
    </vendor-id>
    <severity>
        <member>any</member>
    </severity>
    <cve>
        <member>any</member>
    </cve>
    <threat-name>any</threat-name>
    <host>any</host>
    <category>any</category>
    <packet-capture>disable</packet-capture>
</entry>
"""


def test_empty():
    xmldict = xmltodict.parse(EMPTY)
    rule = VulnerabilityProfileRule.create_from_xmldict(xmldict["entry"])

    assert rule.name == "Empty"

    assert rule.blocks_criticals() is False
    assert rule.blocks_high() is False
    assert rule.blocks_medium() is False
    assert rule.alert_only() is False


def test_empty_child():
    xmldict = xmltodict.parse(EMPTY_CHILD)
    rule = VulnerabilityProfileRule.create_from_xmldict(xmldict["entry"])

    assert rule.name == "Empty-Child"


def test_single_child():
    xmldict = xmltodict.parse(SINGLE_CHILD)
    rule = VulnerabilityProfileRule.create_from_xmldict(xmldict["entry"])

    assert rule.name == "Single-Child"


def test_multi_child():
    xmldict = xmltodict.parse(MULTI_CHILD)
    rule = VulnerabilityProfileRule.create_from_xmldict(xmldict["entry"])

    assert rule.name == "Multi-Child"


def test_blocks():
    xmldict = xmltodict.parse(BLOCKS)
    rule = VulnerabilityProfileRule.create_from_xmldict(xmldict["entry"])

    assert rule.name == "Blocks"
    assert rule.blocks_criticals() is True
    assert rule.blocks_high() is True
    assert rule.blocks_medium() is True
    assert rule.alert_only() is False

    assert rule.action == "reset-both"
    assert rule.vendor_id == ["any"]
    assert rule.severity == ["critical", "high", "medium"]
    assert rule.cve == ["any"]
    assert rule.threat_name == "any"
    assert rule.host == "any"
    assert rule.packet_capture == "single-packet"


def test_alert():
    xmldict = xmltodict.parse(ALERT)
    rule = VulnerabilityProfileRule.create_from_xmldict(xmldict["entry"])

    assert rule.name == "Alert"
    assert rule.blocks_criticals() is False
    assert rule.blocks_high() is False
    assert rule.blocks_medium() is False
    assert rule.alert_only() is True

    assert rule.action == "alert"
