def parse_email(email):
    """
    Korisnička funkcija koja proverava da li prosleđeni string predstavlja validnu E-mail adresu
    po specifičnim pravilima ustanove.
    
    Pravila za email formacije:
    - Svi karakteri do '@' osim ' ', '|' i '-'. (prefiks)
    - Opciono reč "student." odmah nakon '@' simbola.
    - Tačno 3 slova alfabeta (A-Z ili a-z). (fakultet/ustanova)
    - Nastavak .rs ili .bg.ac.rs
    
    Vraća normalizovanu email adresu i njenu skraćenu verziju za prikaz na ekranu,
    ili 'None' ukoliko email ne zadovaljava zadate uslove.
    """
    
    # Razdvajanje email adrese na prefiks i domen preko '@' simbola
    parts = email.split('@')
    if len(parts) != 2:
        return None
        
    prefix = parts[0]
    domain = parts[1]
    
    if not prefix:
        return None
        
    # Provera da li prefiks sadrži nedozvoljene karaktere (' ', '|', '-', '@') i prazne karaktere
    for char in prefix:
        if char in (' ', '\t', '\n', '\r', '|', '-', '@'):
            return None
            
    # Provera i izdvajanje opcionog student dela
    student_part = ""
    if domain.startswith("student."):
        student_part = "student."
        domain = domain[len("student."):] # Uklanjamo "student." iz domena za dalju obradu
        
    # Izdvajanje fax/ustanove (sve do prve tačke) i sufiksa (od prve tačke)
    dot_idx = domain.find('.')
    if dot_idx == -1:
        return None
        
    fax = domain[:dot_idx]
    
    # Fax/ustanova mora sadržati tačno 3 slova alfabeta
    if len(fax) != 3 or not fax.isalpha():
        return None
        
    suffix = domain[dot_idx:]
    
    # Sufiks mora biti .rs ili .bg.ac.rs
    if suffix not in ('.rs', '.bg.ac.rs'):
        return None
        
    # Normalizovana email adresa u malim slovima (.lower()) za lakše poređenje u procesima
    norm = f"{prefix}@{student_part}{fax}.rs".lower()
    
    # Format prikaza ("Display") adrese koji će ići u finalni fajl
    disp = f"{prefix}-{fax}"
    
    return norm, disp

def main():
    """
    Glavna potprogram funkcija.
    Skelet aplikacije zadužen za učitavanje putanja, čitanje datoteke sa diska
    te pisanje u novi txt dokument.
    """
    try:
        # 1) Učitavanje standardnog ulaza (ime ulazne i izlazne datoteke)
        ulaz = open(0, "r", encoding='utf-8')
        input_lines = ulaz.read().splitlines()
        
        # Očekujemo obavezna makar dva reda teksta na standardnom stdin-u
        if len(input_lines) < 2:
            return
            
        in_file = input_lines[0].strip()
        out_file = input_lines[1].strip()
        
        if not in_file or not out_file:
            return
            
        # 2) Učitavanje sadržaja iz targetirane tekstualne datoteke (in_file)
        try:
            with open(in_file, 'r', encoding='utf-8-sig') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print("DAT_GRESKA")
            return
            
        stats = {}  # Rečnik (dict) gde čuvamo statistiku dopisivanja za svakog pronađenog korisnika
        
        # 3) Analiziramo učitane linije datoteke
        for line in lines:
            # Uklanjamo prelaske u novi red i nevidljive karaktere (\n Unix, \r Windows) sa kraja desne strane (rstrip)
            line = line.rstrip('\n').rstrip('\r')
            if not line:
                continue
                
            # Logika razdvajanja 1: Odvajanje adrese pošiljaoca ("Šalje") od onih koji "Primaju" poruku zajedno sa porukom uz pomoć delimiter bloka '|'
            parts1 = line.split('|')
            if len(parts1) != 2:
                raise Exception()
                
            sa = parts1[0].strip() # 'Sa' je adresa prvog sagovornika
            
            # Logika razdvajanja 2: Izvrtanje primaoca i teksta poruke koje razdvaja '-' kao delimiter
            parts2 = parts1[1].split('-')
            
            # Ako postoji manje/više od dva polja, formatiranje cele linije u datoteci nije ispravno
            if len(parts2) != 2:
                raise Exception()
                
            na = parts2[0].strip()   # 'Na' je drugi sagovornik
            poruka = parts2[1]       # 'Poruka' je asocirana poruka koju prenosimo
            
            # Pozivanje naše funkcije (za verifikovanje) sa početka fajla
            sa_res = parse_email(sa)
            na_res = parse_email(na)
            
            # Ukoliko bilo gornja (sa) ili donja (na) adresa ispadne 'None', preskoči skript izraz greškom
            if not sa_res or not na_res:
                raise Exception()
                
            # Raspakujemo tuple strukture n-torki preuzete iz metode iznad
            sa_norm, sa_disp = sa_res
            na_norm, na_disp = na_res
            
            # Računanje niza poslatih znakova putem len() funkcije koja vraća broj stringova
            chars = len(poruka)
            
            # Inicijalizacija profila korisnika ukoliko pošiljalac i/ili primalac još nisu uvedeni u evidenciju evidencije 'stats' rečnika
            if sa_norm not in stats:
                stats[sa_norm] = {'disp': sa_disp, 'chars': 0, 'peers': set()}
            if na_norm not in stats:
                stats[na_norm] = {'disp': na_disp, 'chars': 0, 'peers': set()}
                
            # Akumuliramo pročitane znake razmenjene linije za oba sagovornika
            stats[sa_norm]['chars'] += chars
            stats[na_norm]['chars'] += chars
            
            # Evidentiranje njihovog "peer-to-peer" kontakta putem set() strukture podataka (štiti od dupliranja automatski!)
            stats[sa_norm]['peers'].add(na_disp)
            stats[na_norm]['peers'].add(sa_disp)
            
        # 4) Sastavljanje struktura za izlazni fajl u listu
        out_lines = []
        for norm, data in stats.items():
            # Izdvajati sačuvane podatke korisnika
            disp = data['disp']
            chars = data['chars']
            
            # Sortiranje (abc) kontakata pomoću sorted() dok spajamo sve kroz novu ',' delimiter vezu
            peers_sorted = ",".join(sorted(list(data['peers'])))
            
            # Formatiranje reda na način prikaza zadat specifikacijom i pakovanje nazad
            out_lines.append(f"{disp}({chars}):{peers_sorted}")
            
        # Alfabetski organizuj sve linije korisnika u novoj listi 
        out_lines.sort()
        
        # 5) Generisanje ili prebrisavanje postojećeg rezultanta izlaza na hard disk
        with open(out_file, 'w', encoding='utf-8') as f:
            if out_lines: # Provera osigurava da nam se program ne sruši na prazan niz
                f.write("\n".join(out_lines) + "\n")
                
    except Exception:
        # Sve greške hvata zajednička 'Catch-all' Exeption zgrada, uz prekid izvršne moći programa
        print("GRESKA")
        return

if __name__ == "__main__":
    main()
