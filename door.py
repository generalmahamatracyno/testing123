from pathlib import Path
import time
import streamlit as st

st.set_page_config(page_title="The Three Kingdoms", page_icon="🏰", layout="centered")
ROOT = Path(".")

PICS = {
    "Mage":"mage.png", "Pirate":"pirate.png", "Priest":"priest.png", "Fairy":"fairy.png",
    "Player":"", "Merchant":"merchant.png", "Elder":"elder.png", "Big Bat":"big_bat.png",
    "Drako":"drako.png", "Hydra":"hydra.png", "Echidna":"echidna.png",
    "Drako Crowned":"drako_crowned.png", "Hydra Jail":"hydra_jail.png",
    "Injured Wolf":"injured_baby_wolf.png", "Baby Wolf":"baby_wolf.png",
    "Wolf Reunion":"maha_recognises_son.png", "Maha Bhediya":"maha_bhediya.png",
    "Indera":"indera.png", "Cengkerang":"cengkerang.png",
    "Snake Fang":"snake_fang.png", "Wolf Fur":"wolf_fur.png", "Crab Shell":"crab_shell.png",
    "Starting Cabin":"starting_cabin.png", "Wolvendom Cabin":"wolvendom_cabin.png",
    "Ketanmara Cabin":"ketanmara_cabin.png", "Starting Forest":"starting_forest.png",
    "Wolvendom Forest":"wolvendom_forest.png", "Ketanmara Forest":"ketanmara_forest.png",
    "Bushes":"bushes.png", "Potion":"healing_potion.png", "Hearts":"hearts.png",
    "Stamina":"stamina.png", "Coins":"coins.png", "Weapon":"weapon.png",
    "Red Key":"red_key.png", "Blue Key":"blue_key.png", "Green Key":"green_key.png",
    "Orange Key":"orange_key.png", "Purple Key":"purple_key.png", "Pink Key":"pink_key.png",
    "Stone Door":"stone_door.png", "Ancient Tavern":"ancient_city_tavern.png",
    "Ketanmara Tavern":"ketanmara_tavern.png", "Rest":"resting_place.png",
    "Work":"working_place.png", "Temple":"abandoned_temple.png", "Cloudy Castle":"cloudy_castle.png",
    "Door 3":"door_3_silhouettes.png", "Door 2":"door_2_silhouettes.png",
    "Door 1":"door_1_silhouette.png", "Door 0":"door_no_silhouettes.png",
    "Door Open":"door_open_light.png",
}

ADVENTURERS = {
    "Mage":"4 stamina; every merchant charges only 1 coin.",
    "Pirate":"Starts with 2 coins.",
    "Priest":"4 hearts; healing potions restore 2 hearts.",
    "Fairy":"6 hearts; cannot use shields.",
}

def initial():
    return {
        "scene":"choose", "adventurer":None, "hearts":5, "max_hearts":5,
        "stamina":5, "coins":0, "weapon":0, "potions":0, "shields":0,
        "message":"", "items":[], "seen":[], "battle_done":False, "battle_damage":0,
        "start_cabin_done":False, "wolf_cabin_done":False, "crab_cabin_done":False,
        "forest_shop_done":False, "ophidia_shop_done":False, "wolf_shop_done":False,
        "crab_shop_done":False, "ancient_tavern_done":False, "crab_tavern_done":False,
        "twin_choice":None, "baby_wolf":False, "baby_name":"", "wolf_warning":False,
        "maha_fought_alone":False, "dialogue_steps":{}, "merchant_messages":{},
        "cengkerang_defeated":False,
    }

def reset():
    for k,v in initial().items(): st.session_state[k] = v.copy() if isinstance(v,list) else v
if "scene" not in st.session_state: reset()

def pic(name, width=290):
    filename = PICS.get(name, "")
    if name == "Player": filename = PICS.get(st.session_state.adventurer, "")
    path = ROOT / filename
    if filename and path.is_file(): st.image(str(path), width=width)
    else: st.caption(f"🖼️ Add image: {filename or 'player image'}")

def say(speaker, text, key, image=None, show_image=True):
    if show_image:
        pic(image or ("Player" if speaker == "You" else speaker), 220)
    st.markdown(f"**{speaker}:**")
    if key in st.session_state.seen:
        st.write(text)
    else:
        def words():
            for word in text.split():
                yield word + " "
                time.sleep(0.045)
        st.write_stream(words())
        st.session_state.seen.append(key)

def dialogue(key, lines, cast=None):
    """Show exactly one spoken line at a time and wait for the player."""
    if cast:
        columns=st.columns(len(cast))
        for column,name in zip(columns,cast):
            with column: pic(name,180)
    step=st.session_state.dialogue_steps.get(key,0)
    if step>=len(lines): return True
    speaker,text,*optional_image=lines[step]
    image=optional_image[0] if optional_image else None
    say(speaker,text,f"{key}_{step}",image,show_image=not bool(cast))
    label="Continue ➡️" if step==len(lines)-1 else "Next dialogue ➡️"
    if st.button(label,key=f"dialogue_{key}_{step}",type="primary",use_container_width=True):
        st.session_state.dialogue_steps[key]=step+1
        st.rerun()
    return False

def go(scene, message=""):
    st.session_state.scene=scene; st.session_state.message=message
    st.session_state.battle_done=False; st.session_state.battle_damage=0

def next_to(scene, label="Next ➡️"):
    if st.button(label, type="primary", use_container_width=True): go(scene); st.rerun()

def check_alive():
    if st.session_state.hearts <= 0: go("game_over", "You ran out of hearts.")

def spend_stamina(n):
    st.session_state.stamina -= n
    if st.session_state.stamina <= 0:
        st.session_state.hearts -= 1; st.session_state.stamina += 2
        st.session_state.message="Stamina reached zero: −1 heart and +2 stamina."
        check_alive()

def heal():
    if st.session_state.potions == 0: st.session_state.message="You don't have a healing potion."
    elif st.session_state.hearts >= st.session_state.max_hearts: st.session_state.message="Your hearts are full. You don't need a healing potion."
    else:
        n=2 if st.session_state.adventurer=="Priest" else 1
        old=st.session_state.hearts
        st.session_state.hearts=min(st.session_state.max_hearts,old+n)
        st.session_state.potions-=1
        st.session_state.message=f"The potion restored {st.session_state.hearts-old} heart(s)."

def choose(name):
    reset(); st.session_state.adventurer=name
    if name=="Mage": st.session_state.stamina=4
    elif name=="Pirate": st.session_state.coins=2
    elif name=="Priest": st.session_state.hearts=4
    elif name=="Fairy": st.session_state.hearts=6; st.session_state.max_hearts=6
    go("intro")

def add_item(name):
    if name not in st.session_state["items"]: st.session_state["items"].append(name)

def use_shield():
    if st.session_state.adventurer=="Fairy": st.session_state.message="The Fairy cannot use shields."
    elif st.session_state.shields==0: st.session_state.message="You don't have a shield."
    elif st.session_state.battle_damage==0: st.session_state.message="No hearts were lost in this fight."
    else:
        st.session_state.shields-=1; st.session_state.battle_damage-=1
        st.session_state.hearts=min(st.session_state.max_hearts,st.session_state.hearts+1)
        st.session_state.message="The shield returned 1 heart lost in battle."

def fight(name, level):
    spend_stamina(1)
    if st.session_state.scene=="game_over": return
    damage=max(0,level-st.session_state.weapon)
    st.session_state.hearts-=damage; st.session_state.battle_damage=damage
    st.session_state.battle_done=True
    st.session_state.message=f"{name} was defeated. You lost {damage} heart(s) and 1 stamina."
    check_alive()

def battle(name, level, destination):
    st.subheader(f"⚔️ {name} — Level {level}"); pic(name)
    if not st.session_state.battle_done:
        st.write(f"Your weapon is level **{st.session_state.weapon}**. You must fight.")
        if st.button("Fight", type="primary", use_container_width=True): fight(name,level); st.rerun()
    else:
        st.success(st.session_state.message)
        a,b=st.columns(2)
        if a.button("Use shield",use_container_width=True): use_shield(); st.rerun()
        if b.button("Drink potion",key="battle_heal",use_container_width=True): heal(); st.rerun()
        next_to(destination)

def shop(done_key, back, weapon_level, normal_price, place):
    st.subheader(place); pic("Merchant")
    price=1 if st.session_state.adventurer=="Mage" else normal_price
    feedback=st.session_state.merchant_messages.get(done_key)
    st.markdown("**Merchant:**")
    st.write(feedback or f"Welcome! Choose one item. Each costs {price} coin{'s' if price!=1 else ''}.")
    a,b,c=st.columns(3); choice=None
    if a.button(f"Weapon L{weapon_level}",use_container_width=True): choice="weapon"
    if b.button("Potion",use_container_width=True): choice="potion"
    if c.button("Shield",use_container_width=True): choice="shield"
    if choice:
        if st.session_state[done_key]:
            st.session_state.merchant_messages[done_key]="Oh, sorry! You already bought something from me."
        elif st.session_state.coins<price:
            st.session_state.merchant_messages[done_key]="Oh, I'm sorry! You don't have enough coins."
        else:
            st.session_state.coins-=price
            if choice=="weapon": st.session_state.weapon=max(st.session_state.weapon,weapon_level)
            elif choice=="potion": st.session_state.potions+=1
            else: st.session_state.shields+=1
            st.session_state[done_key]=True
            st.session_state.merchant_messages[done_key]="Thank you for your purchase!"
        st.rerun()
    next_to(back,"Return outside")

def cabin(place,key1,key2,reward1,reward2,done_key,back):
    st.subheader(place); pic(place)
    if st.session_state[done_key]:
        st.info("You already chose one key and opened its chest."); next_to(back,"Return outside"); return
    st.write("Choose one key. The other chest will remain locked.")
    a,b=st.columns(2)
    with a:
        pic(key1,150)
        if st.button(f"Take {key1}",use_container_width=True): reward1(); st.session_state[done_key]=True; go(back,"Chest opened once."); st.rerun()
    with b:
        pic(key2,150)
        if st.button(f"Take {key2}",use_container_width=True): reward2(); st.session_state[done_key]=True; go(back,"Chest opened once."); st.rerun()
    next_to(back,"Return outside")

def status():
    values=[("Hearts","hearts"),("Stamina","stamina"),("Coins","coins"),("Weapon","weapon"),("Potion","potions")]
    cols=st.columns(5)
    for col,(label,key) in zip(cols,values):
        with col: pic(label,42); st.metric(label,st.session_state[key])
    st.caption(f"{st.session_state.adventurer} · Shields: {st.session_state.shields}")
    if st.session_state["items"]: st.write("**Sacred items:** "+", ".join(st.session_state["items"]))

st.title("🏰 The Three Kingdoms")
S=st.session_state.scene
if S!="choose": status()
if st.session_state.message and not st.session_state.battle_done: st.info(st.session_state.message)

if S=="choose":
    st.subheader("Choose Your Adventurer"); cols=st.columns(2)
    for i,(name,ability) in enumerate(ADVENTURERS.items()):
        with cols[i%2]:
            pic(name,180); st.markdown(f"**{name}**"); st.caption(ability)
            if st.button(f"Choose {name}",key=name,use_container_width=True): choose(name); st.rerun()
elif S=="intro":
    if dialogue("intro",[("You","Oh my gosh... where am I? How did I get here? I need to find a way back home.")]):
        next_to("start_hub")
elif S=="start_hub":
    st.subheader("The Wilderness")
    a,b=st.columns(2)
    if a.button("Visit cabin",use_container_width=True): go("start_cabin"); st.rerun()
    if b.button("Enter forest",use_container_width=True): go("start_forest"); st.rerun()
elif S=="start_cabin":
    cabin("Starting Cabin","Red Key","Blue Key",
           lambda:(setattr(st.session_state,"potions",st.session_state.potions+1),setattr(st.session_state,"coins",st.session_state.coins+2)),
           lambda:(setattr(st.session_state,"weapon",max(1,st.session_state.weapon)),setattr(st.session_state,"coins",st.session_state.coins+1)),
           "start_cabin_done","start_hub")
elif S=="start_forest":
    st.subheader("Starting Forest"); pic("Starting Forest")
    a,b=st.columns(2)
    if a.button("Visit merchant",use_container_width=True): go("start_shop"); st.rerun()
    if b.button("Approach stone door",use_container_width=True): go("stone_door"); st.rerun()
    next_to("start_hub","Return outside")
elif S=="start_shop": shop("forest_shop_done","start_forest",1,2,"Forest Merchant")
elif S=="stone_door":
    st.subheader("Stone Door"); pic("Stone Door"); st.write("Opening it costs 2 stamina.")
    if st.button("Open door",use_container_width=True):
        spend_stamina(2)
        if st.session_state.scene != "game_over": go("caves")
        st.rerun()
    next_to("start_forest","Return to forest")
elif S=="caves":
    st.subheader("Beyond the Door"); a,b=st.columns(2)
    if a.button("Cave with light",use_container_width=True): go("bat"); st.rerun()
    if b.button("Dark cave",use_container_width=True): go("ancient_city"); st.rerun()
elif S=="bat": battle("Big Bat",1,"ancient_city")
elif S=="ancient_city":
    st.subheader("Ancient City"); a,b=st.columns(2)
    if a.button("Tavern",use_container_width=True): go("ancient_tavern"); st.rerun()
    if b.button("Village elder",use_container_width=True): go("elder"); st.rerun()
elif S=="ancient_tavern":
    st.subheader("Ancient City Tavern"); pic("Ancient Tavern")
    if st.session_state.ancient_tavern_done: st.info("You already chose work or rest here.")
    else:
        a,b=st.columns(2)
        with a:
            pic("Work",150)
            if st.button("Work: −1 stamina, +2 coins",use_container_width=True): spend_stamina(1); st.session_state.coins+=2; st.session_state.ancient_tavern_done=True; go("ancient_city"); st.rerun()
        with b:
            pic("Rest",150)
            if st.button("Rest: +2 stamina",use_container_width=True): st.session_state.stamina+=2; st.session_state.ancient_tavern_done=True; go("ancient_city"); st.rerun()
    next_to("ancient_city","Return outside")
elif S=="elder":
    if dialogue("elder",[
        ("You","Do you know how I can return home?"),
        ("Elder","Travel to Ophidia and ask the people there. Take this map."),
    ]): next_to("ophidia")

elif S=="ophidia":
    st.subheader("Ophidia")

    dungeon_label = (
        f"Dungeon — {st.session_state.twin_choice} already chosen"
        if st.session_state.twin_choice
        else "Dungeon"
    )

    if st.button(
        dungeon_label,
        use_container_width=True,
        disabled=st.session_state.twin_choice is not None
    ):
        go("dungeon")
        st.rerun()

    if st.button("Merchant", use_container_width=True):
        go("ophidia_shop")
        st.rerun()

    if st.button("Abandoned temple", use_container_width=True):
        go("temple")
        st.rerun()
elif S=="ophidia_shop": shop("ophidia_shop_done","ophidia",2,3,"Ophidia Merchant")
elif S=="dungeon":
    st.subheader("Ophidia Dungeon")
        if st.session_state.twin_choice is not None:
        st.info(
            f"You already chose {st.session_state.twin_choice}. "
            "You cannot choose another companion."
        )
        next_to("ophidia", "Return outside")
        st.stop()
    next_to("ophidia","Return outside")
elif S=="echidna": battle("Echidna",2,"choose_ruler")
elif S=="choose_ruler":
    if dialogue("choose_ruler",[
        ("Drako","The battle is over. Which of us do you choose to lead Ophidia?"),
        ("Hydra","Choose carefully. Which of us do you choose?"),
    ],cast=["Drako","Hydra"]):
        a,b=st.columns(2)
        if a.button("Crown Drako",use_container_width=True): add_item("Snake Fang"); go("drako_reward"); st.rerun()
        if b.button("Crown Hydra",use_container_width=True): st.session_state.hearts-=1; check_alive(); add_item("Snake Fang"); go("hydra_jail"); st.rerun()
elif S=="hydra_jail":
    if dialogue("hydra_jail",[
        ("Hydra","You chose poorly. Both of you will remain here while I take the throne."),
        ("Drako","We will escape together. Ophidia cannot be left to her rule."),
    ],cast=["Hydra Jail"]): next_to("drako_reward")
elif S=="drako_reward":
    st.subheader("King Drako's Gift")
    if dialogue("drako_reward",[
        ("You","How can I return to my home?"),
        ("Drako","Take this Snake Fang and map to Wolvendom. Someone there may know the way."),
    ],cast=["Drako Crowned","Snake Fang"]): next_to("before_wolvendom")
elif S=="before_wolvendom":
    st.subheader("Journey to Wolvendom"); a,b=st.columns(2)
    if a.button("Rest: +2 stamina",use_container_width=True): st.session_state.stamina+=2; go("wolvendom"); st.rerun()
    if b.button("Leave now",use_container_width=True): go("wolvendom"); st.rerun()

elif S=="wolvendom":
    st.subheader("Wolvendom")
    for label,target in [("Cabin","wolf_cabin"),("Merchant","wolf_shop"),("Venture into forest","wolf_forest")]:
        if st.button(label,use_container_width=True): go(target); st.rerun()
elif S=="wolf_cabin":
    cabin("Wolvendom Cabin","Green Key","Orange Key",
           lambda:(setattr(st.session_state,"potions",st.session_state.potions+1),setattr(st.session_state,"coins",st.session_state.coins+2)),
           lambda:(setattr(st.session_state,"weapon",max(3,st.session_state.weapon)),setattr(st.session_state,"coins",st.session_state.coins+1)),
           "wolf_cabin_done","wolvendom")
elif S=="wolf_shop": shop("wolf_shop_done","wolvendom",3,2,"Wolvendom Merchant")
elif S=="wolf_forest":
    st.subheader("Wolvendom Forest"); pic("Wolvendom Forest"); pic("Bushes",220)
    a,b=st.columns(2)
    if a.button("Search bushes",use_container_width=True): go("injured_wolf"); st.rerun()
    if b.button("Keep going",use_container_width=True): go("wolf_reunion" if st.session_state.baby_wolf else "maha_alone"); st.rerun()
    next_to("wolvendom","Return outside")
elif S=="injured_wolf":
    st.subheader("The Hidden Wolf")
    if dialogue("injured_wolf",[("Baby Wolf","Please... can you help me?","Injured Wolf")]):
        if st.session_state.baby_wolf: st.success("The wolf has already been rescued."); next_to("wolf_forest","Return")
        elif st.session_state.potions>0:
            if st.button("Use healing potion",use_container_width=True): st.session_state.potions-=1; st.session_state.baby_wolf=True; go("name_wolf"); st.rerun()
            next_to("wolf_forest","Leave")
        else:
            st.warning("You have no potion. If you proceed, helping the wolf will cost exactly 1 heart.")
            a,b=st.columns(2)
            if a.button("Proceed",use_container_width=True): st.session_state.wolf_warning=True; st.session_state.hearts-=1; check_alive(); st.session_state.baby_wolf=True; go("name_wolf"); st.rerun()
            if b.button("Leave",use_container_width=True): go("wolf_forest"); st.rerun()
elif S=="name_wolf":
    pic("Baby Wolf"); name=st.text_input("Name the baby wolf",value=st.session_state.baby_name)
    if st.button("Confirm name",disabled=not name.strip(),use_container_width=True):
        st.session_state.baby_name=name.strip()
        go("wolf_reward" if st.session_state.maha_fought_alone else "wolf_forest")
        st.rerun()
elif S=="maha_alone":
    battle("Maha Bhediya",3,"missed_wolf")
elif S=="missed_wolf":
    st.session_state.maha_fought_alone=True
    st.info("Maha Bhediya has been defeated, but Wolvendom still has no ruler. You sense that you missed someone near the forest entrance. Search the bushes.")
    next_to("wolf_forest","Return to forest")
elif S=="wolf_reunion":
    st.subheader("A Family Reunited")
    if dialogue("wolf_reunion",[
        (st.session_state.baby_name or "Baby Wolf","Father, stop! This adventurer saved me. There is no need to fight.","Baby Wolf"),
        ("Maha Bhediya","Then Wolvendom's future belongs to you. I will step aside."),
    ]): next_to("wolf_reward")
elif S=="wolf_reward":
    st.subheader("Wolvendom's New King"); add_item("Wolf Fur")
    if dialogue("wolf_reward",[
        ("You","Do you know how I can return home?"),
        (st.session_state.baby_name or "Wolf King","Take this Wolf Fur and map to Ketanmara. Ask someone there for help.","Baby Wolf"),
    ],cast=["Baby Wolf","Wolf Fur"]): next_to("ketanmara")

elif S=="ketanmara":
    st.subheader("Ketanmara"); a,b=st.columns(2)
    if a.button("Village",use_container_width=True): go("crab_village"); st.rerun()
    if b.button("Town centre",use_container_width=True): go("crab_town"); st.rerun()
elif S=="crab_village":
    for label,target in [("Cabin","crab_cabin"),("Merchant","crab_shop"),("Forest","crab_forest")]:
        if st.button(label,use_container_width=True): go(target); st.rerun()
    next_to("ketanmara","Return outside")
elif S=="crab_cabin":
    cabin("Ketanmara Cabin","Purple Key","Pink Key",
           lambda:(setattr(st.session_state,"potions",st.session_state.potions+1),setattr(st.session_state,"coins",st.session_state.coins+2)),
           lambda:(setattr(st.session_state,"weapon",max(4,st.session_state.weapon)),setattr(st.session_state,"coins",st.session_state.coins+1)),
           "crab_cabin_done","crab_village")
elif S=="crab_shop": shop("crab_shop_done","crab_village",4,2,"Ketanmara Merchant")
elif S=="crab_forest":
    st.subheader("Ketanmara Forest"); pic("Ketanmara Forest")
    st.write("A dangerous path continues deep into the forest.")
    next_to("cengkerang_forest","Continue through forest")
    next_to("crab_village","Return outside")
elif S=="cengkerang_forest": battle("Cengkerang",6,"forest_battle_hint")
elif S=="forest_battle_hint":
    st.session_state.cengkerang_defeated=True
    st.success("Cengkerang is defeated. Clues on the path suggest that someone in Ketanmara's Town Centre knows what must happen next.")
    next_to("crab_town","Investigate the Town Centre")
elif S=="crab_town":
    st.subheader("Town Centre")
    for label,target in [("Crooked old house","indera"),("Merchant","crab_town_shop"),("Tavern","crab_tavern")]:
        if st.button(label,use_container_width=True): go(target); st.rerun()
    next_to("ketanmara","Return outside")
elif S=="crab_town_shop": shop("crab_shop_done","crab_town",4,2,"Town Merchant")
elif S=="crab_tavern":
    st.subheader("Ketanmara Tavern"); pic("Ketanmara Tavern")
    if st.session_state.crab_tavern_done: st.info("You already worked or rested here.")
    else:
        a,b=st.columns(2)
        with a:
            pic("Work",150)
            if st.button("Work",use_container_width=True): spend_stamina(1); st.session_state.coins+=2; st.session_state.crab_tavern_done=True; go("crab_town"); st.rerun()
        with b:
            pic("Rest",150)
            if st.button("Rest",use_container_width=True): st.session_state.stamina+=2; st.session_state.crab_tavern_done=True; go("crab_town"); st.rerun()
    next_to("crab_town","Return outside")
elif S=="indera":
    indera_reply=("You found Cengkerang without me. Now we must decide Ketanmara's future."
                  if st.session_state.cengkerang_defeated
                  else "First, Cengkerang must be stopped. Come with me to the Cloudy Castle.")
    if dialogue("indera",[
        ("You","Are you Indera? I was told someone here might know how I can return home."),
        ("Indera",indera_reply),
    ]): next_to("indera_cengkerang" if st.session_state.cengkerang_defeated else "cloudy_castle")
elif S=="cloudy_castle": st.subheader("Cloudy Castle"); pic("Cloudy Castle"); next_to("cengkerang")
elif S=="cengkerang": battle("Cengkerang",6,"indera_cengkerang")
elif S=="indera_cengkerang":
    st.session_state.cengkerang_defeated=True
    if dialogue("indera_cengkerang",[
        ("Indera","The battle is over, Cengkerang. Ketanmara needs peace, not more destruction."),
        ("Cengkerang","Then take the Crab Shell. Let it open the way you seek."),
    ]): next_to("indera_reward")
elif S=="indera_reward":
    st.subheader("King Indera's Gift"); add_item("Crab Shell")
    if dialogue("indera_reward",[
        ("You","How do I finally return home?"),
        ("Indera","Return to the Ancient City. Place the fang, fur and shell into its holy door."),
    ],cast=["Indera","Crab Shell"]): next_to("holy_door_3")

elif S=="holy_door_3": st.subheader("The Holy Door"); pic("Door 3"); st.write("Three empty silhouettes wait."); next_to("holy_door_2","Place Snake Fang")
elif S=="holy_door_2": pic("Door 2"); st.write("The Snake Fang fits. Two silhouettes remain."); next_to("holy_door_1","Place Wolf Fur")
elif S=="holy_door_1": pic("Door 1"); st.write("The Wolf Fur fits. One silhouette remains."); next_to("holy_door_0","Place Crab Shell")
elif S=="holy_door_0": pic("Door 0"); st.write("All three sacred items are in place."); next_to("farewell")
elif S=="farewell":
    if dialogue("farewell",[
        ("Drako","Remember Ophidia—and remember the courage that brought you this far."),
        (st.session_state.baby_name or "Wolf King","Remember Wolvendom. I will never forget that you found me.","Baby Wolf"),
        ("Indera","Remember Ketanmara. The door is ready; it is time for you to go home."),
    ]): next_to("door_open")
elif S=="door_open":
    st.subheader("The Way Home")
    if dialogue("door_open",[("You","I will remember all of you. Farewell.")],cast=["Door Open"]):
        next_to("ending","Enter the light")
elif S=="ending":
    st.success("You pass through the holy door and return safely to your world."); st.balloons()
    if st.button("Play again",use_container_width=True): reset(); st.rerun()
elif S=="game_over":
    st.error(st.session_state.message or "Your adventure has ended.")
    if st.button("Try again",use_container_width=True): reset(); st.rerun()

if S not in {"choose","ending","game_over"} and not st.session_state.battle_done:
    st.divider()
    if st.button("🧪 Drink healing potion",key=f"heal_{S}",use_container_width=True): heal(); st.rerun()
st.sidebar.button("Restart adventure",on_click=reset)
