import sys
import os

def parse_duration(dep, lan):
    dep_h, dep_m = map(int, dep.split(':'))
    lan_h, lan_m = map(int, lan.split(':'))
    
    dep_mins = dep_h * 60 + dep_m
    lan_mins = lan_h * 60 + lan_m
    if lan_mins < dep_mins:
        lan_mins += 24 * 60
    return lan_mins - dep_mins

def citaj_datoteku(putanja="flights.txt"):
    if not os.path.exists(putanja):
        return None
        
    linije_saobracaja = []
    with open(putanja, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split('|')
            if len(parts) != 3:
                raise Exception("GRESKA")
                
            airline = parts[0]
            route = parts[1]
            flights_str = parts[2]
            
            if route.count('->') != 1:
                raise Exception("GRESKA")
                
            dep_city, lan_city = route.split('->')
            if not dep_city or not lan_city:
                raise Exception("GRESKA")
                
            linije_saobracaja.append((airline, route, flights_str))
            
    return linije_saobracaja

def obradi_direktne(linije_saobracaja):
    parsed = {}
    
    for airline, route, flights_str in linije_saobracaja:
        if route not in parsed:
            parsed[route] = []
            
        for f_str in flights_str.split(';'):
            if ',' not in f_str or '-' not in f_str:
                raise Exception("GRESKA")
                
            vreme_deo, price = f_str.split(',')
            if vreme_deo.count('-') != 1:
                raise Exception("GRESKA")
                
            dep, lan = vreme_deo.split('-')
            
            flight_dict = {
                'airline': airline,
                'dep': dep,
                'lan': lan,
                'duration': parse_duration(dep, lan),
                'price': price,
                'raw': f_str
            }
            parsed[route].append(flight_dict)
            
    with open("flights_direct.txt", "w", encoding='utf-8') as f:
        for route in sorted(parsed.keys()):
            f.write(f"{route}\n")
            
            airlines_dict = {}
            for fl in parsed[route]:
                comp = fl['airline']
                if comp not in airlines_dict:
                    airlines_dict[comp] = []
                airlines_dict[comp].append(fl)
                
            for comp in sorted(airlines_dict.keys()):
                f.write(f"{comp}\n")
                s_flights = sorted(airlines_dict[comp], key=lambda x: (x['dep'], x['duration'], x['airline']))
                for fl in s_flights:
                    f.write(f"{fl['raw']}\n")
                    
    return parsed

def obradi_indirektne(parsed_flights, trazeni_par):
    if '->' not in trazeni_par:
        with open("flights_indirect.txt", "w", encoding='utf-8') as f:
            pass
        return
        
    target_dep, target_lan = trazeni_par.split('->')
    
    valid_meds = set()
    for route in parsed_flights.keys():
        d, l = route.split('->')
        if d == target_dep and l != target_lan:
            if f"{l}->{target_lan}" in parsed_flights:
                valid_meds.add(l)
                
    valid_meds = sorted(list(valid_meds))
    
    with open("flights_indirect.txt", "w", encoding='utf-8') as f:
        for med in valid_meds:
            route1 = f"{target_dep}->{med}"
            route2 = f"{med}->{target_lan}"
            
            valid_combos = []
            for f1 in parsed_flights[route1]:
                for f2 in parsed_flights[route2]:
                    if f1['lan'] <= f2['dep']:
                        valid_combos.append((f1, f2))
                        
            if not valid_combos:
                continue
                
            f.write(f"{target_dep}->{med}->{target_lan}\n")
            
            f1s = []
            seen = set()
            for v in valid_combos:
                key = (v[0]['airline'], v[0]['raw'])
                if key not in seen:
                    f1s.append(v[0])
                    seen.add(key)
                    
            f1s.sort(key=lambda x: (x['dep'], x['duration'], x['airline']))
            
            for f1 in f1s:
                f.write(f"{f1['airline']} {f1['raw']}\n")
                
                f2s = [v[1] for v in valid_combos if v[0] == f1]
                f2s.sort(key=lambda x: (x['dep'], x['duration'], x['airline']))
                
                for f2 in f2s:
                     f.write(f"  {f2['airline']} {f2['raw']}\n")

def main():
    if sys.stdin.encoding and sys.stdin.encoding.lower() != 'utf-8':
        sys.stdin.reconfigure(encoding='utf-8')
    try:
        trazeni_par = sys.stdin.readline().strip()
        if not trazeni_par:
            return
            
        linije = citaj_datoteku("flights.txt")
        if linije is None:
            print("DAT_GRESKA")
            return
            
        parsed_flights = obradi_direktne(linije)
        obradi_indirektne(parsed_flights, trazeni_par)
        
    except Exception as e:
        print("GRESKA")

if __name__ == '__main__':
    main()
