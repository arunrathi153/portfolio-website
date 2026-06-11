from resume_reader import extract_text
from resume_parser import extract_resume_details
from job_matcher import rank_candidates

def main():
    # File path to resume aur ye txt or pdf ne hona chye only
    resume_path = 'c:/Users/arun/OneDrive/Desktop/resume project/Resume_Arun_2025.pdf'  # yaha resume dalega jiski info. extract krni h
    
    # Job ki requirements 
    job_requirements = {
        'skills': 'python, machine learning, deep learning, SQL',
        'experience': 0,  # In years
        'education': 'bachelor'
    }

    #1st Extract text from resume file
    resume_text = extract_text(resume_path)

    if resume_text:
        #2nd n.o pr Extract details from the resume
        resume_details = extract_resume_details(resume_text)
        
        # 3rd pr Compare resume details to job requirements
        ranked_results = rank_candidates([resume_details], job_requirements)
        match_results = ranked_results[0]  # since only one resume
 

        # 4th pe result ki output match krni he
        print(f"Matched Skills: {match_results['matched_skills']}")
        print(f"Matched Experience: {'Yes' if match_results['matched_experience'] else 'No'}")
        print(f"Matched Education: {'Yes' if match_results['matched_education'] else 'No'}")
    else:
        print("Error extracting text from resume. Please check the file format.")

if __name__ == '__main__':
    main()
