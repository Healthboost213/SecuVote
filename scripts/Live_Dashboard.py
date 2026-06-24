import mysql.connector
import matplotlib.pyplot as plt
import time


conn = mysql.connector.connect(
    host = "192.168.1.125",
    user = "username",
    password = "username_123",
    database = "Student_Council",
)

cursor = conn.cursor()


def Get_Posting():
    query = """
    Select * from Postings
    """
    cursor.execute(query)
    result =  cursor.fetchall()
    return(result)



def Pie_Chart(Posting_ID , Chart_Title):

    query = f"""
    Select Postings.PostingName , Candidate.CandidateFirstName , Candidate.CandidateLastName , Candidate.CandidateClass , Votes.Votes
    From Votes
    Inner Join Candidate ON Votes.CandidateID = Candidate.CandidateID
    Inner Join Postings ON Votes.PostingID = Postings.PostingID
    Where Postings.PostingID = {Posting_ID}
    """
    cursor.execute(query)
    results = cursor.fetchall()
    

    Name = []
    Votes = []

    for row in results:
        Name.append(row[1] + " " + row[2])
        Votes.append(row[4])
    

    try:
        plt.clf()
        plt.pie(Votes , labels=Name, autopct= '%1.1f%%')
        plt.title(Chart_Title)
        plt.savefig(Chart_Title + ".png")
        
        

    except:
        print("There are no votes avalible for any candidate")
    


while True:
    print("Refreshing Dashboard") 
    print(time.strftime("%H:%M:%S"))
    for posting in Get_Posting():
        Pie_Chart(posting[0] , posting[1])
    time.sleep(10)
  












