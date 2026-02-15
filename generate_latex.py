#!/usr/bin/env python3
"""
Helix Native Factory Preset LaTeX Document Generator
Parses multiple .hls setlist files and generates a combined LaTeX reference.
"""

import json, base64, zlib, re, sys, os
import importlib.util

spec = importlib.util.spec_from_file_location('helix_parser', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'helix_parser.py'))
_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_mod)
MODEL_DB = _mod.MODEL_DB

# ═══════════════════════════════════════════════════════════════
# PRESET DECODER: preset_name -> (decoded_name, description)
# ═══════════════════════════════════════════════════════════════

PRESET_INFO = {
    # ══════════════════════ FACTORY 1 ══════════════════════
    # 0-31: Amp Showcase
    "US Double Nrm": ("Fender Twin Reverb (Normal Channel)", "Amp showcase featuring the legendary Fender Twin Reverb's normal channel, prized for its sparkling clean headroom and lush spring reverb. A versatile studio and stage workhorse since the 1960s."),
    "Essex A30": ("Vox AC-30 Top Boost", "Amp showcase for the Vox AC-30 with top boost circuit, delivering the chimey, jangly British tone that defined the British Invasion and remains a staple of indie and alternative rock."),
    "Brit Plexi Brt": ("Marshall Super Lead 100 (Bright)", "Amp showcase for the Marshall Super Lead 100 bright channel---the quintessential rock amplifier that launched a thousand arena tours."),
    "Cali Rectifire": ("MESA/Boogie Dual Rectifier", "Amp showcase for the MESA/Boogie Dual Rectifier, the defining high-gain amp of 1990s and 2000s heavy rock, known for its thick, saturated crunch."),
    "US Deluxe Nrm": ("Fender Deluxe Reverb (Normal)", "Amp showcase for the Fender Deluxe Reverb normal channel---a recording studio workhorse prized for warm, touch-responsive cleans."),
    "A30 Fawn Nrm": ("Vox AC-30 Fawn (Normal)", "Amp showcase for the early Vox AC-30 Fawn normal channel, the warmer-voiced predecessor to the Top Boost, favored for rounder, organic overdrive."),
    "Revv Gen Purple": ("Revv Generator 120 (Purple/Ch3)", "Amp showcase for the Revv Generator 120's purple channel (Ch3), a modern high-gain design with tight, focused distortion popular in progressive metal."),
    "Revv Gen Red": ("Revv Generator 120 (Red/Ch4)", "Amp showcase for the Revv Generator 120's red channel (Ch4), the highest-gain setting with saturated harmonics and exceptional note clarity."),
    "Archetype Clean": ("PRS Archon (Clean)", "Amp showcase for the PRS Archon's clean channel, providing crystal-clear, full-bodied cleans with excellent headroom."),
    "Matchstick Ch1": ("Matchless DC-30 (Ch1)", "Amp showcase for the Matchless DC-30 channel 1, a boutique EL84 amp celebrated for lush, three-dimensional cleans and rich overdrive."),
    "Das Benzin Mega": ("Diezel VH4 (Mega Channel)", "Amp showcase for the Diezel VH4's mega channel---a modern high-gain powerhouse favored in progressive metal."),
    "Archetype Lead": ("PRS Archon (Lead)", "Amp showcase for the PRS Archon's lead channel, delivering tight, articulate high-gain tone with smooth sustain."),
    "Jazz Rivet 120": ("Roland JC-120 Jazz Chorus", "Amp showcase for the Roland JC-120, the definitive solid-state clean amp famous for its stereo chorus and ultra-clean headroom."),
    "Grammatico GSG": ("Grammatico GSG100", "Amp showcase for the Grammatico GSG100, a boutique American-voiced amp with rich harmonic complexity and exceptional touch sensitivity."),
    "Line 6 Elmsley": ("Line 6 Original (Elmsley)", "Amp showcase for Line 6's Elmsley, an original amp design exclusive to the Helix platform."),
    "Moo)))n Jump": ("Sunn Model T (Jumped Channels)", "Amp showcase for the Sunn Model T with jumped channels---a doom and stoner rock staple. The name references Sunn O)))."),
    "US Princess": ("Fender Princeton Reverb", "Amp showcase for the Fender Princeton Reverb, a small-combo classic beloved for its sweet breakup and onboard reverb/tremolo."),
    "GrammaticoLG Nrm": ("Grammatico LaGrange (Normal)", "Amp showcase for the Grammatico LaGrange normal channel, a boutique Tweed-inspired design with refined voicing."),
    "Placater Dirty": ("Friedman BE-100 (BE/HBE)", "Amp showcase for the Friedman BE-100's dirty channel---a hot-rodded, Marshall-derived design by Dave Friedman."),
    "PV Panama": ("Peavey 5150", "Amp showcase for the Peavey 5150, Eddie Van Halen's signature amp. The name nods to Van Halen's track `Panama.'"),
    "Cali Texas Ch 1": ("MESA/Boogie Lone Star (Clean)", "Amp showcase for the MESA/Boogie Lone Star clean channel, delivering lush, warm cleans with Fender-influenced character."),
    "Line 6 Ventoux": ("Line 6 Original (Ventoux)", "Amp showcase for Line 6's Ventoux, an original Helix-exclusive amp design."),
    "Derailed Ingrid": ("Trainwreck Express", "Amp showcase for the Trainwreck Express, a legendary hand-wired amp by Ken Fischer known for explosive dynamics and vocal-like midrange."),
    "PV Vitriol Lead": ("Peavey Invective (Lead)", "Amp showcase for the Peavey Invective lead channel, Misha Mansoor's signature amp for ultra-tight progressive metal tone."),
    "Cali IV Rhythm 1": ("MESA/Boogie Mark IV (R1)", "Amp showcase for the MESA/Boogie Mark IV rhythm 1 channel, versatile from pristine cleans to crushing leads."),
    "Line 6 Litigator": ("Line 6 Original (Litigator)", "Amp showcase for Line 6's Litigator, often described as a refined blackface-style pedal-platform amp."),
    "Cartographer": ("Ben Adrian Cartographer", "Amp showcase for the Ben Adrian Cartographer, a boutique design created in collaboration with Line 6."),
    "Mandarin Rocker": ("Orange Rockerverb 100 MkIII", "Amp showcase for the Orange Rockerverb 100 MkIII, with the brand's signature thick, compressed midrange."),
    "Mail Order Twin": ("Silvertone 1484", "Amp showcase for the Silvertone 1484, a 1960s `department store' amp now a cult classic for raw, gritty overdrive."),
    "Tweed Blues Brt": ("Fender Bassman (Bright)", "Amp showcase for the Fender Bassman bright channel---ancestor of both the Marshall and MESA/Boogie lineages."),
    "German Mahadeva": ("Bogner Shiva", "Amp showcase for the Bogner Shiva, bridging clean headroom and lush, harmonically rich overdrive."),
    "Line 6 Badonk": ("Line 6 Original (Badonk)", "Amp showcase for Line 6's Badonk, a Helix-exclusive high-gain original design."),
    # 32: DI
    "DI": ("Direct Input (No Amp)", "A direct-input preset with no amp or cab---useful as a template or for reamping."),
    # 33-42: Bass
    "BAS:SVT-4 Pro": ("Ampeg SVT-4 PRO", "Bass amp showcase for the Ampeg SVT-4 PRO, the industry-standard bass amp."),
    "BAS:Cali Bass": ("MESA/Boogie M9 Carbine", "Bass amp showcase for the MESA/Boogie M9 Carbine, a modern, punchy bass tone."),
    "BAS:Agua 51": ("Aguilar DB 751", "Bass amp showcase for the Aguilar DB 751, prized for warm, round tone."),
    "BAS:Cougar 800": ("Gallien-Krueger 800RB", "Bass amp showcase for the GK 800RB, known for aggressive, cutting midrange."),
    "BAS:SVT Nrm": ("Ampeg SVT (Normal)", "Bass amp showcase for the classic all-tube Ampeg SVT normal channel."),
    "BAS:Cali 400 Ch1": ("MESA/Boogie Bass 400+ (Ch1)", "Bass amp showcase for the all-tube MESA/Boogie Bass 400+."),
    "BAS:Agua Sledge": ("Aguilar Tone Hammer", "Bass amp showcase for the Aguilar Tone Hammer with AGS drive circuit."),
    "BAS:Del Sol 300": ("Sunn Coliseum 300", "Bass amp showcase for the Sunn Coliseum 300, a 1970s solid-state powerhouse."),
    "BAS:Woody Blue": ("Acoustic 360", "Bass amp showcase for the Acoustic 360, Jaco Pastorius's legendary bass amp."),
    "BAS:Hire Me!": ("Bass Audition Tone", "A polished, mix-ready bass tone---the kind of sound you'd bring to a session audition."),
    # 43-65: Song/Artist-Inspired
    "Justice Fo Y'all": ("...And Justice for All (Metallica)", "Inspired by Metallica's scooped, aggressive rhythm tone with heavily scooped mids for sharp, biting attack."),
    "Stone Cold Loco": ("Stone Cold Crazy (Queen) / Locomotive (GN'R)", "Driving hard rock tone evoking classic British hard rock energy with a cranked high-gain amp."),
    "Plush Garden": ("Plush (Stone Temple Pilots)", "Inspired by STP's grunge-era midrange crunch with warm medium-gain and lush modulation."),
    "Cowboys from DFW": ("Cowboys from Hell (Pantera)", "Inspired by Pantera's crushing tone, capturing Dimebag Darrell's razor-edged sound."),
    "G.O.A.T. Rodeo": ("Greatest of All Time---Rodeo Rock", "Dynamic country-rock/Southern rock preset with clean-to-crunch and twang."),
    "GRAMMATICO JNC": ("Grammatico Amp Collaboration (JNC)", "Artist collaboration showcasing the Grammatico amp's warmth and dynamic response."),
    "SCREAMS JNC": ("High-Gain Lead (JNC Collaboration)", "High-gain lead from the JNC series, designed for searing lead work."),
    "BIG DUBB": ("Dub/Reggae Inspired", "Deep, dubby tone with warm bass-heavy settings, spacious delay, and reverb."),
    "BIG VENUE DRIVE": ("Large-Venue Driven Tone", "Commanding driven tone designed for large spaces with clarity and projection."),
    "BUBBLE NEST": ("Ambient/Textural Clean", "Atmospheric clean with layered modulation and reverb for ambient playing."),
    "DUSTED": ("Gritty Vintage Overdrive", "Raw, broken-up tone with dusty vintage quality---a well-worn tube amp at its breakup point."),
    "SUNRISE DRIVE": ("Warm Overdrive", "Warm, musical overdrive suited for melodic playing with dynamic responsiveness."),
    "GLISTEN": ("Shimmering Clean", "Pristine clean with chorus, delay, and reverb for a crystalline, glistening palette."),
    "WATERS IN HELL": ("Pink Floyd---Dark Atmospheric", "Inspired by Pink Floyd's brooding soundscapes with warm amp, spacious delay, and modulation."),
    "FAUX 7 STG CHUG": ("Faux 7-String Chug", "Simulates 7-string low-end on a 6-string using pitch shifting and tight high-gain processing."),
    "RICHEESE": ("Rich, Cheesy 1980s Lead", "Saturated lead with 1980s arena rock flair---lush sustain and dramatic character."),
    "RC REINCARNATION": ("RC (Artist) Reincarnation", "Artist collaboration blending vintage amp character with modern effects."),
    "RIFFS AND BEARDS": ("Stoner/Desert Rock Riffing", "Thick, fuzzy riff tone for stoner and desert rock---heavy, detuned, saturated."),
    "FELIX MARK IV": ("Felix---MESA/Boogie Mark IV", "Artist collaboration with the Mark IV for versatile rock playing."),
    "FELIX JAZZ 120": ("Felix---Roland JC-120 Clean", "Artist collaboration for jazz and clean melodic playing."),
    "FELIX DELUXE MOD": ("Felix---Fender Deluxe w/ Modulation", "Artist collaboration pairing the Deluxe Reverb with swirling modulation."),
    "FELIX ENGL": ("Felix---ENGL High-Gain", "Artist collaboration using the ENGL Fireball for modern rock and metal."),
    "SPOTLIGHTS": ("Spotlights (Atmospheric/Post-Rock)", "Atmospheric, cinematic tone for post-rock with layered delays and reverb."),
    # 66-107: Artist Signature
    "BUMBLE ACOUSTIC": ("Ron `Bumblefoot' Thal---Acoustic Sim", "Bumblefoot's (ex-GN'R) signature acoustic simulation from an electric guitar."),
    "BMBLFOOT PRINCE": ("Bumblefoot---Princeton Tone", "Bumblefoot's signature Fender Princeton preset with warm, vintage American character."),
    "SHEEHAN PEARCE": ("Billy Sheehan---Pearce BC-1 Bass", "Billy Sheehan's signature Pearce BC-1 bass tone with aggressive harmonics."),
    "SHEEHAN SVT4PRO": ("Billy Sheehan---Ampeg SVT-4 PRO", "Billy Sheehan's Ampeg SVT-4 PRO signature preset for thunderous bass."),
    "THE BLUE AGAVE": ("Blue Agave (Aguilar Bass)", "Smooth, refined Aguilar-based bass tone with warm low-end and note clarity."),
    "BULB RHYTHM": ("Misha `Bulb' Mansoor (Periphery)---Rhythm", "Mansoor's progressive metal rhythm: ultra-tight, scooped, precise for polyrhythmic riffing."),
    "BULB LEAD": ("Misha Mansoor---Lead", "Mansoor's lead with boosted mids and smooth sustain for soaring melodic lines."),
    "BULB CLEAN": ("Misha Mansoor---Clean", "Mansoor's pristine clean with subtle modulation for atmospheric interludes."),
    "BULB AMBIENT": ("Misha Mansoor---Ambient", "Mansoor's ambient preset with expansive delay, reverb, and modulation."),
    "EMPTY GARBAGE": ("Garbage (Band)---Clean", "Inspired by Garbage's electronic-influenced clean guitar processing."),
    "ONLY GARBAGE": ("Garbage (Band)---Distorted", "Inspired by Garbage's aggressive, industrial-tinged alternative distortion."),
    "GARBAGE BASS": ("Garbage (Band)---Bass", "Inspired by Garbage's processed, slightly gritty bass sound."),
    "BILLY KASTODON": ("Bill Kelliher (Mastodon)---Rhythm", "Kelliher's signature thick, progressive sludge-metal tone."),
    "THIS IS THE END": ("The End (Dramatic High-Gain)", "Dramatic, apocalyptic high-gain tone, possibly referencing The Doors."),
    "DJENT LA FUENTE": ("Djent (La Fuente)", "Tight, percussive djent tone with high gain and aggressive gating."),
    "JONBUTTON UZAPIK": ("Jon Button---Signature", "Artist signature preset with distinctive effects routing."),
    "TrevLukatherSolo": ("Trev Lukather---Solo Lead", "Signature lead for expressive solo work with smooth sustain."),
    "HOWE WILDEST": ("Greg Howe---Wild Lead", "Fusion virtuoso Greg Howe's aggressive, dynamic lead tone."),
    "No:Thing": ("No:Thing (Experimental)", "Experimental preset for avant-garde and atmospheric playing."),
    "PETE THORN DUO": ("Pete Thorn---Dual Amp", "Session guitarist Pete Thorn's dual-amp blend for rich, complex tone."),
    "RHETT'S ALLROUND": ("Rhett Shull---All-Around", "Rhett Shull's versatile preset for blues, rock, and country."),
    "A DEADLY RHYTHM": ("Deadly Precision Rhythm", "Tight, precise rhythm tone with excellent note separation."),
    "JEFF SCHROEDER 1": ("Jeff Schroeder (Smashing Pumpkins)---1", "Schroeder's layered, effects-heavy alternative rock sound."),
    "JEFF SCHROEDER 2": ("Jeff Schroeder (Smashing Pumpkins)---2", "Schroeder's contrasting tonal palette for different song sections."),
    "GRACOXONBUM": ("Graham Coxon (Blur)---Fuzzy", "Inspired by Coxon's raw, fuzzy tone with lo-fi distortion and British amp character."),
    "Buck Mild": ("Peter Buck (R.E.M.)---Jangly Clean", "Inspired by Peter Buck's signature jangly, arpeggiated style with bright, chiming cleans."),
    "LEWIE ALLEN BLUE": ("Lewis Allen---Blues", "Signature blues tone with warm, dynamic tube amp response and musical breakup."),
    "RABEAAFRO LEAD": ("Rabea Massaad---Lead", "Rabea's high-gain lead with smooth sustain and melodic clarity."),
    "RABEAAFRO CHUGGS": ("Rabea Massaad---Chug/Rhythm", "Rabea's tight, percussive chugging rhythm preset."),
    "RABEA AMBIENT": ("Rabea Massaad---Ambient Clean", "Rabea's atmospheric clean with lush reverb and delay."),
    "RABEA AMBI LEAD": ("Rabea Massaad---Ambient Lead", "Rabea's ambient lead combining sustain with spacious delay and reverb."),
    "GUILTY PLEASURES": ("1980s Arena Rock", "Unabashedly 1980s: high gain, lush chorus, dramatic delay."),
    "DEVIN TOWNSEND": ("Devin Townsend---Wall of Sound", "Townsend's signature massive, layered, heavily processed wall-of-sound."),
    "NN BUBBLES": ("Artist NN---Bubbly Textures", "Bubbly, percolating textures from creative effects routing."),
    "SHONN'S SHOTGUN": ("Shonn---Aggressive", "Aggressive, punchy signature tone with tight dynamics."),
    "InSTANtgH0St/24": ("Instant Ghost---Atmospheric", "Ghostly atmospheric preset with eerie, spectral textures."),
    "OveRTONeGHoSt 3": ("Overtone Ghost 3---Harmonic", "Experimental overtone manipulation and ghostly harmonic textures."),
    "PaddingToNe": ("Padding Tone---Synth-Like Pads", "Guitar transformed into sustained, synth-like pad textures."),
    "MJA + PANCAKE": ("MJA (Artist) + Pancake", "Artist collaboration with distinctive amp/effects configuration."),
    "PHILIP BYTONE": ("Philip---Bi-Tone/Dual", "Dual-tone configuration blending two contrasting amp voices."),
    "REUTER LEAD": ("Reuter---Lead", "Artist signature lead optimized for expressive dynamics."),
    "R U SERIOUS?": ("Over-the-Top Tone", "Tongue-in-cheek preset with extreme or surprising tonal choices."),
    # 108-119: Genre/Creative
    "Parallel Muffs": ("Parallel Big Muff Fuzz", "Multiple Big Muff voices in parallel for massive, harmonically complex fuzz."),
    "Big County": ("Big Country---Signature Sound", "Inspired by Big Country's bagpipe-mimicking guitar using harmonizer and delay."),
    "Mockabilly": ("Mock Rockabilly", "Playful rockabilly with slapback delay and twangy character."),
    "Stranger Synth": ("Stranger Things---Style Synth", "Retro-futuristic synth tones inspired by the Stranger Things score."),
    "You Shall Pass": ("Epic/Cinematic Tone", "Epic, cinematic tone evoking grandeur with octave effects and reverb."),
    "GlitchVerb": ("Glitch Reverb---Experimental", "Glitch-style delay artifacts combined with reverb for fragmented textures."),
    "But Does It Doom": ("Doom Metal Test", "Tongue-in-cheek doom preset: massive fuzz, crushing low-end."),
    "Mayer'ish JS": ("John Mayer---Inspired Blues", "Inspired by John Mayer's blues tone with dynamic clean-to-crunch and spring reverb."),
    "Robben'ish JS": ("Robben Ford---Inspired Blues", "Inspired by Robben Ford's jazz-blues tone with vocal-like sustain."),
    "X Ray": ("Transparent Tone", "Highly transparent tone letting the guitar's natural character shine through."),
    "Big Monosynth": ("Monophonic Synth", "Guitar-to-monosynth using tracking effects for fat, analog-style synth sounds."),
    "ISS Flyby": ("Space Station Flyby---Ambient", "Spacey ambient preset with pitch shifting, delay, and reverb."),
    # 120-127: SFX
    "SFX:Dr. Strange": ("SFX---Psychedelic/Mystic", "Psychedelic sound effects with pitch shifting and swirling modulation."),
    "SFX:EXP Disturb": ("SFX---Expression Disturbance", "Expression pedal controls dramatic, unsettling sonic transformations."),
    "SFX:Hokulani": ("SFX---Celestial/Hawaiian", "Celestial shimmer reverb and modulation for ethereal atmosphere."),
    "SFX:Pulse Drone": ("SFX---Pulsing Drone", "Rhythmic pulsing drone textures for meditative soundscapes."),
    "SFX:Rezz Score": ("SFX---Film Score Texture", "Dark, cinematic tension-building textures."),
    "SFX:Slot Machine": ("SFX---Random/Chaotic", "Chaotic, unpredictable sonic elements."),
    "SFX:Trip City": ("SFX---Psychedelic Trip", "Extreme modulation, pitch effects, and delay for mind-bending textures."),
    "SFX:Ufology": ("SFX---UFO/Alien Sounds", "Ring modulation and pitch shifting for extraterrestrial textures."),

    # ══════════════════════ FACTORY 2 ══════════════════════
    "Bentique": ("Boutique Amp Tone", "A refined, boutique amplifier tone emphasizing touch sensitivity and harmonic richness---the kind of tone associated with hand-wired, small-batch amplifiers."),
    "A Swell Time": ("Volume Swell Ambient", "An ambient preset built around volume swells (auto-swell or expression pedal), creating pad-like, orchestral textures from sustained notes."),
    "None More Black": ("Spinal Tap---Maximum Darkness", "A reference to Spinal Tap's `none more black' album cover---an ultra-dark, heavily saturated tone pushing everything to eleven."),
    "Bill&Ted at CERN": ("Time-Warped Sci-Fi Tone", "A playful mashup of Bill & Ted's time-travel adventure and CERN particle physics---expect unusual, physics-defying effects and pitch manipulation."),
    "Dark & Lush": ("Dark Ambient/Lush Clean", "A moody, atmospheric preset pairing dark amp voicing with lush reverb and modulation for introspective, ambient playing."),
    "Wild Year": ("Wild, Energetic Rock", "An energetic, untamed rock tone with aggressive dynamics and a raw, spirited character."),
    "BackWahrds": ("Backwards/Reverse Effects", "A preset featuring reverse delay and/or reverse effects to create the illusion of backwards guitar---an eerie, psychedelic staple."),
    "Chalice of M'eh": ("Mediocre Holy Grail (Humor)", "A tongue-in-cheek preset whose name plays on the `Holy Grail' of tone---this one is intentionally `meh,' or perhaps surprisingly good despite the self-deprecation."),
    "Mmmm Bat Heads": ("Ozzy Osbourne---Heavy Tone", "A reference to Ozzy Osbourne's notorious bat-biting incident. Expect a heavy, dark, sabbath-influenced tone with thick distortion."),
    "In Your House": ("Nine Inch Nails / Depeche Mode---Dark Synth-Rock", "A dark, industrial-tinged preset evoking the moody, electronic-influenced rock of acts like Nine Inch Nails or Depeche Mode."),
    "Eat lt  ": ("Eat It---Aggressive/Humor", "An aggressive tone whose name may reference `Weird Al' Yankovic's parody or simply an in-your-face attitude."),
    "BEL HAVEN, boi!": ("Southern/Bel Haven Tone", "A Southern-flavored tone with warm, slightly overdriven character---think porch-sitting blues-rock with a modern edge."),
    "Spirit of Sky": ("Spirit in the Sky (Norman Greenbaum)", "Inspired by Norman Greenbaum's 1970 hit, famous for its distinctive fuzzy, overdriven guitar tone achieved with a Maestro Fuzz-Tone."),
    "Andy Warb Hall": ("Andy Warhol (David Bowie)", "Inspired by David Bowie's `Andy Warhol' from the Hunky Dory album. Expect a glam-rock tone with artistic, off-kilter character."),
    "No Soup For You": ("Seinfeld Reference---Quirky Tone", "Named after the famous Seinfeld `Soup Nazi' catchphrase. A quirky, characterful preset---perhaps intentionally restrictive or surprising."),
    "Oh No Stereo": ("Wide Stereo Effects", "A preset emphasizing dramatic stereo effects processing---panning, stereo delay, and wide imaging."),
    "Mandarine Gaze": ("Orange-Tinted Shoegaze", "A shoegaze preset with an Orange amp foundation (`Mandarine'), delivering walls of dreamy, effects-drenched distortion."),
    "Chorus Crooner": ("Chorus-Heavy Clean for Crooning", "A lush, chorus-saturated clean tone ideal for smooth, melodic playing reminiscent of classic crooner-style guitar accompaniment."),
    "Sky Explosions": ("Explosions in the Sky (Post-Rock)", "Inspired by the post-rock band Explosions in the Sky---building from delicate, quiet passages to massive, reverb-drenched crescendos."),
    "Watt, Now?": ("Hiwatt/High-Wattage Clean", "A play on `What now?' and the Hiwatt amp brand. Expect a powerful, clean Hiwatt-style tone with exceptional headroom."),
    "Breath Of Odin": ("Julian Cope---Breath of Odin", "Inspired by Julian Cope's `Breath of Odin'---an expansive, psychedelic tone with mystical, Nordic overtones."),
    "Funk'n Roll": ("Funk/Rock Hybrid", "A funky, percussive rhythm tone blending tight funk articulation with rock-and-roll grit and attitude."),
    "Funk Clean": ("Clean Funk Guitar", "A pristine, snappy clean tone optimized for funk rhythm playing---tight compression, bright attack, and percussive clarity."),
    "Sunset Shimmer": ("Shimmering Reverb/Clean", "A warm, sunset-hued clean tone with shimmering reverb and delay, creating a golden, atmospheric quality."),
    "Ever Longer": ("Sustain/Ambient---Lengthened Notes", "A preset designed for maximum sustain and extended note decay, using compression and reverb to stretch notes into infinity."),
    "Rogue Vampires": ("Vampire Weekend---Indie Rock", "Inspired by the indie rock band Vampire Weekend---bright, clean-to-light-crunch tones with an eclectic, worldly character."),
    "Gorilla Clean": ("Gorillaz / Bruno Mars---Funky Clean", "A punchy, funky clean tone possibly inspired by Gorillaz or Bruno Mars---tight, rhythmic, and full of groove."),
    "Sweet Dispozish": ("Sweet Disposition (The Temper Trap)", "Inspired by The Temper Trap's `Sweet Disposition'---a warm, driven indie-rock tone building from clean to soaring crunch."),
    "Smooth Autopan": ("Smooth Auto-Panning Effect", "A smooth, hypnotic preset with auto-panning moving the sound across the stereo field."),
    "Flood In Texas": ("Texas Flood (Stevie Ray Vaughan)", "Inspired by Stevie Ray Vaughan's `Texas Flood'---a thick, bluesy tone with a cranked tube amp, warm overdrive, and expressive dynamics."),
    "Dream Syrup": ("Dreamy, Syrupy Tone", "A thick, sweet, dreamy tone---syrupy saturation with lush effects creating a warm, slow-moving sonic quality."),
    "Rhythm Sandman": ("Enter Sandman---Metallica Rhythm", "Inspired by the rhythm guitar tone from Metallica's `Enter Sandman'---tight, palm-muted chugging with a scooped, aggressive character."),
    "Glengarry Lead": ("Glengarry Glen Ross---`Always Be Leading'", "Named after the film Glengarry Glen Ross---an assertive, confident lead tone that `always closes.' Smooth sustain with cutting presence."),
    "Parallel Space": ("Parallel Signal Path/Effects", "A creative preset using parallel signal routing to blend contrasting effects paths for a complex, layered sound."),
    "'Merican Nights": ("American Nights---Rock", "An American-flavored rock tone evoking warm nights and open highways---think heartland rock with a modern edge."),
    "4D Love of Steve": ("For the Love of God (Steve Vai)", "Inspired by Steve Vai's `For the Love of God'---an expressive, sustain-rich lead tone with whammy bar theatrics and harmonic precision."),
    "Ointment": ("Smooth, Healing Tone", "A smooth, soothing tone---like musical ointment---featuring gentle overdrive with warm, rounded character."),
    "Cherry-coloured": ("Cherry-Coloured Funk (Cocteau Twins)", "Inspired by the Cocteau Twins' `Cherry-Coloured Funk'---an ethereal, dreampop tone with lush chorus, reverb, and shimmering textures."),
    "Low E Sludge": ("Low-Tuned Sludge Metal", "A downtuned sludge metal tone emphasizing the lowest registers with massive, filthy distortion and crushing weight."),
    "Thundermullet": ("Thunderous Rock (with Mullet Energy)", "An aggressive, arena-ready rock tone with the business-in-front, party-in-back energy of a glorious mullet. Pure 1980s thunder."),
    "Nesbit": ("Nesbit (Artist/Reference)", "A preset named for a person or character called Nesbit, featuring a distinctive tonal configuration."),
    "Star Talk": ("Cosmic/Space-Themed Clean", "A cosmic, space-themed tone with sparkling cleans and interstellar effects---inspired by the wonder of space exploration."),
    "Grease Cats": ("Rockabilly/Greaser Tone", "A rockabilly `greaser' tone with slapback delay, bright twangy crunch, and the rebellious energy of 1950s rock and roll."),
    "Dramatic Scene": ("Cinematic/Film Score Tone", "A dramatic, cinematic tone designed for soundtrack-style playing---building tension and emotional weight."),
    "PhD May": ("Brian May (Queen)---Astrophysicist", "Inspired by Brian May's signature guitar tone---the `PhD' references his real-life doctorate in astrophysics. Expect a layered, harmonized lead tone reminiscent of Queen's guitar orchestrations."),
    "Ducked Trails": ("Ducking Delay with Trails", "A delay preset where the repeats duck beneath your playing and bloom when you stop---creating trails that fill the spaces between notes."),
    "Rock Gaze": ("Shoegaze/Rock Hybrid", "A shoegaze-meets-rock tone with walls of fuzzy distortion, heavy reverb, and modulation---a noisier, more aggressive take on the dreampop aesthetic."),
    "Unicorns Forever": ("Magical/Whimsical Tone", "A whimsical, sparkly tone with shimmer effects and bright, fantastical character---unabashedly magical."),
    "Hairy Air": ("Fuzzy Ambient", "A fuzzy, textural tone where distortion and ambient effects combine to create a `hairy,' woolly sonic atmosphere."),
    "Bitey Panner": ("Biting Auto-Pan", "A tone with aggressive, biting character enhanced by rhythmic auto-panning for a choppy, dynamic stereo effect."),
    "Hi Octane": ("High-Energy Rock", "A high-octane, high-energy rock tone with aggressive gain, tight response, and adrenaline-fueled presence."),
    "Knife Fight": ("Aggressive, Cutting Tone", "A sharp, aggressive tone with a cutting edge---designed for confrontational, in-your-face playing."),
    "Barracudies": ("Barracuda (Heart)", "Inspired by Heart's `Barracuda'---a driving, aggressive rock riff tone with tight crunch and powerful dynamics."),
    "Snapshot Hotshot": ("Snapshot Demonstration Preset", "A preset designed to showcase the Helix snapshot feature, with multiple preconfigured tonal variations accessible via snapshot switching."),
    "Twinning": ("Dual/Twin Amp Configuration", "A dual-amp preset blending two Twin-style amps (or two matched amp voices) for a full, doubled sound."),
    "After the Fact": ("Post-Processed/Aftereffect Tone", "A preset emphasizing post-processing: the effects come `after the fact' of the core tone, layering delay, reverb, and modulation."),
    "Dream Off": ("Dreamy Ambient Off-Switch", "A dreamy ambient preset that fades into ethereal territory---like switching off reality into a dream state."),
    "Go Your Way": ("Go Your Own Way (Fleetwood Mac)", "Inspired by Fleetwood Mac's `Go Your Own Way'---a warm, jangly, classic rock rhythm tone with a driving feel."),
    "Double Trackin'": ("Double-Tracked Guitar Effect", "A preset simulating the studio technique of double-tracking guitars using short delays and pitch modulation for a wider, thicker sound."),
    "Bit Like Heaven": ("Just Like Heaven (The Cure)", "Inspired by The Cure's `Just Like Heaven'---a bright, chorus-laden tone with jangly arpeggios and a dreamy new wave character."),
    "Paranoia": ("Paranoid (Black Sabbath)", "Inspired by Black Sabbath's `Paranoid'---a classic heavy rock tone with thick, aggressive crunch and Tony Iommi's signature darkness."),
    "Slowish Ride": ("Slowdive / Ride (Shoegaze Bands)", "A shoegaze tone referencing the bands Slowdive and Ride---heavy reverb, modulation, and distortion creating a dreamy wall of sound."),
    "Smoke on the H2O": ("Smoke on the Water (Deep Purple)", "Inspired by Deep Purple's iconic riff and Ritchie Blackmore's overdriven Marshall tone---one of the most recognizable guitar sounds in rock history."),
    "Ziggy Moondust": ("Ziggy Stardust / Moonage Daydream (Bowie)", "Inspired by David Bowie's glam-rock era---the overdriven, theatrical guitar tone of Mick Ronson on the Ziggy Stardust album."),
    "Sultans": ("Sultans of Swing (Dire Straits)", "Inspired by Mark Knopfler's clean, fingerpicked tone on Dire Straits' `Sultans of Swing'---a warm, dynamic clean sound with natural compression."),
    "Blue Wind": ("Blue Wind (Jeff Beck)", "Inspired by Jeff Beck's `Blue Wind' from the Wired album---a fluid, expressive lead tone with crisp articulation."),
    "25? No, 6 to 4": ("25 or 6 to 4 (Chicago)", "Inspired by Chicago's rock classic---a driving, brass-band-meets-rock-guitar tone with wah and aggressive crunch."),
    "Country Chorus": ("Country Guitar with Chorus", "A bright, clean country tone with lush chorus effect for that signature Nashville shimmer and sparkle."),
    "Rock My Yacht": ("Yacht Rock", "A smooth, polished `yacht rock' tone---warm cleans with subtle chorus and compression, evoking the laid-back sophistication of late-1970s soft rock."),
    "Gimme +/-3 Steps": ("Gimme Three Steps (Lynyrd Skynyrd)", "Inspired by Lynyrd Skynyrd's Southern rock classic---a warm, slightly overdriven tone with Southern swagger and blues-rock grit."),
    "Cliffs of Grover": ("Cliffs of Dover (Eric Johnson)", "Inspired by Eric Johnson's `Cliffs of Dover'---a fluid, singing lead tone with pristine cleans, subtle drive, and chorus for Johnson's signature violin-like sustain."),
    "Goin' Home": ("Going Home (Various Artists)", "A warm, homeward-bound tone evoking the feeling of a long journey's end---clean to light crunch with a comfortable, familiar character."),
    "Jail Breaker": ("Jailbreak (Thin Lizzy / AC/DC)", "Inspired by Thin Lizzy's and AC/DC's hard-rock anthems---a punchy, riff-driven rock tone with dual-guitar energy."),
    "2/3 Beards": ("ZZ Top (Two-Thirds Have Beards)", "A reference to ZZ Top, where two of three members sport iconic beards (ironically, drummer Frank Beard does not). Expect a Texas-blues-rock tone with gritty, boogie-driven character."),
    "On the Road": ("On the Road---Traveling Rock", "A road-ready, versatile rock tone capturing the spirit of the open highway---works for anything from heartland rock to blues."),
    "Senor Sandman": ("Mr. Sandman (The Chordettes) / Enter Sandman", "A dreamy or heavy tone (depending on interpretation) referencing either the classic 1950s doo-wop hit or Metallica's metal anthem."),
    "$$$ For Nothin'": ("Money for Nothing (Dire Straits)", "Inspired by Dire Straits' `Money for Nothing'---Mark Knopfler's legendary overdriven tone, originally recorded with a Gibson Les Paul through a cranked Laney amp."),
    "Phase Dance": ("Phase Dance (Pat Metheny Group)", "Inspired by the Pat Metheny Group's `Phase Dance'---a warm, jazz-fusion tone with phaser effects and smooth, flowing character."),
    "Roundabout": ("Roundabout (Yes)", "Inspired by Yes's prog-rock epic `Roundabout'---a bright, articulate tone combining clean passages with driven sections, capturing Steve Howe's signature sound."),
    "Dbl Match": ("Double Matchless DC-30", "A dual-amp preset running two Matchless DC-30 amp voices for a rich, three-dimensional tone with harmonic depth."),
    # Factory 2 Bass
    "BAS:ParallelFuzz": ("Parallel Fuzz Bass", "A bass tone running fuzz in parallel with the clean signal, preserving low-end definition while adding aggressive fuzz texture on top."),
    "BAS:Hang Me Out": ("Bass---Hang Out Tone", "A relaxed, open bass tone designed for laid-back grooves and casual playing."),
    "BAS:Brit Bass": ("British Bass Amp Tone", "A bass tone built around a British-voiced bass amplifier with gritty midrange and punchy character."),
    "BAS:Pony 1Up": ("Bass---Power Up Tone", "An energetic, powered-up bass tone with enhanced dynamics and aggressive presence."),
    "BAS:FunkIfIKnow": ("Funk Bass---Funky Ignorance", "A slap-friendly funk bass tone with tight compression and bright, snappy attack for percussive playing."),
    "BAS:DangeRuss": ("Dangerous Russ (Artist Bass)", "An artist-named bass preset featuring a bold, assertive bass tone with distinctive character."),
    "BAS:Liberator": ("Liberated Bass Tone", "A free, unrestrained bass tone designed for expressive playing without tonal boundaries."),
    "BAS:Phat Rat": ("Phat RAT Bass (Pro Co RAT)", "A bass tone featuring the Pro Co RAT distortion for a thick, `phat' bass overdrive with aggressive midrange."),
    "BAS:Sydcar Synth": ("Sidecar Synth Bass", "A bass-to-synth preset using synth effects alongside the bass signal for electronic-influenced bass textures."),
    "BAS:Boots Bass": ("Boots---Heavy Bass Tone", "A heavy, boot-stomping bass tone with authoritative low-end and aggressive presence."),
    "BAS:Incubass": ("Incubus-Inspired Bass", "A bass tone inspired by the alternative rock band Incubus---warm, dynamic, and versatile with a modern rock character."),

    # ══════════════════════ TEMPLATES ══════════════════════
    "Quick Start": ("Quick Start Template", "A simple starting template with a Fender Deluxe Reverb, room reverb, and basic effects---the fastest path from silence to sound."),
    "Parallel Spans": ("Parallel Signal Paths Template", "Demonstrates parallel signal routing with two amps (Fender Deluxe Reverb and Hiwatt DR103) running simultaneously on separate DSP paths."),
    "SNP:4-Amp Spill": ("Snapshot: 4-Amp Spillover", "A snapshot-based template cycling through four amps (Deluxe Reverb, JCM800, AC-30 Fawn, Line 6 Fatality) with spillover delay/reverb that persists across amp changes."),
    "Super Serial x2": ("Super Serial Dual-DSP Template", "An empty dual-DSP serial routing template---two full signal chains in series for maximum block count and flexibility."),
    "4-Cable Method": ("4-Cable Method Routing", "Routing template for the 4-cable method, integrating Helix with an external tube amp's effects loop for combined preamp/effects processing."),
    "7-Cable Method": ("7-Cable Method Routing", "Advanced routing template for the 7-cable method, integrating Helix with two external amps and their effects loops simultaneously."),
    "TwoTones A-B": ("Two Tones A/B Switching", "A dual-amp template (Fender Deluxe Reverb and Vox AC-15) with A/B switching between the two---instant tone changes via footswitch."),
    "TwoTones Blend": ("Two Tones Blended", "A dual-amp template (Fender Deluxe Reverb and Vox AC-15) blended together simultaneously for a richer, more complex combined tone."),
    "Ext Amp & Pedals": ("External Amp and Pedals Template", "Routing template for using Helix as an effects-only pedalboard in front of an external amplifier."),
    "Wet-Dry-Wet FRFR": ("Wet/Dry/Wet for FRFR Speakers", "Routing template for a wet/dry/wet monitoring configuration using FRFR (full-range flat-response) powered speakers."),
    "Wet-Dry-Wet Amps": ("Wet/Dry/Wet for Real Amps", "Routing template for a wet/dry/wet rig using a real amp for the dry center channel and Helix for stereo wet effects."),
    "4 Tone Switcher": ("Four-Tone Switcher Template", "A routing template with four independent signal paths selectable via gain/mute blocks, functioning as a four-channel amp switcher."),
    "Guitar + Vocals": ("Guitar and Vocals Dual Path", "A dual-path template processing guitar on DSP1 (Deluxe Reverb) and vocals on DSP2 (vintage preamp with LA-2A compression and EQ)."),
    "Gtr+Vox+Bas+Keys": ("Guitar, Vocals, Bass, and Keys Mixer", "A four-input mixing template routing guitar, vocals, bass, and keys through separate processing chains with individual EQ and compression."),
    "DT25-DT50 Remote": ("DT25/DT50 Amp Remote Control", "Control template for Line 6 DT25 or DT50 tube amplifiers, enabling remote switching of amp topology, class, and voicing from Helix."),
    "Stereo Mixer": ("Stereo Mixer Template", "A multi-channel stereo mixer template with individual EQ, compression, and volume control per channel---useful for mixing multiple instruments."),
    "MIDI Bass Pedals": ("MIDI Bass Pedal Controller", "Configures Helix as a MIDI bass pedal controller, assigning MIDI notes to footswitches for triggering external MIDI sound modules."),
    "Real Bass Pedals": ("Real Bass Pedal Synth Triggers", "Uses 13 instances of the 3-Note Generator synth to create a polyphonic bass pedalboard using Helix footswitches."),
    "Momentary Pitch": ("Momentary Pitch Shift Effects", "Eight momentary pitch shifters assigned to footswitches for real-time pitch manipulation---useful for harmonizer and whammy-style effects."),
    "DAW Remote (MMC)": ("DAW Remote via MIDI Machine Control", "MIDI template turning Helix into a DAW transport controller using MMC (MIDI Machine Control) commands---play, stop, record, rewind."),
    "Cubase Remote": ("Steinberg Cubase DAW Remote", "MIDI remote control template for Steinberg Cubase, mapping Helix footswitches to transport and function controls."),
    "Pro Tools (Mac)": ("Pro Tools (Mac) DAW Remote", "MIDI remote control template for Avid Pro Tools on macOS."),
    "Pro Tools (PC)": ("Pro Tools (PC) DAW Remote", "MIDI remote control template for Avid Pro Tools on Windows."),
    "Logic/GarageBand": ("Apple Logic Pro / GarageBand Remote", "MIDI remote control template for Apple Logic Pro and GarageBand."),
    "Live (Mac)": ("Ableton Live (Mac) Remote", "MIDI remote control template for Ableton Live on macOS."),
    "Live (PC)": ("Ableton Live (PC) Remote", "MIDI remote control template for Ableton Live on Windows."),
    "Reaper (Mac)": ("Cockos Reaper (Mac) Remote", "MIDI remote control template for Cockos Reaper on macOS."),
    "Reaper (PC)": ("Cockos Reaper (PC) Remote", "MIDI remote control template for Cockos Reaper on Windows."),
    "StudioOne Remote": ("PreSonus Studio One Remote", "MIDI remote control template for PreSonus Studio One."),
    "Cakewalk Remote": ("Cakewalk by BandLab Remote", "MIDI remote control template for Cakewalk by BandLab (formerly SONAR)."),
    "MainStage Remote": ("Apple MainStage Remote", "MIDI remote control template for Apple MainStage, useful for live performance with virtual instruments."),
    "QLab Remote": ("Figure 53 QLab Remote", "MIDI remote control template for QLab, a professional show control application for theater and live events."),
    "YouTube Remote": ("YouTube Playback Remote", "MIDI/keyboard shortcut template for controlling YouTube video playback from Helix footswitches."),
    "iTunes Remote": ("Apple iTunes/Music Remote", "MIDI/keyboard shortcut template for controlling Apple iTunes (Music) playback from Helix."),
    "Spotify (Mac)": ("Spotify (Mac) Remote", "MIDI/keyboard shortcut template for controlling Spotify playback on macOS."),
    "Spotify (PC)": ("Spotify (PC) Remote", "MIDI/keyboard shortcut template for controlling Spotify playback on Windows."),
    "Keynote Remote": ("Apple Keynote Presentation Remote", "MIDI/keyboard shortcut template for controlling Apple Keynote presentations---advance slides from your pedalboard."),
    "FPS Video Game": ("First-Person Shooter Game Controller", "A novelty template mapping Helix footswitches to WASD keyboard controls for playing first-person shooter video games with your feet."),
    "SUNDSTERM": ("Sundstorm (Synth Soundscape)", "An elaborate synth soundscape preset using multiple oscillator generators, bitcrusher, autofilter, and pattern tremolo to create evolving electronic textures---one of the few tonal presets in the Templates bank."),
}

# ═══════════════════════════════════════════════════════════════
# ARTIST INDEX: preset_name -> [artist(s)]
# ═══════════════════════════════════════════════════════════════

PRESET_ARTISTS = {
    # Factory 1 - Song/Artist-Inspired
    "Justice Fo Y'all": ["Metallica (James Hetfield)"],
    "Stone Cold Loco": ["Queen", "Guns N' Roses"],
    "Plush Garden": ["Stone Temple Pilots (Dean DeLeo)"],
    "Cowboys from DFW": ["Pantera (Dimebag Darrell)"],
    "GRAMMATICO JNC": ["JNC (Artist Collaboration)"],
    "SCREAMS JNC": ["JNC (Artist Collaboration)"],
    "WATERS IN HELL": ["Pink Floyd (David Gilmour, Roger Waters)"],
    "RC REINCARNATION": ["RC (Artist Collaboration)"],
    "FELIX MARK IV": ["Felix (Artist Collaboration)"],
    "FELIX JAZZ 120": ["Felix (Artist Collaboration)"],
    "FELIX DELUXE MOD": ["Felix (Artist Collaboration)"],
    "FELIX ENGL": ["Felix (Artist Collaboration)"],
    # Factory 1 - Artist Signature
    "BUMBLE ACOUSTIC": ["Ron `Bumblefoot' Thal"],
    "BMBLFOOT PRINCE": ["Ron `Bumblefoot' Thal"],
    "SHEEHAN PEARCE": ["Billy Sheehan"],
    "SHEEHAN SVT4PRO": ["Billy Sheehan"],
    "BULB RHYTHM": ["Misha Mansoor (Periphery)"],
    "BULB LEAD": ["Misha Mansoor (Periphery)"],
    "BULB CLEAN": ["Misha Mansoor (Periphery)"],
    "BULB AMBIENT": ["Misha Mansoor (Periphery)"],
    "EMPTY GARBAGE": ["Garbage (Duke Erikson, Steve Marker)"],
    "ONLY GARBAGE": ["Garbage (Duke Erikson, Steve Marker)"],
    "GARBAGE BASS": ["Garbage"],
    "BILLY KASTODON": ["Bill Kelliher (Mastodon)"],
    "DJENT LA FUENTE": ["La Fuente"],
    "JONBUTTON UZAPIK": ["Jon Button"],
    "TrevLukatherSolo": ["Trev Lukather"],
    "HOWE WILDEST": ["Greg Howe"],
    "PETE THORN DUO": ["Pete Thorn"],
    "RHETT'S ALLROUND": ["Rhett Shull"],
    "JEFF SCHROEDER 1": ["Jeff Schroeder (Smashing Pumpkins)"],
    "JEFF SCHROEDER 2": ["Jeff Schroeder (Smashing Pumpkins)"],
    "GRACOXONBUM": ["Graham Coxon (Blur)"],
    "Buck Mild": ["Peter Buck (R.E.M.)"],
    "LEWIE ALLEN BLUE": ["Lewis Allen"],
    "RABEAAFRO LEAD": ["Rabea Massaad"],
    "RABEAAFRO CHUGGS": ["Rabea Massaad"],
    "RABEA AMBIENT": ["Rabea Massaad"],
    "RABEA AMBI LEAD": ["Rabea Massaad"],
    "DEVIN TOWNSEND": ["Devin Townsend"],
    "SHONN'S SHOTGUN": ["Shonn"],
    "MJA + PANCAKE": ["MJA"],
    "PHILIP BYTONE": ["Philip"],
    "REUTER LEAD": ["Reuter"],
    "PV Vitriol Lead": ["Misha Mansoor (Periphery)"],
    # Factory 2 - Song-Inspired
    "Mmmm Bat Heads": ["Ozzy Osbourne / Black Sabbath"],
    "Spirit of Sky": ["Norman Greenbaum"],
    "Andy Warb Hall": ["David Bowie (Mick Ronson)"],
    "Sky Explosions": ["Explosions in the Sky"],
    "Breath Of Odin": ["Julian Cope"],
    "Sweet Dispozish": ["The Temper Trap"],
    "Flood In Texas": ["Stevie Ray Vaughan"],
    "Rhythm Sandman": ["Metallica (James Hetfield)"],
    "Glengarry Lead": ["Film: Glengarry Glen Ross"],
    "4D Love of Steve": ["Steve Vai"],
    "Cherry-coloured": ["Cocteau Twins (Robin Guthrie)"],
    "PhD May": ["Brian May (Queen)"],
    "Barracudies": ["Heart (Nancy Wilson)"],
    "Go Your Way": ["Fleetwood Mac (Lindsey Buckingham)"],
    "Bit Like Heaven": ["The Cure (Robert Smith)"],
    "Paranoia": ["Black Sabbath (Tony Iommi)"],
    "Slowish Ride": ["Slowdive", "Ride"],
    "Smoke on the H2O": ["Deep Purple (Ritchie Blackmore)"],
    "Ziggy Moondust": ["David Bowie (Mick Ronson)"],
    "Sultans": ["Dire Straits (Mark Knopfler)"],
    "Blue Wind": ["Jeff Beck"],
    "25? No, 6 to 4": ["Chicago (Terry Kath)"],
    "Gimme +/-3 Steps": ["Lynyrd Skynyrd"],
    "Cliffs of Grover": ["Eric Johnson"],
    "Jail Breaker": ["Thin Lizzy", "AC/DC"],
    "2/3 Beards": ["ZZ Top (Billy Gibbons)"],
    "$$$ For Nothin'": ["Dire Straits (Mark Knopfler)"],
    "Phase Dance": ["Pat Metheny Group"],
    "Roundabout": ["Yes (Steve Howe)"],
    "Rogue Vampires": ["Vampire Weekend"],
    "Gorilla Clean": ["Gorillaz / Bruno Mars"],
    "BAS:Incubass": ["Incubus"],
    "None More Black": ["Spinal Tap"],
    "Mayer'ish JS": ["John Mayer"],
    "Robben'ish JS": ["Robben Ford"],
}

# ═══════════════════════════════════════════════════════════════
# GENRE INDEX: preset_name -> [genre(s)]
# ═══════════════════════════════════════════════════════════════

PRESET_GENRES = {
    # ── Blues ──
    "Flood In Texas": ["Blues", "Blues-Rock"],
    "Mayer'ish JS": ["Blues"],
    "Robben'ish JS": ["Jazz-Blues", "Fusion"],
    "LEWIE ALLEN BLUE": ["Blues"],
    "Blue Wind": ["Jazz-Fusion", "Blues-Rock"],
    "Tweed Blues Brt": ["Blues", "Blues-Rock"],
    # ── Classic Rock ──
    "Brit Plexi Brt": ["Classic Rock", "Hard Rock"],
    "Stone Cold Loco": ["Classic Rock", "Hard Rock"],
    "Smoke on the H2O": ["Classic Rock", "Hard Rock"],
    "Paranoia": ["Classic Rock", "Heavy Metal"],
    "Ziggy Moondust": ["Glam Rock", "Classic Rock"],
    "Jail Breaker": ["Classic Rock", "Hard Rock"],
    "$$$ For Nothin'": ["Classic Rock"],
    "Roundabout": ["Progressive Rock"],
    "25? No, 6 to 4": ["Classic Rock", "Jazz-Rock"],
    "PV Panama": ["Hard Rock", "Classic Rock"],
    "Go Your Way": ["Classic Rock", "Pop Rock"],
    # ── Hard Rock / Heavy ──
    "Cowboys from DFW": ["Thrash Metal", "Groove Metal"],
    "Barracudies": ["Hard Rock"],
    "Thundermullet": ["Hard Rock", "Arena Rock"],
    "Hi Octane": ["Hard Rock"],
    "Knife Fight": ["Hard Rock"],
    "Cali Rectifire": ["Hard Rock", "Metal"],
    "Placater Dirty": ["Hard Rock"],
    "Mandarin Rocker": ["Hard Rock", "British Rock"],
    # ── Metal ──
    "Justice Fo Y'all": ["Thrash Metal"],
    "Rhythm Sandman": ["Heavy Metal", "Thrash Metal"],
    "FAUX 7 STG CHUG": ["Metal", "Djent"],
    "Low E Sludge": ["Sludge Metal"],
    "Das Benzin Mega": ["Progressive Metal"],
    "Line 6 Badonk": ["Metal"],
    "BILLY KASTODON": ["Sludge Metal", "Progressive Metal"],
    "THIS IS THE END": ["Metal"],
    "A DEADLY RHYTHM": ["Metal"],
    # ── Progressive Metal / Djent ──
    "Revv Gen Purple": ["Progressive Metal", "Djent"],
    "Revv Gen Red": ["Progressive Metal", "Djent"],
    "PV Vitriol Lead": ["Progressive Metal", "Djent"],
    "BULB RHYTHM": ["Progressive Metal", "Djent"],
    "BULB LEAD": ["Progressive Metal"],
    "DJENT LA FUENTE": ["Djent", "Progressive Metal"],
    # ── Doom / Stoner ──
    "Moo)))n Jump": ["Doom Metal", "Stoner Rock"],
    "RIFFS AND BEARDS": ["Stoner Rock", "Desert Rock"],
    "But Does It Doom": ["Doom Metal"],
    "Mmmm Bat Heads": ["Doom Metal", "Heavy Metal"],
    "None More Black": ["Heavy Metal", "Humor"],
    # ── Grunge / Alternative ──
    "Plush Garden": ["Grunge", "Alternative Rock"],
    "JEFF SCHROEDER 1": ["Alternative Rock"],
    "JEFF SCHROEDER 2": ["Alternative Rock"],
    "GRACOXONBUM": ["Alternative Rock", "Indie Rock"],
    "EMPTY GARBAGE": ["Alternative Rock", "Electronic Rock"],
    "ONLY GARBAGE": ["Alternative Rock", "Industrial Rock"],
    # ── Indie / Post-Punk ──
    "Big County": ["Post-Punk", "New Wave"],
    "Buck Mild": ["Indie Rock", "Jangle Pop"],
    "Rogue Vampires": ["Indie Rock"],
    "Sweet Dispozish": ["Indie Rock"],
    "Bit Like Heaven": ["Post-Punk", "New Wave"],
    # ── Shoegaze / Post-Rock ──
    "Mandarine Gaze": ["Shoegaze"],
    "Rock Gaze": ["Shoegaze", "Alternative Rock"],
    "Slowish Ride": ["Shoegaze"],
    "Sky Explosions": ["Post-Rock"],
    "SPOTLIGHTS": ["Post-Rock", "Ambient"],
    "Hairy Air": ["Shoegaze", "Ambient"],
    # ── Ambient / Atmospheric ──
    "Dark & Lush": ["Ambient"],
    "A Swell Time": ["Ambient"],
    "BUBBLE NEST": ["Ambient"],
    "GLISTEN": ["Ambient", "Clean"],
    "Ever Longer": ["Ambient"],
    "BULB AMBIENT": ["Ambient", "Progressive Metal"],
    "BULB CLEAN": ["Clean", "Ambient"],
    "RABEA AMBIENT": ["Ambient"],
    "RABEA AMBI LEAD": ["Ambient"],
    "Sunset Shimmer": ["Ambient", "Clean"],
    "Dream Syrup": ["Ambient", "Dreampop"],
    "Dream Off": ["Ambient", "Dreampop"],
    "Parallel Space": ["Ambient", "Experimental"],
    "Star Talk": ["Ambient", "Clean"],
    "Unicorns Forever": ["Ambient", "Experimental"],
    "ISS Flyby": ["Ambient", "Experimental"],
    # ── Jazz / Fusion ──
    "Jazz Rivet 120": ["Jazz", "Clean"],
    "FELIX JAZZ 120": ["Jazz", "Clean"],
    "Phase Dance": ["Jazz-Fusion"],
    "HOWE WILDEST": ["Jazz-Fusion"],
    # ── Country ──
    "Country Chorus": ["Country"],
    "G.O.A.T. Rodeo": ["Country", "Southern Rock"],
    "RHETT'S ALLROUND": ["Country", "Blues", "Rock"],
    # ── Southern Rock / Blues-Rock ──
    "Gimme +/-3 Steps": ["Southern Rock"],
    "2/3 Beards": ["Blues-Rock", "Southern Rock"],
    "Goin' Home": ["Blues-Rock", "Southern Rock"],
    "On the Road": ["Rock", "Southern Rock"],
    "'Merican Nights": ["Rock", "Americana"],
    # ── Funk ──
    "Funk'n Roll": ["Funk", "Rock"],
    "Funk Clean": ["Funk", "Clean"],
    "Gorilla Clean": ["Funk", "Pop"],
    "BAS:FunkIfIKnow": ["Funk", "Bass"],
    # ── Pop / Yacht Rock ──
    "Rock My Yacht": ["Yacht Rock", "Soft Rock"],
    "Chorus Crooner": ["Pop", "Clean"],
    "Smooth Autopan": ["Pop", "Ambient"],
    # ── Psychedelic ──
    "WATERS IN HELL": ["Psychedelic Rock", "Progressive Rock"],
    "BackWahrds": ["Psychedelic", "Experimental"],
    "Cherry-coloured": ["Dreampop", "Shoegaze"],
    # ── Glam Rock ──
    "Andy Warb Hall": ["Glam Rock"],
    "GUILTY PLEASURES": ["Arena Rock", "1980s Rock"],
    "RICHEESE": ["Arena Rock", "1980s Rock"],
    # ── Rockabilly ──
    "Mockabilly": ["Rockabilly"],
    "Grease Cats": ["Rockabilly"],
    # ── Synth / Electronic ──
    "Stranger Synth": ["Synth", "Electronic"],
    "Big Monosynth": ["Synth", "Electronic"],
    "BAS:Sydcar Synth": ["Synth", "Bass", "Electronic"],
    "In Your House": ["Industrial", "Electronic Rock"],
    # ── Dub / Reggae ──
    "BIG DUBB": ["Dub", "Reggae"],
    # ── Experimental / SFX ──
    "GlitchVerb": ["Experimental"],
    "No:Thing": ["Experimental", "Ambient"],
    "InSTANtgH0St/24": ["Experimental", "Ambient"],
    "OveRTONeGHoSt 3": ["Experimental"],
    "PaddingToNe": ["Ambient", "Experimental"],
    "R U SERIOUS?": ["Experimental", "Humor"],
    "Bill&Ted at CERN": ["Experimental", "Humor"],
    "Chalice of M'eh": ["Humor"],
    "BIG VENUE DRIVE": ["Rock"],
    "SFX:Dr. Strange": ["Sound Effects"],
    "SFX:EXP Disturb": ["Sound Effects"],
    "SFX:Hokulani": ["Sound Effects"],
    "SFX:Pulse Drone": ["Sound Effects"],
    "SFX:Rezz Score": ["Sound Effects"],
    "SFX:Slot Machine": ["Sound Effects"],
    "SFX:Trip City": ["Sound Effects", "Psychedelic"],
    "SFX:Ufology": ["Sound Effects"],
    # ── Misc tagged ──
    "You Shall Pass": ["Cinematic", "Experimental"],
    "Dramatic Scene": ["Cinematic"],
    "Ducked Trails": ["Ambient", "Utility"],
    "Snapshot Hotshot": ["Utility"],
    "Double Trackin'": ["Studio Technique"],
    "DEVIN TOWNSEND": ["Progressive Metal", "Ambient"],
    "Parallel Muffs": ["Fuzz", "Experimental"],
    "X Ray": ["Clean", "Transparent"],
    "4D Love of Steve": ["Shred", "Hard Rock"],
    "Cliffs of Grover": ["Shred", "Blues-Rock"],
    "PhD May": ["Classic Rock", "Arena Rock"],
    "Sultans": ["Classic Rock", "Blues-Rock"],
    "Dbl Match": ["Boutique", "Clean"],
    "PETE THORN DUO": ["Rock", "Session"],
    "Twinning": ["Clean", "Studio Technique"],
    "After the Fact": ["Ambient"],
    "Bitey Panner": ["Experimental"],
    "Ointment": ["Clean", "Blues"],
    "Nesbit": ["Rock"],
    "Oh No Stereo": ["Stereo", "Experimental"],
    "Watt, Now?": ["Classic Rock", "Clean"],
    "Bentique": ["Boutique", "Clean"],
    "BEL HAVEN, boi!": ["Southern Rock", "Blues-Rock"],
    "No Soup For You": ["Humor"],
    "Wild Year": ["Rock"],
    "Eat lt  ": ["Rock", "Humor"],
    "SUNRISE DRIVE": ["Rock", "Overdrive"],
    "DUSTED": ["Vintage", "Overdrive"],
    "Glengarry Lead": ["Lead", "Rock"],
    "Senor Sandman": ["Rock"],
    "Mail Order Twin": ["Vintage", "Lo-Fi"],
    "SCREAMS JNC": ["High-Gain", "Lead"],
    "GRAMMATICO JNC": ["Boutique", "Clean"],
    "RABEAAFRO LEAD": ["Progressive Metal", "Lead"],
    "RABEAAFRO CHUGGS": ["Progressive Metal", "Djent"],
    "TrevLukatherSolo": ["Rock", "Lead"],
    "BUMBLE ACOUSTIC": ["Acoustic Simulation"],
    "Mockabilly": ["Rockabilly"],
    "Funk'n Roll": ["Funk", "Rock"],
    "Big County": ["Post-Punk", "New Wave"],
    "GARBAGE BASS": ["Alternative Rock", "Bass"],
    "SHEEHAN PEARCE": ["Rock", "Bass"],
    "SHEEHAN SVT4PRO": ["Rock", "Bass"],
    "THE BLUE AGAVE": ["Jazz", "Bass"],
    "BAS:ParallelFuzz": ["Fuzz", "Bass"],
    "BAS:Brit Bass": ["British Rock", "Bass"],
    "BAS:Phat Rat": ["Rock", "Bass"],
    "BAS:Incubass": ["Alternative Rock", "Bass"],
    "BAS:Boots Bass": ["Rock", "Bass"],
    "BAS:Pony 1Up": ["Rock", "Bass"],
    "BAS:DangeRuss": ["Rock", "Bass"],
    "BAS:Liberator": ["Rock", "Bass"],
    "BAS:Hang Me Out": ["Rock", "Bass"],
    "SUNDSTERM": ["Synth", "Experimental", "Sound Effects"],
}

# ═══════════════════════════════════════════════════════════════
# PICKUP RECOMMENDATIONS: preset_name -> (type, position, notes)
#   type: "Humbucker", "Single Coil", "P90", "Either", "Piezo/Acoustic"
#   position: "Bridge", "Neck", "Middle", "Neck or Middle", etc.
#   notes: context string
# Bass and pure-SFX presets omitted where not applicable.
# ═══════════════════════════════════════════════════════════════

PRESET_PICKUPS = {
    # ══════════ FACTORY 1: Amp Showcases ══════════
    "US Double Nrm": ("Either", "Any", "Classic Fender clean---single coils are canonical but humbuckers work for a warmer voice."),
    "Essex A30": ("Single Coil", "Bridge or Middle", "AC-30 chime is most authentic with single coils; bridge for jangle, middle for sweetness."),
    "Brit Plexi Brt": ("Humbucker", "Bridge", "Plexi bright channel into a Les Paul bridge humbucker is the classic rock pairing."),
    "Cali Rectifire": ("Humbucker", "Bridge", "High-output bridge humbucker is the canonical Rectifier pairing for tight metal rhythm."),
    "US Deluxe Nrm": ("Single Coil", "Neck or Middle", "The Deluxe Reverb excels with Strat-style single coils for warm, expressive breakup."),
    "A30 Fawn Nrm": ("Single Coil", "Any", "The Fawn AC-30 pairs beautifully with any single coil position for vintage British warmth."),
    "Revv Gen Purple": ("Humbucker", "Bridge", "Modern high-gain channel designed for tight bridge humbucker articulation."),
    "Revv Gen Red": ("Humbucker", "Bridge", "Highest gain setting---bridge humbucker essential for clarity under extreme saturation."),
    "Archetype Clean": ("Either", "Any", "Versatile clean channel that responds well to any pickup configuration."),
    "Matchstick Ch1": ("Single Coil", "Neck or Middle", "Boutique EL84 cleans shine with single coils; neck for jazz warmth, middle for shimmer."),
    "Das Benzin Mega": ("Humbucker", "Bridge", "Diezel high-gain channel optimized for bridge humbucker precision."),
    "Archetype Lead": ("Humbucker", "Bridge", "High-gain lead channel pairs naturally with bridge humbucker for sustain and cut."),
    "Jazz Rivet 120": ("Single Coil", "Neck", "The JC-120 with a neck single coil is the classic jazz guitar clean tone."),
    "Grammatico GSG": ("Single Coil", "Any", "Boutique clean amp that reveals single coil nuance beautifully."),
    "Line 6 Elmsley": ("Either", "Any", "Original design---experiment freely with pickup choices."),
    "Moo)))n Jump": ("Humbucker", "Bridge", "Doom/stoner tone demands thick bridge humbucker output for massive low-end saturation."),
    "US Princess": ("Single Coil", "Neck or Middle", "The Princeton is quintessentially a single-coil amp; neck for warmth, middle for sparkle."),
    "GrammaticoLG Nrm": ("Single Coil", "Any", "Tweed-inspired boutique amp most authentic with single coils."),
    "Placater Dirty": ("Humbucker", "Bridge", "Hot-rodded Marshall design---bridge humbucker is the intended pairing."),
    "PV Panama": ("Humbucker", "Bridge", "Eddie Van Halen's tone: bridge humbucker is essential."),
    "Cali Texas Ch 1": ("Single Coil", "Neck or Middle", "The Lone Star clean is Fender-influenced; single coils bring out its best."),
    "Line 6 Ventoux": ("Either", "Any", "Original design---no canonical pickup pairing."),
    "Derailed Ingrid": ("Humbucker", "Bridge", "Trainwreck amps are most associated with humbuckers or P90s for explosive dynamics."),
    "PV Vitriol Lead": ("Humbucker", "Bridge", "Misha Mansoor's signature: high-output bridge humbucker for djent precision."),
    "Cali IV Rhythm 1": ("Either", "Any", "Mark IV is versatile---single coils for cleans, humbuckers for driven sounds."),
    "Line 6 Litigator": ("Either", "Any", "Pedal-platform amp that works as a canvas for any pickup type."),
    "Cartographer": ("Either", "Any", "Boutique original---experiment with pickup choices."),
    "Mandarin Rocker": ("Humbucker", "Bridge", "Orange amps pair canonically with bridge humbuckers for thick British voice."),
    "Mail Order Twin": ("Single Coil", "Bridge", "Silvertone's gritty lo-fi character is most authentic with a bright single coil."),
    "Tweed Blues Brt": ("Either", "Any", "The Bassman is universal---equally at home with Teles, Strats, and Les Pauls."),
    "German Mahadeva": ("Humbucker", "Neck or Bridge", "Shiva is versatile; neck humbucker for cleans, bridge for driven tones."),
    "Line 6 Badonk": ("Humbucker", "Bridge", "High-gain metal design built for bridge humbucker aggression."),
    # DI
    "DI": ("Either", "Any", "Direct input---any pickup; blank canvas for reamping."),
    # ══════════ FACTORY 1: Song/Artist-Inspired ══════════
    "Justice Fo Y'all": ("Humbucker", "Bridge", "James Hetfield's tone: EMG 81 bridge humbucker is the canonical choice."),
    "Stone Cold Loco": ("Humbucker", "Bridge", "Classic hard rock: bridge humbucker for aggressive attack."),
    "Plush Garden": ("Humbucker", "Neck or Bridge", "Dean DeLeo used humbuckers; neck for verse warmth, bridge for chorus crunch."),
    "Cowboys from DFW": ("Humbucker", "Bridge", "Dimebag's tone: high-output bridge humbucker (Dean ML) is essential."),
    "G.O.A.T. Rodeo": ("Single Coil", "Bridge or Middle", "Country/Southern rock: Telecaster bridge or Strat middle position is most authentic."),
    "GRAMMATICO JNC": ("Single Coil", "Any", "Boutique clean amp collaboration---single coils reveal the dynamic nuance."),
    "SCREAMS JNC": ("Humbucker", "Bridge", "High-gain lead: bridge humbucker for sustain and harmonic content."),
    "BIG DUBB": ("Either", "Neck", "Dub/reggae: neck pickup for warm, round tone regardless of pickup type."),
    "BIG VENUE DRIVE": ("Humbucker", "Bridge", "Large-venue rock drive works best with bridge humbucker output."),
    "BUBBLE NEST": ("Single Coil", "Neck or Middle", "Ambient clean textures shimmer most with single coils."),
    "DUSTED": ("Either", "Any", "Vintage breakup tone that responds well to any pickup."),
    "SUNRISE DRIVE": ("Either", "Neck or Middle", "Warm overdrive: neck or middle for smooth, musical character."),
    "GLISTEN": ("Single Coil", "Middle or Neck", "Shimmering clean: single coils in middle or neck for crystalline clarity."),
    "WATERS IN HELL": ("Single Coil", "Neck", "Gilmour's tone: Strat neck pickup is the canonical choice for Dark Side atmospherics."),
    "FAUX 7 STG CHUG": ("Humbucker", "Bridge", "Downtuned chugging demands a high-output bridge humbucker for clarity."),
    "RICHEESE": ("Humbucker", "Bridge", "1980s arena lead: bridge humbucker for sustain and harmonic richness."),
    "RC REINCARNATION": ("Either", "Any", "Artist collaboration---flexible pickup choice."),
    "RIFFS AND BEARDS": ("Humbucker", "Bridge", "Stoner/desert rock: thick bridge humbucker for massive fuzz riffs."),
    "FELIX MARK IV": ("Humbucker", "Bridge", "The Mark IV is most associated with bridge humbuckers for its lead channel."),
    "FELIX JAZZ 120": ("Single Coil", "Neck", "JC-120 jazz preset: neck single coil is the classic pairing."),
    "FELIX DELUXE MOD": ("Single Coil", "Neck or Middle", "Fender Deluxe with modulation---single coils for authentic character."),
    "FELIX ENGL": ("Humbucker", "Bridge", "ENGL high-gain: bridge humbucker for tight metal articulation."),
    "SPOTLIGHTS": ("Either", "Neck or Middle", "Post-rock/ambient: neck or middle for warmer, less aggressive input."),
    # ══════════ FACTORY 1: Artist Signature ══════════
    "BUMBLE ACOUSTIC": ("Single Coil", "Neck", "Acoustic simulation most convincing with neck single coil or piezo."),
    "BMBLFOOT PRINCE": ("Either", "Any", "Princeton tone is versatile across pickup types."),
    "BULB RHYTHM": ("Humbucker", "Bridge", "Mansoor's djent rhythm: high-output bridge humbucker (Bareknuckle/Fishman) is essential."),
    "BULB LEAD": ("Humbucker", "Bridge or Neck", "Lead: bridge for aggressive leads, neck for smoother melodic lines."),
    "BULB CLEAN": ("Either", "Neck or Middle", "Clean interludes: neck or middle for warmth."),
    "BULB AMBIENT": ("Either", "Neck", "Ambient textures: neck pickup for smooth, warm input into effects."),
    "EMPTY GARBAGE": ("Either", "Any", "Electronic-influenced alternative---any pickup suits the processed aesthetic."),
    "ONLY GARBAGE": ("Humbucker", "Bridge", "Aggressive alternative distortion: bridge humbucker for bite and sustain."),
    "BILLY KASTODON": ("Humbucker", "Bridge", "Mastodon's sludge: high-output bridge humbucker for crushing riffs."),
    "THIS IS THE END": ("Humbucker", "Bridge", "Dramatic high-gain: bridge humbucker for power and sustain."),
    "DJENT LA FUENTE": ("Humbucker", "Bridge", "Djent requires tight bridge humbucker response for percussive clarity."),
    "JONBUTTON UZAPIK": ("Either", "Any", "Artist signature---flexible."),
    "TrevLukatherSolo": ("Humbucker", "Bridge or Neck", "Solo lead: bridge for cut, neck for smoother sustain."),
    "HOWE WILDEST": ("Humbucker", "Bridge", "Greg Howe's fusion: bridge humbucker for aggressive articulation and speed."),
    "No:Thing": ("Either", "Any", "Experimental---pickup choice is part of the experimentation."),
    "PETE THORN DUO": ("Humbucker", "Bridge", "Pete Thorn favors humbuckers (Suhr) for his versatile session sound."),
    "RHETT'S ALLROUND": ("Either", "Any", "Designed to be versatile---works with any guitar and pickup."),
    "A DEADLY RHYTHM": ("Humbucker", "Bridge", "Precision rhythm: bridge humbucker for tight, percussive attack."),
    "JEFF SCHROEDER 1": ("Humbucker", "Bridge", "Smashing Pumpkins: Strat with hot bridge humbucker or Les Paul is canonical."),
    "JEFF SCHROEDER 2": ("Humbucker", "Bridge", "Alternative rock layering: humbuckers for the dense, saturated wall of sound."),
    "GRACOXONBUM": ("Humbucker", "Bridge", "Coxon's raw fuzzy tone: bridge humbucker or P90 for gritty character."),
    "Buck Mild": ("Single Coil", "Bridge or Middle", "Peter Buck's jangle: Rickenbacker-style or Strat bridge/middle single coil."),
    "LEWIE ALLEN BLUE": ("Single Coil", "Neck or Middle", "Blues: Strat-style single coils in neck or middle for expressive dynamics."),
    "RABEAAFRO LEAD": ("Humbucker", "Bridge", "Rabea's high-gain lead: bridge humbucker for sustain and clarity."),
    "RABEAAFRO CHUGGS": ("Humbucker", "Bridge", "Percussive chugging: bridge humbucker essential for tight palm-mute response."),
    "RABEA AMBIENT": ("Either", "Neck", "Ambient clean: neck pickup for warm, smooth input."),
    "RABEA AMBI LEAD": ("Humbucker", "Neck or Bridge", "Ambient lead: neck for smoother sustain, bridge for more presence."),
    "GUILTY PLEASURES": ("Humbucker", "Bridge", "1980s arena rock: bridge humbucker for the classic high-gain solo tone."),
    "DEVIN TOWNSEND": ("Humbucker", "Bridge", "Townsend's wall of sound: bridge humbucker (EMG) is his standard setup."),
    "NN BUBBLES": ("Either", "Any", "Textural preset---flexible."),
    "SHONN'S SHOTGUN": ("Humbucker", "Bridge", "Aggressive tone: bridge humbucker for immediate attack."),
    "InSTANtgH0St/24": ("Either", "Any", "Experimental---any pickup feeds the ghostly processing."),
    "OveRTONeGHoSt 3": ("Either", "Any", "Experimental---pickup choice affects overtone content."),
    "PaddingToNe": ("Either", "Neck", "Pad textures: neck pickup for smooth, sustained input."),
    "MJA + PANCAKE": ("Either", "Any", "Artist collaboration---flexible."),
    "PHILIP BYTONE": ("Either", "Any", "Dual-amp preset---flexible."),
    "REUTER LEAD": ("Humbucker", "Bridge", "Lead tone: bridge humbucker for sustain and projection."),
    "R U SERIOUS?": ("Either", "Any", "Experimental/humorous---anything goes."),
    # ══════════ FACTORY 1: Genre/Creative ══════════
    "Parallel Muffs": ("Humbucker", "Bridge", "Parallel fuzz: bridge humbucker for maximum saturation and harmonic content."),
    "Big County": ("Single Coil", "Bridge or Middle", "Big Country's harmonizer tone was played on Telecasters and Strats."),
    "Mockabilly": ("Single Coil", "Bridge", "Rockabilly: Telecaster bridge pickup is the canonical choice for twang."),
    "Stranger Synth": ("Either", "Bridge", "Synth tracking works best with a clear, defined signal---bridge pickup."),
    "You Shall Pass": ("Humbucker", "Bridge", "Epic cinematic tone: bridge humbucker for power and sustain."),
    "GlitchVerb": ("Either", "Any", "Experimental---pickup choice feeds the glitch processing differently."),
    "But Does It Doom": ("Humbucker", "Bridge", "Doom metal: bridge humbucker for crushing, sustained low-end."),
    "Mayer'ish JS": ("Single Coil", "Neck or Middle", "John Mayer's tone: Strat neck or middle single coil is essential."),
    "Robben'ish JS": ("Humbucker", "Neck or Bridge", "Robben Ford uses humbuckers; neck for jazz warmth, bridge for blues bite."),
    "X Ray": ("Either", "Any", "Transparent tone: designed to reveal the guitar's natural character."),
    "Big Monosynth": ("Either", "Bridge", "Synth tracking: bridge pickup for cleaner note detection."),
    "ISS Flyby": ("Either", "Any", "Ambient/space: any pickup works with the heavy effects processing."),
    # ══════════ FACTORY 1: SFX ══════════
    "SFX:Dr. Strange": ("Either", "Any", "Sound design---experiment with pickup choices for different textures."),
    "SFX:EXP Disturb": ("Either", "Any", "Sound design---any pickup."),
    "SFX:Hokulani": ("Single Coil", "Neck", "Celestial shimmer: neck single coil for smooth, ethereal input."),
    "SFX:Pulse Drone": ("Either", "Any", "Drone textures---any pickup."),
    "SFX:Rezz Score": ("Either", "Bridge", "Film score tension: bridge for darker, more defined input."),
    "SFX:Slot Machine": ("Either", "Any", "Chaotic sound design---any input."),
    "SFX:Trip City": ("Either", "Any", "Psychedelic sound design---experiment freely."),
    "SFX:Ufology": ("Either", "Any", "Alien textures---any pickup."),
    # ══════════ FACTORY 2 ══════════
    "Bentique": ("Single Coil", "Any", "Boutique clean: single coils reveal touch sensitivity best."),
    "A Swell Time": ("Either", "Neck", "Volume swell ambient: neck pickup for smooth, warm swells."),
    "None More Black": ("Humbucker", "Bridge", "Ultra-heavy saturation: bridge humbucker for maximum darkness."),
    "Bill&Ted at CERN": ("Either", "Any", "Experimental/sci-fi---any pickup feeds the unusual processing."),
    "Dark & Lush": ("Either", "Neck", "Dark ambient: neck pickup for warmer, darker input."),
    "Wild Year": ("Humbucker", "Bridge", "Energetic rock: bridge humbucker for aggressive dynamics."),
    "BackWahrds": ("Either", "Any", "Reverse effects: any pickup works with the psychedelic processing."),
    "Chalice of M'eh": ("Either", "Any", "Humorous/experimental---flexible."),
    "Mmmm Bat Heads": ("Humbucker", "Bridge", "Sabbath-inspired: bridge humbucker for thick, dark distortion."),
    "In Your House": ("Humbucker", "Bridge", "Industrial/dark rock: bridge humbucker for defined, aggressive input."),
    "Eat lt  ": ("Either", "Any", "Aggressive rock---flexible pickup choice."),
    "BEL HAVEN, boi!": ("Single Coil", "Bridge or Middle", "Southern blues-rock: Telecaster or Strat single coils for authentic twang."),
    "Spirit of Sky": ("Single Coil", "Bridge", "Norman Greenbaum used a Telecaster through fuzz---bridge single coil."),
    "Andy Warb Hall": ("Humbucker", "Bridge", "Mick Ronson's glam tone: Les Paul bridge humbucker is canonical."),
    "No Soup For You": ("Either", "Any", "Quirky/humorous---any guitar works."),
    "Oh No Stereo": ("Either", "Any", "Stereo effects showcase---works with any pickup."),
    "Mandarine Gaze": ("Humbucker", "Bridge", "Shoegaze: humbuckers for the wall of distortion."),
    "Chorus Crooner": ("Single Coil", "Neck or Middle", "Chorus-heavy clean: single coils for shimmer and clarity."),
    "Sky Explosions": ("Either", "Any", "Post-rock: dynamics come from volume and effects, not pickup choice."),
    "Watt, Now?": ("Either", "Any", "Hiwatt-style clean: works well with any pickup for its massive headroom."),
    "Breath Of Odin": ("Either", "Any", "Psychedelic/expansive: flexible pickup choice."),
    "Funk'n Roll": ("Single Coil", "Bridge or Middle", "Funk: single coils for snappy, percussive attack and clarity."),
    "Funk Clean": ("Single Coil", "Bridge or Middle", "Funk clean: Strat-style bridge or position 4 (bridge+middle) for tight snap."),
    "Sunset Shimmer": ("Single Coil", "Neck or Middle", "Shimmering clean: single coils for bright, airy quality."),
    "Ever Longer": ("Either", "Neck", "Sustain/ambient: neck pickup for smooth, warm sustain into effects."),
    "Rogue Vampires": ("Single Coil", "Any", "Indie rock: single coils for bright, clean-to-crunch character."),
    "Gorilla Clean": ("Single Coil", "Bridge or Middle", "Funky clean: single coils for percussive snap and clarity."),
    "Sweet Dispozish": ("Either", "Any", "Indie rock: single coils for jangle, humbuckers for warmth."),
    "Smooth Autopan": ("Either", "Neck", "Smooth auto-pan: neck pickup for warm, round input."),
    "Flood In Texas": ("Single Coil", "Neck", "SRV's tone: Strat neck single coil is absolutely essential for authenticity."),
    "Dream Syrup": ("Either", "Neck", "Dreamy, syrupy tone: neck pickup for smooth, sweet character."),
    "Rhythm Sandman": ("Humbucker", "Bridge", "Metallica rhythm: EMG 81 bridge humbucker is the canonical choice."),
    "Glengarry Lead": ("Humbucker", "Bridge or Neck", "Assertive lead: bridge for cut, neck for smoother sustain."),
    "Parallel Space": ("Either", "Any", "Parallel effects routing: any pickup works."),
    "'Merican Nights": ("Either", "Any", "Heartland rock: any American-made guitar and pickup."),
    "4D Love of Steve": ("Humbucker", "Bridge", "Steve Vai: bridge humbucker with whammy bar for expressive lead work."),
    "Ointment": ("Either", "Neck or Middle", "Smooth overdrive: neck or middle for warm, gentle breakup."),
    "Cherry-coloured": ("Either", "Any", "Cocteau Twins: effects dominate the tone; Robin Guthrie used various guitars."),
    "Low E Sludge": ("Humbucker", "Bridge", "Sludge metal: bridge humbucker for maximum low-end weight and definition."),
    "Thundermullet": ("Humbucker", "Bridge", "1980s thunder rock: bridge humbucker for arena-filling power."),
    "Nesbit": ("Either", "Any", "Flexible preset---any pickup."),
    "Star Talk": ("Single Coil", "Neck or Middle", "Cosmic clean: single coils for sparkle and clarity."),
    "Grease Cats": ("Single Coil", "Bridge", "Rockabilly: Telecaster bridge single coil for twangy, slapback-ready tone."),
    "Dramatic Scene": ("Either", "Neck", "Cinematic tone: neck pickup for emotive, dramatic quality."),
    "PhD May": ("Humbucker", "Bridge", "Brian May's Red Special uses single-coil-sized pickups wired in series for humbucker-like output; bridge position through AC-30."),
    "Ducked Trails": ("Either", "Any", "Ducking delay utility: works with any pickup."),
    "Rock Gaze": ("Humbucker", "Bridge", "Shoegaze/rock: humbuckers for thick distortion wall."),
    "Unicorns Forever": ("Either", "Any", "Whimsical/magical: effects define the tone."),
    "Hairy Air": ("Humbucker", "Bridge", "Fuzzy ambient: bridge humbucker for thicker, woollier fuzz texture."),
    "Bitey Panner": ("Either", "Bridge", "Biting auto-pan: bridge for more aggressive, defined input."),
    "Hi Octane": ("Humbucker", "Bridge", "High-energy rock: bridge humbucker for aggressive power."),
    "Knife Fight": ("Humbucker", "Bridge", "Aggressive, cutting tone: bridge humbucker for sharp attack."),
    "Barracudies": ("Humbucker", "Bridge", "Heart's `Barracuda': Nancy Wilson played a Les Paul---bridge humbucker."),
    "Snapshot Hotshot": ("Either", "Any", "Snapshot demonstration: designed to work with any guitar."),
    "Twinning": ("Either", "Any", "Dual-amp blend: flexible across pickup types."),
    "After the Fact": ("Either", "Neck", "Post-processed ambient: neck for smooth input into effects chain."),
    "Dream Off": ("Either", "Neck", "Dreamy ambient: neck pickup for warm, ethereal input."),
    "Go Your Way": ("Either", "Any", "Fleetwood Mac: Buckingham used both Teles and Les Pauls---either works."),
    "Double Trackin'": ("Either", "Any", "Studio double-tracking simulation: works with any pickup."),
    "Bit Like Heaven": ("Single Coil", "Bridge or Middle", "The Cure: Jazzmaster or Strat-style single coils are most authentic."),
    "Paranoia": ("Humbucker", "Bridge", "Tony Iommi: bridge humbucker (originally P90s, later humbuckers) for heavy crunch."),
    "Slowish Ride": ("Either", "Any", "Shoegaze: effects dominate; Slowdive and Ride used various guitars."),
    "Smoke on the H2O": ("Humbucker", "Bridge or Neck", "Blackmore used Strat singles live, but the studio tone suggests bridge humbucker or hot Strat bridge."),
    "Ziggy Moondust": ("Humbucker", "Bridge", "Mick Ronson: Les Paul bridge humbucker is the signature Ziggy pairing."),
    "Sultans": ("Single Coil", "Neck or Middle", "Mark Knopfler's fingerpicked tone: Strat neck or middle single coil is essential."),
    "Blue Wind": ("Humbucker", "Bridge or Neck", "Jeff Beck used a Les Paul on Wired, later Strats---either works."),
    "25? No, 6 to 4": ("Single Coil", "Bridge", "Terry Kath played Strats and Teles---bridge single coil with wah for the solo."),
    "Country Chorus": ("Single Coil", "Bridge or Middle", "Country: Telecaster bridge single coil is the canonical Nashville choice."),
    "Rock My Yacht": ("Single Coil", "Neck or Middle", "Yacht rock: warm, smooth cleans from neck or middle single coil."),
    "Gimme +/-3 Steps": ("Humbucker", "Bridge or Neck", "Southern rock: Les Paul humbuckers or Strat---flexible."),
    "Cliffs of Grover": ("Single Coil", "Neck or Middle", "Eric Johnson's tone: Strat neck single coil is the canonical choice."),
    "Goin' Home": ("Either", "Any", "Warm, versatile rock: flexible pickup choice."),
    "Jail Breaker": ("Humbucker", "Bridge", "Thin Lizzy/AC/DC hard rock: bridge humbucker for punchy riffs."),
    "2/3 Beards": ("Humbucker", "Bridge", "ZZ Top: Billy Gibbons' Les Paul bridge humbucker (Pearly Gates pickup) is iconic."),
    "On the Road": ("Either", "Any", "Road-ready versatile rock: any pickup works."),
    "Senor Sandman": ("Either", "Any", "Flexible rock preset---any pickup."),
    "$$$ For Nothin'": ("Humbucker", "Bridge", "Knopfler recorded this with a Les Paul bridge humbucker---an exception to his usual Strat."),
    "Phase Dance": ("Single Coil", "Any", "Pat Metheny's fusion: warm hollowbody or single coils for smooth, phased character."),
    "Roundabout": ("Single Coil", "Bridge", "Steve Howe: ES-175 or Telecaster-style---bridge for articulation."),
    "Dbl Match": ("Either", "Any", "Double Matchless: boutique amps that respond well to any pickup type."),
}


def parse_hls(filepath):
    with open(filepath, 'r') as f:
        hls = json.load(f)
    decoded = base64.b64decode(hls['encoded_data'])
    decompressed = zlib.decompress(decoded)
    data = json.loads(decompressed)
    return data if isinstance(data, list) else data.get('presets', [])


def extract_blocks(preset):
    tone = preset.get('tone', {})
    blocks = []
    for dsp_key in ['dsp0', 'dsp1']:
        dsp = tone.get(dsp_key, {})
        if not isinstance(dsp, dict):
            continue
        for bk in sorted(dsp.keys()):
            if not bk.startswith('block') and not bk.startswith('cab'):
                continue
            bv = dsp[bk]
            if not isinstance(bv, dict) or '@model' not in bv:
                continue
            model_id = bv['@model']
            enabled = bv.get('@enabled', True)
            info = MODEL_DB.get(model_id, None)
            if info is None:
                category, l6_name, real_name = "Unknown", model_id, model_id
            else:
                category, l6_name, real_name = info
            if category == "System":
                continue
            if bk.startswith('cab') and any(b['model_id'] == model_id for b in blocks):
                continue
            blocks.append({
                'dsp': dsp_key, 'block_key': bk, 'model_id': model_id,
                'category': category, 'l6_name': l6_name,
                'real_name': real_name, 'enabled': enabled,
            })
    return blocks


def tex_escape(s):
    if not s:
        return ""
    # Must escape backslash first
    s = s.replace('\\', '\\textbackslash{}')
    replacements = [
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\^{}'),
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    # Fix over-escaped textbackslash
    s = s.replace('\\textbackslash\\{\\}', '\\textbackslash{}')
    return s

def generate_latex(setlist_data, output_path):
    """setlist_data: list of (setlist_name, presets_list, groups_list)"""
    lines = []

    lines.append(r"""\documentclass[11pt,letterpaper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=1in]{geometry}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{xcolor}
\usepackage{hyperref}
\usepackage{titlesec}
\usepackage{fancyhdr}

\definecolor{disabledcolor}{HTML}{999999}

\titleformat{\section}{\LARGE\bfseries}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\large\bfseries}{}{0em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\itshape}{}{0em}{}

\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\textit{Helix Native Factory Preset Reference}}
\fancyhead[R]{\small\textit{Factory Presets}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

\begin{document}

\begin{titlepage}
\centering
\vspace*{3cm}
{\Huge\bfseries Line 6 Helix Native\\[0.5em]Factory Preset Reference\par}
\vspace{1.5cm}
{\Large Complete Factory 1, Factory 2 \& Templates Setlists\par}
\vspace{1cm}
{\large Signal Chain Documentation \& Decoded Preset Names\par}
\vspace{0.5cm}
{\large Helix Native Version 3.82\par}
\vspace{1.5cm}
{\normalsize Generated from firmware preset data.\\[0.3em]
Model identifications cross-referenced with the\\
Helix Native Owner's Manual and community sources.\par}
\vfill
{\small\today\par}
\end{titlepage}

\tableofcontents
\newpage
""")

    # Collect index data across all setlists
    amp_index = {}    # real_amp_name -> [(setlist, bank_str, preset_name)]
    artist_index = {} # artist -> [(setlist, bank_str, preset_name)]
    genre_index = {}  # genre -> [(setlist, bank_str, preset_name, label)]
    pickup_index = {} # pickup_type -> {position -> [(setlist, bank_str, preset_name, label)]}

    for setlist_name, presets, groups in setlist_data:
        lines.append(r'\section{' + tex_escape(setlist_name) + '}\n')

        for group_title, start_idx, end_idx, group_desc in groups:
            lines.append(r'\subsection{' + tex_escape(group_title) + '}\n')
            lines.append(tex_escape(group_desc) + '\n\n')

            for i in range(start_idx, min(end_idx, len(presets))):
                preset = presets[i]
                meta = preset.get('meta', {})
                name = meta.get('name', f'Preset {i}')

                if name == "New Preset":
                    continue

                info = PRESET_INFO.get(name.strip(), None)
                decoded_name = info[0] if info else name
                description = info[1] if info else "Factory preset."

                blocks = extract_blocks(preset)
                tempo = preset.get('tone', {}).get('global', {}).get('@tempo', None)

                bank = i // 4
                slot = chr(65 + (i % 4))
                bank_str = f"{bank+1:02d}{slot}"

                # Create a unique label for hyperlinking
                preset_label = f"{setlist_name.replace(' ', '')}-{bank_str}"
                lines.append(r'\subsubsection{' + bank_str + ': ' + tex_escape(name.strip()) + '}'
                             + r'\hypertarget{' + preset_label + '}{}\n')

                # ── Collect index data ──
                entry = (setlist_name, bank_str, name.strip(), preset_label)
                # Amp index: gather all amp/preamp blocks
                for b in blocks:
                    if b['category'] in ('Amp', 'Preamp') and b['real_name'] not in ('Unknown',):
                        real = b['real_name']
                        amp_index.setdefault(real, []).append(entry)
                # Artist index
                for artist in PRESET_ARTISTS.get(name.strip(), []):
                    artist_index.setdefault(artist, []).append(entry)
                # Genre index
                for genre in PRESET_GENRES.get(name.strip(), []):
                    genre_index.setdefault(genre, []).append(entry)
                # Pickup index
                pickup_info = PRESET_PICKUPS.get(name.strip(), None)
                if pickup_info:
                    ptype, ppos, pnotes = pickup_info
                    pickup_index.setdefault(ptype, {}).setdefault(ppos, []).append(entry)
                lines.append(r'\noindent\textbf{Decoded:} ' + tex_escape(decoded_name) + '\n')
                lines.append(r'\medskip\noindent ' + tex_escape(description) + '\n')

                # Pickup recommendation
                pickup_info = PRESET_PICKUPS.get(name.strip(), None)
                if pickup_info:
                    ptype, ppos, pnotes = pickup_info
                    pickup_line = r'\smallskip\noindent\textbf{Recommended Pickup:} '
                    pickup_line += tex_escape(ptype) + ', ' + tex_escape(ppos)
                    if pnotes:
                        pickup_line += ' --- \\textit{' + tex_escape(pnotes) + '}'
                    lines.append(pickup_line + '\n')

                if tempo and tempo > 0:
                    lines.append(r'\smallskip\noindent\textit{Tempo: ' + f'{tempo:.0f}' + r' BPM}' + '\n')

                if blocks:
                    lines.append(r'\smallskip')
                    lines.append(r'\begin{small}')
                    lines.append(r'\begin{longtable}{@{} l l l l @{}}')
                    lines.append(r'\toprule')
                    lines.append(r'\textbf{Category} & \textbf{Helix Name} & \textbf{Based On} & \textbf{Status} \\')
                    lines.append(r'\midrule')
                    lines.append(r'\endhead')

                    for b in blocks:
                        cat = tex_escape(b['category'])
                        l6 = tex_escape(b['l6_name'])
                        real = tex_escape(b['real_name'])
                        if not b['enabled']:
                            lines.append(r'\textcolor{disabledcolor}{' + cat + r'} & \textcolor{disabledcolor}{' + l6 + r'} & \textcolor{disabledcolor}{' + real + r'} & \textcolor{disabledcolor}{Off} \\')
                        else:
                            lines.append(cat + ' & ' + l6 + ' & ' + real + r' & On \\')

                    lines.append(r'\bottomrule')
                    lines.append(r'\end{longtable}')
                    lines.append(r'\end{small}')

                lines.append('')

    # ═══════════════════════════════════════════════════════════
    # APPENDIX: INDEX TABLES
    # ═══════════════════════════════════════════════════════════
    lines.append(r'\newpage')
    lines.append(r'\appendix')
    lines.append('')

    # ── Appendix A: Amp Make & Model Index ──
    lines.append(r'\section{Index by Amp Make \& Model}')
    lines.append(r'This index lists all presets grouped by the real-world amplifier they use. '
                 r'Presets using multiple amps appear under each. '
                 r'Amp names reflect the actual hardware modeled, not the Helix alias.')
    lines.append('')
    lines.append(r'\medskip')

    # Group amps by manufacturer
    def amp_manufacturer(name):
        """Extract manufacturer from amp name for grouping."""
        mfrs = [
            ("Fender", ["Fender"]),
            ("Marshall", ["Marshall"]),
            ("Vox", ["Vox"]),
            ("MESA/Boogie", ["MESA"]),
            ("Orange", ["Orange"]),
            ("Bogner", ["Bogner"]),
            ("Friedman", ["Friedman"]),
            ("Diezel", ["Diezel"]),
            ("Revv", ["Revv"]),
            ("Peavey", ["Peavey"]),
            ("PRS", ["PRS"]),
            ("Roland", ["Roland"]),
            ("Matchless", ["Matchless"]),
            ("Trainwreck", ["Trainwreck"]),
            ("Ampeg", ["Ampeg"]),
            ("Aguilar", ["Aguilar"]),
            ("Gallien-Krueger", ["Gallien"]),
            ("Sunn", ["Sunn"]),
            ("Acoustic", ["Acoustic 360", "Acoustic 3"]),
            ("Silvertone", ["Silvertone"]),
            ("Grammatico", ["Grammatico"]),
            ("ENGL", ["ENGL"]),
            ("Line 6", ["Line 6"]),
            ("Ben Adrian", ["Ben Adrian"]),
            ("Park", ["Park"]),
            ("Supro", ["Supro"]),
            ("Divided by 13", ["Divided"]),
            ("Soldano", ["Soldano"]),
            ("Hiwatt", ["Hiwatt"]),
            ("Pearce", ["Pearce"]),
            ("Pro Co", ["Pro Co"]),
            ("Klon", ["Klon"]),
            ("Electro-Harmonix", ["Electro-Harmonix", "EHX"]),
        ]
        for mfr, keys in mfrs:
            for k in keys:
                if k.lower() in name.lower():
                    return mfr
        return "Other"

    # Build manufacturer -> [(amp_name, entries)] structure
    mfr_amps = {}
    for amp_name in sorted(amp_index.keys()):
        mfr = amp_manufacturer(amp_name)
        mfr_amps.setdefault(mfr, []).append((amp_name, amp_index[amp_name]))

    for mfr in sorted(mfr_amps.keys()):
        lines.append(r'\subsection*{' + tex_escape(mfr) + '}')
        lines.append(r'\begin{small}')
        lines.append(r'\begin{longtable}{@{} l l l @{}}')
        lines.append(r'\toprule')
        lines.append(r'\textbf{Amp Model} & \textbf{Setlist} & \textbf{Preset} \\')
        lines.append(r'\midrule')
        lines.append(r'\endhead')

        for amp_name, entries in sorted(mfr_amps[mfr]):
            first = True
            for setlist, bank_str, preset_name, label in entries:
                amp_col = tex_escape(amp_name) if first else ''
                preset_link = r'\hyperlink{' + label + '}{' + bank_str + ': ' + tex_escape(preset_name) + '}'
                lines.append(amp_col + ' & ' + tex_escape(setlist) + ' & '
                             + preset_link + r' \\')
                first = False

        lines.append(r'\bottomrule')
        lines.append(r'\end{longtable}')
        lines.append(r'\end{small}')
        lines.append('')

    # ── Appendix B: Artist Index ──
    lines.append(r'\newpage')
    lines.append(r'\section{Index by Artist}')
    lines.append(r'This index lists presets associated with specific artists, either as '
                 r'official artist collaborations, signature presets, or tones inspired by '
                 r'the artist\textquotesingle s recorded work.')
    lines.append('')
    lines.append(r'\medskip')
    lines.append(r'\begin{small}')
    lines.append(r'\begin{longtable}{@{} l l l @{}}')
    lines.append(r'\toprule')
    lines.append(r'\textbf{Artist} & \textbf{Setlist} & \textbf{Preset} \\')
    lines.append(r'\midrule')
    lines.append(r'\endhead')

    for artist in sorted(artist_index.keys(), key=lambda x: x.lstrip("'\"").lower()):
        entries = artist_index[artist]
        first = True
        for setlist, bank_str, preset_name, label in entries:
            art_col = tex_escape(artist) if first else ''
            preset_link = r'\hyperlink{' + label + '}{' + bank_str + ': ' + tex_escape(preset_name) + '}'
            lines.append(art_col + ' & ' + tex_escape(setlist) + ' & '
                         + preset_link + r' \\')
            first = False

    lines.append(r'\bottomrule')
    lines.append(r'\end{longtable}')
    lines.append(r'\end{small}')

    # ── Appendix C: Genre Index ──
    lines.append(r'\newpage')
    lines.append(r'\section{Index by Genre}')
    lines.append(r'This index groups presets by musical genre or tonal category. '
                 r'Many presets span multiple genres and appear under each applicable heading.')
    lines.append('')
    lines.append(r'\medskip')

    for genre in sorted(genre_index.keys()):
        entries = genre_index[genre]
        lines.append(r'\subsection*{' + tex_escape(genre) + ' (' + str(len(entries)) + r')}')
        lines.append(r'\begin{small}')
        lines.append(r'\begin{longtable}{@{} l l @{}}')
        lines.append(r'\toprule')
        lines.append(r'\textbf{Setlist} & \textbf{Preset} \\')
        lines.append(r'\midrule')
        lines.append(r'\endhead')

        for setlist, bank_str, preset_name, label in entries:
            preset_link = r'\hyperlink{' + label + '}{' + bank_str + ': ' + tex_escape(preset_name) + '}'
            lines.append(tex_escape(setlist) + ' & ' + preset_link + r' \\')

        lines.append(r'\bottomrule')
        lines.append(r'\end{longtable}')
        lines.append(r'\end{small}')
        lines.append('')

    # ── Appendix D: Pickup Recommendation Index ──
    lines.append(r'\newpage')
    lines.append(r'\section{Index by Recommended Pickup Configuration}')
    lines.append(r'This index groups presets by their recommended pickup type and position. '
                 r'Recommendations are based on the canonical guitar and pickup pairings '
                 r'associated with each preset\textquotesingle s target tone, artist, or genre. '
                 r'Bass presets are omitted.')
    lines.append('')
    lines.append(r'\medskip')

    # Order pickup types logically
    type_order = ["Humbucker", "Single Coil", "P90", "Either"]
    for ptype in type_order:
        if ptype not in pickup_index:
            continue
        positions = pickup_index[ptype]
        total = sum(len(v) for v in positions.values())
        lines.append(r'\subsection*{' + tex_escape(ptype) + ' (' + str(total) + r')}')

        # Sort positions in a logical order
        pos_order = ["Bridge", "Bridge or Neck", "Bridge or Middle", "Neck", "Neck or Bridge",
                     "Neck or Middle", "Middle", "Middle or Neck", "Any"]
        sorted_positions = sorted(positions.keys(),
                                  key=lambda p: pos_order.index(p) if p in pos_order else 99)

        lines.append(r'\begin{small}')
        lines.append(r'\begin{longtable}{@{} l l l @{}}')
        lines.append(r'\toprule')
        lines.append(r'\textbf{Position} & \textbf{Setlist} & \textbf{Preset} \\')
        lines.append(r'\midrule')
        lines.append(r'\endhead')

        for pos in sorted_positions:
            entries = positions[pos]
            first = True
            for setlist, bank_str, preset_name, label in entries:
                pos_col = tex_escape(pos) if first else ''
                preset_link = r'\hyperlink{' + label + '}{' + bank_str + ': ' + tex_escape(preset_name) + '}'
                lines.append(pos_col + ' & ' + tex_escape(setlist) + ' & '
                             + preset_link + r' \\')
                first = False

        lines.append(r'\bottomrule')
        lines.append(r'\end{longtable}')
        lines.append(r'\end{small}')
        lines.append('')

    lines.append(r'\end{document}')

    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 generate_latex.py <setlist1.hls> [setlist2.hls ...] [-o output.tex]")
        sys.exit(1)

    hls_files = []
    output_path = 'helix_reference.tex'
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '-o' and i+1 < len(sys.argv):
            output_path = sys.argv[i+1]
            i += 2
        else:
            hls_files.append(sys.argv[i])
            i += 1

    FACTORY1_GROUPS = [
        ("Amp Showcase Presets (01A--08D)", 0, 32,
         "These presets showcase individual amp models with minimal effects, providing a direct reference for each amplifier's tonal character."),
        ("Bass Presets (09A--11B)", 32, 43,
         "Bass-focused presets demonstrating the bass amplifier models, from classic tube to modern solid-state."),
        ("Artist & Song-Inspired Presets (11C--17A)", 43, 66,
         "Presets inspired by specific artists, songs, or tonal aesthetics. Names are often obfuscated for trademark reasons."),
        ("Artist Signature Presets (17B--27C)", 66, 108,
         "Presets created by or in collaboration with professional artists who use the Helix platform."),
        ("Genre & Creative Presets (27D--30C)", 108, 120,
         "Genre-specific, creative sound design, and utility presets."),
        ("Sound Effects Presets (30D--32C)", 120, 128,
         "Experimental sound-design presets for cinematic and ambient textures."),
    ]

    FACTORY2_GROUPS = [
        ("Song-Inspired & Creative Presets (01A--08D)", 0, 32,
         "An eclectic collection of presets inspired by songs, genres, and creative tonal concepts, ranging from boutique cleans to heavy distortion."),
        ("Song-Inspired & Genre Presets (09A--20D)", 32, 80,
         "A broad collection referencing classic rock songs, artists, and genre archetypes from blues and country to prog-rock and shoegaze."),
        ("Bass Presets (21A--23C)", 80, 91,
         "Bass-focused presets covering parallel fuzz, funk, British bass, synth bass, and more."),
    ]

    TEMPLATES_GROUPS = [
        ("Quick Start & Signal Routing Templates (01A--01D)", 0, 4,
         "Basic starter presets and signal routing templates demonstrating parallel paths, snapshot-based amp switching, and serial routing configurations."),
        ("External Amp & Multi-Cable Routing (02A--03D)", 4, 16,
         "Routing templates for integrating Helix with external amplifiers and effects loops, including 4-cable, 7-cable, wet/dry/wet, and A/B tone switching configurations. These are primarily relevant to Helix hardware rather than Helix Native."),
        ("Multi-Instrument & Mixing Templates (04A--04D)", 16, 20,
         "Templates for processing multiple instruments simultaneously, including guitar-and-vocals dual paths, four-input mixing, and DT-series amp control."),
        ("MIDI & Synth Utilities (05A--05D)", 20, 24,
         "Utility templates using Helix as a MIDI controller, synth bass pedalboard, or momentary pitch-shift effects processor."),
        ("DAW Remote Control Templates (06A--10B)", 24, 42,
         "MIDI remote control presets that turn Helix into a DAW transport controller or media playback remote. Each template is preconfigured for a specific application's keyboard shortcuts or MIDI mapping."),
        ("Bonus Presets (32D)", 127, 128,
         "Miscellaneous bonus presets placed at the end of the Templates bank."),
    ]

    setlist_data = []
    for hls_path in hls_files:
        print(f"Parsing: {hls_path}")
        presets = parse_hls(hls_path)
        name = os.path.splitext(os.path.basename(hls_path))[0].replace('_', ' ')
        print(f"  {len(presets)} presets in {name}")

        if 'FACTORY_1' in hls_path.upper() or 'FACTORY1' in hls_path.upper():
            groups = FACTORY1_GROUPS
        elif 'FACTORY_2' in hls_path.upper() or 'FACTORY2' in hls_path.upper():
            groups = FACTORY2_GROUPS
        elif 'TEMPLATE' in hls_path.upper():
            groups = TEMPLATES_GROUPS
        else:
            groups = [("All Presets", 0, len(presets), "All presets in this setlist.")]

        setlist_data.append((name, presets, groups))

    print(f"Generating: {output_path}")
    generate_latex(setlist_data, output_path)
    print("Done!")
