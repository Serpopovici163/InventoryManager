# InventoryManager

Basic inventory manager for Altium BOMs and DigiKey/Mouser orders. This python script allows you to add DigiKey/Mouser orders to a SQLite inventory database, add BOMs to an internal database of PCBs, and automatically subtract the components required by a given PCB from the SQLite inventory database.

Only .csv files are accepted for BOMs. 

TODO:
- Add custom menus in case headers of csv columns
- Intensify logging
- Keep more data about when PCBs are added to system
- Add construct_pcb feature (also maybe add something for substitute or mismatch management in case part number of PCB BOM doesn't match part number in inventory)
- Add manual lookup tools