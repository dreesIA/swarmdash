# teams_config.py

# Team 1: SSA Swarm USL2 2025
SSA_SWARM_USL2 = {
    "logo": "SSALogoTransparent.jpeg",
    "description": "USL2 Performance Center",
    "match_files": {
        "5.17 vs Birmingham Legion 2": "SSA Swarm USL Mens 2 Games Statsports Reports - 5.17 SSA Swarm USL 2 vs Birmingham.csv",
        "5.21 vs Tennessee SC": "SSA Swarm USL Mens 2 Games Statsports Reports - 5.21 Swarm USL 2 Vs TN SC.csv",
        "5.25 vs East Atlanta FC": "SSA Swarm USL Mens 2 Games Statsports Reports - 5.25 SSA Swarm USL 2 vs East Atlanta.csv",
        "5.31 vs Dothan United SC": "SSA Swarm USL Mens 2 Games Statsports Reports - 5.31 Swarm USL 2 vs Dothan.csv",
        "6.4 vs Asheville City SC": "SSA Swarm USL Mens 2 Games Statsports Reports - 6.4 Swarm USL 2 vs Asheville.csv",
        "6.7 vs Dothan United SC": "SSA Swarm USL Mens 2 Games Statsports Reports - 6.7 Swarm USL 2 vs Dothan FC .csv"
    },
    "training_files": {
        "5.12 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 5.12 Training.csv",
        "5.13 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 5.13 Training .csv",
        "5.15 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 5.15 Training.csv",
        "5.16 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 5.16 Training.csv",
        "5.19 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 5.19 Training.csv",
        "5.20 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 5.20 Training.csv",
        "6.3 Training": "SSA Swarm USL 2 Mens Statsports Traning Report  - 6.3 Training.csv",
    },
    "event_files": {
        "5.17 vs Birmingham Legion 2": "SSA USL2 v BHM Legion2 05.17.25.xlsx",
        "5.21 vs Tennessee SC": "SSA USL2 v TSC 05.21.25.xlsx",
        "5.25 vs East Atlanta FC": "SSA USL2 v EAFC 05.25.25.xlsx",
        "5.31 vs Dothan United SC": "SSA v Dothan USL2 05.31.25.xlsx",
        "6.4 vs Asheville City SC": "SSA USL2 v Asheville City SC 06.04.25.xlsx",
        "6.7 vs Dothan United SC": "SSA USL2 v Dothan2 06.07.25.xlsx",
    },
    "event_images": {
        "5.17 vs Birmingham Legion 2": "SSAvBHM2 Event Image.png",
        "5.21 vs Tennessee SC": "TSC New Event Image.png",
        "5.25 vs East Atlanta FC": "East Atlanta Event Data Screenshot.png",
        "5.31 vs Dothan United SC": "Dothan Event Image.png",
        "6.4 vs Asheville City SC": "Asheville Event Image.png",
        "6.7 vs Dothan United SC": "Dothan2 Event Image.png",
    }
}

# Team 2: SSA Boys MLS Next U19
SSA_ACADEMY_U19 = {
    "logo": "SSALogoTransparent.jpeg",
    "description": "U19 MLS Next Performance Center",
    "match_files": {
        # Add more matches...
    },
    "training_files": {
        # Add more training sessions...
    },
    "event_files": {
        # Add more event files...
    },
    "event_images": {
        # Add more event images...
    }
}

# Team 3: SSA Women's First Team
SSA_WOMENS_FIRST = {
    "logo": "SSALogoTransparent.jpeg",
    "description": "USLW Performance Center",
    "match_files": {
        # Add match files...
    },
    "training_files": {
        # Add training files...
    },
    "event_files": {
        # Add event files...
    },
    "event_images": {
        # Add event images...
    }
}

#Team 4: SSA Girls U19
SSA_GIRLS_ACADEMY = {
    "logo":"SSALogoTransparent.jpeg",
    "description": "U19 GA Performance Center",
    "match_files": {

    },
    "training_files": {

    },
    "event_files": {
    },
    "event_images": {
    }
}

# Master configuration
TEAMS_CONFIG = {
    "SSA Swarm USL2": SSA_SWARM_USL2,
    "SSA Swarm USLW": SSA_WOMENS_FIRST,
    "SSA Swarm MLS Next U19": SSA_ACADEMY_U19,
    "SSA Swarm GA U19": SSA_GIRLS_ACADEMY,
    # Add more teams here...
}
