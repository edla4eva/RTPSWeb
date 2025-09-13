# pip install faker
import random
from faker import Faker


# Sample name pools by region
hausa_names = ['Ali', 'Sadiq', 'Amina', 'Bilkisu', 'Yusuf']
yoruba_names = ['Modupe', 'Tobi', 'Ayodele', 'Temi', 'Folake']
igbo_names = ['Nwanchukwu', 'Chinonso', 'Obinna', 'Ngozi', 'Uche']
edo_names = ['ANSWER', 'OKONKWO ', 'EHIMARE', 'BADEJO', 'AGBONTAEN ', 'ADIGIDA', 'Adogah', 'Agbaje', 'AGBOGUN', 'AGHEMELO ', 'AGWU ', 'AIGBEDE', 'Jeffrey', 'AJAYI', 'AKOWE', 'AMAECHI ', 'AMIOKPOMO ', 'ANAKA', 'ANAVHEOKHAI ', 'ARHARHIRE', 'ARINZE ', 'CHARLES', 'EBOSELE', 'EDEMI', 'Efemena ', 'EFETEYAN', 'EHIOROBO ', 'EHIZIBUE ', 'EMOKPAE ', 'ESEWI', 'GODSPOWER', 'IBINAYIN ', 'IGBINOBA ', 'IGHAWUANRE ', 'IKHANA-ISEH', 'IKHILE', 'ILEAVBARE', 'IMARHIAGBE ', 'IMHIENITIE ', 'INOMWAN ', 'SAMUEL ', 'ISERA', 'IYENGUNMWENA ', 'JOSEPH ', 'KAZUNFA', 'KUYINU', 'Momodu', 'MUABOR', 'Nwachukwu ', 'OAIKHENA ', 'OBASUYI', 'Obeira', 'OBIOHA', 'ODIASE–OSAHON', 'OGBEMUDIA ', 'Ogbonna', 'OJAME', 'Okeke', 'OKEKE ', 'OKEREKE ', 'OKHUELEIGBE ', 'OKOJI ', 'OKOROM', 'OKOUGBO ', 'OKOYE ', 'OLIVES', 'OMAGE', 'OMONUWA ', 'OMORUYI ', 'ONOWU', 'Onwualu', 'ONYEKA ', 'OSAGIE', 'OSAGIE', 'SUNNY', 'OSAMUYI', 'OSAROBO ', 'OSELUKWUE ', 'OSE-UGIAGBE ', 'OSIFO ', 'OTUYOMA', 'OZILI', 'OZONUWE', 'UDOCHI', 'UDOETTE', 'UKPONG ', 'MUONEKE', 'OSAMUDIAMEN ', 'AIGBOKHABHO ', 'SANU', 'AKPALA ', 'OGIEVA ', 'AZAKAYE ', 'OBAZEE ', 'OWHOFASA', 'IYASELE', 'KALESANWO', 'ARCHIBONG ', 'ODION ', 'EHONWA', 'OBIANKE ']


# Combine all names
all_names = hausa_names + yoruba_names + igbo_names + edo_names


fake = Faker()
for _ in range(100): 
    print(fake.name() + "," + random.choice(all_names))
