def main():
    try:
        ulaz = open(0, 'r', encoding='utf-8')
        # 1) Učitati podatke sa standardnog ulaza
        input_data = ulaz.read().splitlines()
        
        target_izdavac = ""
        target_manga = ""
        
        # Očistimo ulaz The first line is publisher, second is manga
        if len(input_data) > 0:
            target_izdavac = input_data[0].strip()
        if len(input_data) > 1:
            target_manga = input_data[1].strip()
        
        if not target_izdavac:
            return

        manga_data = {}
        publisher_mangas = set()

        # 2) Učitati iz zadate datoteke manga.txt
        try:
            with open("manga.txt", "r", encoding="utf-8-sig") as f:
                file_lines = f.readlines()
        except FileNotFoundError:
            print("DAT_GRESKA")
            return

        # Parsiranje datoteke
        for line in file_lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(',')
            if len(parts) < 5:
                raise Exception()
            
            cleaned_parts = [p.strip() for p in parts]
            if any(not p for p in cleaned_parts):
                raise Exception()
            
            naziv_mange = cleaned_parts[0]
            izdavac = cleaned_parts[1]
            datum_str = cleaned_parts[2]
            
            if not (len(datum_str) == 8 and datum_str[2] == '.' and datum_str[7] == '.' and datum_str[:2].isdigit() and datum_str[3:7].isdigit()):
                raise Exception()
            
            mm = int(datum_str[0:2])
            yyyy = int(datum_str[3:7])
            date_key = (yyyy, mm)
            
            try:
                broj_strana = int(cleaned_parts[3])
                if broj_strana <= 0:
                    raise Exception()
                
                ch_starts = []
                for p in cleaned_parts[4:]:
                    vp = int(p)
                    if vp <= 0:
                        raise Exception()
                    ch_starts.append(vp)
            except ValueError:
                raise Exception()
            
            if any(s > broj_strana for s in ch_starts):
                raise Exception()
            
            ch_starts.sort()
            
            lengths = []
            for i in range(len(ch_starts) - 1):
                length = ch_starts[i+1] - ch_starts[i]
                if length <= 0:
                    raise Exception()
                lengths.append(length)
            
            last_length = broj_strana - ch_starts[-1] + 1
            if last_length <= 0:
                raise Exception()
            lengths.append(last_length)
            
            if naziv_mange not in manga_data:
                manga_data[naziv_mange] = []
            manga_data[naziv_mange].append({
                'date_key': date_key,
                'izdavac': izdavac,
                'lengths': lengths
            })
            
            if izdavac == target_izdavac:
                publisher_mangas.add(naziv_mange)
                
        # Kreiranje prve izlazne datoteke
        izd_filename = "_".join(target_izdavac.lower().split()) + ".txt"
        
        out_lines = []
        for manga in sorted(list(publisher_mangas)):
            vols = []
            for v in manga_data[manga]:
                if v['izdavac'] == target_izdavac:
                    vols.append(v)
            vols.sort(key=lambda x: x['date_key'])
            
            all_lengths = []
            for v in vols:
                all_lengths.extend(v['lengths'])
                
            num_vols = len(vols)
            num_chaps = len(all_lengths)
            avg_len = sum(all_lengths) / num_chaps if num_chaps > 0 else 0.0
            avg_str = f"{avg_len:.2f}"
            if avg_str.endswith(".00"):
                avg_str = str(int(avg_len))
            elif avg_str[-1] == '0':
                avg_str = avg_str[:-1]
            
            l1 = f"{manga}, {num_vols}, {num_chaps}, {avg_str}"
            l2 = ", ".join(str(x) for x in all_lengths)
            out_lines.append(l1)
            out_lines.append(l2)
            
        with open(izd_filename, "w", encoding="utf-8") as f:
            if out_lines:
                f.write("\n".join(out_lines) + "\n")

        # Kreiranje druge izlazne datoteke (chapters.txt)
        if target_manga and target_manga in manga_data:
            vols = manga_data[target_manga]
            vols.sort(key=lambda x: x['date_key'])
            
            min_len = None
            shortest_chaps = []
            
            for tom_idx, v in enumerate(vols, 1):
                for ch_idx, length in enumerate(v['lengths'], 1):
                    if min_len is None or length < min_len:
                        min_len = length
                        shortest_chaps = [(tom_idx, ch_idx)]
                    elif length == min_len:
                        shortest_chaps.append((tom_idx, ch_idx))
            
            if min_len is not None:
                # Sortiranje rastući po rednom broju poglavlja
                shortest_chaps.sort(key=lambda x: x[1])
                
                with open("chapters.txt", "w", encoding="utf-8") as f:
                    for t, c in shortest_chaps:
                        f.write(f"{t}.{c}\n")
                    f.write(f"{min_len}str\n")

    except Exception:
        print("GRESKA")
        return

if __name__ == "__main__":
    main()
