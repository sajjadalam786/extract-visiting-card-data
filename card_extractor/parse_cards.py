#!/usr/bin/env python3
import json
import re
import csv
import sys
import os

INDIAN_CITIES = {
    'mumbai', 'pune', 'delhi', 'new delhi', 'bengaluru', 'bangalore', 'chennai', 'hyderabad',
    'ahmedabad', 'kolkata', 'surat', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore',
    'thane', 'bhopal', 'visakhapatnam', 'vadodara', 'ghaziabad', 'ludhiana', 'agra',
    'nashik', 'faridabad', 'meerut', 'rajkot', 'varanasi', 'srinagar', 'aurangabad',
    'dhanbad', 'amritsar', 'navi mumbai', 'allahabad', 'prayagraj', 'ranchi', 'howrah',
    'coimbatore', 'jabalpur', 'gwalior', 'vijayawada', 'jodhpur', 'madurai', 'raipur',
    'kota', 'guwahati', 'chandigarh', 'solapur', 'hubli', 'dharwad', 'bareilly',
    'moradabad', 'mysore', 'gurgaon', 'gurugram', 'aligarh', 'jalandhar', 'tiruchirappalli',
    'bhubaneswar', 'salem', 'mira-bhayandar', 'warangal', 'thiruvananthapuram', 'bhiwandi',
    'saharanpur', 'guntur', 'amravati', 'bikaner', 'noida', 'jamshedpur', 'bhilai',
    'cuttack', 'firozabad', 'kochi', 'nellore', 'bhavnagar', 'dehradun', 'durgapur',
    'asansol', 'rourkela', 'nanded', 'kolhapur', 'ajmer', 'akola', 'gulbarga',
    'jamnagar', 'ujjain', 'loni', 'siliguri', 'jhansi', 'ulhasnagar', 'jammu',
    'sangli', 'mangalore', 'erode', 'belgaum', 'ambattur', 'tirunelveli', 'malegaon',
    'gaya', 'jalgaon', 'udaipur', 'maheshtala', 'hospet', 'hosur', 'bellary', 'panipat',
    'satara', 'baramati', 'chakan', 'bhosari', 'talwade', 'ranjangaon', 'vapi', 'ankleshwar',
    'morbi', 'gandhinagar', 'ahmednagar', 'tarapur', 'waluj', 'trivandrum', 'calicut',
    'kollam', 'palakkad', 'thrissur', 'kannur', 'hubballi', 'belagavi', 'davanagere', 'shimoga',
    'udupi', 'tumkur', 'vellore', 'thoothukudi', 'dindigul', 'thanjavur', 'ranipet', 'sivakasi',
    'karur', 'ooty', 'kanchipuram', 'tiruvallur', 'secunderabad', 'khammam', 'karimnagar',
    'nizamabad', 'mahbubnagar', 'tirupati', 'kakinada', 'kadapa', 'anantapur', 'eluru', 'ongole',
    'nandyal', 'machilipatnam', 'adoni', 'tenali', 'proddatur', 'chittoor', 'hindupur',
    'udumalpet', 'tiruppur', 'tirupur', 'sriperumbudur', 'kancheepuram', 'tambaram', 'tada',
    'sricity', 'sri city', 'sricity sez', 'gummidipoondi', 'maraimalai nagar', 'oragadam',
    'palayamkottai', 'palayamkottal', 'perumalpuram', 'rabale', 'kandivali', 'mulund', 'andheri',
    'peenya', 'rajajinagar', 'poonamallee', 'thirumalisai'
}

INDIAN_STATES = {
    'maharashtra', 'gujarat', 'tamil nadu', 'karnataka', 'telangana', 'andhra pradesh',
    'delhi', 'haryana', 'punjab', 'rajasthan', 'uttar pradesh', 'madhya pradesh',
    'west bengal', 'kerala', 'bihar', 'odisha', 'assam', 'jharkhand', 'chhattisgarh',
    'uttarakhand', 'goa', 'himachal pradesh', 'india', 'u.p.', 'm.p.', 't.n.', 'ap', 'tn',
    'germany', 'france', 'italy', 'usa', 'uk'
}

OFFICE_HEADERS = {
    'corporate office', 'corporate office:', 'head office', 'head office:',
    'registered office', 'registered office:', 'regd office', 'regd. office',
    'regd. office:', 'regd office:', 'branch office', 'branch office:',
    'sales office', 'sales office:', 'regional office', 'regional office:',
    'zonal office', 'central office', 'works', 'works:', 'factory', 'factory:',
    'plant', 'plant:', 'associates', 'associates:', 'branches', 'sea freight division'
}

GENERIC_DISCARD = {
    '#startupindia', 'startupindia', 'startuptn', 'for enquiry', 'iso 9001:2015', 'iso certified',
    'certified', 'company', 'scan to save', 'scan here', 'follow us', 'visit us', 'call us',
    'contact us', 'phone', 'email', 'website', 'address', 'our certifications', 'toll free',
    'customer care', 'erstwhile', 'qms', 'cin', 'gstin', 'services we offer', 'products we offer',
    'our services', 'our products', 'we specialize in', 'scope of services', 'global reach, local touch.',
    'iso 9001: 2015, 14001: 2015 & iso : 45001 : 2018', 'buying power is silly', 'an iso certified company',
    'certified company', 'certifications', 'our certification', 'our products & services',
    'specialized services', 'quality', 'our vision', 'our mission', 'associates', 'associates:',
    'thinking ahead', 'fluid technology group', 'associate companies', 'sales companies'
}

STRONG_COMPANY_SUFFIXES = [
    'pvt. ltd.', 'pvt ltd', 'pvt. lid.', 'pvt.ltd.', 'pvt.ltd', 'private limited',
    '(p) ltd', '(p) ltd.', '(p)ltd', 'ltd.', 'ltd', 'limited', 'llp', 'inc.', 'inc',
    'corp.', 'corp', 'corporation', 'j.s.c', 'jsc', 'gmbh & co. kg', 'gmbh'
]

WEAK_COMPANY_SUFFIXES = [
    'enterprises', 'industries', 'technologies', 'solutions', 'systems', 'energy',
    'power', 'engineering', 'works', 'associates', 'group', 'international',
    'co.', 'company', 'agency', 'ventures', 'controls', 'automation', 'instruments',
    'logistics', 'consulting', 'auto components', 'electro tech', 'trading company',
    'pneumec kontrolls', 'kontrolls'
]

COMPANY_WORDS = {
    'tech', 'electro', 'engineering', 'power', 'energy', 'solar', 'wind', 'logistics',
    'automation', 'controls', 'systems', 'solutions', 'industries', 'enterprises',
    'services', 'group', 'products', 'tools', 'supplies', 'works', 'motors',
    'transmissions', 'associates', 'corporation', 'promotions', 'components',
    'digitronics', 'manufacturing', 'consulting', 'hardware', 'chemicals', 'trading',
    'kontrolls'
}

DESIGNATION_KEYWORDS = [
    'managing director', 'director', 'joint director', 'executive director',
    'chief executive officer', 'ceo', 'cfo', 'coo', 'cto', 'chief operating officer',
    'geschäftsführer', 'founder', 'co-founder', 'proprietor', 'partner', 'president',
    'vice president', 'vp', 'v.p', 'general manager', 'gm', 'dy. general manager', 'dgm', 'agm',
    'senior manager', 'sr. manager', 'manager', 'deputy manager', 'assistant manager',
    'sales manager', 'marketing manager', 'business development manager', 'bdm',
    'business development executive', 'business development', 'bussiness development',
    'business development - head', 'bd executive', 'lead', 'head', 'executive', 'officer',
    'sr. engineer', 'junior engineer', 'senior engineer', 'engineer',
    'consultant', 'advisor', 'specialist', 'coordinator', 'technician', 'supervisor',
    'representative', 'expert', 'scientist', 'designer', 'developer', 'author',
    'trainer', 'educator', 'advocate', 'analyst', 'senior analyst', 'market analyst'
]

DESIGNATION_WORDS = {
    'director', 'manager', 'ceo', 'cto', 'cfo', 'coo', 'vp', 'v.p', 'lead', 'head',
    'president', 'officer', 'engineer', 'consultant', 'partner', 'proprietor', 'founder',
    'executive', 'specialist', 'coordinator', 'supervisor', 'analyst', 'geschäftsführer'
}

DEGREES_AND_QUALIFICATIONS = [
    'b.e', 'b.tech', 'm.e', 'm.tech', 'ph.d', 'mba', 'f.i.e', 'fi.e', 'fie',
    'ca', 'cfa', 'b.sc', 'm.sc', 'b.com', 'm.com', 'diploma'
]

EXCLUDE_DOMAINS = {'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'rediffmail.com', 'icloud.com', 'google.com'}

def clean_text(s):
    if not s:
        return ""
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip(" ,;:-_•|/'\"&")

def is_iso_or_cert(s):
    s_l = s.lower()
    return bool(re.search(r'\b(iso|certif|qms|din\s*en|ohsas|ts\s*16949|ce\s*mark|nabl|iatf)\b', s_l) or re.search(r'\b(9001|14001|45001|27001|50001|17025|22000)\b', s_l))

def is_degree_line(s):
    s_l = s.lower()
    return any(deg in s_l for deg in DEGREES_AND_QUALIFICATIONS)

def is_address_line(line, pincode=""):
    line_l = line.lower().strip(" :.-")
    if line_l in OFFICE_HEADERS:
        return True
    if pincode and pincode in line:
        return True
    if any(re.search(r'\b' + re.escape(c) + r'\b', line_l) for c in INDIAN_CITIES):
        return True
    if any(re.search(r'\b' + re.escape(st) + r'\b', line_l) for st in INDIAN_STATES):
        return True
    if any(kw in line_l for kw in ['road', 'street', 'marg', 'nagar', 'industrial', 'midc', 'phase', 'sector', 'plot', 'survey no', 'floor', 'tower', 'bhavan', 'complex', 'opp.', 'near', 'flat no', 'office no', 'lane', 'village', 'taluk', 'dist', 'post box', 'p.o. box', 'estate', 'premises', 'arcade', 'plaza', 'park', 'bypass', 'hönnestraße']):
        return True
    if re.search(r'^\s*(office|works|factory|regd|branch|h\.o\.|r\.o\.|plant|unit\s*[-–—:]?\s*\d?|head office|corporate office)\s*[:\-–—]?', line_l):
        return True
    return False

def contains_designation(line):
    line_l = line.lower()
    return any(re.search(r'\b' + re.escape(w) + r'\b', line_l) for w in DESIGNATION_WORDS)

def is_company_line(line):
    line_l = line.lower()
    if any(s in line_l for s in STRONG_COMPANY_SUFFIXES):
        return True
    return any(re.search(r'\b' + re.escape(w) + r'\b', line_l) for w in COMPANY_WORDS)

def is_valid_person_name(name):
    if not name:
        return False
    name_clean = clean_text(name)
    name_l = name_clean.lower()
    if name_l in OFFICE_HEADERS or any(g in name_l for g in GENERIC_DISCARD):
        return False
    if is_company_line(name):
        return False
    if is_degree_line(name) or is_iso_or_cert(name) or is_address_line(name):
        return False
    if '@' in name or 'www.' in name_l or '.com' in name_l or '.de' in name_l:
        return False
    if re.search(r'\d', name):
        return False
    words = name_clean.split()
    if len(words) > 4:
        return False
    if re.match(r'^(?:[A-Za-z]\.?\s*)*[A-Za-z]{2,}(?:\s+[A-Za-z]{1,})*$', name_clean):
        return True
    return False

def process_card_record(item):
    filename = item.get('file', '')
    raw_lines = item.get('lines', [])
    if not raw_lines:
        return {
            'file': filename, 'brand_name': '', 'person_name': '',
            'mobiles': [], 'emails': [], 'websites': [],
            'address': '', 'pincode': '', 'insta': '', 'services': ''
        }

    orig_text_lines = [clean_text(l['text']) for l in raw_lines if l.get('text', '').strip()]

    emails = []
    email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    for line in orig_text_lines:
        for e in email_regex.findall(line):
            e_clean = e.strip(".,;:()<>[]'\"/").lower()
            if e_clean and e_clean not in emails:
                emails.append(e_clean)

    websites = []
    web_regex = re.compile(r'(?:https?:\/\/)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com|in|org|net|co\.in|io|biz|info|co|edu|tech|ai|de)(?:\.[a-zA-Z]{2,})?(?:\/[^\s]*)?)', re.IGNORECASE)
    for line in orig_text_lines:
        line_no_email = email_regex.sub('', line)
        for w in web_regex.findall(line_no_email):
            w_clean = w.strip(".,;:()<>[]'\"/").lower()
            base_dom = w_clean.split('/')[0]
            if base_dom not in EXCLUDE_DOMAINS and '.' in base_dom:
                if not w_clean.startswith('http'):
                    w_disp = 'www.' + w_clean if not w_clean.startswith('www.') else w_clean
                else:
                    w_disp = w_clean
                if w_disp not in websites:
                    websites.append(w_disp)

    mobiles = []
    for line in orig_text_lines:
        if is_iso_or_cert(line):
            continue
        line_clean = email_regex.sub('', line)
        for w in websites:
            line_clean = line_clean.replace(w, '')
        parts = re.split(r'[/,;&|]', line_clean)
        for part in parts:
            part = part.strip()
            digits = re.sub(r'\D', '', part)
            if digits.startswith('91') and len(digits) == 12:
                digits = digits[2:]
            elif digits.startswith('0') and len(digits) == 11:
                digits = digits[1:]
            
            if len(digits) == 10 and digits[0] in '56789':
                fmt = f"+91 {digits[:5]} {digits[5:]}"
                if fmt not in mobiles:
                    mobiles.append(fmt)
            elif digits.startswith('1800') and len(digits) in (10, 11):
                toll = f"1800 {digits[4:7]} {digits[7:]}"
                if toll not in mobiles:
                    mobiles.append(toll)
            elif len(digits) in (8, 9, 10, 11, 12, 13) and not any(k in part.upper() for k in ['CIN', 'GST', 'PIN', 'ISO', 'PAN', 'FAX']):
                clean_p = part.strip(" :.-+MmobTelOfficeFaxPhone")
                if len(digits) >= 8 and len(clean_p) >= 8:
                    if digits not in [re.sub(r'\D', '', m) for m in mobiles]:
                        mobiles.append(clean_p)

    pincode = ""
    pin_regex = re.compile(r'\b([1-9][0-9]{2}\s?[0-9]{3})\b')
    for line in reversed(orig_text_lines):
        m = pin_regex.search(line)
        if m:
            cand = re.sub(r'\s+', '', m.group(1))
            if not any(cand in re.sub(r'\D', '', mob) for mob in mobiles):
                pincode = cand
                break

    insta = ""
    insta_regex = re.compile(r'(?:instagram\.com\/|insta(?::|\s)|ig(?::|\s)|@)([a-zA-Z0-9._]{3,30})', re.IGNORECASE)
    for line in orig_text_lines:
        if '@' in line and any(ext in line for ext in ['.com', '.in', '.org', '.net']):
            continue
        m = insta_regex.search(line)
        if m:
            cand = m.group(1).lstrip('@')
            if not any(cand.lower() in em for em in emails):
                insta = "@" + cand
                break

    domain_roots = []
    for em in emails:
        dom = em.split('@')[-1].split('.')[0]
        if dom not in EXCLUDE_DOMAINS and len(dom) > 2:
            domain_roots.append(dom.lower())
    for ws in websites:
        clean_w = re.sub(r'^https?://', '', ws)
        clean_w = re.sub(r'^www\.', '', clean_w)
        dom = clean_w.split('.')[0]
        if dom not in EXCLUDE_DOMAINS and len(dom) > 2:
            domain_roots.append(dom.lower())

    designation = ""
    person_name = ""

    email_user_tokens = []
    for em in emails:
        user_part = em.split('@')[0]
        tokens = [t.lower() for t in re.split(r'[._-]', user_part) if len(t) > 2 and t.isalpha()]
        email_user_tokens.extend(tokens)

    for idx, line in enumerate(orig_text_lines):
        line_l = line.lower()
        if is_iso_or_cert(line):
            continue
        if any(k in line_l for k in ['gstin', 'cin:', 'pan:']):
            continue

        is_desig = False
        for des in DESIGNATION_KEYWORDS:
            if re.search(r'\b' + re.escape(des) + r'\b', line_l):
                is_desig = True
                if not designation:
                    designation = line
                elif line not in designation:
                    designation += " / " + line
                
                if not person_name:
                    for back_i in range(idx - 1, max(-1, idx - 4), -1):
                        cand = orig_text_lines[back_i]
                        if is_valid_person_name(cand):
                            person_name = cand
                            break

                if not person_name and idx + 1 < len(orig_text_lines):
                    for fwd_i in range(idx + 1, min(len(orig_text_lines), idx + 3)):
                        cand = orig_text_lines[fwd_i]
                        if is_valid_person_name(cand):
                            person_name = cand
                            break
                break

    if not person_name and email_user_tokens:
        for line in orig_text_lines:
            if is_valid_person_name(line):
                line_words = [w.lower() for w in line.split() if w.isalpha()]
                if any(tok in line_words for tok in email_user_tokens):
                    person_name = line
                    break

    if not person_name:
        for line in orig_text_lines:
            if re.match(r'^(mr\.|mrs\.|ms\.|dr\.|er\.)\s+[A-Za-z]+', line, re.I):
                if is_valid_person_name(line):
                    person_name = line
                    break

    if not person_name:
        for line in orig_text_lines[:6]:
            if is_valid_person_name(line):
                if len(line.split()) >= 2 or (len(line.split()) == 1 and line.isupper() and len(line) >= 4):
                    if not any(d in line.lower() for d in domain_roots):
                        person_name = line
                        break

    if not person_name and emails:
        user_p = emails[0].split('@')[0]
        if '.' in user_p:
            parts = user_p.split('.')
            if len(parts) == 2 and all(p.isalpha() and len(p) >= 2 for p in parts):
                person_name = f"{parts[0].capitalize()} {parts[1].capitalize()}"

    if person_name:
        person_name = re.sub(r'^[&•\-_:\s]+', '', person_name).strip()

    brand_name = ""

    for idx, line in enumerate(orig_text_lines):
        line_l = line.lower().strip(" :.-")
        if is_address_line(line, pincode) or is_iso_or_cert(line) or contains_designation(line):
            continue
        if line == person_name or line in designation:
            continue
        if line_l in OFFICE_HEADERS or any(g in line_l for g in GENERIC_DISCARD):
            continue
        if email_regex.search(line) or web_regex.search(line):
            continue
        if any(s in line_l for s in STRONG_COMPANY_SUFFIXES):
            if idx > 0:
                prev = orig_text_lines[idx - 1]
                prev_l = prev.lower().strip(" :.-")
                if not is_address_line(prev, pincode) and prev != person_name and len(prev.split()) <= 4:
                    if not prev.startswith('(') and not prev.endswith(')') and not contains_designation(prev):
                        if prev_l not in OFFICE_HEADERS and not any(g in prev_l for g in GENERIC_DISCARD) and not email_regex.search(prev) and not web_regex.search(prev) and not is_iso_or_cert(prev):
                            if any(d in (prev_l + line_l) for d in domain_roots) or len(line.split()) <= 3:
                                brand_name = f"{prev} {line}"
            if not brand_name:
                brand_name = line
            break

    if not brand_name:
        for idx, line in enumerate(orig_text_lines):
            line_l = line.lower().strip(" :.-")
            if is_address_line(line, pincode) or is_iso_or_cert(line) or contains_designation(line):
                continue
            if line == person_name or line in designation:
                continue
            if line_l in OFFICE_HEADERS or any(g in line_l for g in GENERIC_DISCARD):
                continue
            if email_regex.search(line) or web_regex.search(line):
                continue
            if any(d in line_l for d in domain_roots):
                brand_name = line
                break

    if not brand_name:
        for idx, line in enumerate(orig_text_lines):
            line_l = line.lower().strip(" :.-")
            if is_address_line(line, pincode) or is_iso_or_cert(line) or contains_designation(line):
                continue
            if line == person_name or line in designation:
                continue
            if line_l in OFFICE_HEADERS or any(g in line_l for g in GENERIC_DISCARD):
                continue
            if email_regex.search(line) or web_regex.search(line):
                continue
            if any(s in line_l for s in WEAK_COMPANY_SUFFIXES):
                if idx > 0:
                    prev = orig_text_lines[idx - 1]
                    prev_l = prev.lower().strip(" :.-")
                    if not is_address_line(prev, pincode) and prev != person_name and len(prev.split()) <= 4:
                        if not prev.startswith('(') and not prev.endswith(')') and not contains_designation(prev):
                            if prev_l not in OFFICE_HEADERS and not any(g in prev_l for g in GENERIC_DISCARD) and not email_regex.search(prev) and not web_regex.search(prev) and not is_iso_or_cert(prev):
                                brand_name = f"{prev} {line}"
                if not brand_name:
                    brand_name = line
                break

    if not brand_name:
        for line in orig_text_lines:
            line_l = line.lower().strip(" :.-")
            if is_address_line(line, pincode) or is_iso_or_cert(line) or contains_designation(line):
                continue
            if line == person_name or line in designation:
                continue
            if line_l in OFFICE_HEADERS or any(g in line_l for g in GENERIC_DISCARD):
                continue
            if email_regex.search(line) or web_regex.search(line):
                continue
            if is_company_line(line):
                brand_name = line
                break

    if not brand_name:
        for line in orig_text_lines:
            line_l = line.lower().strip(" :.-")
            if is_address_line(line, pincode) or is_iso_or_cert(line) or contains_designation(line):
                continue
            if line == person_name or line in designation:
                continue
            if line_l in OFFICE_HEADERS or any(g in line_l for g in GENERIC_DISCARD):
                continue
            if email_regex.search(line) or web_regex.search(line):
                continue
            if any(re.sub(r'\D', '', mob) in re.sub(r'\D', '', line) for mob in mobiles if len(re.sub(r'\D', '', mob)) >= 8):
                continue
            brand_name = line
            break

    if not brand_name and domain_roots:
        dom = domain_roots[0]
        brand_name = dom.replace('-', ' ').title()

    if brand_name:
        brand_name = re.sub(r'^[•\-_:\s]+', '', brand_name).strip()
        brand_name = re.sub(r'^\([A-Za-z0-9\s]+\)\s*', '', brand_name).strip()

    address_lines = []
    services_list = []

    for line in orig_text_lines:
        line_clean = clean_text(line)
        line_l = line_clean.lower().strip(" :.-")
        if line_clean in brand_name or line_clean == person_name or line_clean in designation:
            continue
        if is_iso_or_cert(line_clean):
            continue
        if any(k in line_l for k in ['gstin', 'cin:', 'pan:']):
            continue
        if any(em in line_l for em in emails):
            continue
        if any(w.lower() in line_l for w in websites):
            continue
        if any(re.sub(r'\D', '', mob) in re.sub(r'\D', '', line_clean) for mob in mobiles if len(re.sub(r'\D', '', mob)) >= 8):
            line_no_ph = re.sub(r'[\d\s+\-()./]{7,}', '', line_clean).strip()
            if not line_no_ph:
                continue

        if line_l in OFFICE_HEADERS:
            continue

        if is_address_line(line_clean, pincode):
            clean_addr_line = re.sub(r'^\s*(office|works|factory|regd|branch|h\.o\.|r\.o\.|plant|unit\s*[-–—:]?\s*\d?|head office|corporate office)\s*[:\-–—]\s*', '', line_clean, flags=re.I)
            if clean_addr_line and clean_addr_line.lower().strip(" :.-") not in OFFICE_HEADERS:
                address_lines.append(clean_addr_line)
        else:
            if not any(g in line_l for g in GENERIC_DISCARD):
                services_list.append(line_clean)

    services_str = designation if designation else ""
    if services_list:
        extra_svc = " | ".join([s for s in services_list if len(s) < 100][:3])
        if services_str and extra_svc:
            services_str = f"{services_str} | {extra_svc}"
        elif extra_svc:
            services_str = extra_svc

    return {
        'file': filename,
        'brand_name': clean_text(brand_name),
        'person_name': clean_text(person_name),
        'mobiles': mobiles,
        'emails': emails,
        'websites': websites,
        'address': clean_text(", ".join(address_lines)),
        'pincode': pincode,
        'insta': insta,
        'services': clean_text(services_str)
    }

def classify_lead_comprehensive(r):
    brand = r.get('brand_name', '').strip()
    person = r.get('person_name', '').strip()
    web = ", ".join(r.get('websites', [])).lower()
    email = ", ".join(r.get('emails', [])).lower()
    services = r.get('services', '')
    addr = r.get('address', '').lower()
    all_text = f"{brand} {person} {web} {email} {services} {addr}".lower()

    if 'pettorque' in all_text or 'pet tools' in all_text:
        return ('PetTorque / Pet Tools (Internal)', 'Self / Internal Reference', 99, 'Internal company card (Pet Tools Pvt. Ltd. / PetTorque).')

    wind_oems = ['suzlon', 'vestas', 'nordex', 'acciona', 'siemensgamesa', 'siemens gamesa', 'siemens-energy', 'enercon', 'senvion', 'mundra windtech', 'adani', 'ingeteam', 'gevernova', 'ge vernova']
    if any(k in all_text for k in wind_oems):
        return ('Wind Energy - OEM & Turbine Manufacturing', 'Tier 1: High Priority (Direct End-User)', 1, 'Heavy hydraulic torque wrenches, bolt tensioners & heavy sockets for tower flange assembly, foundation anchor bolts, blade-to-hub mounting & nacelle assembly.')

    wind_services = ['winomech', 'windmechanic', 'gwind', 'speed team', 'speedteam', 'surabi wind', 'surabiwind', 'narayana wind', 'narayanawind', 'samarth wind', 'samarthwind', 'asia wind', 'asiawind', 'sri vbs', 'srivbs', 'renom', 'grenewis', 'grene', 'hove-as', 'hove', 'venwind', 'vayulo', 'dmservice', 'dm service']
    if any(k in all_text for k in wind_services) or ('wind' in all_text and any(w in all_text for w in ['o&m', 'om', 'service', 'erection', 'blade', 'turbine', 'farm'])):
        return ('Wind Energy - Farm O&M & Turbine Services', 'Tier 1: High Priority (Direct End-User)', 1, 'Onsite hydraulic torque wrench rental, annual calibration, flange spreaders, nut splitters & wind turbine scheduled bolt re-torquing maintenance.')

    power_keywords = ['bhel', 'greenko', 'apraava', 'vibrant energy', 'vibrantenergy', 'sekura', 'orient green power', 'orientgreen', 'gaiavolt', 'gaiavoltgreen', 'spr renewable', 'standard electrical', 'standardengineer', 'kvggn', 'refex']
    if any(k in all_text for k in power_keywords) or (any(w in all_text for w in ['solar', 'thermal power', 'power plant', 'substation', 'green energy']) and not any(l in all_text for l in ['logistic', 'freight', 'transport', 'hotel'])):
        return ('Power Generation, Renewables & Solar EPC', 'Tier 1: High Priority (Direct End-User)', 1, 'High-pressure steam pipeline flange bolting, boiler auxiliary maintenance, turbine casing torquing, and heavy solar tracker/substation structural bolting.')

    heavy_eng = ['re tubing', 'onsite re tubing', 'in-situ', 'fabhub', 'emachineshop', 'cold cutting', 'amallgam', 'fairtech', 'shriramm auto', 'srac', 'amsak cranes', 'amsak', 'rapidtec', 'pk engineering', 'pkengineering', 'ace carbo', 'acecarbo', 'sivenara', 'vivablast', 'applied engineering', 'appliedengg', 'urc']
    if any(k in all_text for k in heavy_eng) or (any(w in all_text for w in ['fabrication', 'in-situ', 'machining', 'pressure vessel', 'flange', 'cranes', 'heavy engineering', 'construction contractor', 'piping contractor']) and not any(l in all_text for l in ['logistic', 'freight', 'software', 'erp', 'hr'])):
        return ('Heavy Engineering, Fabrication & Machining', 'Tier 1: High Priority (Direct End-User)', 1, 'Hydraulic torque wrenches, nut splitters & flange alignment tools for heavy steel fabrication, pressure vessels, crane erection & field pipe spool bolting.')

    oems = ['flender', 'freudenberg', 'fst.com', 'voltech', 'hydac', 'anlinda', 'sea hydro', 'seahydro', 'mersen', 'gen moto', 'genmotocoils', 'delta automation', 'deltaautomation', 'tsubaki', 'lechler', 'devkishin', 'savio seals', 'eutectical', 'pramod fibre', 'pramodfibre', 'pulze', 'pinnacle lithium', 'essae', 'secure industries', 'secureclosures', 'pneumec', 'tefoc', 'mvm electro']
    if any(k in all_text for k in oems) or any(w in all_text for w in ['manufacturer of', 'oem', 'gearbox', 'transformer', 'switchgear', 'valves', 'pumps', 'compressor', 'hydraulic cylinder', 'motors', 'transmissions']):
        return ('OEMs - Industrial Machinery & Components', 'Tier 2: Medium Priority (OEM Equipment Builder)', 2, 'Controlled bolting tools & high-pressure electric/pneumatic hydraulic power packs for factory assembly lines, machine builds & QA torque verification.')

    torque_peers = ['torc power', 'torcpower', 'gemini power', 'geminipower', 'diya enterprises', 'power team', 'plarad', 'telma solutions', 'telma.in', 'gedore', 'atlas copco', 'atlascopco', 'chicago pneumatic', 'cp.com', 'hoffmann', 'bega', 'betex', 'uniktork', 'toolsunique', 'torquerepairs', 'perfect enterprises', 'sushma', 'keyan hydraulics', 'keyanhydraulics', 'hawe', 'jk hydro', 'jkhydro']
    if any(k in all_text for k in torque_peers):
        return ('Hydraulics, Bolting & Torque Tools (Peers/Partners)', 'Tier 3: Strategic Partner / Industry Peer', 3, 'Strategic collaboration / cross-supply of specialty bolting accessories, custom impact sockets, hydraulic hoses, or sub-contracting repair & NABL calibration.')

    traders = ['shree nutbolt', 'nutbolt', 'studs', 'ietsupply', 'indo engineering tools', 'southern hardware', 'southernhardware', 'prime tools', 'primetools', 'rudrali', 'harshvijay', 'ep-india', 'eibenstock', 'core cutting', 'des-case', 'descase', 'fastercouplings', 'unitread', 'pramar engg', 'aadhira trading', 'saffron ventures']
    if any(k in all_text for k in traders) or any(w in all_text for w in ['fastener', 'hardware', 'cutting tool', 'distributor', 'trader', 'dealer', 'industrial supply', 'couplings']):
        return ('Industrial Supplies, Fasteners & Hardware Traders', 'Tier 3: Potential Channel Partner / Dealer', 3, 'Potential dealership/distribution partner for PetTorque hydraulic torque tools, heavy-duty impact sockets, backup wrenches & hydraulic accessories.')

    testing = ['mkbest', 'mkbestcalibration', 'calibration', 'ulogam', 'eurotech', 'safeline', 'venus safety', 'venusohs']
    if any(k in all_text for k in testing) or any(w in all_text for w in ['testing', 'certification', 'safety equipment', 'ndt']):
        return ('Testing, Certification & Safety Services', 'Tier 3: Secondary / Ancillary Partner', 3, 'Ancillary partner for NDT inspection, PPE/safety equipment supply, or secondary testing collaboration.')

    logistics = ['logistic', 'freight', 'shipping', 'cargo', 'transport', 'supply chain', 'warehouse', 'nvocc', 'chartering', 'consol', 'fcl', 'cargotone', 'agslog', 'seashell', 'landlshipping', 'adva', 'shiftco', 'allcargo', 'svlpl', 'laflcargo', 'neram', 'dtdc', 'orange cargo', 'bharat logistics', 'cargomax', 'abreco', 'shethia', 'wheelseye', 'tera projects', 'teraship', 'freightbridge', 'fblindia', 'seaindia', 'righteous', 'wf logistics', 'freyer', 'welcome logistiks', 'big navigators', 'bignavigators', 'logisteed']
    if any(k in all_text for k in logistics):
        return ('Logistics, Freight & Supply Chain', 'Tier 4: Non-Target (Logistics & Shipping Vendor)', 4, 'Non-customer for bolting solutions. Useful as potential freight forwarder or heavy transport partner for PetTorque product shipments.')

    corp = ['naukri', 'info edge', 'aspm consulting', 'ven consulting', 'venindia', 'adri human', 'falcon', 'mirai staffing', 'hepl', 'dealsinsight', 'pmtrackerp', 'cloud9', 'ifive', 'hinduja tech', 'tecosim', 'beacon-india', 'tjsb', 'citizencredit', 'mms broking', 'niveshaay', 'nivesh', 'vit®', 'vit.ac.in', 'lyf lzns', 'lyflzns', 'hotel', 'hospitality', 'e-holding', 'infinity solutions', 'infinitysolutionssoft', 'autodesk', 'atyourprice', 'chamber of commerce', 'asian-african', 'newtrace', 'kryasolutions', 'krya', 'synigenceglobal', 'fleurself', 'optimuz', 'avrunityventures']
    if any(k in all_text for k in corp) or any(w in all_text for w in ['consulting', 'software', 'erp', 'staffing', 'recruitment', 'hr', 'bank', 'insurance', 'wealth', 'advisory', 'university']):
        return ('Corporate Services, IT, HR & Consulting', 'Tier 5: Non-Target (Corporate / IT Services)', 5, 'Non-customer. Corporate services provider (recruitment, software, ERP, banking, wealth advisory, or general consulting).')

    media = ['deviva', 'savior', 'saviorprogress', 'ambroise', 'linkpromotions', 'link promotions', 'smarika', 'coffeeday', 'coffee day', 'teamwebpower', 'team web power', 'brightorigin', 'bright origin', 'celebration of life']
    if any(k in all_text for k in media) or any(w in all_text for w in ['exhibition', 'signage', 'stall', 'event', 'gifting', 'graphic design', 'branding']):
        return ('Exhibitions, Signages & Media', 'Tier 5: Non-Target (Event / Media Vendor)', 5, 'Non-customer. Vendor for trade show stall fabrication, branding, corporate gifts, and signage.')

    return ('Other Industrial & Commercial', 'Tier 3: Secondary / Unverified Industrial', 3, 'General industrial contact. Review specific mechanical maintenance or manufacturing assembly requirements.')

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 parse_cards.py <input_ocr_json> <output_csv>")
        sys.exit(1)

    json_path = sys.argv[1]
    csv_out_path = sys.argv[2]

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    data.sort(key=lambda d: d.get('file', ''))

    records = [process_card_record(item) for item in data]

    enriched = []
    for r in records:
        cat, tier, sort_key, pitch = classify_lead_comprehensive(r)
        r['Category'] = cat
        r['Target Fit / Priority'] = tier
        r['PetTorque Opportunity / Pitch'] = pitch
        r['_sort_key'] = sort_key
        enriched.append(r)

    enriched.sort(key=lambda x: (x['_sort_key'], x['Category'], x['brand_name']))

    max_mobs = max(len(r['mobiles']) for r in enriched) if enriched else 1
    max_emails = max(len(r['emails']) for r in enriched) if enriched else 1

    header = ['Category', 'Target Fit / Priority', 'Brand Name', 'Person Name', 'PetTorque Opportunity / Pitch']
    for i in range(1, max_mobs + 1):
        if i == 1:
            header.append('Mob number')
        else:
            header.append(f'Mob number {i}')

    for i in range(1, max_emails + 1):
        if i == 1:
            header.append('Email')
        else:
            header.append(f'Email {i}')

    header.extend(['Website', 'Address', 'pincode', 'Insta Handle', 'Services/ Category'])

    os.makedirs(os.path.dirname(os.path.abspath(csv_out_path)), exist_ok=True)

    with open(csv_out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for r in enriched:
            row = [
                r['Category'],
                r['Target Fit / Priority'],
                r['brand_name'],
                r['person_name'],
                r['PetTorque Opportunity / Pitch']
            ]
            
            for i in range(max_mobs):
                if i < len(r['mobiles']):
                    row.append(r['mobiles'][i])
                else:
                    row.append('')
            
            for i in range(max_emails):
                if i < len(r['emails']):
                    row.append(r['emails'][i])
                else:
                    row.append('')

            row.append(", ".join(r['websites']))
            row.append(r['address'])
            row.append(r['pincode'])
            row.append(r['insta'])
            row.append(r['services'])

            writer.writerow(row)

    print(f"Generated classified CSV at '{csv_out_path}' with {len(enriched)} cards.")

if __name__ == '__main__':
    main()
