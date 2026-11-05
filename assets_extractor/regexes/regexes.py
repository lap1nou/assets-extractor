import ipaddress
import re
from assets_extractor.config.config import ConfigRegexes


def extract_assets(config_regexes: ConfigRegexes = ConfigRegexes(), result_text: str = ""):
    ips = extract_ipv4(config_regexes, result_text)
    ips_cidr = extract_ipv4_cidr(config_regexes, result_text)
    domains = extract_domain(config_regexes, result_text)

    return (ips, ips_cidr, domains)

def extract_ipv4(config_regexes: ConfigRegexes = ConfigRegexes(), result_text: str = ""):
    results = []
    ips = re.findall(config_regexes.ipv4, result_text, re.IGNORECASE)

    if ips:
        for ip in ips:
            try:
                results.append(str(ipaddress.IPv4Address(ip)))
            except ipaddress.AddressValueError:
                continue

    return results

def extract_ipv4_cidr(config_regexes: ConfigRegexes = ConfigRegexes(), result_text: str = ""):
    results = []
    ips_cidr = re.findall(config_regexes.ipv4_cidr, result_text, re.IGNORECASE)

    if ips_cidr:
        for ip_cidr in ips_cidr:
            results.append(ip_cidr)

    return results

def extract_domain(config_regexes: ConfigRegexes = ConfigRegexes(), result_text: str = ""):
    results = []
    domains = re.findall(config_regexes.domain, result_text, re.IGNORECASE)

    if domains:
        for domain in domains:
            results.append(domain)

    return results