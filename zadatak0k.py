import sys
import os

def izracunaj_trajanje(vreme_polaska, vreme_dolaska):
    """
    Pomoćna funkcija koja računa trajanje leta u minutima.
    Korisno ukoliko let počinje uveče, a završava se posle ponoći s obzirom na to
    da se vremena unose u standardnom hh:mm formatu.
    """
    polazak_sati, polazak_minuti = map(int, vreme_polaska.split(':'))
    dolazak_sati, dolazak_minuti = map(int, vreme_dolaska.split(':'))
    
    ukupno_polazak = polazak_sati * 60 + polazak_minuti
    ukupno_dolazak = dolazak_sati * 60 + dolazak_minuti
    
    # Ako je dolazak brojčano manji od polaska, let se prenosi na naredni dan
    if ukupno_dolazak < ukupno_polazak:
        ukupno_dolazak += 24 * 60
        
    return ukupno_dolazak - ukupno_polazak

def citaj_datoteku(putanja="flights.txt"):
    """
    Funkcija zadužena za bezbedno čitanje tekstualne datoteke i osnovnu
    proveru validnosti zapisa na svakoj liniji.
    Vraća listu linija formatiranih po argumentima ili None ukoliko fajl ne postoji.
    """
    if not os.path.exists(putanja):
        return None  # Vraća None što glavnom programu ukazuje na ispisivanje DAT_GRESKA format
        
    linije_saobracaja = []
    
    with open(putanja, 'r', encoding='utf-8') as f:
        for red in f:
            red = red.strip()
            # Prazne linije se smeju preskakati
            if not red:
                continue
                
            # Na osnovu specifikacije 'airline|cityDep->cityLan|flights', delimo prvo na bazi separatora |
            delovi = red.split('|')
            if len(delovi) != 3:
                raise Exception("GRESKA")
                
            aviokompanija = delovi[0]
            ruta = delovi[1]
            letovi_tekst = delovi[2]
            
            # Format tekst|tekst->tekst znači da srednji segment mora sadržati tačno jedno '->' oznaku
            if ruta.count('->') != 1:
                raise Exception("GRESKA")
                
            grad_polazak, grad_dolazak = ruta.split('->')
            
            # Dodatna zaštita ako su gradovi prazni kodovi (npr. '->PRG')
            if not grad_polazak or not grad_dolazak:
                raise Exception("GRESKA")
                
            linije_saobracaja.append((aviokompanija, ruta, letovi_tekst))
            
    return linije_saobracaja

def obradi_direktne_letove(linije_saobracaja):
    """
    Vrši parsiranje spiska i grupiše sve pronalaske pre nego što upiše na izlaz flights_direct.txt.
    Takođe prosleđuje rečnik ('parsed' letove) kao rezultat radi pametnijeg lova indirektnih letova kasnije.
    """
    # Recnik koji preslikava rutu na listu diktova (rečnika) sa podacima o letovima
    svi_letovi = {}
    
    for auto_kompanija, ruta, svi_letovi_zajedno in linije_saobracaja:
        if ruta not in svi_letovi:
            svi_letovi[ruta] = []
            
        # Blokovi letova u ruti su podeljeni znakom tačka-zarez 
        for jedan_let in svi_letovi_zajedno.split(';'):
            # Validacioni blok detalja za jedan termin (format: hh:mm-hh:mm,price)
            if ',' not in jedan_let or '-' not in jedan_let:
                raise Exception("GRESKA")
                
            polazak_i_dolazak, cena = jedan_let.split(',')
            if polazak_i_dolazak.count('-') != 1:
                raise Exception("GRESKA")
                
            polazak, dolazak = polazak_i_dolazak.split('-')
            
            # Skupljanje i formatiranje pojedinačnog zapisa unutar liste za lakši rad
            podaci_o_letu = {
                'airline': auto_kompanija,
                'dep': polazak,
                'lan': dolazak,
                'duration': izracunaj_trajanje(polazak, dolazak),
                'price': cena,
                'raw': jedan_let # celokupan neizmenjen string za lakšu štampu bez cimanja ('05:30-...')
            }
            
            svi_letovi[ruta].append(podaci_o_letu)
            
    # Zapisivanje u fajl "flights_direct.txt" predefinisanim formatom
    with open("flights_direct.txt", "w", encoding='utf-8') as f_izlaz:
        # Leksikografski redosled odredišta po ključevima rečnika
        for trenutna_ruta in sorted(svi_letovi.keys()):
            f_izlaz.write(f"{trenutna_ruta}\n")
            
            # Grupisanje ponavljanih avio kompanija i njihovih ponuda na toj ruti
            po_kompanijama = {}
            for let in svi_letovi[trenutna_ruta]:
                kompanija = let['airline']
                if kompanija not in po_kompanijama:
                    po_kompanijama[kompanija] = []
                po_kompanijama[kompanija].append(let)
                
            # Potom ispis svake kompanije ponaosob sortirane
            for kompanija in sorted(po_kompanijama.keys()):
                f_izlaz.write(f"{kompanija}\n")
                
                # Zadan propis je hronološki rastući prema vremenu polaska, 
                # a za dalju rezoluciju isto kraće trajanje leta, a zatim leksikografski naziv.
                sortirani_letovi_kompanije = sorted(po_kompanijama[kompanija], key=kljuc_za_sortiranje)
                
                for let in sortirani_letovi_kompanije:
                    f_izlaz.write(f"{let['raw']}\n")
                    
    return svi_letovi

def kljuc_za_sortiranje(x):
    """
    Pomoćna metoda za sortiranje koja garantuje primaran fokus na HH:MM.
    Ako letovi kreću u isto vreme, gleda se kraći let, pa tek onda abeceda oznake.
    """
    return (x['dep'], x['duration'], x['airline'])

def obradi_indirektne_letove(svi_letovi, trazeni_par):
    """
    Identifikacija potencijalnih prelaza u jednom međugradu 
    i formiranje tekstualne datoteke flights_indirect.txt sa prikazom čvorišta i opcija.
    """
    # Zaštita ukoliko podatak ubačen za pretragu uopšte ne sadrži '->'
    if '->' not in trazeni_par:
        # Prazan unos prekidamo mirno, samo formirajući fajl kao izlaznu operaciju
        with open("flights_indirect.txt", "w", encoding='utf-8') as _:
            pass
        return
        
    polazni_grad, ciljni_grad = trazeni_par.split('->')
    
    moguci_medjugradovi = set()
    
    # Pronalazimo destinacije do kojih možemo stići iz prvog startnog grada i idemo iz njih do kraja
    for ruta in svi_letovi.keys():
        pocetak, kraj = ruta.split('->')
        if pocetak == polazni_grad and kraj != ciljni_grad:
            # Ako postoji let iz tog potencijalnog međugrada u naš stvarni ciljni grad
            if f"{kraj}->{ciljni_grad}" in svi_letovi:
                moguci_medjugradovi.add(kraj)
                
    # Sortiranje međugradova leksikografski
    sortirani_medjugradovi = sorted(list(moguci_medjugradovi))
    
    with open("flights_indirect.txt", "w", encoding='utf-8') as f_izlaz:
        for medjugrad in sortirani_medjugradovi:
            ruta_prvi_deo = f"{polazni_grad}->{medjugrad}"
            ruta_drugi_deo = f"{medjugrad}->{ciljni_grad}"
            
            validne_konekcije = []
            
            # Kombinujemo sve letove iz prvog sektora sa svim letovima iz drugog sektora
            for let1 in svi_letovi[ruta_prvi_deo]:
                for let2 in svi_letovi[ruta_drugi_deo]:
                    # Obavezna provera izvodljivosti (da prelazni let stiže pre nego što poleti finalni avion sa čvorišta)
                    if let1['lan'] <= let2['dep']:
                        validne_konekcije.append((let1, let2))
                        
            # Ukoliko nakon filtracije ipak nema logičkih i bezbednih spojeva s tim gradom
            if not validne_konekcije:
                continue
                
            # Štampa punu relaciju prvim ispisnim redom bloka
            f_izlaz.write(f"{polazni_grad}->{medjugrad}->{ciljni_grad}\n")
            
            # Skrivamo duplikate levih strana (Start-Med) prvih konekcija koristeći set ključa i raw podataka
            validni_prvi_letovi = []
            zabelezene_id = set()
            for let_prvi, let_drugi in validne_konekcije:
                jedinstveni_kljuc = (let_prvi['airline'], let_prvi['raw'])
                if jedinstveni_kljuc not in zabelezene_id:
                    validni_prvi_letovi.append(let_prvi)
                    zabelezene_id.add(jedinstveni_kljuc)
                    
            # Sortiranje 'let 1' elemenata na zadani način sa metode kljuc_za_sortiranje
            validni_prvi_letovi.sort(key=kljuc_za_sortiranje)
            
            for let_1 in validni_prvi_letovi:
                # Glavni segment prelaza (Let 1 zajedno uz naziv avio-kompanije koja obavlja prevoz)
                f_izlaz.write(f"{let_1['airline']} {let_1['raw']}\n")
                
                # Svaki podudarni (i uslovljen priloženom satnicom na čekanju) let 2
                prateci_letovi = [v[1] for v in validne_konekcije if v[0] == let_1]
                prateci_letovi.sort(key=kljuc_za_sortiranje)
                
                # Let 2 koji sledi let 1 uz blagu vizuelnu hijerarhiju (2 space-a indentacije ispred komp.)
                for let_2 in prateci_letovi:
                    f_izlaz.write(f"  {let_2['airline']} {let_2['raw']}\n")

def main():
    """
    Krupni upravljački logički tok kroz sve faze sa hvatanjem i obradama generičkih i datotečnih Exception-a u Pythonu.
    """
    try:
        # Čita se željeni format i ispravno razdvaja "grad_polaska->grad_dolaska" sa STDIN (terminal) po zadatku
        trazeni_par = sys.stdin.readline().strip()
        
        # Prazan unos prekidamo shodno upozorenju iz samog zaglavlja PDF uvodnog teksta 
        if not trazeni_par:
            return
            
        # Potrebna datoteka "flights.txt" se traži i otvara putem prve pot-funkcije
        linije_saobracaja = citaj_datoteku("flights.txt")
        
        # Sigurnosni mehanizam DAT_GRESKA ukoliko metod prijavi da datoteka prosto ne postoji  
        if linije_saobracaja is None:
            print("DAT_GRESKA")
            return
            
        # Obrađen direktni prolaz nad ruterom koji istovremeno ispisuje ali i vraća parsirani rečnik (Dictionary) obradjenih formata
        svi_letovi = obradi_direktne_letove(linije_saobracaja)
        
        # Ostatku programa prosleđujemo mapu ispravnih letova da uradi laku kalkulaciju nad prelazima i presedanjima
        obradi_indirektne_letove(svi_letovi, trazeni_par)
        
    except Exception as e:
        # Prema zadatku, svaka ostala generička opšta greška tipa Exception na operaciji krahira program prekidom ali uz prethodni ispis "GRESKA"
        print("GRESKA")

if __name__ == '__main__':
    main()
