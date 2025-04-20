from django.core.management.base import BaseCommand
from estimateApp.models import MaterialDescription

class Command(BaseCommand):
    help = "Load or update material descriptions from a hardcoded list"

    def handle(self, *args, **options):
        # Multi-line string with material names.
        materials_data = """
            9m Wooden Pole
            Aluminum Cable
            D-Iron Complete
            Stay Complete
            1.5mm Cable
            3×3 Patrix Box
            Trunk
            One Gang One Way Switch
            Speaker Screw & Wall Plug
            Complete Lightning Arrestor
            35mm Bare Copper
            Excavation of 4×6 feet deep
            Palm Kennel Chaff
            Test Joint
            3Phase 40KA Hager Surge
            Earth Rod Pure Copper
            Panel Box (400×300)
            Transformer
            RCD
            2 Pole Breaker
            Single Breaker
            Panel Accessories
            6mm Black Cable
            6mm Red Cable
            6mm Earth Cable
            AC Switch
            25×38 Trunks
            32 Amps MCCB
            1×6 Screws
            3×3 Patrik Box
            Aluminum Conductor
            3×4mm Flexible Core
            32Amps 2Pole MCB Breaker
            4mm Cable Lugs
            Tower Clips
            Breaker Box
            1.5 Horsepower Pump
            Booster
            Holder Tap
            Plumbing Accessories
            Digital Instant Water Heater
            Crompton Oral Ceiling Fan
            Spotlight
            Round Led Light
            50WATT Led Fork Light
            13Amps Double Socket
            100Amps 30mmA RCD
            1 Gang two way Switch
            3 Gang Switch
            2 Gang Switch
            2 Core flexible Wire
            Fan Hook
            Ceiling Roes
            Lamp Holder
            Pure Copper Earth Rod
            Earth Accessories
            25mm Twin Cable
            3×3 conduit box
            3×6 conduit box
            Circular box
            PVC pipe Interplast
            Complete Control Panel
            1.5mm Cable Gray (Tropical)
            1.5mm Cable Blue (Tropical)
            1.5mm Cable Brown (Tropical)
            1.5mm Cable Black (Tropical)
            2.5mm Cable Blue (Tropical)
            2.5mm Cable Black (Tropical)
            2.5mm Cable Gray (Tropical)
            2.5mm Cable Brown (Tropical)
            2.5mm Cable Earth (Tropical)
            4mm Cable Blue (Tropical)
            4mm Cable Brown (Tropical)
            4mm Cable Black (Tropical)
            4mm Cable Gray (Tropical)
            4mm Cable Earth (Tropical)
            16mm Cable Blue, Brown, Black and Gray
            16mm Cable Earth (Tropical)
            TV Cable (Tropical)
            2.5mm 3 core flex cable
            40Amps Contactor
            Delay Timer
        """
        # Correct the method to strip whitespace: use name.strip()
        material_list = [name.strip() for name in materials_data.strip().splitlines() if name.strip()]
        
        added = 0
        skipped = 0
        for material in material_list:
            obj, created = MaterialDescription.objects.get_or_create(name=material)
            if created:
                added += 1
            else:
                skipped += 1

        print(f"{added} materials added, {skipped} were already in the database.")
