# WO-HANKEFILT01: Hankejuht Filter + Cleanup
**P1** | brrr-hankeradar | Gatekeeper: Risto

## Probleem
1. Automaatne cleanup puudub (430->185 kasitsi 2026-03-03, junk tuleb tagasi)
2. Duplikaadid: sama org+pealkiri eri URL-iga
3. is_junk_title() liiga nork

## Fix 1: cleanup_db() src/scraper/base.py
Kaivita is_junk_title() koigil DB kirjetel. Kustuta True. Logi arv.
Kutsu run_scraper.py lopus automaatselt.

## Fix 2: deduplicate_tenders() src/db/database.py
Duplikaat = sama org + normalized_title + published_date +-1 paev.
Hoia vanim kirje. Kutsu parast cleanup_db().

## Fix 3: is_junk_title() laiendamine
Lisa NOT_TENDER_TITLE_PATTERNS:
soiduauto kindlustus, varakindlustus, ruumide rent, kooskolastus,
eelarve muudatus, pohimaaarus, arengukava, detailplaneering, kmo aruanne
Lisa TOO_GENERIC_TITLES: kutse, kuusitlus, ankeet, avaldus, taotlus

## Fix 4: Slack #cc raport parast scrapit
Hankejuht scrape lopp: ENNE=X, kustutatud Y+Z, JAREL=W
python3 /home/brrr/bin/slack-send.py Claudia cc msg

## EI TOHI
Muuta Supabase sync, kustutada future deadline kirjeid, muuta API endpointe
