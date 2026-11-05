def domains_ips_to_json(ips, domains):
    results = []

    for ip in ips:
        results.append({"ip": ip, "hostname":"", "role":""})

    for domain in domains:
        results.append({"ip": "", "hostname":domain, "role":""})

    return results

def ips_cidr_to_json(ips_cidr):
    results = []

    for ip_cidr in ips_cidr:
        results.append({"range": ip_cidr, "name":""})

    return results