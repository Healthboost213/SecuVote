from sqlalchemy import create_engine, MetaData, select, insert, update, join, func
from sqlalchemy.exc import IntegrityError
import os
import pymysql

# Database Configuration + Pooling for Concurrency

engine = create_engine(f'mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_IP')}/Student_Council',
                       pool_size=30, max_overflow=50, pool_timeout=30, pool_recycle=3600)

# Database Reflection

metadata = MetaData()
metadata.reflect(bind=engine)

users = metadata.tables['StudentDetails']
candidates = metadata.tables['Candidate']
postings = metadata.tables['Postings']
votes = metadata.tables['Votes']

# Functions for main program

def email_inserter(email):

    with engine.connect() as conn:
        with conn.begin():

            # Row Level Locking
            select_stmt = select(users.c.HasVoted).where(users.c.EmailID == email).with_for_update()
            has_double_vote = conn.execute(select_stmt).scalar_one_or_none()
            
            if has_double_vote == 1:
                return True
            else:
                try:
                    insert_stmt = insert(users).values(EmailID=email, HasVoted=False)
                    conn.execute(insert_stmt)
                    return False
                except IntegrityError:
                    return False

def vote_inserter(email, form_data):
    
    try:
        
        with engine.connect() as conn:
            
            with conn.begin():

                # Updates the user to voted State
                update_stmt = update(users).where(users.c.EmailID == email, users.c.HasVoted == 0).values(HasVoted = 1)
                status = conn.execute(update_stmt)

                if status.rowcount == 0:
                    return False # 

                # Iterates through the form_data dictionary to increment candidate votes
                for postID, candID in form_data.items():
                    increment_stmt = update(votes).where(votes.c.PostingID == postID, votes.c.CandidateID == candID).values(Votes=votes.c.Votes + 1)
                    result = conn.execute(increment_stmt) 

                    # Raising error to prevent erroneous values to be passed on to MySQL
                    if result.rowcount == 0:
                        raise LookupError('Could Not Find Matching postingID or candidateID')           
  
            return True
                
    except LookupError:
        print("lookup error")
        return False
    except Exception:
        print("something")
        return False
    
# Data Fetcher for auto-population
def data_fetcher():
    with engine.connect() as conn:
        with conn.begin():
            select_stmt = (
                select(postings.c.PostingName, 
                       func.group_concat(candidates.c.CandidateFirstName).label('FirstName'),
                       func.group_concat(candidates.c.CandidateLastName).label('LastName'),
                       func.group_concat(candidates.c.CandidateClass).label('Class'),
                       func.group_concat(postings.c.PostingID).label('PostingID'),
                       func.group_concat(candidates.c.CandidateID).label('CandidateID'),
                       func.group_concat(candidates.c.ImageName).label('ImageName')
                )
                .select_from(votes)
                .join(candidates, votes.c.CandidateID == candidates.c.CandidateID)
                .join(postings, votes.c. PostingID == postings.c.PostingID)
                .group_by(postings.c.PostingName))
            
            result = conn.execute(select_stmt)

            # Get data and put it into a usable format { PostingName: ( (FirstName, LastName, Class) , ( ... ) ... }
            # Key in dictionary stores a 2D Array as value

            posting_result = result.mappings().all()
            final_election_data = {}

            for posting in posting_result:

                role = posting['PostingName']
                f_names = posting['FirstName'].split(',')
                l_names = posting['LastName'].split(',')
                classes = posting['Class'].split(',')
                p_ids = posting['PostingID'].split(',')
                c_ids = posting['CandidateID'].split(',')
                img_p = posting['ImageName'].split(',')
                
                temp_candidates = []
                for fn, ln, clss, pid, cid, i_p in zip(f_names, l_names, classes, p_ids, c_ids, img_p):
                    # Creating the inner tuple for each candidate
                    candidate_tuple = (pid, cid, f"{fn}", f"{ln}", clss, i_p)
                    temp_candidates.append(candidate_tuple)
            
                final_election_data[role] = tuple(temp_candidates)

            return final_election_data
