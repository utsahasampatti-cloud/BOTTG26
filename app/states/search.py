from aiogram.fsm.state import StatesGroup, State


class SearchFSM(StatesGroup):
    # 1. District
    district = State()

    # 2. Property type (flat / house / room)
    property_type = State()

    # ===== BRANCH B: ROOM =====
    # 3B. Room type (single / double / etc.)
    rooms = State()

    # 4B. Room preferences (multi-select)
    preferences = State()

    # ===== COMMON =====
    # 4A / 5B. Max price
    price_to = State()

    # 5A / 6B. Min area
    area_from = State()

    # ===== BRANCH A: FLAT / HOUSE =====
    # 6A. Number of rooms
    rooms_count = State()  # логічно, але не використовується окремо (див. нижче)

    # ===== COMMON TAIL =====
    # 7. Pets allowed
    pets = State()

    # 8. Private / Agency
    private_type = State()
