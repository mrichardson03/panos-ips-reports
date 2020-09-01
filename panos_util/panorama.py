from __future__ import absolute_import, annotations, division, print_function

from collections import Counter
from xml.etree.ElementTree import Element

from .objects import (
    DefaultVulnerabilityProfile,
    SecurityProfileGroup,
    StrictVulnerabilityProfile,
    VulnerabilityProfile,
)
from .policies import SecurityRule


class Panorama:
    """ Class representing Panorama. """

    def __init__(self, device_groups):
        self.device_groups = device_groups

    def get_device_group(self, name: str) -> DeviceGroup:
        """ Gets a DeviceGroup object by name. """
        return self.device_groups.get(name, None)

    @staticmethod
    def create_from_element(e: Element) -> Panorama:
        """ Create Panorama object from XML element. """
        device_groups = {}

        shared_e = e.find("./shared")
        shared_obj = DeviceGroup.create_from_element(shared_e)
        shared_obj.name = "shared"  # Helps with debugging.
        device_groups.update({"shared": shared_obj})

        for dg_e in e.findall("./devices/entry/device-group/"):
            dg_obj = DeviceGroup.create_from_element(dg_e)
            dg_obj.parent = shared_obj
            device_groups.update({dg_obj.name: dg_obj})

        return Panorama(device_groups)


class DeviceGroup:
    """ Class representing a device group. """

    def __init__(self, name, rules, vuln_profiles, profile_groups, parent=None):
        self.name = name
        self.rules = rules

        # The 'strict' and 'default' vulnerability profiles live at the device group
        # level, but don't actually exist in the config.
        self.vuln_profiles = {
            "strict": StrictVulnerabilityProfile(),
            "default": DefaultVulnerabilityProfile(),
        }
        self.vuln_profiles.update(vuln_profiles)

        self.profile_groups = profile_groups
        self.parent = parent
        self._rule_counts = None

    def rule_counts(self, force_update=False) -> Counter:
        """ Returns a Counter object containing stats for this DeviceGroup. """
        if self._rule_counts is None:
            self._rule_counts = Counter()
            self._update_rule_counts()
        else:
            if force_update is True:  # pragma: no cover
                self._update_rule_counts()

        return self._rule_counts

    def _update_rule_counts(self) -> None:
        """ Recalculates the rule stats for this DeviceGroup. """
        for rule in self.rules:
            self._rule_counts["total"] += 1

            if rule.disabled is False:
                self._rule_counts[rule.action] += 1

                vp = None
                if rule.vulnerability_profile is not None:
                    vp = self.resolve_profile(rule.vulnerability_profile)
                elif rule.security_profile_group is not None:
                    vp = self.resolve_profile_group(rule.security_profile_group)

                if vp is not None:
                    if vp.alert_only() is True:
                        self._rule_counts["alert_only"] += 1
                    else:
                        if vp.blocks_criticals() is True:
                            self._rule_counts["blocks_criticals"] += 1
                        if vp.blocks_high() is True:
                            self._rule_counts["blocks_high"] += 1
                        if vp.blocks_medium() is True:
                            self._rule_counts["blocks_medium"] += 1

            else:
                self._rule_counts["disabled"] += 1

    def resolve_profile(self, name: str) -> VulnerabilityProfile:
        """ Looks up a VulnerabiltyProfile by name. """
        profile = self.vuln_profiles.get(name, None)

        if profile is None:
            return self.parent.resolve_profile(name)

        return profile

    def resolve_profile_group(self, name: str) -> VulnerabilityProfile:
        """ Looks up a VulnerabilityProfile by SecurityProfileGroup name. """
        group = self.profile_groups.get(name, None)

        if group is not None:
            return self.resolve_profile(group.vulnerability)
        else:
            if self.parent is not None:
                return self.parent.resolve_profile_group(name)
            else:
                print("PROBLEM with profile: {0}".format(name))
                return None

    @staticmethod
    def create_from_element(e: Element) -> DeviceGroup:
        """ Create DeviceGroup from XML element. """
        name = e.get("name")

        vuln_profiles = {}
        for vuln_profile in e.findall("./profiles/vulnerability/entry"):
            vp = VulnerabilityProfile.create_from_element(vuln_profile)
            vuln_profiles.update({vp.name: vp})

        profile_groups = {}
        for profile_group in e.findall("./profile-group/entry"):
            pg = SecurityProfileGroup.create_from_element(profile_group)
            profile_groups.update({pg.name: pg})

        rules = []
        for rule in e.findall("./pre-rulebase/security/rules/entry"):
            sr = SecurityRule.create_from_element(rule)
            rules.append(sr)

        return DeviceGroup(name, rules, vuln_profiles, profile_groups)