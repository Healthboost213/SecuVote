from sqlalchemy import create_engine, MetaData, select, insert, update, join, func,text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(f'mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('DATABASE_IP')}/Student_Council')

metadata = MetaData()
metadata.reflect(bind=engine)

votes = metadata.tables['Votes']
candidates = metadata.tables['Candidate']

class Candidate:
    
    def __init__(self):
        self.first_name = ""
        self.last_name = ""
        self.grade = ""
        self.posting = -1

    def get_input(self):
        self.first_name = input("What is the Candidate's First Name? ")
        self.last_name = input("What is the Candidate's Last Name? ")
        self.grade = input("What is the Candidate's Class and Section? ")
        self.posting = input("What is the Candidates's Posting ID? ")
        self.images = input("What is the file name of the Candidate's Photo? ")

    def db_entry(self):
        with engine.connect() as conn:
            with conn.begin():
                
                insert_stmt_cndt = insert(candidates).values(CandidateFirstName = self.first_name,
                                                        CandidateLastName = self.last_name,
                                                        CandidateClass = self.grade,
                                                        ImageName = self.images)
                
                conn.execute(insert_stmt_cndt)
                
                select_candID = select(candidates.c.CandidateID).where(candidates.c.CandidateFirstName == self.first_name)

                curr_candID = conn.execute(select_candID)
                if curr_candID.rowcount > 1:
                    raise Exception

                insert_stmt_vote = insert(votes).values(CandidateID = curr_candID.one()[0], PostingID = self.posting, Votes = 0)
                conn.execute(insert_stmt_vote)


count = input("Enter the number of Candidates that need to be entered: ")
for person in range(0, count):
    data = Candidate()
    data.get_input()
    data.db_entry()

