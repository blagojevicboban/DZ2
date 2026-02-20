import sys
import re

def main():
    """
    Glavna funkcija programa koja vrši obradu podataka o mangama.
    Program učitava metapodatke sa standardnog ulaza, a zatim čita
    tekstualnu datoteku manga.txt, parsira njen sadržaj i ispisuje rezultate.
    """
    try:
        # 1) Učitati podatke sa standardnog ulaza (stdin)
        # Zbog funkcije splitlines(), automatski razdvajamo svaku liniju u element liste
        input_data = sys.stdin.read().splitlines()
        
        target_izdavac = ""
        target_manga = ""
        
        # Očistimo ulaz. Očekuje se da prva linija sadrži ime izdavača, a druga ime mange.
        if len(input_data) > 0:
            target_izdavac = input_data[0].strip()
        if len(input_data) > 1:
            target_manga = input_data[1].strip()
        
        # Ako izdavač nije naveden (prazan unos), prekidamo izvršavanje
        if not target_izdavac:
            return

        manga_data = {}         # Rečnik za skladištenje informacija o svim mangama
        publisher_mangas = set() # Skup u kom ćemo pamtiti sve nage koje su od datog izdavača

        # 2) Učitavanje ulaznih podataka iz zadate datoteke 'manga.txt'
        try:
            # Otvaranje fajla za čitanje, uz postavljanje enkodinga za UTF-8 podršku sa ili bez BOM
            with open("manga.txt", "r", encoding="utf-8-sig") as f:
                file_lines = f.readlines()
        except FileNotFoundError:
            # Ukoliko fajl na disku nije pronađen, ispisuje fiksnu poruku i prekida
            print("DAT_GRESKA")
            return

        # 3) Parsiranje pročitanih linija u datoteci
        for line in file_lines:
            line = line.strip()
            # Ignorišemo sve prazne linije u datoteci
            if not line:
                continue
            
            parts = line.split(',')
            # Svaki red u fajlu mora imati bar 5 polja razdvojenih zarezom
            if len(parts) < 5:
                raise Exception()
            
            # Dalje čišćenje "belih karaktera" sa početka i kraja svakog podatka
            cleaned_parts = [p.strip() for p in parts]
            # Uveravamo se da nijedan element nije ostao potencijalno prazan nakon .strip() komande
            if any(not p for p in cleaned_parts):
                raise Exception()
            
            # Pridruživanje izdvojenih osnovnih delova u varijable po redosledu
            naziv_mange = cleaned_parts[0]
            izdavac = cleaned_parts[1]
            datum_str = cleaned_parts[2]
            
            # Upotreba Regularnog Izraza (Regex) kako bismo proverili ispravnost oblika datuma u formatu MM.GGGG.
            # ^ označava početak, \d{2} je dve cifre, \. je bukvalna tačka, pa 4 cifre, i kraj niske $
            if not re.match(r"^\d{2}\.\d{4}\.$", datum_str):
                raise Exception()
            
            # Sečenje datuma iz stringa i pretvaranje tekstualnih meseca i godine u celobrojne numere (int)
            mm = int(datum_str[0:2])
            yyyy = int(datum_str[3:7])
            # Generišemo ključ kao n-torku (tuple) godina-mesec za lako ređanje kasnije
            date_key = (yyyy, mm)
            
            try:
                # 4. parametar po redu bi trebalo da bude ukupan broj stranica toma
                broj_strana = int(cleaned_parts[3])
                if broj_strana <= 0:
                    raise Exception()
                
                ch_starts = [] # Lista onih stranica od kojih svako poglavlje počinje
                # Prolazi kroz sve preostale elemente iz reda na ulazu koji čine početne brojeve za prvo, drugo... poglavlje
                for p in cleaned_parts[4:]:
                    vp = int(p)
                    if vp <= 0:
                        raise Exception() # Izazivamo grešku obrade (koja skače na kraj try bloka)
                    ch_starts.append(vp)
            except ValueError:
                # Da predupredimo probleme pri cast-u stringa koji bi trebalo da bude broj u int (ValueError)
                raise Exception()
            
            # Poglavlje mangi ne može krenuti na stranici većoj od onoga koliko knjiga uopšte može imati stranica
            if any(s > broj_strana for s in ch_starts):
                raise Exception()
            
            # Sortiramo niz stranica radi logičnog i uobičajenog rasporeda prilikom proračuna
            ch_starts.sort()
            
            lengths = [] # Dužine pojedinačnih poglavlja izražene brojem stranica
            
            # Iteriramo se kroz n-1 elemenata u listi stranica da bismo odredili razlike i saznali broj stranica trenutnog komada
            for i in range(len(ch_starts) - 1):
                # Nažalost nećemo imati dužinu zadnjeg poglavlja sa ovim šablonom pa njega rešavamo ispod loop-a
                length = ch_starts[i+1] - ch_starts[i]
                if length <= 0:  # Nema smisla da poglavlje ima nula ili negativan broj strana (ako su dve stvari imale isti ključ zbog greške ulaza)
                    raise Exception()
                lengths.append(length)
            
            # Manuelno proračunavanje za taj poslednji chapter sve do kraja same knjige manga sveske
            last_length = broj_strana - ch_starts[-1] + 1
            if last_length <= 0:
                raise Exception()
            lengths.append(last_length)
            
            # Ukoliko rečnik ne sadrži manga knjigu od ranije, stvori je i priloži joj praznu listu kao preduslov
            if naziv_mange not in manga_data:
                manga_data[naziv_mange] = []
                
            # Smeštanje proanaliziranih elemenata nazad u matični objekat dict tipa
            manga_data[naziv_mange].append({
                'date_key': date_key,
                'izdavac': izdavac,
                'lengths': lengths
            })
            
            # Obaveštava skup 'publisher_mangas' da ova zbirka mora pratiti u output od traženog izdavača
            if izdavac == target_izdavac:
                publisher_mangas.add(naziv_mange)
                
        # --- Kraj bloka za parsiranje datoteke ---

        # 4) Kreiranje prve izlazne datoteke u kojoj izdvajamo određenu izdavačku kuću
        # Ime tekstualnog fajla mora biti sačinjeno od malih slova imena reči kompanije odvojenih donjim crtama
        izd_filename = "_".join(target_izdavac.lower().split()) + ".txt"
        
        out_lines = []
        # Prebačen nazad u pravu i abecedno uređenu listu svih ključeva - obavezno sort da nas ne minira redosled hasheva u Python set()
        for manga in sorted(list(publisher_mangas)):
            # Odaberimo samo one tomove iz unutrašnjosti (value liste rečnika) čiji je izdavač ciljni target string
            vols = [v for v in manga_data[manga] if v['izdavac'] == target_izdavac]
            
            # Sortiramo te izdvojene elemente korišćenjem anonimne (lambda) ugrađene rutine zasnovanoj na tuple-ovima MM.YYYY iz ranijih koraka
            vols.sort(key=lambda x: x['date_key'])
            
            # Ponovo raspakujemo delove poglavlja samo tog konkretnog toma
            all_lengths = []
            for v in vols:
                all_lengths.extend(v['lengths'])
                
            num_vols = len(vols)
            num_chaps = len(all_lengths)
            # Prosečan broj stranica izračunat kao aritmetička sredina svih poglavlja
            avg_len = sum(all_lengths) / num_chaps if num_chaps > 0 else 0.0
            
            # Predstavljanje naslova, toma, poglavlja i preseka prosečnih strana formatiranom zaporu sa float ispisivanjem na dve decimale 
            l1 = f"{manga}, {num_vols}, {num_chaps}, {avg_len:.2f}"
            # Druga potrebna ispisna linija koja prikazuje same brojeve sekvencionalno povezane kroz ", " kao delimiter.
            l2 = ", ".join(str(x) for x in all_lengths)
            
            out_lines.append(l1)
            out_lines.append(l2)
            
        # Pisanje u ciljani, generisani tekstualni fajl preko komande .write()
        with open(izd_filename, "w", encoding="utf-8") as f:
            if out_lines: # Provera da linije uopšte prilažu elemente pre modifikacije diska
                f.write("\n".join(out_lines) + "\n")

        # 5) Kreiranje druge izlazne datoteke pod specijalnim stalnim imenom ('chapters.txt')
        # Proveravamo da li je meta uneta sa standardnog ulaza validna pre pisanja u novi dokument
        if target_manga and target_manga in manga_data:
            # Selektovana sva njena građa i automatski propuštena sortiranje slična onom kao malo unazad za izdavača
            vols = manga_data[target_manga]
            vols.sort(key=lambda x: x['date_key'])
            
            min_len = None   # Pokazivač koji pretražuje lokalni i globalni minimum dužine
            shortest_chaps = []
            
            # Python enumeracija (enumerate) nam dopušta da elegantnije imamo uvid na kojem smo indeksu, bez korišćenja x += 1 (kreće od baze komada broj 1, ne od bazičnog Nula)
            for tom_idx, v in enumerate(vols, 1):
                for ch_idx, length in enumerate(v['lengths'], 1):
                    # Za prvi krug iniciranje logike jer pokazivači kreću prazni...
                    if min_len is None or length < min_len:
                        min_len = length
                        # Pronalazi novo najmanje - restartuje prethodno sačuvane poglavlje
                        shortest_chaps = [(tom_idx, ch_idx)]
                    # Ukoliko smo naletili na izjednačen obim sveske, dodaj ga ravnopravno u memorije kao i drugog
                    elif length == min_len:
                        shortest_chaps.append((tom_idx, ch_idx))
            
            if min_len is not None:
                # Opet po pravilu zadatka sortiranje rezultujućeg rešenja rastući prema brojevima samog poglavlja
                # (Po default-u bi bilo po izdanjima tj indeksu 0 unutra lambda bloka za parove)
                shortest_chaps.sort(key=lambda x: x[1])
                
                # Izbacivanje rečninkovih formacija teksta na izlaz txt medija  
                with open("chapters.txt", "w", encoding="utf-8") as f:
                    # Svaka n-torka će preuzeti svoju liniju, npr format t.c tj. 4.tom 3.chapter
                    for t, c in shortest_chaps:
                        f.write(f"{t}.{c}\n")
                    f.write(f"{min_len}str\n") # A za kraj fajla ista najmanja cifra u "str" formatu

    except Exception:
        # Premošćavanje celog try() bloka: Neka izuzetna kritična i neslućena greška ili greška koju mi sami trigerujemo kada iskoči iz naših validatora uslova
        print("GRESKA")
        sys.exit()

if __name__ == "__main__":
    main()
