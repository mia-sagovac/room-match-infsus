from __future__ import annotations

from typing import Iterable

from models import (
    Korisnik, Profil, Preferencija, Upitnik, OdgovorUpitnika, Pitanje,
)

def _profil_profil_score(p1: Profil, p2: Profil) -> float:

    if not p1 or not p2:
        return 0.0

    score = 0.0

    if p1.urednost is not None and p2.urednost is not None:
        diff = abs(p1.urednost - p2.urednost)
        score += 10 * (1 - diff / 4)
    else:
        score += 5

    if p1.ritam and p2.ritam:
        if p1.ritam == p2.ritam:
            score += 10
        elif "fleksibilno" in (p1.ritam, p2.ritam):
            score += 7
        else:
            score += 0
    else:
        score += 5

    if p1.pusac is not None and p2.pusac is not None:
        score += 5 if p1.pusac == p2.pusac else 0
    else:
        score += 2.5

    if p1.kucni_ljubimci is not None and p2.kucni_ljubimci is not None:
        score += 5 if p1.kucni_ljubimci == p2.kucni_ljubimci else 0
    else:
        score += 2.5

    return score

def _pref_profil_score(pref: Preferencija | None, profil: Profil | None) -> float:

    if not pref or not profil:
        return 7.5

    score = 0.0

    if pref.zeljeni_grad and profil.grad:
        score += 3 if pref.zeljeni_grad.lower() == profil.grad.lower() else 0
    else:
        score += 1.5

    if pref.zeljeni_kvart and profil.kvart:
        score += 2 if pref.zeljeni_kvart.lower() == profil.kvart.lower() else 0
    else:
        score += 1

    if pref.trazi_pusaca is not None and profil.pusac is not None:
        score += 3 if pref.trazi_pusaca == profil.pusac else 0
    else:
        score += 1.5

    if pref.min_urednost and profil.urednost is not None:
        if profil.urednost >= pref.min_urednost:
            score += 4
        else:

            diff = pref.min_urednost - profil.urednost
            score += max(0, 4 - 2 * diff)
    else:
        score += 2

    if pref.zeljeni_ritam and profil.ritam:
        if pref.zeljeni_ritam == profil.ritam:
            score += 3
        elif "fleksibilno" in (pref.zeljeni_ritam, profil.ritam):
            score += 2
    else:
        score += 1.5

    return score

def _najnoviji_upitnik(upitnici: Iterable[Upitnik]) -> Upitnik | None:
    upitnici = list(upitnici or [])
    if not upitnici:
        return None
    return max(upitnici, key=lambda u: (u.verzija, u.datum_ispunjavanja))

def _slicnost_odgovora(o1: OdgovorUpitnika, o2: OdgovorUpitnika,
                       pitanje: Pitanje) -> float:

    v1, v2 = o1.vrijednost, o2.vrijednost

    if pitanje.tip_odgovora == "skala_1_5":
        try:
            n1, n2 = int(v1), int(v2)
            return 1 - abs(n1 - n2) / 4
        except (TypeError, ValueError):
            return 1.0 if v1 == v2 else 0.0

    if pitanje.tip_odgovora == "da_ne":
        return 1.0 if v1.strip().lower() == v2.strip().lower() else 0.0

    if pitanje.tip_odgovora == "visestruki_izbor":
        return 1.0 if v1 == v2 else 0.0

    return 1.0 if v1.strip().lower() == v2.strip().lower() else 0.0

def _upitnik_upitnik_score(k1: Korisnik, k2: Korisnik) -> tuple[float, int]:

    u1 = _najnoviji_upitnik(k1.upitnici)
    u2 = _najnoviji_upitnik(k2.upitnici)
    if not u1 or not u2:
        return 20.0, 0

    odg1 = {o.pitanje_id: o for o in u1.odgovori}
    odg2 = {o.pitanje_id: o for o in u2.odgovori}
    zajednicka = set(odg1) & set(odg2)
    if not zajednicka:
        return 20.0, 0

    ukupna_tezina = 0.0
    ponderirana_slicnost = 0.0
    for pid in zajednicka:
        o1, o2 = odg1[pid], odg2[pid]
        pitanje = o1.pitanje or o2.pitanje
        if not pitanje:
            continue
        tezina = pitanje.tezina or 1
        ukupna_tezina += tezina
        ponderirana_slicnost += tezina * _slicnost_odgovora(o1, o2, pitanje)

    if ukupna_tezina == 0:
        return 20.0, 0
    return 40 * (ponderirana_slicnost / ukupna_tezina), len(zajednicka)

def izracunaj_kompatibilnost(k1: Korisnik, k2: Korisnik) -> tuple[float, dict]:

    profil_dio = _profil_profil_score(k1.profil, k2.profil)

    pref_dio_1 = _pref_profil_score(k1.preferencija, k2.profil)
    pref_dio_2 = _pref_profil_score(k2.preferencija, k1.profil)

    upitnik_dio, n_zajednicka = _upitnik_upitnik_score(k1, k2)

    ukupno = profil_dio + pref_dio_1 + pref_dio_2 + upitnik_dio
    ukupno = round(min(100.0, max(0.0, ukupno)), 2)

    return ukupno, {
        "profil": round(profil_dio, 2),
        "pref_k1_na_k2": round(pref_dio_1, 2),
        "pref_k2_na_k1": round(pref_dio_2, 2),
        "upitnik": round(upitnik_dio, 2),
        "zajednicka_pitanja": n_zajednicka,
    }
