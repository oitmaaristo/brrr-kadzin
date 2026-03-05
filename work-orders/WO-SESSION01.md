# WO-SESSION01: GatewayLogout Safe Mode
**P1** | brrr-printer2 | Gatekeeper: Risto

## Probleem
Engine crashib kui TopStepX sessioon juba avatud teisest kliendist.

## Fix 1: Tuvasta conflict koht
Leia kus GatewayLogout/session conflict visatakse. Lisa täpne error logisse.

## Fix 2: Retry loogika
Conflict tuvastatud -> logi + oota 30s + retry kuni 3x.

## Fix 3: Graceful exit
3 retry ebaonnestub -> postita #printer2 "Engine startup failed: session conflict" -> exit(0).

## Fix 4: Startup sequence
Enne strateegiate laadimist: kontrolli sessiooni staatus REST-iga, logi tulemus.

## EI TOHI
- Logida teisi sessioone valja
- Muuta auth credentials
