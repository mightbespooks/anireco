def category_mean(anime_list, category):
    STAFF_ROLES = {
        "director", "chief director", "assistant director", "art director", 
        "series composition", "script", "original story", "original character design", "music"
    }

    scores = {}

    for anime in anime_list:
        score = anime.get("score", 0)
        
        if score != 0:
            data = anime.get(category, [])
            items = []

            # dict for studios or staff.
            if isinstance(data, dict) and "edges" in data:
                for edge in data.get("edges", []):
                    full_name = None

                    if category == "staff":
                        if edge.get("role").lower() in STAFF_ROLES:

                            staff_name = edge.get("node", {}).get("name", {})
                            full_name = " ".join(
                                p for p in [
                                    staff_name.get("first"),
                                    staff_name.get("last")
                                ]
                                if p
                            )
                            
                    elif category == "studios":
                        if not edge.get("isMain"):
                            continue

                        full_name = edge.get("node", {}).get("name")

                    if full_name:
                        items.append(full_name)

            # list for genres or tags.
            elif isinstance(data, list):
                for i in data:
                    if isinstance(i, dict):
                        items.append(i.get("name"))
                    else:
                        items.append(i)

            for name in items:
                if name not in scores:
                    scores[name] = []

                scores[name].append(score)

    return {
        name: {
            "mean": round(sum(vals) / len(vals), 2),
            "count": len(vals)
        }
        for name, vals in scores.items()
    }