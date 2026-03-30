def extract_skills(text, skills_list):
    found = []

    for skill in skills_list:
        if skill in text:
            found.append(skill)

        
        if skill == "sql" and "mysql" in text:
            found.append("sql")

        if skill == "html" and "html" in text:
            found.append("html")

        if skill == "python" and "python" in text:
            found.append("python")

    return sorted(list(set(found)))