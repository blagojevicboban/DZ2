import sys
import re

def is_valid_number(num_str):
    """
    Korisnička funkcija koja putem Regularnih Izraza (Regex) validira da li je broj telefona ispravan.
    
    Pravila formata broja:
    - Mora počinjati sa prefiksom '0' ili int. formom '+381'
    - Nakon prefiksa mora slediti blok između 9 i 10 numeričkih cifara (\d)
    
    Vraća True ako postoji podudaranje i False ako je regex pao (broj je nevalidan).
    """
    pattern = r'^(0|\+381)\d{9,10}$'
    # fullmatch garantuje da ceo string od početka (^) do kraja ($) poštuje obrazac, a funkcija bool() prevodi rezultat u Tačno/Netačno
    return bool(re.fullmatch(pattern, num_str))

def main():
    """
    Glavna organizaciona struktura aplikacije zadužena za obradu telefonskih logova 
    smeštenih u prosleđenom baznom tekstualnom fajlu.
    """
    try:
        # 1) Hvatanje linija sa standardnog ulaza red po red pomoću ugrađene Python celine (stdin)
        if sys.stdin.encoding and sys.stdin.encoding.lower() != 'utf-8':
            sys.stdin.reconfigure(encoding='utf-8')
        input_lines = sys.stdin.read().splitlines()
        
        # Prema pravilu neophodna su najmanje 2 podatka: ime_ulaznog_fajla i ime_izlaznog_fajla, inače zaustavi se.
        if len(input_lines) < 2:
            return
            
        in_file = input_lines[0].strip()
        out_file = input_lines[1].strip()
        
        # Ukoliko su uneta imena fajlova prazni karakteri (samo spejsovi), zaustavi se.
        if not in_file or not out_file:
            return
            
        # 2) Pristup hard disku radi preuzimanja celokupnog sadržaja sa input putanje
        try:
            with open(in_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
        except FileNotFoundError:
            # Propisani izlaz u slučaju da fajl sa zadatim imenom logički ne postoji u folderu
            print("DAT_GRESKA")
            return
            
        # Glavni rečnik za agregaciju (sakupljanje) vremena i sagovornika za svaki broj ikada naveden
        stats = {}
        
        # 3) Razlaganje svakog reda teksta baze podataka posebno
        for line in lines:
            line = line.rstrip('\n').rstrip('\r') # Ukloni simbole za novi red sa kraja
            if not line:
                continue # Ako preostane čista praznina prelazi se odmah na novu liniju
                
            # Logička Podela 1: Delimiter bar ('|') deli String na onoga ko zove(levo) i kome on to zvoni (desno)
            parts = line.split('|')
            if len(parts) != 2:
                raise Exception()
                
            # Osoba koja prva inicira poziv - caller (pozivač)
            caller = parts[0].strip()
            # Kroz regex gore ustanovi da li je njen telefonski broj u opsegu mogućeg i dozvoljenog
            if not is_valid_number(caller):
                raise Exception()
                
            calls_str = parts[1].strip()
            
            # Da li uopšte pišu kontakti koje je osoba pokušala zvali?
            if not calls_str:
                raise Exception()
                
            # Logička Podela 2: Telefoni (ljudi) koje zovu se izlistavaju podvojeno preko zareza
            call_items = calls_str.split(',')
            
            # Raščlanjavanje svake sitne instance pozivanja iz te dugačke desne liste (svako polje posebno za sebe)
            for item in call_items:
                item = item.strip()
                
                # Zadan nam je format gde stoji prvo Broj pa onda zagrade sa trajanjem -> "broj(mm:ss)"
                # ^([^(]+): hvata bilo koji blok karaktera sve dok ispred njega ne iskoči znak leve otvorene zagrade '\('
                # \( : Hvata bukvalno znak leve zagrade, sledi ga 2 broja za minut (\d{2}), pa : pa dvocifren sekund, onda desna zagrada \)
                match = re.fullmatch(r'^([^(]+)\((\d{2}):(\d{2})\)$', item)
                if not match:
                    raise Exception()
                    
                callee = match.group(1).strip() # Na osnovu RegExp grupisanja, ovo je taj primalac (deo ispred leve zagrade)
                
                # Validnost drugosagovornikovog broja takođe podložna našoj ugrađenoj Regex proveri
                if not is_valid_number(callee):
                    raise Exception()
                    
                # Drugi par zagrada regex match-a sadrži minute, a treći sekunde. Pomoću int() su pretvorene iz stringa u prave celobrojne numere.
                mm = int(match.group(2))
                ss = int(match.group(3))
                
                # Standardna logika protoka vremena - sekunde i minute moraju padati između nule i 59.
                if not (0 <= mm <= 59) or not (0 <= ss <= 59):
                    raise Exception()
                    
                # Obračunavamo jedinstvenu metricu mere - Trajanje samog poziva svodimo samo na proste sekunde!    
                duration_sec = mm * 60 + ss
                
                # Incijalizacija subjekta u matičnom obikatu analize, provera sa ključevima telefonskih adresa
                # Kreira se i set (da brojimo bez ponovnih dupliranih prikaza u konačnom redu)
                if caller not in stats:
                    stats[caller] = {'duration': 0, 'peers': set()}
                if callee not in stats:
                    stats[callee] = {'duration': 0, 'peers': set()}
                    
                # Akumuliramo novo trajanje poruke u obim dosadašnjih sekundi za OBA klijenta ravnopravno
                stats[caller]['duration'] += duration_sec
                stats[callee]['duration'] += duration_sec
                
                # Registrujemo oba klijenta u adresar poznanstava drugoga 
                stats[caller]['peers'].add(callee)
                stats[callee]['peers'].add(caller)
                
        # 4) Generisanje izlazne forme nakon što se fajl logova isčita do kraja
        out_lines = []
        # Preuzimamo sortirane ključeve i izlistavamo korisnike po redosledu kako su traženi specifikacijom
        for number in sorted(stats.keys()):
            data = stats[number]
            duration = data['duration']
            
            # Sortiramo telefonske brojeve kolega sa kojima su telefonirali od malog ka većem pretvorene u zajednički string razdvojen zarezom
            peers_sorted = ",".join(sorted(list(data['peers'])))
            
            # Krajnja maska koja ispisuje format "broj(ukupne_sekunde):ostali_brojevi_prijatelja"
            out_lines.append(f"{number}({duration}):{peers_sorted}")
            
        # 5) Fizičko prebacivanje novo-pripremljenih informacija po linijama na mesto na disku sa zadatim odredištem datoteke
        with open(out_file, 'w', encoding='utf-8') as f:
            if out_lines: # Samo u slučaju da niz nije bezbroj - tj proračunat makar jednoj proveri 
                f.write("\n".join(out_lines) + "\n")
                
    except Exception:
        # Premošćavanje svake izazvane Raise Exeption unutrašnje anomalije i globalni mehanizam ispisivanja greške teksta programa
        print("GRESKA")
        sys.exit()

# Sistemski ulaz pozivanjem preko terminal komadne linije
if __name__ == "__main__":
    main()
