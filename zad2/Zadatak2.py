import sys
import re

def parse_email(email):
    # Regex for both student and employee emails
    # prefix can be anything except @, |, -, or spaces
    pattern = r'^([^@\s|\-]+)@(student\.)?([A-Za-z]{3})\.(rs|bg\.ac\.rs)$'
    match = re.fullmatch(pattern, email)
    if not match:
        return None
    
    prefix = match.group(1)
    student_part = match.group(2) or ""
    fax = match.group(3)
    
    norm = f"{prefix}@{student_part}{fax}.rs".lower()
    disp = f"{prefix}-{fax}"
    
    return norm, disp

def main():
    try:
        input_lines = sys.stdin.read().splitlines()
        if len(input_lines) < 2:
            return
            
        in_file = input_lines[0].strip()
        out_file = input_lines[1].strip()
        
        if not in_file or not out_file:
            return
            
        try:
            with open(in_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print("DAT_GRESKA")
            return
            
        stats = {}
        
        for line in lines:
            line = line.rstrip('\n').rstrip('\r')
            if not line:
                continue
                
            parts1 = line.split('|')
            if len(parts1) != 2:
                raise Exception()
                
            sa = parts1[0].strip()
            
            parts2 = parts1[1].split('-')
            # "tekst|tekst-tekst" format implies exactly three parts
            if len(parts2) != 2:
                raise Exception()
                
            na = parts2[0].strip()
            poruka = parts2[1]
            
            sa_res = parse_email(sa)
            na_res = parse_email(na)
            
            if not sa_res or not na_res:
                raise Exception()
                
            sa_norm, sa_disp = sa_res
            na_norm, na_disp = na_res
            
            chars = len(poruka)
            
            if sa_norm not in stats:
                stats[sa_norm] = {'disp': sa_disp, 'chars': 0, 'peers': set()}
            if na_norm not in stats:
                stats[na_norm] = {'disp': na_disp, 'chars': 0, 'peers': set()}
                
            stats[sa_norm]['chars'] += chars
            stats[na_norm]['chars'] += chars
            
            stats[sa_norm]['peers'].add(na_disp)
            stats[na_norm]['peers'].add(sa_disp)
            
        out_lines = []
        for norm, data in stats.items():
            disp = data['disp']
            chars = data['chars']
            peers_sorted = ",".join(sorted(list(data['peers'])))
            out_lines.append(f"{disp}({chars}):{peers_sorted}")
            
        out_lines.sort()
        
        with open(out_file, 'w', encoding='utf-8') as f:
            if out_lines:
                f.write("\n".join(out_lines) + "\n")
                
    except Exception:
        print("GRESKA")
        sys.exit()

if __name__ == "__main__":
    main()
