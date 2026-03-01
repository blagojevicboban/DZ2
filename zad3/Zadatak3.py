def is_valid_number(num_str):
    if not num_str:
        return False
        
    if num_str.startswith('0'):
        rest = num_str[1:]
    elif num_str.startswith('+381'):
        rest = num_str[4:]
    else:
        return False
        
    if not (9 <= len(rest) <= 10):
        return False
        
    if not rest.isdigit():
        return False
            
    return True

def main():
    try:
        ulaz = open(0, "r", encoding='utf-8')
        input_lines = ulaz.read().splitlines()
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
                open_paren = item.find('(')
                close_paren = item.find(')')
                if open_paren == -1 or close_paren == -1 or close_paren != len(item) - 1:
                    raise Exception()
                    
                callee = item[:open_paren].strip()
                if not is_valid_number(callee):
                    raise Exception()
                    
                time_str = item[open_paren+1:close_paren]
                time_parts = time_str.split(':')
                if len(time_parts) != 2:
                    raise Exception()
                    
                mm_str = time_parts[0]
                ss_str = time_parts[1]
                
                if len(mm_str) != 2 or len(ss_str) != 2:
                    raise Exception()
                    
                if not mm_str.isdigit() or not ss_str.isdigit():
                    raise Exception()
                    
                mm = int(mm_str)
                ss = int(ss_str)
                
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
        return

if __name__ == "__main__":
    main()
