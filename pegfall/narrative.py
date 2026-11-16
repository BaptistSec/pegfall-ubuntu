from dataclasses import dataclass

@dataclass(frozen=True)
class FarmDay:
    title: str
    surface: str
    warmth: int = 5
    weather: str = 'clear'
    crowd: int = 0
    neighbour: bool = False
    dog: bool = True
    whistle: bool = False
    music: str = 'quiet'
FARM = (FarmDay('The first customer', 'The homemade attraction is ready for its first customer.', neighbour=True, whistle=True), FarmDay('The painted sign', 'First earnings put a painted name on the attraction.'), FarmDay('Fence repair', 'A broken span by the lane is made sound.', neighbour=True), FarmDay('The barn roof', 'The roof is patched. Rain makes the windows feel warm.', weather='rain'), FarmDay('A week in business', 'A crate of new balls marks a week of steady work.', music='soft'), FarmDay('New mechanism oiling', 'Truer salvaged parts make the cradle easier to move.', music='soft'), FarmDay('The awning', 'A new awning shelters the first ordinary crowd.', crowd=4, music='soft'), FarmDay('The pig pen', 'The pen and path are repaired.', whistle=True, crowd=4, music='soft'), FarmDay('Lanterns', 'Lanterns make an evening opening possible.', weather='evening', crowd=4, music='soft'), FarmDay('Locally known', 'A small queue forms for the attraction.', crowd=8, music='warm'), FarmDay('The far field', 'A second plot beyond the lane is now rented.', warmth=4, crowd=4, music='warm'), FarmDay('The new door', 'The farmhouse receives a sound new door.', warmth=4, crowd=4, music='warm'), FarmDay('Fence extended', 'The new plot receives a longer boundary.', warmth=4, weather='evening', crowd=4, music='warm'), FarmDay('The second board', 'A second attraction board is built.', warmth=4, crowd=4, music='warm'), FarmDay('The best season', 'The harvest and trade have made a good year.', warmth=5, crowd=6, music='warm'), FarmDay('The extension', 'Work begins on the house extension.', warmth=4, crowd=3, music='warm'), FarmDay('The new board painted', 'The second board receives its own painted finish.', warmth=4, neighbour=True, music='warm'), FarmDay('After the storm', 'Storm damage is cleared and repaired.', warmth=4, crowd=2, music='warm'), FarmDay('Nearly there', 'Savings are almost sufficient for the village move.', warmth=4, dog=False, music='warm'), FarmDay('The send-off', 'The farm turns out. The move has been earned.', warmth=4, crowd=9, dog=False, music='warm'))
PERCEPTION_LEVELS = (13, 34, 48, 58)
PLANTS = {'neighbour': (1, 3, 17), 'dog_absence': (19,), 'regular': (22, 25, 28, 31), 'apron': (27,), 'flat': (29,)}

def farm_day(index):
    return FARM[max(0, min(19, int(index)))]

@dataclass(frozen=True)
class VillageDay:
    title: str
    surface: str
    warmth: int = 3
    crowd: int = 8
    regular: bool = False
    rain: bool = False
    festival: bool = False
VILLAGE = (VillageDay('The stall', 'A rented market stall opens on the village cobbles.', 4), VillageDay('Repairs to the stall', 'The stall is patched and painted after its first trade.', 4, regular=True), VillageDay('The awning, again', 'A better awning and counter shelter the attraction.', 4), VillageDay('The signwriter', 'A painted sign gives the attraction a proper street name.', 4), VillageDay('A month in the village', 'The first month is banked and the stock expands.', regular=True), VillageDay('From stall to shop', 'A small shopfront houses the larger machine and extended rail.'), VillageDay('The apron', 'Shelves are stocked; a spare apron hangs beside the counter.'), VillageDay('Market day', 'A fine market day brings the richest trade of the month.', 4, 14, True), VillageDay('The flat improves', 'Furniture makes the room above the shop a warmer home.'), VillageDay('Established', 'The attraction has become a fixture of the village street.'), VillageDay('The delivery cart', 'A sound cart extends the reach of an ordinary thriving trade.', regular=True), VillageDay('Fresh paint', 'The shopfront receives a clean coat of paint.'), VillageDay('The festival', 'The shop stays open through the village festival.', crowd=12, festival=True), VillageDay('A quiet weekday', 'Ordinary trading pays for a small stock improvement.'), VillageDay('The back room', 'The shop expands into a useful room behind the counter.'), VillageDay('The long week', 'Busy days keep stock turning through the shop.'), VillageDay('Rain', 'A wet trading day finds the men quietly working under cover.', crowd=4, rain=True), VillageDay('A stock refresh', 'Fresh stock and sound fittings keep the business ready.'), VillageDay('The crates', 'Packing begins for the move to the city.'), VillageDay('The farewell', 'The village turns out; the move to the city has been earned.', crowd=16))

def village_day(index):
    return VILLAGE[max(0, min(19, int(index) - 20))]

@dataclass(frozen=True)
class CityDay:
    title: str
    surface: str
    warmth: int = 3
    crowd: int = 16
    evening: bool = False
    still: bool = False
CITY = (CityDay('The pitch', 'A tiny rented pitch opens on the busy city street.'), CityDay('Pitch repairs', 'The pitch is made sound and the attraction board is painted.'), CityDay('First city customers', 'The attraction earns its first city takings.'), CityDay('The sign over the pitch', 'A proper sign gives the pitch a name.'), CityDay('A month in the city', 'A fine month of trading begins a new savings fund.', crowd=20), CityDay('The lease', 'A small leased shop brings the attraction to a street frontage.'), CityDay('Fit-out', 'The interior receives the finest machine and fittings so far.'), CityDay('An ordinary day', 'Regular trading keeps the little shop in good order.'), CityDay('Saturday', 'A busy and profitable Saturday fills the street.', 4, 24), CityDay('The name over the door', 'The attraction has become a city institution.', 2), CityDay('The better address', 'A good street and sound premises make the work comfortable.', 2), CityDay('Two cups', 'An ordinary day of steady trade in the smart shop.', 2), CityDay('An ordinary Tuesday', 'The attraction opens as usual for another trading day.', 2), CityDay('Open for trade', 'The shop opens for an ordinary day of trade.', 2), CityDay('Refinements', 'Small improvements keep the successful premises in good order.', 2), CityDay('The prestige premises', 'The attraction has its finest address and fittings yet.', 2), CityDay('The still day', 'A calm windless day finds the attraction open as usual.', 2, still=True), CityDay('Another trading day', 'Ordinary trade continues on the busy street.', 2), CityDay('The attraction at its best', 'The perfected machine serves a warm evening crowd.', 2, 22, True), CityDay('The finale', 'The attraction is celebrated; the work built something real.', 2, 24, True))

def city_day(index):
    return CITY[max(0, min(19, int(index) - 40))]

def title(index, fallback):
    return farm_day(index).title if index < 20 else village_day(index).title if index < 40 else city_day(index).title if index < 60 else fallback

def operator_warmth(level):
    if level <= 20:
        return farm_day(level - 1).warmth
    if level <= 40:
        return village_day(level - 1).warmth
    return city_day(level - 1).warmth

def music_key(index):
    return 'farm_%02d' % (index + 1) if index < 20 else 'village_%02d' % (index + 1) if index < 40 else 'city_%02d' % (index + 1)
