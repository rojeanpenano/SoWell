from firebase_init import db
from datetime import datetime

# Preset calendar tasks with descriptions
preset_tasks = [
    {"task": "Ihanda ang lupa", "description": "Araruhin, suyurin, at pantayin ang lupa bago magtanim."},
    {"task": "Ihanda ang binhi", "description": "Piliin ang magandang klase ng binhi, ibabad at patubuin bago itanim."},
    {"task": "Gumawa ng punlaan", "description": "Gumawa ng seedbed para sa mga binhi, lagyan ng pataba, at ayusin ang lupa."},
    {"task": "Magtanim", "description": "Ilipat ang punla mula punlaan papuntang palayan kapag sapat na ang edad nito."},
    {"task": "Mag-abono", "description": "Maglagay ng pataba bilang unang booster ng tanim, kadalasan basal fertilizer."},
    {"task": "Topdress", "description": "Dagdag na abono para sa palay habang tumutubo, ginagawa sa ika-2 o ika-4 na linggo."},
    {"task": "Magpatubig", "description": "Panatilihing basa ang palayan sa tamang oras at stage ng paglaki ng palay."},
    {"task": "Magbunot ng damo", "description": "Alisin ang mga damong tumutubo sa paligid ng tanim para hindi makasagabal."},
    {"task": "Magbantay ng peste", "description": "Regular na suriin ang palayan kung may peste o sakit tulad ng kuhol, GLH, o stemborer."},
    {"task": "Mamulot ng kuhol", "description": "Kolektahin ang mga kuhol sa palayan para hindi masira ang mga bagong tanim."},
    {"task": "Mag-ani", "description": "Um-ani ng palay kapag halos lahat ng butil ay hinog na (80-85%)."},
    {"task": "Magtuyo ng ani", "description": "Patuyuin ang palay sa araw o dryer para hindi ito masira sa imbakan."},
    {"task": "Mag-imbak", "description": "Ilagay sa sako at itabi sa tuyo at malamig na lugar ang tuyong palay."}
]

# Upload to Firestore
for task in preset_tasks:
    db.collection("calendar_events").add({
        "task": task["task"],
        "description": task["description"],
        "is_custom": False,
        "scheduled_datetime": None,
        "created_at": datetime.utcnow()
    })

print("Preset calendar events uploaded successfully to Firestore.")