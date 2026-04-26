# Place your workout and diet PDF files here using this folder structure:
#
# data/pdfs/
# ├── DietPlans/
# │   ├── 3300 calories diet/
# │   │   └── plan.pdf
# │   ├── 2500 calories diet/
# │   │   └── plan.pdf
# │   ├── 1800 calories shredding/
# │   │   └── plan.pdf
# │   └── Vegetarian Bulking/
# │       └── plan.pdf
# ├── WorkoutPlans/
# │   ├── Push Pull Legs Gym/
# │   │   └── routine.pdf
# │   ├── Full Body Home Beginner/
# │   │   └── routine.pdf
# │   ├── Upper Lower Split/
# │   │   └── routine.pdf
# │   └── HIIT Cardio/
# │       └── routine.pdf
# └── (any other top-level folders are tagged as "general")
#
# HOW METADATA IS EXTRACTED:
#   - Top-level folder name → category ("diet" or "workout")
#   - Subfolder name → subcategory + calorie target (if present)
#   - The subfolder name is the LABEL for that plan
#
# TIPS:
#   - Name subfolders descriptively: "3300 calories bulking diet"
#   - Include calories in the folder name and it auto-extracts
#   - You can have multiple PDFs in one subfolder
