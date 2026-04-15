# Skill Generation Framework
Generating and evaluating in-game battle skills using the following methods:

- Random Generation (RDM)
- Rule-Guided Delta Greedy (RGDG)
- Genetic Algorithm (GA)

# Requirements
pip install numpy matplotlib scipy pandas

# How to Run
Run with random template:
python main.py
or
python3 main.py (if using virtual environment)

Run with specific template:
python main.py <template_id>

Template mapping:
1 = basic  
2 = berserk  
3 = glass cannon  
4 = tank  
5 = elite  
6 = boss  

Example:
python main.py 4
or
python3 main.py 4 (if using virtual environment)

# Extention
for directory not found or system path incompatible issue, may require to go to config.py to manually change into absolute path

for tuning with different constraints, may go to

- skill_skeleton_constraint_space.json
- skill_modifier_space.json
- character_basic_modifier.json

to make modifications

