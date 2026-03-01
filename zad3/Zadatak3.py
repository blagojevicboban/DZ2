import sys
import re

def is_valid_number(num_str):
    pattern = r'^(0|\+381)\d{9,10}$'
    return bool(re.fullmatch(pattern, num_str))

def main():
    try:
        if sys.stdin.encoding and sys.stdin.encoding.lower() != 'utf-8':
            sys.stdin.reconfigure(encoding='utf-8')
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
                
            parts = line.split('|')
            if len(parts) != 2:
                raise Exception()
                
            caller = parts[0].strip()
            if not is_valid_number(caller):
                raise Exception()
                
            calls_str = parts[1].strip()
            if not calls_str:
                raise Exception()
                
            call_items = calls_str.split(',')
            for item in call_items:
                item = item.strip()
                # Ocekujemo format: broj(mm:ss)
                match = re.fullmatch(r'^([^(]+)\((\d{2}):(\d{2})\)$', item)
                if not match:
                    raise Exception()
                    
                callee = match.group(1).strip()
                if not is_valid_number(callee):
                    raise Exception()
                    
                mm = int(match.group(2))
                ss = int(match.group(3))
                
                if not (0 <= mm <= 59) or not (0 <= ss <= 59):
                    raise Exception()
                    
                duration_sec = mm * 60 + ss
                
                if caller not in stats:
                    stats[caller] = {'duration': 0, 'peers': set()}
                if callee not in stats:
                    stats[callee] = {'duration': 0, 'peers': set()}
                    
                stats[caller]['duration'] += duration_sec
                stats[callee]['duration'] += duration_sec
                
                stats[caller]['peers'].add(callee)
                stats[callee]['peers'].add(caller)
                
        out_lines = []
        for number in sorted(stats.keys()):
            data = stats[number]
            duration = data['duration']
            peers_sorted = ",".join(sorted(list(data['peers'])))
            out_lines.append(f"{number}({duration}):{peers_sorted}")
            
        with open(out_file, 'w', encoding='utf-8') as f:
            if out_lines:
                f.write("\n".join(out_lines) + "\n")
                
    except Exception:
        print("GRESKA")
        sys.exit()

if __name__ == "__main__":
    main()
