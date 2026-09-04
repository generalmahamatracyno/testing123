from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Three Kingdoms", page_icon="⚔️", layout="centered")

IMG = Path("images")

# Put your drawings in an images folder using these names.
PICTURES = {
    "Mage": "mage.png",
    "Pirate": "pirate.png",
    "Priest": "priest.png",
    "Fairy": "fairy.png",
    "Merchant": "merchant.png",
    "Big Bat": "big_bat.png",
    "Drako": "drako.png",
    "Hydra": "hydra.png",
    "Echidna": "echidna.png",
    "Baby Wolf": "baby_wolf.png",
    "Injured Baby Wolf": "injured_baby_wolf.png",
    "Maha Bhediya": "maha_bhediya.png",
    "Indera": "indera.png",
    "Cengkerang": "cengkerang.png",
    "Snake Fang": "snake_fang.png",
    "Wolf Fur": "wolf_fur.png",
    "Crab Shell": "crab_shell.png",
}

ADVENTURERS = {
    "Mage": "Starts with 4 stamina, but merchants charge only 1 coin.",
    "Pirate": "Starts with 2 coins.",
    "Priest": "Starts with 4 hearts, but healing potions restore 2 hearts.",
    "Fairy": "Starts with 6 hearts, but cannot use shields.",
}


def defaults():
    return {
        "scene": "choose", "adventurer": None, "hearts": 5, "max_hearts": 5,
        "stamina": 5, "coins": 0, "weapon": 0, "potions": 0, "shields": 0,
        "message": "", "battle_done": False, "battle_damage": 0,
        "red_key": False, "blue_key": False, "green_key": False,
        "items": [], "baby_wolf": False, "baby_name": "",
        "ophidia_done": False, "wolvendom_done": False, "ketanmara_done": False,
    }


def reset():
    for key, value in defaults().items():
        st.session_state[key] = value.copy() if isinstance(value, list) else value


if "scene" not in st.session_state:
    reset()


def go(scene, message=""):
    st.session_state.scene = scene
    st.session_state.message = message
    st.session_state.battle_done = False
    st.session_state.battle_damage = 0


def picture(name, width=300):
    path = IMG / PICTURES.get(name, "")
    if path.is_file():
        st.image(str(path), width=width)
    else:
        st.caption(f"🖼️ Add your drawing as: images/{PICTURES.get(name, name.lower() + '.png')}")


def choose(name):
    st.session_state.adventurer = name
    st.session_state.hearts = 5
    st.session_state.max_hearts = 5
    st.session_state.stamina = 5
    st.session_state.coins = 0
    if name == "Mage":
        st.session_state.stamina = 4
    elif name == "Pirate":
        st.session_state.coins = 2
    elif name == "Priest":
        st.session_state.hearts = 4
    elif name == "Fairy":
        st.session_state.hearts = 6
        st.session_state.max_hearts = 6
    go("cabin")


def spend_stamina(amount):
    st.session_state.stamina -= amount
    if st.session_state.stamina <= 0:
        st.session_state.hearts -= 1
        st.session_state.stamina += 2
        st.session_state.message = "Your stamina reached zero: you lost 1 heart and recovered 2 stamina."
    check_alive()


def check_alive():
    if st.session_state.hearts <= 0:
        go("game_over", "You ran out of hearts.")


def drink_potion():
    if st.session_state.potions <= 0:
        st.session_state.message = "You don't have a healing potion."
    elif st.session_state.hearts >= st.session_state.max_hearts:
        st.session_state.message = "Your hearts are full. You don't need a healing potion."
    else:
        healing = 2 if st.session_state.adventurer == "Priest" else 1
        old = st.session_state.hearts
        st.session_state.hearts = min(st.session_state.max_hearts, old + healing)
        st.session_state.potions -= 1
        st.session_state.message = f"The potion restored {st.session_state.hearts - old} heart(s)."


def work():
    spend_stamina(1)
    if st.session_state.scene != "game_over":
        st.session_state.coins += 2
        st.session_state.message = "You worked: −1 stamina, +2 coins."


def rest():
    st.session_state.stamina += 2
    st.session_state.message = "You rested and recovered 2 stamina."


def buy(kind, level=0):
    price = 1 if st.session_state.adventurer == "Mage" else 2
    if st.session_state.coins < price:
        st.session_state.message = f"You need {price} coin(s)."
        return
    st.session_state.coins -= price
    if kind == "potion":
        st.session_state.potions += 1
        st.session_state.message = "You bought a healing potion."
    else:
        st.session_state.weapon = max(st.session_state.weapon, level)
        st.session_state.message = f"You bought a level {level} weapon."


def fight(opponent, level):
    spend_stamina(1)
    if st.session_state.scene == "game_over":
        return
    damage = max(0, level - st.session_state.weapon)
    st.session_state.hearts -= damage
    st.session_state.battle_damage = damage
    st.session_state.battle_done = True
    st.session_state.message = f"{opponent} was defeated. You lost {damage} heart(s) and 1 stamina."
    check_alive()


def use_shields_after_fight():
    if st.session_state.adventurer == "Fairy":
        st.session_state.message = "The Fairy cannot use shields."
    elif st.session_state.shields <= 0:
        st.session_state.message = "You don't have a shield."
    elif st.session_state.battle_damage <= 0:
        st.session_state.message = "You lost no hearts in this fight, so you don't need a shield."
    elif st.session_state.hearts >= st.session_state.max_hearts:
        st.session_state.message = "Your hearts are already full."
    else:
        st.session_state.shields -= 1
        st.session_state.hearts += 1
        st.session_state.battle_damage -= 1
        st.session_state.message = "The shield restored 1 heart lost in the fight."


def battle(name, level, next_scene):
    st.subheader(f"⚔️ {name} — Level {level}")
    picture(name)
    if not st.session_state.battle_done:
        st.write(f"Your weapon is level **{st.session_state.weapon}**. You must fight.")
        if st.button("⚔️ Fight", use_container_width=True):
            fight(name, level)
            st.rerun()
    else:
        st.success(st.session_state.message)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🛡️ Use shield", use_container_width=True):
                use_shields_after_fight(); st.rerun()
        with c2:
            if st.button("🧪 Drink healing potion", use_container_width=True, key="battle_potion"):
                drink_potion(); st.rerun()
        if st.button("Next ➡️", type="primary", use_container_width=True):
            go(next_scene); st.rerun()


def status():
    cols = st.columns(5)
    cols[0].metric("❤️", st.session_state.hearts)
    cols[1].metric("⚡", st.session_state.stamina)
    cols[2].metric("🪙", st.session_state.coins)
    cols[3].metric("⚔️", st.session_state.weapon)
    cols[4].metric("🧪", st.session_state.potions)
    st.caption(f"Adventurer: {st.session_state.adventurer or 'Not chosen'} · Shields: {st.session_state.shields}")
    if st.session_state.items:
        st.write("**Important items:** " + ", ".join(st.session_state.items))


def story(title, text):
    st.subheader(title)
    st.write(text)


def next_button(scene, label="Next ➡️"):
    if st.button(label, type="primary", use_container_width=True):
        go(scene); st.rerun()


st.title("🏰 The Three Kingdoms")
if st.session_state.scene != "choose":
    status()
if st.session_state.message and not st.session_state.battle_done:
    st.info(st.session_state.message)

S = st.session_state.scene

if S == "choose":
    story("Choose your adventurer", "Each adventurer has a different ability.")
    cols = st.columns(2)
    for i, (name, ability) in enumerate(ADVENTURERS.items()):
        with cols[i % 2]:
            picture(name, 180)
            st.markdown(f"**{name}**")
            st.caption(ability)
            if st.button(f"Choose {name}", key=name, use_container_width=True):
                choose(name); st.rerun()

elif S == "cabin":
    story("🏚️ The Cabin", "A table holds a red key and a blue key. You may take only one.")
    c1, c2 = st.columns(2)
    if c1.button("Take red key", use_container_width=True):
        st.session_state.red_key = True; go("red_chest"); st.rerun()
    if c2.button("Take blue key", use_container_width=True):
        st.session_state.blue_key = True; go("blue_chest"); st.rerun()
elif S == "red_chest":
    story("🔴 Red Chest", "The red key opens the chest: +1 healing potion and +2 coins.")
    if not st.session_state.message:
        st.session_state.potions += 1; st.session_state.coins += 2; st.session_state.message = "Chest collected."
    next_button("forest", "Leave the cabin and enter the forest ➡️")
elif S == "blue_chest":
    story("🔵 Blue Chest", "The blue key opens the chest: level 1 weapon and +1 coin.")
    if not st.session_state.message:
        st.session_state.weapon = 1; st.session_state.coins += 1; st.session_state.message = "Chest collected."
    next_button("forest", "Leave the cabin and enter the forest ➡️")
elif S == "forest":
    story("🌲 The Forest", "A merchant waits near a heavy stone door.")
    price = 1 if st.session_state.adventurer == "Mage" else 2
    c1, c2 = st.columns(2)
    if c1.button(f"Buy level 1 weapon — {price} coin(s)", use_container_width=True):
        buy("weapon", 1); st.rerun()
    if c2.button(f"Buy potion — {price} coin(s)", use_container_width=True):
        buy("potion"); st.rerun()
    if st.button("Open stone door — 2 stamina", use_container_width=True):
        spend_stamina(2)
        if st.session_state.scene != "game_over": go("cave_choice")
        st.rerun()
elif S == "cave_choice":
    story("🪨 Beyond the Door", "Choose the cave with light or the dark cave.")
    c1, c2 = st.columns(2)
    if c1.button("Cave with light", use_container_width=True): go("bat_battle"); st.rerun()
    if c2.button("Dark cave", use_container_width=True): go("ancient_city"); st.rerun()
elif S == "bat_battle": battle("Big Bat", 1, "ancient_city")

elif S == "ancient_city":
    story("🏛️ Ancient City", "You arrive at the tavern and village centre.")
    c1, c2 = st.columns(2)
    if c1.button("Visit tavern", use_container_width=True): go("tavern"); st.rerun()
    if c2.button("Meet village elder", use_container_width=True): go("elder"); st.rerun()
elif S == "tavern":
    story("🍞 Tavern", "You may work or rest before continuing.")
    c1, c2 = st.columns(2)
    if c1.button("Work: −1 stamina, +2 coins", use_container_width=True): work(); st.rerun()
    if c2.button("Rest: +2 stamina", use_container_width=True): rest(); st.rerun()
    next_button("elder", "Go to the village elder ➡️")
elif S == "elder":
    story("🧙 Village Elder", "The elder tells you about Ophidia, Wolvendom and Ketanmara, then gives you a map to Ophidia.")
    next_button("ophidia")

elif S == "ophidia":
    story("🐍 Ophidia", "Choose where to go first.")
    for label, target in [("Dungeon", "twins"), ("Market", "ophidia_market"), ("Abandoned Temple", "temple")]:
        if st.button(label, use_container_width=True): go(target); st.rerun()
elif S == "ophidia_market":
    story("Ophidia Market", "The merchant sells stronger equipment.")
    price = 1 if st.session_state.adventurer == "Mage" else 3
    c1, c2 = st.columns(2)
    if c1.button(f"Level 2 weapon — {price} coin(s)", use_container_width=True):
        old = st.session_state.coins
        if old >= price: st.session_state.coins -= price; st.session_state.weapon = max(2, st.session_state.weapon); st.session_state.message = "Weapon upgraded."
        else: st.session_state.message = "Not enough coins."
        st.rerun()
    if c2.button(f"Potion — {price} coin(s)", use_container_width=True):
        if st.session_state.coins >= price: st.session_state.coins -= price; st.session_state.potions += 1; st.session_state.message = "Potion bought."
        else: st.session_state.message = "Not enough coins."
        st.rerun()
    next_button("twins", "Go to the dungeon ➡️")
elif S == "temple":
    story("🏚️ Abandoned Temple", "The trail and sanctuary both lead deeper into Ophidia.")
    c1, c2 = st.columns(2)
    if c1.button("Search trail: −2 stamina, +2 coins", use_container_width=True):
        spend_stamina(2); st.session_state.coins += 2; go("echidna_battle"); st.rerun()
    if c2.button("Rest at sanctuary: −2 coins, +1 stamina", use_container_width=True):
        if st.session_state.coins >= 2: st.session_state.coins -= 2; st.session_state.stamina += 1; go("echidna_battle")
        else: st.session_state.message = "You need 2 coins."
        st.rerun()
elif S == "twins":
    story("🐍 The Serpent Twins", "Drako and Hydra each offer help. Choose one.")
    c1, c2 = st.columns(2)
    with c1:
        picture("Drako", 180)
        if st.button("Choose Drako: shield +2 coins", use_container_width=True):
            st.session_state.shields += 1; st.session_state.coins += 2; go("echidna_battle"); st.rerun()
    with c2:
        picture("Hydra", 180)
        if st.button("Choose Hydra: level 2 weapon +1 coin", use_container_width=True):
            st.session_state.weapon = max(2, st.session_state.weapon); st.session_state.coins += 1; go("echidna_battle"); st.rerun()
elif S == "echidna_battle": battle("Echidna", 2, "ophidia_ruler")
elif S == "ophidia_ruler":
    story("👑 Choose Ophidia's Ruler", "After the fight, the twins ask you to appoint a ruler.")
    c1, c2 = st.columns(2)
    if c1.button("Crown Drako", use_container_width=True):
        st.session_state.items += ["Snake Fang"]; st.session_state.ophidia_done = True; go("before_wolvendom", "Drako is crowned and gives you a Snake Fang and map."); st.rerun()
    if c2.button("Crown Hydra", use_container_width=True):
        st.session_state.hearts -= 1; st.session_state.items += ["Snake Fang"]; st.session_state.ophidia_done = True; go("before_wolvendom", "Hydra betrays you. You and Drako escape; you lose 1 heart. Drako becomes king."); st.rerun()
elif S == "before_wolvendom":
    story("Journey to Wolvendom", "Would you like to rest before leaving?")
    c1, c2 = st.columns(2)
    if c1.button("Rest: +2 stamina", use_container_width=True): rest(); go("wolvendom"); st.rerun()
    if c2.button("Skip rest", use_container_width=True): go("wolvendom"); st.rerun()

elif S == "wolvendom":
    story("🐺 Wolvendom", "Choose a place to visit.")
    for label, target in [("Cabin", "wolf_cabin"), ("Merchant", "wolf_market"), ("Venture into forest", "baby_wolf")]:
        if st.button(label, use_container_width=True): go(target); st.rerun()
elif S == "wolf_cabin":
    story("Wolvendom Cabin", "Choose the green key for a potion and 2 coins, or orange for a level 3 weapon and 1 coin.")
    c1, c2 = st.columns(2)
    if c1.button("Green key", use_container_width=True): st.session_state.potions += 1; st.session_state.coins += 2; go("baby_wolf"); st.rerun()
    if c2.button("Orange key", use_container_width=True): st.session_state.weapon = max(3, st.session_state.weapon); st.session_state.coins += 1; go("baby_wolf"); st.rerun()
elif S == "wolf_market":
    story("Wolvendom Merchant", "Buy an item, then enter the forest.")
    price = 1 if st.session_state.adventurer == "Mage" else 2
    c1, c2 = st.columns(2)
    if c1.button(f"Level 3 weapon — {price}", use_container_width=True): buy("weapon", 3); st.rerun()
    if c2.button(f"Potion — {price}", use_container_width=True): buy("potion"); st.rerun()
    next_button("baby_wolf", "Enter forest ➡️")
elif S == "baby_wolf":
    story("🐾 Injured Baby Wolf", "A baby wolf needs help. A healing potion can help it.")
    picture("Injured Baby Wolf")
    c1, c2 = st.columns(2)
    if c1.button("Give healing potion", use_container_width=True):
        if st.session_state.potions > 0: st.session_state.potions -= 1; st.session_state.baby_wolf = True; go("name_wolf")
        else: st.session_state.message = "You don't have a healing potion."
        st.rerun()
    if c2.button("Continue without helping", use_container_width=True): go("maha_battle"); st.rerun()
elif S == "name_wolf":
    picture("Baby Wolf")
    name = st.text_input("Name the baby wolf", value=st.session_state.baby_name)
    if st.button("Keep this name", type="primary", use_container_width=True, disabled=not name.strip()):
        st.session_state.baby_name = name.strip(); go("maha_peace"); st.rerun()
elif S == "maha_battle": battle("Maha Bhediya", 3, "wolf_reward")
elif S == "maha_peace":
    story("👑 The Wolf King", f"Maha Bhediya recognises {st.session_state.baby_name} as his child. No fight is needed.")
    picture("Maha Bhediya")
    next_button("wolf_reward")
elif S == "wolf_reward":
    story("Wolvendom Restored", "Maha Bhediya becomes king and gives you Wolf Fur and a map to Ketanmara.")
    if "Wolf Fur" not in st.session_state.items: st.session_state.items.append("Wolf Fur")
    next_button("ketanmara")

elif S == "ketanmara":
    story("🦀 Ketanmara", "Choose where to go.")
    for label, target in [("Village cabin", "crab_cabin"), ("Town merchant", "crab_market"), ("Village centre", "indera")]:
        if st.button(label, use_container_width=True): go(target); st.rerun()
elif S == "crab_cabin":
    story("Ketanmara Cabin", "Choose purple for a potion and 2 coins, or pink for a level 4 weapon and 1 coin.")
    c1, c2 = st.columns(2)
    if c1.button("Purple key", use_container_width=True): st.session_state.potions += 1; st.session_state.coins += 2; go("indera"); st.rerun()
    if c2.button("Pink key", use_container_width=True): st.session_state.weapon = max(4, st.session_state.weapon); st.session_state.coins += 1; go("indera"); st.rerun()
elif S == "crab_market":
    story("Ketanmara Merchant", "Buy an item, then visit the village centre.")
    price = 1 if st.session_state.adventurer == "Mage" else 2
    c1, c2 = st.columns(2)
    if c1.button(f"Level 4 weapon — {price}", use_container_width=True): buy("weapon", 4); st.rerun()
    if c2.button(f"Potion — {price}", use_container_width=True): buy("potion"); st.rerun()
    next_button("indera", "Go to village centre ➡️")
elif S == "indera":
    story("☁️ Indera", "In a crooked old house, Indera tells you about Cengkerang and takes you to the Cloudy Castle.")
    picture("Indera")
    next_button("cengkerang_battle")
elif S == "cengkerang_battle": battle("Cengkerang", 6, "crab_reward")
elif S == "crab_reward":
    story("👑 Ketanmara Restored", "Indera shows compassion. Cengkerang is spared and crowned king. You receive the Crab Shell.")
    if "Crab Shell" not in st.session_state.items: st.session_state.items.append("Crab Shell")
    next_button("ending")

elif S == "ending":
    story("📖 The Ancient Book", "The Snake Fang, Wolf Fur and Crab Shell are stored in your book. The three new kings bid you farewell.")
    for name in ["Snake Fang", "Wolf Fur", "Crab Shell"]: picture(name, 150)
    if st.session_state.baby_wolf:
        st.success(f"{st.session_state.baby_name} stays with you for future adventures!")
    st.balloons()
    if st.button("Play again", type="primary", use_container_width=True): reset(); st.rerun()
elif S == "game_over":
    story("Game Over", st.session_state.message or "Your adventure has ended.")
    if st.button("Try again", type="primary", use_container_width=True): reset(); st.rerun()

# Healing potion is available at every story point, including when the player has none.
if S not in {"choose", "game_over", "ending"} and not st.session_state.battle_done:
    st.divider()
    if st.button("🧪 Drink healing potion", key=f"potion_{S}", use_container_width=True):
        drink_potion(); st.rerun()

st.sidebar.button("Restart adventure", on_click=reset)
