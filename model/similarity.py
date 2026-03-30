def get_similarity(resume, job_desc):
    resume_words = resume.split()
    job_words = job_desc.split()

    if not resume_words or not job_words:
        return 10.0   

    matches = 0
    for word in job_words:
        if word in resume_words:
            matches += 1

    score = (matches / len(job_words)) * 100

    
    if score == 0:
        return 10.0

    return round(score, 2)